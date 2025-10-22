"""Thin Alpaca client wrapper targeted at paper trading."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests

from app.config import AlpacaSettings


@dataclass
class Position:
    """Representation of an open position."""

    symbol: str
    quantity: float
    avg_entry_price: float
    current_price: float
    strategy: str

    def unrealized_pct(self) -> float:
        """Return the unrealized profit or loss percentage."""
        if self.avg_entry_price == 0:
            return 0.0
        change = self.current_price - self.avg_entry_price
        return (change / self.avg_entry_price) * 100


class AlpacaClient:
    """Very small subset of the Alpaca API used by the app."""

    def __init__(self, settings: AlpacaSettings) -> None:
        self._settings = settings
        self._session = requests.Session()
        self._session.headers.update(
            {
                "APCA-API-KEY-ID": settings.api_key,
                "APCA-API-SECRET-KEY": settings.api_secret,
            }
        )

    def list_positions(self) -> List[Position]:
        """Return all current paper trading positions."""
        url = f"{self._settings.base_url}/v2/positions"
        response = self._session.get(url, timeout=10)
        response.raise_for_status()
        positions: List[Position] = []
        for raw in response.json():
            strategy = raw.get("symbol", "").split("-")[-1]
            positions.append(
                Position(
                    symbol=raw.get("symbol", ""),
                    quantity=float(raw.get("qty", 0)),
                    avg_entry_price=float(raw.get("avg_entry_price", 0)),
                    current_price=float(raw.get("current_price", 0)),
                    strategy=strategy or "unknown",
                )
            )
        return positions

    def submit_order(
        self,
        *,
        symbol: str,
        quantity: float,
        side: str,
        order_type: str,
        time_in_force: str,
        tag: Optional[str] = None,
        legs: Optional[Iterable[dict]] = None,
    ) -> dict:
        """Submit a multi-leg order for paper trading."""
        url = f"{self._settings.base_url}/v2/orders"
        payload: dict = {
            "symbol": symbol,
            "qty": quantity,
            "side": side,
            "type": order_type,
            "time_in_force": time_in_force,
            "extended_hours": False,
        }

        if tag:
            payload["client_order_id"] = tag

        if legs:
            payload["legs"] = list(legs)

        response = self._session.post(url, json=payload, timeout=10)
        response.raise_for_status()
        return response.json()

    def close_position(self, symbol: str) -> dict:
        """Close an existing paper position."""
        url = f"{self._settings.base_url}/v2/positions/{symbol}"
        response = self._session.delete(url, timeout=10)
        response.raise_for_status()
        return response.json()
