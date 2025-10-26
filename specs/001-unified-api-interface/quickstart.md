# Quickstart Guide: Unified Byapi Client

**For**: Developers using the unified Byapi API client
**Duration**: 5-10 minutes
**Level**: Beginner

---

## Installation

```bash
# Navigate to project directory
cd byapi

# Install dependencies
pip install requests python-dotenv

# (Optional) For DataFrame support
pip install pandas
```

---

## Setup (1 minute)

### 1. Create `.env` file

```bash
# In project root, create .env file
cp .env.example .env

# Edit .env and add your license key(s)
# Single key:
BYAPI_LICENCE=your-key-here

# Multiple keys (for automatic failover):
BYAPI_LICENCE=key1,key2,key3
```

**Never commit `.env` to version control!** It contains sensitive credentials.

### 2. Verify setup

```bash
python -c "from byapi_client_unified import ByapiClient; c = ByapiClient(); print('✓ Setup complete')"
```

---

## Basic Usage (2 minutes)

### Fetch Latest Stock Price

```python
from byapi_client_unified import ByapiClient

# Create client
client = ByapiClient()

# Get latest price for stock 000001 (Ping An Bank)
quote = client.stock_prices.get_latest("000001")

print(f"Stock: {quote.name}")
print(f"Price: ¥{quote.current_price}")
print(f"Change: {quote.change_percent}%")
```

**Output:**
```
Stock: 平安银行
Price: ¥15.23
Change: +1.5%
```

### Get Company Information

```python
# Get company profile
company = client.company_info.get_company("000001")

print(f"Company: {company.name}")
print(f"Industry: {company.industry}")
print(f"Market Cap: ¥{company.market_cap}B")
```

### Get Technical Indicators

```python
# Fetch technical indicators
indicators = client.indicators.get_indicators("000001")

print(f"MA-20: {indicators.ma_20}")
print(f"RSI: {indicators.rsi}")
print(f"MACD: {indicators.macd}")
```

### Get Financial Data

```python
# Fetch financial statements
financials = client.financials.get_financials("000001")

if financials.balance_sheet:
    print(f"Total Assets: ¥{financials.balance_sheet.total_assets}M")
    print(f"Total Liabilities: ¥{financials.balance_sheet.total_liabilities}M")

if financials.income_statement:
    print(f"Revenue: ¥{financials.income_statement.revenue}M")
    print(f"Net Income: ¥{financials.income_statement.net_income}M")
```

### Get Announcements

```python
# Fetch latest 10 announcements
announcements = client.announcements.get_announcements("000001", limit=10)

for ann in announcements:
    print(f"[{ann.announcement_date}] {ann.title}")
    print(f"  Type: {ann.announcement_type}")
    print()
```

---

## Advanced Usage (3-5 minutes)

### Batch Fetch Multiple Stocks

```python
# Fetch data for multiple stocks in one call
stocks = ["000001", "000002", "000858"]
quotes = client.batch.get_batch_prices(stocks)

for quote in quotes:
    print(f"{quote.code}: ¥{quote.current_price}")
```

### Historical Price Data

```python
from datetime import datetime, timedelta

# Fetch last 30 days of price data
end_date = datetime.now().date()
start_date = end_date - timedelta(days=30)

prices = client.stock_prices.get_historical(
    code="000001",
    start_date=start_date,
    end_date=end_date
)

for price in prices:
    print(f"{price.timestamp}: ¥{price.current_price}")
```

### Error Handling

```python
from byapi_client_unified.exceptions import (
    ByapiError,
    NotFoundError,
    RateLimitError,
    AuthenticationError
)

try:
    quote = client.stock_prices.get_latest("999999")
except NotFoundError:
    print("Stock code not found")
except RateLimitError:
    print("Rate limit exceeded, retrying...")
except AuthenticationError:
    print("License key invalid")
except ByapiError as e:
    print(f"API error: {e}")
```

### Access License Key Health Information

```python
# Get health status of all license keys
health_info = client.get_license_health()

for key_health in health_info:
    status = "✓" if key_health.is_usable else "✗"
    print(f"{status} Key {key_health.key[:8]}...")
    print(f"  Status: {key_health.status}")
    print(f"  Failures: {key_health.total_failures}/10")
    print(f"  Consecutive: {key_health.consecutive_failures}/5")
```

### Export Data to CSV

```python
import csv
from datetime import datetime, timedelta

# Fetch data
stocks = ["000001", "000002"]
dates = 30  # Last 30 days

for code in stocks:
    end = datetime.now().date()
    start = end - timedelta(days=dates)

    prices = client.stock_prices.get_historical(code, start, end)

    # Write to CSV
    with open(f"{code}_prices.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Open", "High", "Low", "Close", "Volume"])

        for price in prices:
            writer.writerow([
                price.timestamp,
                price.daily_open,
                price.daily_high,
                price.daily_low,
                price.current_price,
                price.volume
            ])
```

