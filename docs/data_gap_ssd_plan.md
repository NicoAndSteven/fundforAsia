# A 股数据补全 SSD 计划

## 状态：✅ Phase 1 已完成

### 完成于 2026-04-30

已完成的工作：
1. 新增 `src/tools/api_akshare.py` — akshare 数据适配器
2. 增强 `src/tools/api_unified.py` — 优先 akshare，fallback efinance
3. 扩展 `src/tools/api_efinance.py` — 新增每股经营现金流量映射
4. 扩展 `src/data/cache.py` — 新增通用缓存接口

现阶段数据覆盖：

| 指标类别 | 之前 (efinance) | 现在 (+akshare) |
|---------|----------------|----------------|
| 财务指标 | 8 个字段 | 17 个字段 |
| 流动性比率 | ❌ | 流动比率/速动比率/现金比率 |
| 杠杆比率 | ❌ | 资产负债率/产权比率 |
| 利润率 | 仅毛利率 | 毛利率/净利率/ROE |
| 同比增长 | ❌ | 营收增长/净利润增长 |
| 公司新闻 | 0 条 | 10 条/股 |
| 股东增减持 | 0 条 | 20 条/股 |

## 1. 数据源现状

### 1.1 当前 efinance 已提供的数据

| 数据类型 | 状态 | 说明 |
|---------|------|------|
| 日 K 线价格 | ✅ | `get_quote_history()` |
| 分钟 K 线 | ✅ | `get_quote_history(klt=)` |
| 实时行情 | ✅ | `get_latest_quote()` |
| 市场全景 | ✅ | 指数/板块/涨跌统计 |
| 北向资金 | ✅ | 通过 akshare |
| 股票列表 | ✅ | `get_realtime_quotes()` |

### 1.2 当前 `get_financial_metrics()` 能提供的字段

来自 `get_all_company_performance()` + `get_latest_quote()`：

| 字段 | efinance 对应 | 状态 |
|------|-------------|------|
| market_cap | 总市值 | ✅ |
| price_to_earnings_ratio | 动态市盈率 | ✅ |
| gross_margin | 销售毛利率 | ✅ |
| return_on_equity | 净资产收益率 | ✅ |
| revenue_growth | 营业收入同比增长 | ✅ |
| earnings_growth | 净利润同比增长 | ✅ |
| earnings_per_share | 每股收益 | ✅ |
| book_value_per_share | 每股净资产 | ✅ |

### 1.3 当前 `search_line_items()` 能映射的字段

| LineItem 字段 | efinance 列名 | 状态 |
|-------------|--------------|------|
| revenue | 营业收入 | ✅ |
| net_income | 净利润 | ✅ |
| eps | 每股收益 | ✅ |
| roe | 净资产收益率 | ✅ |
| gross_margin | 销售毛利率 | ✅ |
| revenue_growth | 营业收入同比增长 | ✅ |
| earnings_growth | 净利润同比增长 | ✅ |
| book_value_per_share | 每股净资产 | ✅ |

### 1.4 完全缺失的数据

| 数据类型 | 涉及大师 | 影响严重程度 |
|---------|---------|------------|
| 资产负债表 | ALL 价值型大师 | ⛔ 致命 |
| 现金流量表 | Buffett, Valuation, Peter Lynch | ⛔ 致命 |
| 利润表详细项 | ALL | ⛔ 致命 |
| 公司新闻 | News/Sentiment, Peter Lynch, 等 8 个大师 | ⛔ 致命 |
| 高管增减持 | Sentiment, Growth, 等 8 个大师 | ⛔ 致命 |
| 财务指标/比率 | Fundamentals, ALL | 🔴 高 |
| 行业分类详情 | ALL | 🟡 中 |

---

## 2. 数据源方案

### 2.1 东方财富 HTTP API（推荐，零成本）

东方财富提供了开放的 HTTP API，efinance 底层实际上也在使用这些接口。我们可以直接调用以获得比 efinance 封装更丰富的数据：

| API 端点 | 用途 |
|---------|------|
| `https://datacenter-web.eastmoney.com/api/data/v1/get` | 财务报表（利润表、资产负债表、现金流量表） |
| `https://push2.eastmoney.com/api/qt/ulist.np/get` | 批量实时行情（已有部分使用） |
| `https://datacenter.eastmoney.com/securities/api/data/v1/get` | 融资融券、增减持 |
| `https://np-anotice-stock.eastmoney.com/api/security/ann` | 公司公告/新闻 |

