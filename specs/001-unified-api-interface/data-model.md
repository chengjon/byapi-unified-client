# Phase 1 Design: Data Model

**Date**: 2025-10-27
**Status**: Complete
**Based on**: `/specs/001-unified-api-interface/spec.md` + `/research.md`

---

## Overview

This document defines all data models, entities, and their relationships for the Unified Byapi API client. All models use Python 3.8+ dataclasses with type hints and optional Pydantic validation.

---

## Core Data Models

### 1. StockQuote
**Purpose**: Real-time or historical stock price data

```python
@dataclass
class StockQuote:
    """Stock price data for a single stock code."""

    code: str                    # Stock code, e.g., "000001"
    name: str                    # Company name
    current_price: float         # Current/latest trading price
    previous_close: float        # Previous closing price
    daily_open: float            # Today's opening price
    daily_high: float            # Today's highest price
    daily_low: float             # Today's lowest price
    volume: int                  # Trading volume (shares)
    turnover: float              # Trading turnover (currency)
    change: float                # Price change (absolute, e.g., +1.5)
    change_percent: float        # Price change percentage (e.g., +2.5%)
    timestamp: datetime           # Data timestamp
    bid_price: Optional[float]   # Current bid price (optional)
    ask_price: Optional[float]   # Current ask price (optional)

    def __post_init__(self):
        """Validate data consistency."""
        if self.current_price < 0:
            raise ValueError("current_price cannot be negative")
        if self.volume < 0:
            raise ValueError("volume cannot be negative")
```

### 2. FinancialData
**Purpose**: Financial statements (balance sheet, income statement, cash flow)

```python
@dataclass
class BalanceSheet:
    """Company balance sheet data."""
    timestamp: date
    total_assets: float
    total_liabilities: float
    total_equity: float
    current_assets: float
    current_liabilities: float
    fixed_assets: Optional[float] = None
    goodwill: Optional[float] = None

@dataclass
class IncomeStatement:
    """Company income statement data."""
    timestamp: date
    revenue: float
    operating_expenses: float
    operating_income: float
    net_income: float
    eps: float  # Earnings per share

@dataclass
class CashFlowStatement:
    """Company cash flow statement data."""
    timestamp: date
    operating_cash_flow: float
    investing_cash_flow: float
    financing_cash_flow: float
    net_cash_change: float

@dataclass
class FinancialData:
    """All financial statements for a company."""
    code: str
    balance_sheet: Optional[BalanceSheet] = None
    income_statement: Optional[IncomeStatement] = None
    cash_flow: Optional[CashFlowStatement] = None
```

### 3. TechnicalIndicator
**Purpose**: Computed technical analysis indicators

```python
@dataclass
class TechnicalIndicator:
    """Technical indicator data for a stock."""
    code: str
    timestamp: datetime

    # Moving averages
    ma_5: Optional[float] = None      # 5-day moving average
    ma_10: Optional[float] = None     # 10-day moving average
    ma_20: Optional[float] = None     # 20-day moving average
    ma_50: Optional[float] = None     # 50-day moving average
    ma_200: Optional[float] = None    # 200-day moving average

    # Momentum indicators
    rsi: Optional[float] = None       # Relative Strength Index (0-100)
    macd: Optional[float] = None      # MACD value
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None

    # Volatility
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr: Optional[float] = None       # Average True Range
```

### 4. StockAnnouncement
**Purpose**: Company announcements and news

```python
@dataclass
class StockAnnouncement:
    """Company announcement or news item."""
    code: str
    title: str
    content: str
    announcement_date: date
    announcement_type: str          # e.g., "dividend", "split", "acquisition"
    importance: str                 # e.g., "high", "medium", "low"
    source: Optional[str] = None
    url: Optional[str] = None
```

### 5. CompanyInfo
**Purpose**: Company profile and classification data

```python
@dataclass
class CompanyInfo:
    """Company information and classification."""
    code: str
    name: str
    name_en: Optional[str] = None
    industry: str                   # Industry classification
    sector: str                     # Sector classification
    market_cap: Optional[float] = None  # Market capitalization
    employees: Optional[int] = None
    founded_year: Optional[int] = None
    exchange: str                   # e.g., "SHA" (Shanghai), "SZA" (Shenzhen)
    list_date: Optional[date] = None
    description: Optional[str] = None
```

### 6. MarketIndex
**Purpose**: Market index data

