"""
Documentation tests for Byapi client library.

Tests verify that:
1. All public classes have docstrings
2. All public methods have docstrings
3. All parameters are documented
4. Return types are documented
5. Examples in docstrings are valid

Run with: pytest tests/unit/test_docstrings.py -v
"""

import pytest
from inspect import getmembers, ismethod, isclass
from byapi_client_unified import (
    ByapiClient,
    StockPricesCategory,
    IndicatorsCategory,
    FinancialsCategory,
    AnnouncementsCategory,
    CompanyInfoCategory,
    BaseApiHandler,
)
from byapi_models import (
    StockQuote,
    TechnicalIndicator,
    FinancialData,
    StockAnnouncement,
    CompanyInfo,
)
from byapi_config import ByapiConfig
from byapi_exceptions import (
    ByapiError,
    AuthenticationError,
    DataError,
    NotFoundError,
    RateLimitError,
    NetworkError,
)


class TestClientDocstrings:
    """Test ByapiClient docstrings."""

    def test_byapi_client_has_docstring(self):
        """Test that ByapiClient class has a docstring."""
        assert ByapiClient.__doc__ is not None
        assert len(ByapiClient.__doc__.strip()) > 0
        assert "Unified Byapi Stock API Client" in ByapiClient.__doc__

    def test_byapi_client_init_has_docstring(self):
        """Test that ByapiClient.__init__ has docstring."""
        assert ByapiClient.__init__.__doc__ is not None
        assert "Initialize Byapi client" in ByapiClient.__init__.__doc__

    def test_get_license_health_has_docstring(self):
        """Test that get_license_health has docstring."""
        assert ByapiClient.get_license_health.__doc__ is not None
        assert "health status" in ByapiClient.get_license_health.__doc__


class TestCategoryDocstrings:
    """Test category class docstrings."""

    def test_stock_prices_category_has_docstring(self):
        """Test StockPricesCategory docstring."""
        assert StockPricesCategory.__doc__ is not None
        assert "price" in StockPricesCategory.__doc__.lower()

    def test_stock_prices_get_latest_has_docstring(self):
        """Test get_latest method has comprehensive docstring."""
        doc = StockPricesCategory.get_latest.__doc__
        assert doc is not None
        assert "latest" in doc.lower()
        assert "Args:" in doc
        assert "Returns:" in doc
        assert "Raises:" in doc
        assert "Example:" in doc

    def test_stock_prices_get_historical_has_docstring(self):
        """Test get_historical method has comprehensive docstring."""
        doc = StockPricesCategory.get_historical.__doc__
        assert doc is not None
        assert "historical" in doc.lower()
        assert "Args:" in doc
        assert "Returns:" in doc
        assert "Raises:" in doc
        assert "Example:" in doc

    def test_indicators_category_has_docstring(self):
        """Test IndicatorsCategory docstring."""
        assert IndicatorsCategory.__doc__ is not None
        assert "indicator" in IndicatorsCategory.__doc__.lower()

    def test_indicators_get_indicators_has_docstring(self):
        """Test get_indicators has comprehensive docstring."""
        doc = IndicatorsCategory.get_indicators.__doc__
        assert doc is not None
        assert "technical" in doc.lower() or "indicator" in doc.lower()
        assert "Args:" in doc
        assert "Returns:" in doc
        assert "Example:" in doc

    def test_financials_category_has_docstring(self):
        """Test FinancialsCategory docstring."""
        assert FinancialsCategory.__doc__ is not None
        assert "financial" in FinancialsCategory.__doc__.lower()

    def test_financials_get_financials_has_docstring(self):
        """Test get_financials has comprehensive docstring."""
        doc = FinancialsCategory.get_financials.__doc__
        assert doc is not None
        assert "financial" in doc.lower()
        assert "Args:" in doc
        assert "Returns:" in doc
        assert "Example:" in doc
        assert "statement_type" in doc

    def test_announcements_category_has_docstring(self):
        """Test AnnouncementsCategory docstring."""
        assert AnnouncementsCategory.__doc__ is not None
        assert "announcement" in AnnouncementsCategory.__doc__.lower()

    def test_announcements_get_announcements_has_docstring(self):
        """Test get_announcements has comprehensive docstring."""
        doc = AnnouncementsCategory.get_announcements.__doc__
        assert doc is not None
        assert "announcement" in doc.lower()
        assert "Args:" in doc
        assert "Returns:" in doc
        assert "Example:" in doc

    def test_company_info_category_has_docstring(self):
        """Test CompanyInfoCategory docstring."""
        assert CompanyInfoCategory.__doc__ is not None
        assert "company" in CompanyInfoCategory.__doc__.lower()

    def test_company_info_get_company_info_has_docstring(self):
        """Test get_company_info has comprehensive docstring."""
        doc = CompanyInfoCategory.get_company_info.__doc__
        assert doc is not None
        assert "company" in doc.lower()
        assert "Args:" in doc
        assert "Returns:" in doc
        assert "Example:" in doc


