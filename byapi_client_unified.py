"""
Unified Byapi Stock API Client.

A comprehensive Python client library for accessing stock market data from the Byapi API.
Provides a unified, easy-to-use interface for fetching stock prices, technical indicators,
financial statements, announcements, and more.

Usage:
    from byapi_client_unified import ByapiClient

    client = ByapiClient()
    quote = client.stock_prices.get_latest("000001")
    print(f"Stock {quote.name}: ¥{quote.current_price}")

Key Features:
    - Multiple license key support with automatic failover
    - Intelligent retry logic with exponential backoff
    - Automatic license key health tracking (5/10 failure thresholds)
    - Type-hinted responses for IDE autocomplete
    - Comprehensive error handling
    - Structured logging without exposing secrets
"""

import logging
import random
import time
from typing import Optional, List, Any, Dict
from datetime import datetime, timedelta

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError

from byapi_config import ByapiConfig, config
from byapi_exceptions import (
    ByapiError,
    AuthenticationError,
    DataError,
    NotFoundError,
    RateLimitError,
    NetworkError,
)
from byapi_models import (
    StockQuote,
    TechnicalIndicator,
    FinancialData,
    StockAnnouncement,
    CompanyInfo,
    MarketIndex,
    RequestResult,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Configure module version
__version__ = "1.0.0"
__author__ = "Byapi Client Team"


class BaseApiHandler:
    """
    Base class for handling API requests with retry logic and error handling.

    Provides:
    - HTTP request handling
    - License key injection
    - Exponential backoff retry
    - Error mapping to custom exceptions
    - Request/response logging
    """

    def __init__(self, config: ByapiConfig):
        """
        Initialize API handler.

        Args:
            config: ByapiConfig instance with settings
        """
        self.config = config
        self.session = requests.Session()

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        use_https: bool = False,
        **kwargs
    ) -> RequestResult:
        """
        Make an API request with retry logic and error handling.

        Args:
            endpoint: API endpoint (e.g., "hslt/list")
            params: Query parameters
            use_https: Whether to use HTTPS
            **kwargs: Additional arguments to pass to requests

        Returns:
            RequestResult with response data or error information
        """
        base_url = self.config.https_base_url if use_https else self.config.base_url
        license_key = self.config.get_license_key()

        # Construct full URL with license key
        url = f"{base_url}/{endpoint}/{license_key}"

        start_time = time.time()
        attempt = 0
        last_error = None

        while attempt < self.config.max_retries:
            try:
                logger.debug(f"API request: {attempt + 1}/{self.config.max_retries} - {endpoint}")

                response = self.session.get(
                    url,
                    params=params,
                    timeout=self.config.timeout,
                    **kwargs
                )

                response_time_ms = (time.time() - start_time) * 1000

                # Handle HTTP errors
                if response.status_code == 429:
                    # Rate limit - will retry
                    last_error = ("rate_limit", "HTTP 429: Too Many Requests")
                    attempt += 1
                    if attempt < self.config.max_retries:
                        self._wait_exponential(attempt)
                    continue

                elif response.status_code == 401 or response.status_code == 403:
                    # Auth error
                    self.config.key_manager.mark_key_failure(
                        license_key, f"HTTP {response.status_code}: Authentication failed"
                    )
                    raise AuthenticationError(
                        f"Authentication failed (HTTP {response.status_code}). "
                        f"Check your license key.",
                        status_code=response.status_code,
                    )

                elif response.status_code >= 400:
                    # Client error (4xx except above)
                    error_msg = f"HTTP {response.status_code}: Client error"
                    self.config.key_manager.mark_key_failure(license_key, error_msg)
                    raise DataError(
                        f"API request failed: {error_msg}",
                        status_code=response.status_code,
                    )

                elif response.status_code >= 500:
                    # Server error (5xx) - will retry
                    last_error = ("server_error", f"HTTP {response.status_code}")
                    attempt += 1
                    if attempt < self.config.max_retries:
                        self._wait_exponential(attempt)
                    continue

                # Success (2xx)
                response.raise_for_status()

                # Parse response
                try:
                    data = response.json()
                except ValueError as e:
                    raise DataError(
                        f"Failed to parse API response as JSON: {e}",
                        cause=e,
                    )

                # Mark key as successful
                self.config.key_manager.mark_key_success(license_key)

                logger.debug(f"API request successful in {response_time_ms:.1f}ms")

                # Return successful result
                return RequestResult(
                    success=True,
                    data=data,
                    status_code=response.status_code,
                    response_time_ms=response_time_ms,
                    license_key_used=license_key[:8] + "...",
                    timestamp=datetime.now(),
                )

            except (Timeout, ConnectionError) as e:
                # Network error - will retry
                last_error = ("network_error", str(e))
                self.config.key_manager.mark_key_failure(license_key, f"Network error: {e}")
                attempt += 1
                if attempt < self.config.max_retries:
                    self._wait_exponential(attempt)
                continue

            except (AuthenticationError, DataError) as e:
                # These are already handled, re-raise
                raise

            except Exception as e:
                # Unknown error
                logger.error(f"Unexpected error: {e}")
                raise ByapiError(
                    f"Unexpected error during API call: {e}",
                    cause=e,
                )

        # All retries exhausted
        response_time_ms = (time.time() - start_time) * 1000

        if last_error:
            error_type, error_msg = last_error
            if error_type == "rate_limit":
                raise RateLimitError(
                    f"Rate limit exceeded after {self.config.max_retries} retries",
                )
            else:
                raise NetworkError(
                    f"Network error after {self.config.max_retries} retries: {error_msg}",
                )
        else:
            raise ByapiError(
                f"API request failed after {self.config.max_retries} retries",
            )

    def _wait_exponential(self, attempt: int) -> None:
        """
        Wait with exponential backoff and jitter.

        Args:
            attempt: Current attempt number (1-indexed)
        """
        # Calculate delay: base * (2 ^ (attempt - 1))
        delay = self.config.retry_base_delay * (2 ** (attempt - 1))
        delay = min(delay, self.config.retry_max_delay)

        # Add jitter: ±20%
        jitter = delay * random.uniform(-0.2, 0.2)
        actual_delay = delay + jitter

        logger.debug(f"Retry {attempt}: waiting {actual_delay:.2f}s (base: {delay:.2f}s)")
        time.sleep(actual_delay)


