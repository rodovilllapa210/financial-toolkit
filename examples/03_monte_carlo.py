"""
Example 3: Monte Carlo Simulation

This example demonstrates how to run Monte Carlo simulations
to project portfolio evolution and assess risk.
"""

from datetime import datetime, timedelta
from src.extractors.yahoo_finance import YahooFinanceExtractor
from src.models.portfolio import Portfolio
from src.processors.cleaner import DataCleaner
from src.utils.helpers import setup_logging

# Setup logging
setup_logging(level="INFO")

print("=" * 60)
print("EXAMPLE 3: Monte Carlo Simulation")
print("=" * 60)

# Step 1: Create portfolio
print("\n1. Setting up portfolio...")
extractor = YahooFinanceExtractor()

end_date = datetime.now()
start_date = end_date - timedelta(days=365)

symbols = ["SPY", "QQQ", "IWM"]  # ETFs for diversification
price_series = extractor.get_multiple_series(symbols, start_date, end_date)

# Clean and align
cleaned = [DataCleaner.clean_price_series(ps) for ps in price_series.values()]
aligned = DataCleaner.align_series(cleaned, method='inner')
aligned_dict = {ps.symbol: ps for ps in aligned}

portfolio = Portfolio(
    name="Diversified ETF Portfolio",
    holdings={"SPY": 100, "QQQ": 50, "IWM": 75},
    price_series=aligned_dict,
    cash=5000.0
)

print(f"Portfolio value: ${portfolio.total_value:,.2f}")

# Step 2: Run Monte Carlo simulation
print("\n2. Running Monte Carlo simulation...")
print("   (This may take a moment...)")

mc_results = portfolio.monte_carlo_simulation(
    n_simulations=10000,
    n_days=252,  # 1 year
    method='geometric_brownian',
    confidence_level=0.95,
    simulate_individual=False
)

# Step 3: Display results
print("\n3. Simulation Results:")
print("-" * 60)

stats = mc_results['statistics']
print(f"Initial Value:        ${stats['initial_value']:>12,.2f}")
print(f"Mean Final Value:     ${stats['mean_final_value']:>12,.2f}")
print(f"Median Final Value:   ${stats['median_final_value']:>12,.2f}")
print(f"Expected Return:      {stats['mean_return']:>12.2%}")
print(f"\nRisk Metrics:")
print(f"Value at Risk (95%):  ${stats['var']:>12,.2f}")
print(f"CVaR (95%):           ${stats['cvar']:>12,.2f}")
print(f"\nRange:")
print(f"Best Case:            ${stats['max_final_value']:>12,.2f}")
print(f"Worst Case:           ${stats['min_final_value']:>12,.2f}")

# Step 4: Run simulation with individual assets
print("\n4. Running simulation with individual asset paths...")

mc_individual = portfolio.monte_carlo_simulation(
    n_simulations=5000,
    n_days=252,
    simulate_individual=True
)

print("\nIndividual asset simulation completed.")
print(f"Simulated {len(mc_individual['individual_simulations'])} assets")

# Step 5: Generate full report with Monte Carlo
print("\n5. Generating comprehensive report with Monte Carlo...")

portfolio.report(
    output_file="./monte_carlo_report.md",
    include_monte_carlo=True,
    monte_carlo_params={
        'n_simulations': 10000,
        'n_days': 252,
        'confidence_level': 0.95
    },
    print_to_console=False
)

print("Report saved to: ./monte_carlo_report.md")

# Step 6: Generate plots
print("\n6. Generating visualization plots...")

portfolio.plots_report(
    output_dir="./reports/monte_carlo",
    include_monte_carlo=True,
    monte_carlo_params={'n_simulations': 10000, 'n_days': 252}
)

print("Plots saved to: ./reports/monte_carlo/")

print("\n" + "=" * 60)
print("Example completed successfully!")
print("=" * 60)
