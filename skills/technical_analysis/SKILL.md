# Technical Analysis Skill

**Proceduralization**: 85% | **Token Reduction**: 80-90%

## Overview

This Skill handles procedural technical analysis workflows for crypto markets, including:
- Support/resistance level identification using price action analysis
- Chart pattern recognition (head & shoulders, double tops/bottoms, triangles)
- Momentum scoring across multiple timeframes
- Volatility analysis and breakout detection

## MCP Dependencies

This Skill requires the following MCPs:

### Tier 1 (Required)
- **ccxt-mcp**: Historical price data for pattern recognition
- **crypto-indicators-mcp**: RSI, MACD, Stochastic for momentum scoring

### Tier 2 (Enhanced)
- **crypto-indicators-mcp__calculate_bollinger_bands**: Volatility bands
- **crypto-indicators-mcp__calculate_average_true_range**: Volatility measure

## Usage

### From Agent
```python
from skills.technical_analysis import (
    identify_support_resistance,
    recognize_patterns,
    score_momentum,
    analyze_volatility,
)

# Identify key price levels (87% token reduction)
levels = identify_support_resistance(symbol="BTC/USDT", timeframe="1d", lookback=100)

# Recognize chart patterns
patterns = recognize_patterns(symbol="BTC/USDT", timeframe="4h")

# Score momentum across timeframes
momentum = score_momentum(symbol="BTC/USDT", timeframes=["15m", "1h", "4h", "1d"])

# Analyze volatility and breakout potential
volatility = analyze_volatility(symbol="BTC/USDT", timeframe="1h")
```

### From Command Line
```bash
crypto-skills ta levels --symbol BTC/USDT --timeframe 1d
crypto-skills ta patterns --symbol BTC/USDT --timeframe 4h
crypto-skills ta momentum --symbol BTC/USDT --timeframes 15m,1h,4h,1d
```

## Output Format

All technical analysis functions return standardized JSON:

```json
{
  "timestamp": "2025-10-26T12:00:00Z",
  "source": "technical-analysis-skill",
  "symbol": "BTC/USDT",
  "data_type": "support_resistance",
  "data": {
    "support_levels": [
      {"price": 42500.0, "strength": 0.85, "touches": 3},
      {"price": 41000.0, "strength": 0.72, "touches": 2}
    ],
    "resistance_levels": [
      {"price": 45000.0, "strength": 0.90, "touches": 4},
      {"price": 46500.0, "strength": 0.65, "touches": 2}
    ],
    "current_price": 43800.0,
    "nearest_support": 42500.0,
    "nearest_resistance": 45000.0
  },
  "metadata": {
    "timeframe": "1d",
    "lookback_periods": 100,
    "confidence": 0.88
  }
}
```

## Token Impact

| Task | Agent-Only Approach | Skills Approach | Reduction |
|------|---------------------|-----------------|-----------|
| Support/Resistance Identification | 3,500 tokens | 450 tokens | 87% |
| Pattern Recognition | 4,000 tokens | 600 tokens | 85% |
| Momentum Scoring (4 timeframes) | 5,000 tokens | 700 tokens | 86% |
| Volatility Analysis | 2,500 tokens | 350 tokens | 86% |
| **Total** | **15,000 tokens** | **2,100 tokens** | **86%** |

## Implementation Notes

- Vectorized calculations using NumPy for performance
- Pattern recognition uses probabilistic scoring (not binary detection)
- Support/resistance levels weighted by volume at price level
- Momentum scoring normalized across timeframes for comparability
- All calculations cached with 5-minute TTL for real-time analysis

## Algorithms

### Support/Resistance Identification
1. Identify local minima/maxima in price action (pivot points)
2. Cluster price levels within 1% tolerance
3. Weight by number of touches and volume at level
4. Return top 5 support and resistance levels

### Pattern Recognition
1. Normalize price data to 0-1 scale
2. Apply sliding window correlation with pattern templates
3. Score pattern confidence based on correlation strength
4. Validate with volume confirmation
5. Return patterns with confidence > 0.70

### Momentum Scoring
1. Calculate RSI, MACD, Stochastic across timeframes
2. Normalize each indicator to 0-100 scale
3. Weight by timeframe importance (1d > 4h > 1h > 15m)
4. Combine into unified momentum score
5. Classify as: Strong Buy, Buy, Neutral, Sell, Strong Sell

## Testing

```bash
# Unit tests
pytest tests/test_skills/test_technical_analysis.py

# Integration tests (requires MCP servers)
pytest tests/test_integration/test_technical_analysis_mcp.py -m integration

# Pattern recognition validation
pytest tests/test_skills/test_pattern_recognition.py --pattern head_shoulders
```

## Dependencies

From `pyproject.toml`:
```toml
[project.optional-dependencies]
skills = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scipy>=1.10.0",  # For clustering algorithms
]
```
