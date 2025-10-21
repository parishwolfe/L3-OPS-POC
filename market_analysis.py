"""
Market analysis module for sentiment, volatility, and trend calculations.
"""
import pandas as pd
import numpy as np
from ta.volatility import AverageTrueRange, BollingerBands
from ta.trend import SMAIndicator, EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator


class MarketAnalyzer:
    """Analyzes market conditions for trading decisions."""
    
    def __init__(self, data):
        """
        Initialize analyzer with price data.
        
        Args:
            data: DataFrame with OHLCV data
        """
        self.data = data.copy()
        self._calculate_indicators()
    
    def _calculate_indicators(self):
        """Calculate all technical indicators."""
        if len(self.data) < 2:
            return
        
        # Moving averages
        self.data['sma_20'] = SMAIndicator(
            close=self.data['close'], window=20
        ).sma_indicator()
        
        self.data['sma_50'] = SMAIndicator(
            close=self.data['close'], window=50
        ).sma_indicator()
        
        self.data['ema_12'] = EMAIndicator(
            close=self.data['close'], window=12
        ).ema_indicator()
        
        self.data['ema_26'] = EMAIndicator(
            close=self.data['close'], window=26
        ).ema_indicator()
        
        # MACD
        macd = MACD(close=self.data['close'])
        self.data['macd'] = macd.macd()
        self.data['macd_signal'] = macd.macd_signal()
        self.data['macd_diff'] = macd.macd_diff()
        
        # RSI
        self.data['rsi'] = RSIIndicator(
            close=self.data['close'], window=14
        ).rsi()
        
        # Bollinger Bands
        bb = BollingerBands(close=self.data['close'])
        self.data['bb_upper'] = bb.bollinger_hband()
        self.data['bb_middle'] = bb.bollinger_mavg()
        self.data['bb_lower'] = bb.bollinger_lband()
        
        # ATR for volatility
        self.data['atr'] = AverageTrueRange(
            high=self.data['high'],
            low=self.data['low'],
            close=self.data['close']
        ).average_true_range()
        
        # ADX for trend strength
        adx = ADXIndicator(
            high=self.data['high'],
            low=self.data['low'],
            close=self.data['close']
        )
        self.data['adx'] = adx.adx()
        self.data['adx_pos'] = adx.adx_pos()
        self.data['adx_neg'] = adx.adx_neg()
    
    def calculate_volatility(self):
        """
        Calculate current market volatility.
        
        Returns:
            float: Volatility score (0-1 scale)
        """
        if len(self.data) < 20:
            return 0.5
        
        # Use ATR normalized by price
        recent_data = self.data.tail(20)
        avg_atr = recent_data['atr'].mean()
        avg_close = recent_data['close'].mean()
        
        volatility = avg_atr / avg_close if avg_close > 0 else 0.5
        
        # Also consider Bollinger Band width
        bb_width = (recent_data['bb_upper'] - recent_data['bb_lower']) / recent_data['bb_middle']
        avg_bb_width = bb_width.mean()
        
        # Combine both metrics
        combined_volatility = (volatility + avg_bb_width) / 2
        
        return min(combined_volatility, 1.0)
    
    def calculate_trend_strength(self):
        """
        Calculate trend strength and direction.
        
        Returns:
            float: Trend strength (-1 to 1, negative = bearish, positive = bullish)
        """
        if len(self.data) < 50:
            return 0.0
        
        recent_data = self.data.tail(20)
        
        # ADX shows trend strength
        adx_value = recent_data['adx'].iloc[-1] if not recent_data['adx'].isna().all() else 25
        adx_normalized = min(adx_value / 50, 1.0)
        
        # Direction from ADX +DI and -DI
        adx_pos = recent_data['adx_pos'].iloc[-1] if not recent_data['adx_pos'].isna().all() else 25
        adx_neg = recent_data['adx_neg'].iloc[-1] if not recent_data['adx_neg'].isna().all() else 25
        
        if adx_pos > adx_neg:
            direction = 1
        else:
            direction = -1
        
        # SMA trend
        sma_20 = recent_data['sma_20'].iloc[-1]
        sma_50 = recent_data['sma_50'].iloc[-1]
        
        if not pd.isna(sma_20) and not pd.isna(sma_50):
            sma_trend = 1 if sma_20 > sma_50 else -1
        else:
            sma_trend = direction
        
        # MACD trend
        macd_diff = recent_data['macd_diff'].iloc[-1]
        macd_trend = 1 if macd_diff > 0 else -1 if not pd.isna(macd_diff) else direction
        
        # Combine signals
        trend_direction = np.sign(direction + sma_trend + macd_trend)
        trend_strength = adx_normalized * trend_direction
        
        return trend_strength
    
    def calculate_sentiment(self):
        """
        Calculate market sentiment.
        
        Returns:
            float: Sentiment score (-1 to 1, negative = bearish, positive = bullish)
        """
        if len(self.data) < 14:
            return 0.0
        
        recent_data = self.data.tail(14)
        
        # RSI-based sentiment
        rsi = recent_data['rsi'].iloc[-1]
        if pd.isna(rsi):
            rsi = 50
        
        rsi_sentiment = (rsi - 50) / 50
        
        # Price position relative to Bollinger Bands
        close = recent_data['close'].iloc[-1]
        bb_upper = recent_data['bb_upper'].iloc[-1]
        bb_lower = recent_data['bb_lower'].iloc[-1]
        bb_middle = recent_data['bb_middle'].iloc[-1]
        
        if not pd.isna(bb_upper) and not pd.isna(bb_lower) and bb_upper != bb_lower:
            bb_position = (close - bb_middle) / (bb_upper - bb_lower)
        else:
            bb_position = 0
        
        # MACD sentiment
        macd_diff = recent_data['macd_diff'].iloc[-1]
        macd_sentiment = np.tanh(macd_diff / 10) if not pd.isna(macd_diff) else 0
        
        # Combine sentiments
        sentiment = (rsi_sentiment + bb_position + macd_sentiment) / 3
        
        return np.clip(sentiment, -1, 1)
    
    def get_market_conditions(self):
        """
        Get comprehensive market condition analysis.
        
        Returns:
            dict: Market conditions including volatility, trend, and sentiment
        """
        return {
            'volatility': self.calculate_volatility(),
            'trend_strength': self.calculate_trend_strength(),
            'sentiment': self.calculate_sentiment(),
            'current_price': self.data['close'].iloc[-1],
            'rsi': self.data['rsi'].iloc[-1] if 'rsi' in self.data.columns else None,
            'adx': self.data['adx'].iloc[-1] if 'adx' in self.data.columns else None
        }
