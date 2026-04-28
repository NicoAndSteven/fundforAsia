"""
A股完整交易流程测试脚本
测试数据流是否正常工作
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.api_unified import (
    get_prices,
    get_financial_metrics,
    get_market_cap,
    get_insider_trades,
    get_company_news,
    prices_to_df,
)


def test_data_flow_for_trading():
    """测试交易所需的数据流"""
    print("\n" + "=" * 80)
    print("A股完整交易流程数据测试")
    print("=" * 80)
    
    tickers = ["000001", "600000"]
    end_date = "2024-03-31"
    start_date = "2024-01-01"
    
    print(f"\n测试股票: {', '.join(tickers)}")
    print(f"日期范围: {start_date} ~ {end_date}")
    
    all_results = {}
    
    for ticker in tickers:
        print(f"\n{'='*60}")
        print(f"处理股票: {ticker}")
        print(f"{'='*60}")
        
        results = {}
        
        # 1. 价格数据
        print(f"\n[1/5] 获取价格数据...")
        prices = get_prices(ticker, start_date, end_date)
        if prices:
            df = prices_to_df(prices)
            results['prices'] = {
                'count': len(prices),
                'start': str(df.index.min()),
                'end': str(df.index.max()),
                'latest_close': float(df['close'].iloc[-1]),
            }
            print(f"  成功获取 {len(prices)} 条价格数据")
            print(f"  最新收盘价: {df['close'].iloc[-1]:.2f}")
        else:
            results['prices'] = None
            print(f"  获取价格数据失败")
        
        # 2. 财务指标
        print(f"\n[2/5] 获取财务指标...")
        metrics = get_financial_metrics(ticker, end_date)
        if metrics:
            m = metrics[0]
            results['metrics'] = {
                'market_cap': m.market_cap,
                'pe_ratio': m.price_to_earnings_ratio,
                'pb_ratio': m.price_to_book_ratio,
                'roe': m.return_on_equity,
                'net_margin': m.net_margin,
                'eps': m.earnings_per_share,
            }
            print(f"  市值: {m.market_cap:.2f} 亿元" if m.market_cap else "  市值: N/A")
            print(f"  ROE: {m.return_on_equity:.2f}%" if m.return_on_equity else "  ROE: N/A")
            print(f"  净利率: {m.net_margin:.2f}%" if m.net_margin else "  净利率: N/A")
            print(f"  EPS: {m.earnings_per_share:.2f}" if m.earnings_per_share else "  EPS: N/A")
        else:
            results['metrics'] = None
            print(f"  获取财务指标失败")
        
        # 3. 市值
        print(f"\n[3/5] 获取市值...")
        market_cap = get_market_cap(ticker, end_date)
        if market_cap:
            results['market_cap'] = market_cap
            print(f"  市值: {market_cap:.2f} 亿元")
        else:
            results['market_cap'] = None
            print(f"  获取市值失败")
        
        # 4. 内部交易
        print(f"\n[4/5] 获取内部交易数据...")
        insider_trades = get_insider_trades(ticker, end_date)
        results['insider_trades'] = len(insider_trades)
        print(f"  内部交易记录: {len(insider_trades)} 条 (BaoStock不支持)")
        
        # 5. 公司新闻
        print(f"\n[5/5] 获取公司新闻...")
        news = get_company_news(ticker, end_date, limit=5)
        results['news'] = len(news)
        print(f"  新闻记录: {len(news)} 条")
        
        all_results[ticker] = results
    
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    for ticker, results in all_results.items():
        print(f"\n{ticker}:")
        prices_ok = results['prices'] is not None
        metrics_ok = results['metrics'] is not None
        market_cap_ok = results['market_cap'] is not None
        
        print(f"  价格数据: {'OK' if prices_ok else 'FAIL'}")
        print(f"  财务指标: {'OK' if metrics_ok else 'FAIL'}")
        print(f"  市值数据: {'OK' if market_cap_ok else 'FAIL'}")
    
    all_passed = all(
        r['prices'] is not None and r['metrics'] is not None and r['market_cap'] is not None
        for r in all_results.values()
    )
    
    if all_passed:
        print("\n所有股票数据获取成功！系统可以正常运行。")
        print("\n下一步：配置LLM API密钥后运行完整交易流程")
        print("  1. 复制 .env.china 为 .env")
        print("  2. 在 .env 中配置你的 LLM API 密钥（如 DEEPSEEK_API_KEY）")
        print("  3. 运行: poetry run python src/main.py --ticker 000001")
    else:
        print("\n部分股票数据获取失败，请检查数据源。")
    
    return all_passed


if __name__ == "__main__":
    test_data_flow_for_trading()
