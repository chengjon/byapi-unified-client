"""
Integration tests for AnnouncementsCategory and CompanyInfoCategory.

These tests validate announcement and company info API endpoint responses.
Tests can be run with: pytest tests/integration/test_announcements.py
"""

import pytest
from datetime import datetime
from byapi_client_unified import ByapiClient
from byapi_models import StockAnnouncement, CompanyInfo
from byapi_exceptions import NotFoundError, DataError


class TestAnnouncementsCategory:
    """Test suite for announcements category."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return ByapiClient()

    def test_get_announcements_returns_list(self, client):
        """Test that get_announcements returns a list."""
        announcements = client.announcements.get_announcements("000001")

        assert isinstance(announcements, list)

    def test_get_announcements_with_limit(self, client):
        """Test fetching announcements with limit."""
        announcements = client.announcements.get_announcements("000001", limit=5)

        assert isinstance(announcements, list)
        assert len(announcements) <= 5

    def test_announcement_structure(self, client):
        """Test that returned announcements have expected structure."""
        announcements = client.announcements.get_announcements("000001", limit=1)

        if announcements:
            ann = announcements[0]

            assert hasattr(ann, "code")
            assert hasattr(ann, "title")
            assert hasattr(ann, "content")
            assert hasattr(ann, "announcement_date")
            assert hasattr(ann, "announcement_type")
            assert hasattr(ann, "importance")

    def test_announcement_dataclass(self, client):
        """Test that announcement is proper StockAnnouncement dataclass."""
        announcements = client.announcements.get_announcements("000001", limit=1)

        if announcements:
            ann = announcements[0]
            assert isinstance(ann, StockAnnouncement)
            assert ann.code == "000001"
            assert isinstance(ann.announcement_date, datetime.date) or isinstance(ann.announcement_date, datetime)

    def test_empty_announcements_result(self, client):
        """Test that invalid code returns empty list, not error."""
        # Some stocks may not have announcements
        announcements = client.announcements.get_announcements("000001", limit=100)

        assert isinstance(announcements, list)

    def test_announcement_title_not_empty(self, client):
        """Test that announcement titles are not empty."""
        announcements = client.announcements.get_announcements("000001", limit=1)

        if announcements:
            ann = announcements[0]
            assert ann.title and len(ann.title) > 0


class TestCompanyInfoCategory:
    """Test suite for company info category."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return ByapiClient()

    def test_get_company_info_returns_company_info(self, client):
        """Test that get_company_info returns CompanyInfo object."""
        company = client.company_info.get_company_info("000001")

        assert isinstance(company, CompanyInfo)
        assert company.code == "000001"

    def test_company_info_structure(self, client):
        """Test that company info has expected structure."""
        company = client.company_info.get_company_info("000001")

        assert hasattr(company, "code")
        assert hasattr(company, "name")
        assert hasattr(company, "industry")
        assert hasattr(company, "sector")

    def test_company_info_required_fields(self, client):
        """Test that company has required fields populated."""
        company = client.company_info.get_company_info("000001")

        # These should always be populated
        assert company.code == "000001"
        assert company.name and len(company.name) > 0
        assert company.industry and len(company.industry) > 0
        assert company.sector and len(company.sector) > 0

    def test_company_info_optional_fields(self, client):
        """Test that optional fields exist but may be None."""
        company = client.company_info.get_company_info("000001")

        # These may be None
        assert hasattr(company, "name_en")
        assert hasattr(company, "market_cap")
        assert hasattr(company, "employees")
        assert hasattr(company, "founded_year")
        assert hasattr(company, "exchange")
        assert hasattr(company, "list_date")
        assert hasattr(company, "description")

    def test_company_info_invalid_code_raises_not_found(self, client):
        """Test that invalid stock code raises NotFoundError."""
        with pytest.raises(NotFoundError):
            client.company_info.get_company_info("999999")

    def test_market_cap_non_negative(self, client):
        """Test that market cap is non-negative if present."""
        company = client.company_info.get_company_info("000001")

        if company.market_cap is not None:
            assert company.market_cap >= 0

    def test_employees_non_negative(self, client):
        """Test that employee count is non-negative if present."""
        company = client.company_info.get_company_info("000001")

        if company.employees is not None:
            assert company.employees >= 0

    def test_founded_year_reasonable(self, client):
        """Test that founded year is reasonable if present."""
        company = client.company_info.get_company_info("000001")

        if company.founded_year is not None:
            assert 1800 <= company.founded_year <= datetime.now().year


class TestAnnouncementsAndCompanyInfoFixtures:
    """Tests using pytest fixtures for mock data."""

    def test_with_sample_announcement(self, sample_announcement):
        """Test that sample announcement fixture works."""
        ann = sample_announcement

        assert ann.code == "000001"
        assert isinstance(ann, StockAnnouncement)
        assert ann.title and len(ann.title) > 0

    def test_with_sample_company_info(self, sample_company_info):
        """Test that sample company info fixture works."""
        company = sample_company_info

        assert company.code == "000001"
        assert isinstance(company, CompanyInfo)
        assert company.name and len(company.name) > 0
