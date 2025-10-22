"""Bull market strategy: bullish iron condor variation."""
from __future__ import annotations

from app.strategies.base import Strategy


class BullStrategy(Strategy):
    """Constructs a bullish options spread."""

    name = "bull_iron_condor"
    underlying_symbol = "QQQ"
    take_profit_pct = 25.0
    stop_loss_pct = 15.0

    def build_order_legs(self):
        """Return legs for a bullish iron condor on QQQ."""
        return [
            {"symbol": "QQQ230915C00370000", "ratio": 1, "side": "sell"},
            {"symbol": "QQQ230915C00375000", "ratio": 1, "side": "buy"},
            {"symbol": "QQQ230915P00340000", "ratio": 1, "side": "buy"},
            {"symbol": "QQQ230915P00345000", "ratio": 1, "side": "sell"},
        ]
