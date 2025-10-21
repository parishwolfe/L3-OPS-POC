# Usage Examples

## Command Line Examples

### Basic Trading

#### Execute Trade with Default Symbol (SPY)
```bash
python main.py trade
```

#### Execute Trade with Specific Symbol
```bash
python main.py trade QQQ
```

#### Check Account Status
```bash
python main.py status SPY
```

### Backtesting

#### Run Standard Backtest (180 days)
```bash
python main.py backtest SPY
```

#### Run Extended Backtest (1 year)
```bash
python main.py backtest SPY 365
```

#### Run Short Backtest (30 days)
```bash
python main.py backtest SPY 30
```

#### Backtest Different ETFs
```bash
python main.py backtest QQQ 180
python main.py backtest IWM 180
python main.py backtest DIA 180
```

## API Examples

### Using cURL

#### Execute Trade
```bash
curl -X POST https://YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{
    "action": "trade",
    "symbol": "SPY"
  }'
```

#### Run Backtest
```bash
curl -X POST https://YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{
    "action": "backtest",
    "symbol": "SPY",
    "days": 180
  }'
```

#### Check Status
```bash
curl -X POST https://YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{
    "action": "status",
    "symbol": "SPY"
  }'
```

### Using Python Requests

```python
import requests
import json

FUNCTION_URL = "https://YOUR_FUNCTION_URL"

# Execute trade
response = requests.post(
    FUNCTION_URL,
    json={
        "action": "trade",
        "symbol": "SPY"
    }
)
print(json.dumps(response.json(), indent=2))

# Run backtest
response = requests.post(
    FUNCTION_URL,
    json={
        "action": "backtest",
        "symbol": "QQQ",
        "days": 180
    }
)
print(json.dumps(response.json(), indent=2))
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');

const FUNCTION_URL = 'https://YOUR_FUNCTION_URL';

async function executeTrade(symbol) {
    try {
        const response = await axios.post(FUNCTION_URL, {
            action: 'trade',
            symbol: symbol
        });
        console.log(JSON.stringify(response.data, null, 2));
    } catch (error) {
        console.error('Error:', error.message);
    }
}

async function runBacktest(symbol, days) {
    try {
        const response = await axios.post(FUNCTION_URL, {
            action: 'backtest',
            symbol: symbol,
            days: days
        });
        console.log(JSON.stringify(response.data, null, 2));
    } catch (error) {
        console.error('Error:', error.message);
    }
}

// Execute
executeTrade('SPY');
runBacktest('QQQ', 180);
```

## Python Integration Examples

### Direct Module Usage

```python
from trading_engine import TradingEngine
from backtesting import BacktestEngine
from config import Config

# Initialize trading engine
engine = TradingEngine()

# Execute trade
result = engine.analyze_and_trade('SPY')
print(f"Action: {result['action']}")
print(f"Mode: {result['mode']}")

# Get account info
account = engine.get_account_info()
print(f"Equity: ${account['equity']:,.2f}")

# Run backtest
backtest = BacktestEngine(initial_capital=10000)
results = backtest.run_backtest('SPY', days=180)
backtest.print_results(results)
```

### Custom Market Analysis

```python
from market_data import MarketDataProvider
from market_analysis import MarketAnalyzer

# Get market data
provider = MarketDataProvider()
data = provider.get_historical_data('SPY', days=60)

# Analyze market
analyzer = MarketAnalyzer(data)
conditions = analyzer.get_market_conditions()

print(f"Volatility: {conditions['volatility']:.3f}")
print(f"Trend Strength: {conditions['trend_strength']:.3f}")
print(f"Sentiment: {conditions['sentiment']:.3f}")
```

### Custom Strategy Implementation

```python
from trading_modes import TradingStrategy, ModeSelector

class CustomStrategy(TradingStrategy):
    """Custom trading strategy."""
    
    def should_enter_long(self):
        conditions = self.market_conditions
        # Custom logic
        return conditions['sentiment'] > 0.5 and conditions['rsi'] < 50
    
    def should_enter_short(self):
        conditions = self.market_conditions
        # Custom logic
        return conditions['sentiment'] < -0.5 and conditions['rsi'] > 50
    
    def should_exit(self, position):
        # Custom exit logic
        return False, None

# Use custom strategy
conditions = {'volatility': 0.2, 'trend_strength': 0.3, 'sentiment': 0.6, 'rsi': 45}
strategy = CustomStrategy(conditions)

if strategy.should_enter_long():
    print("Enter long position")
```

## Scheduled Execution Examples

### Using GCP Cloud Scheduler

Create a Cloud Scheduler job to run trading at market open:

```bash
gcloud scheduler jobs create http daily-trading \
  --schedule="0 9 * * 1-5" \
  --time-zone="America/New_York" \
  --uri="https://YOUR_FUNCTION_URL" \
  --http-method=POST \
  --message-body='{"action":"trade","symbol":"SPY"}' \
  --headers="Content-Type=application/json"
```

