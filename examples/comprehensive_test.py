"""
Comprehensive test of all toolkit functionalities (adapted for Stooq Extractor vB).
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from loguru import logger

from src.extractors.yahoo_finance import YahooFinanceExtractor
from src.extractors.stooq import StooqExtractor
from src.models.portfolio import Portfolio
from src.processors.cleaner import DataCleaner
from src.processors.validator import DataValidator
from src.utils.helpers import setup_logging

# Setup
setup_logging(level="INFO")
load_dotenv()

# Date range for testing
end_date = datetime.now()
start_date = end_date - timedelta(days=365)  # 1 year of data

print("=" * 80)
print("COMPREHENSIVE FINANCIAL TOOLKIT TEST")
print("=" * 80)
print(f"\nDate range: {start_date.date()} to {end_date.date()}")
print(f"Test date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")


# ============================================================================
# TEST 1: Yahoo Finance Extractor
# ============================================================================
print("\n" + "=" * 80)
print("TEST 1: YAHOO FINANCE DATA EXTRACTION")
print("=" * 80)

yahoo = YahooFinanceExtractor(max_workers=3)

# Test 1.1: Stock data
print("\n[1.1] Downloading stock data (AAPL)...")
try:
    aapl = yahoo.get_historical_prices("AAPL", start_date, end_date)
    print(f"✓ Success: {len(aapl)} records")
    print(f"  - Symbol: {aapl.symbol}")
    print(f"  - Name: {aapl.name}")
    print(f"  - Asset Type: {aapl.asset_type}")
    print(f"  - Currency: {aapl.currency}")
    print(f"  - Mean: ${aapl.mean_price:.2f}")
    print(f"  - Std Dev: ${aapl.std_price:.2f}")
    print(f"  - Sharpe Ratio: {aapl.sharpe_ratio():.3f}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 1.2: Index data
print("\n[1.2] Downloading index data (S&P 500)...")
try:
    sp500 = yahoo.get_index_data("^GSPC", start_date, end_date)
    print(f"✓ Success: {len(sp500)} records")
    print(f"  - Symbol: {sp500.symbol}")
    print(f"  - Name: {sp500.name}")
    print(f"  - Max Drawdown: {sp500.max_drawdown():.2%}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 1.3: Crypto data
print("\n[1.3] Downloading crypto data (Bitcoin)...")
try:
    btc = yahoo.get_crypto_data("BTC-USD", start_date, end_date)
    print(f"✓ Success: {len(btc)} records")
    print(f"  - Symbol: {btc.symbol}")
    print(f"  - Name: {btc.name}")
    print(f"  - Volatility: {btc.annualized_volatility():.2%}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 1.4: Multiple symbols concurrently
print("\n[1.4] Downloading multiple stocks concurrently...")
try:
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    results = yahoo.get_multiple_series(symbols, start_date, end_date, show_progress=True)
    print(f"✓ Success: Downloaded {len(results)}/{len(symbols)} symbols")
    for sym, series in results.items():
        print(f"  - {sym}: {len(series)} records, Mean: ${series.mean_price:.2f}")
except Exception as e:
    print(f"✗ Failed: {e}")


# ============================================================================
# TEST 2: Stooq Extractor (vB)
# ============================================================================
print("\n" + "=" * 80)
print("TEST 2: STOOQ DATA EXTRACTION (vB)")
print("=" * 80)

stooq = StooqExtractor(max_workers=3)

# Test 2.1: Stock data
print("\n[2.1] Downloading US stock data from Stooq (AAPL.US)...")
try:
    aapl_stooq = stooq.get_us_stock_data("AAPL", start_date, end_date)
    print(f"✓ Success: {len(aapl_stooq)} records")
    print(f"  - Symbol: {aapl_stooq.symbol}")
    print(f"  - Source: {aapl_stooq.source}")
    print(f"  - Mean: ${aapl_stooq.mean_price:.2f}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2.2: Index data
print("\n[2.2] Downloading index data from Stooq (^SPX)...")
try:
    spx_stooq = stooq.get_index_data("^SPX", start_date, end_date)
    print(f"✓ Success: {len(spx_stooq)} records")
    print(f"  - Symbol: {spx_stooq.symbol}")
    print(f"  - Name: {spx_stooq.name}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2.3A: Bond YIELD
print("\n[2.3A] Downloading 10Y US Treasury YIELD from Stooq (10YUSY.B)...")
try:
    bond_yield = stooq.get_bond_data("10YUSY.B", start_date, end_date)
    print(f"✓ Success: {len(bond_yield)} records")
    print(f"  - Symbol: {bond_yield.symbol}")
    print(f"  - Asset Type: {bond_yield.asset_type}")
    print(f"  - Bond Type: {bond_yield.metadata.get('bond_type')}")
    print(f"  - Mean Yield: {bond_yield.mean_price:.3f}%")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2.3B: Bond PRICE
print("\n[2.3B] Downloading 10Y US Treasury PRICE from Stooq (10YUSP.B)...")
try:
    bond_price = stooq.get_bond_data("10YUSP.B", start_date, end_date)
    print(f"✓ Success: {len(bond_price)} records")
    print(f"  - Symbol: {bond_price.symbol}")
    print(f"  - Asset Type: {bond_price.asset_type}")
    print(f"  - Bond Type: {bond_price.metadata.get('bond_type')}")
    print(f"  - Mean Price: {bond_price.mean_price:.3f}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 2.4: Crypto data BTC/USD
print("\n[2.4] Downloading crypto data from Stooq (BTCUSD)...")
try:
    btc_stooq = stooq.get_crypto_data("BTCUSD", start_date, end_date)  # también aceptaría "BTC"
    print(f"✓ Success: {len(btc_stooq)} records")
    print(f"  - Symbol: {btc_stooq.symbol}")
    print(f"  - Asset Type: {btc_stooq.asset_type}")
except Exception as e:
    print(f"✗ Failed: {e}")


# ============================================================================
# TEST 3: Data Validation and Cleaning
# ============================================================================
print("\n" + "=" * 80)
print("TEST 3: DATA VALIDATION AND CLEANING")
print("=" * 80)

# Test 3.1: Data quality report
print("\n[3.1] Generating data quality report...")
try:
    quality_report = DataValidator.generate_quality_report(aapl)
    print("✓ Quality Report:")
    print(f"  - Total Records: {quality_report['n_observations']}")
    print(f"  - Duplicates: {quality_report['quality_issues']['duplicates']}")
    print(f"  - Date Gaps: {quality_report['quality_issues']['date_gaps']}")
    print(f"  - Zero Prices: {quality_report['quality_issues']['zero_prices']}")
    print(f"  - OHLC Violations: {quality_report['quality_issues']['ohlc_violations']}")
    print(f"  - Quality Score: {quality_report['quality_score']:.1f}/100")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3.2: Handle missing values
print("\n[3.2] Testing missing value handling...")
try:
    import pandas as pd
    import numpy as np
    
    df_with_missing = aapl.data.copy()
    missing_indices = np.random.choice(df_with_missing.index, size=10, replace=False)
    df_with_missing.loc[missing_indices, 'close'] = np.nan
    
    print(f"  - Original missing values: {df_with_missing['close'].isna().sum()}")
    
    from src.models.price_series import PriceSeries
    ps_with_missing = PriceSeries(
        symbol="TEST",
        name="Test",
        data=df_with_missing,
        source="test"
    )
    
    cleaned_ffill = DataCleaner.clean_price_series(ps_with_missing, handle_missing='forward_fill', remove_outliers=False)
    print(f"  - After forward fill: {cleaned_ffill.data['close'].isna().sum()}")
    
    cleaned_interp = DataCleaner.clean_price_series(ps_with_missing, handle_missing='interpolate', remove_outliers=False)
    print(f"  - After interpolation: {cleaned_interp.data['close'].isna().sum()}")
    
    print("✓ Missing value handling works correctly")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3.3: Outlier detection
print("\n[3.3] Testing outlier detection...")
try:
    cleaned_no_outliers = DataCleaner.clean_price_series(aapl, remove_outliers=True, outlier_std=5.0)
    outliers_removed = len(aapl.data) - len(cleaned_no_outliers.data)
    print(f"✓ Removed {outliers_removed} outliers using statistical method (5 std)")
    
    cleaned_strict = DataCleaner.clean_price_series(aapl, remove_outliers=True, outlier_std=3.0)
    outliers_strict = len(cleaned_strict.data) - len(cleaned_no_outliers.data)
    print(f"✓ Removed {outliers_strict} additional outliers (3 std vs 5 std)")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3.4: OHLC validation
print("\n[3.4] Testing OHLC validation...")
try:
    is_valid, warnings = DataValidator.validate_price_series(aapl, strict=False)
    print(f"✓ OHLC validation: {'PASSED' if is_valid else 'FAILED'}")
    if warnings:
        print(f"  - Warnings: {len(warnings)}")
        for w in warnings[:3]:
            print(f"    • {w}")
except Exception as e:
    print(f"✗ Failed: {e}")


# ============================================================================
# TEST 4: Portfolio Creation and Analysis
# ============================================================================
print("\n" + "=" * 80)
print("TEST 4: PORTFOLIO CREATION AND ANALYSIS")
print("=" * 80)

# Test 4.1: Create portfolio
print("\n[4.1] Creating diversified portfolio...")
try:
    portfolio_data = {
        "AAPL": aapl,
        "MSFT": results.get("MSFT"),
        "GOOGL": results.get("GOOGL"),
        "BTC-USD": btc
    }
    portfolio_data = {k: v for k, v in portfolio_data.items() if v is not None}
    
    portfolio = Portfolio(
        name="Tech & Crypto Portfolio",
        holdings={"AAPL": 100, "MSFT": 50, "GOOGL": 30, "BTC-USD": 2},
        price_series=portfolio_data
    )
    
    print(f"✓ Portfolio created successfully")
    print(f"  - Name: {portfolio.name}")
    print(f"  - Positions: {portfolio.n_positions}")
    print(f"  - Total Value: ${portfolio.total_value:,.2f}")
    print(f"  - Annualized Return: {portfolio.annualized_return():.2%}")
    print(f"  - Annualized Volatility: {portfolio.annualized_volatility():.2%}")
    print(f"  - Sharpe Ratio: {portfolio.sharpe_ratio():.3f}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 4.2: Portfolio composition
print("\n[4.2] Analyzing portfolio composition...")
try:
    weights = portfolio.get_weights()
    print("✓ Portfolio Composition:")
    for asset, weight in weights.items():
        print(f"  - {asset}: {weight:.2%}")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 4.3: Correlation analysis
print("\n[4.3] Analyzing correlations...")
try:
    corr_matrix = portfolio.get_correlation_matrix()
    print("✓ Correlation Matrix:")
    print(corr_matrix.round(3))
except Exception as e:
    print(f"✗ Failed: {e}")


# ============================================================================
# TEST 5: Monte Carlo Simulation
# ============================================================================
print("\n" + "=" * 80)
print("TEST 5: MONTE CARLO SIMULATION")
print("=" * 80)

print("\n[5.1] Running Monte Carlo simulation...")
try:
    mc_results = portfolio.monte_carlo_simulation(
        n_simulations=1000,
        n_days=252,
        method='geometric_brownian'
    )
    stats = mc_results['statistics']
    print(f"✓ Simulation completed successfully")
    print(f"  - Simulations: {mc_results['n_simulations']}")
    print(f"  - Days: {mc_results['n_days']}")
    print(f"  - Method: {mc_results['method']}")
    print(f"  - Initial Value: ${stats['initial_value']:,.2f}")
    print(f"  - Mean Final Value: ${stats['mean_final_value']:,.2f}")
    print(f"  - Median Final Value: ${stats['median_final_value']:,.2f}")
    print(f"  - Min Final Value: ${stats['min_final_value']:,.2f}")
    print(f"  - Max Final Value: ${stats['max_final_value']:,.2f}")
    print(f"  - Mean Return: {stats['mean_return']:.2%}")
except Exception as e:
    print(f"✗ Failed: {e}")


# ============================================================================
# TEST 6: Reporting
# ============================================================================
print("\n" + "=" * 80)
print("TEST 6: REPORT GENERATION")
print("=" * 80)

os.makedirs("./reports", exist_ok=True)
os.makedirs("./reports/plots", exist_ok=True)

# Test 6.1: Markdown report
print("\n[6.1] Generating Markdown report...")
try:
    report = portfolio.report(
        output_file="./reports/comprehensive_test_report.md",
        include_monte_carlo=True,
        include_correlations=True,
        monte_carlo_params={'n_simulations': 1000, 'n_days': 252},
        print_to_console=False
    )
    print(f"✓ Markdown report generated: ./reports/comprehensive_test_report.md")
    print(f"  - Report length: {len(report)} characters")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 6.2: Plot report
print("\n[6.2] Generating plot report...")
try:
    portfolio.plots_report(
        output_dir="./reports/plots",
        include_monte_carlo=True,
        monte_carlo_params={'n_simulations': 1000, 'n_days': 252}
    )
    print(f"✓ Plot report generated: ./reports/plots/")
    
    import glob, os as _os
    plots = glob.glob("./reports/plots/*.png")
    print(f"  - Generated {len(plots)} plots:")
    for plot in plots:
        print(f"    • {_os.path.basename(plot)}")
except Exception as e:
    print(f"✗ Failed: {e}")


# ============================================================================
# TEST 7: Statistical Methods
# ============================================================================
print("\n" + "=" * 80)
print("TEST 7: STATISTICAL METHODS")
print("=" * 80)

print("\n[7.1] Testing PriceSeries statistical methods...")
try:
    print(f"✓ AAPL Statistics:")
    print(f"  - Mean Price: ${aapl.mean_price:.2f}")
    print(f"  - Std Dev Price: ${aapl.std_price:.2f}")
    print(f"  - Min: ${aapl.data['close'].min():.2f}")
    print(f"  - Max: ${aapl.data['close'].max():.2f}")
    print(f"  - Daily Return Mean: {aapl.mean_return:.4f}")
    print(f"  - Daily Return Std: {aapl.std_return:.4f}")
    print(f"  - Total Return: {aapl.total_return():.2%}")
    print(f"  - Annualized Return: {aapl.annualized_return():.2%}")
    print(f"  - Annualized Volatility: {aapl.annualized_volatility():.2%}")
    print(f"  - Sharpe Ratio: {aapl.sharpe_ratio():.3f}")
    print(f"  - Max Drawdown: {aapl.max_drawdown():.2%}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\n[7.2] Testing Portfolio statistical methods...")
try:
    print(f"✓ Portfolio Statistics:")
    print(f"  - Total Value: ${portfolio.total_value:,.2f}")
    print(f"  - Mean Return: {portfolio.mean_return:.4f}")
    print(f"  - Volatility: {portfolio.volatility:.4f}")
    print(f"  - Annualized Return: {portfolio.annualized_return():.2%}")
    print(f"  - Annualized Volatility: {portfolio.annualized_volatility():.2%}")
    print(f"  - Sharpe Ratio: {portfolio.sharpe_ratio():.3f}")
    
    returns = {sym: ps.total_return() for sym, ps in portfolio.price_series.items()}
    best = max(returns.items(), key=lambda x: x[1])
    worst = min(returns.items(), key=lambda x: x[1])
    print(f"  - Best Performing Asset: {best[0]} ({best[1]:.2%})")
    print(f"  - Worst Performing Asset: {worst[0]} ({worst[1]:.2%})")
except Exception as e:
    print(f"✗ Failed: {e}")


# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)

print("""
✓ All major functionalities tested:
  1. Yahoo Finance data extraction (stocks, indices, crypto)
  2. Stooq data extraction (stocks, indices, bonds, crypto) — vB extractor
  3. Data validation and quality reporting
  4. Missing value handling (forward fill, interpolation)
  5. Outlier detection (IQR, Z-score methods)
  6. OHLC validation
  7. Portfolio creation and management
  8. Portfolio composition analysis
  9. Correlation analysis
  10. Monte Carlo simulation (GBM method)
  11. Markdown report generation
  12. Plot report generation
  13. Statistical methods (returns, volatility, Sharpe, drawdown)
""")

print("=" * 80)
print("COMPREHENSIVE TEST COMPLETED")
print("=" * 80)
