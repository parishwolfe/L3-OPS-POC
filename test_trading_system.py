"""
Tests for the trading system components.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from market_analysis import MarketAnalyzer
from trading_modes import ModeSelector, MarketMode, BullStrategy, VolatileStrategy, BearStrategy
from risk_management import RiskManager
from config import Config


class TestMarketAnalyzer:
    """Test market analysis functionality."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes with data."""
        dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
        data = pd.DataFrame({
            'open': np.random.uniform(100, 110, 50),
            'high': np.random.uniform(110, 120, 50),
            'low': np.random.uniform(90, 100, 50),
            'close': np.random.uniform(100, 110, 50),
            'volume': np.random.randint(1000000, 5000000, 50)
        }, index=dates)
        
        analyzer = MarketAnalyzer(data)
        assert analyzer.data is not None
        assert len(analyzer.data) == 50
    
    def test_calculate_volatility(self):
        """Test volatility calculation."""
        dates = pd.date_range(start='2024-01-01', periods=50, freq='D')
        data = pd.DataFrame({
            'open': np.random.uniform(100, 110, 50),
            'high': np.random.uniform(110, 120, 50),
            'low': np.random.uniform(90, 100, 50),
            'close': np.random.uniform(100, 110, 50),
            'volume': np.random.randint(1000000, 5000000, 50)
        }, index=dates)
        
        analyzer = MarketAnalyzer(data)
        volatility = analyzer.calculate_volatility()
        
        assert isinstance(volatility, float)
        assert 0 <= volatility <= 1
    
    def test_calculate_trend_strength(self):
        """Test trend strength calculation."""
        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        # Create uptrend data
        close_prices = np.linspace(100, 120, 60) + np.random.normal(0, 1, 60)
        data = pd.DataFrame({
            'open': close_prices + np.random.uniform(-1, 1, 60),
            'high': close_prices + np.random.uniform(1, 3, 60),
            'low': close_prices + np.random.uniform(-3, -1, 60),
            'close': close_prices,
            'volume': np.random.randint(1000000, 5000000, 60)
        }, index=dates)
        
        analyzer = MarketAnalyzer(data)
        trend_strength = analyzer.calculate_trend_strength()
        
        assert isinstance(trend_strength, float)
        assert -1 <= trend_strength <= 1
    
    def test_calculate_sentiment(self):
        """Test sentiment calculation."""
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        data = pd.DataFrame({
            'open': np.random.uniform(100, 110, 30),
            'high': np.random.uniform(110, 120, 30),
            'low': np.random.uniform(90, 100, 30),
            'close': np.random.uniform(100, 110, 30),
            'volume': np.random.randint(1000000, 5000000, 30)
        }, index=dates)
        
        analyzer = MarketAnalyzer(data)
        sentiment = analyzer.calculate_sentiment()
        
        assert isinstance(sentiment, float)
        assert -1 <= sentiment <= 1
    
    def test_get_market_conditions(self):
        """Test getting comprehensive market conditions."""
        dates = pd.date_range(start='2024-01-01', periods=60, freq='D')
        data = pd.DataFrame({
            'open': np.random.uniform(100, 110, 60),
            'high': np.random.uniform(110, 120, 60),
            'low': np.random.uniform(90, 100, 60),
            'close': np.random.uniform(100, 110, 60),
            'volume': np.random.randint(1000000, 5000000, 60)
        }, index=dates)
        
        analyzer = MarketAnalyzer(data)
        conditions = analyzer.get_market_conditions()
        
        assert 'volatility' in conditions
        assert 'trend_strength' in conditions
        assert 'sentiment' in conditions
        assert 'current_price' in conditions


class TestModeSelector:
    """Test trading mode selection."""
    
    def test_select_bull_mode(self):
        """Test selection of bull mode."""
        conditions = {
            'volatility': 0.1,
            'trend_strength': 0.7,
            'sentiment': 0.5
        }
        
        mode = ModeSelector.select_mode(conditions)
        assert mode == MarketMode.BULL
    
    def test_select_bear_mode(self):
        """Test selection of bear mode."""
        conditions = {
            'volatility': 0.1,
            'trend_strength': -0.7,
            'sentiment': -0.5
        }
        
        mode = ModeSelector.select_mode(conditions)
        assert mode == MarketMode.BEAR
    
    def test_select_volatile_mode(self):
        """Test selection of volatile mode."""
        conditions = {
            'volatility': 0.3,
            'trend_strength': 0.2,
            'sentiment': 0.1
        }
        
        mode = ModeSelector.select_mode(conditions)
        assert mode == MarketMode.VOLATILE
    
    def test_get_strategy(self):
        """Test getting strategy for mode."""
        conditions = {
            'volatility': 0.1,
            'trend_strength': 0.7,
            'sentiment': 0.5,
            'rsi': 50
        }
        
        strategy = ModeSelector.get_strategy(MarketMode.BULL, conditions)
        assert isinstance(strategy, BullStrategy)
        
        strategy = ModeSelector.get_strategy(MarketMode.VOLATILE, conditions)
        assert isinstance(strategy, VolatileStrategy)
        
        strategy = ModeSelector.get_strategy(MarketMode.BEAR, conditions)
        assert isinstance(strategy, BearStrategy)


