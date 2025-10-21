"""
GCP Cloud Functions entry point for L3 Options POC trading system.
"""
import json
import functions_framework
from config import Config
from trading_engine import TradingEngine
from backtesting import BacktestEngine


@functions_framework.http
def trading_handler(request):
    """
    HTTP Cloud Function for trading operations.
    
    Request JSON format:
    {
        "action": "trade" | "backtest" | "status",
        "symbol": "SPY",
        "days": 180  # for backtest
    }
    
    Args:
        request: Flask request object
        
    Returns:
        JSON response with results
    """
    # Set CORS headers for the response
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'Content-Type',
    }
    
    # Handle preflight request
    if request.method == 'OPTIONS':
        return ('', 204, headers)
    
    try:
        # Validate configuration
        Config.validate()
        
        # Parse request
        request_json = request.get_json(silent=True)
        if not request_json:
            return (
                json.dumps({'error': 'Invalid JSON in request'}),
                400,
                headers
            )
        
        action = request_json.get('action', 'trade')
        symbol = request_json.get('symbol', Config.DEFAULT_SYMBOL)
        
        # Route to appropriate handler
        if action == 'trade':
            result = handle_trade(symbol)
        elif action == 'backtest':
            days = request_json.get('days', 180)
            result = handle_backtest(symbol, days)
        elif action == 'status':
            result = handle_status(symbol)
        else:
            return (
                json.dumps({'error': f'Unknown action: {action}'}),
                400,
                headers
            )
        
        return (json.dumps(result, default=str), 200, headers)
    
    except ValueError as e:
        return (
            json.dumps({'error': f'Configuration error: {str(e)}'}),
            500,
            headers
        )
    except Exception as e:
        return (
            json.dumps({'error': f'Internal error: {str(e)}'}),
            500,
            headers
        )


def handle_trade(symbol):
    """
    Execute trading logic.
    
    Args:
        symbol: Stock/ETF symbol
        
    Returns:
        dict: Trading results
    """
    engine = TradingEngine()
    result = engine.analyze_and_trade(symbol)
    return result


def handle_backtest(symbol, days):
    """
    Run backtest.
    
    Args:
        symbol: Stock/ETF symbol
        days: Number of days to backtest
        
    Returns:
        dict: Backtest results
    """
    backtest = BacktestEngine(initial_capital=10000)
    results = backtest.run_backtest(symbol, days=days)
    
    # Remove detailed trades and equity curve for response size
    if 'trades' in results:
        results['sample_trades'] = results['trades'][:10]  # First 10 trades
        del results['trades']
    
    if 'equity_curve' in results:
        # Sample every 10th point
        results['equity_curve_sample'] = results['equity_curve'][::10]
        del results['equity_curve']
    
    return results


def handle_status(symbol):
    """
    Get current status and account info.
    
    Args:
        symbol: Stock/ETF symbol
        
    Returns:
        dict: Status information
    """
    engine = TradingEngine()
    
    account = engine.get_account_info()
    position = engine.get_current_position(symbol)
    
    return {
        'account': account,
        'position': position,
        'symbol': symbol,
        'paper_trading': Config.ALPACA_PAPER
    }


# For local testing
if __name__ == '__main__':
    import sys
    
    print("L3 Options POC - Trading System")
    print("="*50)
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <action> [symbol] [days]")
        print("Actions: trade, backtest, status")
        sys.exit(1)
    
    action = sys.argv[1]
    symbol = sys.argv[2] if len(sys.argv) > 2 else Config.DEFAULT_SYMBOL
    
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set required environment variables or create .env file")
        sys.exit(1)
    
    if action == 'trade':
        print(f"\nExecuting trade for {symbol}...")
        result = handle_trade(symbol)
        print(json.dumps(result, indent=2, default=str))
    
    elif action == 'backtest':
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 180
        print(f"\nRunning backtest for {symbol} over {days} days...")
        backtest = BacktestEngine(initial_capital=10000)
        results = backtest.run_backtest(symbol, days=days)
        backtest.print_results(results)
    
    elif action == 'status':
        print(f"\nFetching status for {symbol}...")
        result = handle_status(symbol)
        print(json.dumps(result, indent=2, default=str))
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