具体报表 API：
```
# 利润表
https://datacenter-web.eastmoney.com/api/data/v1/get?
  reportName=RPT_LICO_FN_CPD&columns=SECURITY_CODE,REPORT_DATE,BASIC_EPS,
  REVENUE,OPERATE_INCOME,TOTAL_PROFIT,NET_PROFIT,OPERATE_COST,
  SALE_EXPENSE,MANAGE_EXPENSE,FINANCE_EXPENSE

# 资产负债表
https://datacenter-web.eastmoney.com/api/data/v1/get?
  reportName=RPT_LICO_FN_CPD&columns=SECURITY_CODE,REPORT_DATE,
  TOTAL_ASSETS,TOTAL_LIABILITIES,TOTAL_EQUITY,CURRENT_ASSETS,
  CURRENT_LIABILITIES,FIXED_ASSETS

# 现金流量表
https://datacenter-web.eastmoney.com/api/data/v1/get?
  reportName=RPT_LICO_FN_CPD&columns=SECURITY_CODE,REPORT_DATE,
  OPERATE_CASH_FLOW,INVEST_CASH_FLOW,FINANCE_CASH_FLOW,
  FREE_CASH_FLOW
```

### 2.2 备选方案：akshare

akshare 提供了更丰富的 A 股数据，但需要额外安装。作为 efinance 的补充：

| 功能 | akshare 函数 |
|------|-------------|
| 利润表 | `ak.stock_profit_sheet_by_report_em()` |
| 资产负债表 | `ak.stock_balance_sheet_by_report_em()` |
| 现金流量表 | `ak.stock_cash_flow_sheet_by_report_em()` |
| 财务指标 | `ak.stock_financial_abstract_ths()` |
| 新闻 | `ak.stock_news_em()` |
| 增减持 | `ak.stock_holder_trade_em()` |

---

## 3. 实施路线图

### Phase 1: 财务数据基础设施（优先级 P0，估算 3-5 天）

**目标**：从东方财富 HTTP API 获取完整的三大报表数据

#### Task 1.1: 在 `api_efinance.py` 中新增财务报表 HTTP API 调用

创建新的数据获取方法：

```python
def get_financial_statements(self, ticker: str, report_type: str) -> dict:
    """
    获取财务报表
    report_type: 'balance_sheet' | 'income_statement' | 'cash_flow'
    返回结构化数据
    """
```

需要处理：
- 报表日期对齐（确保三大报表使用相同报告期）
- 数据缓存
- 单位统一（东方财富返回 元，需转为合适的单位）
- 错误处理和重试

#### Task 1.2: 扩展 `FinancialMetrics` 和 `LineItem` 数据填充

当前 `FinancialMetrics` 有 38 个 Optional 字段，只有 8 个被填充。接入三大报表后，需要填充：

**资产负债表可填充字段：**
- `total_assets`, `total_liabilities` → `debt_to_assets`, `debt_to_equity`
- `current_assets`, `current_liabilities` → `current_ratio`, `quick_ratio`
- `cash_and_equivalents`
- `shareholders_equity`

**利润表可填充字段：**
- `revenue` (已有), `operating_income` → `operating_margin`
- `net_income` (已有), `ebit`, `ebitda` → `net_margin`
- `interest_expense` → `interest_coverage`

**现金流量表可填充字段：**
- `free_cash_flow` → `free_cash_flow_yield`, `free_cash_flow_per_share`
- `capital_expenditure`
- `depreciation_and_amortization`

#### Task 1.3: 扩展 `search_line_items` 的数据映射

`_map_line_item` 当前只支持 8 个映射，需要扩展到完整的 30+ 映射。

具体扩展映射表：

```python
@staticmethod
def _map_line_item(item: str) -> Optional[str]:
    mapping = {
        # 利润表
        "revenue": "营业收入",
        "net_income": "净利润",
        "operating_income": "营业利润",
        "ebit": "营业利润",  # or 息税前利润
        "ebitda": "息税折旧摊销前利润",
        "interest_expense": "利息费用",
        "gross_profit": "营业毛利",
        "operating_expense": "营业总费用",
        "research_and_development": "研发费用",
        "depreciation_and_amortization": "折旧与摊销",
        "eps": "每股收益",
        "earnings_per_share": "每股收益",
        
        # 资产负债表
        "total_assets": "资产总计",
        "total_liabilities": "负债合计",
        "shareholders_equity": "股东权益合计",
        "current_assets": "流动资产合计",
        "current_liabilities": "流动负债合计",
        "cash_and_equivalents": "货币资金",
        "intangible_assets": "无形资产",
        "goodwill": "商誉",
        "inventory": "存货",
        "accounts_receivable": "应收账款",
        
        # 现金流量表
        "free_cash_flow": "自由现金流",
        "capital_expenditure": "购建固定资产无形资产支付的现金",
        "operating_cash_flow": "经营活动现金流量净额",
        "financing_cash_flow": "筹资活动现金流量净额",
        "investing_cash_flow": "投资活动现金流量净额",
        
        # 比率
        "roe": "净资产收益率",
        "gross_margin": "销售毛利率",
        "revenue_growth": "营业收入同比增长",
        "earnings_growth": "净利润同比增长",
        "book_value_per_share": "每股净资产",
    }
    return mapping.get(item)
```

