# System Architecture

## Overview

The L3 Options POC is a modular, adaptive trading system designed for deployment on Google Cloud Platform. The system continuously monitors market conditions and automatically selects optimal trading strategies based on volatility, trend strength, and sentiment analysis.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     GCP Cloud Functions                      │
│                         (main.py)                            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Trading    │  │  Backtest    │  │   Status     │     │
│  │   Handler    │  │   Handler    │  │   Handler    │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                            │                                 │
└────────────────────────────┼─────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────┐
        │       Trading Engine               │
        │     (trading_engine.py)            │
        │                                    │
        │  • Orchestrates all components    │
        │  • Manages order execution        │
        │  • Position monitoring            │
        └────────┬───────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    ▼            ▼            ▼
┌───────┐  ┌─────────┐  ┌──────────┐
│Market │  │ Market  │  │  Risk    │
│ Data  │  │Analysis │  │Management│
└───┬───┘  └────┬────┘  └────┬─────┘
    │           │            │
    │           │            │
    ▼           ▼            ▼
┌────────────────────────────────────┐
│        Trading Modes               │
│     (trading_modes.py)             │
│                                    │
│  ┌────────┐ ┌─────────┐ ┌──────┐ │
│  │  Bull  │ │Volatile │ │ Bear │ │
│  │Strategy│ │Strategy │ │Strategy│
│  └────────┘ └─────────┘ └──────┘ │
└────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────┐
│     External APIs                  │
│                                    │
│  • Alpaca API (Trading)           │
│  • Alpha Vantage (Market Data)    │
└────────────────────────────────────┘
```

## Component Breakdown

### 1. Cloud Functions Entry Point (`main.py`)

**Responsibilities:**
- HTTP request handling
- Request routing (trade/backtest/status)
- Response formatting
- Error handling

**Key Functions:**
- `trading_handler()`: Main HTTP handler
- `handle_trade()`: Route to trading engine
- `handle_backtest()`: Route to backtesting
- `handle_status()`: Route to account status

### 2. Configuration (`config.py`)

**Responsibilities:**
- Environment variable management
- API credential loading
- Trading parameter configuration
- Configuration validation

**Key Settings:**
- API keys (Alpaca, Alpha Vantage)
- Position sizing
- Risk parameters (stop-loss, take-profit)
- Mode thresholds

### 3. Market Data Provider (`market_data.py`)

**Responsibilities:**
- Historical data retrieval
- Intraday data fetching
- API fallback handling
- Data normalization

**Data Sources:**
- Primary: Alpaca API
- Fallback: Alpha Vantage API

**Key Methods:**
- `get_historical_data()`: Fetch daily OHLCV data
- `get_intraday_data()`: Fetch intraday data

### 4. Market Analyzer (`market_analysis.py`)

**Responsibilities:**
- Technical indicator calculation
- Market condition assessment
- Volatility analysis
- Trend and sentiment evaluation

**Indicators Calculated:**
- Moving Averages (SMA, EMA)
- MACD (Moving Average Convergence Divergence)
- RSI (Relative Strength Index)
- Bollinger Bands
- ATR (Average True Range)
- ADX (Average Directional Index)

**Key Methods:**
- `calculate_volatility()`: Returns 0-1 scale
- `calculate_trend_strength()`: Returns -1 to 1
- `calculate_sentiment()`: Returns -1 to 1
- `get_market_conditions()`: Comprehensive analysis

### 5. Trading Modes (`trading_modes.py`)

**Responsibilities:**
- Mode selection logic
- Strategy implementation
- Entry/exit signal generation
- Position sizing recommendations

**Modes:**

#### Bull Strategy
- **Focus**: Long positions, momentum trading
- **Entry**: Bullish signals + positive sentiment
- **Exit**: Bearish reversal or overbought
- **Position Size**: 100% of base

#### Volatile Strategy
- **Focus**: Range trading, mean reversion
- **Entry**: Oversold/overbought extremes
- **Exit**: Return to neutral levels
- **Position Size**: 70% of base

#### Bear Strategy
- **Focus**: Short positions, capital preservation
- **Entry**: Bearish signals + negative sentiment
- **Exit**: Bullish reversal or oversold
- **Position Size**: 50% of base

### 6. Risk Manager (`risk_management.py`)

**Responsibilities:**
- Stop-loss monitoring
- Take-profit execution
- Bailout condition detection
- Position size calculation
- Trade validation

**Protection Mechanisms:**
- Fixed percentage stop-loss (default 2%)
- Fixed percentage take-profit (default 5%)
- Extreme volatility bailout (>50%)
- Mode transition protection
- Position size limits (max 20% of account)

### 7. Trading Engine (`trading_engine.py`)

**Responsibilities:**
- Component orchestration
- Order placement
- Position management
- Account monitoring
- Trade execution workflow

**Workflow:**
1. Fetch market data
2. Analyze market conditions
3. Select trading mode
4. Get current position
5. Check exit conditions (if positioned)
6. Check entry conditions (if no position)
7. Validate trade parameters
8. Execute orders

### 8. Backtesting Engine (`backtesting.py`)

**Responsibilities:**
- Historical strategy simulation
- Performance metrics calculation
- Equity curve tracking
- Trade history recording

**Metrics Calculated:**
- Total return and percentage
- Win rate and trade counts
- Average win/loss
- Profit factor
- Sharpe ratio
- Maximum drawdown
- Mode distribution

## Data Flow

### Trading Flow

```
1. HTTP Request → main.py
2. Parse request → trading_handler()
3. Fetch market data → market_data.py
4. Calculate indicators → market_analysis.py
5. Select mode → trading_modes.py
6. Check risk → risk_management.py
7. Execute trade → trading_engine.py
8. Place order → Alpaca API
9. Return result → HTTP Response
```

### Backtesting Flow

```
1. HTTP Request → main.py
2. Parse request → handle_backtest()
3. Initialize backtest → backtesting.py
4. Load historical data → market_data.py
5. For each day:
   a. Analyze market → market_analysis.py
   b. Select strategy → trading_modes.py
   c. Check positions → risk_management.py
   d. Simulate trade → backtesting.py
