"""
统一数据API接口
数据源：efinance（东方财富，实时A股/美股/港股数据，无需API Key）
"""
from __future__ import annotations
from typing import List, Optional
import pandas as pd
from src.data.models import Price, FinancialMetrics, InsiderTrade, CompanyNews, LineItem
from src.tools.api_efinance import get_ef_adapter


def prices_to_df(prices: List[Price]) -> pd.DataFrame:
    """Convert a list of Price objects to a DataFrame."""
    if not prices:
        return pd.DataFrame()
    df = pd.DataFrame([p.model_dump() for p in prices])
    df["Date"] = pd.to_datetime(df["time"])
    df = df.set_index("Date")
    for col in ["open", "close", "high", "low", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_prices(
    ticker: str,
    start_date: str,
    end_date: str,
    api_key: str = None
) -> List[Price]:
    """获取A股价格数据"""
    adapter = get_ef_adapter()
    return adapter.get_prices(ticker, start_date, end_date, api_key)


def get_financial_metrics(
    ticker: str,
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
    api_key: str = None,
) -> List[FinancialMetrics]:
    """获取A股财务指标数据"""
    adapter = get_ef_adapter()
    return adapter.get_financial_metrics(ticker, end_date, period, limit, api_key)


def get_insider_trades(
    ticker: str,
    end_date: str,
    start_date: Optional[str] = None,
    limit: int = 1000,
    api_key: str = None,
) -> List[InsiderTrade]:
    """获取A股高管持股变动数据"""
    adapter = get_ef_adapter()
    return adapter.get_insider_trades(ticker, end_date, start_date, limit, api_key)


def get_company_news(
    ticker: str,
    end_date: str,
    start_date: Optional[str] = None,
    limit: int = 1000,
    api_key: str = None,
) -> List[CompanyNews]:
    """获取A股公司新闻数据"""
    adapter = get_ef_adapter()
    return adapter.get_company_news(ticker, end_date, start_date, limit, api_key)


def get_market_overview() -> dict:
    """获取A股市场全景概览数据（指数、板块、涨跌统计等）"""
    adapter = get_ef_adapter()
    return adapter.get_market_overview()


def get_market_cap(
    ticker: str,
    end_date: str,
    api_key: str = None,
) -> Optional[float]:
    """获取A股市值"""
    adapter = get_ef_adapter()
    return adapter.get_market_cap(ticker, end_date, api_key)


def search_line_items(
    ticker: str,
    line_items: List[str],
    end_date: str,
    period: str = "ttm",
    limit: int = 10,
    api_key: str = None,
) -> List[LineItem]:
    """搜索A股财务报表行项目"""
    adapter = get_ef_adapter()
    return adapter.search_line_items(ticker, line_items, end_date, period, limit, api_key)


def get_price_data(
    ticker: str,
    start_date: str,
    end_date: str,
    api_key: str = None
) -> pd.DataFrame:
    """获取A股价格数据并转换为DataFrame"""
    prices = get_prices(ticker, start_date, end_date, api_key)
    return prices_to_df(prices)


def get_north_money(date: str = None) -> pd.DataFrame:
    """获取北向资金数据"""
    adapter = get_ef_adapter()
    return adapter.get_north_money(date)


def get_margin_trading(ticker: str, date: str) -> pd.DataFrame:
    """获取融资融券数据"""
    adapter = get_ef_adapter()
    return adapter.get_margin_trading(ticker, date)


def get_industry_classification(ticker: str) -> Optional[dict]:
    """获取行业分类信息"""
    adapter = get_ef_adapter()
    return adapter.get_industry_classification(ticker)


def get_stock_list(status: str = '1') -> pd.DataFrame:
    """获取A股股票列表"""
    adapter = get_ef_adapter()
    return adapter.get_stock_list(status)


def get_intraday_prices(
    ticker: str,
    date: str,
    frequency: str = "5",
    api_key: str = None
) -> List[Price]:
    """
    获取A股分钟级K线数据

    Args:
        ticker: 股票代码
        date: 日期 (YYYY-MM-DD)
        frequency: 频率，可选 "5" / "15" / "30" / "60" 分钟
        api_key: 保留参数，未使用

    Returns:
        分钟级价格数据列表
    """
    adapter = get_ef_adapter()
    return adapter.get_intraday_prices(ticker, date, frequency, api_key)


def get_sector_stocks(sector_code: str) -> List[str]:
    """获取指定板块的所有成分股代码。

    Args:
        sector_code: 板块代码，如 "BK0420"（半导体）

    Returns:
        股票代码列表
    """
    adapter = get_ef_adapter()
    return adapter.get_sector_stocks(sector_code)
