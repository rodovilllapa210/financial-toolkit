"""
Markdown report generation for portfolios and price series.
"""

from typing import Optional, Dict, List
from datetime import datetime
import pandas as pd
import numpy as np
from tabulate import tabulate
from loguru import logger

from src.models.price_series import PriceSeries
from src.models.portfolio import Portfolio
from src.processors.validator import DataValidator


class MarkdownReporter:
    """
    Generates formatted Markdown reports for financial analysis.
    """
    
    @staticmethod
    def generate_price_series_report(
        price_series: PriceSeries,
        include_validation: bool = True,
        include_statistics: bool = True
    ) -> str:
        """
        Generate a Markdown report for a single price series.
        
        Args:
            price_series: PriceSeries to report on
            include_validation: Include data quality validation
            include_statistics: Include statistical analysis
        
        Returns:
            Markdown formatted report
        """
        lines = []
        
        # Header
        lines.append(f"# Price Series Report: {price_series.symbol}")
        lines.append(f"**{price_series.name}**\n")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        lines.append("---\n")
        
        # Basic Information
        lines.append("## Basic Information\n")
        lines.append(f"- **Symbol**: {price_series.symbol}")
        lines.append(f"- **Name**: {price_series.name}")
        lines.append(f"- **Asset Type**: {price_series.asset_type}")
        lines.append(f"- **Currency**: {price_series.currency}")
        lines.append(f"- **Data Source**: {price_series.source}")
        lines.append(f"- **Date Range**: {price_series.start_date.date()} to {price_series.end_date.date()}")
        lines.append(f"- **Observations**: {len(price_series.data)}\n")
        
        # Price Summary
        lines.append("## Price Summary\n")
        lines.append(f"- **Current Price**: ${price_series.current_price:.2f}")
        lines.append(f"- **Initial Price**: ${price_series.initial_price:.2f}")
        lines.append(f"- **Total Return**: {price_series.total_return():.2%}")
        lines.append(f"- **Min Price**: ${price_series.data['adjusted_close'].min():.2f}")
        lines.append(f"- **Max Price**: ${price_series.data['adjusted_close'].max():.2f}")
        lines.append(f"- **Average Price**: ${price_series.mean_price:.2f}\n")
        
        # Statistics
        if include_statistics:
            lines.append("## Statistical Analysis\n")
            lines.append("### Returns\n")
            lines.append(f"- **Mean Daily Return**: {price_series.mean_return:.4%}")
            lines.append(f"- **Daily Volatility**: {price_series.std_return:.4%}")
            lines.append(f"- **Annualized Return**: {price_series.annualized_return():.2%}")
            lines.append(f"- **Annualized Volatility**: {price_series.annualized_volatility():.2%}")
            lines.append(f"- **Sharpe Ratio**: {price_series.sharpe_ratio():.3f}")
            lines.append(f"- **Maximum Drawdown**: {price_series.max_drawdown():.2%}\n")
        
        # Data Quality
        if include_validation:
            lines.append("## Data Quality\n")
            quality_report = DataValidator.generate_quality_report(price_series)
            lines.append(f"**Quality Score**: {quality_report['quality_score']:.1f}/100\n")
            
            if quality_report['quality_issues']:
                lines.append("### Issues Detected\n")
                for issue, count in quality_report['quality_issues'].items():
                    if count > 0:
                        lines.append(f"- **{issue.replace('_', ' ').title()}**: {count}")
                lines.append("")
            
            # Completeness table
            if quality_report['completeness']:
                lines.append("### Data Completeness\n")
                completeness_data = [
                    [col, f"{info['percentage']:.1f}%", info['count']]
                    for col, info in quality_report['completeness'].items()
                ]
                lines.append(tabulate(
                    completeness_data,
                    headers=['Column', 'Completeness', 'Count'],
                    tablefmt='pipe'
                ))
                lines.append("")
        
        # Metadata
        if price_series.metadata:
            lines.append("## Additional Information\n")
            for key, value in price_series.metadata.items():
                lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    def generate_portfolio_report(
        portfolio: Portfolio,
        include_monte_carlo: bool = False,
        include_correlations: bool = True,
        monte_carlo_params: Optional[Dict] = None
    ) -> str:
        """
        Generate a comprehensive Markdown report for a portfolio.
        
        Args:
            portfolio: Portfolio to report on
            include_monte_carlo: Include Monte Carlo simulation results
            include_correlations: Include correlation analysis
            monte_carlo_params: Parameters for Monte Carlo simulation
        
        Returns:
            Markdown formatted report
        """
        lines = []
        
        # Header
        lines.append(f"# Portfolio Analysis Report: {portfolio.name}")
        lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        lines.append("---\n")
        
        # Executive Summary
        lines.append("## Executive Summary\n")
        stats = portfolio.get_statistics()
        lines.append(f"- **Total Value**: ${stats['total_value']:,.2f} {portfolio.currency}")
        lines.append(f"- **Number of Positions**: {stats['n_positions']}")
        lines.append(f"- **Cash Position**: ${portfolio.cash:,.2f}")
        lines.append(f"- **Annualized Return**: {stats['annualized_return']:.2%}")
        lines.append(f"- **Annualized Volatility**: {stats['annualized_volatility']:.2%}")
        lines.append(f"- **Sharpe Ratio**: {stats['sharpe_ratio']:.3f}\n")
        
        # Holdings
        lines.append("## Portfolio Holdings\n")
        holdings_data = []
        weights = portfolio.get_weights()
        
        for symbol in portfolio.symbols:
            value = portfolio.get_position_value(symbol)
            weight = weights[symbol]
            shares = portfolio.holdings[symbol]
            price = portfolio.price_series[symbol].current_price
            
            holdings_data.append([
                symbol,
                f"{shares:.2f}",
                f"${price:.2f}",
                f"${value:,.2f}",
                f"{weight:.2%}"
            ])
        
        lines.append(tabulate(
            holdings_data,
            headers=['Symbol', 'Shares', 'Price', 'Value', 'Weight'],
            tablefmt='pipe'
        ))
        lines.append("")
        
        # Individual Asset Performance
        lines.append("## Individual Asset Performance\n")
        performance_data = []
        
        for symbol in portfolio.symbols:
            ps = portfolio.price_series[symbol]
            performance_data.append([
                symbol,
                ps.name[:30] + "..." if len(ps.name) > 30 else ps.name,
                f"{ps.total_return():.2%}",
                f"{ps.annualized_return():.2%}",
                f"{ps.annualized_volatility():.2%}",
                f"{ps.sharpe_ratio():.3f}"
            ])
        
        lines.append(tabulate(
            performance_data,
            headers=['Symbol', 'Name', 'Total Return', 'Ann. Return', 'Ann. Vol', 'Sharpe'],
            tablefmt='pipe'
        ))
        lines.append("")
        
        # Correlation Analysis
        if include_correlations and portfolio.n_positions > 1:
            lines.append("## Correlation Analysis\n")
            corr_matrix = portfolio.get_correlation_matrix()
            
            lines.append("### Correlation Matrix\n")
            lines.append(corr_matrix.to_markdown())
            lines.append("")
            
            # Highlight high correlations
            lines.append("### Notable Correlations\n")
            high_corr = []
            for i in range(len(corr_matrix)):
                for j in range(i+1, len(corr_matrix)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:
                        symbol1 = corr_matrix.index[i]
                        symbol2 = corr_matrix.columns[j]
                        high_corr.append([symbol1, symbol2, f"{corr_val:.3f}"])
            
            if high_corr:
                lines.append(tabulate(
                    high_corr,
                    headers=['Asset 1', 'Asset 2', 'Correlation'],
                    tablefmt='pipe'
                ))
            else:
                lines.append("*No correlations above 0.7 detected.*")
            lines.append("")
        
        # Monte Carlo Simulation
        if include_monte_carlo:
            lines.append("## Monte Carlo Simulation\n")
            
            if monte_carlo_params is None:
                monte_carlo_params = {
                    'n_simulations': 10000,
                    'n_days': 252,
                    'confidence_level': 0.95
                }
            
            logger.info("Running Monte Carlo simulation for report...")
            mc_results = portfolio.monte_carlo_simulation(**monte_carlo_params)
            mc_stats = mc_results['statistics']
            
            lines.append(f"**Simulation Parameters**:")
            lines.append(f"- Simulations: {monte_carlo_params['n_simulations']:,}")
            lines.append(f"- Time Horizon: {monte_carlo_params['n_days']} days")
            lines.append(f"- Method: {mc_results['method']}\n")
            
            lines.append(f"**Results**:")
            lines.append(f"- **Initial Value**: ${mc_stats['initial_value']:,.2f}")
            lines.append(f"- **Mean Final Value**: ${mc_stats['mean_final_value']:,.2f}")
            lines.append(f"- **Median Final Value**: ${mc_stats['median_final_value']:,.2f}")
            lines.append(f"- **Expected Return**: {mc_stats['mean_return']:.2%}")
            lines.append(f"- **Value at Risk (VaR)**: ${mc_stats['var']:,.2f}")
            lines.append(f"- **Conditional VaR (CVaR)**: ${mc_stats['cvar']:,.2f}")
            lines.append(f"- **Best Case**: ${mc_stats['max_final_value']:,.2f}")
            lines.append(f"- **Worst Case**: ${mc_stats['min_final_value']:,.2f}\n")
        
        # Warnings and Recommendations
        lines.append("## Warnings and Recommendations\n")
        
        warnings = []
        recommendations = []
        
        # Check concentration risk
        max_weight = max(weights.values())
        if max_weight > 0.4:
            warnings.append(f"⚠️ High concentration risk: {max(weights, key=weights.get)} represents {max_weight:.1%} of portfolio")
            recommendations.append("Consider diversifying to reduce concentration risk")
        
        # Check volatility
        if stats['annualized_volatility'] > 0.3:
            warnings.append(f"⚠️ High portfolio volatility: {stats['annualized_volatility']:.1%}")
            recommendations.append("Consider adding lower-volatility assets to reduce risk")
        
        # Check Sharpe ratio
        if stats['sharpe_ratio'] < 0.5:
            warnings.append(f"⚠️ Low risk-adjusted returns: Sharpe ratio of {stats['sharpe_ratio']:.2f}")
            recommendations.append("Review asset selection to improve risk-adjusted performance")
        
        # Check correlations
        if include_correlations and portfolio.n_positions > 1:
            corr_matrix = portfolio.get_correlation_matrix()
            avg_corr = corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)].mean()
            if avg_corr > 0.7:
                warnings.append(f"⚠️ High average correlation: {avg_corr:.2f}")
                recommendations.append("Assets are highly correlated; diversification benefits may be limited")
        
        if warnings:
            lines.append("### Warnings\n")
            for warning in warnings:
                lines.append(f"- {warning}")
            lines.append("")
        
        if recommendations:
            lines.append("### Recommendations\n")
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        if not warnings and not recommendations:
            lines.append("✅ No significant issues detected. Portfolio appears well-balanced.\n")
        
        # Footer
        lines.append("---")
        lines.append(f"*Report generated by Financial Market Analysis Toolkit*")
        
        return "\n".join(lines)
    
    @staticmethod
    def save_report(content: str, filename: str):
        """
        Save report to file.
        
        Args:
            content: Report content
            filename: Output filename
        """
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"Report saved to {filename}")
