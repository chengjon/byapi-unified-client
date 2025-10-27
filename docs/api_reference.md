# Byapi Stock API Client - API Reference

Complete API reference for the Unified Byapi Stock API Client.

## Quick Links

- [Client Initialization](#client-initialization)
- [Stock Prices](#stock-prices-category)
- [Technical Indicators](#technical-indicators-category)  
- [Financial Statements](#financial-statements-category)
- [Announcements](#announcements-category)
- [Company Information](#company-information-category)
- [Exceptions](#exception-hierarchy)
- [Data Models](#data-models)

## Client Initialization

```python
from byapi_client_unified import ByapiClient

client = ByapiClient()
```

**Available Categories:**
- `client.stock_prices`: Real-time and historical prices
- `client.indicators`: Technical indicators
- `client.financials`: Financial statements
- `client.announcements`: Company news
- `client.company_info`: Company profiles

## Stock Prices Category

### get_latest(code: str) -> StockQuote

Get the latest stock price.

**Example:**
```python
quote = client.stock_prices.get_latest("000001")
print(f"{quote.name}: ¥{quote.current_price} ({quote.change_percent:+.2f}%)")
```

### get_historical(code: str, start_date: str, end_date: str) -> List[StockQuote]

Get historical prices for a date range.

**Example:**
```python
quotes = client.stock_prices.get_historical("000001", "2025-01-01", "2025-01-31")
for q in quotes:
    print(f"{q.timestamp.date()}: ¥{q.current_price}")
```

## Technical Indicators Category

### get_indicators(code: str, start_date: Optional[str], end_date: Optional[str]) -> List[TechnicalIndicator]

Get technical indicators (MA, RSI, MACD, Bollinger Bands, ATR).

**Example:**
```python
indicators = client.indicators.get_indicators("000001")
if indicators:
    ind = indicators[-1]
    print(f"RSI: {ind.rsi:.2f}, MACD: {ind.macd:.4f}, MA20: ¥{ind.ma_20:.2f}")
```

## Financial Statements Category

### get_financials(code: str, statement_type: str = "all") -> FinancialData

Get financial statements.

**statement_type options:**
- `"all"`: All statements (default)
- `"balance_sheet"`: Balance sheet only
- `"income_statement"`: Income statement only
- `"cash_flow"`: Cash flow only

**Example:**
```python
financials = client.financials.get_financials("000001", "balance_sheet")
if financials.balance_sheet:
    bs = financials.balance_sheet
    print(f"Total Assets: ¥{bs.total_assets/1e8:.1f}B")
```

## Announcements Category

### get_announcements(code: str, limit: int = 10) -> List[StockAnnouncement]

Get company announcements.

**Example:**
```python
announcements = client.announcements.get_announcements("000001", limit=5)
for ann in announcements:
    print(f"[{ann.announcement_type}] {ann.title} ({ann.announcement_date})")
```

## Company Information Category

### get_company_info(code: str) -> CompanyInfo

Get company profile information.

**Example:**
```python
company = client.company_info.get_company_info("000001")
print(f"{company.name} - {company.industry}/{company.sector}")
print(f"Market Cap: ¥{company.market_cap/1e8:.1f}B")
```

## Exception Hierarchy

```
ByapiError (base)
├── AuthenticationError
├── DataError
├── NotFoundError
├── RateLimitError
└── NetworkError
```

**Example:**
```python
from byapi_exceptions import AuthenticationError, NotFoundError

try:
    quote = client.stock_prices.get_latest("000001")
except NotFoundError:
    print("Stock not found")
except AuthenticationError:
    print("License key issue")
```

## Data Models

All responses use typed dataclasses from `byapi_models`:
- `StockQuote`
- `TechnicalIndicator`
- `FinancialData` (with `BalanceSheet`, `IncomeStatement`, `CashFlowStatement`)
- `StockAnnouncement`
- `CompanyInfo`

## License Key Management

```python
health = client.get_license_health()
for key_health in health:
    print(f"Status: {key_health.status}")  # healthy, faulty, invalid
    print(f"Failures: {key_health.total_failures}/10")
```

## Configuration

Set environment variables in `.env`:
```env
BYAPI_LICENCE=your_api_key
BYAPI_TIMEOUT=30
BYAPI_MAX_RETRIES=5
BYAPI_LOG_LEVEL=INFO
```

## Error Handling

All methods raise custom exceptions from `byapi_exceptions`:
- `AuthenticationError`: License key issue
- `NotFoundError`: Resource not found  
- `NetworkError`: Connection failed
- `RateLimitError`: Rate limit exceeded
- `DataError`: Response parsing failed

---

**API Version**: 1.0.0
**For full documentation, see docstrings in source code or `help(client.stock_prices.get_latest)`**

