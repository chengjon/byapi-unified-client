# 统一 Byapi 股票 API 客户端

一个全面的、生产就绪的 Python 客户端库，用于从 Byapi API 获取股票市场数据。提供易于使用的函数来获取中国 A 股的实时和历史股价、技术指标、财务报表和公司信息。

## 🎯 特性

- **统一接口**: 所有股票数据按逻辑分类组织，便于发现和使用
- **类型安全**: 完整的类型提示，支持 IDE 自动完成和静态类型检查
- **自动重试**: 带抖动的指数退避，处理瞬时故障
- **多密钥故障转移**: 自动切换许可证密钥，带健康跟踪（连续 5 次失败 = 故障，总计 10 次 = 禁用）
- **错误处理**: 自定义异常层次结构，实现智能错误处理
- **结构化日志**: 全面的日志记录，不暴露敏感数据
- **速率限制支持**: 内置对 API 速率限制的尊重
- **零配置**: 自动从 `.env` 文件加载配置

## 📦 安装

```bash
pip install requests python-dotenv
```

然后将 Byapi 客户端文件复制到您的项目中。

## 🚀 快速开始

### 1. 设置环境

创建 `.env` 文件：

```env
BYAPI_LICENCE=your_api_key_here
```

### 2. 基本用法

```python
from byapi_client_unified import ByapiClient

client = ByapiClient()

# 获取最新股价
quote = client.stock_prices.get_latest("000001")
print(f"{quote.name}: ¥{quote.current_price}")

# 获取历史价格
quotes = client.stock_prices.get_historical("000001", "2025-01-01", "2025-01-31")

# 获取技术指标
indicators = client.indicators.get_indicators("000001")

# 获取财务报表
financials = client.financials.get_financials("000001")

# 获取公司信息
company = client.company_info.get_company_info("000001")

# 获取公告
announcements = client.announcements.get_announcements("000001")
```

## 📚 API 参考

### 数据分类

#### 股票价格
- `get_latest(code: str) -> StockQuote`: 实时价格
- `get_historical(code: str, start_date: str, end_date: str) -> List[StockQuote]`: 历史价格

#### 技术指标
- `get_indicators(code: str, start_date: Optional[str], end_date: Optional[str]) -> List[TechnicalIndicator]`

包含: MA-5/10/20/50/200, RSI, MACD, 布林带, ATR

#### 财务报表
- `get_financials(code: str, statement_type: str = "all") -> FinancialData`

支持: balance_sheet（资产负债表）, income_statement（利润表）, cash_flow（现金流量表）

#### 公告
- `get_announcements(code: str, limit: int = 10) -> List[StockAnnouncement]`

#### 公司信息
- `get_company_info(code: str) -> CompanyInfo`

### 许可证密钥管理

```python
health = client.get_license_health()
for key in health:
    print(f"状态: {key.status}")  # healthy, faulty, 或 invalid
```

## 🛠 错误处理

```python
from byapi_exceptions import (
    AuthenticationError, NotFoundError, NetworkError,
    RateLimitError, DataError
)

try:
    quote = client.stock_prices.get_latest("000001")
except NotFoundError:
    print("股票未找到")
except AuthenticationError:
    print("许可证密钥问题")
except NetworkError:
    print("网络错误 - 自动重试中")
```

## 🔄 多密钥故障转移与健康跟踪

客户端支持多个许可证密钥，具有自动故障转移和健康跟踪功能：

### 配置

在 `.env` 中使用逗号分隔的密钥：

```env
BYAPI_LICENCE=key1,key2,key3
```

### 健康状态

- **Healthy（健康）**: 正常工作
- **Faulty（故障）**: 连续失败 5+ 次（仍可使用）
- **Invalid（无效）**: 总失败 10+ 次（本次会话永久禁用）

### 使用示例

```python
from byapi_client_unified import ByapiClient

client = ByapiClient()

# 检查所有密钥的健康状况
health = client.get_license_health()
for key in health:
    print(f"密钥: {key.key}")           # 为安全起见已掩码（如 "5E93C803..."）
    print(f"状态: {key.status}")        # healthy, faulty, 或 invalid
    print(f"失败次数: {key.total_failures}/10")

# 自动故障转移透明进行
quote = client.stock_prices.get_latest("000001")  # 使用健康密钥
# 如果密钥失败 5+ 次 → 切换到下一个密钥
# 如果所有密钥失败 10+ 次 → 抛出错误
```

### 高级：手动密钥管理

```python
from byapi_config import KeyRotationManager

# 手动密钥轮换
manager = KeyRotationManager(["key1", "key2", "key3"])

# 跟踪密钥健康
manager.mark_key_failure("key1", "401 Unauthorized")
manager.mark_key_success("key2")

# 获取下一个可用密钥
next_key = manager.get_next_key()  # 优先: healthy > faulty > invalid
```

### 密钥优先级层次

客户端按以下顺序自动选择密钥：
1. **健康密钥**（优先）
2. **故障密钥**（如果没有健康密钥可用）
3. **无效密钥**（作为最后手段 - 可能会失败）

完整示例请参见 `examples/license_failover.py`。

## ⚙️ 配置

### 环境变量

| 变量 | 默认值 |
|------|--------|
| `BYAPI_LICENCE` | *（必需）* |
| `BYAPI_BASE_URL` | `http://api.biyingapi.com` |
| `BYAPI_TIMEOUT` | `30` 秒 |
| `BYAPI_MAX_RETRIES` | `5` |
| `BYAPI_LOG_LEVEL` | `INFO` |
| `BYAPI_CONSECUTIVE_FAILURES` | `5`（故障阈值） |
| `BYAPI_TOTAL_FAILURES` | `10`（无效阈值） |

### 重试逻辑

- **基础延迟**: 100ms
- **最大延迟**: 30 秒
- **乘数**: 每次尝试 2 倍
- **抖动**: ±20%
- **最大尝试次数**: 5

### 恢复机制

- **会话作用域**: 进程重启时健康状态重置
- **优雅降级**: 如果没有健康密钥，故障密钥仍可使用
- **日志记录**: 所有密钥失败都会记录以便监控

## 🧪 测试

```bash
pytest tests/integration/
```

## 📈 示例

- `examples/basic_usage.py` - 7 个完整的 API 使用示例
- `examples/license_failover.py` - 多密钥故障转移和健康跟踪（6 个示例）

## 📝 数据类型

所有响应都是类型化的数据类：
- `StockQuote`: 价格数据
- `TechnicalIndicator`: 技术分析
- `FinancialData`: 财务报表
- `StockAnnouncement`: 公告
- `CompanyInfo`: 公司简介

## 版本

**v1.0.0** - 初始版本

功能：
- 股票价格（实时和历史）
- 技术指标
- 财务报表
- 公告和新闻
- 公司信息
- 多密钥故障转移
- 全面的错误处理
- 结构化日志

---

**专为中国股市分析构建**