class TestTradingStrategies:
    """Test trading strategy implementations."""
    
    def test_bull_strategy_enter_long(self):
        """Test bull strategy long entry."""
        conditions = {
            'volatility': 0.1,
            'trend_strength': 0.5,
            'sentiment': 0.3,
            'rsi': 60
        }
        
        strategy = BullStrategy(conditions)
        assert strategy.should_enter_long() == True
    
    def test_bear_strategy_enter_short(self):
        """Test bear strategy short entry."""
        conditions = {
            'volatility': 0.1,
            'trend_strength': -0.5,
            'sentiment': -0.3,
            'rsi': 40
        }
        
        strategy = BearStrategy(conditions)
        assert strategy.should_enter_short() == True
    
    def test_volatile_strategy_mean_reversion(self):
        """Test volatile strategy mean reversion."""
        conditions = {
            'volatility': 0.3,
            'trend_strength': 0.1,
            'sentiment': -0.6,
            'rsi': 25
        }
        
        strategy = VolatileStrategy(conditions)
        assert strategy.should_enter_long() == True


class TestRiskManager:
    """Test risk management functionality."""
    
    def test_stop_loss_long(self):
        """Test stop loss for long position."""
        risk_manager = RiskManager()
        position = {
            'side': 'long',
            'entry_price': 100,
            'qty': 10
        }
        
        # Price drops below stop loss
        current_price = 97
        should_close, reason = risk_manager.check_stop_loss(position, current_price)
        assert should_close == True
        assert 'stop_loss' in reason
    
    def test_stop_loss_short(self):
        """Test stop loss for short position."""
        risk_manager = RiskManager()
        position = {
            'side': 'short',
            'entry_price': 100,
            'qty': 10
        }
        
        # Price rises above stop loss
        current_price = 103
        should_close, reason = risk_manager.check_stop_loss(position, current_price)
        assert should_close == True
        assert 'stop_loss' in reason
    
    def test_take_profit_long(self):
        """Test take profit for long position."""
        risk_manager = RiskManager()
        position = {
            'side': 'long',
            'entry_price': 100,
            'qty': 10
        }
        
        # Price rises to take profit
        current_price = 106
        should_close, reason = risk_manager.check_take_profit(position, current_price)
        assert should_close == True
        assert 'take_profit' in reason
    
    def test_bailout_extreme_volatility(self):
        """Test bailout on extreme volatility."""
        risk_manager = RiskManager()
        position = {
            'side': 'long',
            'entry_price': 100,
            'qty': 10
        }
        
        market_conditions = {
            'volatility': 0.6,
            'trend_strength': 0.1,
            'sentiment': 0
        }
        
        should_bailout, reason = risk_manager.check_bailout(
            position, market_conditions, MarketMode.BULL
        )
        assert should_bailout == True
        assert 'volatility' in reason
    
    def test_validate_trade(self):
        """Test trade validation."""
        risk_manager = RiskManager()
        
        # Valid trade
        is_valid, reason = risk_manager.validate_trade(
            'long', 10, 100, 10000
        )
        assert is_valid == True
        
        # Trade too large
        is_valid, reason = risk_manager.validate_trade(
            'long', 100, 100, 10000
        )
        assert is_valid == False
    
    def test_calculate_position_size(self):
        """Test position size calculation."""
        risk_manager = RiskManager()
        
        market_conditions = {
            'volatility': 0.2,
            'trend_strength': 0.3
        }
        
        position_size = risk_manager.calculate_position_size(
            MarketMode.BULL, market_conditions, 10000
        )
        
        assert isinstance(position_size, float)
        assert position_size > 0
        assert position_size <= 1000  # Should not exceed base size


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
