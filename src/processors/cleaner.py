"""
Data cleaning and preprocessing utilities.
"""

from typing import Optional, List
import pandas as pd
import numpy as np
from loguru import logger

from src.models.price_series import PriceSeries


class DataCleaner:
    """
    Utilities for cleaning and preprocessing financial time series data.
    
    Handles common issues like missing values, outliers, and data quality problems.
    """
    
    @staticmethod
    def clean_price_series(
        price_series: PriceSeries,
        handle_missing: str = 'forward_fill',
        remove_outliers: bool = True,
        outlier_std: float = 5.0,
        min_data_points: int = 30
    ) -> PriceSeries:
        """
        Clean a price series with various preprocessing steps.
        
        Args:
            price_series: PriceSeries to clean
            handle_missing: Method for handling missing values
                           ('forward_fill', 'backward_fill', 'interpolate', 'drop')
            remove_outliers: Whether to remove statistical outliers
            outlier_std: Number of standard deviations for outlier detection
            min_data_points: Minimum required data points
        
        Returns:
            Cleaned PriceSeries
        """
        logger.info(f"Cleaning price series for {price_series.symbol}")
        
        df = price_series.data.copy()
        initial_len = len(df)
        
        # Check minimum data points
        if len(df) < min_data_points:
            raise ValueError(
                f"Insufficient data points: {len(df)} < {min_data_points}"
            )
        
        # Handle missing values
        df = DataCleaner._handle_missing_values(df, handle_missing)
        
        # Remove outliers
        if remove_outliers:
            df = DataCleaner._remove_outliers(df, outlier_std)
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['date'], keep='first')
        
        # Ensure chronological order
        df = df.sort_values('date').reset_index(drop=True)
        
        # Validate OHLC relationships
        df = DataCleaner._validate_ohlc(df)
        
        final_len = len(df)
        if final_len < initial_len:
            logger.info(f"Removed {initial_len - final_len} problematic records")
        
        # Create new PriceSeries with cleaned data
        return PriceSeries(
            symbol=price_series.symbol,
            name=price_series.name,
            data=df,
            source=price_series.source,
            asset_type=price_series.asset_type,
            currency=price_series.currency,
            metadata={
                **price_series.metadata,
                'cleaned': True,
                'cleaning_params': {
                    'handle_missing': handle_missing,
                    'remove_outliers': remove_outliers,
                    'outlier_std': outlier_std
                }
            }
        )
    
    @staticmethod
    def _handle_missing_values(df: pd.DataFrame, method: str) -> pd.DataFrame:
        """Handle missing values in the DataFrame."""
        missing_count = df.isnull().sum().sum()
        
        if missing_count == 0:
            return df
        
        logger.debug(f"Handling {missing_count} missing values using {method}")
        
        if method == 'forward_fill':
            df = df.fillna(method='ffill')
        elif method == 'backward_fill':
            df = df.fillna(method='bfill')
        elif method == 'interpolate':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].interpolate(method='linear')
        elif method == 'drop':
            df = df.dropna()
        else:
            raise ValueError(f"Unknown missing value method: {method}")
        
        # Drop any remaining NaN values
        df = df.dropna()
        
        return df
    
    @staticmethod
    def _remove_outliers(df: pd.DataFrame, n_std: float) -> pd.DataFrame:
        """Remove statistical outliers from price data."""
        # Calculate returns
        returns = df['adjusted_close'].pct_change()
        
        # Calculate bounds
        mean_return = returns.mean()
        std_return = returns.std()
        lower_bound = mean_return - n_std * std_return
        upper_bound = mean_return + n_std * std_return
        
        # Identify outliers
        outliers = (returns < lower_bound) | (returns > upper_bound)
        n_outliers = outliers.sum()
        
        if n_outliers > 0:
            logger.debug(f"Removing {n_outliers} outliers")
            # Keep first row (no return calculated)
            mask = ~outliers
            mask.iloc[0] = True
            df = df[mask].reset_index(drop=True)
        
        return df
    
    @staticmethod
    def _validate_ohlc(df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and fix OHLC relationships.
        
        Ensures: Low <= Open, Close <= High and Low <= High
        """
        # Check if OHLC columns exist and are not all NaN
        ohlc_cols = ['open', 'high', 'low', 'close']
        has_ohlc = all(col in df.columns for col in ohlc_cols)
        
        if not has_ohlc:
            return df
        
        # Check for invalid OHLC relationships
        invalid_mask = (
            (df['low'] > df['high']) |
            (df['open'] > df['high']) |
            (df['open'] < df['low']) |
            (df['close'] > df['high']) |
            (df['close'] < df['low'])
        )
        
        n_invalid = invalid_mask.sum()
        
        if n_invalid > 0:
            logger.warning(f"Found {n_invalid} records with invalid OHLC relationships")
            
            # Fix by adjusting high/low to accommodate open/close
            df.loc[invalid_mask, 'high'] = df.loc[invalid_mask, [
                'open', 'high', 'close'
            ]].max(axis=1)
            
            df.loc[invalid_mask, 'low'] = df.loc[invalid_mask, [
                'open', 'low', 'close'
            ]].min(axis=1)
        
        return df
    
    @staticmethod
    def align_series(
        series_list: List[PriceSeries],
        method: str = 'inner'
    ) -> List[PriceSeries]:
        """
        Align multiple price series to common dates.
        
        Args:
            series_list: List of PriceSeries to align
            method: Alignment method ('inner' or 'outer')
        
        Returns:
            List of aligned PriceSeries
        """
        if len(series_list) < 2:
            return series_list
        
        logger.info(f"Aligning {len(series_list)} price series using {method} join")
        
        # Get all unique dates
        if method == 'inner':
            # Find common dates
            date_sets = [set(ps.data['date']) for ps in series_list]
            common_dates = set.intersection(*date_sets)
            
            if not common_dates:
                raise ValueError("No common dates found across all series")
            
            logger.info(f"Found {len(common_dates)} common dates")
            
            # Filter each series to common dates
            aligned = []
            for ps in series_list:
                filtered_data = ps.data[ps.data['date'].isin(common_dates)].copy()
                filtered_data = filtered_data.sort_values('date').reset_index(drop=True)
                
                aligned.append(PriceSeries(
                    symbol=ps.symbol,
                    name=ps.name,
                    data=filtered_data,
                    source=ps.source,
                    asset_type=ps.asset_type,
                    currency=ps.currency,
                    metadata={**ps.metadata, 'aligned': True}
                ))
            
            return aligned
        
        elif method == 'outer':
            # Get all dates
            all_dates = set()
            for ps in series_list:
                all_dates.update(ps.data['date'])
            
            all_dates = sorted(all_dates)
            logger.info(f"Aligning to {len(all_dates)} total dates")
            
            # Reindex each series to all dates
            aligned = []
            for ps in series_list:
                df = ps.data.set_index('date').reindex(all_dates)
                df = df.fillna(method='ffill').fillna(method='bfill')
                df = df.reset_index().rename(columns={'index': 'date'})
                
                aligned.append(PriceSeries(
                    symbol=ps.symbol,
                    name=ps.name,
                    data=df,
                    source=ps.source,
                    asset_type=ps.asset_type,
                    currency=ps.currency,
                    metadata={**ps.metadata, 'aligned': True}
                ))
            
            return aligned
        
        else:
            raise ValueError(f"Unknown alignment method: {method}")
    
    @staticmethod
    def resample_to_frequency(
        price_series: PriceSeries,
        frequency: str = 'W'
    ) -> PriceSeries:
        """
        Resample price series to a different frequency.
        
        Args:
            price_series: PriceSeries to resample
            frequency: Target frequency ('D', 'W', 'M', 'Q', 'Y')
        
        Returns:
            Resampled PriceSeries
        """
        return price_series.resample(frequency)
