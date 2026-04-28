# A股免费数据源综合测试脚本使用指南

## 📋 概述

这个综合测试脚本可以自动检测你的Python环境，安装必要的依赖，并测试所有免费的A股数据源。

## 🚀 快速开始

### 1. 确保Python版本

**推荐**: Python 3.9+ （可以测试所有数据源）  
**最低**: Python 3.8 （只能测试BaoStock）

### 2. 运行测试脚本

```bash
python tests/comprehensive_test.py
```

## 📊 测试的数据源

### Python 3.8环境

| 数据源 | 状态 | 说明 |
|--------|------|------|
| **BaoStock** | ✅ 可测试 | 完全兼容 |
| **eFinance** | ❌ 不可测试 | 需要Python 3.9+ |
| **qstock** | ❌ 不可测试 | 需要Python 3.9+ |
| **AKShare** | ⚠️ 可能失败 | 依赖冲突 |

### Python 3.9+环境

| 数据源 | 状态 | 说明 |
|--------|------|------|
| **BaoStock** | ✅ 可测试 | 完全兼容 |
| **eFinance** | ✅ 可测试 | 完全兼容 |
| **qstock** | ✅ 可测试 | 完全兼容 |
| **AKShare** | ⚠️ 需手动安装 | 需要先安装curl_cffi |

## 🔧 测试内容

### BaoStock测试项

1. **历史K线数据** - 获取股票历史价格数据
2. **财务指标** - 获取ROE、ROA等财务数据
3. **股票基本信息** - 获取全市场股票列表

### eFinance测试项

1. **历史数据** - 获取股票历史价格
2. **实时行情** - 获取实时股票行情
3. **财务数据** - 获取财务分析数据

### qstock测试项

1. **股票数据** - 获取股票基础数据
2. **市场数据** - 获取市场整体数据

### AKShare测试项

1. **历史数据** - 获取股票历史价格
2. **实时行情** - 获取实时股票行情
3. **财务数据** - 获取财务指标
4. **新闻数据** - 获取股票相关新闻

## 📝 测试报告

测试完成后会生成两个报告：

1. **控制台输出** - 实时显示测试进度和结果
2. **JSON报告** - 保存到 `data_source_test_report.json`

### 报告内容

- ✅ 总体对比表格
- 🏆 最佳数据源推荐
- 📊 详细功能对比
- 📈 成功率统计

## ⚙️ 高级用法

### 1. 手动安装依赖

如果自动安装失败，可以手动安装：

```bash
# 安装BaoStock
pip install baostock

# 安装eFinance (Python 3.9+)
pip install efinance

# 安装qstock (Python 3.9+)
pip install qstock

# 安装AKShare (需要先安装curl_cffi)
pip install curl_cffi
pip install akshare
```

### 2. 使用虚拟环境

推荐使用虚拟环境测试：

```bash
# 创建虚拟环境
python -m venv test_env

# 激活虚拟环境
# Windows:
test_env\Scripts\activate
# Linux/Mac:
source test_env/bin/activate

# 运行测试
python tests/comprehensive_test.py
```

### 3. 使用Conda环境

```bash
# 创建Conda环境
conda create -n test_env python=3.9

# 激活环境
conda activate test_env

# 运行测试
python tests/comprehensive_test.py
```

## 🐛 常见问题

### Q1: AKShare安装失败怎么办？

**A**: AKShare需要先安装curl_cffi：

```bash
pip install curl_cffi
pip install akshare
```

如果仍然失败，可能需要：
- 升级pip: `pip install --upgrade pip`
- 使用Python 3.9+环境

### Q2: eFinance/qstock提示Python版本不兼容？

**A**: 这两个库需要Python 3.9+，请升级Python版本：

```bash
# 使用Conda升级
conda install python=3.9

# 或创建新环境
conda create -n py39_env python=3.9
conda activate py39_env
```

### Q3: BaoStock登录失败？

**A**: BaoStock需要网络连接，请检查：
- 网络是否正常
- 防火墙是否阻止
- 是否需要代理

### Q4: 测试数据为空怎么办？

**A**: 可能的原因：
- 测试日期范围内无交易日
- 股票代码不存在
- 数据源API限制

## 📈 性能优化建议

### 1. 使用缓存

测试脚本已内置缓存机制，重复测试会更快。

### 2. 并行测试

可以修改脚本实现并行测试：

```python
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [
        executor.submit(self.test_baostock),
        executor.submit(self.test_efinance),
        executor.submit(self.test_qstock),
        executor.submit(self.test_akshare),
    ]
    concurrent.futures.wait(futures)
```

### 3. 选择性测试

如果只想测试特定数据源，可以注释掉其他测试：

```python
def run_all_tests(self):
    # self.test_baostock()  # 跳过BaoStock测试
    self.test_efinance()     # 只测试eFinance
    # self.test_qstock()     # 跳过qstock测试
    # self.test_akshare()    # 跳过AKShare测试
```

## 🎯 下一步

测试完成后，根据结果选择最佳数据源：

1. **BaoStock** - 如果测试通过，推荐作为主数据源
2. **eFinance** - 如果需要实时行情，可作为补充
3. **AKShare** - 功能最全面，但安装可能有问题
4. **qstock** - 功能相对简单，适合基础需求

## 📚 相关文档

- [完整测试报告](COMPLETE_DATA_SOURCE_TEST_REPORT.md)
- [元数据映射解决方案](METADATA_MAPPING_SOLUTION.md)
- [免费数据源测试报告](FREE_DATA_SOURCE_TEST_REPORT.md)

---

**最后更新**: 2026-04-24  
**维护者**: AI Hedge Fund Team
