"""Utilities for fetching market data from third-party APIs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import requests

from app.config import AlphaVantageSettings
from app.config import AlpacaSettings


@dataclass
class MarketSnapshot:
    """Aggregate snapshot of metrics used for analysis."""

    vix: float
    sentiment_score: float
    breadth_ratio: float


class AlphaVantageClient:
    """Minimal AlphaVantage client."""

    def __init__(self, settings: AlphaVantageSettings) -> None:
        self._settings = settings

    def fetch_vix_daily(self) -> float:
        """Return the latest VIX value using AlphaVantage."""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": "VIX",
            "apikey": self._settings.api_key,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data: Dict[str, Dict[str, str]] = response.json().get("Time Series (Daily)", {})
        latest_day = sorted(data.keys())[-1]
        return float(data[latest_day]["4. close"])

    def fetch_sentiment_score(self) -> float:
        """Return a crude sentiment score using AlphaVantage news sentiment endpoint."""
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": "SPY,QQQ,DIA",
            "apikey": self._settings.api_key,
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        feed = response.json().get("feed", [])
        if not feed:
            return 0.0
        total = sum(item.get("overall_sentiment_score", 0.0) for item in feed)
        return total / len(feed)


class AlpacaMarketClient:
    """Small helper to fetch index breadth using Alpaca market data."""

    def __init__(self, settings: AlpacaSettings) -> None:
        self._settings = settings
        self._session = requests.Session()
        self._session.headers.update(
            {
                "APCA-API-KEY-ID": settings.api_key,
                "APCA-API-SECRET-KEY": settings.api_secret,
            }
        )

    def fetch_market_breadth(self) -> float:
        """Return a simple advance/decline breadth ratio."""
        url = "https://data.alpaca.markets/v2/stocks/market/movers"
        response = self._session.get(url, timeout=10)
        response.raise_for_status()
        movers = response.json().get("movers", [])
        advancers = sum(1 for item in movers if item.get("change", 0) > 0)
        decliners = sum(1 for item in movers if item.get("change", 0) < 0)
        if decliners == 0:
            return float(advancers)
        return advancers / decliners


def build_snapshot(*, alpha_client: AlphaVantageClient, alpaca_client: AlpacaMarketClient) -> MarketSnapshot:
    """Gather key metrics for the analysis."""
    vix = alpha_client.fetch_vix_daily()
    sentiment = alpha_client.fetch_sentiment_score()
    breadth = alpaca_client.fetch_market_breadth()
    return MarketSnapshot(vix=vix, sentiment_score=sentiment, breadth_ratio=breadth)