### Phase 2: 新闻和情绪数据（优先级 P1，估算 2-3 天）

**目标**：为公司新闻和分析师情绪提供数据支持

#### Task 2.1: 实现 `get_company_news`（基于东方财富公告 + akshare）

```python
def get_company_news(self, ticker, end_date, start_date=None, limit=100):
    """通过东方财富公告 API + akshare 获取新闻"""
    # 方案 A: 东方财富公告 API
    # https://np-anotice-stock.eastmoney.com/api/security/ann
    # 方案 B: akshare stock_news_em()
```

新闻数据缺失影响的 agents 最多（8 个 agents），这是最关键的数据补全。

#### Task 2.2: 实现 `get_insider_trades`（基于东方财富增减持数据）

```python
def get_insider_trades(self, ticker, end_date, start_date=None, limit=1000):
    """通过东方财富高管增减持数据"""
    # 使用 akshare: ak.stock_holder_trade_em()
```

### Phase 3: 财务指标推导和计算（优先级 P1，估算 2 天）

**目标**：基于三大报表原始数据，自动计算财务比率

#### Task 3.1: 在 `FinancialMetrics` 中添加计算属性

新增 `FinancialMetricsCalculator` 类或静态方法，从 LineItem 数据计算：

```python
def calculate_ratios(line_items: List[LineItem]) -> Dict[str, float]:
    """从财务行项目计算各种财务比率"""
    ratios = {}
    latest = line_items[0]
    
    # 流动性比率
    if latest.current_assets and latest.current_liabilities:
        ratios['current_ratio'] = latest.current_assets / latest.current_liabilities
    if latest.cash_and_equivalents and latest.current_liabilities:
        ratios['cash_ratio'] = latest.cash_and_equivalents / latest.current_liabilities
    
    # 杠杆比率
    if latest.total_debt and latest.shareholders_equity:
        ratios['debt_to_equity'] = latest.total_debt / latest.shareholders_equity
    if latest.total_liabilities and latest.total_assets:
        ratios['debt_to_assets'] = latest.total_liabilities / latest.total_assets
    
    # 盈利能力比率
    if latest.operating_income and latest.revenue:
        ratios['operating_margin'] = latest.operating_income / latest.revenue
    if latest.net_income and latest.revenue:
        ratios['net_margin'] = latest.net_income / latest.revenue
    
    # 估值比率
    if latest.market_cap and latest.net_income:
        ratios['price_to_earnings_ratio'] = latest.market_cap / latest.net_income
    # ... 更多比率
    
    return ratios
```

#### Task 3.2: 多期数据对齐和趋势计算

多期数据是 Graham 和 Buffett 分析的基础。需要实现：

```python
def get_multi_period_data(ticker, periods=5):
    """获取多期对齐的财务数据"""
    # 按报告期对齐三大报表
    # 计算同比增长
    # 计算 CAGR
```

### Phase 4: 补充行业分类（优先级 P2，估算 1 天）

**目标**：完善行业分类信息

```python
def get_industry_classification(self, ticker):
    """增强的行业分类"""
    # 通过东方财富 HTTP API 获取申万行业分类
    # 获取行业 PE/PB 中位数（用于估值对比）
```

### Phase 5: 融资融券数据（优先级 P2，估算 0.5 天）

**目标**：支持 A 股特有的融资融券分析

### Phase 6: 集成和测试（估算 2 天）

1. 为每个新增 API 编写单元测试
2. 在现有 agent 中验证数据完整性
3. 端到端回归测试

---

## 4. 按大师优先级排序的数据需求

### 🅿️ 优先级 P0：当前数据严重不足的大师