class StockPricesCategory:
    """
    Stock price data retrieval category.

    Provides access to real-time and historical stock price data for Chinese A-share stocks.
    Automatically handles license key injection, error handling, and data parsing.

    Example:
        >>> client = ByapiClient()
        >>> quote = client.stock_prices.get_latest("000001")
        >>> print(f"Stock {quote.name}: ¥{quote.current_price}")
        Stock 中国神华: ¥15.45

        >>> quotes = client.stock_prices.get_historical("000001", "2025-01-01", "2025-01-10")
        >>> for q in quotes:
        ...     print(f"{q.timestamp.date()}: ¥{q.current_price}")
    """

    def __init__(self, handler: BaseApiHandler):
        """
        Initialize stock prices category.

        Args:
            handler: BaseApiHandler instance for API requests with retry logic
        """
        self.handler = handler

    def get_latest(self, code: str) -> StockQuote:
        """
        Get latest/current stock price for a single stock.

        Fetches real-time trading price data for a single stock code. Returns a StockQuote
        object containing current price, daily high/low, volume, and price changes.

        Args:
            code (str): Stock code in 6-digit format (e.g., "000001" for 中国神华).
                       Supports both Shanghai (600xxx) and Shenzhen (000xxx, 200xxx) codes.

        Returns:
            StockQuote: Object containing:
                - code: Stock code
                - name: Company name
                - current_price: Current trading price (latest)
                - daily_open: Today's opening price
                - daily_high: Today's highest price
                - daily_low: Today's lowest price
                - volume: Trading volume (shares)
                - turnover: Trading amount (currency)
                - change: Absolute price change
                - change_percent: Percentage price change
                - timestamp: Data timestamp
                - bid_price: Bid price (optional)
                - ask_price: Ask price (optional)

        Raises:
            NotFoundError: If stock code is invalid or not found.
            AuthenticationError: If API authentication fails (license key issue).
            DataError: If API response is malformed or unparseable.
            NetworkError: If network connection fails after retries.
            RateLimitError: If rate limit is exceeded.

        Example:
            >>> client = ByapiClient()
            >>> quote = client.stock_prices.get_latest("000001")
            >>> print(f"{quote.name}: ¥{quote.current_price} ({quote.change_percent:+.2f}%)")
            中国神华: ¥15.45 (+2.50%)
            >>> print(f"Volume: {quote.volume:,} shares")
            Volume: 45,678,900 shares
        """
        # API endpoint: hsstock/latest/{stock_code_market}/d/n
        # Where stock_code_market is code with market prefix (SHA: 600xxx, SZA: 000xxx)
        # For simplicity, we'll use the code directly (API will resolve it)
        result = self.handler._make_request(
            f"hsstock/latest/{code}/d/n",
            use_https=True
        )

        if not result.data:
            raise NotFoundError(f"No data found for stock code: {code}")

        # Parse the response - API returns raw dict
        data = result.data

        # Build StockQuote from response
        try:
            quote = StockQuote(
                code=code,
                name=data.get("name", ""),
                current_price=float(data.get("close", 0)),
                previous_close=float(data.get("pre_close", 0)),
                daily_open=float(data.get("open", 0)),
                daily_high=float(data.get("high", 0)),
                daily_low=float(data.get("low", 0)),
                volume=int(data.get("volume", 0)),
                turnover=float(data.get("amount", 0)),
                change=float(data.get("price_change", 0)),
                change_percent=float(data.get("pct_change", 0)),
                timestamp=datetime.fromisoformat(data.get("trade_date", datetime.now().isoformat())),
                bid_price=float(data.get("bid", 0)) if "bid" in data else None,
                ask_price=float(data.get("ask", 0)) if "ask" in data else None,
            )
            return quote
        except (KeyError, ValueError, TypeError) as e:
            raise DataError(f"Failed to parse stock quote data: {e}", cause=e)

    def get_historical(
        self,
        code: str,
        start_date: str,
        end_date: str,
    ) -> List[StockQuote]:
        """
        Get historical stock prices for a date range.

        Fetches historical daily price data for a stock between two dates. Useful for
        analyzing price trends, computing technical indicators, or backtesting strategies.

        Args:
            code (str): Stock code in 6-digit format (e.g., "000001").
            start_date (str): Start date in YYYY-MM-DD format (e.g., "2025-01-01").
                            Inclusive - data from this date is included.
            end_date (str): End date in YYYY-MM-DD format (e.g., "2025-01-31").
                           Inclusive - data up to this date is included.

        Returns:
            List[StockQuote]: List of StockQuote objects, one per trading day.
                             Ordered chronologically (oldest first).
                             Empty list if no data available for date range.

                             Each StockQuote contains:
                             - code, name: Stock identifier
                             - current_price, daily_open, daily_high, daily_low: Price data
                             - volume, turnover: Trading activity
                             - change, change_percent: Price movement
                             - timestamp: Trading date

        Raises:
            NotFoundError: If stock code is invalid or not found.
            AuthenticationError: If API authentication fails.
            DataError: If response is malformed.
            NetworkError: If connection fails.

        Example:
            >>> from datetime import datetime, timedelta
            >>> client = ByapiClient()
            >>> end = datetime.now().strftime("%Y-%m-%d")
            >>> start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            >>> quotes = client.stock_prices.get_historical("000001", start, end)
            >>> print(f"Retrieved {len(quotes)} trading days")
            Retrieved 20 trading days
            >>> for q in quotes[-5:]:  # Last 5 days
            ...     print(f"{q.timestamp.date()}: Open ¥{q.daily_open:.2f}, "
            ...           f"Close ¥{q.current_price:.2f}, Vol {q.volume:,}")
            2025-01-27: Open ¥15.20, Close ¥15.45, Vol 45678900
            2025-01-28: Open ¥15.45, Close ¥15.60, Vol 52341200
        """
        # API endpoint: hsstock/history/{stock_code_market}/d/n
        # Parameters: st (start time), et (end time)
        params = {
            "st": start_date,
            "et": end_date,
        }

        result = self.handler._make_request(
            f"hsstock/history/{code}/d/n",
            params=params,
            use_https=True
        )

        if not result.data:
            return []

        quotes = []
        data_list = result.data if isinstance(result.data, list) else [result.data]

        try:
            for data in data_list:
                quote = StockQuote(
                    code=code,
                    name=data.get("name", ""),
                    current_price=float(data.get("close", 0)),
                    previous_close=float(data.get("pre_close", 0)),
                    daily_open=float(data.get("open", 0)),
                    daily_high=float(data.get("high", 0)),
                    daily_low=float(data.get("low", 0)),
                    volume=int(data.get("volume", 0)),
                    turnover=float(data.get("amount", 0)),
                    change=float(data.get("price_change", 0)),
                    change_percent=float(data.get("pct_change", 0)),
                    timestamp=datetime.fromisoformat(data.get("trade_date", datetime.now().isoformat())),
                )
                quotes.append(quote)
            return quotes
        except (KeyError, ValueError, TypeError) as e:
            raise DataError(f"Failed to parse historical quote data: {e}", cause=e)


