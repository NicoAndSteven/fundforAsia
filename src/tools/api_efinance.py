"""
efinance 数据适配器
基于东方财富的免费实时数据源
支持 A 股/美股/港股的实时行情, 无需 API Key
"""
import logging
from typing import List, Optional, Dict, Any
import pandas as pd
import efinance as ef
from datetime import datetime, timedelta

from src.data.cache import get_cache
from src.data.models import Price, FinancialMetrics, InsiderTrade, CompanyNews, LineItem

logger = logging.getLogger(__name__)
_cache = get_cache()


class EFDataAdapter:
    """efinance 数据适配器 - 基于东方财富的实时数据源"""

    def __init__(self):
        self._stock_basic_cache = None

    # ------------------------------------------------------------------
    # Ticker normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_ticker(ticker: str) -> str:
        """
        标准化股票代码为 efinance 兼容格式.
        efinance 接受纯数字代码即可, 但对于 A 股自动识别市场.

        Args:
            ticker: 股票代码, 如 '600519' / 'AAPL' / '000001'
        Returns:
            标准化后的代码
        """
        return str(ticker).upper().strip().replace(".SH", "").replace(".SZ", "")

    @staticmethod
    def _is_a_share(ticker: str) -> bool:
        """判断是否为 A 股代码."""
        t = ticker.strip()
        return t.isdigit() and (t.startswith(("0", "3", "6", "8")))

    # ------------------------------------------------------------------
    # Prices
    # ------------------------------------------------------------------

    def get_prices(
        self,
        ticker: str,
        start_date: str,
        end_date: str,
        api_key: str = None,
    ) -> List[Price]:
        """
        获取日 K 线价格数据 (当天实时可用).

        Args:
            ticker: 股票代码
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            api_key: 未使用, 保持接口一致
        Returns:
            价格数据列表
        """
        cache_key = f"ef_{ticker}_{start_date}_{end_date}"
        if cached_data := _cache.get_prices(cache_key):
            return [Price(**p) for p in cached_data]

        code = self.normalize_ticker(ticker)
        try:
            df = ef.stock.get_quote_history(code, klt=101)
        except Exception as e:
            logger.error("efinance get_quote_history(%s) failed: %s", code, e)
            return []

        if df is None or df.empty:
            logger.warning("No price data for %s", ticker)
            return []

        # Filter by date range
        df["日期"] = df["日期"].astype(str)
        if start_date:
            df = df[df["日期"] >= start_date]
        if end_date:
            df = df[df["日期"] <= end_date]

        prices: list[Price] = []
        for _, row in df.iterrows():
            try:
                prices.append(Price(
                    open=float(row["开盘"]),
                    close=float(row["收盘"]),
                    high=float(row["最高"]),
                    low=float(row["最低"]),
                    volume=int(float(row["成交量"])) if row["成交量"] else 0,
                    time=str(row["日期"]),
                ))
            except (ValueError, TypeError, KeyError) as e:
                logger.debug("Skipping price row %s: %s", row.to_dict(), e)
                continue

        if prices:
            _cache.set_prices(cache_key, [p.model_dump() for p in prices])
            logger.info("Fetched %d price rows for %s (efinance)", len(prices), ticker)
        return prices

    def get_intraday_prices(
        self,
        ticker: str,
        date: str,
        frequency: str = "5",
        api_key: str = None,
    ) -> List[Price]:
        """
        获取分钟级 K 线数据 (盘中实时).

        Args:
            ticker: 股票代码
            date: 日期 YYYY-MM-DD
            frequency: 频率 "5"/"15"/"30"/"60" 分钟
            api_key: 未使用
        Returns:
            分钟级价格数据列表
        """
        cache_key = f"ef_intraday_{ticker}_{date}_{frequency}"
        if cached_data := _cache.get_prices(cache_key):
            return [Price(**p) for p in cached_data]

        code = self.normalize_ticker(ticker)
        klt = int(frequency)
        try:
            df = ef.stock.get_quote_history(code, klt=klt)
        except Exception as e:
            logger.error("efinance get_quote_history(%s, klt=%s) failed: %s", code, frequency, e)
            return []

        if df is None or df.empty:
            return []

        df["日期"] = df["日期"].astype(str)
        df = df[df["日期"].str.startswith(date[:10])]

        prices: list[Price] = []
        for _, row in df.iterrows():
            try:
                prices.append(Price(
                    open=float(row["开盘"]),
                    close=float(row["收盘"]),
                    high=float(row["最高"]),
                    low=float(row["最低"]),
                    volume=int(float(row["成交量"])) if row["成交量"] else 0,
                    time=str(row["日期"]),
                ))
            except (ValueError, TypeError, KeyError):
                continue

        if prices:
            _cache.set_prices(cache_key, [p.model_dump() for p in prices])
        return prices

    # ------------------------------------------------------------------
    # Financial metrics
    # ------------------------------------------------------------------

    def get_financial_metrics(
        self,
        ticker: str,
        end_date: str,
        period: str = "ttm",
        limit: int = 10,
        api_key: str = None,
    ) -> List[FinancialMetrics]:
        """
        获取财务指标.
        数据来源: efinance get_all_company_performance + get_latest_quote.

        Args:
            ticker: 股票代码
            end_date: 报告期 (仅用于缓存键)
            period: 未使用 (efinance 返回最新季度)
            limit: 限制返回数
            api_key: 未使用
        Returns:
            财务指标列表
        """
        cache_key = f"ef_financial_{ticker}_{end_date}"
        if cached_data := _cache.get_financial_metrics(cache_key):
            return [FinancialMetrics(**m) for m in cached_data]

        code = self.normalize_ticker(ticker)

        # ── 季度财务数据 ──
        perf = {}
        try:
            df_perf = ef.stock.get_all_company_performance()
            if df_perf is not None and not df_perf.empty:
                df_perf["股票代码"] = df_perf["股票代码"].astype(str).str.strip()
                match = df_perf[df_perf["股票代码"] == code]
                if not match.empty:
                    perf = match.iloc[-1].to_dict()
        except Exception as e:
            logger.debug("get_all_company_performance failed for %s: %s", ticker, e)

        # ── 实时行情 (含市值/PE) ──
        quote = {}
        try:
            df_q = ef.stock.get_latest_quote([code])
            if df_q is not None and not df_q.empty:
                quote = df_q.iloc[0].to_dict()
        except Exception as e:
            logger.debug("get_latest_quote failed for %s: %s", ticker, e)

        # ── 拼装 FinancialMetrics ──
        def _val(d, key):
            v = d.get(key)
            if v is None or v == "" or v == "--":
                return None
            try:
                return float(v)
            except (ValueError, TypeError):
                return None

        market_cap = _val(quote, "总市值")
        pe_ratio = _val(quote, "动态市盈率")
        close_price = _val(quote, "最新价")

        metrics = FinancialMetrics(
            ticker=ticker,
            report_period=str(perf.get("公告日期", end_date))[:10] if perf else end_date,
            period=period,
            currency="CNY",
            market_cap=market_cap,
            enterprise_value=market_cap,
            price_to_earnings_ratio=pe_ratio,
            price_to_book_ratio=None,  # efinance 不直接提供
            price_to_sales_ratio=None,
            enterprise_value_to_ebitda_ratio=None,
            enterprise_value_to_revenue_ratio=None,
            free_cash_flow_yield=None,
            peg_ratio=None,
            gross_margin=_val(perf, "销售毛利率"),
            operating_margin=None,
            net_margin=None,
            return_on_equity=_val(perf, "净资产收益率"),
            return_on_assets=None,
            return_on_invested_capital=None,
            asset_turnover=None,
            inventory_turnover=None,
            receivables_turnover=None,
            days_sales_outstanding=None,
            operating_cycle=None,
            working_capital_turnover=None,
            current_ratio=None,
            quick_ratio=None,
            cash_ratio=None,
            operating_cash_flow_ratio=None,
            debt_to_equity=None,
            debt_to_assets=None,
            interest_coverage=None,
            revenue_growth=_val(perf, "营业收入同比增长"),
            earnings_growth=_val(perf, "净利润同比增长"),
            book_value_growth=None,
            earnings_per_share=_val(perf, "每股收益"),
            earnings_per_share_growth=None,
            free_cash_flow_growth=None,
            operating_income_growth=None,
            ebitda_growth=None,
            payout_ratio=None,
            book_value_per_share=_val(perf, "每股净资产"),
            free_cash_flow_per_share=None,
        )

        result = [metrics]
        _cache.set_financial_metrics(cache_key, [m.model_dump() for m in result])
        logger.info("Fetched financial metrics for %s (efinance)", ticker)
        return result

    # ------------------------------------------------------------------
    # Market cap
    # ------------------------------------------------------------------

    def get_market_cap(
        self,
        ticker: str,
        end_date: str,
        api_key: str = None,
    ) -> Optional[float]:
        """获取总市值 (从实时行情)."""
        code = self.normalize_ticker(ticker)
        try:
            df = ef.stock.get_latest_quote([code])
            if df is not None and not df.empty:
                val = df.iloc[0].get("总市值")
                if val is not None and val != "":
                    return float(val)
        except Exception as e:
            logger.debug("get_market_cap(%s) failed: %s", ticker, e)
        return None

    # ------------------------------------------------------------------
    # Company news  (via akshare fallback)
    # ------------------------------------------------------------------

    def get_company_news(
        self,
        ticker: str,
        end_date: str,
        start_date: Optional[str] = None,
        limit: int = 1000,
        api_key: str = None,
    ) -> List[CompanyNews]:
        """
        获取公司新闻 (使用 akshare 东方财富新闻源).
        """
        cache_key = f"ef_news_{ticker}_{start_date}_{end_date}_{limit}"
        if cached_data := _cache.get_company_news(cache_key):
            return [CompanyNews(**n) for n in cached_data]

        code = self.normalize_ticker(ticker)
        news_list: list[CompanyNews] = []

        try:
            import akshare as ak
            df = ak.stock_news_em(symbol=code)
            if df is not None and not df.empty:
                for _, row in df.head(limit).iterrows():
                    try:
                        news_list.append(CompanyNews(
                            ticker=ticker,
                            title=str(row.get("新闻标题", "")),
                            author=str(row.get("关键词", "")),
                            source=str(row.get("文章来源", "东方财富")),
                            date=str(row.get("发布时间", "")),
                            url=str(row.get("新闻链接", "")),
                            sentiment=None,
                        ))
                    except Exception:
                        continue
        except ImportError:
            logger.warning("akshare not installed; cannot fetch news.  pip install akshare")
        except Exception as e:
            logger.warning("Failed to fetch news for %s: %s", ticker, e)

        if news_list:
            _cache.set_company_news(cache_key, [n.model_dump() for n in news_list])
        return news_list

    # ------------------------------------------------------------------
    # Insider trades  (via akshare fallback)
    # ------------------------------------------------------------------

    def get_insider_trades(
        self,
        ticker: str,
        end_date: str,
        start_date: Optional[str] = None,
        limit: int = 1000,
        api_key: str = None,
    ) -> List[InsiderTrade]:
        """
        获取内部交易/高管增减持 (使用 akshare).
        """
        cache_key = f"ef_insider_{ticker}_{start_date}_{end_date}_{limit}"
        if cached_data := _cache.get_insider_trades(cache_key):
            return [InsiderTrade(**t) for t in cached_data]

        code = self.normalize_ticker(ticker)
        trades: list[InsiderTrade] = []

        try:
            import akshare as ak
            df = ak.stock_ggcg_em()
            if df is not None and not df.empty:
                stock_trades = df[df["代码"] == code]
                for _, row in stock_trades.head(limit).iterrows():
                    try:
                        change_type = str(row.get("持股变动信息-增减", ""))
                        shares_raw = row.get("持股变动信息-变动数量")
                        try:
                            tx_shares = float(shares_raw) * 10000 if shares_raw else 0
                        except (ValueError, TypeError):
                            tx_shares = 0
                        if change_type == "减持":
                            tx_shares = -abs(tx_shares)
                        elif change_type == "增持":
                            tx_shares = abs(tx_shares)

                        trades.append(InsiderTrade(
                            ticker=ticker,
                            issuer=str(row.get("名称", ticker)),
                            name=str(row.get("股东名称", "")),
                            title="高管/股东",
                            is_board_director=True,
                            transaction_date=str(row.get("变动开始日", "")),
                            transaction_shares=tx_shares,
                            transaction_price_per_share=None,
                            transaction_value=None,
                            shares_owned_before_transaction=None,
                            shares_owned_after_transaction=None,
                            security_title="A股",
                            filing_date=str(row.get("公告日", "")),
                        ))
                    except Exception:
                        continue
        except ImportError:
            logger.warning("akshare not installed; cannot fetch insider trades.  pip install akshare")
        except Exception as e:
            logger.warning("Failed to fetch insider trades for %s: %s", ticker, e)

        if trades:
            _cache.set_insider_trades(cache_key, [t.model_dump() for t in trades])
        return trades

    # ------------------------------------------------------------------
    # Line items  (from financial metrics)
    # ------------------------------------------------------------------

    def search_line_items(
        self,
        ticker: str,
        line_items: List[str],
        end_date: str,
        period: str = "ttm",
        limit: int = 10,
        api_key: str = None,
    ) -> List[LineItem]:
        """搜索财务行项目 (基于 efinance 季度财务数据)."""
        code = self.normalize_ticker(ticker)
        data: dict[str, Any] = {}

        try:
            df = ef.stock.get_all_company_performance()
            if df is not None and not df.empty:
                df["股票代码"] = df["股票代码"].astype(str).str.strip()
                match = df[df["股票代码"] == code]
                if not match.empty:
                    row = match.iloc[-1].to_dict()
                    for item in line_items:
                        mapped = self._map_line_item(item)
                        if mapped and mapped in row:
                            v = row[mapped]
                            if v is not None and v != "" and v != "--":
                                try:
                                    data[item] = float(v)
                                except (ValueError, TypeError):
                                    data[item] = v
        except Exception as e:
            logger.debug("search_line_items(%s) failed: %s", ticker, e)

        if data:
            return [LineItem(ticker=ticker, report_period=end_date, period=period, currency="CNY", **data)]
        return []

    @staticmethod
    def _map_line_item(item: str) -> Optional[str]:
        mapping = {
            "revenue": "营业收入",
            "net_income": "净利润",
            "eps": "每股收益",
            "roe": "净资产收益率",
            "gross_margin": "销售毛利率",
            "revenue_growth": "营业收入同比增长",
            "earnings_growth": "净利润同比增长",
            "book_value_per_share": "每股净资产",
        }
        return mapping.get(item)

    # ------------------------------------------------------------------
    # A-share specific features
    # ------------------------------------------------------------------

    def get_north_money(self, date: str = None) -> pd.DataFrame:
        """北向资金数据 (via akshare)."""
        try:
            import akshare as ak
            df = ak.stock_hsgt_hist_em()
            if date and df is not None and not df.empty:
                col = "日期" if "日期" in df.columns else df.columns[0]
                df = df[df[col] == date]
            return df if df is not None else pd.DataFrame()
        except ImportError:
            logger.warning("akshare not installed")
            return pd.DataFrame()
        except Exception as e:
            logger.warning("get_north_money failed: %s", e)
            return pd.DataFrame()

    def get_stock_list(self, status: str = "1") -> pd.DataFrame:
        """获取股票列表."""
        try:
            df = ef.stock.get_realtime_quotes()
            return df[["股票代码", "股票名称", "市场类型"]].copy() if df is not None else pd.DataFrame()
        except Exception as e:
            logger.warning("get_stock_list failed: %s", e)
            return pd.DataFrame()

    def get_industry_classification(self, ticker: str) -> Optional[Dict[str, Any]]:
        """获取行业信息 (via akshare)."""
        code = self.normalize_ticker(ticker)
        try:
            df = ef.stock.get_base_info(code)
            if df is not None and not df.empty:
                row = df.iloc[0].to_dict() if isinstance(df, pd.DataFrame) else df.to_dict()
                return {
                    "ticker": ticker,
                    "name": row.get("股票简称", ""),
                }
        except Exception:
            pass
        return None

    def get_margin_trading(self, ticker: str, date: str) -> pd.DataFrame:
        """融资融券数据 (efinance 暂无直接接口)."""
        logger.debug("get_margin_trading not directly supported by efinance")
        return pd.DataFrame()

    def get_market_overview(self) -> dict:
        """市场全景概览 (通过 akshare)."""
        import akshare as ak
        from datetime import datetime

        result = {
            "indices": [],
            "market_breadth": {},
            "top_gainers": [],
            "top_losers": [],
            "top_volume": [],
            "updated_at": datetime.now().isoformat(),
        }

        # 指数
        try:
            idx_df = ak.stock_zh_index_spot_em()
            if idx_df is not None and not idx_df.empty:
                targets = ["sh000001", "sz399001", "sz399006", "sh000688", "sh000300"]
                for _, row in idx_df[idx_df["代码"].isin(targets)].iterrows():
                    result["indices"].append({
                        "code": row["代码"], "name": row["名称"],
                        "current": round(float(row["最新价"]), 2),
                        "change_pct": round(float(row["涨跌幅"]), 2),
                    })
        except Exception as e:
            logger.debug("market_overview indices: %s", e)

        # 涨跌统计
        try:
            spot = ak.stock_zh_a_spot_em()
            if spot is not None and not spot.empty:
                total = len(spot)
                up = len(spot[spot["涨跌幅"] > 0])
                down = len(spot[spot["涨跌幅"] < 0])
                result["market_breadth"] = {"total": total, "up": int(up), "down": int(down), "flat": total - up - down}
                result["top_gainers"] = spot.nlargest(5, "涨跌幅")[["代码", "名称", "涨跌幅"]].to_dict(orient="records")
                result["top_losers"] = spot.nsmallest(5, "涨跌幅")[["代码", "名称", "涨跌幅"]].to_dict(orient="records")
                if "成交额" in spot.columns:
                    result["top_volume"] = spot.nlargest(5, "成交额")[["代码", "名称", "成交额"]].to_dict(orient="records")
        except Exception as e:
            logger.debug("market_overview breadth: %s", e)

        return result


# ------------------------------------------------------------------
# Singleton
# ------------------------------------------------------------------
_ef_adapter: Optional[EFDataAdapter] = None


def get_ef_adapter() -> EFDataAdapter:
    global _ef_adapter
    if _ef_adapter is None:
        _ef_adapter = EFDataAdapter()
    return _ef_adapter