### Convert to Pandas DataFrame

```python
import pandas as pd

# Fetch price data
prices = client.stock_prices.get_historical("000001", start_date, end_date)

# Convert to DataFrame
df = pd.DataFrame([
    {
        'date': p.timestamp,
        'open': p.daily_open,
        'high': p.daily_high,
        'low': p.daily_low,
        'close': p.current_price,
        'volume': p.volume
    }
    for p in prices
])

# Now you can use pandas for analysis
df['sma_20'] = df['close'].rolling(20).mean()
df['volatility'] = df['close'].pct_change().std()
print(df.head())
```

---

## Understanding License Key Failover

The client automatically manages multiple license keys with intelligent failover:

```python
# Configure multiple keys in .env:
# BYAPI_LICENCE=key1,key2,key3

# How failover works:
# 1. Client attempts with key1
# 2. If key1 fails 5 times consecutively → mark as "faulty", try key2
# 3. If key1 fails 10 times total → mark as "invalid", never use again this session
# 4. All keys automatically rotate; no code changes needed
```

**Example session log:**
```
[INFO] Using license key: key1...
[INFO] Call successful
[INFO] Call successful
[WARNING] Call failed (attempt 1/5)
[WARNING] Call failed (attempt 2/5)
[WARNING] Call failed (attempt 3/5)
[WARNING] Call failed (attempt 4/5)
[WARNING] Call failed (attempt 5/5) - Key marked faulty, switching to key2
[INFO] Using license key: key2...
[INFO] Call successful
```

---

## Debugging

### Enable Debug Logging

```python
import logging

# Set to DEBUG for detailed request/response logs
logging.basicConfig(level=logging.DEBUG)

# Now API calls will show full details
client = ByapiClient()
quote = client.stock_prices.get_latest("000001")  # Shows detailed logs
```

### Check API Response Details

```python
from byapi_client_unified import RequestResult

# Get raw response metadata
result: RequestResult = client.stock_prices.get_latest_raw("000001")

print(f"Success: {result.success}")
print(f"Status: {result.status_code}")
print(f"Time: {result.response_time_ms}ms")
print(f"License Key Used: {result.license_key_used}")
print(f"Error: {result.error}")
```

---

## Troubleshooting

### Issue: "License key not found"

**Fix**: Check that `.env` file exists in project root and contains `BYAPI_LICENCE=xxx`

```bash
# Verify .env exists
ls -la .env

# Check content (don't commit this!)
cat .env
```

### Issue: "Rate limit exceeded"

**Fix**: The client has automatic retries; if you still hit rate limit:
1. Add more license keys to `.env`: `BYAPI_LICENCE=key1,key2,key3`
2. Reduce request frequency
3. Use batch endpoints when possible

### Issue: "Stock code not found"

**Fix**: Stock code must be 6 digits (A-share format):
- ✓ Correct: `"000001"` (Ping An)
- ✗ Wrong: `"1"` or `"SH0001"`

### Issue: Data looks strange or incomplete

**Fix**: Check that you're requesting the right data type:
```python
# Empty results are normal for some data types
prices = client.stock_prices.get_latest("000001")
if prices is None:
    print("No price data available")
```

---

## Next Steps

1. **Explore all available functions**: See full API reference in project README
2. **Check examples/**: Run example scripts to see more patterns
3. **Review data-model.md**: Understand all available fields in response objects
4. **Read research.md**: Learn architecture decisions

---

## API Reference

### Client Categories

| Category | Purpose | Example |
|----------|---------|---------|
| `client.stock_prices` | Real-time & historical prices | `get_latest()`, `get_historical()` |
| `client.indicators` | Technical indicators | `get_indicators()` |
| `client.financials` | Financial statements | `get_financials()` |
| `client.announcements` | News & announcements | `get_announcements()` |
| `client.company_info` | Company profiles | `get_company()` |
| `client.indices` | Market indices | `get_all_indices()` |
| `client.batch` | Batch operations | `get_batch_prices()` |

### Response Data Types

- `StockQuote`: Price data
- `TechnicalIndicator`: Indicators (MACD, RSI, etc.)
- `FinancialData`: Balance sheet, income, cash flow
- `StockAnnouncement`: News items
- `CompanyInfo`: Company profile
- `MarketIndex`: Index data

See `/specs/001-unified-api-interface/data-model.md` for complete data structure.

---

## Support

- 📖 **Documentation**: See `README.md` and spec documents in `/specs/001-unified-api-interface/`
- 🐛 **Bug Reports**: Create issue in repository
- 💬 **Questions**: Check examples in `/examples/` directory

**Happy coding! 🚀**
