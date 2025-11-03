# Quick Start Guide

Get started with the Financial Market Analysis Toolkit in minutes!

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/financial-toolkit.git
cd financial-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

## Basic Usage

### 1. Extract Stock Data

```python
from datetime import datetime, timedelta
from src.extractors.yahoo_finance import YahooFinanceExtractor

# Create extractor
extractor = YahooFinanceExtractor()

# Get data for Apple
end_date = datetime.now()
start_date = end_date - timedelta(days=365)

apple = extractor.get_historical_prices(
    symbol="AAPL",
    start_date=start_date,
    end_date=end_date
)

print(f"Extracted {len(apple)} data points")
print(f"Current price: ${apple.current_price:.2f}")
print(f"Annual return: {apple.annualized_return():.2%}")
```

### 2. Create a Portfolio

```python
from src.models.portfolio import Portfolio

# Get data for multiple stocks
symbols = ["AAPL", "MSFT", "GOOGL"]
price_series = extractor.get_multiple_series(symbols, start_date, end_date)

# Create portfolio
portfolio = Portfolio(
    name="Tech Portfolio",
    holdings={
        "AAPL": 50,
        "MSFT": 30,
        "GOOGL": 20
    },
    price_series=price_series,
    cash=10000
)

print(f"Portfolio value: ${portfolio.total_value:,.2f}")
print(f"Sharpe ratio: {portfolio.sharpe_ratio():.3f}")
```

### 3. Run Monte Carlo Simulation

```python
# Simulate portfolio evolution
results = portfolio.monte_carlo_simulation(
    n_simulations=10000,
    n_days=252  # 1 year
)

stats = results['statistics']
print(f"Expected value: ${stats['mean_final_value']:,.2f}")
print(f"Value at Risk: ${stats['var']:,.2f}")
```

### 4. Generate Reports

```python
# Markdown report
portfolio.report(
    output_file="my_portfolio_report.md",
    include_monte_carlo=True
)

# Visualization plots
portfolio.plots_report(
    output_dir="./reports/plots"
)
```

## Command Line Interface

### Extract Data

```bash
python main.py extract --symbols AAPL,MSFT,GOOGL --days 365
```

### Analyze Portfolio

```bash
python main.py portfolio \
    --symbols AAPL,MSFT,GOOGL \
    --shares 50,30,20 \
    --report portfolio_report.md \
    --plots ./reports
```

### Monte Carlo Simulation

```bash
python main.py simulate \
    --symbols AAPL,MSFT \
    --shares 100,50 \
    --simulations 10000 \
    --horizon 252 \
    --report simulation_report.md
```

## Working with Custom Data

```python
import pandas as pd
from src.processors.validator import DataValidator

# Load your data
df = pd.read_csv("my_data.csv")

# Check if it can be converted
can_accept, reason = DataValidator.can_accept_input(df)

if can_accept:
    # Convert to PriceSeries
    price_series = DataValidator.convert_arbitrary_input(
        df,
        symbol="CUSTOM",
        name="My Custom Asset"
    )
    
    # Use it like any other PriceSeries
    print(price_series.get_statistics())
```

## Data Cleaning

```python
from src.processors.cleaner import DataCleaner

# Clean a price series
cleaned = DataCleaner.clean_price_series(
    price_series,
    handle_missing='forward_fill',
    remove_outliers=True
)

# Align multiple series to common dates
aligned = DataCleaner.align_series(
    [series1, series2, series3],
    method='inner'
)
```

## Next Steps

- Check out the [examples/](../examples/) directory for more detailed examples
- Read the [Architecture Documentation](ARCHITECTURE.md) to understand the design
- See [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute to the project

## Common Issues

### API Rate Limits

Yahoo Finance is free but has rate limits. If you're downloading many symbols:

```python
# Use smaller batches
extractor = YahooFinanceExtractor(max_workers=3)  # Reduce concurrent requests
```

### Missing Data

Some symbols may not have complete data:

```python
# Clean and handle missing values
cleaned = DataCleaner.clean_price_series(
    price_series,
    handle_missing='forward_fill'
)
```

### Memory Issues

For very large datasets:

```python
# Resample to lower frequency
weekly = price_series.resample('W')  # Weekly instead of daily
```

## Support

- Open an issue on GitHub
- Check existing issues for solutions
- Read the documentation in `docs/`

Happy analyzing! 📊
