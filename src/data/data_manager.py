from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import yfinance as yf
import ccxt
import redis
import pymongo
from typing import Dict, Any, Optional, List
import pandas_ta as ta
from ..utils.logger import setup_logger
from ..utils.config import Config

logger = setup_logger(__name__)
config = Config()

class DataSource(ABC):
    @abstractmethod
    def fetch_data(self, symbol: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
        pass

class YahooFinanceSource(DataSource):
    def fetch_data(self, symbol: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
        ticker = yf.Ticker(symbol)
        return ticker.history(start=start_date, end=end_date, interval=interval)

class CryptoExchangeSource(DataSource):
    def __init__(self, exchange_id: str = 'binance'):
        self.exchange = getattr(ccxt, exchange_id)()
        
    def fetch_data(self, symbol: str, start_date: str, end_date: str, interval: str) -> pd.DataFrame:
        timeframe = self._convert_interval(interval)
        ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    
    def _convert_interval(self, interval: str) -> str:
        # Convert interval to exchange format
        mapping = {'1m': '1m', '1h': '1h', '1d': '1d', '1w': '1w'}
        return mapping.get(interval, '1d')

class DataManager:
    def __init__(self):
        self.logger = setup_logger(__name__)
        self.config = Config()
        self.cache = self._setup_cache()
        self.sources = {
            'yahoo': YahooFinanceSource(),
            'crypto': CryptoExchangeSource()
        }
        
    def _setup_cache(self) -> None:

        return {}

    def fetch_data(self,
                  symbol: str,
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  interval: str = "1d",
                  source: str = "yahoo") -> pd.DataFrame:

        cache_key = f"{symbol}_{start_date}_{end_date}_{interval}_{source}"
        
        # Try to get from cache
        if self.cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        # Fetch from source
        try:
            data_source = self.sources[source]
            df = data_source.fetch_data(symbol, start_date, end_date, interval)
            df = self._add_indicators(df)
            
            # Cache the data
            if self.cache is not None:
                self.cache[cache_key] = df
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching data: {e}")
            raise
    
    def _add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            # Basic indicators
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            # Bollinger Bands
            rolling_mean = df['Close'].rolling(window=20).mean()
            rolling_std = df['Close'].rolling(window=20).std()
            df['BB_Upper'] = rolling_mean + (rolling_std * 2)
            df['BB_Middle'] = rolling_mean
            df['BB_Lower'] = rolling_mean - (rolling_std * 2)
            
            # ATR
            high_low = df['High'] - df['Low']
            high_close = (df['High'] - df['Close'].shift()).abs()
            low_close = (df['Low'] - df['Close'].shift()).abs()
            ranges = pd.concat([high_low, high_close, low_close], axis=1)
            true_range = ranges.max(axis=1)
            df['ATR'] = true_range.rolling(14).mean()
            
            # MACD
            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = exp1 - exp2
            df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            # OBV (On Balance Volume)
            df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
            
            return df
        except Exception as e:
            self.logger.error(f"Error calculating indicators: {e}")
            raise

    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:

        # Remove duplicates
        df = df[~df.index.duplicated(keep='first')]
        
        # Sort by timestamp
        df.sort_index(inplace=True)
        
        # Forward fill missing values
        df.fillna(method='ffill', inplace=True)
        
        # Remove rows with remaining NaN values
        df.dropna(inplace=True)
        
        return df