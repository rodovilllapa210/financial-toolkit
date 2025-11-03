"""
Plot generation for financial data visualization.
"""

from typing import Optional, Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from pathlib import Path
from loguru import logger

from src.models.price_series import PriceSeries
from src.models.portfolio import Portfolio

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10


class PlotGenerator:
    """
    Generates various plots for financial analysis.
    """
    
    @staticmethod
    def plot_price_history(
        price_series: PriceSeries,
        show_volume: bool = True,
        save_path: Optional[str] = None
    ):
        """
        Plot price history with optional volume.
        
        Args:
            price_series: PriceSeries to plot
            show_volume: Include volume subplot
            save_path: Path to save figure
        """
        if show_volume and 'volume' in price_series.data.columns:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                           gridspec_kw={'height_ratios': [3, 1]})
        else:
            fig, ax1 = plt.subplots(figsize=(12, 6))
            ax2 = None
        
        # Price plot
        dates = price_series.data['date']
        prices = price_series.data['adjusted_close']
        
        ax1.plot(dates, prices, linewidth=2, color='#2E86AB', label='Price')
        ax1.fill_between(dates, prices, alpha=0.3, color='#2E86AB')
        
        ax1.set_title(f'{price_series.symbol} - {price_series.name}', 
                     fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price ($)', fontsize=12)
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # Add moving averages
        if len(prices) >= 50:
            ma20 = prices.rolling(window=20).mean()
            ma50 = prices.rolling(window=50).mean()
            ax1.plot(dates, ma20, '--', linewidth=1.5, color='orange', 
                    label='MA20', alpha=0.7)
            ax1.plot(dates, ma50, '--', linewidth=1.5, color='red', 
                    label='MA50', alpha=0.7)
            ax1.legend(loc='upper left')
        
        # Volume plot
        if ax2 is not None:
            volume = price_series.data['volume']
            colors = ['g' if prices.iloc[i] >= prices.iloc[i-1] else 'r' 
                     for i in range(1, len(prices))]
            colors = ['gray'] + colors
            
            ax2.bar(dates, volume, color=colors, alpha=0.5)
            ax2.set_ylabel('Volume', fontsize=12)
            ax2.set_xlabel('Date', fontsize=12)
            ax2.grid(True, alpha=0.3)
        else:
            ax1.set_xlabel('Date', fontsize=12)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_returns_distribution(
        price_series: PriceSeries,
        save_path: Optional[str] = None
    ):
        """
        Plot returns distribution with statistics.
        
        Args:
            price_series: PriceSeries to analyze
            save_path: Path to save figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
        
        returns = price_series.returns.dropna()
        
        # Histogram with KDE
        ax1.hist(returns, bins=50, density=True, alpha=0.7, 
                color='#2E86AB', edgecolor='black')
        
        # Fit normal distribution
        mu, sigma = returns.mean(), returns.std()
        x = np.linspace(returns.min(), returns.max(), 100)
        ax1.plot(x, 1/(sigma * np.sqrt(2 * np.pi)) * 
                np.exp(-(x - mu)**2 / (2 * sigma**2)),
                'r-', linewidth=2, label='Normal Distribution')
        
        ax1.axvline(mu, color='green', linestyle='--', linewidth=2, 
                   label=f'Mean: {mu:.4f}')
        ax1.set_title(f'Returns Distribution - {price_series.symbol}', 
                     fontsize=12, fontweight='bold')
        ax1.set_xlabel('Daily Returns', fontsize=10)
        ax1.set_ylabel('Density', fontsize=10)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Q-Q plot
        from scipy import stats
        stats.probplot(returns, dist="norm", plot=ax2)
        ax2.set_title('Q-Q Plot', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_portfolio_composition(
        portfolio: Portfolio,
        save_path: Optional[str] = None
    ):
        """
        Plot portfolio composition pie chart.
        
        Args:
            portfolio: Portfolio to visualize
            save_path: Path to save figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        weights = portfolio.get_weights()
        
        # Pie chart
        colors = plt.cm.Set3(range(len(weights)))
        wedges, texts, autotexts = ax1.pie(
            weights.values(),
            labels=weights.keys(),
            autopct='%1.1f%%',
            colors=colors,
            startangle=90
        )
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax1.set_title(f'Portfolio Composition - {portfolio.name}', 
                     fontsize=12, fontweight='bold')
        
        # Bar chart with values
        symbols = list(weights.keys())
        values = [portfolio.get_position_value(s) for s in symbols]
        
        bars = ax2.barh(symbols, values, color=colors)
        ax2.set_xlabel('Value ($)', fontsize=10)
        ax2.set_title('Position Values', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='x')
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            ax2.text(value, i, f' ${value:,.0f}', 
                    va='center', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_correlation_matrix(
        portfolio: Portfolio,
        save_path: Optional[str] = None
    ):
        """
        Plot correlation matrix heatmap.
        
        Args:
            portfolio: Portfolio to analyze
            save_path: Path to save figure
        """
        corr_matrix = portfolio.get_correlation_matrix()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn',
                   center=0, vmin=-1, vmax=1, square=True,
                   linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax)
        
        ax.set_title(f'Correlation Matrix - {portfolio.name}', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_monte_carlo_simulation(
        portfolio: Portfolio,
        mc_results: Dict,
        n_paths_to_show: int = 100,
        save_path: Optional[str] = None
    ):
        """
        Plot Monte Carlo simulation results.
        
        Args:
            portfolio: Portfolio object
            mc_results: Results from monte_carlo_simulation
            n_paths_to_show: Number of simulation paths to display
            save_path: Path to save figure
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        simulations = mc_results['simulations']
        stats = mc_results['statistics']
        n_days = mc_results['n_days']
        
        # 1. Simulation paths
        indices = np.random.choice(len(simulations), 
                                  min(n_paths_to_show, len(simulations)), 
                                  replace=False)
        
        for idx in indices:
            ax1.plot(simulations[idx], alpha=0.1, color='blue', linewidth=0.5)
        
        # Mean path
        mean_path = simulations.mean(axis=0)
        ax1.plot(mean_path, color='red', linewidth=2, label='Mean Path')
        
        # Confidence intervals
        percentiles = [5, 25, 75, 95]
        for p in percentiles:
            path = np.percentile(simulations, p, axis=0)
            ax1.plot(path, '--', linewidth=1.5, alpha=0.7, 
                    label=f'{p}th Percentile')
        
        ax1.set_title('Monte Carlo Simulation Paths', fontsize=12, fontweight='bold')
        ax1.set_xlabel('Days', fontsize=10)
        ax1.set_ylabel('Portfolio Value ($)', fontsize=10)
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # 2. Final value distribution
        final_values = simulations[:, -1]
        ax2.hist(final_values, bins=50, density=True, alpha=0.7, 
                color='#2E86AB', edgecolor='black')
        
        ax2.axvline(stats['mean_final_value'], color='red', 
                   linestyle='--', linewidth=2, 
                   label=f"Mean: ${stats['mean_final_value']:,.0f}")
        ax2.axvline(stats['median_final_value'], color='green', 
                   linestyle='--', linewidth=2,
                   label=f"Median: ${stats['median_final_value']:,.0f}")
        ax2.axvline(stats['var'], color='orange', 
                   linestyle='--', linewidth=2,
                   label=f"VaR: ${stats['var']:,.0f}")
        
        ax2.set_title('Distribution of Final Portfolio Values', 
                     fontsize=12, fontweight='bold')
        ax2.set_xlabel('Final Value ($)', fontsize=10)
        ax2.set_ylabel('Density', fontsize=10)
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. Returns distribution
        returns = (final_values / stats['initial_value']) - 1
        ax3.hist(returns, bins=50, density=True, alpha=0.7, 
                color='green', edgecolor='black')
        
        ax3.axvline(returns.mean(), color='red', linestyle='--', 
                   linewidth=2, label=f"Mean: {returns.mean():.2%}")
        ax3.axvline(0, color='black', linestyle='-', linewidth=1)
        
        ax3.set_title('Distribution of Returns', fontsize=12, fontweight='bold')
        ax3.set_xlabel('Return (%)', fontsize=10)
        ax3.set_ylabel('Density', fontsize=10)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Statistics summary
        ax4.axis('off')
        
        summary_text = f"""
        Monte Carlo Simulation Summary
        ═══════════════════════════════
        
        Initial Value:        ${stats['initial_value']:,.2f}
        
        Expected Outcomes:
        ─────────────────
        Mean Final Value:     ${stats['mean_final_value']:,.2f}
        Median Final Value:   ${stats['median_final_value']:,.2f}
        Expected Return:      {stats['mean_return']:.2%}
        
        Risk Metrics:
        ─────────────
        Std Dev:              ${stats['std_final_value']:,.2f}
        Value at Risk (95%):  ${stats['var']:,.2f}
        CVaR (95%):           ${stats['cvar']:,.2f}
        
        Range:
        ─────────────
        Best Case:            ${stats['max_final_value']:,.2f}
        Worst Case:           ${stats['min_final_value']:,.2f}
        
        Simulation Parameters:
        ─────────────────────
        Paths:                {mc_results['n_simulations']:,}
        Time Horizon:         {n_days} days
        Method:               {mc_results['method']}
        """
        
        ax4.text(0.1, 0.5, summary_text, fontsize=10, 
                family='monospace', verticalalignment='center')
        
        plt.suptitle(f'Monte Carlo Analysis - {portfolio.name}', 
                    fontsize=16, fontweight='bold', y=0.995)
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_portfolio_evolution(
        portfolio: Portfolio,
        save_path: Optional[str] = None
    ):
        """
        Plot historical portfolio value evolution.
        
        Args:
            portfolio: Portfolio to analyze
            save_path: Path to save figure
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Calculate portfolio values over time
        if portfolio._portfolio_values is None:
            portfolio._calculate_portfolio_values()
        
        pv = portfolio._portfolio_values
        
        ax.plot(pv['date'], pv['portfolio_value'], 
               linewidth=2, color='#2E86AB', label='Portfolio Value')
        ax.fill_between(pv['date'], pv['portfolio_value'], 
                       alpha=0.3, color='#2E86AB')
        
        # Add benchmark (equal-weighted)
        initial_value = pv['portfolio_value'].iloc[0]
        ax.axhline(initial_value, color='gray', linestyle='--', 
                  linewidth=1, label='Initial Value', alpha=0.7)
        
        ax.set_title(f'Portfolio Value Evolution - {portfolio.name}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Portfolio Value ($)', fontsize=12)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        
        # Add annotations
        current_value = pv['portfolio_value'].iloc[-1]
        total_return = (current_value / initial_value - 1) * 100
        
        ax.text(0.02, 0.98, 
               f'Total Return: {total_return:+.2f}%\n'
               f'Initial: ${initial_value:,.2f}\n'
               f'Current: ${current_value:,.2f}',
               transform=ax.transAxes,
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8),
               fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    @staticmethod
    def generate_full_report(
        portfolio: Portfolio,
        output_dir: str = "./reports",
        include_monte_carlo: bool = True,
        monte_carlo_params: Optional[Dict] = None
    ):
        """
        Generate all plots for a portfolio.
        
        Args:
            portfolio: Portfolio to analyze
            output_dir: Directory to save plots
            include_monte_carlo: Include Monte Carlo simulation
            monte_carlo_params: Parameters for Monte Carlo
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating plots for {portfolio.name}...")
        
        # Portfolio composition
        PlotGenerator.plot_portfolio_composition(
            portfolio,
            save_path=str(output_path / "01_composition.png")
        )
        
        # Portfolio evolution
        PlotGenerator.plot_portfolio_evolution(
            portfolio,
            save_path=str(output_path / "02_evolution.png")
        )
        
        # Correlation matrix
        if portfolio.n_positions > 1:
            PlotGenerator.plot_correlation_matrix(
                portfolio,
                save_path=str(output_path / "03_correlations.png")
            )
        
        # Individual asset plots
        for i, symbol in enumerate(portfolio.symbols, 1):
            ps = portfolio.price_series[symbol]
            
            PlotGenerator.plot_price_history(
                ps,
                save_path=str(output_path / f"04_{i}_{symbol}_price.png")
            )
            
            PlotGenerator.plot_returns_distribution(
                ps,
                save_path=str(output_path / f"05_{i}_{symbol}_returns.png")
            )
        
        # Monte Carlo simulation
        if include_monte_carlo:
            if monte_carlo_params is None:
                monte_carlo_params = {
                    'n_simulations': 10000,
                    'n_days': 252
                }
            
            mc_results = portfolio.monte_carlo_simulation(**monte_carlo_params)
            PlotGenerator.plot_monte_carlo_simulation(
                portfolio,
                mc_results,
                save_path=str(output_path / "06_monte_carlo.png")
            )
        
        logger.info(f"All plots saved to {output_dir}")