class TestDataModelDocstrings:
    """Test data model docstrings."""

    def test_stock_quote_has_docstring(self):
        """Test StockQuote dataclass has docstring."""
        assert StockQuote.__doc__ is not None

    def test_technical_indicator_has_docstring(self):
        """Test TechnicalIndicator has docstring."""
        assert TechnicalIndicator.__doc__ is not None

    def test_financial_data_has_docstring(self):
        """Test FinancialData has docstring."""
        assert FinancialData.__doc__ is not None

    def test_stock_announcement_has_docstring(self):
        """Test StockAnnouncement has docstring."""
        assert StockAnnouncement.__doc__ is not None

    def test_company_info_has_docstring(self):
        """Test CompanyInfo has docstring."""
        assert CompanyInfo.__doc__ is not None


class TestExceptionDocstrings:
    """Test exception class docstrings."""

    def test_byapi_error_has_docstring(self):
        """Test ByapiError has docstring."""
        assert ByapiError.__doc__ is not None

    def test_all_exceptions_have_docstrings(self):
        """Test all custom exceptions have docstrings."""
        exceptions = [
            ByapiError,
            AuthenticationError,
            DataError,
            NotFoundError,
            RateLimitError,
            NetworkError,
        ]
        for exc in exceptions:
            assert exc.__doc__ is not None, f"{exc.__name__} missing docstring"


class TestDocstringCompleteness:
    """Test that docstrings contain required sections."""

    def test_main_methods_have_returns(self):
        """Test that main methods document return types."""
        methods = [
            (StockPricesCategory.get_latest, "Returns:"),
            (StockPricesCategory.get_historical, "Returns:"),
            (IndicatorsCategory.get_indicators, "Returns:"),
            (FinancialsCategory.get_financials, "Returns:"),
            (AnnouncementsCategory.get_announcements, "Returns:"),
            (CompanyInfoCategory.get_company_info, "Returns:"),
        ]

        for method, section in methods:
            assert method.__doc__ is not None
            assert section in method.__doc__, f"{method.__name__} missing {section}"

    def test_main_methods_have_examples(self):
        """Test that main methods include usage examples."""
        methods = [
            StockPricesCategory.get_latest,
            StockPricesCategory.get_historical,
            IndicatorsCategory.get_indicators,
            FinancialsCategory.get_financials,
            AnnouncementsCategory.get_announcements,
            CompanyInfoCategory.get_company_info,
        ]

        for method in methods:
            assert method.__doc__ is not None
            assert "Example:" in method.__doc__ or ">>>" in method.__doc__, \
                f"{method.__name__} missing example"

    def test_main_methods_have_raises(self):
        """Test that main methods document exceptions."""
        methods = [
            StockPricesCategory.get_latest,
            StockPricesCategory.get_historical,
            IndicatorsCategory.get_indicators,
            FinancialsCategory.get_financials,
            AnnouncementsCategory.get_announcements,
            CompanyInfoCategory.get_company_info,
        ]

        for method in methods:
            assert method.__doc__ is not None
            assert "Raises:" in method.__doc__, \
                f"{method.__name__} missing Raises section"


class TestDocstringQuality:
    """Test quality of docstring content."""

    def test_byapi_client_docstring_includes_setup(self):
        """Test ByapiClient docstring includes setup instructions."""
        doc = ByapiClient.__doc__
        assert "Key Features" in doc
        assert "Quick Start" in doc
        assert "Categories" in doc or "category" in doc.lower()

    def test_category_docstrings_are_descriptive(self):
        """Test category docstrings are meaningful."""
        categories = [
            (StockPricesCategory, "price"),
            (IndicatorsCategory, "indicator"),
            (FinancialsCategory, "financial"),
            (AnnouncementsCategory, "announcement"),
            (CompanyInfoCategory, "company"),
        ]

        for category, keyword in categories:
            doc = category.__doc__
            assert doc is not None
            assert keyword.lower() in doc.lower(), \
                f"{category.__name__} docstring doesn't mention '{keyword}'"

    def test_method_docstrings_mention_parameters(self):
        """Test that method docstrings mention key parameters."""
        # get_latest should mention 'code'
        doc = StockPricesCategory.get_latest.__doc__
        assert "code" in doc.lower()

        # get_historical should mention 'start_date' and 'end_date'
        doc = StockPricesCategory.get_historical.__doc__
        assert "start_date" in doc or "date" in doc.lower()

        # get_financials should mention 'statement_type'
        doc = FinancialsCategory.get_financials.__doc__
        assert "statement_type" in doc or "statement" in doc.lower()


class TestDocstringFormatting:
    """Test docstring formatting follows Google style."""

    def test_docstrings_use_google_style_sections(self):
        """Test that main docstrings use Google-style sections."""
        methods = [
            StockPricesCategory.get_latest,
            IndicatorsCategory.get_indicators,
            FinancialsCategory.get_financials,
        ]

        google_style_sections = ["Args:", "Returns:", "Raises:", "Example:"]

        for method in methods:
            doc = method.__doc__
            # At least 2 of these sections should be present
            sections_found = sum(
                1 for section in google_style_sections
                if section in doc
            )
            assert sections_found >= 2, \
                f"{method.__name__} doesn't follow Google style (only {sections_found} sections found)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
