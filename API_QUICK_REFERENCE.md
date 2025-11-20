# API 快速参考

Byapi 股票 API 客户端的快速函数参考手册。

## 使用方法

```python
from byapi_client_unified import ByapiClient

client = ByapiClient()

# 获取股票价格
quote = client.stock_prices.get_latest("000001")

# 获取技术指标
indicators = client.indicators.get_indicators("000001")

# 获取公司信息
company = client.company_info.get_company_info("000001")
```

## 主要功能

- **股票价格**: 实时和历史数据
- **技术指标**: MA、RSI、MACD、布林带等
- **财务数据**: 资产负债表、利润表、现金流量表
- **公司公告**: 最新公司公告和新闻
- **公司信息**: 公司基本信息

详细文档请参考 README.md