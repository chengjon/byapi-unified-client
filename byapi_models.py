"""
Data models for the Byapi Stock API Client.

This module defines all dataclasses for API responses using Python 3.8+ type hints.
All models are designed for type safety and IDE autocomplete support.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Any, Dict


@dataclass
class StockQuote:
    """Stock price data for a single stock code."""

    code: str
    """Stock code, e.g., "000001" (6-digit format)"""

    name: str
    """Company name"""

    current_price: float
    """Current/latest trading price"""

    previous_close: float
    """Previous closing price"""

    daily_open: float
    """Today's opening price"""

    daily_high: float
    """Today's highest price"""

    daily_low: float
    """Today's lowest price"""

    volume: int
    """Trading volume (shares)"""

    turnover: float
    """Trading turnover (currency)"""

    change: float
    """Price change (absolute, e.g., +1.5)"""

    change_percent: float
    """Price change percentage (e.g., +2.5%)"""

    timestamp: datetime
    """Data timestamp"""

    bid_price: Optional[float] = None
    """Current bid price (optional)"""

    ask_price: Optional[float] = None
    """Current ask price (optional)"""

    def __post_init__(self):
        """Validate data consistency."""
        if self.current_price < 0:
            raise ValueError("current_price cannot be negative")
        if self.volume < 0:
            raise ValueError("volume cannot be negative")


@dataclass
class BalanceSheet:
    """Company balance sheet data."""

    timestamp: date
    """Statement date"""

    total_assets: float
    """Total assets"""

    total_liabilities: float
    """Total liabilities"""

    total_equity: float
    """Total shareholders' equity"""

    current_assets: float
    """Current assets"""

    current_liabilities: float
    """Current liabilities"""

    fixed_assets: Optional[float] = None
    """Fixed assets (optional)"""

    goodwill: Optional[float] = None
    """Goodwill (optional)"""


@dataclass
class IncomeStatement:
    """Company income statement data."""

    timestamp: date
    """Statement date"""

    revenue: float
    """Total revenue"""

    operating_expenses: float
    """Operating expenses"""

    operating_income: float
    """Operating income"""

    net_income: float
    """Net income"""

    eps: float
    """Earnings per share"""


@dataclass
class CashFlowStatement:
    """Company cash flow statement data."""

    timestamp: date
    """Statement date"""

    operating_cash_flow: float
    """Cash flow from operations"""

    investing_cash_flow: float
    """Cash flow from investing"""

    financing_cash_flow: float
    """Cash flow from financing"""

    net_cash_change: float
    """Net change in cash"""


@dataclass
class FinancialData:
    """All financial statements for a company."""

    code: str
    """Stock code"""

    balance_sheet: Optional[BalanceSheet] = None
    """Balance sheet data (optional)"""

    income_statement: Optional[IncomeStatement] = None
    """Income statement data (optional)"""

    cash_flow: Optional[CashFlowStatement] = None
    """Cash flow statement data (optional)"""


@dataclass
class TechnicalIndicator:
    """Technical indicator data for a stock."""

    code: str
    """Stock code"""

    timestamp: datetime
    """Indicator timestamp"""

    # Moving averages
    ma_5: Optional[float] = None
    """5-day moving average"""

    ma_10: Optional[float] = None
    """10-day moving average"""

    ma_20: Optional[float] = None
    """20-day moving average"""

    ma_50: Optional[float] = None
    """50-day moving average"""

    ma_200: Optional[float] = None
    """200-day moving average"""

    # Momentum indicators
    rsi: Optional[float] = None
    """Relative Strength Index (0-100)"""

    macd: Optional[float] = None
    """MACD value"""

    macd_signal: Optional[float] = None
    """MACD signal line"""

    macd_histogram: Optional[float] = None
    """MACD histogram (difference between MACD and signal)"""

    # Volatility indicators
    bollinger_upper: Optional[float] = None
    """Bollinger Band upper boundary"""

    bollinger_middle: Optional[float] = None
    """Bollinger Band middle line (SMA)"""

    bollinger_lower: Optional[float] = None
    """Bollinger Band lower boundary"""

    atr: Optional[float] = None
    """Average True Range (volatility measure)"""

    def __post_init__(self):
        """Validate indicator ranges."""
        if self.rsi is not None and not (0 <= self.rsi <= 100):
            raise ValueError("RSI must be between 0 and 100")


@dataclass
class StockAnnouncement:
    """Company announcement or news item."""

    code: str
    """Stock code"""

    title: str
    """Announcement title"""

    content: str
    """Announcement content"""

    announcement_date: date
    """Date announcement was made"""

    announcement_type: str
    """Type of announcement (e.g., "dividend", "split", "acquisition")"""

    importance: str
    """Importance level (e.g., "high", "medium", "low")"""

    source: Optional[str] = None
    """Source of announcement"""

    url: Optional[str] = None
    """URL to announcement details"""


@dataclass
class CompanyInfo:
    """Company information and classification."""

    code: str
    """Stock code"""

    name: str
    """Company name (Chinese)"""

    industry: str
    """Industry classification"""

    sector: str
    """Sector classification"""

    name_en: Optional[str] = None
    """Company name (English)"""

    market_cap: Optional[float] = None
    """Market capitalization"""

    employees: Optional[int] = None
    """Number of employees"""

    founded_year: Optional[int] = None
    """Year company was founded"""

    exchange: Optional[str] = None
    """Stock exchange code (e.g., "SHA", "SZA")"""

    list_date: Optional[date] = None
    """Date company was listed"""

    description: Optional[str] = None
    """Company description"""


@dataclass
class MarketIndex:
    """Stock market index data."""

    code: str
    """Index code"""

    name: str
    """Index name"""

    current_value: float
    """Current index value"""

    previous_value: float
    """Previous closing value"""

    change: float
    """Point change"""

    change_percent: float
    """Percentage change"""

    timestamp: datetime
    """Data timestamp"""

    constituent_count: Optional[int] = None
    """Number of stocks in the index"""


@dataclass
class RequestResult:
    """Result wrapper for all API responses with metadata."""

    success: bool
    """Whether the request was successful"""

    data: Any
    """Actual response data"""

    error: Optional[str] = None
    """Error message if request failed"""

    error_code: Optional[str] = None
    """Error code identifier"""

    status_code: Optional[int] = None
    """HTTP status code"""

    request_id: Optional[str] = None
    """Request ID for tracing"""

    license_key_used: Optional[str] = None
    """Which license key was used (masked)"""

    response_time_ms: float = 0
    """Response time in milliseconds"""

    timestamp: datetime = field(default_factory=datetime.now)
    """Timestamp of this result"""


# Type aliases for convenience
StockQuoteList = List[StockQuote]
AnnouncementList = List[StockAnnouncement]
IndexList = List[MarketIndex]
