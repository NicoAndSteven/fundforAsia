"""
系统元数据需求分析
分析AI对冲基金系统所需的完整元数据清单
"""

# 系统元数据需求清单

SYSTEM_METADATA_REQUIREMENTS = {
    "价格数据": {
        "必需字段": [
            "open",      # 开盘价
            "close",     # 收盘价
            "high",      # 最高价
            "low",       # 最低价
            "volume",    # 成交量
            "time",      # 时间
        ],
        "用途": "技术分析、趋势跟踪、波动率分析",
        "重要性": "🔴 关键 - 必须有",
    },
    
    "财务指标": {
        "必需字段": [
            "market_cap",                    # 市值
            "enterprise_value",              # 企业价值
            "price_to_earnings_ratio",       # 市盈率
            "price_to_book_ratio",           # 市净率
            "price_to_sales_ratio",          # 市销率
            "gross_margin",                  # 毛利率
            "operating_margin",              # 营业利润率
            "net_margin",                    # 净利润率
            "return_on_equity",              # ROE
            "return_on_assets",              # ROA
            "return_on_invested_capital",    # ROIC
            "current_ratio",                 # 流动比率
            "quick_ratio",                   # 速动比率
            "debt_to_equity",                # 资产负债率
            "revenue_growth",                # 营收增长率
            "earnings_growth",               # 盈利增长率
            "earnings_per_share",            # 每股收益
            "book_value_per_share",          # 每股净资产
        ],
        "用途": "基本面分析、估值分析、财务健康度评估",
        "重要性": "🔴 关键 - 必须有",
    },
    
    "财务报表项目": {
        "必需字段": [
            "free_cash_flow",                # 自由现金流
            "net_income",                    # 净利润
            "depreciation_and_amortization", # 折旧摊销
            "capital_expenditure",           # 资本支出
            "working_capital",               # 营运资本
            "total_debt",                    # 总债务
            "cash_and_equivalents",          # 现金及等价物
            "interest_expense",              # 利息支出
            "revenue",                       # 营业收入
            "operating_income",              # 营业利润
            "ebit",                          # 息税前利润
            "ebitda",                        # 息税折旧摊销前利润
        ],
        "用途": "估值模型（DCF、Owner Earnings）、现金流分析",
        "重要性": "🟡 重要 - 估值Agent必需",
    },
    
    "内部交易数据": {
        "必需字段": [
            "transaction_date",              # 交易日期
            "transaction_shares",            # 交易股数
            "transaction_price_per_share",   # 交易价格
            "name",                          # 交易人姓名
            "title",                         # 职位
        ],
        "用途": "情绪分析、内部人交易信号",
        "重要性": "🟢 可选 - 情绪Agent使用",
    },
    
    "公司新闻": {
        "必需字段": [
            "title",       # 新闻标题
            "source",      # 新闻来源
            "date",        # 发布日期
            "url",         # 新闻链接
            "sentiment",   # 情绪标签
        ],
        "用途": "情绪分析、市场情绪评估",
        "重要性": "🟢 可选 - 情绪Agent使用",
    },
    
    "公司基本信息": {
        "必需字段": [
            "name",          # 公司名称
            "industry",      # 行业
            "sector",        # 板块
            "exchange",      # 交易所
            "listing_date",  # 上市日期
        ],
        "用途": "公司分析、行业对比",
        "重要性": "🟢 可选 - 辅助信息",
    },
}

# A股特有元数据需求

A_SHARE_SPECIFIC_REQUIREMENTS = {
    "涨跌停数据": {
        "必需字段": [
            "limit_up_price",    # 涨停价
            "limit_down_price",  # 跌停价
            "is_limit_up",       # 是否涨停
            "is_limit_down",     # 是否跌停
        ],
        "用途": "涨跌停板分析",
        "重要性": "🟡 重要 - A股特有",
    },
    
    "北向资金": {
        "必需字段": [
            "north_money",       # 北向资金净流入
            "date",              # 日期
        ],
        "用途": "外资流向分析",
        "重要性": "🟡 重要 - A股特有",
    },
    
    "融资融券": {
        "必需字段": [
            "margin_balance",    # 融资余额
            "short_balance",     # 融券余额
        ],
        "用途": "杠杆资金分析",
        "重要性": "🟢 可选 - A股特有",
    },
}

def print_requirements():
    """打印元数据需求"""
    print("="*80)
    print("系统元数据需求清单")
    print("="*80)
    
    for category, info in SYSTEM_METADATA_REQUIREMENTS.items():
        print(f"\n【{category}】")
        print(f"重要性: {info['重要性']}")
        print(f"用途: {info['用途']}")
        print(f"必需字段 ({len(info['必需字段'])}个):")
        for i, field in enumerate(info['必需字段'], 1):
            print(f"  {i}. {field}")
    
    print("\n" + "="*80)
    print("A股特有元数据需求")
    print("="*80)
    
    for category, info in A_SHARE_SPECIFIC_REQUIREMENTS.items():
        print(f"\n【{category}】")
        print(f"重要性: {info['重要性']}")
        print(f"用途: {info['用途']}")
        print(f"必需字段 ({len(info['必需字段'])}个):")
        for i, field in enumerate(info['必需字段'], 1):
            print(f"  {i}. {field}")

if __name__ == "__main__":
    print_requirements()
