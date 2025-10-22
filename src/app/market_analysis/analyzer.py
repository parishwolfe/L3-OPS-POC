"""Market condition analyzer."""
from __future__ import annotations

from dataclasses import dataclass

from app.market_analysis.data_sources import MarketSnapshot


@dataclass
class MarketAssessment:
    """Result of the market condition analysis."""

    regime: str
    score: float
    snapshot: MarketSnapshot


class MarketAnalyzer:
    """Produce a simple market regime classification."""

    def assess(self, snapshot: MarketSnapshot) -> MarketAssessment:
        """Return a market assessment score and regime."""
        score = self._score_snapshot(snapshot)
        if score >= 65:
            regime = "bull"
        elif score <= 35:
            regime = "bear"
        else:
            regime = "sideways"
        return MarketAssessment(regime=regime, score=score, snapshot=snapshot)

    def _score_snapshot(self, snapshot: MarketSnapshot) -> float:
        """Combine metrics into a 0-100 score."""
        vix_score = max(0.0, min(100.0, 80 - snapshot.vix))
        sentiment_score = max(0.0, min(100.0, 50 + snapshot.sentiment_score * 50))
        breadth_score = max(0.0, min(100.0, snapshot.breadth_ratio * 20 + 50))
        return (vix_score * 0.4) + (sentiment_score * 0.3) + (breadth_score * 0.3)
