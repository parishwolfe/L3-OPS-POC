# L3-OPS-POC
Level 3 Options Proof Of Concept - Adaptive Trading System

## Overview

An intelligent, adaptive trading system built for Level 3 options trading using the Alpaca API, deployed on Google Cloud Platform (GCP) Cloud Functions. The system implements three distinct trading modes (Bull, Volatile, Bear) and continuously assesses market sentiment, volatility, and trend strength to select optimal strategies.

## Features

### Adaptive Trading Modes
- **Bull Market Mode**: Focuses on long positions with momentum trading
- **Volatile Market Mode**: Range trading and mean reversion strategies
- **Bear Market Mode**: Short positions and capital preservation

### Market Analysis
- Real-time sentiment analysis using technical indicators (RSI, MACD)
- Volatility calculation using ATR and Bollinger Bands
- Trend strength analysis using ADX and moving averages
- Integration with Alpaca and Alpha Vantage for market data

### Risk Management
- Configurable stop-loss protection (default 2%)
- Take-profit triggers (default 5%)
- Bailout logic for extreme market conditions
- Automatic mode transitions with position protection
- Position sizing based on volatility and market mode

### Backtesting Framework
- Historical strategy evaluation
- Performance metrics (Sharpe ratio, max drawdown, win rate)
- Mode distribution analysis
- Equity curve tracking

### Paper Trading
- ETF paper trading for safe testing
- Real-time market data integration
- Full order management via Alpaca API

## Architecture

```
├── main.py                 # GCP Cloud Functions entry point
├── config.py              # Configuration and environment variables
├── market_data.py         # Market data integration (Alpaca + Alpha Vantage)
├── market_analysis.py     # Technical analysis and indicators
├── trading_modes.py       # Bull, Volatile, and Bear strategies
├── trading_engine.py      # Core trading orchestration
├── risk_management.py     # Stop-loss, take-profit, and bailout logic
├── backtesting.py         # Strategy backtesting framework
├── requirements.txt       # Python dependencies
├── cloudbuild.yaml        # GCP Cloud Build configuration
└── deploy.sh             # Deployment script
```

## Installation

### Prerequisites
- Python 3.11+
- Alpaca API account (paper trading or live)
- Alpha Vantage API key
- GCP account (for Cloud Functions deployment)

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/parishwolfe/L3-OPS-POC.git
cd L3-OPS-POC
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
- `ALPACA_API_KEY`: Your Alpaca API key
- `ALPACA_SECRET_KEY`: Your Alpaca secret key
- `ALPACA_PAPER`: Set to `true` for paper trading
- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key

## Usage

### Command Line Interface

#### Execute Trade
```bash
python main.py trade SPY
```

#### Run Backtest
```bash
python main.py backtest SPY 180
```

#### Check Status
```bash
python main.py status SPY
```

### Cloud Functions Deployment

1. Install Google Cloud SDK:
```bash
# Follow instructions at https://cloud.google.com/sdk/docs/install
```

2. Authenticate:
```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

3. Deploy function:
```bash
./deploy.sh
```

Or use Cloud Build:
```bash
gcloud builds submit --config cloudbuild.yaml
```

### API Usage

Once deployed, the Cloud Function accepts HTTP POST requests:

```bash
# Execute trade
curl -X POST https://YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{"action": "trade", "symbol": "SPY"}'

# Run backtest
curl -X POST https://YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{"action": "backtest", "symbol": "SPY", "days": 180}'

