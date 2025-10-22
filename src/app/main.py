"""Entry point for the daily Cloud Run job."""
from __future__ import annotations

from app.config import AppSettings
from app.market_analysis.analyzer import MarketAnalyzer
from app.market_analysis.data_sources import (
    AlpacaMarketClient,
    AlphaVantageClient,
    build_snapshot,
)
from app.portfolio.alpaca_client import AlpacaClient
from app.portfolio.position_manager import PositionManager
from app.state import StrategyStateStore
from app.strategies.base import Strategy, StrategyResult
from app.strategies.bear import BearStrategy
from app.strategies.bull import BullStrategy
from app.strategies.sideways import SidewaysStrategy


def pick_strategy(regime: str) -> Strategy:
    """Return the strategy instance for the detected regime."""
    registry = {
        "bull": BullStrategy(),
        "bear": BearStrategy(),
        "sideways": SidewaysStrategy(),
    }
    return registry[regime]


def run() -> StrategyResult:
    """Run the daily process and return the decision."""
    settings = AppSettings.from_env()

    alpha_client = AlphaVantageClient(settings.alpha_vantage)
    alpaca_market_client = AlpacaMarketClient(settings.alpaca)
    alpaca_trading_client = AlpacaClient(settings.alpaca)

    snapshot = build_snapshot(alpha_client=alpha_client, alpaca_client=alpaca_market_client)
    analyzer = MarketAnalyzer()
    assessment = analyzer.assess(snapshot)

    strategy = pick_strategy(assessment.regime)

    state_store = StrategyStateStore()
    position_manager = PositionManager(alpaca_trading_client)

    position = position_manager.find_position(strategy.underlying_symbol)
    stored_state = state_store.get(strategy.underlying_symbol)

    if position and stored_state and stored_state.strategy_name == strategy.name:
        health = position_manager.evaluate_health(
            position=position,
            take_profit_pct=strategy.take_profit_pct,
            stop_loss_pct=strategy.stop_loss_pct,
        )
        if health.status in {"take_profit", "stop_loss"}:
            position_manager.close_position(position)
            state_store.remove(strategy.underlying_symbol)
            return StrategyResult(
                name=strategy.name,
                action=health.status,
                detail=health.reason,
            )
        return StrategyResult(
            name=strategy.name,
            action="hold",
            detail="position remains within risk limits",
        )

    if position and stored_state:
        position_manager.close_position(position)
        state_store.remove(strategy.underlying_symbol)
        return StrategyResult(
            name=strategy.name,
            action="close_mismatched",
            detail="position existed but did not match stored strategy",
        )

    legs = strategy.build_order_legs()
    position_manager.open_order(tag=strategy.name, legs=legs)
    state_store.set(strategy.underlying_symbol, strategy.name)
    return StrategyResult(
        name=strategy.name,
        action="open",
        detail=f"opened new {strategy.underlying_symbol} position",
    )


if __name__ == "__main__":  # pragma: no cover - script entry point
    result = run()
    print(result)
