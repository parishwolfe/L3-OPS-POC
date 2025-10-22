"""Bear market strategy: bearish put spread."""
from __future__ import annotations

from app.strategies.base import Strategy


class BearStrategy(Strategy):
    """Constructs a bearish put spread on DIA."""

    name = "bear_put_spread"
    underlying_symbol = "DIA"
    take_profit_pct = 30.0
    stop_loss_pct = 18.0

    def build_order_legs(self):
        """Return legs for a bearish put spread on DIA."""
        return [
            {"symbol": "DIA230915P00340000", "ratio": 1, "side": "buy"},
            {"symbol": "DIA230915P00330000", "ratio": 1, "side": "sell"},
        ]
