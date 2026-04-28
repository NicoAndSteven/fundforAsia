"""
A股Agent集成测试脚本
测试各个Agent能否正确使用A股数据
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.api_unified import (
    get_prices,
    get_financial_metrics,
    get_market_cap,
    prices_to_df,
)


def test_technicals_data():
    """测试技术分析Agent所需数据"""
    print("\n" + "=" * 60)
    print("测试: 技术分析Agent数据获取")
    print("=" * 60)
    
    ticker = "000001"
    end_date = "2024-03-31"
    start_date = "2024-01-01"
    
    print(f"股票代码: {ticker}")
    print(f"日期范围: {start_date} ~ {end_date}")
    
    prices = get_prices(ticker, start_date, end_date)
    
    if prices:
        df = prices_to_df(prices)
        print(f"\n[OK] 成功获取 {len(prices)} 条价格数据")
        print(f"DataFrame形状: {df.shape}")
        print(f"日期范围: {df.index.min()} ~ {df.index.max()}")
        return True
    else:
        print("[FAIL] 获取价格数据失败")
        return False


def test_fundamentals_data():
    """测试基本面分析Agent所需数据"""
    print("\n" + "=" * 60)
    print("测试: 基本面分析Agent数据获取")
    print("=" * 60)
    
    ticker = "000001"
    end_date = "2024-03-31"
    
    print(f"股票代码: {ticker}")
    print(f"结束日期: {end_date}")
    
    metrics = get_financial_metrics(ticker, end_date)
    
    if metrics:
        m = metrics[0]
        print(f"\n[OK] 成功获取财务指标")
        
        available_fields = []
        missing_fields = []
        
        fields_to_check = [
            ('ticker', m.ticker),
            ('market_cap', m.market_cap),
            ('price_to_earnings_ratio', m.price_to_earnings_ratio),
            ('price_to_book_ratio', m.price_to_book_ratio),
            ('return_on_equity', m.return_on_equity),
            ('return_on_assets', m.return_on_assets),
            ('gross_margin', m.gross_margin),
            ('net_margin', m.net_margin),
            ('current_ratio', m.current_ratio),
            ('debt_to_equity', m.debt_to_equity),
            ('earnings_per_share', m.earnings_per_share),
            ('book_value_per_share', m.book_value_per_share),
            ('revenue_growth', m.revenue_growth),
            ('earnings_growth', m.earnings_growth),
        ]
        
        for name, value in fields_to_check:
            if value is not None:
                available_fields.append(name)
            else:
                missing_fields.append(name)
        
        print(f"可用字段 ({len(available_fields)}): {', '.join(available_fields)}")
        if missing_fields:
            print(f"缺失字段 ({len(missing_fields)}): {', '.join(missing_fields)}")
        
        return len(available_fields) > 0
    else:
        print("[FAIL] 获取财务指标失败")
        return False


def test_valuation_data():
    """测试估值Agent所需数据"""
    print("\n" + "=" * 60)
    print("测试: 估值Agent数据获取")
    print("=" * 60)
    
    ticker = "000001"
    end_date = "2024-03-31"
    
    print(f"股票代码: {ticker}")
    
    market_cap = get_market_cap(ticker, end_date)
    
    if market_cap:
        print(f"\n[OK] 成功获取市值: {market_cap:.2f} 亿元")
        return True
    else:
        print("[FAIL] 获取市值失败")
        return False


def test_sentiment_data():
    """测试情绪分析Agent所需数据"""
    print("\n" + "=" * 60)
    print("测试: 情绪分析Agent数据获取")
    print("=" * 60)
    
    from src.tools.api_unified import get_insider_trades, get_company_news
    
    ticker = "000001"
    end_date = "2024-03-31"
    
    print(f"股票代码: {ticker}")
    
    insider_trades = get_insider_trades(ticker, end_date)
    print(f"\n内部交易数据: {len(insider_trades)} 条 (BaoStock不支持此数据)")
    
    company_news = get_company_news(ticker, end_date, limit=5)
    print(f"公司新闻数据: {len(company_news)} 条")
    
    if company_news:
        print("[OK] 新闻数据可用（需要akshare）")
        return True
    else:
        print("[WARN] 新闻数据不可用，情绪分析可能受限")
        return True


def test_risk_manager_data():
    """测试风险管理Agent所需数据"""
    print("\n" + "=" * 60)
    print("测试: 风险管理Agent数据获取")
    print("=" * 60)
    
    ticker = "000001"
    end_date = "2024-03-31"
    start_date = "2024-01-01"
    
    print(f"股票代码: {ticker}")
    
    prices = get_prices(ticker, start_date, end_date)
    
    if prices:
        df = prices_to_df(prices)
        returns = df['close'].pct_change().dropna()
        volatility = returns.std() * (252 ** 0.5)
        
        print(f"\n[OK] 成功计算风险指标")
        print(f"数据点数: {len(prices)}")
        print(f"年化波动率: {volatility:.2%}")
        return True
    else:
        print("[FAIL] 获取价格数据失败")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("A股 Agent集成测试")
    print("测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    results = []
    
    results.append(("技术分析数据", test_technicals_data()))
    results.append(("基本面分析数据", test_fundamentals_data()))
    results.append(("估值分析数据", test_valuation_data()))
    results.append(("情绪分析数据", test_sentiment_data()))
    results.append(("风险管理数据", test_risk_manager_data()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n所有测试通过！Agent可以正常使用A股数据。")
    else:
        print(f"\n有 {total - passed} 个测试失败，部分功能可能受限。")


if __name__ == "__main__":
    main()
