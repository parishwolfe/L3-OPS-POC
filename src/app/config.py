"""Application configuration helpers."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AlpacaSettings:
    """Settings for the Alpaca client."""

    api_key: str
    api_secret: str
    base_url: str = "https://paper-api.alpaca.markets"


@dataclass
class AlphaVantageSettings:
    """Settings for the AlphaVantage client."""

    api_key: str


@dataclass
class AppSettings:
    """Top level application settings."""

    alpaca: AlpacaSettings
    alpha_vantage: AlphaVantageSettings

    @classmethod
    def from_env(cls) -> "AppSettings":
        """Build settings from environment variables."""
        alpaca_key = os.getenv("ALPACA_API_KEY", "")
        alpaca_secret = os.getenv("ALPACA_API_SECRET", "")
        alpha_vantage_key = os.getenv("ALPHAVANTAGE_API_KEY", "")

        if not alpaca_key or not alpaca_secret:
            raise RuntimeError("Alpaca credentials are required for paper trading.")

        if not alpha_vantage_key:
            raise RuntimeError("AlphaVantage API key is required.")

        alpaca = AlpacaSettings(api_key=alpaca_key, api_secret=alpaca_secret)
        alpha_vantage = AlphaVantageSettings(api_key=alpha_vantage_key)
        return cls(alpaca=alpaca, alpha_vantage=alpha_vantage)
