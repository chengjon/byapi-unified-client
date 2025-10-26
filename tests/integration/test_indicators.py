"""
Integration tests for IndicatorsCategory.

These tests validate technical indicator API endpoint responses and data parsing.
Tests can be run with: pytest tests/integration/test_indicators.py
"""

import pytest
from datetime import datetime, timedelta
from byapi_client_unified import ByapiClient
from byapi_models import TechnicalIndicator
from byapi_exceptions import DataError, NetworkError


class TestIndicatorsCategory:
    """Test suite for technical indicators category."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return ByapiClient()

    def test_get_indicators_returns_list(self, client):
        """Test that get_indicators returns a list of TechnicalIndicator objects."""
        indicators = client.indicators.get_indicators("000001")

        assert isinstance(indicators, list)
        if indicators:  # May be empty if no indicator data
            assert all(isinstance(ind, TechnicalIndicator) for ind in indicators)

    def test_get_indicators_with_dates(self, client):
        """Test fetching indicators with date range."""
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")

        indicators = client.indicators.get_indicators(
            "000001",
            start_date=start_date,
            end_date=end_date
        )

        assert isinstance(indicators, list)

    def test_indicator_structure(self, client):
        """Test that returned indicators have expected structure."""
        indicators = client.indicators.get_indicators("000001")

        if indicators:
            ind = indicators[0]

            # Check required fields
            assert hasattr(ind, "code")
            assert hasattr(ind, "timestamp")

            # Check optional indicator fields
            assert hasattr(ind, "ma_5")
            assert hasattr(ind, "ma_10")
            assert hasattr(ind, "ma_20")
            assert hasattr(ind, "rsi")
            assert hasattr(ind, "macd")
            assert hasattr(ind, "bollinger_upper")

    def test_rsi_validation(self, client):
        """Test that RSI values are within valid range (0-100)."""
        indicators = client.indicators.get_indicators("000001")

        for ind in indicators:
            if ind.rsi is not None:
                assert 0 <= ind.rsi <= 100, f"RSI value {ind.rsi} out of range"

    def test_moving_averages_positive(self, client):
        """Test that moving average values are non-negative."""
        indicators = client.indicators.get_indicators("000001")

        for ind in indicators:
            for ma_field in ["ma_5", "ma_10", "ma_20", "ma_50", "ma_200"]:
                value = getattr(ind, ma_field, None)
                if value is not None:
                    assert value >= 0, f"{ma_field} should be non-negative"

    def test_empty_indicator_result(self, client):
        """Test handling of empty indicator results."""
        # Use a very old date range
        indicators = client.indicators.get_indicators(
            "000001",
            start_date="1980-01-01",
            end_date="1980-01-31"
        )

        # Should return empty list, not error
        assert isinstance(indicators, list)

    def test_indicator_timestamp_format(self, client):
        """Test that indicator timestamps are datetime objects."""
        indicators = client.indicators.get_indicators("000001")

        if indicators:
            for ind in indicators:
                assert isinstance(ind.timestamp, datetime)


class TestIndicatorsCategoryFixtures:
    """Tests using pytest fixtures for mock indicator data."""

    def test_with_sample_technical_indicator(self, sample_technical_indicator):
        """Test that sample technical indicator fixture works."""
        indicator = sample_technical_indicator

        assert indicator.code == "000001"
        assert isinstance(indicator.timestamp, datetime)

        # RSI should be in valid range
        if indicator.rsi is not None:
            assert 0 <= indicator.rsi <= 100
