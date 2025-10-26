#!/usr/bin/env python
"""
Basic usage example for the Unified Byapi Stock API Client.

This example demonstrates common operations with the Byapi client library.
It shows how to:
1. Initialize the client
2. Fetch stock prices (latest and historical)
3. Get technical indicators
4. Access financial statements
5. Retrieve announcements and company information
6. Handle errors gracefully

Requirements:
- Python 3.8+
- requests library
- python-dotenv library
- BYAPI_LICENCE environment variable set in .env file

Example .env file:
    BYAPI_LICENCE=your_api_key_here
"""

import logging
from datetime import datetime, timedelta
from byapi_client_unified import ByapiClient
from byapi_exceptions import (
    ByapiError,
    AuthenticationError,
    DataError,
    NotFoundError,
    NetworkError,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_1_latest_stock_price():
    """Example 1: Fetch the latest stock price."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Fetch Latest Stock Price")
    print("="*60)

    try:
        # Initialize client (loads BYAPI_LICENCE from .env)
        client = ByapiClient()
        print(f"✓ Client initialized: {client}")

        # Get latest price for stock 000001 (China Shenhua Energy)
        stock_code = "000001"
        quote = client.stock_prices.get_latest(stock_code)

        # Display results
        print(f"\nStock: {quote.name} ({quote.code})")
        print(f"Current Price: ¥{quote.current_price:.2f}")
        print(f"Daily High: ¥{quote.daily_high:.2f}")
        print(f"Daily Low: ¥{quote.daily_low:.2f}")
        print(f"Change: {quote.change:+.2f} ({quote.change_percent:+.2f}%)")
        print(f"Volume: {quote.volume:,} shares")
        print(f"Timestamp: {quote.timestamp}")

    except NotFoundError as e:
        print(f"✗ Stock not found: {e}")
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
        print("  Make sure BYAPI_LICENCE is set in .env file")
    except NetworkError as e:
        print(f"✗ Network error: {e}")
    except ByapiError as e:
        print(f"✗ API error: {e}")


def example_2_historical_prices():
    """Example 2: Fetch historical stock prices."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Fetch Historical Stock Prices")
    print("="*60)

    try:
        client = ByapiClient()

        # Get historical prices for the last 5 trading days
        stock_code = "000001"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        print(f"\nFetching historical prices from {start_date} to {end_date}...")

        quotes = client.stock_prices.get_historical(
            stock_code,
            start_date=start_date,
            end_date=end_date
        )

        if quotes:
            print(f"Found {len(quotes)} trading records:\n")
            print(f"{'Date':<12} {'Close':<10} {'High':<10} {'Low':<10} {'Volume':>12}")
            print("-" * 55)

            for quote in quotes:
                date_str = quote.timestamp.strftime("%Y-%m-%d")
                print(
                    f"{date_str:<12} "
                    f"¥{quote.current_price:<9.2f} "
                    f"¥{quote.daily_high:<9.2f} "
                    f"¥{quote.daily_low:<9.2f} "
                    f"{quote.volume:>12,}"
                )
        else:
            print("No data available for the requested date range")

    except ByapiError as e:
        print(f"✗ Error: {e}")