# Check status
curl -X POST https://YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{"action": "status", "symbol": "SPY"}'
```

## Trading Strategy Details

### Mode Selection Logic

The system automatically selects trading modes based on:

1. **Volatility**: High volatility (>25%) triggers Volatile mode
2. **Trend Strength**: Strong uptrend (>0.6) → Bull mode, Strong downtrend (<-0.6) → Bear mode
3. **Market Conditions**: Combined analysis of sentiment, volatility, and trend

### Bull Market Strategy
- **Entry**: Bullish signals with positive sentiment and RSI < 70
- **Exit**: Bearish reversal, extreme overbought, or risk management triggers
- **Position Size**: Standard (100% of base size)

### Volatile Market Strategy
- **Entry**: Oversold/overbought extremes for mean reversion
- **Exit**: Return to neutral RSI or sentiment
- **Position Size**: Conservative (70% of base size)

### Bear Market Strategy
- **Entry**: Bearish signals with negative sentiment
- **Exit**: Bullish reversal, extreme oversold, or risk management triggers
- **Position Size**: Very conservative (50% of base size)

## Risk Management

### Stop-Loss
- Automatically closes positions at 2% loss (configurable)
- Applies to both long and short positions

### Take-Profit
- Automatically closes positions at 5% profit (configurable)
- Locks in gains before potential reversals

### Bailout Conditions
- Extreme volatility spikes (>50%)
- Strong trend reversals against position
- Mode transitions with adverse positions

## Configuration

Edit `.env` or set environment variables:

```bash
# Trading Parameters
DEFAULT_SYMBOL=SPY
POSITION_SIZE=1000
STOP_LOSS_PERCENT=0.02
TAKE_PROFIT_PERCENT=0.05

# Market Mode Thresholds
VOLATILITY_THRESHOLD_HIGH=0.25
VOLATILITY_THRESHOLD_LOW=0.15
TREND_STRENGTH_BULL=0.6
TREND_STRENGTH_BEAR=-0.6
```

## Testing

Run the test suite:
```bash
pytest test_trading_system.py -v
```

Run with coverage:
```bash
pytest test_trading_system.py --cov=. --cov-report=html
```

## Backtesting Results

Example backtest output:
```
==================================================
BACKTEST RESULTS
==================================================
Initial Capital: $10,000.00
Final Capital: $11,250.00
Total Return: $1,250.00 (12.50%)

Total Trades: 45
Winning Trades: 28
Losing Trades: 17
Win Rate: 62.22%

Average Win: $150.00
Average Loss: $75.00
Profit Factor: 2.00

Sharpe Ratio: 1.45
Max Drawdown: $500.00 (5.00%)

Mode Distribution:
  bull: 20 trades
  volatile: 15 trades
  bear: 10 trades
==================================================
```

## Performance Considerations

- **Cloud Functions**: Configured with 512MB memory and 540s timeout
- **Rate Limits**: Respects Alpaca and Alpha Vantage API rate limits
- **Data Caching**: Considers implementing caching for repeated requests
- **Cost Optimization**: Uses paper trading by default to avoid real capital

## Security

- Never commit API keys to the repository
- Use GCP Secret Manager for production deployments
- Enable authentication for Cloud Functions in production
- Regularly rotate API keys

## Limitations

- Paper trading recommended for initial testing
- Subject to Alpaca API rate limits
- Alpha Vantage free tier has limited API calls
- Cloud Function cold starts may affect latency

## Roadmap

- [ ] Add options trading strategies (Level 3)
- [ ] Implement machine learning for mode prediction
- [ ] Add Telegram/Discord notifications
- [ ] Create web dashboard for monitoring
- [ ] Add multi-symbol portfolio management
- [ ] Implement advanced risk metrics (VaR, CVaR)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

See LICENSE file for details.

## Disclaimer

This software is for educational and research purposes only. Trading involves substantial risk of loss. Use paper trading for testing and never invest more than you can afford to lose. The authors are not responsible for any financial losses incurred through the use of this software.

## Support

For issues and questions:
- Open an issue on GitHub
- Check existing documentation
- Review Alpaca API documentation: https://alpaca.markets/docs/

## Acknowledgments

- Alpaca API for market data and trading
- Alpha Vantage for additional market data
- TA-Lib Python wrapper for technical analysis
- Google Cloud Platform for serverless deployment
