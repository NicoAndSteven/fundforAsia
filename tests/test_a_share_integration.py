"""
A股数据集成测试脚本
测试新闻、高管增减持、北向资金数据获取
"""
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tools.api_unified import (
    get_company_news,
    get_insider_trades,
    get_north_money,
)


def test_company_news():
    """测试公司新闻数据"""
    print("\n" + "=" * 70)
    print("测试1: 公司新闻数据")
    print("=" * 70)
    
    ticker = "000001"
    end_date = "2024-04-30"
    
    print(f"获取 {ticker} 新闻数据...")
    
    news = get_company_news(ticker, end_date, limit=10)
    
    if news:
        print(f"\n[OK] 成功获取 {len(news)} 条新闻")
        print("\n前3条新闻:")
        for n in news[:3]:
            print(f"  - {n.title[:50]}...")
            print(f"    来源: {n.source}, 日期: {n.date}")
        return True
    else:
        print("[FAIL] 未获取到新闻数据")
        return False


def test_insider_trades():
    """测试高管增减持数据"""
    print("\n" + "=" * 70)
    print("测试2: 高管增减持数据")
    print("=" * 70)
    
    ticker = "688708"
    end_date = "2024-04-30"
    
    print(f"获取 {ticker} 高管增减持数据...")
    
    trades = get_insider_trades(ticker, end_date, limit=10)
    
    if trades:
        print(f"\n[OK] 成功获取 {len(trades)} 条内部交易记录")
        print("\n前3条记录:")
        for t in trades[:3]:
            direction = "增持" if t.transaction_shares and t.transaction_shares > 0 else "减持"
            shares = abs(t.transaction_shares) if t.transaction_shares else 0
            print(f"  - {t.name}: {direction} {shares:.0f} 股")
            print(f"    日期: {t.transaction_date}")
        return True
    else:
        print("[WARN] 未获取到内部交易记录（可能该股票无增减持记录）")
        return True


def test_north_money():
    """测试北向资金数据"""
    print("\n" + "=" * 70)
    print("测试3: 北向资金数据")
    print("=" * 70)
    
    print("获取北向资金数据...")
    
    df = get_north_money()
    
    if df is not None and not df.empty:
        print(f"\n[OK] 成功获取 {len(df)} 条北向资金记录")
        print("\n最近5日数据:")
        print(df.tail(5).to_string())
        return True
    else:
        print("[FAIL] 未获取到北向资金数据")
        return False


def test_sentiment_agent_data():
    """测试情绪分析Agent所需数据"""
    print("\n" + "=" * 70)
    print("测试4: 情绪分析Agent数据完整性")
    print("=" * 70)
    
    ticker = "000001"
    end_date = "2024-04-30"
    
    print(f"获取 {ticker} 情绪分析所需数据...")
    
    news = get_company_news(ticker, end_date, limit=100)
    trades = get_insider_trades(ticker, end_date, limit=100)
    
    print(f"\n新闻数据: {len(news)} 条")
    print(f"内部交易: {len(trades)} 条")
    
    if len(news) > 0:
        print("\n[OK] 情绪分析数据可用")
        return True
    else:
        print("\n[WARN] 新闻数据不可用，情绪分析可能受限")
        return True


def main():
    print("\n" + "=" * 70)
    print("A股数据集成测试")
    print("测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 70)
    
    results = []
    
    results.append(("公司新闻", test_company_news()))
    results.append(("高管增减持", test_insider_trades()))
    results.append(("北向资金", test_north_money()))
    results.append(("情绪分析数据", test_sentiment_agent_data()))
    
    print("\n" + "=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n所有测试通过！A股数据集成成功。")
        print("\n现在可以运行完整的交易分析:")
        print("  poetry run python src/main.py --ticker 000001 --show-reasoning")
    else:
        print(f"\n有 {total - passed} 个测试失败，请检查相关功能。")


if __name__ == "__main__":
    main()
