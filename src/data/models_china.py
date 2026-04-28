from pydantic import BaseModel
from typing import Optional
from datetime import date


class NorthMoneyFlow(BaseModel):
    """北向资金流向数据（A股特有）"""
    trade_date: str
    ggt_ss: Optional[float] = None
    ggt_sz: Optional[float] = None
    hgt: Optional[float] = None
    sgt: Optional[float] = None
    north_money: Optional[float] = None
    south_money: Optional[float] = None


class MarginTrading(BaseModel):
    """融资融券数据（A股特有）"""
    ticker: str
    trade_date: str
    rzye: Optional[float] = None
    rzmre: Optional[float] = None
    rzche: Optional[float] = None
    rqye: Optional[float] = None
    rqmcl: Optional[float] = None
    rqchl: Optional[float] = None
    rzrqye: Optional[float] = None


class ChinaStockInfo(BaseModel):
    """A股股票基本信息"""
    ticker: str
    name: str
    area: Optional[str] = None
    industry: Optional[str] = None
    market: Optional[str] = None
    exchange: Optional[str] = None
    list_status: Optional[str] = None
    list_date: Optional[str] = None
    delist_date: Optional[str] = None
    is_hs: Optional[str] = None


class ChinaFinancialMetrics(BaseModel):
    """A股财务指标（扩展版）"""
    ticker: str
    report_period: str
    period: str
    currency: str = 'CNY'
    
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    
    price_to_earnings_ratio: Optional[float] = None
    price_to_book_ratio: Optional[float] = None
    price_to_sales_ratio: Optional[float] = None
    enterprise_value_to_ebitda_ratio: Optional[float] = None
    
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    
    return_on_equity: Optional[float] = None
    return_on_assets: Optional[float] = None
    return_on_invested_capital: Optional[float] = None
    
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    book_value_growth: Optional[float] = None
    earnings_per_share_growth: Optional[float] = None
    
    earnings_per_share: Optional[float] = None
    book_value_per_share: Optional[float] = None
    free_cash_flow_per_share: Optional[float] = None
    
    dividend_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    
    roe_diluted: Optional[float] = None
    roa_diluted: Optional[float] = None
    operating_cycle: Optional[float] = None
    
    net_profit_dedt: Optional[float] = None
    net_profit_dedt_yoy: Optional[float] = None
    
    total_revenue: Optional[float] = None
    total_revenue_yoy: Optional[float] = None
    
    total_assets: Optional[float] = None
    total_liabilities: Optional[float] = None
    total_equity: Optional[float] = None
    
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None
    
    capital_expenditure: Optional[float] = None
    depreciation_amortization: Optional[float] = None


class LimitUpLimitDown(BaseModel):
    """涨跌停数据（A股特有）"""
    ticker: str
    trade_date: str
    close: float
    pct_chg: float
    limit_up: Optional[float] = None
    limit_down: Optional[float] = None
    is_limit_up: bool = False
    is_limit_down: bool = False
    limit_type: Optional[str] = None


class IndustryPerformance(BaseModel):
    """行业表现数据"""
    industry: str
    trade_date: str
    pct_chg: Optional[float] = None
    amount: Optional[float] = None
    turnover_rate: Optional[float] = None
    pe: Optional[float] = None
    pb: Optional[float] = None


class ConceptPerformance(BaseModel):
    """概念板块表现数据"""
    concept: str
    trade_date: str
    pct_chg: Optional[float] = None
    amount: Optional[float] = None
    turnover_rate: Optional[float] = None
    lead_stock: Optional[str] = None
