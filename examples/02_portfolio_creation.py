"""
Example 2: Portfolio Creation and Analysis

This example demonstrates how to create a portfolio,
analyze its performance, and generate reports.
"""

from datetime import datetime, timedelta
from src.extractors.yahoo_finance import YahooFinanceExtractor
from src.models.portfolio import Portfolio
from src.processors.cleaner import DataCleaner
from src.utils.helpers import setup_logging

# Setup logging
setup_logging(level="INFO")

print("=" * 60)
print("EXAMPLE 2: Portfolio Creation and Analysis")
print("=" * 60)

# Step 1: Extract data for multiple assets
print("\n1. Extracting data for portfolio assets...")
extractor = YahooFinanceExtractor()

end_date = datetime.now()
start_date = end_date - timedelta(days=730)  # 2 years

symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
price_series = extractor.get_multiple_series(
    symbols=symbols,
    start_date=start_date,
    end_date=end_date
)

# Step 2: Clean the data
print("\n2. Cleaning and preprocessing data...")
cleaned_series = {}
for symbol, ps in price_series.items():
    cleaned_series[symbol] = DataCleaner.clean_price_series(
        ps,
        handle_missing='forward_fill',
        remove_outliers=True
    )

# Step 3: Align all series to common dates
print("\n3. Aligning series to common dates...")
aligned_series = DataCleaner.align_series(
    list(cleaned_series.values()),
    method='inner'
)

# Convert back to dictionary
aligned_dict = {ps.symbol: ps for ps in aligned_series}

# Step 4: Create portfolio
print("\n4. Creating portfolio...")
portfolio = Portfolio(
    name="Tech Growth Portfolio",
    holdings={
        "AAPL": 50,    # 50 shares of Apple
        "MSFT": 30,    # 30 shares of Microsoft
        "GOOGL": 20,   # 20 shares of Google
        "AMZN": 10,    # 10 shares of Amazon
        "TSLA": 15     # 15 shares of Tesla
    },
    price_series=aligned_dict,
    cash=10000.0    # $10,000 cash
)

print(f"\nPortfolio created: {portfolio}")
print(f"Total value: ${portfolio.total_value:,.2f}")

# Step 5: Analyze portfolio
print("\n5. Portfolio Analysis:")
print("-" * 60)

stats = portfolio.get_statistics()
print(f"Annualized Return: {stats['annualized_return']:.2%}")
print(f"Annualized Volatility: {stats['annualized_volatility']:.2%}")
print(f"Sharpe Ratio: {stats['sharpe_ratio']:.3f}")

print("\nPortfolio Weights:")
weights = portfolio.get_weights()
for symbol, weight in weights.items():
    value = portfolio.get_position_value(symbol)
    print(f"  {symbol}: {weight:.2%} (${value:,.2f})")

# Step 6: Correlation analysis
print("\n6. Correlation Analysis:")
print("-" * 60)
corr_matrix = portfolio.get_correlation_matrix()
print(corr_matrix)

# Step 7: Generate report
print("\n7. Generating Markdown report...")
report = portfolio.report(
    output_file="./portfolio_report.md",
    include_monte_carlo=False,
    include_correlations=True,
    print_to_console=False
)

print("Report saved to: ./portfolio_report.md")

print("\n" + "=" * 60)
print("Example completed successfully!")
print("=" * 60)
