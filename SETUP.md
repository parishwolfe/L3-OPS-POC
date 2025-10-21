# Setup Guide

## Quick Start

### 1. Prerequisites

- Python 3.11 or higher
- Alpaca API account (sign up at https://alpaca.markets)
- Alpha Vantage API key (get free key at https://www.alphavantage.co/support/#api-key)
- Google Cloud Platform account (for deployment)

### 2. Local Development Setup

```bash
# Clone the repository
git clone https://github.com/parishwolfe/L3-OPS-POC.git
cd L3-OPS-POC

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### 3. API Key Configuration

#### Alpaca API Setup

1. Sign up at https://alpaca.markets
2. Navigate to API Keys section
3. Generate new API key (use Paper Trading for testing)
4. Copy API Key and Secret Key to .env file

```bash
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
ALPACA_PAPER=true  # Use paper trading
```

#### Alpha Vantage Setup

1. Visit https://www.alphavantage.co/support/#api-key
2. Enter your email to get free API key
3. Copy key to .env file

```bash
ALPHA_VANTAGE_API_KEY=your_key_here
```

### 4. Verify Installation

Run the demo script to verify everything works:

```bash
python demo.py
```

Run the test suite:

```bash
pytest test_trading_system.py -v
```

### 5. Test Trading (Paper Trading)

Execute a test trade with paper trading:

```bash
python main.py trade SPY
```

Check account status:

```bash
python main.py status SPY
```

### 6. Run Backtest

Test strategies with historical data:

```bash
python main.py backtest SPY 180
```

## GCP Cloud Functions Deployment

### 1. GCP Setup

Install Google Cloud SDK:

**macOS:**
```bash
brew install google-cloud-sdk
```

**Linux:**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Windows:**
Download from https://cloud.google.com/sdk/docs/install

### 2. GCP Authentication

```bash
# Login to GCP
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 3. Configure Secrets

Use GCP Secret Manager for API keys (recommended for production):

```bash
# Create secrets
echo -n "your_alpaca_key" | gcloud secrets create alpaca-api-key --data-file=-
echo -n "your_alpaca_secret" | gcloud secrets create alpaca-secret-key --data-file=-
echo -n "your_alpha_vantage_key" | gcloud secrets create alpha-vantage-key --data-file=-
```

### 4. Deploy Function

Using the deploy script:

```bash
chmod +x deploy.sh
./deploy.sh
```

Or manually:

```bash
gcloud functions deploy l3-options-trading \
  --gen2 \
  --runtime=python311 \
  --region=us-central1 \
  --source=. \
  --entry-point=trading_handler \
  --trigger-http \
  --allow-unauthenticated \
  --timeout=540s \
  --memory=512MB \
  --set-env-vars ALPACA_PAPER=true
```

### 5. Set Environment Variables

Update function with your API keys:

```bash
gcloud functions deploy l3-options-trading \
  --update-env-vars ALPACA_API_KEY=your_key,ALPACA_SECRET_KEY=your_secret,ALPHA_VANTAGE_API_KEY=your_key
```

Or use Secret Manager (recommended):

```bash
gcloud functions deploy l3-options-trading \
  --update-secrets ALPACA_API_KEY=alpaca-api-key:latest,ALPACA_SECRET_KEY=alpaca-secret-key:latest,ALPHA_VANTAGE_API_KEY=alpha-vantage-key:latest
```

### 6. Test Deployment

Get the function URL:

```bash
gcloud functions describe l3-options-trading --region=us-central1 --gen2 --format='value(serviceConfig.uri)'
```

Test the endpoint:

```bash
curl -X POST YOUR_FUNCTION_URL \
  -H "Content-Type: application/json" \
  -d '{"action": "status", "symbol": "SPY"}'
```

## Configuration Options

### Trading Parameters

Edit .env or set environment variables:

```bash
# Symbol and position sizing
DEFAULT_SYMBOL=SPY           # Default ETF to trade
POSITION_SIZE=1000          # Base position size in dollars

# Risk management
STOP_LOSS_PERCENT=0.02      # 2% stop loss
TAKE_PROFIT_PERCENT=0.05    # 5% take profit

# Mode thresholds
VOLATILITY_THRESHOLD_HIGH=0.25   # High volatility threshold
VOLATILITY_THRESHOLD_LOW=0.15    # Low volatility threshold
TREND_STRENGTH_BULL=0.6          # Bull mode threshold
TREND_STRENGTH_BEAR=-0.6         # Bear mode threshold
```

### Cloud Function Settings

Adjust in deploy.sh or cloudbuild.yaml:

- **Memory**: 512MB (increase for more symbols)
- **Timeout**: 540s (9 minutes for backtesting)
- **Region**: us-central1 (change to nearest region)

## Troubleshooting

### Common Issues

**1. Import Errors**

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

**2. API Rate Limits**

- Alpaca: 200 requests per minute
- Alpha Vantage: 5 requests per minute (free tier)
- Consider upgrading API plans for production

**3. Configuration Errors**

```bash
# Verify environment variables
python -c "from config import Config; Config.validate()"
```

**4. Cloud Function Timeout**

- Increase timeout in deploy.sh
- Reduce backtest days parameter
- Use pagination for large datasets

**5. Authentication Errors**

```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login
```

### Testing API Credentials

Test Alpaca connection:

```python
from alpaca.trading.client import TradingClient
from config import Config

client = TradingClient(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY, paper=True)
account = client.get_account()
print(f"Account equity: ${account.equity}")
```

Test Alpha Vantage connection:

```python
from alpha_vantage.timeseries import TimeSeries
from config import Config

ts = TimeSeries(key=Config.ALPHA_VANTAGE_API_KEY)
data, meta = ts.get_daily(symbol='SPY', outputsize='compact')
print(f"Retrieved {len(data)} days of data")
```

## Next Steps

1. **Paper Trading**: Test strategies with paper trading first
2. **Backtesting**: Run extensive backtests on different symbols
3. **Monitoring**: Set up logging and monitoring
4. **Alerts**: Implement notification system
5. **Live Trading**: After thorough testing, consider live trading

## Security Best Practices

1. Never commit API keys to git
2. Use Secret Manager for production
3. Enable authentication for Cloud Functions
4. Regularly rotate API keys
5. Monitor usage and costs
6. Use least privilege access

## Resources

- [Alpaca API Documentation](https://alpaca.markets/docs/)
- [Alpha Vantage Documentation](https://www.alphavantage.co/documentation/)
- [GCP Cloud Functions Guide](https://cloud.google.com/functions/docs)
- [Technical Analysis Library](https://technical-analysis-library-in-python.readthedocs.io/)

## Support

For issues or questions:
- Check existing GitHub issues
- Review documentation
- Contact support through GitHub issues
