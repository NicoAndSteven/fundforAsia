# BaoStock数据适配器使用指南

## 📋 概述

BaoStock数据适配器是AI对冲基金项目完全免费的A股数据源解决方案，基于BaoStock开源库实现。

## 🎯 核心优势

- ✅ **完全免费** - 无需注册、无需Token、无任何费用
- ✅ **稳定可靠** - 测试通过率100%
- ✅ **响应快速** - 平均响应时间<0.1秒
- ✅ **数据全面** - 覆盖全市场8,703只股票
- ✅ **元数据覆盖100%** - 满足系统所有需求

## 🚀 快速开始

### 1. 安装依赖

```bash
poetry install
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 复制配置模板
cp .env.baostock.example .env

# 编辑 .env 文件
DATA_SOURCE=china  # 使用A股数据源
OPENAI_API_KEY=your_openai_key  # 配置LLM API
```

### 3. 运行测试

```bash
python tests/test_baostock_adapter.py
```

### 4. 分析A股股票

```bash
# 分析单只股票
poetry run python src/main.py --ticker 000001

# 分析多只股票
poetry run python src/main.py --ticker 000001,600000,300001

# 指定日期范围
poetry run python src/main.py --ticker 000001 --start-date 2024-01-01 --end-date 2024-12-31
```

## 📊 支持的功能

### 1. 价格数据获取

```python
from src.tools.api_unified import get_prices

# 获取价格数据
prices = get_prices(
    ticker="000001",
    start_date="2024-01-01",
    end_date="2024-12-31"
)

# 价格数据包含：
# - open: 开盘价
# - close: 收盘价
# - high: 最高价
# - low: 最低价
# - volume: 成交量
# - time: 日期
```

### 2. 财务指标获取

```python
from src.tools.api_unified import get_financial_metrics

# 获取财务指标
metrics = get_financial_metrics(
    ticker="000001",
    end_date="2024-12-31"
)

# 财务指标包含：
# - return_on_equity: ROE
# - return_on_assets: ROA
# - earnings_per_share: 每股收益
# - book_value_per_share: 每股净资产
# - revenue_growth: 营收增长率
# - earnings_growth: 盈利增长率
# - current_ratio: 流动比率
# - debt_to_equity: 资产负债率
# ... 等更多指标
```

### 3. 市值获取

```python
from src.tools.api_unified import get_market_cap

# 获取市值
market_cap = get_market_cap(
    ticker="000001",
    end_date="2024-12-31"
)

print(f"市值: {market_cap:.2f} 亿元")
```

## 🔧 高级用法

### 1. 直接使用BaoStock适配器

```python
from src.tools.api_baostock import get_baostock_adapter

# 获取适配器
adapter = get_baostock_adapter()

# 获取价格数据
prices = adapter.get_prices("000001", "2024-01-01", "2024-12-31")

# 获取财务指标
metrics = adapter.get_financial_metrics("000001", "2024-12-31")

# 获取市值
market_cap = adapter.get_market_cap("000001", "2024-12-31")
```

### 2. 股票代码格式

支持多种股票代码格式：

```python
# 以下格式都会被正确识别
"000001"      # 自动识别为 sz.000001
"600000"      # 自动识别为 sh.600000
"300001"      # 自动识别为 sz.300001
"688001"      # 自动识别为 sh.688001
"sz.000001"   # 直接使用
"sh.600000"   # 直接使用
```

### 3. 数据缓存

系统内置缓存机制，相同数据不会重复获取：

```python
# 第一次调用会从API获取
prices1 = get_prices("000001", "2024-01-01", "2024-12-31")

# 第二次调用会从缓存读取
prices2 = get_prices("000001", "2024-01-01", "2024-12-31")
```

## 📈 数据覆盖范围

### 支持的股票类型

- ✅ 上海主板 (600xxx, 601xxx, 603xxx)
- ✅ 深圳主板 (000xxx, 001xxx)
- ✅ 创业板 (300xxx)
- ✅ 科创板 (688xxx)
- ✅ ST股票

### 支持的数据类型

| 数据类型 | 支持状态 | 说明 |
|---------|---------|------|
| 历史价格 | ✅ | 日线数据 |
| 财务指标 | ✅ | 季度财务数据 |
| 盈利能力 | ✅ | ROE、ROA、净利润等 |
| 成长能力 | ✅ | 营收增长率、利润增长率 |
| 偿债能力 | ✅ | 流动比率、资产负债率 |
| 运营能力 | ✅ | 周转率等 |
| 现金流量 | ✅ | 自由现金流等 |
| 公司信息 | ✅ | 基本信息 |
| 新闻数据 | ❌ | 不支持 |

## ⚠️ 注意事项

### 1. 数据时效性

- BaoStock数据可能有1-2天延迟
- 建议使用缓存减少API调用
- 实时交易需结合实时数据源

### 2. 数据完整性

- 部分股票可能缺少某些财务指标
- 系统已添加数据完整性检查
- 提供降级方案

### 3. 调用频率

- 建议控制调用频率，避免被封
- 使用批量接口减少请求次数
- 系统已实现缓存机制

### 4. 登录机制

- BaoStock需要登录才能使用
- 系统自动管理登录/登出
- 单例模式确保连接复用

## 🔄 与美股数据源切换

### 切换到美股

```bash
# 修改 .env 文件
DATA_SOURCE=us
FINANCIAL_DATASETS_API_KEY=your_key
```

### 切换回A股

```bash
# 修改 .env 文件
DATA_SOURCE=china
```

## 📚 API参考

### get_prices()

```python
def get_prices(
    ticker: str,           # 股票代码
    start_date: str,       # 开始日期 (YYYY-MM-DD)
    end_date: str,         # 结束日期 (YYYY-MM-DD)
    api_key: str = None    # API密钥（未使用）
) -> List[Price]:
    """获取股票价格数据"""
```

### get_financial_metrics()

```python
def get_financial_metrics(
    ticker: str,           # 股票代码
    end_date: str,         # 结束日期
    period: str = "ttm",   # 周期
    limit: int = 10,       # 返回记录数限制
    api_key: str = None    # API密钥（未使用）
) -> List[FinancialMetrics]:
    """获取财务指标数据"""
```

### get_market_cap()

```python
def get_market_cap(
    ticker: str,           # 股票代码
    end_date: str,         # 结束日期
    api_key: str = None    # API密钥（未使用）
) -> Optional[float]:
    """获取股票市值（亿元）"""
```

## 🐛 故障排除

### Q1: 登录失败怎么办？

**A**: 检查网络连接，BaoStock需要网络访问。

### Q2: 数据为空怎么办？

**A**: 可能的原因：
- 股票代码不存在
- 日期范围内无交易日
- 数据源API限制

### Q3: 响应速度慢怎么办？

**A**: 
- 使用缓存机制
- 减少日期范围
- 批量获取数据

## 📖 相关文档

- [BaoStock官方文档](http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3)
- [免费数据源测试报告](FREE_DATA_SOURCE_TEST_REPORT.md)
- [完整测试报告](COMPLETE_DATA_SOURCE_TEST_REPORT.md)

---

**最后更新**: 2026-04-26  
**维护者**: AI Hedge Fund Team
