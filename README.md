# AI 对冲基金 (AI Hedge Fund)

> **基于大语言模型的 A 股智能投研系统**  
> 本项目源于 [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund) 的二次开发，已将数据源改造为**纯 A 股版本**。

---

## 免责声明

**本项目仅用于教育和研究目的。**

- 不构成任何投资建议
- 不提供收益保证
- 作者不对任何金融损失承担责任
- 投资决策请咨询专业金融顾问
- 过往表现不代表未来结果

---

## 目录

- [项目介绍](#项目介绍)
- [系统架构](#系统架构)
- [安装](#安装)
- [配置](#配置)
- [运行方式](#运行方式)
- [Agent 说明](#agent-说明)
- [数据源](#数据源)
- [项目结构](#项目结构)
- [许可证](#许可证)

---

## 项目介绍

AI 对冲基金是一个利用多个 AI Agent 协作进行 A 股投资决策的实验性系统。系统内置了多位风格各异的投资大师 Agent，分别从不同角度分析股票并给出交易信号，最后由风险经理和投资组合经理综合决策。

### 核心特点

- 纯 A 股数据支持（沪深市场，通过 efinance 获取实时数据）
- 多个 AI Agent 并行分析（价值投资、成长投资、技术分析等）
- 实时数据获取（当天数据盘中即可获取，无需 T+1 等待）
- 支持分钟级 K 线分析
- 命令行 + Web 双模式
- 支持回测

---

## 系统架构

```
输入股票代码
     │
     ▼
┌─────────────────────────────────────────────┐
│  多个 AI Agent 并行分析                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐ │
│  │ 巴菲特   │ │ 格雷厄姆 │ │ 彼得·林奇    │ │
│  ├──────────┤ ├──────────┤ ├──────────────┤ │
│  │ 达摩达兰 │ │ 费雪     │ │ 阿克曼       │ │
│  ├──────────┤ ├──────────┤ ├──────────────┤ │
│  │ 伍德     │ │ 芒格     │ │ 德里豪森     │ │
│  ├──────────┤ ├──────────┤ ├──────────────┤ │
│  │ 塔勒布   │ │ 伯里     │ │ 帕布莱       │ │
│  └──────────┘ └──────────┘ └──────────────┘ │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │   风险经理      │
         └────────┬────────┘
                  │
                  ▼
         ┌─────────────────┐
         │  投资组合经理   │
         └────────┬────────┘
                  │
                  ▼
           交易决策输出
```

---

## 安装

### 前置要求

- Python 3.11+
- Conda（推荐）或 pip

### 1. 克隆仓库

```bash
git clone https://github.com/your-username/ai-hedge-fund.git
cd ai-hedge-fund
```

### 2. 创建环境

```bash
conda create -n aifund python=3.11
conda activate aifund
```

### 3. 安装依赖

```bash
pip install poetry
poetry install
```

### 4. 安装数据源

```bash
pip install efinance
```

> efinance 基于东方财富 API，完全免费，无需 API Key。

### 5. 配置 API Key

复制环境变量文件并编辑:

```bash
cp .env.example .env
```

至少设置一个 LLM 的 API Key，例如:

```
# .env
DEEPSEEK_API_KEY=your-deepseek-api-key
```

数据源无需 API Key，efinance 完全免费。

---

## 运行方式

### ⌨️ 命令行

```bash
# 分析单只 A 股
python src/main.py --ticker 600519

# 分析多只股票
python src/main.py --ticker 000001,600519,300750

# 指定时间范围
python src/main.py --ticker 600519 --start-date 2025-01-01 --end-date 2026-04-28

# 查看所有选项
python src/main.py --help
```

### 回测

```bash
python src/backtester.py --ticker 000001,600519
```

### 🖥️ Web 应用

```bash
# 启动后端
cd app
pip install -r requirements.txt
uvicorn main:app --reload
```

详细说明请查看 [app/README.md](app/README.md)。

---

## Agent 说明

| Agent | 风格 | 核心策略 |
|-------|------|---------|
| **巴菲特 (Warren Buffett)** | 价值投资 | 寻找优质公司、护城河、合理价格 |
| **格雷厄姆 (Ben Graham)** | 深度价值 | 安全边际、低估资产 |
| **达摩达兰 (Aswath Damodaran)** | 估值分析 | 内在价值评估、DCF 模型 |
| **彼得·林奇 (Peter Lynch)** | 成长价值 | 日常生活选股、十倍股 |
| **费雪 (Phil Fisher)** | 成长投资 | 深入调研、成长潜力 |
| **芒格 (Charlie Munger)** | 长期持有 | 优质企业、合理价格 |
| **阿克曼 (Bill Ackman)** | 激进投资 | 集中持仓、主动推动变革 |
| **伍德 (Cathie Wood)** | 成长投资 | 创新颠覆、高增长行业 |
| **塔勒布 (Nassim Taleb)** | 风险分析 | 黑天鹅、尾部风险、反脆弱 |
| **伯里 (Michael Burry)** | 逆向投资 | 深度价值、做空泡沫 |
| **帕布莱 (Mohnish Pabrai)** | 低风险投资 | Dhandho 策略、低风险高回报 |
| **德里豪森 (Stanley Druckenmiller)** | 宏观策略 | 不对称机会、顺势而为 |
| **技术分析 Agent** | 技术面 | K线形态、均线、成交量分析 |
| **基本面 Agent** | 基本面 | 财务指标、估值分析 |
| **情绪分析 Agent** | 市场情绪 | 新闻情绪、资金流向 |
| **估值 Agent** | 综合评估 | 多维度估值 |
| **风险经理** | 风控 | 仓位限制、风险指标 |
| **投资组合经理** | 决策 | 综合信号、生成交易指令 |

---

## 数据源

本项目使用 **efinance** 作为默认数据源，底层对接东方财富 API。

| 特性 | 说明 |
|------|------|
| A 股数据 | ✅ 沪深全部股票 |
| 实时性 | ✅ 当天盘中实时数据 |
| 分钟 K 线 | ✅ 支持 5/15/30/60 分钟 |
| 美股/港股 | ✅ 支持 |
| API Key | ❌ 不需要，完全免费 |
| 安装 | `pip install efinance` |

> efinance 基于东方财富 API，完全免费，无需 API Key，支持 A 股/美股/港股的实时与历史数据。

---

## 项目结构

```
ai-hedge-fund/
├── src/
│   ├── agents/           # AI Agent 实现
│   ├── backtesting/      # 回测引擎
│   ├── tools/
│   │   ├── api_efinance.py    # efinance 数据适配器（默认数据源）
│   │   └── api_unified.py     # 统一数据入口
│   ├── data/             # 数据模型 & 缓存
│   ├── graph/            # Agent 状态图
│   ├── utils/            # 工具函数
│   └── main.py           # 入口
├── app/                  # Web 应用
├── tests/                # 测试
├── v2/                   # 新架构实验
├── .env                  # 环境变量
└── pyproject.toml        # 项目配置
```

---

## 许可证

本项目基于 MIT 许可证开源。

### 致谢

- 原始项目: [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)
- 数据源: [efinance](https://github.com/Micro-sheep/efinance) — 基于东方财富的免费数据库
