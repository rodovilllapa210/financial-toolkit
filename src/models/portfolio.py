"""
Portfolio DataClass: Represents a collection of financial instruments.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import pandas as pd
import numpy as np
from loguru import logger

from src.models.price_series import PriceSeries


@dataclass
class Portfolio:
    """
    Represents a portfolio of financial instruments.
    
    A portfolio is essentially a collection of PriceSeries objects with associated quantities.
    It provides methods for portfolio-level analysis, including Monte Carlo simulations.
    
    Attributes:
        name: Portfolio name
        holdings: Dictionary mapping symbols to quantities (number of shares)
        price_series: Dictionary mapping symbols to PriceSeries objects
        cash: Cash position in the portfolio
        currency: Portfolio currency
    """
    
    name: str
    holdings: Dict[str, float]
    price_series: Dict[str, PriceSeries]
    cash: float = 0.0
    currency: str = "USD"
    metadata: Dict = field(default_factory=dict)
    
    # Cached calculations
    _portfolio_values: Optional[pd.DataFrame] = field(default=None, init=False, repr=False)
    _correlation_matrix: Optional[pd.DataFrame] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Validate portfolio after initialization."""
        self._validate_portfolio()
        self._align_dates()
        logger.info(f"Portfolio '{self.name}' created with {len(self.holdings)} positions")
    
    def _validate_portfolio(self):
        """Validate that holdings match available price series."""
        for symbol in self.holdings.keys():
            if symbol not in self.price_series:
                raise ValueError(f"No price series found for symbol: {symbol}")
        
        # Warn about price series without holdings
        for symbol in self.price_series.keys():
            if symbol not in self.holdings:
                logger.warning(f"Price series for {symbol} exists but has no holdings")
    
    def _align_dates(self):
        """Align all price series to common dates."""
        if not self.price_series:
            return
        
        # Find common date range
        all_dates = [set(ps.data['date']) for ps in self.price_series.values()]
        common_dates = set.intersection(*all_dates)
        
        if not common_dates:
            logger.warning("No common dates found across all series - will use outer join with forward fill")
            # Don't modify the data - let _calculate_portfolio_values handle it
            return
        
        # Only filter if we have a reasonable number of common dates
        min_required_dates = 10
        if len(common_dates) >= min_required_dates:
            # Filter each series to common dates
            for symbol, ps in self.price_series.items():
                ps.data = ps.data[ps.data['date'].isin(common_dates)].reset_index(drop=True)
        else:
            logger.warning(f"Only {len(common_dates)} common dates found - will use outer join with forward fill")
    
    @property
    def symbols(self) -> List[str]:
        """List of symbols in the portfolio."""
        return list(self.holdings.keys())
    
    @property
    def n_positions(self) -> int:
        """Number of positions in the portfolio."""
        return len(self.holdings)
    
    @property
    def start_date(self) -> datetime:
        """Earliest common date across all holdings."""
        if not self.price_series:
            return None
        return min(ps.start_date for ps in self.price_series.values())
    
    @property
    def end_date(self) -> datetime:
        """Latest common date across all holdings."""
        if not self.price_series:
            return None
        return max(ps.end_date for ps in self.price_series.values())
    
    def get_position_value(self, symbol: str, date: Optional[datetime] = None) -> float:
        """
        Get the value of a specific position.
        
        Args:
            symbol: Ticker symbol
            date: Date for valuation (default: most recent)
        
        Returns:
            Position value in portfolio currency
        """
        if symbol not in self.holdings:
            return 0.0
        
        ps = self.price_series[symbol]
        
        if date is None:
            price = ps.current_price
        else:
            # Find closest date
            mask = ps.data['date'] == date
            if not mask.any():
                raise ValueError(f"Date {date} not found in price series for {symbol}")
            price = ps.data.loc[mask, 'adjusted_close'].iloc[0]
        
        return self.holdings[symbol] * price
    
    @property
    def total_value(self) -> float:
        """Current total portfolio value including cash."""
        positions_value = sum(
            self.get_position_value(symbol) 
            for symbol in self.holdings.keys()
        )
        return positions_value + self.cash
    
    @property
    def positions_value(self) -> float:
        """Current value of all positions (excluding cash)."""
        return sum(
            self.get_position_value(symbol) 
            for symbol in self.holdings.keys()
        )
    
    def get_weights(self) -> Dict[str, float]:
        """
        Calculate portfolio weights.
        
        Returns:
            Dictionary mapping symbols to their portfolio weights
        """
        total = self.positions_value
        
        if total == 0:
            return {symbol: 0.0 for symbol in self.holdings.keys()}
        
        return {
            symbol: self.get_position_value(symbol) / total
            for symbol in self.holdings.keys()
        }
    
    def get_portfolio_returns(self) -> pd.Series:
        """
        Calculate portfolio returns time series.
        
        Returns:
            Series of portfolio returns
        """
        if self._portfolio_values is None:
            self._calculate_portfolio_values()
        
        return self._portfolio_values['portfolio_value'].pct_change().dropna()
    
    def _calculate_portfolio_values(self):
        """Calculate historical portfolio values."""
        if not self.price_series:
            return
        
        # Build a DataFrame with all prices aligned by date
        price_dfs = []
        for symbol in self.holdings.keys():
            ps = self.price_series[symbol]
            df = ps.data[['date', 'adjusted_close']].copy()
            df = df.rename(columns={'adjusted_close': symbol})
            df = df.set_index('date')
            price_dfs.append(df)
        
        # Merge all dataframes on date (outer join to keep all dates)
        if len(price_dfs) == 1:
            all_prices = price_dfs[0]
        else:
            all_prices = price_dfs[0]
            for df in price_dfs[1:]:
                all_prices = all_prices.join(df, how='outer')
        
        # Forward fill missing values
        all_prices = all_prices.fillna(method='ffill').fillna(method='bfill')
        
        # Drop any remaining NaN rows
        all_prices = all_prices.dropna()
        
        if len(all_prices) == 0:
            logger.warning("No valid dates after alignment")
            self._portfolio_values = pd.DataFrame({
                'date': [],
                'portfolio_value': []
            })
            return
        
        # Calculate portfolio value for each date
        portfolio_values = []
        for idx, row in all_prices.iterrows():
            total = sum(
                self.holdings[symbol] * row[symbol]
                for symbol in self.holdings.keys()
            )
            portfolio_values.append(total)
        
        self._portfolio_values = pd.DataFrame({
            'date': all_prices.index,
            'portfolio_value': portfolio_values
        }).reset_index(drop=True)
    
    @property
    def mean_return(self) -> float:
        """Average portfolio return."""
        returns = self.get_portfolio_returns()
        if len(returns) == 0:
            return 0.0
        return float(returns.mean())
    
    @property
    def volatility(self) -> float:
        """Portfolio volatility (standard deviation of returns)."""
        returns = self.get_portfolio_returns()
        if len(returns) == 0:
            return 0.0
        return float(returns.std())
    
    def annualized_return(self, trading_days: int = 252) -> float:
        """Calculate annualized portfolio return."""
        returns = self.get_portfolio_returns()
        if len(returns) == 0:
            return 0.0
        return float((1 + returns.mean()) ** trading_days - 1)
    
    def annualized_volatility(self, trading_days: int = 252) -> float:
        """Calculate annualized portfolio volatility."""
        vol = self.volatility
        if vol == 0:
            return 0.0
        return vol * np.sqrt(trading_days)
    
    def sharpe_ratio(self, risk_free_rate: float = 0.02, trading_days: int = 252) -> float:
        """Calculate portfolio Sharpe ratio."""
        ann_return = self.annualized_return(trading_days)
        ann_vol = self.annualized_volatility(trading_days)
        
        if ann_vol == 0:
            return 0.0
        
        return (ann_return - risk_free_rate) / ann_vol
    
    def get_correlation_matrix(self) -> pd.DataFrame:
        """
        Calculate correlation matrix of returns.
        
        Returns:
            DataFrame with correlation matrix
        """
        if self._correlation_matrix is not None:
            return self._correlation_matrix
        
        # Build returns DataFrame
        returns_dict = {}
        for symbol in self.holdings.keys():
            ps = self.price_series[symbol]
            if ps.returns is not None and len(ps.returns) > 0:
                returns_dict[symbol] = ps.returns
        
        if not returns_dict:
            # Return empty correlation matrix if no returns available
            symbols = list(self.holdings.keys())
            self._correlation_matrix = pd.DataFrame(
                np.eye(len(symbols)),
                index=symbols,
                columns=symbols
            )
        else:
            returns_df = pd.DataFrame(returns_dict)
            self._correlation_matrix = returns_df.corr()
        
        return self._correlation_matrix
    
    def monte_carlo_simulation(
        self,
        n_simulations: int = 10000,
        n_days: int = 252,
        method: str = 'geometric_brownian',
        confidence_level: float = 0.95,
        simulate_individual: bool = False
    ) -> Dict:
        """
        Perform Monte Carlo simulation for portfolio evolution.
        
        Args:
            n_simulations: Number of simulation paths
            n_days: Number of days to simulate
            method: Simulation method ('geometric_brownian', 'historical')
            confidence_level: Confidence level for VaR calculation
            simulate_individual: If True, simulate each asset individually
        
        Returns:
            Dictionary with simulation results
        """
        logger.info(f"Running Monte Carlo simulation: {n_simulations} paths, {n_days} days")
        
        if method == 'geometric_brownian':
            results = self._monte_carlo_gbm(n_simulations, n_days, simulate_individual)
        elif method == 'historical':
            results = self._monte_carlo_historical(n_simulations, n_days)
        else:
            raise ValueError(f"Unknown simulation method: {method}")
        
        # Calculate statistics
        final_values = results['simulations'][:, -1]
        initial_value = self.total_value
        
        results['statistics'] = {
            'initial_value': initial_value,
            'mean_final_value': float(np.mean(final_values)),
            'median_final_value': float(np.median(final_values)),
            'std_final_value': float(np.std(final_values)),
            'min_final_value': float(np.min(final_values)),
            'max_final_value': float(np.max(final_values)),
            'mean_return': float(np.mean(final_values) / initial_value - 1),
            'var': float(np.percentile(final_values, (1 - confidence_level) * 100)),
            'cvar': float(np.mean(final_values[final_values <= np.percentile(
                final_values, (1 - confidence_level) * 100)])),
        }
        
        return results
    
    def _monte_carlo_gbm(
        self, 
        n_simulations: int, 
        n_days: int,
        simulate_individual: bool
    ) -> Dict:
        """
        Monte Carlo using Geometric Brownian Motion.
        
        This simulates each asset's price path and aggregates to portfolio level.
        """
        initial_value = self.total_value
        simulations = np.zeros((n_simulations, n_days + 1))
        simulations[:, 0] = initial_value
        
        if simulate_individual:
            # Simulate each asset separately
            individual_sims = {}
            
            for symbol in self.holdings.keys():
                ps = self.price_series[symbol]
                mu = ps.mean_return if ps.mean_return is not None else 0.0
                sigma = ps.std_return if ps.std_return is not None else 0.01
                S0 = ps.current_price
                n_shares = self.holdings[symbol]
                
                # Generate random walks
                dt = 1
                asset_sims = np.zeros((n_simulations, n_days + 1))
                asset_sims[:, 0] = S0
                
                for t in range(1, n_days + 1):
                    z = np.random.standard_normal(n_simulations)
                    asset_sims[:, t] = asset_sims[:, t-1] * np.exp(
                        (mu - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * z
                    )
                
                individual_sims[symbol] = asset_sims * n_shares
            
            # Aggregate to portfolio level
            for symbol in self.holdings.keys():
                simulations += individual_sims[symbol]
            
            return {
                'simulations': simulations,
                'individual_simulations': individual_sims,
                'method': 'geometric_brownian_motion',
                'n_simulations': n_simulations,
                'n_days': n_days
            }
        
        else:
            # Simulate at portfolio level
            mu = self.mean_return if self.mean_return is not None else 0.0
            sigma = self.volatility if self.volatility is not None else 0.01
            
            # Use small default if sigma is 0
            if sigma == 0:
                sigma = 0.01
            
            for t in range(1, n_days + 1):
                z = np.random.standard_normal(n_simulations)
                simulations[:, t] = simulations[:, t-1] * np.exp(
                    (mu - 0.5 * sigma**2) + sigma * z
                )
            
            return {
                'simulations': simulations,
                'method': 'geometric_brownian_motion',
                'n_simulations': n_simulations,
                'n_days': n_days
            }
    
    def _monte_carlo_historical(self, n_simulations: int, n_days: int) -> Dict:
        """Monte Carlo using historical bootstrap."""
        returns = self.get_portfolio_returns().values
        initial_value = self.total_value
        
        simulations = np.zeros((n_simulations, n_days + 1))
        simulations[:, 0] = initial_value
        
        for t in range(1, n_days + 1):
            # Sample returns with replacement
            sampled_returns = np.random.choice(returns, size=n_simulations)
            simulations[:, t] = simulations[:, t-1] * (1 + sampled_returns)
        
        return {
            'simulations': simulations,
            'method': 'historical_bootstrap',
            'n_simulations': n_simulations,
            'n_days': n_days
        }
    
    def get_statistics(self) -> Dict:
        """Get comprehensive portfolio statistics."""
        weights = self.get_weights()
        
        return {
            'name': self.name,
            'n_positions': self.n_positions,
            'total_value': self.total_value,
            'positions_value': self.positions_value,
            'cash': self.cash,
            'currency': self.currency,
            'weights': weights,
            'mean_return': self.mean_return,
            'volatility': self.volatility,
            'annualized_return': self.annualized_return(),
            'annualized_volatility': self.annualized_volatility(),
            'sharpe_ratio': self.sharpe_ratio(),
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else None,
            'end_date': self.end_date.strftime('%Y-%m-%d') if self.end_date else None,
        }
    
    def report(
        self,
        output_file: Optional[str] = None,
        include_monte_carlo: bool = False,
        include_correlations: bool = True,
        monte_carlo_params: Optional[Dict] = None,
        print_to_console: bool = True
    ) -> str:
        """
        Generate a comprehensive Markdown report for the portfolio.
        
        Args:
            output_file: Path to save the report (optional)
            include_monte_carlo: Include Monte Carlo simulation
            include_correlations: Include correlation analysis
            monte_carlo_params: Parameters for Monte Carlo simulation
            print_to_console: Print report to console
        
        Returns:
            Markdown formatted report string
        """
        from src.reporting.markdown_report import MarkdownReporter
        
        report_content = MarkdownReporter.generate_portfolio_report(
            self,
            include_monte_carlo=include_monte_carlo,
            include_correlations=include_correlations,
            monte_carlo_params=monte_carlo_params
        )
        
        if output_file:
            MarkdownReporter.save_report(report_content, output_file)
        
        if print_to_console:
            print(report_content)
        
        return report_content
    
    def plots_report(
        self,
        output_dir: str = "./reports/plots",
        include_monte_carlo: bool = True,
        monte_carlo_params: Optional[Dict] = None
    ):
        """
        Generate and save all visualization plots for the portfolio.
        
        Args:
            output_dir: Directory to save plots
            include_monte_carlo: Include Monte Carlo simulation plots
            monte_carlo_params: Parameters for Monte Carlo simulation
        """
        from src.reporting.plots import PlotGenerator
        
        PlotGenerator.generate_full_report(
            self,
            output_dir=output_dir,
            include_monte_carlo=include_monte_carlo,
            monte_carlo_params=monte_carlo_params
        )
        
        logger.info(f"All plots generated and saved to {output_dir}")
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"Portfolio(name='{self.name}', "
                f"positions={self.n_positions}, "
                f"value=${self.total_value:,.2f})")
