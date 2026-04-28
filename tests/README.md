# A股免费数据源测试

## 🚀 一键测试

```bash
python tests/comprehensive_test.py
```

## 📋 测试说明

这个脚本会自动：
1. ✅ 检测你的Python版本
2. ✅ 安装必要的依赖包
3. ✅ 测试所有免费A股数据源
4. ✅ 生成详细测试报告

## 🎯 推荐环境

- **Python 3.9+**: 可以测试所有数据源
- **Python 3.8**: 只能测试BaoStock

## 📊 测试的数据源

| 数据源 | Python 3.8 | Python 3.9+ | 说明 |
|--------|-----------|-------------|------|
| BaoStock | ✅ | ✅ | 推荐，稳定可靠 |
| eFinance | ❌ | ✅ | 实时行情 |
| qstock | ❌ | ✅ | 简单易用 |
| AKShare | ⚠️ | ⚠️ | 功能最全，但依赖复杂 |

## 📝 测试报告

测试完成后会生成：
- 控制台输出：实时测试结果
- JSON报告：`data_source_test_report.json`

## 📚 详细文档

查看 [综合测试指南](docs/COMPREHENSIVE_TEST_GUIDE.md) 了解更多详情。