```python
@dataclass
class MarketIndex:
    """Stock market index data."""
    code: str
    name: str
    current_value: float
    previous_value: float
    change: float
    change_percent: float
    timestamp: datetime
    constituent_count: Optional[int] = None  # Number of stocks in index
```

### 7. LicenseKeyHealth
**Purpose**: Track health status of each license key

```python
@dataclass
class LicenseKeyHealth:
    """License key health tracking for failover."""
    key: str                        # The API license key (masked in logs)
    consecutive_failures: int = 0   # Failures in a row (resets on success)
    total_failures: int = 0         # Total failures in session
    status: str = "healthy"         # healthy | faulty | invalid
    last_failed_timestamp: Optional[datetime] = None
    last_failed_reason: Optional[str] = None

    def mark_failure(self, reason: str) -> str:
        """Record a failure, update status, return new status."""
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_failed_timestamp = datetime.now()
        self.last_failed_reason = reason

        if self.total_failures >= 10:
            self.status = "invalid"
        elif self.consecutive_failures >= 5:
            self.status = "faulty"

        return self.status

    def mark_success(self) -> None:
        """Reset consecutive counter on successful API call."""
        self.consecutive_failures = 0
        self.status = "healthy"

    @property
    def is_usable(self) -> bool:
        """Returns True if key can be used for API calls."""
        return self.status in ["healthy", "faulty"]  # Can retry faulty

    @property
    def is_permanently_disabled(self) -> bool:
        """Returns True if key should never be used again this session."""
        return self.status == "invalid"
```

---

## Response Wrapper Models

### RequestResult
**Purpose**: Wrapper for all API call results with metadata

```python
@dataclass
class RequestResult:
    """Result of an API call with metadata."""
    success: bool
    data: Any                       # Actual response data
    error: Optional[str] = None
    error_code: Optional[str] = None
    status_code: Optional[int] = None
    request_id: Optional[str] = None  # For tracing
    license_key_used: Optional[str] = None  # Which key returned this
    response_time_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.now)
```

---

## Validation Rules

All dataclasses validate data according to these rules:

| Model | Field | Validation |
|-------|-------|-----------|
| StockQuote | current_price | Must be >= 0 |
| StockQuote | volume | Must be >= 0 |
| StockQuote | code | 6-character string (A-share format) |
| FinancialData | timestamp | Must be a valid date |
| TechnicalIndicator | rsi | Must be 0-100 or None |
| CompanyInfo | code | 6-character string |
| LicenseKeyHealth | consecutive_failures | 0 <= x <= 5+ |
| LicenseKeyHealth | total_failures | 0 <= x <= 10+ |

---

## State Transitions

### LicenseKeyHealth State Machine

```
healthy (0 failures)
   |
   | Failure
   v
healthy (1-4 consecutive, N total)
   |
   | 5th consecutive failure
   v
faulty (switch to next key)
   |
   +-> Success: back to healthy
   |
   | Total reaches 10
   v
invalid (permanently disabled this session)
```

---

## Entity Relationships

```
ByapiClient
├── ClientConfig
│   └── LicenseKeyHealth[] (one per key)
├── StockPricesCategory
│   └── methods return StockQuote
├── IndicatorsCategory
│   └── methods return TechnicalIndicator
├── FinancialsCategory
│   └── methods return FinancialData
├── AnnouncementsCategory
│   └── methods return StockAnnouncement
├── CompanyInfoCategory
│   └── methods return CompanyInfo
└── IndicesCategory
    └── methods return MarketIndex
```

---

## Optional: Pydantic Validation

For runtime validation, use Pydantic v2:

```python
from pydantic import BaseModel, Field, validator

class StockQuoteModel(BaseModel):
    """Pydantic version with validation."""
    code: str = Field(..., pattern=r'^\d{6}$')
    current_price: float = Field(..., ge=0)
    volume: int = Field(..., ge=0)

    @validator('code')
    def code_valid_format(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('Stock code must be 6 digits')
        return v

# Usage:
data = StockQuoteModel(**raw_api_response)  # Raises ValidationError if invalid
```

This is optional for MVP; dataclass validation sufficient for initial release.

---

## Summary

- **9 primary data models** covering all API response types
- **LicenseKeyHealth** tracks each key's reliability
- **RequestResult** wraps all responses with metadata
- All models use **type hints** for IDE support
- **Validation rules** ensure data integrity
- **State machine** for license key lifecycle
- Optional **Pydantic** for runtime validation in future versions
