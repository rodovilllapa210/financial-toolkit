"""
PriceSeries DataClass: Standardized representation of financial time series data.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from loguru import logger


@dataclass
class PriceSeries:
    """
    Standardized representation of a financial instrument's price series.
    
    This class provides a unified interface for price data regardless of the source API.
    Automatically calculates basic statistics upon initialization.
    
    Attributes:
        symbol: Ticker symbol (e.g., 'AAPL', 'SPY')
        name: Full name of the instrument
        data: DataFrame with columns [date, open, high, low, close, volume, adjusted_close]
        source: Data source identifier (e.g., 'yahoo', 'alpha_vantage')
        asset_type: Type of asset ('stock', 'index', 'etf', 'crypto', etc.)
        currency: Currency of prices
        metadata: Additional information from the source
    """
    
    symbol: str
    name: str
    data: pd.DataFrame
    source: str
    asset_type: str = "stock"
    currency: str = "USD"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Statistics (calculated automatically)
    _mean_price: Optional[float] = field(default=None, init=False, repr=False)
    _std_price: Optional[float] = field(default=None, init=False, repr=False)
    _mean_return: Optional[float] = field(default=None, init=False, repr=False)
    _std_return: Optional[float] = field(default=None, init=False, repr=False)
    _returns: Optional[pd.Series] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Validate and calculate basic statistics after initialization."""
        self._validate_data()
        self._standardize_columns()
        self._calculate_basic_stats()
        logger.info(f"PriceSeries created for {self.symbol} with {len(self.data)} records")
    
    def _validate_data(self):
        """Validate that the DataFrame has the required structure."""
        required_columns = ['date', 'close']
        
        if not isinstance(self.data, pd.DataFrame):
            raise TypeError("data must be a pandas DataFrame")
        
        if self.data.empty:
            raise ValueError("data DataFrame cannot be empty")
        
        # Check for required columns
        missing_cols = [col for col in required_columns if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Ensure date column is datetime
        if not pd.api.types.is_datetime64_any_dtype(self.data['date']):
            self.data['date'] = pd.to_datetime(self.data['date'])
        
        # Sort by date
        self.data = self.data.sort_values('date').reset_index(drop=True)
    
    def _standardize_columns(self):
        """Ensure all standard columns exist, filling with NaN if necessary."""
        standard_columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'adjusted_close']
        
        for col in standard_columns:
            if col not in self.data.columns:
                if col == 'adjusted_close':
                    # Use close price if adjusted_close is not available
                    self.data['adjusted_close'] = self.data['close']
                else:
                    self.data[col] = np.nan
        
        # Reorder columns
        self.data = self.data[standard_columns]
    
    def _calculate_basic_stats(self):
        """Calculate mean and standard deviation automatically."""
        prices = self.data['adjusted_close'].dropna()
        
        if len(prices) > 0:
            self._mean_price = float(prices.mean())
            self._std_price = float(prices.std())
            
            # Calculate returns
            self._returns = prices.pct_change().dropna()
            
            if len(self._returns) > 0:
                self._mean_return = float(self._returns.mean())
                self._std_return = float(self._returns.std())
    
    @property
    def mean_price(self) -> float:
        """Average price over the period."""
        return self._mean_price
    
    @property
    def std_price(self) -> float:
        """Standard deviation of prices."""
        return self._std_price
    
    @property
    def mean_return(self) -> float:
        """Average daily return."""
        return self._mean_return
    
    @property
    def std_return(self) -> float:
        """Standard deviation of daily returns (volatility)."""
        return self._std_return
    
    @property
    def returns(self) -> pd.Series:
        """Daily returns series."""
        return self._returns
    
    @property
    def start_date(self) -> datetime:
        """First date in the series."""
        return self.data['date'].iloc[0]
    
    @property
    def end_date(self) -> datetime:
        """Last date in the series."""
        return self.data['date'].iloc[-1]
    
    @property
    def current_price(self) -> float:
        """Most recent price."""
        return float(self.data['adjusted_close'].iloc[-1])
    
    @property
    def initial_price(self) -> float:
        """First price in the series."""
        return float(self.data['adjusted_close'].iloc[0])
    
    def total_return(self) -> float:
        """Total return over the entire period."""
        return (self.current_price / self.initial_price) - 1
    
    def annualized_return(self, trading_days: int = 252) -> float:
        """
        Calculate annualized return.
        
        Args:
            trading_days: Number of trading days per year (default: 252)
        
        Returns:
            Annualized return as a decimal
        """
        n_days = len(self.data)
        years = n_days / trading_days
        
        if years == 0:
            return 0.0
        
        total_ret = self.total_return()
        return (1 + total_ret) ** (1 / years) - 1
    
    def annualized_volatility(self, trading_days: int = 252) -> float:
        """
        Calculate annualized volatility.
        
        Args:
            trading_days: Number of trading days per year (default: 252)
        
        Returns:
            Annualized volatility as a decimal
        """
        return self.std_return * np.sqrt(trading_days)
    
    def sharpe_ratio(self, risk_free_rate: float = 0.02, trading_days: int = 252) -> float:
        """
        Calculate Sharpe ratio.
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 0.02 or 2%)
            trading_days: Number of trading days per year (default: 252)
        
        Returns:
            Sharpe ratio
        """
        ann_return = self.annualized_return(trading_days)
        ann_vol = self.annualized_volatility(trading_days)
        
        if ann_vol == 0:
            return 0.0
        
        return (ann_return - risk_free_rate) / ann_vol
    
    def max_drawdown(self) -> float:
        """
        Calculate maximum drawdown.
        
        Returns:
            Maximum drawdown as a decimal (negative value)
        """
        prices = self.data['adjusted_close']
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        return float(drawdown.min())
    
    def get_statistics(self) -> Dict[str, float]:
        """
        Get comprehensive statistics for the price series.
        
        Returns:
            Dictionary with various statistical measures
        """
        return {
            'symbol': self.symbol,
            'start_date': self.start_date.strftime('%Y-%m-%d'),
            'end_date': self.end_date.strftime('%Y-%m-%d'),
            'n_observations': len(self.data),
            'initial_price': self.initial_price,
            'current_price': self.current_price,
            'mean_price': self.mean_price,
            'std_price': self.std_price,
            'min_price': float(self.data['adjusted_close'].min()),
            'max_price': float(self.data['adjusted_close'].max()),
            'total_return': self.total_return(),
            'annualized_return': self.annualized_return(),
            'mean_daily_return': self.mean_return,
            'daily_volatility': self.std_return,
            'annualized_volatility': self.annualized_volatility(),
            'sharpe_ratio': self.sharpe_ratio(),
            'max_drawdown': self.max_drawdown(),
        }
    
    def resample(self, frequency: str = 'W') -> 'PriceSeries':
        """
        Resample the price series to a different frequency.
        
        Args:
            frequency: Pandas frequency string ('D', 'W', 'M', etc.)
        
        Returns:
            New PriceSeries with resampled data
        """
        resampled = self.data.set_index('date').resample(frequency).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'adjusted_close': 'last'
        }).dropna().reset_index()
        
        return PriceSeries(
            symbol=self.symbol,
            name=self.name,
            data=resampled,
            source=self.source,
            asset_type=self.asset_type,
            currency=self.currency,
            metadata={**self.metadata, 'resampled_from': frequency}
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'symbol': self.symbol,
            'name': self.name,
            'source': self.source,
            'asset_type': self.asset_type,
            'currency': self.currency,
            'data': self.data.to_dict('records'),
            'metadata': self.metadata,
            'statistics': self.get_statistics()
        }
    
    def __len__(self) -> int:
        """Return number of data points."""
        return len(self.data)
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"PriceSeries(symbol='{self.symbol}', "
                f"records={len(self.data)}, "
                f"period={self.start_date.date()} to {self.end_date.date()})")
