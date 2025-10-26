# Action Mapping Patterns

## Overview

This document describes the action mapping patterns used throughout the crypto-skills-mcp agent system. These patterns map internal enum values to standardized investment actions and categorical assessments.

## Purpose

Action mapping ensures consistent output formats across all agents and prevents type mismatches between internal representations (enums) and expected API contracts (strings).

## Pattern 1: Thesis Type to Investment Action

**Location:** `agents/thesis_synthesizer.py` - `synthesize_signals()` method

**Purpose:** Map investment thesis classifications to actionable recommendations.

### Mapping Table

| Thesis Type (Enum) | Investment Action | Description |
|-------------------|------------------|-------------|
| `STRONG_BULLISH` | `STRONG_BUY` | All signals aligned bullish - aggressive entry |
| `BULLISH` | `BUY` | Majority bullish signals - standard entry |
| `NEUTRAL` | `HOLD` | Mixed signals - maintain current position |
| `BEARISH` | `SELL` | Majority bearish signals - reduce exposure |
| `STRONG_BEARISH` | `STRONG_SELL` | All signals aligned bearish - exit position |

### Implementation

```python
# In synthesize_signals method
action_map = {
    "strong_bullish": "STRONG_BUY",
    "bullish": "BUY",
    "neutral": "HOLD",
    "bearish": "SELL",
    "strong_bearish": "STRONG_SELL",
}
action = action_map.get(thesis_type.value, "HOLD")
```

### Default Behavior

- **Default action:** `HOLD` (when thesis_type is unknown or None)
- **Rationale:** Conservative approach - maintain position rather than make uninformed trade

## Pattern 2: Sentiment Regime to Assessment

**Location:** `agents/crypto_sentiment_analyst.py` - `synthesize_sentiment_outlook()` method

**Purpose:** Map internal sentiment classifications to categorical assessments for investment decisions.

### Mapping Table

| Sentiment Regime (Enum) | Assessment | Investment Implication |
|------------------------|-----------|----------------------|
| `extreme_fear` | `contrarian_buy` | Extreme pessimism - buying opportunity |
| `fear` | `bearish` | Elevated fear - cautious stance |
| `neutral` | `neutral` | Balanced sentiment - no strong signal |
| `greed` | `bullish` | Elevated optimism - positive outlook |
| `extreme_greed` | `contrarian_sell` | Extreme euphoria - selling opportunity |

### Implementation

```python
# In synthesize_sentiment_outlook method
sentiment_map = {
    "extreme_fear": "contrarian_buy",
    "fear": "bearish",
    "neutral": "neutral",
    "greed": "bullish",
    "extreme_greed": "contrarian_sell",
}
sentiment_assessment = sentiment_map.get(crowd['sentiment_regime'], "neutral")
```

### Default Behavior

- **Default assessment:** `neutral` (when sentiment_regime is unknown)
- **Rationale:** Neutral position is safest when sentiment signal is unclear

## Key Principles

### 1. Enum Value Extraction

Always use `.value` property to extract string from enum:

```python
thesis_type = ThesisType.BULLISH
# Good
action = action_map.get(thesis_type.value, "HOLD")  # "bullish" -> "BUY"

# Bad
action = action_map.get(thesis_type, "HOLD")  # Enum object -> KeyError
```

### 2. Default Values

Every mapping should specify a safe default using `.get()`:

```python
# Good - provides fallback
action = action_map.get(thesis_type.value, "HOLD")

# Bad - raises KeyError if key missing
action = action_map[thesis_type.value]
```

### 3. Conservative Defaults

Default values should be conservative:
- Investment actions → `HOLD` (maintain position)
- Sentiment assessments → `neutral` (no strong bias)

### 4. Mapping Consistency

Use consistent naming conventions:
- Investment actions: UPPERCASE (`BUY`, `SELL`, `HOLD`)
- Sentiment assessments: lowercase (`bullish`, `bearish`, `neutral`)
- Contrarian signals: `contrarian_` prefix

## Testing

### Test Pattern for Action Mapping

```python
def test_action_mapping():
    """Verify thesis type maps to correct investment action"""
    synthesizer = ThesisSynthesizer()

    # Mock data with specific thesis type
    macro = {"regime": "risk_on", "recommendation": "BUY"}
    fundamental = {"overall_score": 75, "recommendation": "BUY"}
    sentiment = {"sentiment_assessment": "bullish"}

    result = synthesizer.synthesize_signals(macro, fundamental, sentiment)

    # Assert action is investment action string, not enum value
    assert result["recommendation"] in ["STRONG_BUY", "BUY", "HOLD", "SELL", "STRONG_SELL"]
    assert result["thesis_type"] in ["strong_bullish", "bullish", "neutral", "bearish", "strong_bearish"]
```

### Common Test Failures

**Symptom:** Test expects string but gets enum value or concatenated string

**Cause:** Missing action mapping - method returns `thesis_type.value` directly

**Fix:** Add action_map dictionary and use `.get()` method

**Example:**
```python
# Before (fails tests)
return {"recommendation": thesis_type.value}  # Returns "neutral" instead of "HOLD"

# After (passes tests)
action_map = {"neutral": "HOLD", "bullish": "BUY", ...}
return {"recommendation": action_map.get(thesis_type.value, "HOLD")}
```

## Common Pitfalls

### Pitfall 1: Returning Enum Object

```python
# Wrong - returns enum object
return {"conflicts_detected": ConflictType.MACRO_SENTIMENT_MISMATCH}

# Correct - returns list of conflict dicts
detected = await self.detect_conflicts(...)
return {"conflicts_detected": detected}
```

### Pitfall 2: String Concatenation Instead of Mapping

```python
# Wrong - concatenates strings
sentiment_assessment = f"{crowd['sentiment_regime']} with {whales['positioning']}"
# Result: "greed with bullish whale positioning" (not categorical)

# Correct - uses mapping
sentiment_map = {"greed": "bullish", ...}
sentiment_assessment = sentiment_map.get(crowd['sentiment_regime'], "neutral")
# Result: "bullish" (clean categorical value)
```

### Pitfall 3: Duplicate Method Definitions

```python
# Python uses the LAST definition silently
def synthesize_signals(...):  # Line 536 - ignored!
    return {"recommendation": "BUY"}

def synthesize_signals(...):  # Line 660 - actually used
    return {"recommendation": thesis_type.value}
```

**Fix:** Remove all duplicate methods, keep only one definition

## Version History

- **v1.0.0** (2025-10-26): Initial documentation based on integration test fixes
  - Added thesis type → investment action mapping
  - Added sentiment regime → assessment mapping
  - Documented testing patterns and common pitfalls

## Related Files

- [agents/thesis_synthesizer.py](../agents/thesis_synthesizer.py) - ThesisSynthesizer implementation
- [agents/crypto_sentiment_analyst.py](../agents/crypto_sentiment_analyst.py) - CryptoSentimentAnalyst implementation
- [tests/test_agents/test_agent_integration.py](../tests/test_agents/test_agent_integration.py) - Integration tests validating mappings
- [SESSION_COMPLETION_REPORT.md](../SESSION_COMPLETION_REPORT.md) - Test fixing session details
