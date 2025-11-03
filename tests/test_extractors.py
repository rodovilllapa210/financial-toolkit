"""
Unit tests for data extractors.
"""

import pytest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from src.extractors.yahoo_finance import YahooFinanceExtractor
from src.extractors.stooq import StooqExtractor
from src.models.price_series import PriceSeries


# Test fixtures
@pytest.fixture
def date_range():
    """Provide a standard date range for testing."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)  # 3 months
    return start_date, end_date


@pytest.fixture
def yahoo_extractor():
    """Create a Yahoo Finance extractor instance."""
    return YahooFinanceExtractor(max_workers=2)


@pytest.fixture
def stooq_extractor():
    """Create a Stooq extractor instance."""
    return StooqExtractor(max_workers=2)


# ============================================================================
# Yahoo Finance Extractor Tests
# ============================================================================

class TestYahooFinanceExtractor:
    """Tests for Yahoo Finance data extractor."""
    
    def test_initialization(self, yahoo_extractor):
        """Test extractor initialization."""
        assert yahoo_extractor is not None
        assert yahoo_extractor.max_workers == 2
        assert yahoo_extractor.api_key is None
        assert yahoo_extractor.source_name == 'yahoofinance'
    
    def test_get_stock_data(self, yahoo_extractor, date_range):
        """Test downloading stock data."""
        start_date, end_date = date_range
        
        price_series = yahoo_extractor.get_historical_prices(
            "AAPL",
            start_date,
            end_date
        )
        
        assert isinstance(price_series, PriceSeries)
        assert price_series.symbol == "AAPL"
        assert price_series.source == "yahoo_finance"
        assert price_series.asset_type == "stock"
        assert len(price_series) > 0
        assert price_series.currency == "USD"
        
        # Check required columns
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            assert col in price_series.data.columns
    
    def test_get_index_data(self, yahoo_extractor, date_range):
        """Test downloading index data."""
        start_date, end_date = date_range
        
        price_series = yahoo_extractor.get_index_data(
            "^GSPC",
            start_date,
            end_date
        )
        
        assert isinstance(price_series, PriceSeries)
        assert price_series.symbol == "^GSPC"
        assert price_series.asset_type == "index"
        assert len(price_series) > 0
    
    def test_get_crypto_data(self, yahoo_extractor, date_range):
        """Test downloading cryptocurrency data."""
        start_date, end_date = date_range
        
        price_series = yahoo_extractor.get_crypto_data(
            "BTC-USD",
            start_date,
            end_date
        )
        
        assert isinstance(price_series, PriceSeries)
        assert "BTC" in price_series.symbol
        assert price_series.asset_type == "crypto"
        assert len(price_series) > 0
    
    def test_get_forex_data(self, yahoo_extractor, date_range):
        """Test downloading forex data."""
        start_date, end_date = date_range
        
        price_series = yahoo_extractor.get_forex_data(
            "EUR",
            "USD",
            start_date,
            end_date
        )
        
        assert isinstance(price_series, PriceSeries)
        assert "EUR" in price_series.symbol
        assert "USD" in price_series.symbol
        assert price_series.asset_type == "forex"
        assert len(price_series) > 0
    
    def test_get_multiple_series(self, yahoo_extractor, date_range):
        """Test downloading multiple symbols concurrently."""
        start_date, end_date = date_range
        symbols = ["AAPL", "MSFT", "GOOGL"]
        
        results = yahoo_extractor.get_multiple_series(
            symbols,
            start_date,
            end_date,
            show_progress=False
        )
        
        assert isinstance(results, dict)
        assert len(results) >= 2  # At least 2 should succeed
        
        for symbol, price_series in results.items():
            assert isinstance(price_series, PriceSeries)
            assert price_series.symbol == symbol
            assert len(price_series) > 0
    
    def test_invalid_symbol(self, yahoo_extractor, date_range):
        """Test handling of invalid symbol."""
        start_date, end_date = date_range
        
        with pytest.raises(Exception):
            yahoo_extractor.get_historical_prices(
                "INVALID_SYMBOL_12345",
                start_date,
                end_date
            )
    
    def test_get_fundamentals(self, yahoo_extractor):
        """Test getting fundamental data."""
        fundamentals = yahoo_extractor.get_fundamentals("AAPL")
        
        assert isinstance(fundamentals, dict)
        assert 'symbol' in fundamentals
        assert fundamentals['symbol'] == "AAPL"
        assert 'name' in fundamentals
        assert 'sector' in fundamentals
        assert 'market_cap' in fundamentals
    
    def test_validate_symbol(self, yahoo_extractor):
        """Test symbol validation."""
        # Valid symbol
        assert yahoo_extractor.validate_symbol("AAPL") == True
        
        # Invalid symbol (this might take a moment)
        # Note: This test might be slow, consider marking as slow
        # assert yahoo_extractor.validate_symbol("INVALID12345") == False


# ============================================================================
# Stooq Extractor Tests
# ============================================================================

class TestStooqExtractor:
    """Tests for Stooq data extractor."""
    
    def test_initialization(self, stooq_extractor):
        """Test extractor initialization."""
        assert stooq_extractor is not None
        assert stooq_extractor.max_workers == 2
        assert stooq_extractor.api_key is None
        assert stooq_extractor.source_name == 'stooq'
    
    def test_get_us_stock_data(self, stooq_extractor, date_range):
        """Test downloading US stock data from Stooq."""
        start_date, end_date = date_range
        
        price_series = stooq_extractor.get_us_stock_data(
            "AAPL",
            start_date,
            end_date
        )
        
        assert isinstance(price_series, PriceSeries)
        assert "AAPL" in price_series.symbol
        assert ".US" in price_series.symbol
        assert price_series.source == "stooq"
        assert price_series.asset_type == "stock"
        assert len(price_series) > 0
        
        # Check required columns
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            assert col in price_series.data.columns
    
    def test_get_index_data(self, stooq_extractor, date_range):
        """Test downloading index data from Stooq."""
        start_date, end_date = date_range
        
        price_series = stooq_extractor.get_index_data(
            "^SPX",
            start_date,
            end_date
        )
        
        assert isinstance(price_series, PriceSeries)
        assert price_series.symbol == "^SPX"
        assert price_series.asset_type == "index"
        assert len(price_series) > 0
    
    def test_get_bond_data(self, stooq_extractor, date_range):
        """Test downloading bond data from Stooq."""
        start_date, end_date = date_range
        
        price_series = stooq_extractor.get_bond_data(
            "10USY.B",
            start_date,
            end_date
        )
        
        assert isinstance(price_series, PriceSeries)
        assert price_series.symbol == "10USY.B"
        assert price_series.asset_type == "bond"
        assert len(price_series) > 0
    
    def test_get_crypto_data(self, stooq_extractor, date_range):
        """Test downloading crypto data from Stooq."""
        start_date, end_date = date_range
        
        price_series = stooq_extractor.get_crypto_data(
            "BTC",
            start_date,
            end_date
        )
        
        assert isinstance(price_series, PriceSeries)
        assert "BTC" in price_series.symbol
        assert ".USD" in price_series.symbol
        assert price_series.asset_type == "crypto"
        assert len(price_series) > 0
    
    def test_determine_asset_type(self, stooq_extractor):
        """Test asset type determination."""
        assert stooq_extractor._determine_asset_type("^SPX") == "index"
        assert stooq_extractor._determine_asset_type("AAPL.US") == "stock"
        assert stooq_extractor._determine_asset_type("BTC.USD") == "crypto"
        assert stooq_extractor._determine_asset_type("10USY.B") == "bond"
    
    def test_get_currency_from_symbol(self, stooq_extractor):
        """Test currency extraction from symbol."""
        assert stooq_extractor._get_currency_from_symbol("AAPL.US") == "USD"
        assert stooq_extractor._get_currency_from_symbol("BTC.USD") == "USD"
        assert stooq_extractor._get_currency_from_symbol("^SPX") == "USD"
        assert stooq_extractor._get_currency_from_symbol("10USY.B") == "USD"
    
    def test_get_exchange_from_symbol(self, stooq_extractor):
        """Test exchange extraction from symbol."""
        assert stooq_extractor._get_exchange_from_symbol("AAPL.US") == "US"
        assert stooq_extractor._get_exchange_from_symbol("^SPX") == "INDEX"
        assert stooq_extractor._get_exchange_from_symbol("10USY.B") == "BOND"
    
    def test_invalid_symbol(self, stooq_extractor, date_range):
        """Test handling of invalid symbol."""
        start_date, end_date = date_range
        
        with pytest.raises(Exception):
            stooq_extractor.get_historical_prices(
                "INVALID_SYMBOL_12345",
                start_date,
                end_date
            )


# ============================================================================
# Comparison Tests
# ============================================================================

class TestExtractorComparison:
    """Tests comparing data from different extractors."""
    
    def test_data_standardization(self, yahoo_extractor, stooq_extractor, date_range):
        """Test that data from different sources is standardized."""
        start_date, end_date = date_range
        
        # Get same stock from both sources
        yahoo_data = yahoo_extractor.get_historical_prices("AAPL", start_date, end_date)
        stooq_data = stooq_extractor.get_us_stock_data("AAPL", start_date, end_date)
        
        # Both should have same columns
        assert set(yahoo_data.data.columns) == set(stooq_data.data.columns)
        
        # Both should be PriceSeries
        assert isinstance(yahoo_data, PriceSeries)
        assert isinstance(stooq_data, PriceSeries)
        
        # Both should have similar number of records (within 10%)
        ratio = len(yahoo_data) / len(stooq_data)
        assert 0.9 <= ratio <= 1.1
    
    def test_price_correlation(self, yahoo_extractor, stooq_extractor, date_range):
        """Test that prices from different sources are highly correlated."""
        start_date, end_date = date_range
        
        # Get same stock from both sources
        yahoo_data = yahoo_extractor.get_historical_prices("AAPL", start_date, end_date)
        stooq_data = stooq_extractor.get_us_stock_data("AAPL", start_date, end_date)
        
        # Align dates
        yahoo_df = yahoo_data.data.set_index('date')
        stooq_df = stooq_data.data.set_index('date')
        
        # Find common dates
        common_dates = yahoo_df.index.intersection(stooq_df.index)
        
        if len(common_dates) > 10:  # Need enough data points
            yahoo_prices = yahoo_df.loc[common_dates, 'close']
            stooq_prices = stooq_df.loc[common_dates, 'close']
            
            # Calculate correlation
            correlation = yahoo_prices.corr(stooq_prices)
            
            # Prices should be highly correlated (> 0.95)
            assert correlation > 0.95, f"Correlation too low: {correlation}"


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_future_dates(self, yahoo_extractor):
        """Test handling of future dates."""
        start_date = datetime.now() + timedelta(days=30)
        end_date = datetime.now() + timedelta(days=60)
        
        with pytest.raises(Exception):
            yahoo_extractor.get_historical_prices("AAPL", start_date, end_date)
    
    def test_invalid_date_range(self, yahoo_extractor):
        """Test handling of invalid date range (end before start)."""
        start_date = datetime.now()
        end_date = datetime.now() - timedelta(days=30)
        
        with pytest.raises(Exception):
            yahoo_extractor.get_historical_prices("AAPL", start_date, end_date)
    
    def test_very_old_dates(self, yahoo_extractor):
        """Test handling of very old dates."""
        start_date = datetime(1990, 1, 1)
        end_date = datetime(1990, 12, 31)
        
        # Should work for AAPL (founded 1980)
        price_series = yahoo_extractor.get_historical_prices("AAPL", start_date, end_date)
        assert len(price_series) > 0
    
    def test_empty_symbol_list(self, yahoo_extractor, date_range):
        """Test handling of empty symbol list."""
        start_date, end_date = date_range
        
        results = yahoo_extractor.get_multiple_series(
            [],
            start_date,
            end_date,
            show_progress=False
        )
        
        assert isinstance(results, dict)
        assert len(results) == 0
    
    def test_single_day_range(self, yahoo_extractor):
        """Test downloading data for a single day."""
        date = datetime(2023, 1, 3)  # A trading day
        
        price_series = yahoo_extractor.get_historical_prices(
            "AAPL",
            date,
            date + timedelta(days=1)
        )
        
        # Should have at least 1 record
        assert len(price_series) >= 1


# ============================================================================
# Performance Tests
# ============================================================================

class TestPerformance:
    """Tests for performance and concurrency."""
    
    @pytest.mark.slow
    def test_concurrent_downloads(self, yahoo_extractor, date_range):
        """Test concurrent downloading performance."""
        start_date, end_date = date_range
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "AMD"]
        
        import time
        start_time = time.time()
        
        results = yahoo_extractor.get_multiple_series(
            symbols,
            start_date,
            end_date,
            show_progress=False
        )
        
        elapsed_time = time.time() - start_time
        
        # Should complete in reasonable time (< 30 seconds for 8 symbols)
        assert elapsed_time < 30
        
        # Should successfully download most symbols
        assert len(results) >= len(symbols) * 0.75  # At least 75% success rate
    
    def test_max_workers_setting(self):
        """Test that max_workers setting is respected."""
        extractor_1 = YahooFinanceExtractor(max_workers=1)
        extractor_5 = YahooFinanceExtractor(max_workers=5)
        
        assert extractor_1.max_workers == 1
        assert extractor_5.max_workers == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
