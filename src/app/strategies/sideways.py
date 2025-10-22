"""Sideways market strategy: delta-neutral iron condor."""
from __future__ import annotations

from app.strategies.base import Strategy


class SidewaysStrategy(Strategy):
    """Constructs a market neutral iron condor on SPY."""

    name = "sideways_iron_condor"
    underlying_symbol = "SPY"
    take_profit_pct = 20.0
    stop_loss_pct = 12.5

    def build_order_legs(self):
        """Return legs for a neutral iron condor on SPY."""
        return [
            {"symbol": "SPY230915C00450000", "ratio": 1, "side": "sell"},
            {"symbol": "SPY230915C00455000", "ratio": 1, "side": "buy"},
            {"symbol": "SPY230915P00410000", "ratio": 1, "side": "buy"},
            {"symbol": "SPY230915P00405000", "ratio": 1, "side": "sell"},
        ]
