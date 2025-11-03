"""
Example 4: Working with Custom Data

This example demonstrates how to import custom data
and convert it to PriceSeries format.
"""

import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from src.processors.validator import DataValidator
from src.models.price_series import PriceSeries
from src.utils.helpers import setup_logging

# Setup logging
setup_logging(level="INFO")

print("=" * 60)
print("EXAMPLE 4: Working with Custom Data")
print("=" * 60)

# Example 1: Create synthetic data
print("\n1. Creating synthetic price data...")

dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
np.random.seed(42)

# Simulate price path using geometric Brownian motion
S0 = 100  # Initial price
mu = 0.0005  # Daily drift
sigma = 0.02  # Daily volatility

returns = np.random.normal(mu, sigma, len(dates))
prices = S0 * np.exp(np.cumsum(returns))

# Create DataFrame
custom_data = pd.DataFrame({
    'Date': dates,
    'Close': prices,
    'Open': prices * (1 + np.random.uniform(-0.01, 0.01, len(dates))),
    'High': prices * (1 + np.random.uniform(0, 0.02, len(dates))),
    'Low': prices * (1 - np.random.uniform(0, 0.02, len(dates))),
    'Volume': np.random.randint(1000000, 10000000, len(dates))
})

print(f"Created {len(custom_data)} data points")
print(custom_data.head())

# Example 2: Validate if data can be accepted
print("\n2. Validating custom data...")

can_accept, reason = DataValidator.can_accept_input(custom_data)
print(f"Can accept: {can_accept}")
print(f"Reason: {reason}")

# Example 3: Convert to PriceSeries
print("\n3. Converting to PriceSeries...")

if can_accept:
    price_series = DataValidator.convert_arbitrary_input(
        custom_data,
        symbol="CUSTOM",
        name="Custom Synthetic Asset"
    )
    
    print(f"Created: {price_series}")
    print(f"Mean price: ${price_series.mean_price:.2f}")
    print(f"Volatility: {price_series.annualized_volatility():.2%}")
    print(f"Sharpe ratio: {price_series.sharpe_ratio():.3f}")

# Example 4: Data quality report
print("\n4. Generating data quality report...")

quality_report = DataValidator.generate_quality_report(price_series)

print(f"\nQuality Score: {quality_report['quality_score']:.1f}/100")
print(f"Observations: {quality_report['n_observations']}")
print(f"Date Range: {quality_report['date_range']['start']} to {quality_report['date_range']['end']}")

print("\nCompleteness:")
for col, info in quality_report['completeness'].items():
    print(f"  {col}: {info['percentage']:.1f}%")

print("\nQuality Issues:")
for issue, count in quality_report['quality_issues'].items():
    print(f"  {issue}: {count}")

# Example 5: Load from CSV (simulated)
print("\n5. Example: Loading from CSV file...")

# Save our synthetic data to CSV
csv_file = "./custom_data.csv"
custom_data.to_csv(csv_file, index=False)
print(f"Saved data to {csv_file}")

# Load it back
loaded_data = pd.read_csv(csv_file)
print(f"Loaded {len(loaded_data)} rows from CSV")

# Convert to PriceSeries
loaded_series = DataValidator.convert_arbitrary_input(
    loaded_data,
    symbol="LOADED",
    name="Loaded from CSV"
)

print(f"Created PriceSeries: {loaded_series}")

# Example 6: Validate the series
print("\n6. Validating the loaded series...")

is_valid, warnings = DataValidator.validate_price_series(
    loaded_series,
    strict=False
)

print(f"Valid: {is_valid}")
if warnings:
    print("Warnings:")
    for warning in warnings:
        print(f"  - {warning}")
else:
    print("No warnings - data quality is good!")

print("\n" + "=" * 60)
print("Example completed successfully!")
print("=" * 60)
