"""
Unit tests for data cleaning and validation.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from src.processors.data_cleaner import DataCleaner
from src.processors.data_validator import DataValidator


# Test fixtures
@pytest.fixture
def sample_clean_data():
    """Create a clean sample dataset."""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'date': dates,
        'open': 100 + np.random.randn(100).cumsum(),
        'high': 105 + np.random.randn(100).cumsum(),
        'low': 95 + np.random.randn(100).cumsum(),
        'close': 100 + np.random.randn(100).cumsum(),
        'volume': np.random.randint(1000000, 10000000, 100),
        'adjusted_close': 100 + np.random.randn(100).cumsum()
    })
    
    # Ensure OHLC relationships are correct
    data['high'] = data[['open', 'high', 'close']].max(axis=1) + 1
    data['low'] = data[['open', 'low', 'close']].min(axis=1) - 1
    
    return data


@pytest.fixture
def sample_data_with_missing():
    """Create a dataset with missing values."""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'date': dates,
        'open': 100 + np.random.randn(100).cumsum(),
        'high': 105 + np.random.randn(100).cumsum(),
        'low': 95 + np.random.randn(100).cumsum(),
        'close': 100 + np.random.randn(100).cumsum(),
        'volume': np.random.randint(1000000, 10000000, 100),
        'adjusted_close': 100 + np.random.randn(100).cumsum()
    })
    
    # Introduce missing values
    missing_indices = np.random.choice(data.index, size=10, replace=False)
    data.loc[missing_indices, 'close'] = np.nan
    data.loc[missing_indices[:5], 'volume'] = np.nan
    
    return data


@pytest.fixture
def sample_data_with_outliers():
    """Create a dataset with outliers."""
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'date': dates,
        'open': 100 + np.random.randn(100).cumsum(),
        'high': 105 + np.random.randn(100).cumsum(),
        'low': 95 + np.random.randn(100).cumsum(),
        'close': 100 + np.random.randn(100).cumsum(),
        'volume': np.random.randint(1000000, 10000000, 100),
        'adjusted_close': 100 + np.random.randn(100).cumsum()
    })
    
    # Introduce outliers
    data.loc[10, 'close'] = 1000  # Extreme high
    data.loc[20, 'close'] = 10    # Extreme low
    data.loc[30, 'volume'] = 100000000  # Extreme volume
    
    return data


@pytest.fixture
def sample_data_with_gaps():
    """Create a dataset with date gaps."""
    dates = pd.date_range('2023-01-01', periods=80, freq='D')
    # Remove some dates to create gaps
    dates = dates.delete([10, 11, 12, 30, 31, 50])
    
    np.random.seed(42)
    data = pd.DataFrame({
        'date': dates,
        'open': 100 + np.random.randn(len(dates)).cumsum(),
        'high': 105 + np.random.randn(len(dates)).cumsum(),
        'low': 95 + np.random.randn(len(dates)).cumsum(),
        'close': 100 + np.random.randn(len(dates)).cumsum(),
        'volume': np.random.randint(1000000, 10000000, len(dates)),
        'adjusted_close': 100 + np.random.randn(len(dates)).cumsum()
    })
    
    return data


# ============================================================================
# DataCleaner Tests
# ============================================================================

class TestDataCleaner:
    """Tests for DataCleaner class."""
    
    def test_handle_missing_values_ffill(self, sample_data_with_missing):
        """Test forward fill method for missing values."""
        original_missing = sample_data_with_missing['close'].isna().sum()
        assert original_missing > 0
        
        cleaned = DataCleaner.handle_missing_values(
            sample_data_with_missing,
            method='ffill'
        )
        
        assert cleaned['close'].isna().sum() < original_missing
    
    def test_handle_missing_values_bfill(self, sample_data_with_missing):
        """Test backward fill method for missing values."""
        original_missing = sample_data_with_missing['close'].isna().sum()
        assert original_missing > 0
        
        cleaned = DataCleaner.handle_missing_values(
            sample_data_with_missing,
            method='bfill'
        )
        
        assert cleaned['close'].isna().sum() < original_missing
    
    def test_handle_missing_values_interpolate(self, sample_data_with_missing):
        """Test interpolation method for missing values."""
        original_missing = sample_data_with_missing['close'].isna().sum()
        assert original_missing > 0
        
        cleaned = DataCleaner.handle_missing_values(
            sample_data_with_missing,
            method='interpolate'
        )
        
        assert cleaned['close'].isna().sum() == 0
    
    def test_handle_missing_values_drop(self, sample_data_with_missing):
        """Test drop method for missing values."""
        original_length = len(sample_data_with_missing)
        
        cleaned = DataCleaner.handle_missing_values(
            sample_data_with_missing,
            method='drop'
        )
        
        assert len(cleaned) < original_length
        assert cleaned['close'].isna().sum() == 0
    
    def test_detect_outliers_iqr(self, sample_data_with_outliers):
        """Test outlier detection using IQR method."""
        outliers = DataCleaner.detect_outliers(
            sample_data_with_outliers,
            column='close',
            method='iqr'
        )
        
        assert isinstance(outliers, pd.Series)
        assert outliers.dtype == bool
        assert outliers.sum() > 0  # Should detect some outliers
    
    def test_detect_outliers_zscore(self, sample_data_with_outliers):
        """Test outlier detection using Z-score method."""
        outliers = DataCleaner.detect_outliers(
            sample_data_with_outliers,
            column='close',
            method='zscore',
            threshold=3
        )
        
        assert isinstance(outliers, pd.Series)
        assert outliers.dtype == bool
        assert outliers.sum() > 0  # Should detect some outliers
    
    def test_remove_outliers(self, sample_data_with_outliers):
        """Test outlier removal."""
        original_length = len(sample_data_with_outliers)
        
        cleaned = DataCleaner.remove_outliers(
            sample_data_with_outliers,
            column='close',
            method='iqr'
        )
        
        assert len(cleaned) < original_length
    
    def test_clip_outliers(self, sample_data_with_outliers):
        """Test outlier clipping."""
        original_max = sample_data_with_outliers['close'].max()
        original_min = sample_data_with_outliers['close'].min()
        
        cleaned = DataCleaner.clip_outliers(
            sample_data_with_outliers,
            column='close',
            method='iqr'
        )
        
        # After clipping, extreme values should be reduced
        assert cleaned['close'].max() < original_max
        assert cleaned['close'].min() > original_min
    
    def test_fill_date_gaps(self, sample_data_with_gaps):
        """Test filling date gaps."""
        original_length = len(sample_data_with_gaps)
        
        filled = DataCleaner.fill_date_gaps(
            sample_data_with_gaps,
            freq='D'
        )
        
        assert len(filled) > original_length
        
        # Check that dates are continuous
        date_diff = filled['date'].diff().dropna()
        assert (date_diff == pd.Timedelta(days=1)).all()
    
    def test_remove_duplicates(self):
        """Test duplicate removal."""
        data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=10, freq='D').tolist() * 2,
            'close': [100] * 20
        })
        
        cleaned = DataCleaner.remove_duplicates(data, subset=['date'])
        
        assert len(cleaned) == 10
        assert cleaned['date'].is_unique
    
    def test_align_series(self, sample_clean_data):
        """Test aligning multiple series."""
        # Create two series with different dates
        series1 = sample_clean_data.iloc[:80].copy()
        series2 = sample_clean_data.iloc[20:].copy()
        
        aligned = DataCleaner.align_series([series1, series2])
        
        assert len(aligned) == 2
        assert len(aligned[0]) == len(aligned[1])
        
        # Dates should match
        assert (aligned[0]['date'] == aligned[1]['date']).all()
    
    def test_normalize_volume(self, sample_clean_data):
        """Test volume normalization."""
        normalized = DataCleaner.normalize_volume(sample_clean_data)
        
        # Volume should be scaled
        assert 'volume_normalized' in normalized.columns
        assert normalized['volume_normalized'].min() >= 0
        assert normalized['volume_normalized'].max() <= 1


# ============================================================================
# DataValidator Tests
# ============================================================================

class TestDataValidator:
    """Tests for DataValidator class."""
    
    def test_validate_required_columns(self, sample_clean_data):
        """Test required columns validation."""
        # Should pass with all required columns
        assert DataValidator.validate_required_columns(sample_clean_data) == True
        
        # Should fail with missing columns
        incomplete_data = sample_clean_data.drop(columns=['close'])
        assert DataValidator.validate_required_columns(incomplete_data) == False
    
    def test_validate_date_column(self, sample_clean_data):
        """Test date column validation."""
        # Should pass with proper date column
        assert DataValidator.validate_date_column(sample_clean_data) == True
        
        # Should fail with missing date column
        no_date = sample_clean_data.drop(columns=['date'])
        assert DataValidator.validate_date_column(no_date) == False
    
    def test_validate_ohlc(self, sample_clean_data):
        """Test OHLC validation."""
        # Should pass with proper OHLC relationships
        assert DataValidator.validate_ohlc(sample_clean_data) == True
        
        # Create invalid OHLC data
        invalid_data = sample_clean_data.copy()
        invalid_data.loc[0, 'high'] = invalid_data.loc[0, 'low'] - 10
        
        assert DataValidator.validate_ohlc(invalid_data) == False
    
    def test_validate_positive_prices(self, sample_clean_data):
        """Test positive prices validation."""
        # Should pass with positive prices
        assert DataValidator.validate_positive_prices(sample_clean_data) == True
        
        # Should fail with negative prices
        invalid_data = sample_clean_data.copy()
        invalid_data.loc[0, 'close'] = -10
        
        assert DataValidator.validate_positive_prices(invalid_data) == False
    
    def test_validate_positive_volume(self, sample_clean_data):
        """Test positive volume validation."""
        # Should pass with positive volume
        assert DataValidator.validate_positive_volume(sample_clean_data) == True
        
        # Should fail with negative volume
        invalid_data = sample_clean_data.copy()
        invalid_data.loc[0, 'volume'] = -1000
        
        assert DataValidator.validate_positive_volume(invalid_data) == False
    
    def test_check_missing_values(self, sample_data_with_missing):
        """Test missing values check."""
        missing_info = DataValidator.check_missing_values(sample_data_with_missing)
        
        assert isinstance(missing_info, dict)
        assert 'total_missing' in missing_info
        assert 'missing_by_column' in missing_info
        assert missing_info['total_missing'] > 0
    
    def test_check_duplicates(self):
        """Test duplicate check."""
        data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=10, freq='D').tolist() + 
                    [pd.Timestamp('2023-01-01')],
            'close': [100] * 11
        })
        
        duplicates = DataValidator.check_duplicates(data, subset=['date'])
        
        assert duplicates > 0
    
    def test_generate_quality_report(self, sample_clean_data):
        """Test quality report generation."""
        report = DataValidator.generate_quality_report(sample_clean_data)
        
        assert isinstance(report, dict)
        assert 'total_records' in report
        assert 'missing_values' in report
        assert 'duplicate_dates' in report
        assert 'date_gaps' in report
        assert 'negative_prices' in report
        assert 'ohlc_violations' in report
        assert 'quality_score' in report
        
        # Clean data should have high quality score
        assert report['quality_score'] > 90
    
    def test_quality_report_with_issues(self, sample_data_with_missing):
        """Test quality report with data issues."""
        report = DataValidator.generate_quality_report(sample_data_with_missing)
        
        assert report['missing_values'] > 0
        assert report['quality_score'] < 100
    
    def test_convert_arbitrary_input_dataframe(self, sample_clean_data):
        """Test converting DataFrame input."""
        converted = DataValidator.convert_arbitrary_input(sample_clean_data)
        
        assert isinstance(converted, pd.DataFrame)
        assert 'date' in converted.columns
        assert 'close' in converted.columns
    
    def test_convert_arbitrary_input_dict(self):
        """Test converting dictionary input."""
        data_dict = {
            'date': ['2023-01-01', '2023-01-02', '2023-01-03'],
            'close': [100, 101, 102]
        }
        
        converted = DataValidator.convert_arbitrary_input(data_dict)
        
        assert isinstance(converted, pd.DataFrame)
        assert len(converted) == 3
        assert 'date' in converted.columns
    
    def test_convert_arbitrary_input_series(self):
        """Test converting Series input."""
        dates = pd.date_range('2023-01-01', periods=10, freq='D')
        series = pd.Series([100 + i for i in range(10)], index=dates)
        
        converted = DataValidator.convert_arbitrary_input(series)
        
        assert isinstance(converted, pd.DataFrame)
        assert 'date' in converted.columns
        assert 'close' in converted.columns
        assert len(converted) == 10


# ============================================================================
# Integration Tests
# ============================================================================

class TestDataProcessingIntegration:
    """Integration tests for data cleaning and validation."""
    
    def test_full_cleaning_pipeline(self, sample_data_with_missing):
        """Test complete data cleaning pipeline."""
        # 1. Check initial quality
        initial_report = DataValidator.generate_quality_report(sample_data_with_missing)
        assert initial_report['quality_score'] < 100
        
        # 2. Handle missing values
        cleaned = DataCleaner.handle_missing_values(
            sample_data_with_missing,
            method='interpolate'
        )
        
        # 3. Remove duplicates
        cleaned = DataCleaner.remove_duplicates(cleaned, subset=['date'])
        
        # 4. Check final quality
        final_report = DataValidator.generate_quality_report(cleaned)
        
        # Quality should improve
        assert final_report['quality_score'] > initial_report['quality_score']
        assert final_report['missing_values'] == 0
    
    def test_outlier_handling_pipeline(self, sample_data_with_outliers):
        """Test outlier detection and handling pipeline."""
        # 1. Detect outliers
        outliers = DataCleaner.detect_outliers(
            sample_data_with_outliers,
            column='close',
            method='iqr'
        )
        
        assert outliers.sum() > 0
        
        # 2. Clip outliers
        cleaned = DataCleaner.clip_outliers(
            sample_data_with_outliers,
            column='close',
            method='iqr'
        )
        
        # 3. Verify outliers are reduced
        outliers_after = DataCleaner.detect_outliers(
            cleaned,
            column='close',
            method='iqr'
        )
        
        assert outliers_after.sum() < outliers.sum()
    
    def test_date_gap_filling_pipeline(self, sample_data_with_gaps):
        """Test date gap filling pipeline."""
        # 1. Check initial gaps
        initial_report = DataValidator.generate_quality_report(sample_data_with_gaps)
        assert initial_report['date_gaps'] > 0
        
        # 2. Fill gaps
        filled = DataCleaner.fill_date_gaps(sample_data_with_gaps, freq='D')
        
        # 3. Handle missing values created by gap filling
        filled = DataCleaner.handle_missing_values(filled, method='interpolate')
        
        # 4. Check final gaps
        final_report = DataValidator.generate_quality_report(filled)
        
        # Gaps should be reduced or eliminated
        assert final_report['date_gaps'] <= initial_report['date_gaps']


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases in data processing."""
    
    def test_empty_dataframe(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        
        with pytest.raises(Exception):
            DataValidator.validate_required_columns(empty_df)
    
    def test_single_row_dataframe(self):
        """Test handling of single-row DataFrame."""
        single_row = pd.DataFrame({
            'date': [pd.Timestamp('2023-01-01')],
            'open': [100],
            'high': [105],
            'low': [95],
            'close': [102],
            'volume': [1000000],
            'adjusted_close': [102]
        })
        
        assert DataValidator.validate_required_columns(single_row) == True
        assert DataValidator.validate_ohlc(single_row) == True
    
    def test_all_missing_column(self):
        """Test handling of column with all missing values."""
        data = pd.DataFrame({
            'date': pd.date_range('2023-01-01', periods=10, freq='D'),
            'close': [np.nan] * 10
        })
        
        cleaned = DataCleaner.handle_missing_values(data, method='ffill')
        
        # Should still have NaN if all values are missing
        assert cleaned['close'].isna().all()
    
    def test_no_outliers(self, sample_clean_data):
        """Test outlier detection when there are no outliers."""
        outliers = DataCleaner.detect_outliers(
            sample_clean_data,
            column='close',
            method='iqr'
        )
        
        # Should return boolean series
        assert isinstance(outliers, pd.Series)
        assert outliers.dtype == bool


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
