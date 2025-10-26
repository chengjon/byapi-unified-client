"""
Integration tests for FinancialsCategory.

These tests validate financial statement API endpoint responses and data parsing.
Tests can be run with: pytest tests/integration/test_financials.py
"""

import pytest
from datetime import datetime
from byapi_client_unified import ByapiClient
from byapi_models import FinancialData, BalanceSheet, IncomeStatement, CashFlowStatement
from byapi_exceptions import DataError, NetworkError


class TestFinancialsCategory:
    """Test suite for financial statements category."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return ByapiClient()

    def test_get_financials_returns_financial_data(self, client):
        """Test that get_financials returns FinancialData object."""
        financials = client.financials.get_financials("000001")

        assert isinstance(financials, FinancialData)
        assert financials.code == "000001"

    def test_get_financials_all_statements(self, client):
        """Test fetching all financial statements."""
        financials = client.financials.get_financials("000001", statement_type="all")

        assert isinstance(financials, FinancialData)
        # May have any combination of these statements
        assert hasattr(financials, "balance_sheet")
        assert hasattr(financials, "income_statement")
        assert hasattr(financials, "cash_flow")

    def test_get_financials_balance_sheet(self, client):
        """Test fetching balance sheet."""
        financials = client.financials.get_financials("000001", statement_type="balance_sheet")

        assert isinstance(financials, FinancialData)
        if financials.balance_sheet:
            assert isinstance(financials.balance_sheet, BalanceSheet)

    def test_get_financials_income_statement(self, client):
        """Test fetching income statement."""
        financials = client.financials.get_financials("000001", statement_type="income_statement")

        assert isinstance(financials, FinancialData)
        if financials.income_statement:
            assert isinstance(financials.income_statement, IncomeStatement)

    def test_get_financials_cash_flow(self, client):
        """Test fetching cash flow statement."""
        financials = client.financials.get_financials("000001", statement_type="cash_flow")

        assert isinstance(financials, FinancialData)
        if financials.cash_flow:
            assert isinstance(financials.cash_flow, CashFlowStatement)

    def test_balance_sheet_structure(self, client):
        """Test balance sheet has valid structure."""
        financials = client.financials.get_financials("000001", statement_type="balance_sheet")

        if financials.balance_sheet:
            bs = financials.balance_sheet

            # Check required fields
            assert hasattr(bs, "timestamp")
            assert hasattr(bs, "total_assets")
            assert hasattr(bs, "total_liabilities")
            assert hasattr(bs, "total_equity")
            assert hasattr(bs, "current_assets")
            assert hasattr(bs, "current_liabilities")

    def test_balance_sheet_validation(self, client):
        """Test balance sheet financial equations."""
        financials = client.financials.get_financials("000001", statement_type="balance_sheet")

        if financials.balance_sheet:
            bs = financials.balance_sheet

            # Assets should be roughly equal to liabilities + equity
            # (May have rounding differences)
            expected_total = bs.total_liabilities + bs.total_equity
            # Allow 5% tolerance for rounding
            assert abs(bs.total_assets - expected_total) <= (expected_total * 0.05)

    def test_income_statement_structure(self, client):
        """Test income statement has valid structure."""
        financials = client.financials.get_financials("000001", statement_type="income_statement")

        if financials.income_statement:
            inc = financials.income_statement

            assert hasattr(inc, "timestamp")
            assert hasattr(inc, "revenue")
            assert hasattr(inc, "operating_income")
            assert hasattr(inc, "net_income")
            assert hasattr(inc, "eps")

    def test_income_statement_validation(self, client):
        """Test income statement values are logically consistent."""
        financials = client.financials.get_financials("000001", statement_type="income_statement")

        if financials.income_statement:
            inc = financials.income_statement

            # Operating income should be less than revenue
            assert inc.operating_income <= inc.revenue
            # Net income should be positive for healthy companies (if available)
            if inc.net_income:
                assert inc.net_income >= -1  # Allow small negative values

    def test_cash_flow_structure(self, client):
        """Test cash flow statement has valid structure."""
        financials = client.financials.get_financials("000001", statement_type="cash_flow")

        if financials.cash_flow:
            cf = financials.cash_flow

            assert hasattr(cf, "timestamp")
            assert hasattr(cf, "operating_cash_flow")
            assert hasattr(cf, "investing_cash_flow")
            assert hasattr(cf, "financing_cash_flow")
            assert hasattr(cf, "net_cash_change")

    def test_cash_flow_validation(self, client):
        """Test cash flow equation."""
        financials = client.financials.get_financials("000001", statement_type="cash_flow")

        if financials.cash_flow:
            cf = financials.cash_flow

            # Net cash change should equal sum of three cash flows
            expected_net = (
                cf.operating_cash_flow +
                cf.investing_cash_flow +
                cf.financing_cash_flow
            )

            # Allow for rounding differences
            assert abs(cf.net_cash_change - expected_net) <= abs(expected_net * 0.05)

    def test_financial_values_numeric(self, client):
        """Test that all financial values are numeric."""
        financials = client.financials.get_financials("000001", statement_type="all")

        if financials.balance_sheet:
            bs = financials.balance_sheet
            assert isinstance(bs.total_assets, (int, float))
            assert isinstance(bs.total_liabilities, (int, float))

        if financials.income_statement:
            inc = financials.income_statement
            assert isinstance(inc.revenue, (int, float))
            assert isinstance(inc.net_income, (int, float))

        if financials.cash_flow:
            cf = financials.cash_flow
            assert isinstance(cf.operating_cash_flow, (int, float))


class TestFinancialsCategoryFixtures:
    """Tests using pytest fixtures for mock financial data."""

    def test_with_sample_financial_data(self, sample_financial_data):
        """Test that sample financial data fixture works."""
        fd = sample_financial_data

        assert fd.code == "000001"
        assert isinstance(fd, FinancialData)