6. Calculate metrics → backtesting.py
7. Return results → HTTP Response
```

## Mode Selection Logic

```
Input: Market Conditions
├── Volatility > 0.25?
│   └── Yes → VOLATILE MODE
│   └── No → Continue
├── Trend Strength > 0.6?
│   └── Yes → BULL MODE
│   └── No → Continue
├── Trend Strength < -0.6?
│   └── Yes → BEAR MODE
│   └── No → Continue
├── Volatility > 0.15?
│   └── Yes → VOLATILE MODE
│   └── No → Continue
└── Trend Strength > 0?
    └── Yes → BULL MODE
    └── No → BEAR MODE
```

## Risk Management Flow

```
Position Check:
├── Stop Loss Triggered?
│   └── Yes → CLOSE POSITION (highest priority)
│   └── No → Continue
├── Take Profit Triggered?
│   └── Yes → CLOSE POSITION
│   └── No → Continue
├── Bailout Needed?
│   ├── Extreme Volatility (>50%)?
│   ├── Strong Reversal?
│   └── Mode Transition Risk?
│   └── Yes → CLOSE POSITION
│   └── No → Continue
└── Hold Position
```

## Deployment Architecture

### Local Development
```
Developer Machine
├── Python 3.11+
├── Virtual Environment
├── .env file (secrets)
└── Local testing
```

### Cloud Deployment
```
GCP Project
├── Cloud Functions
│   ├── HTTP Trigger
│   ├── Python 3.11 Runtime
│   ├── 512MB Memory
│   └── 540s Timeout
├── Secret Manager (optional)
│   ├── Alpaca API Key
│   ├── Alpaca Secret Key
│   └── Alpha Vantage Key
├── Cloud Scheduler (optional)
│   └── Scheduled trading execution
└── Cloud Logging
    └── Execution logs
```

## Security Architecture

### Credential Management
```
Development:
└── .env file (gitignored)

Production:
├── Environment Variables
└── GCP Secret Manager
    ├── Encrypted at rest
    ├── Version control
    └── Access logging
```

### API Security
```
Alpaca API:
├── Paper Trading (default)
├── API Key Authentication
└── Rate Limiting (200/min)

Alpha Vantage:
├── API Key Authentication
└── Rate Limiting (5/min free tier)
```

## Scalability Considerations

### Current Limits
- Single symbol per request
- Synchronous execution
- Cloud Function timeout: 540s
- API rate limits apply

### Future Enhancements
- Multi-symbol portfolio management
- Asynchronous processing
- Caching layer for market data
- Message queue for high-volume trading
- Database for trade history
- Real-time WebSocket connections

## Monitoring and Observability

### Logging Points
1. Request received
2. Market data fetched
3. Mode selected
4. Trade signal generated
5. Order placed
6. Order filled
7. Position updated
8. Errors and exceptions

### Metrics to Track
- Trade execution latency
- API response times
- Success/failure rates
- Position profit/loss
- Mode distribution
- Error rates

## Testing Strategy

### Unit Tests
- Market analysis calculations
- Mode selection logic
- Risk management rules
- Strategy entry/exit signals

### Integration Tests
- API connectivity
- Order execution
- Position tracking
- Account management

### Backtesting
- Historical performance
- Strategy validation
- Risk assessment
- Parameter optimization

## Error Handling Strategy

### Levels of Fallback
1. Primary: Alpaca API
2. Fallback: Alpha Vantage API
3. Graceful degradation: Return error response
4. Logging: Record all failures
5. Alerts: Notify on critical errors

### Error Categories
- **Configuration**: Missing API keys
- **Network**: API timeouts, connectivity
- **Data**: Invalid or missing market data
- **Trading**: Order rejection, insufficient funds
- **System**: Unexpected exceptions

## Performance Optimization

### Current Optimizations
- Efficient indicator calculations
- Minimal API calls
- Vectorized operations (NumPy/Pandas)
- Strategic data caching

### Future Optimizations
- Redis caching layer
- Asynchronous API calls
- Batch processing
- Pre-computed indicators
- Database indexing

## Maintenance and Updates

### Regular Tasks
- Monitor API changes
- Update dependencies
- Review trading performance
- Adjust thresholds
- Rotate API keys

### Version Control
- Semantic versioning
- Git-based workflow
- Feature branches
- Pull request reviews
- Automated testing

## Disaster Recovery

### Backup Strategy
- Configuration backed up in git
- Trade history logged
- Account snapshots
- State recovery procedures

### Failsafe Mechanisms
- Paper trading default
- Position size limits
- Stop-loss protection
- Extreme volatility bailout
- Manual override capability
