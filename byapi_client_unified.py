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
        # TODO: Implement once API endpoints are known
        raise NotImplementedError("Waiting for API endpoint mapping")

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
        # TODO: Implement once API endpoints are known
        raise NotImplementedError("Waiting for API endpoint mapping")


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

        logger.info(f"ByapiClient initialized (v{__version__})")

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
