"""
Main entry point for the Financial Market Analysis Toolkit.

This script provides a simple CLI interface for common operations.
"""

import argparse
from datetime import datetime, timedelta
from src.extractors.yahoo_finance import YahooFinanceExtractor
from src.models.portfolio import Portfolio
from src.processors.cleaner import DataCleaner
from src.utils.helpers import setup_logging


def main():
    parser = argparse.ArgumentParser(
        description='Financial Market Analysis Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract data for a single stock
  python main.py extract --symbols AAPL --days 365
  
  # Create and analyze a portfolio
  python main.py portfolio --symbols AAPL,MSFT,GOOGL --shares 10,20,15
  
  # Run Monte Carlo simulation
  python main.py simulate --symbols AAPL,MSFT --shares 50,30 --simulations 10000
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Extract command
    extract_parser = subparsers.add_parser('extract', help='Extract price data')
    extract_parser.add_argument('--symbols', required=True, help='Comma-separated symbols')
    extract_parser.add_argument('--days', type=int, default=365, help='Days of history')
    extract_parser.add_argument('--output', help='Output file (CSV)')
    
    # Portfolio command
    portfolio_parser = subparsers.add_parser('portfolio', help='Analyze portfolio')
    portfolio_parser.add_argument('--symbols', required=True, help='Comma-separated symbols')
    portfolio_parser.add_argument('--shares', required=True, help='Comma-separated share counts')
    portfolio_parser.add_argument('--days', type=int, default=365, help='Days of history')
    portfolio_parser.add_argument('--report', help='Output report file')
    portfolio_parser.add_argument('--plots', help='Output plots directory')
    
    # Simulate command
    simulate_parser = subparsers.add_parser('simulate', help='Monte Carlo simulation')
    simulate_parser.add_argument('--symbols', required=True, help='Comma-separated symbols')
    simulate_parser.add_argument('--shares', required=True, help='Comma-separated share counts')
    simulate_parser.add_argument('--days', type=int, default=365, help='Days of history')
    simulate_parser.add_argument('--simulations', type=int, default=10000, help='Number of simulations')
    simulate_parser.add_argument('--horizon', type=int, default=252, help='Simulation horizon (days)')
    simulate_parser.add_argument('--report', help='Output report file')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level='INFO')
    
    if args.command == 'extract':
        extract_command(args)
    elif args.command == 'portfolio':
        portfolio_command(args)
    elif args.command == 'simulate':
        simulate_command(args)
    else:
        parser.print_help()


def extract_command(args):
    """Extract price data for symbols."""
    print("=" * 60)
    print("EXTRACTING PRICE DATA")
    print("=" * 60)
    
    symbols = [s.strip() for s in args.symbols.split(',')]
    
    extractor = YahooFinanceExtractor()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    print(f"\nFetching data for {len(symbols)} symbols...")
    print(f"Date range: {start_date.date()} to {end_date.date()}")
    
    price_series = extractor.get_multiple_series(
        symbols=symbols,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"\nSuccessfully extracted {len(price_series)} series")
    
    # Display summary
    print("\nSummary:")
    print("-" * 60)
    for symbol, ps in price_series.items():
        print(f"{symbol}: {len(ps)} records, "
              f"Return: {ps.annualized_return():.2%}, "
              f"Volatility: {ps.annualized_volatility():.2%}")
    
    # Save to CSV if requested
    if args.output:
        for symbol, ps in price_series.items():
            filename = args.output.replace('.csv', f'_{symbol}.csv')
            ps.data.to_csv(filename, index=False)
            print(f"\nSaved {symbol} to {filename}")


