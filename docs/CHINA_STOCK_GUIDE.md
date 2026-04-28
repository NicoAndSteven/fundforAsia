# A股市场适配指南

本文档详细说明如何将AI对冲基金项目适配到A股市场。

## 📋 目录

- [快速开始](#快速开始)
- [数据源配置](#数据源配置)
- [使用方法](#使用方法)
- [A股特有功能](#a股特有功能)
- [注意事项](#注意事项)
- [常见问题](#常见问题)

## 🚀 快速开始

### 1. 安装依赖

```bash
poetry install
```

这将自动安装以下A股数据源依赖：
- `tushare` - 主要A股数据源
- `akshare` - 补充数据源

### 2. 获取Tushare Token

1. 访问 [Tushare官网](https://tushare.pro/)
2. 注册账号并登录
3. 在个人中心获取API Token
4. 免费版有积分限制，建议购买积分获得更多权限

### 3. 配置环境变量

编辑 `.env` 文件：

```bash
# 设置数据源为A股
DATA_SOURCE=china

# 配置Tushare Token
TUSHARE_TOKEN=your_tushare_token_here

# 配置LLM API（至少需要一个）
OPENAI_API_KEY=your_openai_api_key
# 或者使用其他LLM
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 4. 运行测试

```bash
poetry run python tests/test_china_adapter.py
```

## 📊 数据源配置

### Tushare Pro

**优点：**
- 数据全面、质量高
- 财务数据准确
- 社区活跃、文档完善
- 支持历史数据回测

**缺点：**
- 需要积分权限
- 部分高级数据需要付费

**数据覆盖：**
- 股票行情（日线、周线、月线）
- 财务数据（三大报表）
- 财务指标（PE、PB、ROE等）
- 公司基本信息
- 高管增减持
- 融资融券
- 北向资金

### Akshare

**优点：**
- 完全免费
- 开源社区维护
- 数据源丰富

**缺点：**
- 数据质量参差不齐
- 部分接口不稳定
- 缺少历史数据

**数据覆盖：**
- 实时行情
- 新闻资讯
- 资金流向
- 板块数据

## 💡 使用方法

### 方式一：命令行运行

```bash
# 分析A股股票（使用股票代码）
poetry run python src/main.py --ticker 000001,600000,300001

# 指定日期范围
poetry run python src/main.py --ticker 000001,600000 --start-date 2024-01-01 --end-date 2024-12-31

# 显示推理过程
poetry run python src/main.py --ticker 000001 --show-reasoning
```

### 方式二：Python代码调用

```python
from src.tools.api_china import get_china_adapter

# 获取数据适配器
adapter = get_china_adapter()

# 获取价格数据
prices = adapter.get_prices("000001", "2024-01-01", "2024-12-31")

# 获取财务指标
metrics = adapter.get_financial_metrics("000001", "2024-12-31")

# 获取北向资金
north_money = adapter.get_north_money("2024-12-31")
```

### 方式三：使用统一API

```python
from src.tools.api_unified import get_prices, get_financial_metrics

# 自动根据DATA_SOURCE配置选择数据源
prices = get_prices("000001", "2024-01-01", "2024-12-31")
```

## 🇨🇳 A股特有功能

### 1. 涨跌停板分析

A股特有的涨跌停板制度，系统会自动识别：

- **主板股票**：±10%
- **ST股票**：±5%
- **创业板/科创板**：±20%

```python
from src.agents.technicals_china import check_limit_status

# 检查涨跌停状态
limit_status = check_limit_status(prices_df, "000001")
```

### 2. 北向资金追踪

追踪外资流入流出：

```python
from src.tools.api_china import get_china_adapter

adapter = get_china_adapter()
north_money = adapter.get_north_money("2024-12-31")
```

### 3. 融资融券数据

获取融资融券余额：

```python
margin_data = adapter.get_margin_trading("000001", "2024-12-31")
```

### 4. 股票代码标准化

系统自动处理多种股票代码格式：

```python
# 以下格式都会被正确识别
"000001"      # 自动识别为 000001.SZ
"600000"      # 自动识别为 600000.SH
"000001.SZ"   # 直接使用
"600000.SH"   # 直接使用
```

## ⚠️ 注意事项

### 1. 数据权限

Tushare采用积分制，不同积分等级有不同的数据权限：

| 积分等级 | 权限 |
|---------|------|
| 0-120 | 基础数据 |
| 120-2000 | 中级数据 |
| 2000+ | 高级数据 |

建议至少获得120积分以使用完整功能。

### 2. 数据延迟

- **免费版**：数据可能有15-20分钟延迟
- **付费版**：可获取实时数据

### 3. 调用频率限制

Tushare对API调用频率有限制：

- 每分钟最多200次
- 建议使用缓存机制
- 系统已内置缓存功能

### 4. 财务数据差异

A股财务数据与美股有以下差异：

- 会计准则不同（中国会计准则 vs US GAAP）
- 财务报告频率（季报、半年报、年报）
- 特殊指标（扣非净利润、ROE计算方式等）

### 5. 交易时间

A股交易时间：
- 上午：9:30-11:30
- 下午：13:00-15:00
- 节假日休市

## ❓ 常见问题

### Q1: 如何获取Tushare Token？

**A:** 
1. 访问 https://tushare.pro/
2. 注册并登录
3. 在"个人中心"->"接口Token"中获取

### Q2: 提示"权限不足"怎么办？

**A:** 
- 检查Tushare积分是否足够
- 部分高级数据需要更高积分
- 可以通过分享、捐赠等方式获取积分

### Q3: 数据获取失败怎么办？

**A:** 
1. 检查网络连接
2. 确认Tushare Token是否正确
3. 查看API调用频率是否超限
4. 检查股票代码格式是否正确

### Q4: 如何切换回美股数据？

**A:** 
修改 `.env` 文件：
```bash
DATA_SOURCE=us
```

### Q5: 支持哪些A股股票？

**A:** 
支持所有A股股票：
- 上海主板（600xxx, 601xxx, 603xxx）
- 深圳主板（000xxx, 001xxx）
- 创业板（300xxx）
- 科创板（688xxx）
- ST股票

### Q6: 如何获取更多历史数据？

**A:** 
- Tushare免费版支持近3年数据
- 付费版可获取更长时间的历史数据
- 建议使用本地缓存减少API调用

## 📈 性能优化建议

### 1. 使用缓存

系统已内置缓存机制，相同数据不会重复获取：

```python
# 第一次调用会从API获取
prices1 = adapter.get_prices("000001", "2024-01-01", "2024-12-31")

# 第二次调用会从缓存读取
prices2 = adapter.get_prices("000001", "2024-01-01", "2024-12-31")
```

### 2. 批量获取

建议一次性获取多只股票数据，减少API调用次数：

```python
tickers = ["000001", "600000", "300001"]
for ticker in tickers:
    prices = adapter.get_prices(ticker, start_date, end_date)
    # 处理数据...
```

### 3. 合理设置日期范围

- 避免获取过长的时间范围
- 建议每次不超过1年
- 可以分段获取后合并

## 🔧 高级配置

### 自定义数据源

如果需要使用其他数据源，可以扩展 `ChinaDataAdapter` 类：

```python
from src.tools.api_china import ChinaDataAdapter

class CustomDataAdapter(ChinaDataAdapter):
    def get_prices(self, ticker, start_date, end_date, api_key=None):
        # 自定义实现
        pass
```

### 添加新的A股指标

在 `src/data/models_china.py` 中添加新的数据模型：

```python
class CustomMetric(BaseModel):
    ticker: str
    metric_name: str
    value: float
    # 其他字段...
```

## 📚 相关资源

- [Tushare官方文档](https://tushare.pro/document/2)
- [Akshare文档](https://akshare.akfamily.xyz/)
- [项目GitHub](https://github.com/virattt/ai-hedge-fund)

## 🤝 贡献

欢迎提交Issue和Pull Request来完善A股适配功能！

---

**最后更新**: 2024年
**维护者**: AI Hedge Fund Team
