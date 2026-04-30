"""
efinance 数据适配器
基于东方财富的免费实时数据源
支持 A 股/美股/港股的实时行情, 无需 API Key
"""
import logging
from typing import List, Optional, Dict, Any
import pandas as pd
import warnings
from datetime import datetime, timedelta

# Suppress pandas FutureWarning from efinance concat (module-based to avoid multiline regex issues)
warnings.filterwarnings("ignore", category=FutureWarning, module="efinance")

try:
    import efinance as ef
except Exception:
    ef = None

from src.data.cache import get_cache
from src.data.models import Price, FinancialMetrics, InsiderTrade, CompanyNews, LineItem

logger = logging.getLogger(__name__)
_cache = get_cache()

# 东方财富行业/概念板块代码（申万分类 + 热门题材）
# 通过 push2.eastmoney.com/api/qt/ulist.np/get 接口批量查询
_INDUSTRY_PLATE_CODES = [
    # ── 传统行业板块 (BK04xx-BK05xx) ──
    "BK0420", "BK0421", "BK0422", "BK0424", "BK0425", "BK0427", "BK0428", "BK0429",
    "BK0433", "BK0436", "BK0437", "BK0438", "BK0440", "BK0447", "BK0448",
    "BK0450", "BK0451", "BK0454", "BK0456", "BK0457", "BK0458", "BK0459",
    "BK0464", "BK0465", "BK0470", "BK0471",
    "BK0473", "BK0474", "BK0475", "BK0476", "BK0477", "BK0478", "BK0479",
    "BK0480", "BK0481", "BK0482", "BK0484", "BK0485", "BK0486",
    "BK0490", "BK0492", "BK0493", "BK0494",
    "BK0498", "BK0499", "BK0500", "BK0501", "BK0505", "BK0506", "BK0509",
    "BK0511", "BK0512", "BK0514", "BK0519", "BK0520", "BK0523", "BK0524",
    "BK0525", "BK0528", "BK0534", "BK0535", "BK0536", "BK0538", "BK0539",
    "BK0545", "BK0546", "BK0547", "BK0548", "BK0549", "BK0552", "BK0554",
    "BK0556", "BK0566", "BK0567", "BK0568",
    "BK0574", "BK0577", "BK0578", "BK0579", "BK0580", "BK0581", "BK0588",
    "BK0590", "BK0592", "BK0594", "BK0595", "BK0596", "BK0597",
    # ── 新兴行业 / 题材板块 (BK06xx-BK07xx) ──
    "BK0600", "BK0601", "BK0603", "BK0604", "BK0606",
    "BK0610", "BK0611", "BK0612", "BK0614", "BK0615", "BK0617", "BK0619",
    "BK0622", "BK0623", "BK0625", "BK0628", "BK0629", "BK0632", "BK0634",
    "BK0636", "BK0637", "BK0638", "BK0641", "BK0643", "BK0644",
    "BK0653", "BK0655", "BK0656", "BK0662", "BK0664", "BK0665", "BK0666",
    "BK0667", "BK0668", "BK0669", "BK0671", "BK0672", "BK0674", "BK0675",
    "BK0676", "BK0677", "BK0679", "BK0680", "BK0682", "BK0683", "BK0684",
    "BK0685", "BK0689", "BK0690", "BK0692", "BK0693", "BK0695", "BK0696",
    "BK0697", "BK0698", "BK0699", "BK0700", "BK0701", "BK0703", "BK0704",
    "BK0705", "BK0706", "BK0707", "BK0708", "BK0710", "BK0711", "BK0712",
    "BK0714", "BK0715", "BK0718", "BK0721", "BK0722", "BK0724", "BK0725",
    "BK0726", "BK0727", "BK0728", "BK0729", "BK0730", "BK0731", "BK0732",
    "BK0733", "BK0734", "BK0735", "BK0736", "BK0737", "BK0738", "BK0739",
    "BK0740", "BK0742", "BK0743",
    # ── 科技 / 热门题材板块 (BK08xx-BK09xx) ──
    "BK0800", "BK0801", "BK0802", "BK0803", "BK0804", "BK0805", "BK0806",
    "BK0807", "BK0808", "BK0809", "BK0811", "BK0812", "BK0813", "BK0814",
    "BK0815", "BK0816", "BK0817", "BK0818", "BK0821", "BK0822", "BK0823",
    "BK0825", "BK0830", "BK0832", "BK0833", "BK0834", "BK0835", "BK0837",
    "BK0838", "BK0839", "BK0840", "BK0841", "BK0843", "BK0845", "BK0847",
    "BK0852", "BK0853", "BK0854", "BK0855", "BK0856", "BK0859", "BK0860",
    "BK0861", "BK0864", "BK0865", "BK0866", "BK0867", "BK0868", "BK0870",
    "BK0872", "BK0873", "BK0875", "BK0877", "BK0879", "BK0880", "BK0881",
    "BK0882", "BK0883", "BK0884", "BK0885", "BK0886", "BK0887", "BK0888",
    "BK0889", "BK0890", "BK0891", "BK0892", "BK0893", "BK0894", "BK0895",
    "BK0896", "BK0897", "BK0898", "BK0899",
    "BK0900", "BK0901", "BK0902", "BK0905", "BK0906", "BK0907", "BK0908",
    "BK0909", "BK0910", "BK0914", "BK0915", "BK0916", "BK0917", "BK0918",
    "BK0920", "BK0921", "BK0922", "BK0923", "BK0924", "BK0925", "BK0926",
    "BK0927", "BK0932", "BK0933", "BK0935", "BK0936", "BK0937", "BK0938",
    "BK0939", "BK0940", "BK0943", "BK0944", "BK0945", "BK0946", "BK0947",
    "BK0948", "BK0949", "BK0950", "BK0951", "BK0952", "BK0953", "BK0954",
    "BK0955", "BK0957", "BK0958", "BK0959", "BK0960", "BK0961", "BK0963",
    "BK0964", "BK0965", "BK0966", "BK0967", "BK0968", "BK0969", "BK0970",
    "BK0972", "BK0974", "BK0975", "BK0976", "BK0977", "BK0979", "BK0980",
    "BK0981", "BK0982", "BK0983", "BK0984", "BK0985", "BK0986", "BK0988",
    "BK0989", "BK0990", "BK0991", "BK0992", "BK0993", "BK0994", "BK0995",
    "BK0996", "BK0998", "BK0999",
]


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

        # 每股经营现金流量 (operating CF per share)
        oper_cf_ps = _val(perf, "每股经营现金流量")

        metrics = FinancialMetrics(
            ticker=ticker,
            report_period=str(perf.get("公告日期", end_date))[:10] if perf else end_date,
            period=period,
            currency="CNY",
            market_cap=market_cap,
            enterprise_value=market_cap,
            price_to_earnings_ratio=pe_ratio,
            price_to_book_ratio=None,
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
            current_ratio=None,
            quick_ratio=None,
            debt_to_equity=None,
            revenue_growth=_val(perf, "营业收入同比增长"),
            earnings_growth=_val(perf, "净利润同比增长"),
            earnings_per_share=_val(perf, "每股收益"),
            book_value_per_share=_val(perf, "每股净资产"),
            free_cash_flow_per_share=oper_cf_ps,
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
    # Company news  (暂不可用，efinance 无新闻 API)
    # ------------------------------------------------------------------

    def get_company_news(self, ticker: str, end_date: str, start_date: Optional[str] = None, limit: int = 1000, api_key: str = None) -> List[CompanyNews]:
        """获取公司新闻 (efinance 不提供新闻数据，返回空列表)."""
        return []

    # ------------------------------------------------------------------
    # Insider trades  (暂不可用，efinance 无增减持 API)
    # ------------------------------------------------------------------

    def get_insider_trades(self, ticker: str, end_date: str, start_date: Optional[str] = None, limit: int = 1000, api_key: str = None) -> List[InsiderTrade]:
        """获取内部交易/高管增减持 (efinance 不提供，返回空列表)."""
        return []

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
            # ── Income Statement ──
            "revenue": "营业收入",
            "net_income": "净利润",
            "eps": "每股收益",
            "earnings_per_share": "每股收益",
            "roe": "净资产收益率",
            "gross_margin": "销售毛利率",
            "revenue_growth": "营业收入同比增长",
            "earnings_growth": "净利润同比增长",
            "book_value_per_share": "每股净资产",
            "operating_cash_flow_per_share": "每股经营现金流量",
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
        """市场全景概览 (通过 efinance / 东方财富 HTTPS API)."""
        from datetime import datetime
        import requests as req

        now = datetime.now()
        result = {
            "indices": [],
            "market_breadth": {},
            "sectors": [],
            "top_gainers": [],
            "top_losers": [],
            "top_volume": [],
            "market_summary": {},
            "limit_up_count": 0,
            "limit_down_count": 0,
            "updated_at": now.isoformat(),
        }

        api_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://quote.eastmoney.com/",
        }

        # ── 指数数据 ──
        # 通过 https://push2.eastmoney.com/api/qt/ulist.np/get 接口，
        # 使用带市场前缀的 ID（1=上交所, 0=深交所）获取指数实时行情
        index_map = {
            "1.000001": "上证指数",
            "0.399001": "深证成指",
            "0.399006": "创业板指",
            "1.000688": "科创50",
            "1.000300": "沪深300",
            "1.000016": "上证50",
        }
        try:
            url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            params = {
                "OSVersion": "14.3",
                "appVersion": "6.3.8",
                "fields": "f12,f14,f3,f2,f4,f15,f16",
                "fltt": "2",
                "plat": "Iphone",
                "product": "EFund",
                "secids": ",".join(index_map),
                "serverVersion": "6.3.6",
                "version": "6.3.8",
            }
            resp = req.get(url, params=params, timeout=10, headers=api_headers)
            if resp.status_code == 200:
                payload = resp.json()
                for item in payload.get("data", {}).get("diff", []):
                    code = item.get("f12", "")
                    name = item.get("f14", "")
                    current = item.get("f2")
                    chg_pct = item.get("f3")
                    if current is None or chg_pct is None:
                        continue
                    result["indices"].append({
                        "code": code,
                        "name": name,
                        "current": round(float(current), 2),
                        "change": round(float(item.get("f4", 0)), 2) if item.get("f4") else 0,
                        "change_pct": round(float(chg_pct), 2),
                        "high": round(float(item.get("f15", 0)), 2) if item.get("f15") else 0,
                        "low": round(float(item.get("f16", 0)), 2) if item.get("f16") else 0,
                    })
        except Exception as e:
            logger.warning("获取指数数据失败: %s", e)

        # ── 全市场实时行情（涨跌分布、涨幅榜等）──
        # 部分网络环境会阻断 HTTP 80 端口，快速失败后走替补方案
        market_data = None
        try:
            # 临时提升 urllib3 日志级别，避免重试阶段的 WARNING 刷屏
            urllib3_logger = logging.getLogger("urllib3.connectionpool")
            old_level = urllib3_logger.level
            urllib3_logger.setLevel(logging.ERROR)
        except Exception:
            pass
        try:
            import efinance as ef
            df = ef.stock.get_realtime_quotes()
            if df is not None and not df.empty:
                market_data = df
        except Exception as e:
            logger.debug("get_realtime_quotes() 失败，尝试替补方案: %s", e)
        finally:
            try:
                urllib3_logger.setLevel(old_level)
            except Exception:
                pass

        if market_data is None:
            # 替补：通过 ulist.np/get 接口批量查询热门股票
            try:
                url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
                # 获取各板块代表性股票 + 热门个股
                hot_codes = [
                    "1.600519", "0.300750", "0.000858",  # 贵州茅台、宁德时代、五粮液
                    "1.601318", "0.000333", "1.600036",  # 中国平安、美的集团、招商银行
                    "0.002415", "1.600900", "0.300059",  # 海康威视、长江电力、东方财富
                    "1.601166", "1.601899", "0.000568",  # 兴业银行、紫金矿业、泸州老窖
                    "1.600276", "0.002594", "1.601012",  # 恒瑞医药、比亚迪、隆基绿能
                    "1.603259", "0.300124", "0.002475",  # 药明康德、汇川技术、立讯精密
                    "1.600809", "1.601088", "1.600030",  # 山西汾酒、中国神华、中信证券
                    "0.001979", "1.600585", "1.600887",  # 招商蛇口、海螺水泥、伊利股份
                    "0.300015", "0.002714", "1.603288",  # 爱尔眼科、牧原股份、海天味业
                    "0.300274", "0.000651", "1.601985",  # 阳光电源、格力电器、中国核电
                ]
                params = {
                    "OSVersion": "14.3",
                    "appVersion": "6.3.8",
                    "fields": "f12,f14,f3,f2,f15,f16,f17,f4,f8,f5,f6,f10,f20,f21",
                    "fltt": "2",
                    "plat": "Iphone",
                    "product": "EFund",
                    "secids": ",".join(hot_codes),
                    "serverVersion": "6.3.6",
                    "version": "6.3.8",
                }
                resp2 = req.get(url, params=params, timeout=10, headers=api_headers)
                if resp2.status_code == 200:
                    payload2 = resp2.json()
                    rows = payload2.get("data", {}).get("diff", [])
                    if rows:
                        import pandas as pd
                        df2 = pd.DataFrame(rows)
                        df2.rename(columns={
                            "f12": "股票代码", "f14": "股票名称",
                            "f3": "涨跌幅", "f2": "最新价",
                            "f15": "最高", "f16": "最低", "f17": "今开",
                            "f4": "涨跌额", "f8": "换手率",
                            "f5": "成交量", "f6": "成交额",
                            "f10": "量比", "f20": "总市值",
                            "f21": "流通市值",
                        }, inplace=True)
                        market_data = df2
            except Exception as e2:
                logger.debug("替补行情也失败: %s", e2)

        if market_data is not None:
            try:
                total = len(market_data)
                up = len(market_data[market_data["涨跌幅"] > 0]) if "涨跌幅" in market_data.columns else 0
                down = len(market_data[market_data["涨跌幅"] < 0]) if "涨跌幅" in market_data.columns else 0
                if len(market_data) > 200:  # 全市场约 5000 只，替补仅 30 只，不够代表性
                    result["market_breadth"] = {
                        "total": int(total),
                        "up": int(up),
                        "down": int(down),
                        "flat": int(total - up - down),
                        "up_ratio": round(up / total * 100, 1) if total > 0 else 0,
                    }

                if "涨跌幅" in market_data.columns:
                    result["top_gainers"] = market_data.nlargest(5, "涨跌幅")[
                        ["股票代码", "股票名称", "涨跌幅"]
                    ].rename(columns={"股票代码": "代码", "股票名称": "名称"}).to_dict(orient="records")
                    result["top_losers"] = market_data.nsmallest(5, "涨跌幅")[
                        ["股票代码", "股票名称", "涨跌幅"]
                    ].rename(columns={"股票代码": "代码", "股票名称": "名称"}).to_dict(orient="records")
                if "成交额" in market_data.columns:
                    vol_df = market_data.nlargest(5, "成交额")[
                        ["股票代码", "股票名称", "成交额"]
                    ].rename(columns={"股票代码": "代码", "股票名称": "名称"})
                    vol_df["成交额"] = vol_df["成交额"].apply(
                        lambda x: f"{x/1e8:.1f}亿" if x >= 1e8 else f"{x/1e4:.0f}万"
                    )
                    result["top_volume"] = vol_df.to_dict(orient="records")
                    total_vol = market_data["成交额"].sum()
                    result["market_summary"] = {
                        "total_volume": float(total_vol),
                        "total_volume_str": f"{total_vol/1e8:.0f}亿",
                    }
            except Exception as e3:
                logger.debug("处理行情数据失败: %s", e3)

        # ── 行业板块排名 ──
        # 通过 ulist.np/get 批量获取板块行情（clint/get 端点已不再可用）
        try:
            from itertools import islice

            def batched(iterable, n):
                it = iter(iterable)
                while batch := list(islice(it, n)):
                    yield batch

            url = "https://push2.eastmoney.com/api/qt/ulist.np/get"
            all_sectors = []
            for batch in batched(_INDUSTRY_PLATE_CODES, 50):
                params = {
                    "fltt": "2",
                    "np": "1",
                    "fields": "f12,f14,f3,f104,f105,f128,f20,f6",
                    "secids": ",".join(f"90.{c}" for c in batch),
                }
                resp = req.get(url, params=params, timeout=10, headers=api_headers)
                if resp.status_code == 200:
                    payload = resp.json()
                    for item in payload.get("data", {}).get("diff", []):
                        chg = item.get("f3")
                        if chg is None:
                            continue
                        all_sectors.append({
                            "板块名称": item.get("f14", ""),
                            "板块代码": item.get("f12", ""),
                            "涨跌幅": round(float(chg), 2),
                            "上涨家数": item.get("f104") or 0,
                            "下跌家数": item.get("f105") or 0,
                            "领涨股票": item.get("f128", ""),
                            "总市值": item.get("f20"),
                            "成交额": item.get("f6"),
                        })
            # 按涨跌幅降序排列
            all_sectors.sort(key=lambda x: x["涨跌幅"], reverse=True)
            result["sectors"] = all_sectors

            # ── 板块宽度：用板块涨跌作为市场宽度替代指标 ──
            sector_up = sum(1 for s in all_sectors if s["涨跌幅"] > 0)
            sector_down = sum(1 for s in all_sectors if s["涨跌幅"] < 0)
            sector_flat = len(all_sectors) - sector_up - sector_down
            sector_breadth = {
                "total": len(all_sectors),
                "up": sector_up,
                "down": sector_down,
                "flat": sector_flat,
                "up_ratio": round(sector_up / len(all_sectors) * 100, 1) if all_sectors else 0,
            }
            # 如果个股级宽度为空，则使用板块宽度作为替补
            if not result.get("market_breadth"):
                result["market_breadth"] = sector_breadth
                result["market_breadth"]["source"] = "sectors"
            else:
                result["market_breadth"]["source"] = "stocks"
            result["sector_breadth"] = sector_breadth
        except Exception as e4:
            logger.debug("获取板块排名失败: %s", e4)

        return result


    def get_sector_stocks(self, sector_code: str) -> List[str]:
        """获取指定板块的所有成分股代码。

        通过东方财富 HTTP API 获取板块成分股列表。

        Args:
            sector_code: 板块代码，如 "BK0420"（半导体）

        Returns:
            股票代码列表，如 ["600519", "000001", ...]
        """
        import requests as req

        api_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://quote.eastmoney.com/",
        }

        url = "https://push2.eastmoney.com/api/qt/clist/get"
        all_stocks: List[str] = []

        try:
            params = {
                "pn": "1",
                "pz": "2000",      # 一次性获取足够多的记录
                "np": "1",
                "fltt": "2",
                "invt": "2",
                "fields": "f12",   # f12 = 股票代码
                "fid": "f3",
                "po": "1",
                "fs": f"b:{sector_code}",
            }
            resp = req.get(url, params=params, timeout=15, headers=api_headers)
            if resp.status_code == 200:
                payload = resp.json()
                items = payload.get("data", {}).get("diff", [])
                for item in items:
                    code = item.get("f12", "")
                    if code:
                        all_stocks.append(str(code).strip())
        except Exception as e:
            logger.error("获取板块(%s)成分股失败: %s", sector_code, e)

        return all_stocks


# ------------------------------------------------------------------
# Singleton
# ------------------------------------------------------------------
_ef_adapter: Optional[EFDataAdapter] = None


def get_ef_adapter() -> EFDataAdapter:
    global _ef_adapter
    if _ef_adapter is None:
        _ef_adapter = EFDataAdapter()
    return _ef_adapter