def example_3_technical_indicators():
    """Example 3: Fetch technical indicators."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Fetch Technical Indicators")
    print("="*60)

    try:
        client = ByapiClient()

        stock_code = "000001"
        print(f"\nFetching technical indicators for {stock_code}...")

        indicators = client.indicators.get_indicators(stock_code)

        if indicators:
            latest = indicators[-1]  # Most recent
            print(f"\nLatest Indicators (as of {latest.timestamp}):")
            print(f"  Moving Averages:")
            print(f"    MA-5:   {latest.ma_5:.2f}" if latest.ma_5 else "    MA-5:   N/A")
            print(f"    MA-10:  {latest.ma_10:.2f}" if latest.ma_10 else "    MA-10:  N/A")
            print(f"    MA-20:  {latest.ma_20:.2f}" if latest.ma_20 else "    MA-20:  N/A")
            print(f"    MA-50:  {latest.ma_50:.2f}" if latest.ma_50 else "    MA-50:  N/A")

            print(f"  Momentum:")
            print(f"    RSI:    {latest.rsi:.2f}" if latest.rsi else "    RSI:    N/A")
            print(f"    MACD:   {latest.macd:.4f}" if latest.macd else "    MACD:   N/A")

            if latest.bollinger_upper and latest.bollinger_lower:
                print(f"  Volatility (Bollinger Bands):")
                print(f"    Upper:  {latest.bollinger_upper:.2f}")
                print(f"    Middle: {latest.bollinger_middle:.2f}")
                print(f"    Lower:  {latest.bollinger_lower:.2f}")
        else:
            print("No technical indicator data available")

    except ByapiError as e:
        print(f"✗ Error: {e}")


def example_4_financial_statements():
    """Example 4: Fetch financial statements."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Fetch Financial Statements")
    print("="*60)

    try:
        client = ByapiClient()

        stock_code = "000001"
        print(f"\nFetching financial statements for {stock_code}...")

        financials = client.financials.get_financials(stock_code, statement_type="all")

        print(f"\nFinancial Data for {stock_code}:")

        if financials.balance_sheet:
            bs = financials.balance_sheet
            print(f"\n  Balance Sheet (as of {bs.timestamp}):")
            print(f"    Total Assets:       ¥{bs.total_assets:,.0f}")
            print(f"    Total Liabilities:  ¥{bs.total_liabilities:,.0f}")
            print(f"    Total Equity:       ¥{bs.total_equity:,.0f}")

        if financials.income_statement:
            inc = financials.income_statement
            print(f"\n  Income Statement (as of {inc.timestamp}):")
            print(f"    Revenue:            ¥{inc.revenue:,.0f}")
            print(f"    Operating Income:   ¥{inc.operating_income:,.0f}")
            print(f"    Net Income:         ¥{inc.net_income:,.0f}")
            print(f"    EPS:                ¥{inc.eps:.2f}")

        if financials.cash_flow:
            cf = financials.cash_flow
            print(f"\n  Cash Flow Statement (as of {cf.timestamp}):")
            print(f"    Operating CF:       ¥{cf.operating_cash_flow:,.0f}")
            print(f"    Investing CF:       ¥{cf.investing_cash_flow:,.0f}")
            print(f"    Financing CF:       ¥{cf.financing_cash_flow:,.0f}")

    except ByapiError as e:
        print(f"✗ Error: {e}")


def example_5_announcements():
    """Example 5: Fetch company announcements."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Fetch Company Announcements")
    print("="*60)

    try:
        client = ByapiClient()

        stock_code = "000001"
        print(f"\nFetching announcements for {stock_code}...")

        announcements = client.announcements.get_announcements(stock_code, limit=5)

        if announcements:
            print(f"\nLatest {len(announcements)} Announcements:\n")
            for i, ann in enumerate(announcements, 1):
                print(f"{i}. {ann.title}")
                print(f"   Date: {ann.announcement_date}")
                print(f"   Type: {ann.announcement_type}")
                print(f"   Importance: {ann.importance}")
                print()
        else:
            print("No announcements available")

    except ByapiError as e:
        print(f"✗ Error: {e}")


def example_6_company_info():
    """Example 6: Fetch company information."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Fetch Company Information")
    print("="*60)

    try:
        client = ByapiClient()

        stock_code = "000001"
        print(f"\nFetching company info for {stock_code}...")

        company = client.company_info.get_company_info(stock_code)

        print(f"\nCompany Information:")
        print(f"  Name:        {company.name}")
        if company.name_en:
            print(f"  Name (EN):   {company.name_en}")
        print(f"  Industry:    {company.industry}")
        print(f"  Sector:      {company.sector}")
        if company.market_cap:
            print(f"  Market Cap:  ¥{company.market_cap:,.0f}")
        if company.employees:
            print(f"  Employees:   {company.employees:,}")
        if company.founded_year:
            print(f"  Founded:     {company.founded_year}")
        if company.exchange:
            print(f"  Exchange:    {company.exchange}")
        if company.list_date:
            print(f"  Listed:      {company.list_date}")

    except ByapiError as e:
        print(f"✗ Error: {e}")


def example_7_error_handling():
    """Example 7: Error handling and license key health."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Error Handling & License Key Health")
    print("="*60)

    try:
        client = ByapiClient()

        # Check license key health
        health = client.get_license_health()
        print(f"\nLicense Key Health ({len(health)} key(s)):")
        for i, key_health in enumerate(health, 1):
            print(f"  Key {i}:")
            print(f"    Status:                {key_health.status}")
            print(f"    Consecutive Failures:  {key_health.consecutive_failures}")
            print(f"    Total Failures:        {key_health.total_failures}")

        # Attempt to fetch data for an invalid stock
        print(f"\nAttempting to fetch data for invalid stock code...")
        try:
            client.stock_prices.get_latest("999999")
        except NotFoundError as e:
            print(f"  ✓ Caught NotFoundError: {e}")

    except ByapiError as e:
        print(f"✗ Error: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("Unified Byapi Stock API Client - Usage Examples")
    print("="*60)

    # Run all examples
    example_1_latest_stock_price()
    example_2_historical_prices()
    example_3_technical_indicators()
    example_4_financial_statements()
    example_5_announcements()
    example_6_company_info()
    example_7_error_handling()

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
