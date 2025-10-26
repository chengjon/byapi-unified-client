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
    """Category for stock price-related operations."""

    def __init__(self, handler: BaseApiHandler):
        """
        Initialize stock prices category.

        Args:
            handler: BaseApiHandler instance for API calls
        """
        self.handler = handler

    def get_latest(self, code: str) -> StockQuote:
        """
        Get latest stock price for a single stock.

        Args:
            code: Stock code (6-digit format, e.g., "000001")

        Returns:
            StockQuote with latest price data

        Raises:
            NotFoundError: If stock code is invalid
            AuthenticationError: If authentication fails
            NetworkError: If network call fails
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

        Args:
            code: Stock code
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)

        Returns:
            List of StockQuote objects for the date range

        Raises:
            NotFoundError: If stock code is invalid
            AuthenticationError: If authentication fails
            NetworkError: If network call fails
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
    """Category for technical indicators."""

    def __init__(self, handler: BaseApiHandler):
        """Initialize indicators category."""
        self.handler = handler

    def get_indicators(self, code: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[TechnicalIndicator]:
        """
        Get technical indicators for a stock.

        Args:
            code: Stock code
            start_date: Optional start date (YYYY-MM-DD format)
            end_date: Optional end date (YYYY-MM-DD format)

        Returns:
            List of TechnicalIndicator objects

        Raises:
            NotFoundError: If stock code is invalid
            DataError: If response parsing fails
            NetworkError: If API call fails
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
    """Category for financial statements."""

    def __init__(self, handler: BaseApiHandler):
        """Initialize financials category."""
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

        Args:
            code: Stock code
            statement_type: Type of statement: 'balance_sheet', 'income_statement', 'cash_flow', or 'all'
            start_date: Optional start date
            end_date: Optional end date

        Returns:
            FinancialData object with requested statements

        Raises:
            DataError: If response parsing fails
            NetworkError: If API call fails
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
    """Category for company announcements and news."""

    def __init__(self, handler: BaseApiHandler):
        """Initialize announcements category."""
        self.handler = handler

    def get_announcements(self, code: str, limit: int = 10) -> List[StockAnnouncement]:
        """
        Get recent company announcements for a stock.

        Args:
            code: Stock code
            limit: Maximum number of announcements to return (default: 10)

        Returns:
            List of StockAnnouncement objects

        Raises:
            DataError: If response parsing fails
            NetworkError: If API call fails
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
    """Category for company information and classification."""

    def __init__(self, handler: BaseApiHandler):
        """Initialize company info category."""
        self.handler = handler

    def get_company_info(self, code: str) -> CompanyInfo:
        """
        Get company information for a stock.

        Args:
            code: Stock code

        Returns:
            CompanyInfo object with company details

        Raises:
            NotFoundError: If company not found
            DataError: If response parsing fails
            NetworkError: If API call fails
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
    Main unified API client for accessing Byapi stock data.

    Provides category-based access to all stock market data:
    - stock_prices: Real-time and historical price data
    - indicators: Technical indicators and analysis
    - financials: Financial statements
    - announcements: Company news and announcements
    - company_info: Company profile information
    - indices: Market indices

    Example:
        client = ByapiClient()
        quote = client.stock_prices.get_latest("000001")
        print(f"Price: ¥{quote.current_price}")
    """

    def __init__(self, config_instance: Optional[ByapiConfig] = None):
        """
        Initialize Byapi client.

        Args:
            config_instance: Optional ByapiConfig instance (uses global if not provided)

        Raises:
            ValueError: If configuration is invalid or missing
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

    def get_license_health(self):
        """
        Get health status of all configured license keys.

        Returns:
            List of LicenseKeyHealth objects showing status of each key

        Example:
            health = client.get_license_health()
            for key_health in health:
                print(f"Key status: {key_health.status}")
                print(f"Failures: {key_health.total_failures}/10")
        """
        return self.config.get_license_health()

    def __repr__(self) -> str:
        """Return string representation of client."""
        return f"<ByapiClient v{__version__} with {len(self.config.license_keys)} key(s)>"