def portfolio_command(args):
    """Analyze a portfolio."""
    print("=" * 60)
    print("PORTFOLIO ANALYSIS")
    print("=" * 60)
    
    symbols = [s.strip() for s in args.symbols.split(',')]
    shares = [float(s.strip()) for s in args.shares.split(',')]
    
    if len(symbols) != len(shares):
        print("Error: Number of symbols must match number of shares")
        return
    
    # Extract data
    extractor = YahooFinanceExtractor()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    print(f"\nFetching data for {len(symbols)} symbols...")
    price_series = extractor.get_multiple_series(symbols, start_date, end_date)
    
    # Clean and align
    cleaned = [DataCleaner.clean_price_series(ps) for ps in price_series.values()]
    aligned = DataCleaner.align_series(cleaned, method='inner')
    aligned_dict = {ps.symbol: ps for ps in aligned}
    
    # Create portfolio
    holdings = dict(zip(symbols, shares))
    portfolio = Portfolio(
        name="My Portfolio",
        holdings=holdings,
        price_series=aligned_dict
    )
    
    print(f"\nPortfolio created: {portfolio}")
    
    # Display statistics
    stats = portfolio.get_statistics()
    print("\nPortfolio Statistics:")
    print("-" * 60)
    print(f"Total Value:          ${stats['total_value']:,.2f}")
    print(f"Annualized Return:    {stats['annualized_return']:.2%}")
    print(f"Annualized Volatility: {stats['annualized_volatility']:.2%}")
    print(f"Sharpe Ratio:         {stats['sharpe_ratio']:.3f}")
    
    # Generate report if requested
    if args.report:
        portfolio.report(
            output_file=args.report,
            include_correlations=True,
            print_to_console=False
        )
        print(f"\nReport saved to {args.report}")
    
    # Generate plots if requested
    if args.plots:
        portfolio.plots_report(
            output_dir=args.plots,
            include_monte_carlo=False
        )
        print(f"\nPlots saved to {args.plots}")


def simulate_command(args):
    """Run Monte Carlo simulation."""
    print("=" * 60)
    print("MONTE CARLO SIMULATION")
    print("=" * 60)
    
    symbols = [s.strip() for s in args.symbols.split(',')]
    shares = [float(s.strip()) for s in args.shares.split(',')]
    
    if len(symbols) != len(shares):
        print("Error: Number of symbols must match number of shares")
        return
    
    # Extract data
    extractor = YahooFinanceExtractor()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=args.days)
    
    print(f"\nFetching data for {len(symbols)} symbols...")
    price_series = extractor.get_multiple_series(symbols, start_date, end_date)
    
    # Clean and align
    cleaned = [DataCleaner.clean_price_series(ps) for ps in price_series.values()]
    aligned = DataCleaner.align_series(cleaned, method='inner')
    aligned_dict = {ps.symbol: ps for ps in aligned}
    
    # Create portfolio
    holdings = dict(zip(symbols, shares))
    portfolio = Portfolio(
        name="Simulation Portfolio",
        holdings=holdings,
        price_series=aligned_dict
    )
    
    print(f"\nPortfolio value: ${portfolio.total_value:,.2f}")
    print(f"\nRunning {args.simulations:,} simulations over {args.horizon} days...")
    
    # Run simulation
    mc_results = portfolio.monte_carlo_simulation(
        n_simulations=args.simulations,
        n_days=args.horizon,
        confidence_level=0.95
    )
    
    # Display results
    stats = mc_results['statistics']
    print("\nSimulation Results:")
    print("-" * 60)
    print(f"Initial Value:        ${stats['initial_value']:,.2f}")
    print(f"Mean Final Value:     ${stats['mean_final_value']:,.2f}")
    print(f"Expected Return:      {stats['mean_return']:.2%}")
    print(f"Value at Risk (95%):  ${stats['var']:,.2f}")
    print(f"Best Case:            ${stats['max_final_value']:,.2f}")
    print(f"Worst Case:           ${stats['min_final_value']:,.2f}")
    
    # Generate report if requested
    if args.report:
        portfolio.report(
            output_file=args.report,
            include_monte_carlo=True,
            monte_carlo_params={
                'n_simulations': args.simulations,
                'n_days': args.horizon
            },
            print_to_console=False
        )
        print(f"\nFull report saved to {args.report}")


if __name__ == '__main__':
    main()
