"""
Data validation utilities.
"""

from typing import List, Dict, Tuple
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from loguru import logger

from src.models.price_series import PriceSeries


class DataValidator:
    """
    Validates financial time series data for quality and consistency.
    """
    
    @staticmethod
    def validate_price_series(
        price_series: PriceSeries,
        strict: bool = False
    ) -> Tuple[bool, List[str]]:
        """
        Validate a price series for data quality issues.
        
        Args:
            price_series: PriceSeries to validate
            strict: If True, apply stricter validation rules
        
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        # Check for minimum data points
        if len(price_series.data) < 30:
            warnings.append(f"Insufficient data: only {len(price_series.data)} points")
        
        # Check for missing values
        missing = price_series.data.isnull().sum()
        if missing.any():
            warnings.append(f"Missing values detected: {missing[missing > 0].to_dict()}")
        
        # Check for duplicate dates
        duplicates = price_series.data['date'].duplicated().sum()
        if duplicates > 0:
            warnings.append(f"Found {duplicates} duplicate dates")
        
        # Check for gaps in dates
        gaps = DataValidator._check_date_gaps(price_series.data['date'])
        if gaps > 0:
            warnings.append(f"Found {gaps} significant date gaps")
        
        # Check for zero or negative prices
        price_cols = ['open', 'high', 'low', 'close', 'adjusted_close']
        for col in price_cols:
            if col in price_series.data.columns:
                invalid = (price_series.data[col] <= 0).sum()
                if invalid > 0:
                    warnings.append(f"Found {invalid} zero/negative values in {col}")
        
        # Check for extreme returns
        if price_series.returns is not None:
            extreme_returns = (abs(price_series.returns) > 0.5).sum()
            if extreme_returns > 0:
                warnings.append(
                    f"Found {extreme_returns} extreme returns (>50% daily change)"
                )
        
        # Check OHLC relationships
        ohlc_issues = DataValidator._validate_ohlc_relationships(price_series.data)
        if ohlc_issues > 0:
            warnings.append(f"Found {ohlc_issues} OHLC relationship violations")
        
        # Strict mode additional checks
        if strict:
            # Check for sufficient trading volume
            if 'volume' in price_series.data.columns:
                zero_volume = (price_series.data['volume'] == 0).sum()
                if zero_volume > len(price_series.data) * 0.1:  # More than 10%
                    warnings.append(
                        f"High proportion of zero volume days: {zero_volume}"
                    )
            
            # Check for price consistency
            price_changes = price_series.data['adjusted_close'].pct_change()
            if price_changes.std() > 0.1:  # Very high volatility
                warnings.append(
                    f"Extremely high volatility detected: {price_changes.std():.2%}"
                )
        
        is_valid = len(warnings) == 0
        
        if warnings:
            logger.warning(f"Validation issues for {price_series.symbol}: {len(warnings)} warnings")
            for warning in warnings:
                logger.debug(f"  - {warning}")
        else:
            logger.info(f"Validation passed for {price_series.symbol}")
        
        return is_valid, warnings
    
    @staticmethod
    def _check_date_gaps(dates: pd.Series, max_gap_days: int = 10) -> int:
        """Check for significant gaps in date series."""
        if len(dates) < 2:
            return 0
        
        dates_sorted = dates.sort_values()
        gaps = dates_sorted.diff()
        
        # Count gaps larger than threshold
        significant_gaps = (gaps > timedelta(days=max_gap_days)).sum()
        
        return significant_gaps
    
    @staticmethod
    def _validate_ohlc_relationships(df: pd.DataFrame) -> int:
        """Validate OHLC price relationships."""
        ohlc_cols = ['open', 'high', 'low', 'close']
        
        if not all(col in df.columns for col in ohlc_cols):
            return 0
        
        # Check relationships
        violations = (
            (df['low'] > df['high']) |
            (df['open'] > df['high']) |
            (df['open'] < df['low']) |
            (df['close'] > df['high']) |
            (df['close'] < df['low'])
        ).sum()
        
        return violations
    
    @staticmethod
    def generate_quality_report(price_series: PriceSeries) -> Dict:
        """
        Generate a comprehensive quality report for a price series.
        
        Args:
            price_series: PriceSeries to analyze
        
        Returns:
            Dictionary with quality metrics
        """
        df = price_series.data
        
        # Basic metrics
        report = {
            'symbol': price_series.symbol,
            'n_observations': len(df),
            'date_range': {
                'start': price_series.start_date.strftime('%Y-%m-%d'),
                'end': price_series.end_date.strftime('%Y-%m-%d'),
                'days': (price_series.end_date - price_series.start_date).days
            },
            'completeness': {},
            'quality_issues': {},
            'statistics': {}
        }
        
        # Completeness
        for col in df.columns:
            if col != 'date':
                non_null = df[col].notna().sum()
                report['completeness'][col] = {
                    'count': int(non_null),
                    'percentage': float(non_null / len(df) * 100)
                }
        
        # Quality issues
        report['quality_issues']['duplicates'] = int(df['date'].duplicated().sum())
        report['quality_issues']['date_gaps'] = int(
            DataValidator._check_date_gaps(df['date'])
        )
        
        if 'adjusted_close' in df.columns:
            report['quality_issues']['zero_prices'] = int(
                (df['adjusted_close'] <= 0).sum()
            )
        
        report['quality_issues']['ohlc_violations'] = int(
            DataValidator._validate_ohlc_relationships(df)
        )
        
        # Statistical summary
        if 'adjusted_close' in df.columns:
            prices = df['adjusted_close'].dropna()
            report['statistics']['price'] = {
                'mean': float(prices.mean()),
                'std': float(prices.std()),
                'min': float(prices.min()),
                'max': float(prices.max()),
                'cv': float(prices.std() / prices.mean()) if prices.mean() != 0 else 0
            }
        
        if price_series.returns is not None:
            returns = price_series.returns.dropna()
            report['statistics']['returns'] = {
                'mean': float(returns.mean()),
                'std': float(returns.std()),
                'skewness': float(returns.skew()),
                'kurtosis': float(returns.kurtosis()),
                'min': float(returns.min()),
                'max': float(returns.max())
            }
        
        if 'volume' in df.columns:
            volume = df['volume'].dropna()
            report['statistics']['volume'] = {
                'mean': float(volume.mean()),
                'std': float(volume.std()),
                'zero_volume_days': int((volume == 0).sum())
            }
        
        # Overall quality score (0-100)
        score = 100
        score -= report['quality_issues']['duplicates'] * 2
        score -= report['quality_issues']['date_gaps'] * 5
        score -= report['quality_issues']['zero_prices'] * 10
        score -= report['quality_issues']['ohlc_violations'] * 3
        
        # Penalize for incompleteness
        avg_completeness = np.mean([
            v['percentage'] for v in report['completeness'].values()
        ])
        score = score * (avg_completeness / 100)
        
        report['quality_score'] = max(0, min(100, score))
        
        return report
    
    @staticmethod
    def can_accept_input(data: pd.DataFrame) -> Tuple[bool, str]:
        """
        Check if arbitrary input data can be converted to a PriceSeries.
        
        Args:
            data: DataFrame with potential price data
        
        Returns:
            Tuple of (can_accept, reason)
        """
        # Must be a DataFrame
        if not isinstance(data, pd.DataFrame):
            return False, "Input must be a pandas DataFrame"
        
        # Must not be empty
        if data.empty:
            return False, "DataFrame is empty"
        
        # Must have a date column (various possible names)
        date_columns = ['date', 'Date', 'datetime', 'Datetime', 'timestamp', 'time']
        has_date = any(col in data.columns for col in date_columns)
        
        if not has_date:
            return False, "No date/time column found"
        
        # Must have at least a price column
        price_columns = ['close', 'Close', 'price', 'Price', 'value', 'Value']
        has_price = any(col in data.columns for col in price_columns)
        
        if not has_price:
            return False, "No price column found"
        
        # Check if date column can be converted to datetime
        date_col = next(col for col in date_columns if col in data.columns)
        try:
            pd.to_datetime(data[date_col])
        except Exception:
            return False, f"Cannot convert {date_col} to datetime"
        
        # Check if price column is numeric
        price_col = next(col for col in price_columns if col in data.columns)
        if not pd.api.types.is_numeric_dtype(data[price_col]):
            return False, f"Price column {price_col} is not numeric"
        
        return True, "Input can be converted to PriceSeries"
    
    @staticmethod
    def convert_arbitrary_input(
        data: pd.DataFrame,
        symbol: str = "UNKNOWN",
        name: str = "Unknown Asset"
    ) -> PriceSeries:
        """
        Convert arbitrary DataFrame to PriceSeries.
        
        Args:
            data: DataFrame with price data
            symbol: Symbol to assign
            name: Name to assign
        
        Returns:
            PriceSeries object
        """
        can_accept, reason = DataValidator.can_accept_input(data)
        
        if not can_accept:
            raise ValueError(f"Cannot convert input: {reason}")
        
        df = data.copy()
        
        # Standardize column names
        column_mapping = {}
        
        # Map date column
        date_columns = ['date', 'Date', 'datetime', 'Datetime', 'timestamp', 'time']
        for col in date_columns:
            if col in df.columns:
                column_mapping[col] = 'date'
                break
        
        # Map price columns
        price_mappings = {
            'close': ['close', 'Close', 'price', 'Price', 'value', 'Value'],
            'open': ['open', 'Open'],
            'high': ['high', 'High'],
            'low': ['low', 'Low'],
            'volume': ['volume', 'Volume', 'vol', 'Vol']
        }
        
        for target, sources in price_mappings.items():
            for col in sources:
                if col in df.columns:
                    column_mapping[col] = target
                    break
        
        df = df.rename(columns=column_mapping)
        
        # Ensure date is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Create adjusted_close if not present
        if 'adjusted_close' not in df.columns:
            df['adjusted_close'] = df['close']
        
        # Fill missing standard columns
        for col in ['open', 'high', 'low', 'volume']:
            if col not in df.columns:
                if col == 'volume':
                    df[col] = 0
                else:
                    df[col] = df['close']
        
        # Select only standard columns
        df = df[['date', 'open', 'high', 'low', 'close', 'volume', 'adjusted_close']]
        
        return PriceSeries(
            symbol=symbol,
            name=name,
            data=df,
            source='user_input',
            asset_type='unknown',
            metadata={'converted_from_arbitrary_input': True}
        )
