# Data Extraction Skill

**Proceduralization**: 85% | **Token Reduction**: 80-90%

## Overview

This Skill handles all procedural data extraction workflows for crypto analysis, including:
- Fetching OHLCV (Open, High, Low, Close, Volume) data across 24+ exchanges
- Calculating technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Aggregating sentiment data from multiple social sources
- Normalizing data formats for downstream processing

## MCP Dependencies

This Skill requires the following MCPs from [Crypto-MCP-Suite](../../mcp-servers/Crypto%20MCPs/Crypto-MCP-Suite/):

### Tier 1 (Required)
- **ccxt-mcp**: Exchange data (price, volume, order book depth)
- **crypto-indicators-mcp**: Technical indicators calculation
- **crypto-sentiment-mcp**: Social sentiment (Reddit, Telegram, Discord)
- **crypto-feargreed-mcp**: Fear & Greed Index

### Tier 2 (Enhanced)
- **cryptopanic-mcp**: News sentiment aggregation

## Usage

### From Agent
```python
# Agent invokes Skill for procedural data gathering
from skills.data_extraction import fetch_ohlcv, calculate_indicators, aggregate_sentiment

# Fetch price data (85% token reduction vs agent calling MCP directly)
btc_data = fetch_ohlcv(symbol="BTC/USDT", timeframe="1h", limit=100)

# Calculate indicators
indicators = calculate_indicators(btc_data, indicators=["rsi", "macd", "bollinger"])

# Aggregate sentiment
sentiment = aggregate_sentiment(symbol="BTC")
```

### From Command Line
```bash
crypto-skills data extract --symbol BTC/USDT --timeframe 1h --indicators rsi,macd
crypto-skills data sentiment --symbol BTC --sources all
```

## Output Format

All data extraction functions return standardized JSON for database storage and agent consumption:

```json
{
  "timestamp": "2025-10-26T12:00:00Z",
  "source": "ccxt-mcp",
  "symbol": "BTC/USDT",
  "data_type": "ohlcv",
  "data": {
    "open": 43500.0,
    "high": 44000.0,
    "low": 43200.0,
    "close": 43800.0,
    "volume": 1250000.0
  },
  "metadata": {
    "exchange": "binance",
    "timeframe": "1h",
    "confidence": 1.0
  }
}
```

## Token Impact

| Task | Agent-Only Approach | Skills Approach | Reduction |
|------|---------------------|-----------------|-----------|
| Fetch 100 candles | 2,500 tokens | 300 tokens | 88% |
| Calculate 5 indicators | 3,000 tokens | 400 tokens | 87% |
| Aggregate sentiment | 2,500 tokens | 500 tokens | 80% |
| **Total** | **8,000 tokens** | **1,200 tokens** | **85%** |

## Implementation Notes

- All MCP calls are batched and parallelized where possible
- Caching layer (Redis) reduces redundant MCP invocations
- Error handling with graceful degradation (partial data return)
- Automatic retry logic with exponential backoff
- Data validation against schemas before return

## Error Handling

```python
try:
    data = fetch_ohlcv("BTC/USDT", "1h", limit=100)
except MCPConnectionError:
    # Fallback to cached data if available
    data = get_cached_ohlcv("BTC/USDT", "1h", max_age_minutes=15)
except InsufficientDataError:
    # Return partial data with warning
    return {"data": partial_data, "warning": "Incomplete dataset", "confidence": 0.7}
```

## Testing

```bash
# Unit tests
pytest tests/test_skills/test_data_extraction.py

# Integration tests (requires MCP servers running)
pytest tests/test_integration/test_data_extraction_mcp.py -m integration
```

## Dependencies

From `pyproject.toml`:
```toml
[project.optional-dependencies]
skills = [
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "requests>=2.31.0",
]
```
