# A股市场适配指南

本文档说明如何使用AI Hedge Fund系统进行A股市场分析和交易决策。

## 快速开始

### 1. 环境配置

```bash
# 复制A股配置文件
cp .env.china .env

# 编辑.env文件，配置你的LLM API密钥
# 推荐使用DeepSeek（国内访问快，性价比高）
DEEPSEEK_API_KEY=your_deepseek_api_key
```

### 2. 安装依赖

```bash
# 安装基础依赖
poetry install

# 安装akshare获取完整数据（新闻、高管增减持、北向资金）
pip install akshare
```

### 3. 运行系统

```bash
# 分析单只A股股票
poetry run python src/main.py --ticker 000001

# 分析多只A股股票
poetry run python src/main.py --ticker 000001,600000,300001

# 指定日期范围
poetry run python src/main.py --ticker 000001 --start 2024-01-01 --end 2024-03-31

# 显示推理过程
poetry run python src/main.py --ticker 000001 --show-reasoning

# 使用DeepSeek模型
poetry run python src/main.py --ticker 000001 --model-provider deepseek --model deepseek-chat
```

## 数据源说明

### BaoStock + Akshare 组合（推荐）

**BaoStock** 提供基础数据（免费，无需API密钥）：
- 历史K线数据（日/周/月）
- 财务指标（盈利能力、成长能力、偿债能力等）
- 股票基础信息（行业分类、上市状态等）

**Akshare** 提供增强数据（免费，需要安装）：
- 公司新闻数据 ✅
- 高管增减持数据 ✅
- 北向资金数据 ✅
- 更多A股特有数据

### 安装Akshare后可用功能

| 功能 | 数据源 | 说明 |
|------|--------|------|
| 新闻数据 | Akshare | 东方财富新闻，用于情绪分析 |
| 高管增减持 | Akshare | 实时高管交易数据，用于内部交易分析 |
| 北向资金 | Akshare | 沪深港通资金流向，A股特有指标 |

### 财务指标可用性

| 指标 | 可用性 | BaoStock字段 |
|------|--------|--------------|
| 市值 | ✅ | 计算值 |
| ROE | ✅ | roeAvg |
| 净利率 | ✅ | npMargin |
| 负债率 | ✅ | liabilityToAsset |
| EPS | ✅ | epsTTM |
| 盈利增长 | ✅ | YOYNI |
| 流动比率 | ⚠️ | currentRatio（部分股票可能为空）|
| 毛利率 | ⚠️ | gpMargin（部分股票可能为空）|
| 市盈率 | ⚠️ | 计算值（依赖EPS）|
| 市净率 | ⚠️ | 计算值（依赖财务数据）|

## Agent功能说明

### 完全支持的Agents

所有Agent在A股模式下都可以正常工作（需要安装akshare）：

| Agent | 功能 | 数据依赖 |
|-------|------|----------|
| 技术分析 | K线形态、趋势分析 | 价格数据 ✅ |
| 基本面分析 | 财务指标分析 | 财务数据 ✅ |
| 估值分析 | 市值、PE/PB分析 | 市值数据 ✅ |
| 风险管理 | 波动率、风险指标 | 价格数据 ✅ |
| 情绪分析 | 新闻情绪、内部交易 | 新闻+增减持 ✅ |
| Warren Buffett | 价值投资分析 | 财务数据 ✅ |
| Ben Graham | 安全边际分析 | 财务数据 ✅ |
| Peter Lynch | 成长投资分析 | 财务数据 ✅ |
| Bill Ackman | 激进投资分析 | 财务数据 ✅ |
| Cathie Wood | 创新投资分析 | 财务数据 ✅ |
| Michael Burry | 深度价值分析 | 财务+增减持 ✅ |
| Charlie Munger | 价值投资分析 | 财务+增减持 ✅ |

### 未安装Akshare时

如果未安装akshare，以下Agent功能会受限：
- 情绪分析：返回中性信号
- Michael Burry：内部交易分析不可用
- Charlie Munger：内部交易分析不可用

## 股票代码格式

系统支持多种股票代码格式：

```python
# 以下格式都有效
"000001"      # 自动识别为深圳股票
"600000"      # 自动识别为上海股票
"sz.000001"   # 明确指定深圳
"sh.600000"   # 明确指定上海
"SZ.000001"   # 大写也有效
```

## 常见问题

### 1. 获取数据失败

**问题：** 提示"未获取到价格数据"

**解决方案：**
- 确保日期范围在股票上市日期之后
- 检查股票代码是否正确
- BaoStock服务器可能有延迟，稍后重试

### 2. 财务指标缺失

**问题：** 部分财务指标显示N/A

**解决方案：**
- 这是正常现象，BaoStock部分字段可能为空
- 系统会自动处理缺失数据
- 建议使用多个Agent综合分析

### 3. 情绪分析返回中性

**问题：** 情绪分析总是返回neutral

**解决方案：**
- 确保已安装akshare：`pip install akshare`
- 安装后系统会自动获取新闻和内部交易数据
- 情绪分析将正常工作

### 4. LLM API错误

**问题：** 提示API密钥无效

**解决方案：**
- 检查.env文件中的API密钥是否正确
- 确保API密钥有足够的余额
- 推荐使用DeepSeek（国内访问稳定）

## 性能优化建议

1. **使用缓存**：系统会自动缓存数据，避免重复请求
2. **批量分析**：一次分析多只股票比多次分析单只股票更高效
3. **选择Agent**：使用`--analysts`参数只运行必要的Agent

```bash
# 只运行技术分析和基本面分析
poetry run python src/main.py --ticker 000001 --analysts technical_fundamentals
```

## 切换回美股模式

如需切换回美股模式，修改.env文件：

```
DATA_SOURCE=us
FINANCIAL_DATASETS_API_KEY=your_api_key
```

## 功能支持总结

| 功能 | A股支持 | 数据源 | 备注 |
|------|---------|--------|------|
| 价格数据 | ✅ 完全支持 | BaoStock | 免费 |
| 财务指标 | ✅ 基本支持 | BaoStock | 部分字段可能为空 |
| 市值计算 | ✅ 支持 | BaoStock | 计算值 |
| 公司新闻 | ✅ 支持 | Akshare | 需安装 |
| 高管增减持 | ✅ 支持 | Akshare | 需安装 |
| 北向资金 | ✅ 支持 | Akshare | 需安装 |
| 行业分类 | ✅ 支持 | BaoStock | 免费 |

## 技术支持

- BaoStock文档：http://baostock.com/
- 项目GitHub：提交Issue获取帮助
- DeepSeek API：https://platform.deepseek.com/
