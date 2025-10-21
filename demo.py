"""
Demo script to showcase the trading system without live API keys.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from market_analysis import MarketAnalyzer
from trading_modes import ModeSelector, MarketMode
from risk_management import RiskManager


def generate_sample_data(days=60, trend='bull'):
    """Generate sample market data for demonstration."""
    dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
    
    if trend == 'bull':
        # Uptrend with some noise
        base_prices = np.linspace(100, 120, days)
    elif trend == 'bear':
        # Downtrend with some noise
        base_prices = np.linspace(120, 100, days)
    else:  # volatile
        # Sideways with high volatility
        base_prices = 110 + np.random.uniform(-10, 10, days)
    
    # Add noise
    noise = np.random.normal(0, 1, days)
    close_prices = base_prices + noise
    
    data = pd.DataFrame({
        'open': close_prices + np.random.uniform(-0.5, 0.5, days),
        'high': close_prices + np.random.uniform(0.5, 2, days),
        'low': close_prices + np.random.uniform(-2, -0.5, days),
        'close': close_prices,
        'volume': np.random.randint(1000000, 5000000, days)
    }, index=dates)
    
    return data


def demo_market_analysis(trend_type):
    """Demonstrate market analysis on sample data."""
    print(f"\n{'='*60}")
    print(f"DEMO: {trend_type.upper()} MARKET ANALYSIS")
    print(f"{'='*60}")
    
    # Generate sample data
    data = generate_sample_data(days=60, trend=trend_type)
    
    # Analyze market
    analyzer = MarketAnalyzer(data)
    conditions = analyzer.get_market_conditions()
    
    print(f"\nMarket Conditions:")
    print(f"  Current Price: ${conditions['current_price']:.2f}")
    print(f"  Volatility: {conditions['volatility']:.3f}")
    print(f"  Trend Strength: {conditions['trend_strength']:.3f}")
    print(f"  Sentiment: {conditions['sentiment']:.3f}")
    print(f"  RSI: {conditions['rsi']:.2f}" if conditions['rsi'] else "  RSI: N/A")
    print(f"  ADX: {conditions['adx']:.2f}" if conditions['adx'] else "  ADX: N/A")
    
    # Select trading mode
    selected_mode = ModeSelector.select_mode(conditions)
    print(f"\nSelected Trading Mode: {selected_mode.value.upper()}")
    
    # Get strategy
    strategy = ModeSelector.get_strategy(selected_mode, conditions)
    
    # Check entry signals
    should_long = strategy.should_enter_long()
    should_short = strategy.should_enter_short()
    
    print(f"\nTrading Signals:")
    print(f"  Enter Long: {'YES' if should_long else 'NO'}")
    print(f"  Enter Short: {'YES' if should_short else 'NO'}")
    
    # Risk management demo
    if should_long or should_short:
        risk_manager = RiskManager()
        account_value = 10000
        position_size = risk_manager.calculate_position_size(
            selected_mode, conditions, account_value
        )
        
        qty = int(position_size / conditions['current_price'])
        
        print(f"\nPosition Sizing:")
        print(f"  Account Value: ${account_value:,.2f}")
        print(f"  Recommended Position Size: ${position_size:.2f}")
        print(f"  Quantity: {qty} shares")
        
        # Calculate stop loss and take profit
        if should_long:
            stop_loss = conditions['current_price'] * (1 - risk_manager.stop_loss_percent)
            take_profit = conditions['current_price'] * (1 + risk_manager.take_profit_percent)
        else:
            stop_loss = conditions['current_price'] * (1 + risk_manager.stop_loss_percent)
            take_profit = conditions['current_price'] * (1 - risk_manager.take_profit_percent)
        
        print(f"\nRisk Management:")
        print(f"  Entry Price: ${conditions['current_price']:.2f}")
        print(f"  Stop Loss: ${stop_loss:.2f}")
        print(f"  Take Profit: ${take_profit:.2f}")
        
        side = 'long' if should_long else 'short'
        is_valid, reason = risk_manager.validate_trade(
            side, qty, conditions['current_price'], account_value
        )
        print(f"  Trade Validation: {'PASS' if is_valid else 'FAIL'}")
        if not is_valid:
            print(f"    Reason: {reason}")


def demo_mode_transitions():
    """Demonstrate mode transitions with different market conditions."""
    print(f"\n{'='*60}")
    print(f"DEMO: MODE TRANSITION ANALYSIS")
    print(f"{'='*60}")
    
    test_scenarios = [
        {
            'name': 'Strong Bull Market',
            'volatility': 0.1,
            'trend_strength': 0.7,
            'sentiment': 0.5
        },
        {
            'name': 'High Volatility',
            'volatility': 0.35,
            'trend_strength': 0.1,
            'sentiment': 0
        },
        {
            'name': 'Strong Bear Market',
            'volatility': 0.15,
            'trend_strength': -0.7,
            'sentiment': -0.5
        },
        {
            'name': 'Moderate Uptrend',
            'volatility': 0.2,
            'trend_strength': 0.4,
            'sentiment': 0.3
        }
    ]
    
    for scenario in test_scenarios:
        conditions = {
            'volatility': scenario['volatility'],
            'trend_strength': scenario['trend_strength'],
            'sentiment': scenario['sentiment'],
            'current_price': 110,
            'rsi': 50,
            'adx': 30
        }
        
        mode = ModeSelector.select_mode(conditions)
        
        print(f"\nScenario: {scenario['name']}")
        print(f"  Volatility: {conditions['volatility']:.2f}")
        print(f"  Trend: {conditions['trend_strength']:.2f}")
        print(f"  Sentiment: {conditions['sentiment']:.2f}")
        print(f"  → Selected Mode: {mode.value.upper()}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("L3 OPTIONS POC - TRADING SYSTEM DEMONSTRATION")
    print("="*60)
    
    # Demo different market conditions
    demo_market_analysis('bull')
    demo_market_analysis('volatile')
    demo_market_analysis('bear')
    
    # Demo mode transitions
    demo_mode_transitions()
    
    print(f"\n{'='*60}")
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nTo use with real market data:")
    print("1. Set up API keys in .env file")
    print("2. Run: python main.py trade SPY")
    print("3. Or run backtest: python main.py backtest SPY 180")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
