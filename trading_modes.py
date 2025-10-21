"""
Trading mode strategies: Bull, Volatile, and Bear market strategies.
"""
from enum import Enum
from config import Config


class MarketMode(Enum):
    """Market mode enumeration."""
    BULL = "bull"
    VOLATILE = "volatile"
    BEAR = "bear"


class TradingStrategy:
    """Base class for trading strategies."""
    
    def __init__(self, market_conditions):
        """
        Initialize strategy with market conditions.
        
        Args:
            market_conditions: Dict with volatility, trend_strength, sentiment
        """
        self.market_conditions = market_conditions
    
    def should_enter_long(self):
        """Determine if should enter long position."""
        raise NotImplementedError
    
    def should_enter_short(self):
        """Determine if should enter short position."""
        raise NotImplementedError
    
    def should_exit(self, position):
        """Determine if should exit current position."""
        raise NotImplementedError
    
    def get_position_size(self):
        """Calculate position size."""
        return Config.POSITION_SIZE


class BullStrategy(TradingStrategy):
    """Bull market strategy - focus on long positions with momentum."""
    
    def should_enter_long(self):
        """Enter long on bullish signals."""
        conditions = self.market_conditions
        
        # Strong uptrend with positive sentiment
        if (conditions['trend_strength'] > 0.3 and
            conditions['sentiment'] > 0.2 and
            conditions.get('rsi', 50) < 70):
            return True
        
        # Oversold bounce in uptrend
        if (conditions['trend_strength'] > 0.1 and
            conditions.get('rsi', 50) < 35):
            return True
        
        return False
    
    def should_enter_short(self):
        """Rarely enter short in bull market."""
        conditions = self.market_conditions
        
        # Only on extreme overbought with reversal signals
        if (conditions.get('rsi', 50) > 80 and
            conditions['sentiment'] < -0.3 and
            conditions['trend_strength'] < 0):
            return True
        
        return False
    
    def should_exit(self, position):
        """Exit on trend reversal or stop loss."""
        conditions = self.market_conditions
        
        if position['side'] == 'long':
            # Exit on bearish reversal
            if conditions['trend_strength'] < -0.2 or conditions['sentiment'] < -0.4:
                return True, "trend_reversal"
            
            # Exit on extreme overbought
            if conditions.get('rsi', 50) > 75:
                return True, "overbought"
        
        elif position['side'] == 'short':
            # Exit short quickly if trend resumes
            if conditions['trend_strength'] > 0.1 or conditions['sentiment'] > 0.2:
                return True, "bullish_resumption"
        
        return False, None


class VolatileStrategy(TradingStrategy):
    """Volatile market strategy - range trading and quick profits."""
    
    def should_enter_long(self):
        """Enter long at support levels."""
        conditions = self.market_conditions
        
        # Oversold with high volatility
        if (conditions.get('rsi', 50) < 30 and
            conditions['volatility'] > Config.VOLATILITY_THRESHOLD_HIGH):
            return True
        
        # Mean reversion from extreme negative sentiment
        if conditions['sentiment'] < -0.5:
            return True
        
        return False
    
    def should_enter_short(self):
        """Enter short at resistance levels."""
        conditions = self.market_conditions
        
        # Overbought with high volatility
        if (conditions.get('rsi', 50) > 70 and
            conditions['volatility'] > Config.VOLATILITY_THRESHOLD_HIGH):
            return True
        
        # Mean reversion from extreme positive sentiment
        if conditions['sentiment'] > 0.5:
            return True
        
        return False
    
    def should_exit(self, position):
        """Quick exits at mean reversion points."""
        conditions = self.market_conditions
        
        if position['side'] == 'long':
            # Exit at neutral or overbought
            if conditions.get('rsi', 50) > 55 or conditions['sentiment'] > 0.1:
                return True, "mean_reversion"
        
        elif position['side'] == 'short':
            # Exit at neutral or oversold
            if conditions.get('rsi', 50) < 45 or conditions['sentiment'] < -0.1:
                return True, "mean_reversion"
        
        return False, None
    
    def get_position_size(self):
        """Smaller position size in volatile markets."""
        return Config.POSITION_SIZE * 0.7


class BearStrategy(TradingStrategy):
    """Bear market strategy - focus on short positions and capital preservation."""
    
    def should_enter_long(self):
        """Rarely enter long in bear market."""
        conditions = self.market_conditions
        
        # Only on extreme oversold with reversal signals
        if (conditions.get('rsi', 50) < 20 and
            conditions['sentiment'] > 0.3 and
            conditions['trend_strength'] > 0):
            return True
        
        return False
    
    def should_enter_short(self):
        """Enter short on bearish signals."""
        conditions = self.market_conditions
        
        # Strong downtrend with negative sentiment
        if (conditions['trend_strength'] < -0.3 and
            conditions['sentiment'] < -0.2 and
            conditions.get('rsi', 50) > 30):
            return True
        
        # Overbought rally in downtrend
        if (conditions['trend_strength'] < -0.1 and
            conditions.get('rsi', 50) > 65):
            return True
        
        return False
    
    def should_exit(self, position):
        """Exit on trend reversal or stop loss."""
        conditions = self.market_conditions
        
        if position['side'] == 'short':
            # Exit on bullish reversal
            if conditions['trend_strength'] > 0.2 or conditions['sentiment'] > 0.4:
                return True, "trend_reversal"
            
            # Exit on extreme oversold
            if conditions.get('rsi', 50) < 25:
                return True, "oversold"
        
        elif position['side'] == 'long':
            # Exit long quickly if downtrend resumes
            if conditions['trend_strength'] < -0.1 or conditions['sentiment'] < -0.2:
                return True, "bearish_resumption"
        
        return False, None
    
    def get_position_size(self):
        """Conservative position sizing in bear markets."""
        return Config.POSITION_SIZE * 0.5


class ModeSelector:
    """Selects appropriate trading mode based on market conditions."""
    
    @staticmethod
    def select_mode(market_conditions):
        """
        Select the appropriate trading mode.
        
        Args:
            market_conditions: Dict with volatility, trend_strength, sentiment
            
        Returns:
            MarketMode: Selected market mode
        """
        volatility = market_conditions['volatility']
        trend_strength = market_conditions['trend_strength']
        
        # High volatility -> Volatile mode
        if volatility > Config.VOLATILITY_THRESHOLD_HIGH:
            return MarketMode.VOLATILE
        
        # Strong bullish trend -> Bull mode
        if trend_strength > Config.TREND_STRENGTH_BULL:
            return MarketMode.BULL
        
        # Strong bearish trend -> Bear mode
        if trend_strength < Config.TREND_STRENGTH_BEAR:
            return MarketMode.BEAR
        
        # Moderate volatility with unclear trend -> Volatile mode
        if volatility > Config.VOLATILITY_THRESHOLD_LOW:
            return MarketMode.VOLATILE
        
        # Default to mode based on trend direction
        if trend_strength > 0:
            return MarketMode.BULL
        else:
            return MarketMode.BEAR
    
    @staticmethod
    def get_strategy(market_mode, market_conditions):
        """
        Get trading strategy for the selected mode.
        
        Args:
            market_mode: MarketMode enum
            market_conditions: Dict with market metrics
            
        Returns:
            TradingStrategy: Strategy instance
        """
        strategies = {
            MarketMode.BULL: BullStrategy,
            MarketMode.VOLATILE: VolatileStrategy,
            MarketMode.BEAR: BearStrategy
        }
        
        strategy_class = strategies.get(market_mode, BullStrategy)
        return strategy_class(market_conditions)
