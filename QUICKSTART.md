# Quick Start Guide

Get started with L3-OPS-POC in 5 minutes!

## Prerequisites

- Python 3.11+
- Alpaca API account (free paper trading)
- Alpha Vantage API key (free tier)

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
ALPACA_PAPER=true  # Keep paper trading enabled
```

## 3. Run Demo (No API Keys Required)

Test the system without API keys:

```bash
python demo.py
```

You should see output showing:
- Bull market analysis
- Volatile market analysis
- Bear market analysis
- Mode transition examples

## 4. Run Tests

Verify everything works:

```bash
pytest test_trading_system.py -v
```

Expected: **18 tests passing** ✅

## 5. Execute Your First Trade

With API keys configured:

```bash
python main.py trade SPY
```

This will:
1. Fetch real market data for SPY
2. Analyze market conditions
3. Select optimal trading mode
4. Generate buy/sell signals
5. Execute paper trades (if signals generated)

## 6. Run a Backtest

Test strategies on historical data:

```bash
python main.py backtest SPY 180
```

This analyzes 180 days of historical data and shows:
- Total return
- Win rate
- Sharpe ratio
- Maximum drawdown
- Mode distribution

## 7. Check Status

View your account and positions:

```bash
python main.py status SPY
```

## What's Next?

### Local Development
- Review [SETUP.md](SETUP.md) for detailed configuration
- Check [EXAMPLES.md](EXAMPLES.md) for more usage patterns
- Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system

### Deploy to GCP
1. Install Google Cloud SDK
2. Authenticate: `gcloud auth login`
3. Deploy: `./deploy.sh`
4. Done! Your function is live

### Customize

Edit these files to customize behavior:
- **config.py**: Trading parameters, thresholds
- **trading_modes.py**: Strategy entry/exit logic
- **risk_management.py**: Stop-loss, take-profit levels

## Common Commands

```bash
# Trade different symbols
python main.py trade QQQ
python main.py trade IWM

# Backtest different timeframes
python main.py backtest SPY 30   # 1 month
python main.py backtest SPY 365  # 1 year

# Run tests with coverage
pytest test_trading_system.py --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Key Features Available

✅ Adaptive trading modes (Bull/Volatile/Bear)
✅ 10+ technical indicators
✅ Risk management (stop-loss, take-profit)
✅ Backtesting framework
✅ Paper trading
✅ Real-time market data
✅ GCP Cloud Functions deployment

## Getting Help

- **Setup Issues**: See [SETUP.md](SETUP.md)
- **Usage Examples**: See [EXAMPLES.md](EXAMPLES.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **GitHub Issues**: Report bugs or ask questions

## Safety First! ⚠️

- Always use **paper trading** for testing
- Never commit API keys to git
- Start with small position sizes
- Test thoroughly before live trading
- Understand the risks involved

## Success Checklist

- [ ] Dependencies installed
- [ ] API keys configured
- [ ] Demo runs successfully
- [ ] All tests pass
- [ ] First paper trade executed
- [ ] Backtest completed
- [ ] Ready to customize strategies

---

**You're all set!** Start trading with confidence. 🚀

For detailed documentation, see the main [README.md](README.md).
