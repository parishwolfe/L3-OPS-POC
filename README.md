# L3-OPS-POC

Level 3 Options Proof Of Concept

## Overview

This project provides a simple, readable Python application designed to run on a daily Google Cloud Run job. The program:

1. Collects market data from AlphaVantage and Alpaca (paper trading only).
2. Scores current market conditions (0-100) and classifies the regime as bull, bear, or sideways.
3. Chooses the corresponding options strategy (bull, bear, or sideways) and manages open positions with take-profit and stop-loss logic.
4. Records the strategy used for each underlying symbol so the next run can decide to hold, take profit, stop loss, or close mismatched positions.

## Running Locally

```bash
PYTHONPATH=src python -m app.main
```

Set the following environment variables before running:

- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`
- `ALPHAVANTAGE_API_KEY`

All Alpaca operations use the paper trading endpoint by default.

## Adding Strategies

Add a new strategy by creating a file in `src/app/strategies/` that subclasses `Strategy`, sets the `name`, `underlying_symbol`, `take_profit_pct`, `stop_loss_pct`, and implements `build_order_legs()`. Update `pick_strategy` in `src/app/main.py` to include the new strategy mapping.
