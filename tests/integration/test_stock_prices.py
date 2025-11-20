"""
Integration tests for StockPricesCategory.

These tests validate real API endpoint responses and data parsing.
Tests can be run with: pytest tests/integration/test_stock_prices.py
"""

import pytest
from datetime import datetime, timedelta
from byapi_client_unified import ByapiClient
from byapi_models import StockQuote
from byapi_exceptions import NotFoundError, DataError, NetworkError


class TestStockPricesCategory:
    """Test suite for stock prices category."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return ByapiClient()

    def test_get_latest_valid_stock(self, client):
        """Test fetching latest price for a valid stock code."""
        # Using a well-known stock code
        quote = client.stock_prices.get_latest("000001")

        # Validate response structure
        assert isinstance(quote, StockQuote)
        assert quote.code == "000001"
        assert quote.current_price > 0
        assert quote.daily_high >= quote.current_price
        assert quote.daily_low <= quote.current_price
        assert isinstance(quote.timestamp, datetime)

    def test_get_latest_returns_stock_quote(self, client):
        """Test that get_latest returns proper StockQuote dataclass."""
        quote = client.stock_prices.get_latest("000001")

        # Check all required fields
        assert hasattr(quote, "code")
        assert hasattr(quote, "name")
        assert hasattr(quote, "current_price")
        assert hasattr(quote, "daily_high")
        assert hasattr(quote, "daily_low")
        assert hasattr(quote, "volume")
        assert hasattr(quote, "change_percent")
        assert hasattr(quote, "timestamp")

    def test_get_latest_invalid_code_raises_not_found(self, client):
        """Test that invalid stock code raises NotFoundError."""
        with pytest.raises(NotFoundError):
            client.stock_prices.get_latest("999999")

    def test_get_historical_valid_range(self, client):
        """Test fetching historical prices for a valid date range."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        quotes = client.stock_prices.get_historical("000001", start_date, end_date)

        # Validate response
        assert isinstance(quotes, list)
        if quotes:  # May be empty if no data in range
            assert all(isinstance(q, StockQuote) for q in quotes)
            assert all(q.code == "000001" for q in quotes)

    def test_get_historical_returns_list(self, client):
        """Test that get_historical returns a list."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

        quotes = client.stock_prices.get_historical("000001", start_date, end_date)

        assert isinstance(quotes, list)

    def test_get_historical_empty_result(self, client):
        """Test that empty date range returns empty list, not error."""
        # Use a far future date range that won't have data
        start_date = "2100-01-01"
        end_date = "2100-01-31"

        quotes = client.stock_prices.get_historical("000001", start_date, end_date)

        assert isinstance(quotes, list)
        assert len(quotes) == 0

    def test_get_latest_price_validation(self, client):
        """Test that price values are properly validated."""
        quote = client.stock_prices.get_latest("000001")

        # Prices should be positive
        assert quote.current_price >= 0
        assert quote.daily_high >= 0
        assert quote.daily_low >= 0
        assert quote.previous_close >= 0

        # High should be >= low
        assert quote.daily_high >= quote.daily_low

    def test_get_latest_volume_validation(self, client):
        """Test that volume is a valid integer."""
        quote = client.stock_prices.get_latest("000001")

        assert isinstance(quote.volume, int)
        assert quote.volume >= 0

    def test_stock_quote_dataclass_validation(self, client):
        """Test that StockQuote enforces data validation."""
        quote = client.stock_prices.get_latest("000001")

        # Dataclass post_init validation should prevent negative prices/volumes
        # If these assertions fail, dataclass validation is working
        with pytest.raises(ValueError):
            StockQuote(
                code="000001",
                name="Test",
                current_price=-1.0,  # This should raise ValueError
                previous_close=10.0,
                daily_open=10.0,
                daily_high=11.0,
                daily_low=9.0,
                volume=1000,
                turnover=10000.0,
                change=0.5,
                change_percent=0.05,
                timestamp=datetime.now(),
            )


class TestStockPricesCategoryFixtures:
    """Tests using pytest fixtures for mock data."""

    def test_with_sample_stock_quote(self, sample_stock_quote):
        """Test that sample fixture works correctly."""
        quote = sample_stock_quote

        assert quote.code == "000001"
        assert quote.current_price > 0
        assert quote.daily_high >= quote.daily_low
