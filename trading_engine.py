"""
Core trading engine that orchestrates strategy execution and order management.
"""
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from config import Config
from market_data import MarketDataProvider
from market_analysis import MarketAnalyzer
from trading_modes import ModeSelector, MarketMode
from risk_management import RiskManager


class TradingEngine:
    """Main trading engine for executing strategies."""
    
    def __init__(self):
        """Initialize trading engine."""
        self.trading_client = TradingClient(
            Config.ALPACA_API_KEY,
            Config.ALPACA_SECRET_KEY,
            paper=Config.ALPACA_PAPER
        )
        self.data_provider = MarketDataProvider()
        self.risk_manager = RiskManager()
        self.current_mode = None
        self.current_position = None
    
    def get_account_info(self):
        """Get current account information."""
        try:
            account = self.trading_client.get_account()
            return {
                'equity': float(account.equity),
                'cash': float(account.cash),
                'buying_power': float(account.buying_power),
                'portfolio_value': float(account.portfolio_value)
            }
        except Exception as e:
            print(f"Error fetching account info: {e}")
            return None
    
    def get_current_position(self, symbol):
        """Get current position for a symbol."""
        try:
            positions = self.trading_client.get_all_positions()
            for position in positions:
                if position.symbol == symbol:
                    return {
                        'symbol': position.symbol,
                        'qty': float(position.qty),
                        'side': 'long' if float(position.qty) > 0 else 'short',
                        'entry_price': float(position.avg_entry_price),
                        'current_price': float(position.current_price),
                        'market_value': float(position.market_value),
                        'unrealized_pl': float(position.unrealized_pl),
                        'unrealized_plpc': float(position.unrealized_plpc)
                    }
            return None
        except Exception as e:
            print(f"Error fetching position: {e}")
            return None
    
    def place_order(self, symbol, qty, side):
        """
        Place a market order.
        
        Args:
            symbol: Stock/ETF symbol
            qty: Quantity to trade
            side: 'buy' or 'sell'
            
        Returns:
            Order object or None
        """
        try:
            order_side = OrderSide.BUY if side == 'buy' else OrderSide.SELL
            
            request = MarketOrderRequest(
                symbol=symbol,
                qty=qty,
                side=order_side,
                time_in_force=TimeInForce.DAY
            )
            
            order = self.trading_client.submit_order(request)
            print(f"Order placed: {side} {qty} {symbol}")
            return order
        except Exception as e:
            print(f"Error placing order: {e}")
            return None
    
    def close_position(self, symbol, reason="manual"):
        """Close all positions for a symbol."""
        try:
            self.trading_client.close_position(symbol)
            print(f"Position closed for {symbol}: {reason}")
            return True
        except Exception as e:
            print(f"Error closing position: {e}")
            return False
    
    def analyze_and_trade(self, symbol):
        """
        Main trading logic: analyze market and execute trades.
        
        Args:
            symbol: Stock/ETF symbol to trade
            
        Returns:
            dict: Trade execution results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'action': 'none',
            'mode': None,
            'conditions': None,
            'position': None
        }
        
        try:
            # Get market data
            historical_data = self.data_provider.get_historical_data(symbol, days=60)
            if historical_data.empty:
                results['error'] = "No historical data available"
                return results
            
            # Analyze market
            analyzer = MarketAnalyzer(historical_data)
            market_conditions = analyzer.get_market_conditions()
            results['conditions'] = market_conditions
            
            # Select trading mode
            selected_mode = ModeSelector.select_mode(market_conditions)
            self.current_mode = selected_mode
            results['mode'] = selected_mode.value
            
            # Get strategy
            strategy = ModeSelector.get_strategy(selected_mode, market_conditions)
            
            # Get current position
            current_position = self.get_current_position(symbol)
            results['position'] = current_position
            
            # Get account info
            account = self.get_account_info()
            if not account:
                results['error'] = "Could not fetch account info"
                return results
            
            current_price = market_conditions['current_price']
            
            # Check existing position
            if current_position:
                # Check if should exit
                should_exit, exit_reason = strategy.should_exit(current_position)
                
                # Check risk management
                should_close_risk, risk_reason = self.risk_manager.should_close_position(
                    current_position, current_price, market_conditions, selected_mode
                )
                
                if should_exit or should_close_risk:
                    reason = exit_reason or risk_reason
                    if self.close_position(symbol, reason):
                        results['action'] = 'closed'
                        results['reason'] = reason
                        return results
            
            # No position, check if should enter
            else:
                # Check for long entry
                if strategy.should_enter_long():
                    position_size = self.risk_manager.calculate_position_size(
                        selected_mode, market_conditions, account['equity']
                    )
                    qty = int(position_size / current_price)
                    
                    # Validate trade
                    is_valid, reason = self.risk_manager.validate_trade(
                        'long', qty, current_price, account['equity']
                    )
                    
                    if is_valid and qty > 0:
                        order = self.place_order(symbol, qty, 'buy')
                        if order:
                            results['action'] = 'opened_long'
                            results['qty'] = qty
                            results['price'] = current_price
                
                # Check for short entry
                elif strategy.should_enter_short():
                    position_size = self.risk_manager.calculate_position_size(
                        selected_mode, market_conditions, account['equity']
                    )
                    qty = int(position_size / current_price)
                    
                    # Validate trade
                    is_valid, reason = self.risk_manager.validate_trade(
                        'short', qty, current_price, account['equity']
                    )
                    
                    if is_valid and qty > 0:
                        order = self.place_order(symbol, qty, 'sell')
                        if order:
                            results['action'] = 'opened_short'
                            results['qty'] = qty
                            results['price'] = current_price
            
        except Exception as e:
            results['error'] = str(e)
            print(f"Error in analyze_and_trade: {e}")
        
        return results
    
    def run_paper_trading(self, symbol, iterations=1):
        """
        Run paper trading for testing.
        
        Args:
            symbol: Symbol to trade
            iterations: Number of trading cycles
            
        Returns:
            list: Results from each iteration
        """
        results = []
        for i in range(iterations):
            print(f"\n=== Trading Iteration {i+1}/{iterations} ===")
            result = self.analyze_and_trade(symbol)
            results.append(result)
            print(f"Action: {result['action']}")
            print(f"Mode: {result['mode']}")
            if result.get('conditions'):
                print(f"Volatility: {result['conditions']['volatility']:.3f}")
                print(f"Trend: {result['conditions']['trend_strength']:.3f}")
                print(f"Sentiment: {result['conditions']['sentiment']:.3f}")
        
        return results
