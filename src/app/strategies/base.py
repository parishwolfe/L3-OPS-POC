"""Strategy interfaces."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class StrategyResult:
    """Simple description of the action taken."""

    name: str
    action: str
    detail: str


class Strategy:
    """Contract for executable strategies."""

    name: str
    underlying_symbol: str
    take_profit_pct: float
    stop_loss_pct: float

    def build_order_legs(self) -> Iterable[dict]:  # pragma: no cover - simple contract
        raise NotImplementedError
