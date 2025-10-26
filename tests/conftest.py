"""
Pytest configuration and shared fixtures for Byapi tests.

This module provides:
- Shared test fixtures
- Configuration for test environment
- Mock/stub data for testing
"""

import os
import pytest
from datetime import datetime, date


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment before running tests."""
    # Set test environment variable to disable real API calls if needed
    os.environ["BYAPI_LOG_LEVEL"] = "WARNING"  # Reduce noise in test output
    yield
    # Cleanup after tests if needed


@pytest.fixture
def sample_stock_quote():
    """Fixture providing sample stock quote data."""
    return {
        "code": "000001",
        "name": "平安银行",
        "current_price": 15.23,
        "previous_close": 15.10,
        "daily_open": 15.15,
        "daily_high": 15.30,
        "daily_low": 15.05,
        "volume": 100000000,
        "turnover": 1500000000,
        "change": 0.13,
        "change_percent": 0.86,
        "timestamp": datetime.now().isoformat(),
        "bid_price": 15.22,
        "ask_price": 15.24,
    }


@pytest.fixture
def sample_technical_indicator():
    """Fixture providing sample technical indicator data."""
    return {
        "code": "000001",
        "timestamp": datetime.now().isoformat(),
        "ma_5": 15.25,
        "ma_10": 15.20,
        "ma_20": 15.15,
        "ma_50": 15.10,
        "ma_200": 15.05,
        "rsi": 65.5,
        "macd": 0.15,
        "macd_signal": 0.12,
        "macd_histogram": 0.03,
        "bollinger_upper": 15.40,
        "bollinger_middle": 15.20,
        "bollinger_lower": 15.00,
        "atr": 0.25,
    }


@pytest.fixture
def sample_financial_data():
    """Fixture providing sample financial statement data."""
    return {
        "code": "000001",
        "balance_sheet": {
            "timestamp": date.today().isoformat(),
            "total_assets": 1500000,
            "total_liabilities": 1000000,
            "total_equity": 500000,
            "current_assets": 800000,
            "current_liabilities": 400000,
        },
        "income_statement": {
            "timestamp": date.today().isoformat(),
            "revenue": 200000,
            "operating_expenses": 100000,
            "operating_income": 100000,
            "net_income": 80000,
            "eps": 0.8,
        },
        "cash_flow": {
            "timestamp": date.today().isoformat(),
            "operating_cash_flow": 90000,
            "investing_cash_flow": -30000,
            "financing_cash_flow": -20000,
            "net_cash_change": 40000,
        },
    }


@pytest.fixture
def sample_announcement():
    """Fixture providing sample company announcement data."""
    return {
        "code": "000001",
        "title": "关于发布2025年年度报告的公告",
        "content": "公司已完成2025年年度报告，详见附件。",
        "announcement_date": date.today().isoformat(),
        "announcement_type": "financial_report",
        "importance": "high",
        "source": "CNINFO",
    }


@pytest.fixture
def sample_company_info():
    """Fixture providing sample company information."""
    return {
        "code": "000001",
        "name": "平安银行",
        "name_en": "Ping An Bank",
        "industry": "金融和保险业",
        "sector": "金融",
        "market_cap": 150000000000,
        "employees": 50000,
        "founded_year": 1991,
        "exchange": "SZA",
        "list_date": "1991-04-03",
        "description": "平安银行股份有限公司是中国领先的上市银行之一。",
    }


@pytest.fixture
def sample_market_index():
    """Fixture providing sample market index data."""
    return {
        "code": "000001",
        "name": "上证指数",
        "current_value": 3500.00,
        "previous_value": 3480.50,
        "change": 19.50,
        "change_percent": 0.56,
        "timestamp": datetime.now().isoformat(),
        "constituent_count": 1691,
    }


@pytest.fixture
def mock_requests_module(monkeypatch):
    """
    Fixture providing a mock requests module for API testing.

    Usage:
        def test_api_call(mock_requests_module):
            mock_requests_module.get.return_value.json.return_value = {...}
    """
    from unittest.mock import MagicMock

    mock = MagicMock()
    monkeypatch.setattr("requests.get", mock.get)
    monkeypatch.setattr("requests.post", mock.post)
    return mock
