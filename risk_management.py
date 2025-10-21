"""
Risk management module with stop-loss, take-profit, and bailout logic.
"""
from config import Config
from trading_modes import MarketMode


class RiskManager:
    """Manages risk for trading positions."""
    
    def __init__(self):
        """Initialize risk manager."""
        self.stop_loss_percent = Config.STOP_LOSS_PERCENT
        self.take_profit_percent = Config.TAKE_PROFIT_PERCENT
    
    def check_stop_loss(self, position, current_price):
        """
        Check if stop loss is triggered.
        
        Args:
            position: Dict with position details (entry_price, side, qty)
            current_price: Current market price
            
        Returns:
            tuple: (should_close, reason)
        """
        entry_price = position['entry_price']
        side = position['side']
        
        if side == 'long':
            loss_percent = (entry_price - current_price) / entry_price
            if loss_percent >= self.stop_loss_percent:
                return True, f"stop_loss_triggered_{loss_percent:.2%}"
        
        elif side == 'short':
            loss_percent = (current_price - entry_price) / entry_price
            if loss_percent >= self.stop_loss_percent:
                return True, f"stop_loss_triggered_{loss_percent:.2%}"
        
        return False, None
    
    def check_take_profit(self, position, current_price):
        """
        Check if take profit is triggered.
        
        Args:
            position: Dict with position details
            current_price: Current market price
            
        Returns:
            tuple: (should_close, reason)
        """
        entry_price = position['entry_price']
        side = position['side']
        
        if side == 'long':
            profit_percent = (current_price - entry_price) / entry_price
            if profit_percent >= self.take_profit_percent:
                return True, f"take_profit_triggered_{profit_percent:.2%}"
        
        elif side == 'short':
            profit_percent = (entry_price - current_price) / entry_price
            if profit_percent >= self.take_profit_percent:
                return True, f"take_profit_triggered_{profit_percent:.2%}"
        
        return False, None
    
    def check_bailout(self, position, market_conditions, current_mode):
        """
        Check if bailout is needed due to adverse conditions.
        
        Args:
            position: Dict with position details
            market_conditions: Current market conditions
            current_mode: Current trading mode
            
        Returns:
            tuple: (should_bailout, reason)
        """
        side = position['side']
        volatility = market_conditions['volatility']
        trend_strength = market_conditions['trend_strength']
        sentiment = market_conditions['sentiment']
        
        # Extreme volatility spike
        if volatility > 0.5:
            return True, "extreme_volatility_spike"
        
        # Long position bailouts
        if side == 'long':
            # Strong bearish reversal
            if trend_strength < -0.5 and sentiment < -0.5:
                return True, "strong_bearish_reversal"
            
            # Mode transition to bear with long position
            if current_mode == MarketMode.BEAR and trend_strength < -0.3:
                return True, "bear_mode_transition"
        
        # Short position bailouts
        elif side == 'short':
            # Strong bullish reversal
            if trend_strength > 0.5 and sentiment > 0.5:
                return True, "strong_bullish_reversal"
            
            # Mode transition to bull with short position
            if current_mode == MarketMode.BULL and trend_strength > 0.3:
                return True, "bull_mode_transition"
        
        return False, None
    
    def should_close_position(self, position, current_price, market_conditions, current_mode):
        """
        Comprehensive position closure check.
        
        Args:
            position: Position details
            current_price: Current market price
            market_conditions: Market conditions
            current_mode: Current trading mode
            
        Returns:
            tuple: (should_close, reason)
        """
        # Check stop loss first (highest priority)
        should_close, reason = self.check_stop_loss(position, current_price)
        if should_close:
            return True, reason
        
        # Check take profit
        should_close, reason = self.check_take_profit(position, current_price)
        if should_close:
            return True, reason
        
        # Check bailout conditions
        should_close, reason = self.check_bailout(position, market_conditions, current_mode)
        if should_close:
            return True, reason
        
        return False, None
    
    def calculate_position_size(self, mode, market_conditions, account_value):
        """
        Calculate appropriate position size based on risk.
        
        Args:
            mode: Current trading mode
            market_conditions: Market conditions
            account_value: Total account value
            
        Returns:
            float: Position size in dollars
        """
        base_size = min(Config.POSITION_SIZE, account_value * 0.1)
        
        # Adjust for volatility
        volatility = market_conditions['volatility']
        if volatility > 0.3:
            base_size *= 0.7
        elif volatility > 0.25:
            base_size *= 0.85
        
        # Adjust for mode
        if mode == MarketMode.BEAR:
            base_size *= 0.6
        elif mode == MarketMode.VOLATILE:
            base_size *= 0.75
        
        return base_size
    
    def validate_trade(self, side, quantity, price, account_value):
        """
        Validate if trade is within risk parameters.
        
        Args:
            side: 'long' or 'short'
            quantity: Number of shares
            price: Entry price
            account_value: Total account value
            
        Returns:
            tuple: (is_valid, reason)
        """
        trade_value = quantity * price
        
        # Check if trade size is reasonable
        if trade_value > account_value * 0.2:
            return False, "trade_size_exceeds_20_percent_of_account"
        
        if trade_value < 100:
            return False, "trade_size_too_small"
        
        # Check if sufficient buying power
        required_buying_power = trade_value * 1.1  # 10% buffer
        if required_buying_power > account_value:
            return False, "insufficient_buying_power"
        
        return True, "trade_validated"
