"""
Yahoo Finance data extractor.
"""

from datetime import datetime
from typing import List, Dict
import pandas as pd
import yfinance as yf
from loguru import logger

from src.extractors.base import BaseExtractor
from src.models.price_series import PriceSeries


class YahooFinanceExtractor(BaseExtractor):
    """
    Extractor for Yahoo Finance data.
    
    Yahoo Finance provides free access to historical stock, index, and ETF data.
    No API key required.
    """
    
    def __init__(self, max_workers: int = 5):
        """Initialize Yahoo Finance extractor."""
        super().__init__(api_key=None, max_workers=max_workers)
    
    def get_historical_prices(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        interval: str = "1d"
    ) -> PriceSeries:
        """
        Get historical price data from Yahoo Finance.
        
        Args:
            symbol: Ticker symbol (e.g., 'AAPL', 'MSFT')
            start_date: Start date
            end_date: End date
            interval: Data interval ('1d', '1h', '1wk', '1mo')
        
        Returns:
            PriceSeries with standardized data
        """
        try:
            logger.debug(f"Fetching {symbol} from Yahoo Finance")
            
            # Download data using yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(
                start=start_date,
                end=end_date,
                interval=interval,
                auto_adjust=False
            )
            
            if df.empty:
                raise ValueError(f"No data returned for {symbol}")
            
            # Standardize column names and format
            df = df.reset_index()
            df.columns = [col.lower().replace(' ', '_') for col in df.columns]
            
            # Rename columns to match our standard
            column_mapping = {
                'date': 'date',
                'open': 'open',
                'high': 'high',
                'low': 'low',
                'close': 'close',
                'volume': 'volume',
                'adj_close': 'adjusted_close'
            }
            
            df = df.rename(columns=column_mapping)
            
            # Get ticker info for metadata
            info = ticker.info
            name = info.get('longName', symbol)
            asset_type = self._determine_asset_type(symbol, info)
            currency = info.get('currency', 'USD')
            
            # Create PriceSeries
            price_series = PriceSeries(
                symbol=symbol,
                name=name,
                data=df[['date', 'open', 'high', 'low', 'close', 'volume', 'adjusted_close']],
                source='yahoo_finance',
                asset_type=asset_type,
                currency=currency,
                metadata={
                    'interval': interval,
                    'exchange': info.get('exchange', 'Unknown'),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A')
                }
            )
            
            logger.debug(f"Successfully fetched {len(df)} records for {symbol}")
            return price_series
            
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {str(e)}")
            raise
    
    def get_index_data(
        self,
        index_symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> PriceSeries:
        """
        Get historical data for a market index.
        
        Common index symbols:
        - ^GSPC: S&P 500
        - ^DJI: Dow Jones Industrial Average
        - ^IXIC: NASDAQ Composite
        - ^FTSE: FTSE 100
        - ^N225: Nikkei 225
        
        Args:
            index_symbol: Index symbol (typically starts with ^)
            start_date: Start date
            end_date: End date
        
        Returns:
            PriceSeries with index data
        """
        # Ensure index symbol format
        if not index_symbol.startswith('^') and index_symbol not in ['SPY', 'QQQ', 'DIA']:
            logger.warning(f"Index symbol {index_symbol} doesn't start with ^. "
                         f"This might not be an index.")
        
        return self.get_historical_prices(index_symbol, start_date, end_date)
    
    def get_crypto_data(
        self,
        crypto_symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> PriceSeries:
        """
        Get cryptocurrency data.
        
        Args:
            crypto_symbol: Crypto symbol (e.g., 'BTC-USD', 'ETH-USD')
            start_date: Start date
            end_date: End date
        
        Returns:
            PriceSeries with crypto data
        """
        # Ensure proper format
        if '-USD' not in crypto_symbol and '-' not in crypto_symbol:
            crypto_symbol = f"{crypto_symbol}-USD"
        
        return self.get_historical_prices(crypto_symbol, start_date, end_date)
    
    def get_forex_data(
        self,
        base_currency: str,
        quote_currency: str,
        start_date: datetime,
        end_date: datetime
    ) -> PriceSeries:
        """
        Get forex exchange rate data.
        
        Args:
            base_currency: Base currency code (e.g., 'EUR')
            quote_currency: Quote currency code (e.g., 'USD')
            start_date: Start date
            end_date: End date
        
        Returns:
            PriceSeries with forex data
        """
        symbol = f"{base_currency}{quote_currency}=X"
        return self.get_historical_prices(symbol, start_date, end_date)
    
    def search_symbol(self, query: str) -> List[Dict[str, str]]:
        """
        Search for symbols matching a query.
        
        Note: Yahoo Finance doesn't have a direct search API, so this is limited.
        
        Args:
            query: Search query
        
        Returns:
            List of matching symbols with basic info
        """
        try:
            ticker = yf.Ticker(query)
            info = ticker.info
            
            if info:
                return [{
                    'symbol': query.upper(),
                    'name': info.get('longName', 'Unknown'),
                    'type': info.get('quoteType', 'Unknown'),
                    'exchange': info.get('exchange', 'Unknown')
                }]
            return []
            
        except Exception as e:
            logger.error(f"Error searching for {query}: {str(e)}")
            return []
    
    def _determine_asset_type(self, symbol: str, info: Dict) -> str:
        """Determine asset type from symbol and info."""
        quote_type = info.get('quoteType', '').lower()
        
        if symbol.startswith('^'):
            return 'index'
        elif '-USD' in symbol or 'crypto' in quote_type:
            return 'crypto'
        elif '=X' in symbol or quote_type == 'currency':
            return 'forex'
        elif quote_type == 'etf':
            return 'etf'
        else:
            return 'stock'
    
    def get_fundamentals(self, symbol: str) -> Dict:
        """
        Get fundamental data for a symbol.
        
        Args:
            symbol: Ticker symbol
        
        Returns:
            Dictionary with fundamental data
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            fundamentals = {
                'symbol': symbol,
                'name': info.get('longName', 'Unknown'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'dividend_yield': info.get('dividendYield'),
                'beta': info.get('beta'),
                'eps': info.get('trailingEps'),
                'revenue': info.get('totalRevenue'),
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
            }
            
            return fundamentals
            
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {str(e)}")
            raise
