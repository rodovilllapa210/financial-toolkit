"""
Example 1: Basic Data Extraction

This example demonstrates how to extract historical price data
from Yahoo Finance for stocks and indices.
"""

from datetime import datetime, timedelta
from src.extractors.yahoo_finance import YahooFinanceExtractor
from src.utils.helpers import setup_logging

# Setup logging
setup_logging(level="INFO")

# Create extractor
extractor = YahooFinanceExtractor()

# Define date range (last year)
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

print("=" * 60)
print("EXAMPLE 1: Basic Data Extraction")
print("=" * 60)

# Example 1: Single stock
print("\n1. Extracting single stock (AAPL)...")
apple = extractor.get_historical_prices(
    symbol="AAPL",
    start_date=start_date,
    end_date=end_date
)

print(f"\nExtracted {len(apple)} data points for {apple.symbol}")
print(f"Date range: {apple.start_date.date()} to {apple.end_date.date()}")
print(f"Current price: ${apple.current_price:.2f}")
print(f"Total return: {apple.total_return():.2%}")

# Example 2: Market index
print("\n2. Extracting market index (S&P 500)...")
sp500 = extractor.get_index_data(
    index_symbol="^GSPC",
    start_date=start_date,
    end_date=end_date
)

print(f"\nExtracted {len(sp500)} data points for {sp500.symbol}")
print(f"Annualized return: {sp500.annualized_return():.2%}")
print(f"Annualized volatility: {sp500.annualized_volatility():.2%}")
print(f"Sharpe ratio: {sp500.sharpe_ratio():.3f}")

# Example 3: Multiple stocks at once
print("\n3. Extracting multiple stocks concurrently...")
symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

multiple_series = extractor.get_multiple_series(
    symbols=symbols,
    start_date=start_date,
    end_date=end_date,
    show_progress=True
)

print(f"\nSuccessfully extracted {len(multiple_series)} out of {len(symbols)} symbols")

# Display statistics for each
print("\nStatistics Summary:")
print("-" * 80)
print(f"{'Symbol':<10} {'Return':<12} {'Volatility':<12} {'Sharpe':<10} {'Max DD':<10}")
print("-" * 80)

for symbol, ps in multiple_series.items():
    print(f"{symbol:<10} {ps.annualized_return():>10.2%}  "
          f"{ps.annualized_volatility():>10.2%}  "
          f"{ps.sharpe_ratio():>8.3f}  "
          f"{ps.max_drawdown():>8.2%}")

print("\n" + "=" * 60)
print("Example completed successfully!")
print("=" * 60)