### Using Cron (Linux/Mac)

Add to crontab (`crontab -e`):

```bash
# Run trading at 9:30 AM EST on weekdays
30 9 * * 1-5 cd /path/to/L3-OPS-POC && python main.py trade SPY >> /var/log/trading.log 2>&1

# Run backtest weekly on Sunday at 8 PM
0 20 * * 0 cd /path/to/L3-OPS-POC && python main.py backtest SPY 180 >> /var/log/backtest.log 2>&1
```

### Using Python Schedule Library

```python
import schedule
import time
from trading_engine import TradingEngine

def run_trading():
    """Execute trading job."""
    engine = TradingEngine()
    result = engine.analyze_and_trade('SPY')
    print(f"Trade executed: {result['action']}")

def run_backtest():
    """Execute backtest job."""
    from backtesting import BacktestEngine
    backtest = BacktestEngine()
    results = backtest.run_backtest('SPY', days=30)
    print(f"Backtest complete: {results['total_return_percent']:.2%}")

# Schedule jobs
schedule.every().day.at("09:30").do(run_trading)
schedule.every().sunday.at("20:00").do(run_backtest)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

## Response Examples

### Trade Response

```json
{
  "timestamp": "2024-01-15T09:30:00",
  "symbol": "SPY",
  "action": "opened_long",
  "mode": "bull",
  "qty": 10,
  "price": 450.25,
  "conditions": {
    "volatility": 0.18,
    "trend_strength": 0.45,
    "sentiment": 0.32,
    "current_price": 450.25,
    "rsi": 58.3,
    "adx": 28.7
  },
  "position": null
}
```

### Status Response

```json
{
  "account": {
    "equity": 105234.56,
    "cash": 98234.56,
    "buying_power": 196469.12,
    "portfolio_value": 105234.56
  },
  "position": {
    "symbol": "SPY",
    "qty": 10,
    "side": "long",
    "entry_price": 445.50,
    "current_price": 450.25,
    "market_value": 4502.50,
    "unrealized_pl": 47.50,
    "unrealized_plpc": 0.0107
  },
  "symbol": "SPY",
  "paper_trading": true
}
```

### Backtest Response

```json
{
  "total_trades": 45,
  "winning_trades": 28,
  "losing_trades": 17,
  "win_rate": 0.6222,
  "initial_capital": 10000.0,
  "final_capital": 11250.0,
  "total_return": 1250.0,
  "total_return_percent": 0.125,
  "avg_win": 150.0,
  "avg_loss": -75.0,
  "profit_factor": 2.0,
  "sharpe_ratio": 1.45,
  "max_drawdown": 500.0,
  "max_drawdown_percent": 0.05,
  "mode_distribution": {
    "bull": 20,
    "volatile": 15,
    "bear": 10
  },
  "sample_trades": [
    {
      "symbol": "SPY",
      "side": "long",
      "entry_date": "2024-01-15",
      "exit_date": "2024-01-18",
      "entry_price": 445.50,
      "exit_price": 450.25,
      "qty": 22,
      "pl": 104.50,
      "pl_percent": 0.0107,
      "exit_reason": "take_profit_triggered_5.00%",
      "mode": "bull"
    }
  ]
}
```

## Error Handling Examples

### Handle Missing Configuration

```python
from config import Config

try:
    Config.validate()
    # Proceed with trading
except ValueError as e:
    print(f"Configuration error: {e}")
    print("Please check your .env file")
```

### Handle API Errors

```python
from trading_engine import TradingEngine

engine = TradingEngine()

try:
    result = engine.analyze_and_trade('INVALID_SYMBOL')
    if 'error' in result:
        print(f"Error: {result['error']}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Handle Network Issues

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def make_request_with_retry(url, data):
    """Make HTTP request with automatic retries."""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    
    try:
        response = session.post(url, json=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
```

## Monitoring Examples

### Log All Trades

```python
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    filename=f'trading_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def execute_and_log_trade(symbol):
    """Execute trade and log results."""
    from trading_engine import TradingEngine
    
    engine = TradingEngine()
    result = engine.analyze_and_trade(symbol)
    
    logging.info(f"Symbol: {symbol}")
    logging.info(f"Action: {result['action']}")
    logging.info(f"Mode: {result['mode']}")
    
    if result.get('conditions'):
        logging.info(f"Conditions: {result['conditions']}")
    
    return result
```

### Send Alerts

```python
def send_alert(message, webhook_url=None):
    """Send alert via webhook (Slack, Discord, etc.)."""
    import requests
    
    if webhook_url:
        try:
            requests.post(webhook_url, json={'text': message})
        except Exception as e:
            print(f"Failed to send alert: {e}")

# Use in trading
result = engine.analyze_and_trade('SPY')
if result['action'] != 'none':
    send_alert(f"Trade executed: {result['action']} on {result['symbol']}")
```
