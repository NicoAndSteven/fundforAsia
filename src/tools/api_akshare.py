"""
akshare 数据适配器
通过 akshare 提供 A 股财务指标、新闻、股东变动等增强数据
作为 efinance 的补充数据源

依赖: akshare>=1.14.0 (可选)
"""
import os
os.environ["AKSHARE_PROGRESS_BAR"] = "F"
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="akshare")

logger = logging.getLogger(__name__)

try:
    import akshare as ak
except ImportError:
    ak = None

from src.data.cache import get_cache
from src.data.models import FinancialMetrics, LineItem, CompanyNews, InsiderTrade

_cache = get_cache()


def _parse_abstract_value(val: Any) -> Optional[float]:
    """解析 akshare 财务摘要中的数值，处理百分比、亿元等单位"""
    if val is None or val is False or val == "" or val == "--":
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if not s:
        return None
    is_pct = False
    if s.endswith("%"):
        is_pct = True
        s = s[:-1].strip()
    if s.endswith("亿"):
        s = s[:-1].strip()
        try:
            v = float(s) * 100_000_000
            return v / 100.0 if is_pct else v
        except ValueError:
            return None
    if s.endswith("万"):
        s = s[:-1].strip()
        try:
            v = float(s) * 10_000
            return v / 100.0 if is_pct else v
        except ValueError:
            return None
    try:
        v = float(s)
        return v / 100.0 if is_pct else v
    except ValueError:
        return None


def _find_substr(seq: list, keyword: str) -> Optional[int]:
    """Find index of first element containing keyword substring."""
    for i, item in enumerate(seq):
        if keyword in str(item):
            return i
    return None


