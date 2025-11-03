"""
Base extractor class defining the interface for all data extractors.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from loguru import logger

from src.models.price_series import PriceSeries


class BaseExtractor(ABC):
    """
    Abstract base class for financial data extractors.
    
    All extractors must implement the core methods to ensure standardized output
    regardless of the data source.
    """
    
    def __init__(self, api_key: Optional[str] = None, max_workers: int = 5):
        """
        Initialize the extractor.
        
        Args:
            api_key: API key if required by the source
            max_workers: Maximum number of concurrent requests
        """
        self.api_key = api_key
        self.max_workers = max_workers
        self.source_name = self.__class__.__name__.replace('Extractor', '').lower()
        logger.info(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def get_historical_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> PriceSeries:
        """
        Get historical price data for a single symbol.
        
        Args:
            symbol: Ticker symbol
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval ('1d', '1h', etc.)
        
        Returns:
            PriceSeries object with standardized data
        """
        pass
    
    @abstractmethod
    def get_index_data(
        self,
        index_symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> PriceSeries:
        """
        Get historical data for a market index.
        
        Args:
            index_symbol: Index symbol (e.g., '^GSPC' for S&P 500)
            start_date: Start date for data
            end_date: End date for data
        
        Returns:
            PriceSeries object with standardized data
        """
        pass
    
    def get_multiple_series(
        self,
        symbols: List[str],
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d",
        show_progress: bool = True
    ) -> Dict[str, PriceSeries]:
        """
        Get historical data for multiple symbols concurrently.
        
        Args:
            symbols: List of ticker symbols
            start_date: Start date for data
            end_date: End date for data
            interval: Data interval
            show_progress: Show progress bar
        
        Returns:
            Dictionary mapping symbols to PriceSeries objects
        """
        logger.info(f"Fetching data for {len(symbols)} symbols concurrently")
        
        results = {}
        failed = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(
                    self.get_historical_prices,
                    symbol,
                    start_date,
                    end_date,
                    interval
                ): symbol
                for symbol in symbols
            }
            
            # Process completed tasks with progress bar
            iterator = as_completed(future_to_symbol)
            if show_progress:
                iterator = tqdm(iterator, total=len(symbols), desc="Downloading")
            
            for future in iterator:
                symbol = future_to_symbol[future]
                try:
                    results[symbol] = future.result()
                except Exception as e:
                    logger.error(f"Failed to fetch {symbol}: {str(e)}")
                    failed.append(symbol)
        
        if failed:
            logger.warning(f"Failed to fetch {len(failed)} symbols: {failed}")
        
        logger.info(f"Successfully fetched {len(results)}/{len(symbols)} symbols")
        return results
    
    @abstractmethod
    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        """
        Search for symbols matching a query.
        
        Args:
            query: Search query
        
        Returns:
            List of dictionaries with symbol information
        """
        pass
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Check if a symbol is valid.
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            True if valid, False otherwise
        """
        try:
            # Try to fetch a small amount of recent data
            end_date = datetime.now()
            start_date = datetime(end_date.year, end_date.month, 1)
            self.get_historical_prices(symbol, start_date, end_date)
            return True
        except Exception:
            return False
