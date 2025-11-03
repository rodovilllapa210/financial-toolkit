"""
Unit tests for PriceSeries class.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from src.models.price_series import PriceSeries


@pytest.fixture
def sample_data():
    """Create sample price data for testing."""
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    n = len(dates)
    
    # Generate synthetic price data
    np.random.seed(42)
    prices = 100 * np.exp(np.cumsum(np.random.normal(0.0005, 0.02, n)))
    
    df = pd.DataFrame({
        'date': dates,
        'open': prices * (1 + np.random.uniform(-0.01, 0.01, n)),
        'high': prices * (1 + np.random.uniform(0, 0.02, n)),
        'low': prices * (1 - np.random.uniform(0, 0.02, n)),
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, n),
        'adjusted_close': prices
    })
    
    return df


def test_price_series_creation(sample_data):
    """Test basic PriceSeries creation."""
    ps = PriceSeries(
        symbol="TEST",
        name="Test Asset",
        data=sample_data,
        source="test",
        asset_type="stock"
    )
    
    assert ps.symbol == "TEST"
    assert ps.name == "Test Asset"
    assert len(ps) == len(sample_data)
    assert ps.source == "test"


def test_automatic_statistics_calculation(sample_data):
    """Test that statistics are calculated automatically."""
    ps = PriceSeries(
        symbol="TEST",
        name="Test Asset",
        data=sample_data,
        source="test"
    )
    
    assert ps.mean_price is not None
    assert ps.std_price is not None
    assert ps.mean_return is not None
    assert ps.std_return is not None


def test_price_series_properties(sample_data):
    """Test various properties of PriceSeries."""
    ps = PriceSeries(
        symbol="TEST",
        name="Test Asset",
        data=sample_data,
        source="test"
    )
    
    assert isinstance(ps.start_date, datetime)
    assert isinstance(ps.end_date, datetime)
    assert ps.current_price > 0
    assert ps.initial_price > 0


def test_returns_calculation(sample_data):
    """Test that returns are calculated correctly."""
    ps = PriceSeries(
        symbol="TEST",
        name="Test Asset",
        data=sample_data,
        source="test"
    )
    
    returns = ps.returns
    assert len(returns) == len(sample_data) - 1
    assert returns.notna().all()


def test_sharpe_ratio(sample_data):
    """Test Sharpe ratio calculation."""
    ps = PriceSeries(
        symbol="TEST",
        name="Test Asset",
        data=sample_data,
        source="test"
    )
    
    sharpe = ps.sharpe_ratio()
    assert isinstance(sharpe, float)
    assert not np.isnan(sharpe)


def test_max_drawdown(sample_data):
    """Test maximum drawdown calculation."""
    ps = PriceSeries(
        symbol="TEST",
        name="Test Asset",
        data=sample_data,
        source="test"
    )
    
    mdd = ps.max_drawdown()
    assert isinstance(mdd, float)
    assert mdd <= 0  # Drawdown should be negative


def test_resample(sample_data):
    """Test resampling to different frequency."""
    ps = PriceSeries(
        symbol="TEST",
        name="Test Asset",
        data=sample_data,
        source="test"
    )
    
    weekly = ps.resample('W')
    assert len(weekly) < len(ps)
    assert weekly.symbol == ps.symbol


def test_missing_required_columns():
    """Test that missing required columns raise an error."""
    df = pd.DataFrame({
        'date': pd.date_range('2023-01-01', periods=10),
        'open': np.random.rand(10) * 100
        # Missing 'close' column
    })
    
    with pytest.raises(ValueError):
        PriceSeries(
            symbol="TEST",
            name="Test",
            data=df,
            source="test"
        )


def test_empty_dataframe():
    """Test that empty DataFrame raises an error."""
    df = pd.DataFrame()
    
    with pytest.raises(ValueError):
        PriceSeries(
            symbol="TEST",
            name="Test",
            data=df,
            source="test"
        )


def test_get_statistics(sample_data):
    """Test statistics dictionary generation."""
    ps = PriceSeries(
        symbol="TEST",
        name="Test Asset",
        data=sample_data,
        source="test"
    )
    
    stats = ps.get_statistics()
    
    assert 'symbol' in stats
    assert 'total_return' in stats
    assert 'annualized_return' in stats
    assert 'sharpe_ratio' in stats
    assert isinstance(stats, dict)