| 大师 | 缺失数据 | 所需 Phase |
|------|---------|-----------|
| **Ben Graham** | 资产负债表(current_assets, current_liabilities, total_assets, total_liabilities), 股息, 流通股 | Phase 1 |
| **Warren Buffett** | FCF, 折旧摊销, 资本支出, 股东权益, 总资产, 负债 | Phase 1 |
| **Valuation** | FCF, 折旧摊销, 资本支出, 营运资本, 总负债, 现金, 利息费用 | Phase 1 |
| **Peter Lynch** | FCF, 资本支出, 现金, 总负债, 股东权益, 流通股, 内幕交易, 新闻 | Phase 1 + 2 |
| **Fundamentals** | current_ratio, debt_to_equity, FCF/股, operating_margin, net_margin, P/B, P/S | Phase 1 + 3 |

### 🅿️ 优先级 P1：次重要

| 大师 | 缺失数据 | 所需 Phase |
|------|---------|-----------|
| **Charlie Munger** | 内幕交易, 新闻 | Phase 2 |
| **Michael Burry** | 内幕交易, 新闻 | Phase 2 |
| **Nassim Taleb** | 内幕交易, 新闻 | Phase 2 |
| **Phil Fisher** | 内幕交易, 新闻 | Phase 2 |
| **Stanley Druckenmiller** | 内幕交易, 新闻 | Phase 2 |
| **Growth Analyst** | 内幕交易 | Phase 2 |

### 🅿️ 优先级 P2：增强功能

| 大师 | 缺失数据 | 所需 Phase |
|------|---------|-----------|
| **News Sentiment** | 公司新闻 | Phase 2 |
| **Sentiment** | 内幕交易, 新闻 | Phase 2 |
| **All** | 行业分类对比 | Phase 4 |

---

## 5. 实施策略

### 5.1 分阶段实施建议

**第一批（Phase 1）— 核心财务数据：**
- 接入东方财富 HTTP API 获取三大报表
- 扩展 `search_line_items` 映射
- 填充 `FinancialMetrics` 核心字段
- 验证：Ben Graham, Warren Buffett, Valuation 三个最受影响的大师能否正常获得所需数据

**第二批（Phase 2）— 新闻和内幕交易：**
- 接入东方财富公告 API / akshare
- 验证：News Sentiment, Sentiment, Peter Lynch 等大师的数据流

**第三批（Phase 3）— 比率计算和优化：**
- 自动财务比率计算
- 多期数据对齐
- 性能优化

### 5.2 数据结构决策

建议在 `api_unified.py` 层增加一个数据增强中间件：

```
现有: api_unified.py → api_efinance.py (限制)
改进: api_unified.py → api_efinance.py (基础) + api_eastmoney.py (增强 HTTP API)
```

新增 `api_eastmoney.py` 专门封装东方财富 HTTP API 的调用，与现有的 `api_efinance.py` 协同工作。`api_unified.py` 作为统一入口，优先使用增强数据，fallback 到基础数据。

### 5.3 关键技术决策

1. **HTTP API vs akshare**：
   - 核心财务数据：优先使用东方财富 HTTP API（不需要额外依赖，更可控）
   - 新闻/增减持：可使用 akshare 作为快速实现方案
   - akshare 作为 optional dependency

2. **缓存策略**：
   - 财务数据变化低频（季度），缓存时间可设为 24 小时
   - 新闻数据变化高频，缓存时间设为 1 小时
   - 使用现有 `src/data/cache.py` 缓存机制

3. **错误处理**：
   - 所有新增 API 调用必须 try/except
   - 数据不可用时返回 None，不抛出异常
   - agent 端已有空值处理逻辑

### 5.4 风险与缓解措施

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 东方财富 API 变更 | 低 | 高 | 使用 akshare 作为备用数据源 |
| 网络限制 | 中 | 中 | 已有 HTTP 阻断处理经验，增加重试 + 超时 |
| akshare 版本兼容 | 低 | 低 | pip freeze 锁定版本 |
| 数据单位不一致 | 中 | 中 | 统一在 `api_eastmoney.py` 层做单位转换 |

---

## 6. MVP 快速见效方案

如果只想用最短时间看到效果，推荐按以下顺序实现：

1. **Day 1**：实现 `search_line_items` 扩展映射（在现有 `_map_line_item` 中新增映射到 `get_all_company_performance()` 已有的列）
   - 最大程度利用已有数据，最少代码改动
   - 收益：所有 agents 能获得更多基础数据

2. **Day 2-3**：实现三大报表 HTTP API
   - 直接带来资产负债表、利润表、现金流量表的完整数据
   - 收益：所有价值型大师的核心分析逻辑开始工作

3. **Day 4-5**：实现财务比率计算
   - 自动从报表原始数据计算比率
   - 收益：Fundamentals 分析师获得完整比率数据

4. **Day 6**：接入 akshare 新闻/增减持
   - 收益：8 个依赖新闻和增减持的大师获得数据
