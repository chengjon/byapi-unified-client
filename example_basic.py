#!/usr/bin/env python3
"""
Basic usage example for the Byapi Stock API Client.

This example demonstrates common operations with the Byapi client library.
It shows how to:
1. Initialize the client
2. Fetch stock prices (latest and historical)
3. Get technical indicators
4. Handle errors gracefully

Requirements:
- Python 3.8+
- requests library
- python-dotenv library
- BYAPI_LICENCE environment variable set in .env file
"""

import logging
from datetime import datetime, timedelta
from byapi_client_simple import ByapiClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_1_latest_stock_price():
    """Example 1: Fetch the latest stock price."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Fetch Latest Stock Price")
    print("="*60)

    try:
        client = ByapiClient()
        stock_code = "000001"
        quote = client.stock_prices.get_latest(stock_code)

        print(f"\nStock: {quote.name} ({quote.code})")
        print(f"Current Price: ¥{quote.current_price:.2f}")
        print(f"Change: {quote.change:+.2f} ({quote.change_percent:+.2f}%)")

    except Exception as e:
        print(f"✗ Error: {e}")


def example_2_historical_prices():
    """Example 2: Fetch historical stock prices."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Fetch Historical Stock Prices")
    print("="*60)

    try:
        client = ByapiClient()
        stock_code = "000001"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d")

        quotes = client.stock_prices.get_historical(
            stock_code, start_date, end_date
        )

        if quotes:
            print(f"\nFound {len(quotes)} trading records:\n")
            for quote in quotes[-3:]:  # Show last 3
                date_str = quote.timestamp.strftime("%Y-%m-%d")
                print(f"{date_str}: ¥{quote.current_price:.2f} ({quote.change_percent:+.2f}%)")

    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run examples."""
    print("\n" + "="*60)
    print("Byapi Stock API Client - Usage Examples")
    print("="*60)

    example_1_latest_stock_price()
    example_2_historical_prices()

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()