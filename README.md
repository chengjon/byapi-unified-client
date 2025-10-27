# Unified Byapi Stock API Client

A comprehensive, production-ready Python client library for accessing stock market data from the Byapi API. Provides easy-to-use functions for fetching real-time and historical stock prices, technical indicators, financial statements, and company information for Chinese A-share stocks.

## 🎯 Features

- **Unified Interface**: All stock data organized into logical categories for easy discovery
- **Type Safety**: Full type hints for IDE autocomplete and static type checking
- **Automatic Retry**: Exponential backoff with jitter for handling transient failures
- **Multi-Key Failover**: Automatic switching between license keys with health tracking (5 consecutive failures = faulty, 10 total = disabled)
- **Error Handling**: Custom exception hierarchy for intelligent error handling
- **Structured Logging**: Comprehensive logging without exposing sensitive data
- **Rate Limit Support**: Built-in respect for API rate limits
- **Zero Configuration**: Loads configuration from `.env` file automatically

## 📦 Installation

```bash
pip install requests python-dotenv
```

Then copy the Byapi client files to your project.

## 🚀 Quick Start

### 1. Setup Environment

Create a `.env` file:

```env
BYAPI_LICENCE=your_api_key_here
```

### 2. Basic Usage

```python
from byapi_client_unified import ByapiClient

client = ByapiClient()

# Get latest stock price
quote = client.stock_prices.get_latest("000001")
print(f"{quote.name}: ¥{quote.current_price}")

# Get historical prices
quotes = client.stock_prices.get_historical("000001", "2025-01-01", "2025-01-31")

# Get technical indicators
indicators = client.indicators.get_indicators("000001")

# Get financial statements
financials = client.financials.get_financials("000001")

# Get company information
company = client.company_info.get_company_info("000001")

# Get announcements
announcements = client.announcements.get_announcements("000001")
```

## 📚 API Reference

### Data Categories

#### Stock Prices
- `get_latest(code: str) -> StockQuote`: Real-time price
- `get_historical(code: str, start_date: str, end_date: str) -> List[StockQuote]`: Historical prices

#### Technical Indicators
- `get_indicators(code: str, start_date: Optional[str], end_date: Optional[str]) -> List[TechnicalIndicator]`

Includes: MA-5/10/20/50/200, RSI, MACD, Bollinger Bands, ATR

#### Financial Statements
- `get_financials(code: str, statement_type: str = "all") -> FinancialData`

Supports: balance_sheet, income_statement, cash_flow

#### Announcements
- `get_announcements(code: str, limit: int = 10) -> List[StockAnnouncement]`

#### Company Information
- `get_company_info(code: str) -> CompanyInfo`

### License Key Management

```python
health = client.get_license_health()
for key in health:
    print(f"Status: {key.status}")  # healthy, faulty, or invalid
```

## 🛠 Error Handling

```python
from byapi_exceptions import (
    AuthenticationError, NotFoundError, NetworkError,
    RateLimitError, DataError
)

try:
    quote = client.stock_prices.get_latest("000001")
except NotFoundError:
    print("Stock not found")
except AuthenticationError:
    print("License key issue")
except NetworkError:
    print("Network error - auto-retrying")
```

## 🔄 Multi-Key Failover & Health Tracking

The client supports multiple license keys with automatic failover and health tracking:

### Configuration

Use comma-separated keys in `.env`:

```env
BYAPI_LICENCE=key1,key2,key3
```

### Health States

- **Healthy**: Working normally
- **Faulty**: 5+ consecutive failures (still usable)
- **Invalid**: 10+ total failures (permanently disabled this session)

### Example Usage

```python
from byapi_client_unified import ByapiClient

client = ByapiClient()

# Check health of all keys
health = client.get_license_health()
for key in health:
    print(f"Key: {key.key}")           # Masked for safety (e.g., "5E93C803...")
    print(f"Status: {key.status}")     # healthy, faulty, or invalid
    print(f"Failures: {key.total_failures}/10")

# Automatic failover happens transparently
quote = client.stock_prices.get_latest("000001")  # Uses healthy key
# If key fails 5+ times → switches to next key
# If all keys fail 10+ times → raises error
```

### Advanced: Manual Key Management

```python
from byapi_config import KeyRotationManager

# Manual key rotation
manager = KeyRotationManager(["key1", "key2", "key3"])

# Track key health
manager.mark_key_failure("key1", "401 Unauthorized")
manager.mark_key_success("key2")

# Get next usable key
next_key = manager.get_next_key()  # Prefers healthy > faulty > invalid
```

### Key Preference Hierarchy

The client automatically selects keys in this order:
1. **Healthy keys** (preferred)
2. **Faulty keys** (if no healthy keys available)
3. **Invalid keys** (as last resort - will likely fail)

See `examples/license_failover.py` for complete examples.

## ⚙️ Configuration

### Environment Variables

| Variable | Default |
|----------|---------|
| `BYAPI_LICENCE` | *(required)* |
| `BYAPI_BASE_URL` | `http://api.biyingapi.com` |
| `BYAPI_TIMEOUT` | `30` seconds |
| `BYAPI_MAX_RETRIES` | `5` |
| `BYAPI_LOG_LEVEL` | `INFO` |
| `BYAPI_CONSECUTIVE_FAILURES` | `5` (threshold for faulty) |
| `BYAPI_TOTAL_FAILURES` | `10` (threshold for invalid) |

### Retry Logic

- **Base delay**: 100ms
- **Max delay**: 30 seconds
- **Multiplier**: 2x per attempt
- **Jitter**: ±20%
- **Max attempts**: 5

### Recovery

- **Session-scoped**: Health state resets when process restarts
- **Graceful degradation**: Faulty keys are still used if no healthy keys exist
- **Logging**: All key failures are logged for monitoring

## 🧪 Testing

```bash
pytest tests/integration/
```

## 📈 Examples

- `examples/basic_usage.py` - 7 complete API usage examples
- `examples/license_failover.py` - Multi-key failover and health tracking (6 examples)

## 📝 Data Types

All responses are typed dataclasses:
- `StockQuote`: Price data
- `TechnicalIndicator`: Technical analysis
- `FinancialData`: Financial statements
- `StockAnnouncement`: Announcements
- `CompanyInfo`: Company profile

## Version

**v1.0.0** - Initial Release

Features:
- Stock prices (real-time and historical)
- Technical indicators
- Financial statements
- Announcements and news
- Company information
- Multi-key failover
- Comprehensive error handling
- Structured logging

---

**Built for Chinese stock market analysis**
