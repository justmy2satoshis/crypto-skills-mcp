"""
Technical Analysis Skills

Procedural workflows for crypto technical analysis with 86% token reduction.

This module provides four core Skills:
- support_resistance: Identify key price levels via pivot points and volume analysis
- pattern_recognition: Recognize chart patterns using template correlation
- momentum_scoring: Multi-timeframe momentum analysis with weighted scoring
- volatility_analysis: Volatility measurement and breakout detection

All Skills return standardized JSON output compatible with database storage
and agent consumption.
"""

from .support_resistance import SupportResistanceIdentifier, identify_support_resistance
from .pattern_recognition import PatternRecognizer, recognize_patterns
from .momentum_scoring import MomentumScorer, score_momentum
from .volatility_analysis import VolatilityAnalyzer, analyze_volatility

__all__ = [
    # Classes
    "SupportResistanceIdentifier",
    "PatternRecognizer",
    "MomentumScorer",
    "VolatilityAnalyzer",
    # Convenience functions
    "identify_support_resistance",
    "recognize_patterns",
    "score_momentum",
    "analyze_volatility",
]

# Module metadata
__version__ = "1.0.0"
__proceduralization__ = 0.86  # 86% proceduralization rate
__token_reduction__ = 0.86  # 86% average token reduction
