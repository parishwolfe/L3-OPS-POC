"""Helpers to manage open positions and their health."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from app.portfolio.alpaca_client import AlpacaClient, Position


@dataclass
class PositionHealth:
    """Simple summary of a position's health."""

    status: str
    reason: str


class PositionManager:
    """Evaluates current positions and applies strategy rules."""

    def __init__(self, alpaca: AlpacaClient) -> None:
        self._alpaca = alpaca

    def find_position(self, symbol: str) -> Optional[Position]:
        """Return the matching position if it exists."""
        positions = self._alpaca.list_positions()
        for position in positions:
            if position.symbol == symbol:
                return position
        return None

    def evaluate_health(
        self,
        *,
        position: Position,
        take_profit_pct: float,
        stop_loss_pct: float,
    ) -> PositionHealth:
        """Decide whether to hold, take profit, or stop loss."""
        change = position.unrealized_pct()
        if change >= take_profit_pct:
            return PositionHealth(status="take_profit", reason="target reached")
        if change <= -abs(stop_loss_pct):
            return PositionHealth(status="stop_loss", reason="drawdown too large")
        return PositionHealth(status="hold", reason="within risk limits")

    def close_position(self, position: Position) -> None:
        """Close a paper position."""
        self._alpaca.close_position(position.symbol)

    def open_order(self, *, tag: str, legs: Iterable[dict]) -> None:
        """Submit a multi-leg options order."""
        self._alpaca.submit_order(
            symbol="combo",  # placeholder for multi-leg order
            quantity=1,
            side="buy",
            order_type="limit",
            time_in_force="day",
            tag=tag,
            legs=legs,
        )
