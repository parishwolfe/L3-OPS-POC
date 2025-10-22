"""State persistence for tracking strategy positions."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


STATE_FILE = Path("state/positions.json")


@dataclass
class StrategyState:
    """State about a strategy-applied position."""

    symbol: str
    strategy_name: str


class StrategyStateStore:
    """Very small JSON-backed store for strategy state."""

    def __init__(self, path: Path = STATE_FILE) -> None:
        self._path = path
        if not self._path.parent.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> Dict[str, StrategyState]:
        """Load all state entries."""
        if not self._path.exists():
            return {}
        data = json.loads(self._path.read_text())
        return {symbol: StrategyState(symbol=symbol, strategy_name=item["strategy_name"]) for symbol, item in data.items()}

    def save(self, entries: Dict[str, StrategyState]) -> None:
        """Persist all state entries."""
        serializable = {
            symbol: {"strategy_name": state.strategy_name} for symbol, state in entries.items()
        }
        self._path.write_text(json.dumps(serializable, indent=2))

    def get(self, symbol: str) -> Optional[StrategyState]:
        """Return the stored state for a symbol."""
        return self.load().get(symbol)

    def set(self, symbol: str, strategy_name: str) -> None:
        """Record the strategy used for a symbol."""
        entries = self.load()
        entries[symbol] = StrategyState(symbol=symbol, strategy_name=strategy_name)
        self.save(entries)

    def remove(self, symbol: str) -> None:
        """Remove state for a symbol."""
        entries = self.load()
        entries.pop(symbol, None)
        self.save(entries)
