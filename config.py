"""
Configuration module for L3 Options POC trading system.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration class for trading system settings."""
    
    # Alpaca API Configuration
    ALPACA_API_KEY = os.getenv('ALPACA_API_KEY', '')
    ALPACA_SECRET_KEY = os.getenv('ALPACA_SECRET_KEY', '')
    ALPACA_PAPER = os.getenv('ALPACA_PAPER', 'true').lower() == 'true'
    
    # Alpha Vantage API Configuration
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    
    # Trading Parameters
    DEFAULT_SYMBOL = os.getenv('DEFAULT_SYMBOL', 'SPY')
    POSITION_SIZE = float(os.getenv('POSITION_SIZE', '1000'))
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '0.02'))
    TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '0.05'))
    
    # Market Mode Thresholds
    VOLATILITY_THRESHOLD_HIGH = float(os.getenv('VOLATILITY_THRESHOLD_HIGH', '0.25'))
    VOLATILITY_THRESHOLD_LOW = float(os.getenv('VOLATILITY_THRESHOLD_LOW', '0.15'))
    TREND_STRENGTH_BULL = float(os.getenv('TREND_STRENGTH_BULL', '0.6'))
    TREND_STRENGTH_BEAR = float(os.getenv('TREND_STRENGTH_BEAR', '-0.6'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration parameters."""
        required_fields = [
            ('ALPACA_API_KEY', cls.ALPACA_API_KEY),
            ('ALPACA_SECRET_KEY', cls.ALPACA_SECRET_KEY),
            ('ALPHA_VANTAGE_API_KEY', cls.ALPHA_VANTAGE_API_KEY)
        ]
        
        missing = [field for field, value in required_fields if not value]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        return True