class IndicatorsCategory:
    """
    Technical indicators and analysis category.

    Provides access to technical analysis indicators (moving averages, RSI, MACD, Bollinger Bands, etc.)
    for price analysis and trading signal generation.

    Example:
        >>> client = ByapiClient()
        >>> indicators = client.indicators.get_indicators("000001")
        >>> if indicators:
        ...     latest = indicators[-1]
        ...     print(f"RSI: {latest.rsi:.2f}")
        ...     print(f"MA-20: ¥{latest.ma_20:.2f}")
        ...     print(f"MACD: {latest.macd:.4f}")
    """

    def __init__(self, handler: BaseApiHandler):
        """
        Initialize indicators category.

        Args:
            handler: BaseApiHandler instance for API requests
        """
        self.handler = handler

    def get_indicators(self, code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[TechnicalIndicator]:
        """
        Get technical indicators for a stock.

        Fetches technical analysis indicators including moving averages (MA-5/10/20/50/200),
        momentum indicators (RSI, MACD), and volatility indicators (Bollinger Bands, ATR).

        Args:
            code (str): Stock code in 6-digit format (e.g., "000001").
            start_date (str, optional): Start date in YYYY-MM-DD format. Defaults to None (all available data).
            end_date (str, optional): End date in YYYY-MM-DD format. Defaults to None (current).

        Returns:
            List[TechnicalIndicator]: List of indicator objects, one per time period.
                                    Empty list if no data available.

                                    Each TechnicalIndicator contains:
                                    - code, timestamp: Identifier and time
                                    - ma_5, ma_10, ma_20, ma_50, ma_200: Moving averages
                                    - rsi: Relative Strength Index (0-100)
                                    - macd, macd_signal, macd_histogram: MACD indicators
                                    - bollinger_upper/middle/lower: Bollinger Bands
                                    - atr: Average True Range (volatility)

        Raises:
            DataError: If response parsing fails.
            NetworkError: If connection fails.

        Example:
            >>> client = ByapiClient()
            >>> indicators = client.indicators.get_indicators("000001", "2025-01-01", "2025-01-31")
            >>> print(f"Retrieved {len(indicators)} indicator records")
            Retrieved 20 indicator records
            >>> for ind in indicators[-3:]:
            ...     print(f"{ind.timestamp.date()}: RSI={ind.rsi:.2f} "
            ...           f"MACD={ind.macd:.4f} MA20=¥{ind.ma_20:.2f}")
            2025-01-27: RSI=65.32 MACD=0.0234 MA20=¥15.18
            2025-01-28: RSI=68.45 MACD=0.0267 MA20=¥15.22
        """
        # API endpoint: hsstock/indicators
        params = {"stock_code_market": code}
        if start_date:
            params["st"] = start_date
        if end_date:
            params["et"] = end_date

        result = self.handler._make_request(
            "hsstock/indicators",
            params=params,
            use_https=True
        )

        if not result.data:
            return []

        indicators = []
        data_list = result.data if isinstance(result.data, list) else [result.data]

        try:
            for data in data_list:
                indicator = TechnicalIndicator(
                    code=code,
                    timestamp=datetime.fromisoformat(data.get("date", datetime.now().isoformat())),
                    ma_5=float(data.get("ma5", 0)) if "ma5" in data else None,
                    ma_10=float(data.get("ma10", 0)) if "ma10" in data else None,
                    ma_20=float(data.get("ma20", 0)) if "ma20" in data else None,
                    ma_50=float(data.get("ma50", 0)) if "ma50" in data else None,
                    ma_200=float(data.get("ma200", 0)) if "ma200" in data else None,
                    rsi=float(data.get("rsi", 0)) if "rsi" in data else None,
                    macd=float(data.get("macd", 0)) if "macd" in data else None,
                    macd_signal=float(data.get("macd_signal", 0)) if "macd_signal" in data else None,
                    macd_histogram=float(data.get("macd_histogram", 0)) if "macd_histogram" in data else None,
                    bollinger_upper=float(data.get("boll_up", 0)) if "boll_up" in data else None,
                    bollinger_middle=float(data.get("boll_mid", 0)) if "boll_mid" in data else None,
                    bollinger_lower=float(data.get("boll_dn", 0)) if "boll_dn" in data else None,
                    atr=float(data.get("atr", 0)) if "atr" in data else None,
                )
                indicators.append(indicator)
            return indicators
        except (KeyError, ValueError, TypeError) as e:
            raise DataError(f"Failed to parse technical indicator data: {e}", cause=e)


class FinancialsCategory:
    """
    Financial statements category.

    Provides access to company financial data including balance sheets, income statements,
    and cash flow statements. Useful for fundamental analysis and financial health assessment.

    Example:
        >>> client = ByapiClient()
        >>> financials = client.financials.get_financials("000001")
        >>> if financials.balance_sheet:
        ...     bs = financials.balance_sheet
        ...     print(f"Total Assets: ¥{bs.total_assets:,.0f}")
        ...     print(f"Debt/Equity: {bs.total_liabilities/bs.total_equity:.2f}")
    """

    def __init__(self, handler: BaseApiHandler):
        """
        Initialize financials category.

        Args:
            handler: BaseApiHandler instance for API requests
        """
        self.handler = handler

    def get_financials(
        self,
        code: str,
        statement_type: str = "all",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> FinancialData:
        """
        Get financial statements for a stock.

        Retrieves company financial data from annual/quarterly reports. Can fetch balance sheets,
        income statements, and cash flow statements independently or together.

        Args:
            code (str): Stock code in 6-digit format (e.g., "000001").
            statement_type (str): Which statements to retrieve. Options:
                                - "all": All three statements (default)
                                - "balance_sheet": Balance sheet only
                                - "income_statement": Income statement only
                                - "cash_flow": Cash flow statement only
            start_date (str, optional): Start date for historical data (YYYY-MM-DD format).
            end_date (str, optional): End date for historical data (YYYY-MM-DD format).

        Returns:
            FinancialData: Object containing:
                - code: Stock code
                - balance_sheet: BalanceSheet object (if requested) with:
                    * total_assets, total_liabilities, total_equity
                    * current_assets, current_liabilities, fixed_assets
                - income_statement: IncomeStatement object (if requested) with:
                    * revenue, operating_expenses, operating_income, net_income, eps
                - cash_flow: CashFlowStatement object (if requested) with:
                    * operating_cash_flow, investing_cash_flow, financing_cash_flow, net_cash_change

        Raises:
            DataError: If response parsing fails.
            NetworkError: If connection fails.

        Example:
            >>> client = ByapiClient()
            >>> fd = client.financials.get_financials("000001", "balance_sheet")
            >>> if fd.balance_sheet:
            ...     bs = fd.balance_sheet
            ...     print(f"Balance Sheet as of {bs.timestamp}")
            ...     print(f"Assets: ¥{bs.total_assets/1e8:.1f}B")
            ...     print(f"Equity: ¥{bs.total_equity/1e8:.1f}B")
            Balance Sheet as of 2024-12-31
            Assets: ¥128.5B
            Equity: ¥72.3B

            >>> fd_all = client.financials.get_financials("000001", "all")
            >>> if fd_all.income_statement:
            ...     inc = fd_all.income_statement
            ...     profit_margin = (inc.net_income / inc.revenue) * 100
            ...     print(f"Profit Margin: {profit_margin:.2f}%")
            Profit Margin: 12.45%
        """
        financial_data = FinancialData(code=code)

        try:
            if statement_type in ["balance_sheet", "all"]:
                balance_result = self.handler._make_request(
                    "hsstock/financial/balance",
                    params={"stock_code_market": code},
                    use_https=True
                )
                if balance_result.data:
                    data = balance_result.data
                    financial_data.balance_sheet = BalanceSheet(
                        timestamp=datetime.fromisoformat(data.get("date", datetime.now().isoformat())).date(),
                        total_assets=float(data.get("total_assets", 0)),
                        total_liabilities=float(data.get("total_liabilities", 0)),
                        total_equity=float(data.get("total_equity", 0)),
                        current_assets=float(data.get("current_assets", 0)),
                        current_liabilities=float(data.get("current_liabilities", 0)),
                        fixed_assets=float(data.get("fixed_assets", 0)) if "fixed_assets" in data else None,
                    )

            if statement_type in ["income_statement", "all"]:
                income_result = self.handler._make_request(
                    "hsstock/financial/income",
                    params={"stock_code_market": code},
                    use_https=True
                )
                if income_result.data:
                    data = income_result.data
                    financial_data.income_statement = IncomeStatement(
                        timestamp=datetime.fromisoformat(data.get("date", datetime.now().isoformat())).date(),
                        revenue=float(data.get("revenue", 0)),
                        operating_expenses=float(data.get("operating_expenses", 0)),
                        operating_income=float(data.get("operating_income", 0)),
                        net_income=float(data.get("net_income", 0)),
                        eps=float(data.get("eps", 0)),
                    )

            if statement_type in ["cash_flow", "all"]:
                cashflow_result = self.handler._make_request(
                    "hsstock/financial/cashflow",
                    params={"stock_code_market": code},
                    use_https=True
                )
                if cashflow_result.data:
                    data = cashflow_result.data
                    financial_data.cash_flow = CashFlowStatement(
                        timestamp=datetime.fromisoformat(data.get("date", datetime.now().isoformat())).date(),
                        operating_cash_flow=float(data.get("operating_cash_flow", 0)),
                        investing_cash_flow=float(data.get("investing_cash_flow", 0)),
                        financing_cash_flow=float(data.get("financing_cash_flow", 0)),
                        net_cash_change=float(data.get("net_cash_change", 0)),
                    )

            return financial_data
        except (KeyError, ValueError, TypeError) as e:
            raise DataError(f"Failed to parse financial data: {e}", cause=e)


class AnnouncementsCategory:
    """
    Company announcements and news category.

    Provides access to company news, announcements, and major events (dividends, splits,
    acquisitions, earnings, etc.) that may impact stock prices.

    Example:
        >>> client = ByapiClient()
        >>> announcements = client.announcements.get_announcements("000001", limit=5)
        >>> for ann in announcements:
        ...     print(f"[{ann.announcement_type.upper()}] {ann.title}")
        ...     print(f"  Importance: {ann.importance} | Date: {ann.announcement_date}")
    """

    def __init__(self, handler: BaseApiHandler):
        """
        Initialize announcements category.

        Args:
            handler: BaseApiHandler instance for API requests
        """
        self.handler = handler

    def get_announcements(self, code: str, limit: int = 10) -> List[StockAnnouncement]:
        """
        Get recent company announcements for a stock.

        Retrieves latest company announcements, news, and major events. Useful for
        tracking corporate actions and news that may affect stock performance.

        Args:
            code (str): Stock code in 6-digit format (e.g., "000001").
            limit (int): Maximum number of announcements to return (default: 10).
                        Use larger values for more historical announcements.

        Returns:
            List[StockAnnouncement]: List of announcements, newest first.
                                    Empty list if no announcements available.

                                    Each StockAnnouncement contains:
                                    - code: Stock code
                                    - title: Announcement title
                                    - content: Full announcement text
                                    - announcement_date: Date announcement was made
                                    - announcement_type: Type (e.g., "dividend", "split", "acquisition")
                                    - importance: Level ("high", "medium", "low")
                                    - source: News source (optional)
                                    - url: Link to full announcement (optional)

        Raises:
            DataError: If response parsing fails.
            NetworkError: If connection fails.

        Example:
            >>> client = ByapiClient()
            >>> announcements = client.announcements.get_announcements("000001", limit=10)
            >>> print(f"Found {len(announcements)} recent announcements")
            Found 8 recent announcements
            >>> for ann in announcements[:3]:
            ...     print(f"{ann.announcement_date}: {ann.title}")
            ...     print(f"  Type: {ann.announcement_type}, Importance: {ann.importance}")
            2025-01-28: 2024年度分红预案
              Type: dividend, Importance: high
            2025-01-20: 股东大会预告
              Type: shareholder_meeting, Importance: medium
        """
        # API endpoint: hscp/ljgg (latest announcements)
        params = {"stock_code": code}

        result = self.handler._make_request(
            "hscp/ljgg",
            params=params
        )

        if not result.data:
            return []

        announcements = []
        data_list = result.data if isinstance(result.data, list) else [result.data]

        try:
            for i, data in enumerate(data_list):
                if i >= limit:
                    break

                announcement = StockAnnouncement(
                    code=code,
                    title=data.get("title", ""),
                    content=data.get("content", ""),
                    announcement_date=datetime.fromisoformat(data.get("date", datetime.now().isoformat())).date(),
                    announcement_type=data.get("type", "news"),
                    importance=data.get("importance", "medium"),
                    source=data.get("source", None),
                    url=data.get("url", None),
                )
                announcements.append(announcement)
            return announcements
        except (KeyError, ValueError, TypeError) as e:
            raise DataError(f"Failed to parse announcement data: {e}", cause=e)


class CompanyInfoCategory:
    """
    Company information and classification category.

    Provides access to company profile information including industry classification,
    market cap, employee count, founding date, and exchange listing details.

    Example:
        >>> client = ByapiClient()
        >>> company = client.company_info.get_company_info("000001")
        >>> print(f"{company.name} ({company.code})")
        >>> print(f"Industry: {company.industry} | Sector: {company.sector}")
        >>> if company.market_cap:
        ...     print(f"Market Cap: ¥{company.market_cap/1e8:.1f}B")
    """

    def __init__(self, handler: BaseApiHandler):
        """
        Initialize company info category.

        Args:
            handler: BaseApiHandler instance for API requests
        """
        self.handler = handler

    def get_company_info(self, code: str) -> CompanyInfo:
        """
        Get company information for a stock.

        Retrieves detailed company profile information including name, industry/sector
        classification, market cap, employee count, founding year, and exchange listing details.

        Args:
            code (str): Stock code in 6-digit format (e.g., "000001").

        Returns:
            CompanyInfo: Object containing:
                - code: Stock code (6-digit)
                - name: Company name in Chinese
                - industry: Industry classification (e.g., "能源")
                - sector: Sector classification (e.g., "采矿")
                - name_en: Company name in English (optional)
                - market_cap: Market capitalization in yuan (optional)
                - employees: Number of employees (optional)
                - founded_year: Year company was founded (optional)
                - exchange: Stock exchange code (e.g., "SHA", "SZA") (optional)
                - list_date: Date listed on exchange (optional)
                - description: Company description (optional)

        Raises:
            NotFoundError: If company not found.
            DataError: If response parsing fails.
            NetworkError: If connection fails.

        Example:
            >>> client = ByapiClient()
            >>> company = client.company_info.get_company_info("000001")
            >>> print(f"Company: {company.name}")
            Company: 中国神华能源股份有限公司
            >>> print(f"Listed: {company.list_date} on {company.exchange}")
            Listed: 2008-10-16 on SZA
            >>> if company.market_cap:
            ...     cap_b = company.market_cap / 1e8
            ...     print(f"Market Cap: ¥{cap_b:.1f}B")
            Market Cap: ¥128.5B
            >>> if company.employees:
            ...     print(f"Employees: {company.employees:,}")
            Employees: 45,200
        """
        # API endpoint: hscp/gsjj (company introduction)
        params = {"stock_code": code}

        result = self.handler._make_request(
            "hscp/gsjj",
            params=params
        )

        if not result.data:
            raise NotFoundError(f"Company information not found for code: {code}")

        try:
            data = result.data
            company = CompanyInfo(
                code=code,
                name=data.get("name", ""),
                industry=data.get("industry", ""),
                sector=data.get("sector", ""),
                name_en=data.get("name_en", None),
                market_cap=float(data.get("market_cap", 0)) if "market_cap" in data else None,
                employees=int(data.get("employees", 0)) if "employees" in data else None,
                founded_year=int(data.get("founded_year", 0)) if "founded_year" in data else None,
                exchange=data.get("exchange", None),
                list_date=datetime.fromisoformat(data.get("list_date", datetime.now().isoformat())).date() if "list_date" in data else None,
                description=data.get("description", None),
            )
            return company
        except (KeyError, ValueError, TypeError) as e:
            raise DataError(f"Failed to parse company info: {e}", cause=e)


class ByapiClient:
    """
    Unified Byapi Stock API Client - Main entry point.

    A comprehensive, production-ready Python client library for accessing stock market data
    from the Byapi API (http://api.biyingapi.com). Provides easy-to-use functions for
    fetching stock prices, technical indicators, financial statements, and company information.

    **Key Features**:
    - **Unified Interface**: All data organized into logical categories for discoverability
    - **Type Safety**: Full type hints for IDE autocomplete and static type checking
    - **Error Handling**: Custom exception hierarchy for intelligent error handling
    - **Automatic Retry**: Exponential backoff with jitter for transient failures
    - **Multi-Key Failover**: Automatic switching between license keys with health tracking
    - **Structured Logging**: Comprehensive logging without exposing sensitive data
    - **Rate Limit Handling**: Built-in respect for API rate limits

    **Installation**:
        pip install byapi-client

    **Setup** (create `.env` file):
        BYAPI_LICENCE=your_api_key_here

    **Quick Start**:
        from byapi_client_unified import ByapiClient

        client = ByapiClient()

        # Get latest stock price
        quote = client.stock_prices.get_latest("000001")
        print(f"{quote.name}: ¥{quote.current_price}")

        # Get technical indicators
        indicators = client.indicators.get_indicators("000001")

        # Get financial statements
        financials = client.financials.get_financials("000001")

        # Get company information
        company = client.company_info.get_company_info("000001")

        # Get announcements
        announcements = client.announcements.get_announcements("000001")

    **Categories** (accessed as properties):
        client.stock_prices: Real-time and historical price data
        client.indicators: Technical indicators and analysis
        client.financials: Balance sheets, income, cash flow statements
        client.announcements: Company news and announcements
        client.company_info: Company profile and classification

    **Error Handling**:
        from byapi_exceptions import (
            AuthenticationError, NotFoundError, NetworkError,
            RateLimitError, DataError
        )

        try:
            quote = client.stock_prices.get_latest("000001")
        except NotFoundError:
            print("Stock code not found")
        except AuthenticationError:
            print("License key issue - check .env file")
        except NetworkError:
            print("Network issue - will retry automatically")
        except RateLimitError:
            print("Rate limit exceeded - try again later")

    **License Key Management**:
        # Single key
        BYAPI_LICENCE=key_abc123

        # Multiple keys (automatic failover)
        BYAPI_LICENCE=key_abc123,key_def456,key_ghi789

        # Check key health
        health = client.get_license_health()
        for key_health in health:
            print(f"Status: {key_health.status}")
            print(f"Failures: {key_health.total_failures}/10")

    **Environment Variables**:
        BYAPI_LICENCE (required): API license key(s) - comma-separated for multiple
        BYAPI_BASE_URL (optional): API base URL (default: http://api.biyingapi.com)
        BYAPI_HTTPS_BASE_URL (optional): HTTPS URL (default: https://api.biyingapi.com)
        BYAPI_TIMEOUT (optional): Request timeout in seconds (default: 30)
        BYAPI_MAX_RETRIES (optional): Max retry attempts (default: 5)
        BYAPI_LOG_LEVEL (optional): Logging level (default: INFO)
    """

    def __init__(self, config_instance: Optional[ByapiConfig] = None):
        """
        Initialize Byapi client.

        Initializes the client with configuration from environment variables (.env file).
        Creates instances of all data access categories.

        Args:
            config_instance (ByapiConfig, optional): Custom configuration instance.
                                                    If None, loads from .env file.
                                                    Default: None (use global config).

        Raises:
            ValueError: If BYAPI_LICENCE environment variable is missing.
            EnvironmentError: If .env file cannot be loaded.

        Example:
            >>> # Load config from .env (default)
            >>> client = ByapiClient()

            >>> # Use custom config
            >>> from byapi_config import ByapiConfig
            >>> config = ByapiConfig()
            >>> config.license_keys = ["key1", "key2"]
            >>> client = ByapiClient(config_instance=config)
        """
        self.config = config_instance or config
        self.handler = BaseApiHandler(self.config)

        # Initialize data categories
        self.stock_prices = StockPricesCategory(self.handler)
        self.indicators = IndicatorsCategory(self.handler)
        self.financials = FinancialsCategory(self.handler)
        self.announcements = AnnouncementsCategory(self.handler)
        self.company_info = CompanyInfoCategory(self.handler)

        logger.info(f"ByapiClient initialized (v{__version__}) with {len(self.config.license_keys)} key(s)")

    def get_license_health(self) -> List[Any]:
        """
        Get health status of all configured license keys.

        Returns information about each configured license key's health status,
        including failure counts and current status. Useful for monitoring
        API access and debugging authentication issues.

        Returns:
            List[LicenseKeyHealth]: List of health objects, one per license key.
                                   Each contains:
                                   - key: Masked license key (first 8 chars only)
                                   - consecutive_failures: Count of consecutive failures (0-5+)
                                   - total_failures: Total failures in session (0-10+)
                                   - status: "healthy", "faulty" (5 consecutive failures),
                                           or "invalid" (10 total failures)
                                   - last_failed_timestamp: When last failure occurred

        Example:
            >>> client = ByapiClient()
            >>> health = client.get_license_health()
            >>> for key_health in health:
            ...     print(f"Key {key_health.key}:")
            ...     print(f"  Status: {key_health.status}")
            ...     print(f"  Consecutive Failures: {key_health.consecutive_failures}")
            ...     print(f"  Total Failures: {key_health.total_failures}/10")
            Key 12345678...:
              Status: healthy
              Consecutive Failures: 0
              Total Failures: 0/10

            >>> # Check if any keys are marked invalid
            >>> invalid_keys = [kh for kh in health if kh.status == "invalid"]
            >>> if invalid_keys:
            ...     print(f"Warning: {len(invalid_keys)} license key(s) are disabled")
            ...     print("Consider refreshing your .env file or restarting the application")
        """
        return self.config.get_license_health()

    def __repr__(self) -> str:
        """Return string representation of client."""
        return f"<ByapiClient v{__version__} with {len(self.config.license_keys)} key(s)>"
