"""
Backtesting framework for strategy evaluation.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from market_data import MarketDataProvider
from market_analysis import MarketAnalyzer
from trading_modes import ModeSelector
from risk_management import RiskManager
from config import Config


class BacktestEngine:
    """Backtesting engine for strategy evaluation."""
    
    def __init__(self, initial_capital=10000):
        """
        Initialize backtesting engine.
        
        Args:
            initial_capital: Starting capital for backtest
        """
        self.initial_capital = initial_capital
        self.data_provider = MarketDataProvider()
        self.risk_manager = RiskManager()
    
    def run_backtest(self, symbol, days=180):
        """
        Run backtest on historical data.
        
        Args:
            symbol: Symbol to backtest
            days: Number of days of historical data
            
        Returns:
            dict: Backtest results with performance metrics
        """
        print(f"Running backtest for {symbol} over {days} days...")
        
        # Get historical data
        historical_data = self.data_provider.get_historical_data(symbol, days=days)
        if historical_data.empty:
            return {'error': 'No historical data available'}
        
        # Initialize tracking variables
        capital = self.initial_capital
        position = None
        trades = []
        equity_curve = []
        
        # Run through historical data day by day
        lookback_period = 60
        for i in range(lookback_period, len(historical_data)):
            # Get data up to current day
            current_data = historical_data.iloc[:i+1]
            current_date = current_data.index[-1]
            current_price = current_data['close'].iloc[-1]
            
            # Analyze market
            analyzer = MarketAnalyzer(current_data)
            market_conditions = analyzer.get_market_conditions()
            
            # Select mode and strategy
            selected_mode = ModeSelector.select_mode(market_conditions)
            strategy = ModeSelector.get_strategy(selected_mode, market_conditions)
            
            # Check existing position
            if position:
                # Update position value
                if position['side'] == 'long':
                    position['current_value'] = position['qty'] * current_price
                    position['pl'] = position['current_value'] - position['entry_value']
                else:  # short
                    position['current_value'] = position['qty'] * current_price
                    position['pl'] = position['entry_value'] - position['current_value']
                
                # Check if should exit
                should_exit, exit_reason = strategy.should_exit(position)
                
                # Check risk management
                should_close, risk_reason = self.risk_manager.should_close_position(
                    position, current_price, market_conditions, selected_mode
                )
                
                if should_exit or should_close:
                    # Close position
                    exit_reason = exit_reason or risk_reason
                    trade = self._close_position(
                        position, current_price, current_date, exit_reason
                    )
                    trades.append(trade)
                    
                    # Update capital
                    capital += trade['pl']
                    position = None
            
            # No position, check if should enter
            else:
                # Check for long entry
                if strategy.should_enter_long():
                    position_size = self.risk_manager.calculate_position_size(
                        selected_mode, market_conditions, capital
                    )
                    position_size = min(position_size, capital * 0.95)
                    qty = int(position_size / current_price)
                    
                    if qty > 0:
                        position = self._open_position(
                            'long', symbol, qty, current_price, current_date, selected_mode
                        )
                        capital -= position['entry_value']
                
                # Check for short entry
                elif strategy.should_enter_short():
                    position_size = self.risk_manager.calculate_position_size(
                        selected_mode, market_conditions, capital
                    )
                    position_size = min(position_size, capital * 0.95)
                    qty = int(position_size / current_price)
                    
                    if qty > 0:
                        position = self._open_position(
                            'short', symbol, qty, current_price, current_date, selected_mode
                        )
                        capital -= position['entry_value']
            
            # Record equity
            total_equity = capital
            if position:
                total_equity += position.get('current_value', position['entry_value'])
            
            equity_curve.append({
                'date': current_date,
                'equity': total_equity,
                'mode': selected_mode.value
            })
        
        # Close any remaining position
        if position:
            final_price = historical_data['close'].iloc[-1]
            final_date = historical_data.index[-1]
            trade = self._close_position(position, final_price, final_date, "backtest_end")
            trades.append(trade)
            capital += trade['pl']
        
        # Calculate performance metrics
        results = self._calculate_metrics(
            trades, equity_curve, self.initial_capital, capital
        )
        
        return results
    
    def _open_position(self, side, symbol, qty, price, date, mode):
        """Open a new position."""
        return {
            'side': side,
            'symbol': symbol,
            'qty': qty,
            'entry_price': price,
            'entry_value': qty * price,
            'entry_date': date,
            'mode': mode.value,
            'current_value': qty * price,
            'pl': 0
        }
    
    def _close_position(self, position, exit_price, exit_date, reason):
        """Close a position and create trade record."""
        if position['side'] == 'long':
            pl = (exit_price - position['entry_price']) * position['qty']
            pl_percent = (exit_price - position['entry_price']) / position['entry_price']
        else:  # short
            pl = (position['entry_price'] - exit_price) * position['qty']
            pl_percent = (position['entry_price'] - exit_price) / position['entry_price']
        
        return {
            'symbol': position['symbol'],
            'side': position['side'],
            'entry_date': position['entry_date'],
            'exit_date': exit_date,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'qty': position['qty'],
            'pl': pl,
            'pl_percent': pl_percent,
            'exit_reason': reason,
            'mode': position['mode']
        }
    
    def _calculate_metrics(self, trades, equity_curve, initial_capital, final_capital):
        """Calculate performance metrics."""
        if not trades:
            return {
                'total_trades': 0,
                'initial_capital': initial_capital,
                'final_capital': final_capital,
                'total_return': 0,
                'total_return_percent': 0
            }
        
        trades_df = pd.DataFrame(trades)
        equity_df = pd.DataFrame(equity_curve)
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = trades_df[trades_df['pl'] > 0]
        losing_trades = trades_df[trades_df['pl'] < 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        # Returns
        total_return = final_capital - initial_capital
        total_return_percent = (final_capital - initial_capital) / initial_capital
        
        # Win/Loss stats
        avg_win = winning_trades['pl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pl'].mean() if len(losing_trades) > 0 else 0
        
        # Risk metrics
        equity_df['returns'] = equity_df['equity'].pct_change()
        sharpe_ratio = self._calculate_sharpe_ratio(equity_df['returns'])
        max_drawdown = self._calculate_max_drawdown(equity_df['equity'])
        
        # Mode distribution
        mode_counts = trades_df['mode'].value_counts().to_dict()
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'initial_capital': initial_capital,
            'final_capital': final_capital,
            'total_return': total_return,
            'total_return_percent': total_return_percent,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else float('inf'),
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_percent': max_drawdown / initial_capital,
            'mode_distribution': mode_counts,
            'equity_curve': equity_curve,
            'trades': trades
        }
    
    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        """Calculate Sharpe ratio."""
        if returns.empty or returns.std() == 0:
            return 0
        
        excess_returns = returns.mean() - risk_free_rate / 252
        return (excess_returns / returns.std()) * np.sqrt(252)
    
    def _calculate_max_drawdown(self, equity_curve):
        """Calculate maximum drawdown."""
        if len(equity_curve) == 0:
            return 0
        
        peak = equity_curve.expanding(min_periods=1).max()
        drawdown = equity_curve - peak
        max_drawdown = drawdown.min()
        
        return abs(max_drawdown)
    
    def print_results(self, results):
        """Print backtest results in a formatted way."""
        if 'error' in results:
            print(f"Error: {results['error']}")
            return
        
        print("\n" + "="*50)
        print("BACKTEST RESULTS")
        print("="*50)
        print(f"Initial Capital: ${results['initial_capital']:,.2f}")
        print(f"Final Capital: ${results['final_capital']:,.2f}")
        print(f"Total Return: ${results['total_return']:,.2f} ({results['total_return_percent']:.2%})")
        print(f"\nTotal Trades: {results['total_trades']}")
        print(f"Winning Trades: {results['winning_trades']}")
        print(f"Losing Trades: {results['losing_trades']}")
        print(f"Win Rate: {results['win_rate']:.2%}")
        print(f"\nAverage Win: ${results['avg_win']:,.2f}")
        print(f"Average Loss: ${results['avg_loss']:,.2f}")
        print(f"Profit Factor: {results['profit_factor']:.2f}")
        print(f"\nSharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: ${results['max_drawdown']:,.2f} ({results['max_drawdown_percent']:.2%})")
        print(f"\nMode Distribution:")
        for mode, count in results['mode_distribution'].items():
            print(f"  {mode}: {count} trades")
        print("="*50)
