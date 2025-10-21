"""
Market data integration module using Alpaca and Alpha Vantage APIs.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpha_vantage.timeseries import TimeSeries
from config import Config


class MarketDataProvider:
    """Provides market data from Alpaca and Alpha Vantage."""
    
    def __init__(self):
        """Initialize market data providers."""
        self.alpaca_client = StockHistoricalDataClient(
            Config.ALPACA_API_KEY,
            Config.ALPACA_SECRET_KEY
        )
        self.alpha_vantage = TimeSeries(
            key=Config.ALPHA_VANTAGE_API_KEY,
            output_format='pandas'
        )
    
    def get_historical_data(self, symbol, days=30):
        """
        Get historical price data for a symbol.
        
        Args:
            symbol: Stock/ETF ticker symbol
            days: Number of days of historical data
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            request = StockBarsRequest(
                symbol_or_symbols=symbol,
                timeframe=TimeFrame.Day,
                start=start_date,
                end=end_date
            )
            
            bars = self.alpaca_client.get_stock_bars(request)
            df = bars.df
            
            if symbol in df.index.get_level_values(0):
                df = df.xs(symbol, level=0)
            
            return df
        except Exception as e:
            print(f"Error fetching historical data from Alpaca: {e}")
            return self._fallback_to_alpha_vantage(symbol)
    
    def _fallback_to_alpha_vantage(self, symbol):
        """Fallback to Alpha Vantage if Alpaca fails."""
        try:
            data, _ = self.alpha_vantage.get_daily(symbol=symbol, outputsize='full')
            data.columns = ['open', 'high', 'low', 'close', 'volume']
            return data.head(30)
        except Exception as e:
            print(f"Error fetching data from Alpha Vantage: {e}")
            return pd.DataFrame()
    
    def get_intraday_data(self, symbol, interval='5min'):
        """
        Get intraday price data.
        
        Args:
            symbol: Stock/ETF ticker symbol
            interval: Time interval (5min, 15min, 30min, 60min)
            
        Returns:
            DataFrame with intraday OHLCV data
        """
        try:
            data, _ = self.alpha_vantage.get_intraday(
                symbol=symbol,
                interval=interval,
                outputsize='full'
            )
            data.columns = ['open', 'high', 'low', 'close', 'volume']
            return data
        except Exception as e:
            print(f"Error fetching intraday data: {e}")
            return pd.DataFrame()