class AKShareAdapter:
    """akshare 数据适配器"""

    def __init__(self):
        pass

    @staticmethod
    def is_available() -> bool:
        return ak is not None

    @staticmethod
    def _market_code(code: str) -> str:
        """Add SH/SZ prefix for akshare financial statement functions."""
        c = code.strip()
        if len(c) != 6:
            return c
        if c.startswith(('6', '9', '5')):
            return f"SH{c}"
        return f"SZ{c}"

    # ──────────────────────────────────────────────────────────
    # Financial metrics
    # ──────────────────────────────────────────────────────────

    def get_financial_metrics(
        self, ticker: str, end_date: str, period: str = "ttm",
        limit: int = 10, api_key: str = None,
    ) -> List[FinancialMetrics]:
        """
        使用 akshare 获取 A 股财务指标。
        数据源: stock_financial_abstract_ths() (比率) + stock_financial_abstract() (原始值)
        """
        if not self.is_available():
            return []

        cache_key = f"ak_financial_{ticker}_{end_date}"
        if cached := _cache.get_financial_metrics(cache_key):
            return [FinancialMetrics(**m) for m in cached]

        code = ticker.strip()
        data = {}

        # ── Source 1: 财务摘要(ths) — 含比率，带%单位 ──
        try:
            df = ak.stock_financial_abstract_ths(symbol=code)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                cols = list(df.columns)
                for keyword, field in [
                    ("净利润", "net_income"),
                    ("净利润同比增长", "earnings_growth"),
                    ("营业总收入", "revenue"),
                    ("营业总收入同比增长", "revenue_growth"),
                    ("基本每股收益", "earnings_per_share"),
                    ("每股净资产", "book_value_per_share"),
                    ("每股经营现金流", "free_cash_flow_per_share"),
                    ("销售净利率", "net_margin"),
                    ("销售毛利率", "gross_margin"),
                    ("净资产收益率", "return_on_equity"),
                    ("流动比率", "current_ratio"),
                    ("速动比率", "quick_ratio"),
                    ("保守速动比率", "cash_ratio"),
                    ("产权比率", "debt_to_equity"),
                    ("资产负债率", "debt_to_assets"),
                ]:
                    idx = _find_substr(cols, keyword)
                    if idx is not None:
                        v = _parse_abstract_value(latest.iloc[idx])
                        if v is not None:
                            data[field] = v
        except Exception as e:
            logger.debug("ths failed %s: %s", ticker, e)

        # ── Source 2: 财务摘要(通用) — 多期原始值(无%单位，直接数值) ──
        raw_fields = {
            "资产总计": "total_assets",
            "负债合计": "total_liabilities",
            "流动资产合计": "current_assets",
            "流动负债合计": "current_liabilities",
            "股东权益合计": "shareholders_equity",
            "净资产": "shareholders_equity",
            "股本": "outstanding_shares",
            "营业总收入": "revenue",
            "净利润": "net_income",
            "经营活动现金流量净额": "operating_cash_flow",
        }
        try:
            df2 = ak.stock_financial_abstract(symbol=code)
            if df2 is not None and not df2.empty and len(df2.columns) >= 3:
                date_cols = [c for c in df2.columns[2:]]
                if date_cols:
                    latest_period = date_cols[0]
                    for _, row in df2.iterrows():
                        indicator = str(row.iloc[1]).strip()
                        for keyword, field in raw_fields.items():
                            if keyword in indicator and field not in data:
                                v = _parse_abstract_value(row[latest_period])
                                if v is not None:
                                    data[field] = v
                                break
        except Exception as e:
            logger.debug("abstract failed %s: %s", ticker, e)

        if not data:
            return []

        metrics = FinancialMetrics(
            ticker=ticker,
            report_period=end_date, period=period, currency="CNY",
            gross_margin=data.get("gross_margin"),
            operating_margin=data.get("operating_margin"),
            net_margin=data.get("net_margin"),
            return_on_equity=data.get("return_on_equity"),
            current_ratio=data.get("current_ratio"),
            quick_ratio=data.get("quick_ratio"),
            cash_ratio=data.get("cash_ratio"),
            debt_to_equity=data.get("debt_to_equity"),
            debt_to_assets=data.get("debt_to_assets"),
            revenue_growth=data.get("revenue_growth"),
            earnings_growth=data.get("earnings_growth"),
            earnings_per_share=data.get("earnings_per_share"),
            book_value_per_share=data.get("book_value_per_share"),
            free_cash_flow_per_share=data.get("free_cash_flow_per_share"),
            market_cap=data.get("market_cap"),
            price_to_earnings_ratio=data.get("price_to_earnings_ratio"),
        )
        result = [metrics]
        _cache.set_financial_metrics(cache_key, [m.model_dump() for m in result])
        return result

    # ──────────────────────────────────────────────────────────
    # Line items (from stock_financial_abstract + financial statements)
    # ──────────────────────────────────────────────────────────

    _BS_FIELDS = {
        "total_assets": "TOTAL_ASSETS",
        "total_liabilities": "TOTAL_LIABILITIES",
        "current_assets": "TOTAL_CURRENT_ASSETS",
        "current_liabilities": "TOTAL_CURRENT_LIAB",
        "shareholders_equity": "TOTAL_EQUITY",
        "cash_and_equivalents": "MONETARYFUNDS",
        "outstanding_shares": "SHARE_CAPITAL",
        "inventory": "INVENTORY",
        "accounts_receivable": "ACCOUNTS_RECE",
        "fixed_assets": "FIXED_ASSET",
        "intangible_assets": "INTANGIBLE_ASSET",
        "goodwill": "GOODWILL",
        "total_debt": None,  # calculated from short + long term borrowings
    }

    _PL_FIELDS = {
        "revenue": "TOTAL_OPERATE_INCOME",
        "operating_income": "OPERATE_PROFIT",
        "total_profit": "TOTAL_PROFIT",
        "net_income": "NETPROFIT",
        "parent_net_income": "PARENT_NETPROFIT",
        "recurring_net_income": "DEDUCT_PARENT_NETPROFIT",
        "interest_expense": "INTEREST_EXPENSE",
        "research_and_development": "RESEARCH_EXPENSE",
        "selling_expense": "SALE_EXPENSE",
        "administrative_expense": "MANAGE_EXPENSE",
        "financing_expense": "FINANCE_EXPENSE",
        "income_tax": "INCOME_TAX",
        "basic_eps": "BASIC_EPS",
        "diluted_eps": "DILUTED_EPS",
        "operate_cost": "OPERATE_COST",
    }

    _CF_FIELDS = {
        "operating_cash_flow": "NETCASH_OPERATE",
        "investing_cash_flow": "NETCASH_INVEST",
        "financing_cash_flow": "NETCASH_FINANCE",
        "capital_expenditure": "CONSTRUCT_LONG_ASSET",
        "free_cash_flow": None,  # calculated: NETCASH_OPERATE - CONSTRUCT_LONG_ASSET
        "dividends_paid": "ASSIGN_DIVIDEND_PORFIT",
        "cc_change": "CCE_ADD",
        "beginning_cash": "BEGIN_CCE",
        "ending_cash": "END_CCE",
    }

    def search_line_items(
        self, ticker: str, line_items: List[str], end_date: str,
        period: str = "ttm", limit: int = 10, api_key: str = None,
    ) -> List[LineItem]:
        """
        搜索财务行项目。
        优先使用三大报表 API（完整、准确），fallback 到 financial_abstract。
        """
        if not self.is_available():
            return []

        key = f"ak_sli_{ticker}_{'_'.join(sorted(line_items))}"
        if cached := _cache.get("line_items", key):
            return [LineItem(**m) for m in cached]

        data = {}
        mkt_code = self._market_code(ticker)

        # ── Source 1: Financial statements (most complete) ──
        try:
            bs = ak.stock_balance_sheet_by_report_em(symbol=mkt_code)
            pl = ak.stock_profit_sheet_by_report_em(symbol=mkt_code)
            cf = ak.stock_cash_flow_sheet_by_report_em(symbol=mkt_code)

            if bs is not None and not bs.empty:
                row = bs.iloc[0]
                for field, col in self._BS_FIELDS.items():
                    if col and row[col] is not None and str(row[col]) != 'nan':
                        data[field] = float(row[col])
                # Calculate total_debt: short/long term borrowings + bonds
                debt = 0
                for dc in ['SHORT_BORROW', 'LONG_BORROW', 'SHORT_BOND_PAYABLE', 'BOND_PAYABLE', 'LEASE_LIAB', 'PERPETUAL_BOND']:
                    if dc in bs.columns and row[dc] is not None and str(row[dc]) != 'nan':
                        debt += float(row[dc])
                if debt > 0:
                    data['total_debt'] = debt

            if pl is not None and not pl.empty:
                row = pl.iloc[0]
                for field, col in self._PL_FIELDS.items():
                    if col and row[col] is not None and str(row[col]) != 'nan':
                        data[field] = float(row[col])
                # Calculate EBITDA: OPERATE_PROFIT + depreciation (approximate with FINANCE_EXPENSE + some estimates)
                # In Chinese reporting, D&A is embedded in costs, not separate
                op_profit = data.get('operating_income', 0)

            if cf is not None and not cf.empty:
                row = cf.iloc[0]
                for field, col in self._CF_FIELDS.items():
                    if col and row[col] is not None and str(row[col]) != 'nan':
                        data[field] = float(row[col])
                # Calculate FCF: operating CF - capex
                oper_cf = data.get('operating_cash_flow', 0)
                capex = data.get('capital_expenditure', 0)
                if oper_cf != 0 and capex != 0:
                    data['free_cash_flow'] = oper_cf - capex

        except Exception as e:
            logger.debug("fin statements failed %s: %s", ticker, e)

        # ── Source 2: stock_financial_abstract (fallback for missing items) ──
        if not all(li in data for li in line_items):
            try:
                df = ak.stock_financial_abstract(symbol=ticker.strip())
                if df is not None and not df.empty and len(df.columns) >= 3:
                    date_cols = [c for c in df.columns[2:]]
                    if date_cols:
                        abs_field_keywords = {
                            "revenue": "营业总收入", "net_income": "净利润",
                            "operating_income": "营业利润", "shareholders_equity": "股东权益合计",
                            "outstanding_shares": "股本",
                            "operating_cash_flow": "经营活动现金流量净额",
                        }
                        indicator_rows = {}
                        for _, row in df.iterrows():
                            indicator_rows[str(row.iloc[1]).strip()] = row
                        for li in line_items:
                            if li not in data:
                                keyword = abs_field_keywords.get(li, li)
                                for ind, row in indicator_rows.items():
                                    if keyword in ind:
                                        v = _parse_abstract_value(row[date_cols[0]])
                                        if v is not None:
                                            data[li] = v
                                        break
            except Exception as e:
                logger.debug("abs fallback failed %s: %s", ticker, e)

        if not data:
            return []

        result = [LineItem(
            ticker=ticker, report_period=end_date,
            period=period, currency="CNY", **data,
        )]
        _cache.set("line_items", key, [m.model_dump() for m in result])
        return result

    # ──────────────────────────────────────────────────────────
    # Company news
    # ──────────────────────────────────────────────────────────

    def get_company_news(
        self, ticker: str, end_date: str,
        start_date: Optional[str] = None, limit: int = 100,
        api_key: str = None,
    ) -> List[CompanyNews]:
        """获取A股公司新闻 (含简单情绪分析)。"""
        if not self.is_available():
            return []

        cache_key = f"ak_news_{ticker}_{end_date}"
        if cached := _cache.get("news", cache_key):
            return [CompanyNews(**n) for n in cached]

        news = []
        try:
            df = ak.stock_news_em(symbol=ticker.strip())
            if df is not None and not df.empty:
                negative_kw = ["下跌", "亏损", "风险", "减持", "利空", "诉讼", "调查"]
                positive_kw = ["上涨", "盈利", "增长", "突破", "利好", "增持"]
                for _, row in df.iterrows():
                    title = str(row.iloc[1]) if len(row) > 1 else ""
                    pub = str(row.iloc[3]) if len(row) > 3 else ""
                    if start_date and pub[:10] < start_date:
                        continue
                    if pub[:10] > end_date:
                        continue
                    if any(k in title for k in negative_kw):
                        sentiment = "negative"
                    elif any(k in title for k in positive_kw):
                        sentiment = "positive"
                    else:
                        sentiment = "neutral"
                    news.append(CompanyNews(
                        ticker=ticker, title=title,
                        source=str(row.iloc[4]) if len(row) > 4 else "东方财富",
                        date=pub[:19] if pub else end_date,
                        url=str(row.iloc[5]) if len(row) > 5 else "",
                        sentiment=sentiment,
                    ))
                    if len(news) >= limit:
                        break
        except Exception as e:
            logger.debug("news failed %s: %s", ticker, e)

        if news:
            _cache.set("news", cache_key, [n.model_dump() for n in news])
        return news

    # ──────────────────────────────────────────────────────────
    # Insider trades
    # ──────────────────────────────────────────────────────────

    def get_insider_trades(
        self, ticker: str, end_date: str,
        start_date: Optional[str] = None, limit: int = 1000,
        api_key: str = None,
    ) -> List[InsiderTrade]:
        """获取股东增减持数据。"""
        if not self.is_available():
            return []

        cache_key = f"ak_insider_{ticker}_{end_date}"
        if cached := _cache.get("insider_trades", cache_key):
            return [InsiderTrade(**t) for t in cached]

        trades = []
        try:
            df = ak.stock_shareholder_change_ths(symbol=ticker.strip())
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    ad = str(row.iloc[0]) if len(row) > 0 else ""
                    if ad:
                        if start_date and ad[:10] < start_date:
                            continue
                        if ad[:10] > end_date:
                            continue
                    trades.append(InsiderTrade(
                        ticker=ticker,
                        issuer=str(row.iloc[1]) if len(row) > 1 else None,
                        transaction_shares=_parse_abstract_value(row.iloc[2]) if len(row) > 2 else None,
                        transaction_price_per_share=_parse_abstract_value(row.iloc[3]) if len(row) > 3 else None,
                        filing_date=ad[:10] if ad else end_date,
                        transaction_date=ad[:10] if ad else None,
                    ))
                    if len(trades) >= limit:
                        break
        except Exception as e:
            logger.debug("insider failed %s: %s", ticker, e)

        if trades:
            _cache.set("insider_trades", cache_key, [t.model_dump() for t in trades])
        return trades


# ── Singleton ──
_ak_adapter: Optional[AKShareAdapter] = None


def get_ak_adapter() -> AKShareAdapter:
    global _ak_adapter
    if _ak_adapter is None:
        _ak_adapter = AKShareAdapter()
    return _ak_adapter
