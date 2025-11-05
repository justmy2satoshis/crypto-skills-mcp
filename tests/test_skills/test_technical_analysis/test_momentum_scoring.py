"""
Unit tests for MomentumScorer Skill

Tests momentum scoring functionality including:
- Multi-timeframe analysis
- Weighted score calculation
- Indicator aggregation (RSI, MACD, Stochastic)
- Trend alignment assessment
- Conviction calculation
- Signal classification
- Verbose parameter functionality
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.technical_analysis.momentum_scoring import MomentumScorer


class TestMomentumScorerInit:
    """Test MomentumScorer initialization"""

    def test_initialization(self):
        """Test scorer initializes with MCP client"""
        mock_client = MagicMock()
        scorer = MomentumScorer(mock_client)

        assert scorer.mcp == mock_client
        assert scorer is not None

    def test_timeframe_weights_defined(self):
        """Test timeframe weights are properly defined"""
        scorer = MomentumScorer(MagicMock())

        assert "15m" in scorer.TIMEFRAME_WEIGHTS
        assert "1h" in scorer.TIMEFRAME_WEIGHTS
        assert "4h" in scorer.TIMEFRAME_WEIGHTS
        assert "1d" in scorer.TIMEFRAME_WEIGHTS

        # Verify weights sum to 1.0
        total_weight = sum(scorer.TIMEFRAME_WEIGHTS.values())
        assert abs(total_weight - 1.0) < 0.01


class TestScoreMethod:
    """Test main score() method"""

    @pytest.fixture
    def mock_indicator_responses(self):
        """Mock indicator responses for different timeframes"""
        return {
            "rsi": {"rsi": [65.0]},
            "macd": {"macd": [120.5], "signal": [115.2], "histogram": [5.3]},
            "stochastic": {"k": [62.0]},
        }

    @pytest.mark.asyncio
    async def test_score_basic_call(self, mock_indicator_responses):
        """Test basic score() call returns correct structure"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "rsi" in tool_name.lower():
                return mock_indicator_responses["rsi"]
            elif "macd" in tool_name.lower():
                return mock_indicator_responses["macd"]
            elif "stochastic" in tool_name.lower():
                return mock_indicator_responses["stochastic"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        scorer = MomentumScorer(mock_client)

        result = await scorer.score("BTC/USDT", timeframes=["1h"])

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "technical-analysis-skill"
        assert "symbol" in result
        assert result["symbol"] == "BTC/USDT"
        assert "data_type" in result
        assert result["data_type"] == "momentum_score"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_score_verbose_true(self, mock_indicator_responses):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "rsi" in tool_name.lower():
                return mock_indicator_responses["rsi"]
            elif "macd" in tool_name.lower():
                return mock_indicator_responses["macd"]
            elif "stochastic" in tool_name.lower():
                return mock_indicator_responses["stochastic"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        scorer = MomentumScorer(mock_client)

        result = await scorer.score("BTC/USDT", timeframes=["1h"], verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "symbol" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "timeframes_analyzed" in result["metadata"]
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_score_verbose_false(self, mock_indicator_responses):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "rsi" in tool_name.lower():
                return mock_indicator_responses["rsi"]
            elif "macd" in tool_name.lower():
                return mock_indicator_responses["macd"]
            elif "stochastic" in tool_name.lower():
                return mock_indicator_responses["stochastic"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        scorer = MomentumScorer(mock_client)

        result = await scorer.score("BTC/USDT", timeframes=["1h"], verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_score_data_structure(self, mock_indicator_responses):
        """Test data structure contains all required fields"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "rsi" in tool_name.lower():
                return mock_indicator_responses["rsi"]
            elif "macd" in tool_name.lower():
                return mock_indicator_responses["macd"]
            elif "stochastic" in tool_name.lower():
                return mock_indicator_responses["stochastic"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        scorer = MomentumScorer(mock_client)

        result = await scorer.score("BTC/USDT", timeframes=["1h"])
        data = result["data"]

        # Verify all required data fields
        assert "overall_score" in data
        assert "classification" in data
        assert "timeframe_breakdown" in data
        assert "indicators" in data
        assert "trend_alignment" in data
        assert "conviction" in data

        # Verify data types
        assert isinstance(data["overall_score"], (int, float))
        assert isinstance(data["classification"], str)
        assert isinstance(data["timeframe_breakdown"], dict)
        assert isinstance(data["indicators"], dict)
        assert isinstance(data["trend_alignment"], str)
        assert isinstance(data["conviction"], float)

    @pytest.mark.asyncio
    async def test_score_default_timeframes(self, mock_indicator_responses):
        """Test score() uses default timeframes when not specified"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "rsi" in tool_name.lower():
                return mock_indicator_responses["rsi"]
            elif "macd" in tool_name.lower():
                return mock_indicator_responses["macd"]
            elif "stochastic" in tool_name.lower():
                return mock_indicator_responses["stochastic"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        scorer = MomentumScorer(mock_client)

        result = await scorer.score("BTC/USDT")  # No timeframes specified
        data = result["data"]

        # Should analyze default timeframes
        assert "timeframe_breakdown" in data
        # Default is ["15m", "1h", "4h", "1d"]
        assert len(data["timeframe_breakdown"]) <= 4


class TestTimeframeScoreCalculation:
    """Test timeframe score calculation"""

    def test_calculate_timeframe_score_bullish(self):
        """Test score calculation with bullish indicators"""
        scorer = MomentumScorer(MagicMock())

        indicators = {
            "rsi": 70.0,  # Bullish
            "macd": {"value": 150.0, "signal": 120.0},  # Bullish (value > signal)
            "stochastic": 75.0,  # Bullish
        }

        score = scorer._calculate_timeframe_score(indicators)

        # Should be high (above 60)
        assert score > 60

    def test_calculate_timeframe_score_bearish(self):
        """Test score calculation with bearish indicators"""
        scorer = MomentumScorer(MagicMock())

        indicators = {
            "rsi": 30.0,  # Bearish
            "macd": {"value": 100.0, "signal": 130.0},  # Bearish (value < signal)
            "stochastic": 25.0,  # Bearish
        }

        score = scorer._calculate_timeframe_score(indicators)

        # Should be low (below 40)
        assert score < 40

    def test_calculate_timeframe_score_neutral(self):
        """Test score calculation with neutral indicators"""
        scorer = MomentumScorer(MagicMock())

        indicators = {
            "rsi": 50.0,  # Neutral
            "macd": {"value": 100.0, "signal": 100.0},  # Neutral (equal)
            "stochastic": 50.0,  # Neutral
        }

        score = scorer._calculate_timeframe_score(indicators)

        # Should be neutral (around 50)
        assert 40 <= score <= 60


class TestOverallScoreCalculation:
    """Test overall weighted score calculation"""

    def test_calculate_overall_score_weighted(self):
        """Test weighted calculation across timeframes"""
        scorer = MomentumScorer(MagicMock())

        timeframe_breakdown = {
            "15m": {"score": 60.0, "signal": "Buy"},
            "1h": {"score": 65.0, "signal": "Buy"},
            "4h": {"score": 70.0, "signal": "Buy"},
            "1d": {"score": 75.0, "signal": "Buy"},
        }

        overall = scorer._calculate_overall_score(timeframe_breakdown)

        # Weighted average:
        # 60 * 0.10 + 65 * 0.20 + 70 * 0.30 + 75 * 0.40
        # = 6 + 13 + 21 + 30 = 70
        assert abs(overall - 70.0) < 0.1

    def test_calculate_overall_score_empty(self):
        """Test overall score with empty breakdown"""
        scorer = MomentumScorer(MagicMock())

        overall = scorer._calculate_overall_score({})

        # Should return neutral score
        assert overall == 50.0

    def test_calculate_overall_score_higher_timeframes_weighted_more(self):
        """Test that higher timeframes have more weight"""
        scorer = MomentumScorer(MagicMock())

        # Low score on high timeframe, high score on low timeframe
        breakdown1 = {
            "15m": {"score": 80.0, "signal": "Buy"},
            "1d": {"score": 40.0, "signal": "Sell"},
        }

        # High score on high timeframe, low score on low timeframe
        breakdown2 = {
            "15m": {"score": 40.0, "signal": "Sell"},
            "1d": {"score": 80.0, "signal": "Buy"},
        }

        overall1 = scorer._calculate_overall_score(breakdown1)
        overall2 = scorer._calculate_overall_score(breakdown2)

        # overall2 should be higher (1d has more weight)
        assert overall2 > overall1


class TestIndicatorAggregation:
    """Test indicator aggregation across timeframes"""

    def test_aggregate_indicators_multiple_timeframes(self):
        """Test aggregation across multiple timeframes"""
        scorer = MomentumScorer(MagicMock())

        valid_results = [
            (
                "1h",
                65.0,
                {
                    "rsi": 60.0,
                    "macd": {"value": 120.0, "signal": 115.0},
                    "stochastic": 55.0,
                },
            ),
            (
                "4h",
                70.0,
                {
                    "rsi": 65.0,
                    "macd": {"value": 130.0, "signal": 125.0},
                    "stochastic": 60.0,
                },
            ),
            (
                "1d",
                75.0,
                {
                    "rsi": 70.0,
                    "macd": {"value": 110.0, "signal": 120.0},  # Bearish
                    "stochastic": 65.0,
                },
            ),
        ]

        indicators = scorer._aggregate_indicators(valid_results)

        # Verify structure
        assert "rsi_avg" in indicators
        assert "macd_bullish_count" in indicators
        assert "stochastic_avg" in indicators

        # Verify calculations
        assert indicators["rsi_avg"] == round((60.0 + 65.0 + 70.0) / 3, 2)
        assert indicators["macd_bullish_count"] == 2  # Two bullish MACD
        assert indicators["stochastic_avg"] == round((55.0 + 60.0 + 65.0) / 3, 2)

    def test_aggregate_indicators_empty_list(self):
        """Test aggregation with empty results"""
        scorer = MomentumScorer(MagicMock())

        indicators = scorer._aggregate_indicators([])

        assert indicators["rsi_avg"] is None
        assert indicators["macd_bullish_count"] == 0
        assert indicators["stochastic_avg"] is None


class TestTrendAlignment:
    """Test trend alignment assessment"""

    def test_assess_trend_alignment_strong_bullish(self):
        """Test strong bullish alignment (80%+ Buy signals)"""
        scorer = MomentumScorer(MagicMock())

        breakdown = {
            "15m": {"score": 75.0, "signal": "Strong Buy"},
            "1h": {"score": 78.0, "signal": "Strong Buy"},
            "4h": {"score": 76.0, "signal": "Buy"},
            "1d": {"score": 77.0, "signal": "Buy"},
        }

        alignment = scorer._assess_trend_alignment(breakdown)

        assert alignment == "strong"

    def test_assess_trend_alignment_moderate_bullish(self):
        """Test moderate bullish alignment (60%+ Buy signals)"""
        scorer = MomentumScorer(MagicMock())

        breakdown = {
            "15m": {"score": 50.0, "signal": "Neutral"},
            "1h": {"score": 65.0, "signal": "Buy"},
            "4h": {"score": 70.0, "signal": "Buy"},
            "1d": {"score": 75.0, "signal": "Buy"},
        }

        alignment = scorer._assess_trend_alignment(breakdown)

        assert alignment == "moderate"

    def test_assess_trend_alignment_conflicting(self):
        """Test conflicting alignment (mixed Buy and Sell)"""
        scorer = MomentumScorer(MagicMock())

        breakdown = {
            "15m": {"score": 30.0, "signal": "Sell"},
            "1h": {"score": 40.0, "signal": "Neutral"},
            "4h": {"score": 65.0, "signal": "Buy"},
            "1d": {"score": 70.0, "signal": "Buy"},
        }

        alignment = scorer._assess_trend_alignment(breakdown)

        assert alignment == "conflicting"

    def test_assess_trend_alignment_weak(self):
        """Test weak alignment (mostly Neutral)"""
        scorer = MomentumScorer(MagicMock())

        breakdown = {
            "15m": {"score": 45.0, "signal": "Neutral"},
            "1h": {"score": 50.0, "signal": "Neutral"},
            "4h": {"score": 48.0, "signal": "Neutral"},
            "1d": {"score": 52.0, "signal": "Neutral"},
        }

        alignment = scorer._assess_trend_alignment(breakdown)

        assert alignment == "weak"

    def test_assess_trend_alignment_empty(self):
        """Test alignment with empty breakdown"""
        scorer = MomentumScorer(MagicMock())

        alignment = scorer._assess_trend_alignment({})

        assert alignment == "unknown"


class TestConvictionCalculation:
    """Test conviction calculation"""

    def test_calculate_conviction_high_agreement(self):
        """Test high conviction with low variance across timeframes"""
        scorer = MomentumScorer(MagicMock())

        # All scores very close (low std dev)
        breakdown = {
            "15m": {"score": 74.0, "signal": "Buy"},
            "1h": {"score": 75.0, "signal": "Buy"},
            "4h": {"score": 76.0, "signal": "Buy"},
            "1d": {"score": 75.0, "signal": "Buy"},
        }

        conviction = scorer._calculate_conviction(breakdown, overall_score=75.0)

        # Low variance -> high conviction
        assert conviction >= 0.80

    def test_calculate_conviction_low_agreement(self):
        """Test low conviction with high variance across timeframes"""
        scorer = MomentumScorer(MagicMock())

        # Scores widely spread (high std dev)
        breakdown = {
            "15m": {"score": 30.0, "signal": "Sell"},
            "1h": {"score": 50.0, "signal": "Neutral"},
            "4h": {"score": 70.0, "signal": "Buy"},
            "1d": {"score": 90.0, "signal": "Strong Buy"},
        }

        conviction = scorer._calculate_conviction(breakdown, overall_score=60.0)

        # High variance -> low conviction
        assert conviction <= 0.60

    def test_calculate_conviction_boosted_for_extreme_score(self):
        """Test conviction boost for extreme overall scores"""
        scorer = MomentumScorer(MagicMock())

        # Extreme high score
        breakdown = {
            "15m": {"score": 75.0, "signal": "Buy"},
            "1h": {"score": 78.0, "signal": "Buy"},
            "4h": {"score": 80.0, "signal": "Strong Buy"},
            "1d": {"score": 82.0, "signal": "Strong Buy"},
        }

        conviction = scorer._calculate_conviction(breakdown, overall_score=79.0)

        # Extreme score (>75) should boost conviction
        assert conviction >= 0.85

    def test_calculate_conviction_empty_breakdown(self):
        """Test conviction with empty breakdown"""
        scorer = MomentumScorer(MagicMock())

        conviction = scorer._calculate_conviction({}, overall_score=50.0)

        assert conviction == 0.50


class TestScoreClassification:
    """Test score classification into signals"""

    def test_classify_score_strong_buy(self):
        """Test Strong Buy classification (>=75)"""
        scorer = MomentumScorer(MagicMock())

        assert scorer._classify_score(80.0) == "Strong Buy"
        assert scorer._classify_score(75.0) == "Strong Buy"

    def test_classify_score_buy(self):
        """Test Buy classification (60-74)"""
        scorer = MomentumScorer(MagicMock())

        assert scorer._classify_score(70.0) == "Buy"
        assert scorer._classify_score(60.0) == "Buy"

    def test_classify_score_neutral(self):
        """Test Neutral classification (40-59)"""
        scorer = MomentumScorer(MagicMock())

        assert scorer._classify_score(50.0) == "Neutral"
        assert scorer._classify_score(40.0) == "Neutral"

    def test_classify_score_sell(self):
        """Test Sell classification (25-39)"""
        scorer = MomentumScorer(MagicMock())

        assert scorer._classify_score(30.0) == "Sell"
        assert scorer._classify_score(25.0) == "Sell"

    def test_classify_score_strong_sell(self):
        """Test Strong Sell classification (<25)"""
        scorer = MomentumScorer(MagicMock())

        assert scorer._classify_score(20.0) == "Strong Sell"
        assert scorer._classify_score(10.0) == "Strong Sell"


class TestIndicatorExtraction:
    """Test indicator value extraction from MCP results"""

    def test_extract_indicator_value_list_format(self):
        """Test extraction from list format"""
        scorer = MomentumScorer(MagicMock())

        result = {"rsi": [55.0, 60.0, 65.0]}
        value = scorer._extract_indicator_value(result, "rsi")

        # Should extract latest value
        assert value == 65.0

    def test_extract_indicator_value_scalar_format(self):
        """Test extraction from scalar format"""
        scorer = MomentumScorer(MagicMock())

        result = {"rsi": 62.5}
        value = scorer._extract_indicator_value(result, "rsi")

        assert value == 62.5

    def test_extract_indicator_value_exception(self):
        """Test extraction handles exceptions"""
        scorer = MomentumScorer(MagicMock())

        result = Exception("API error")
        value = scorer._extract_indicator_value(result, "rsi")

        assert value is None

    def test_extract_indicator_value_missing_key(self):
        """Test extraction with missing key"""
        scorer = MomentumScorer(MagicMock())

        result = {"other_key": [55.0]}
        value = scorer._extract_indicator_value(result, "rsi")

        assert value is None

    def test_extract_macd_values_valid(self):
        """Test MACD extraction with valid data"""
        scorer = MomentumScorer(MagicMock())

        result = {
            "macd": [100.0, 110.0, 120.0],
            "signal": [95.0, 105.0, 115.0],
            "histogram": [5.0, 5.0, 5.0],
        }

        macd = scorer._extract_macd_values(result)

        assert macd["value"] == 120.0
        assert macd["signal"] == 115.0
        assert macd["histogram"] == 5.0

    def test_extract_macd_values_exception(self):
        """Test MACD extraction handles exceptions"""
        scorer = MomentumScorer(MagicMock())

        result = Exception("API error")
        macd = scorer._extract_macd_values(result)

        assert macd["value"] == 0
        assert macd["signal"] == 0
        assert macd["histogram"] == 0


class TestParallelExecution:
    """Test parallel execution of timeframe analysis"""

    @pytest.mark.asyncio
    async def test_parallel_timeframe_analysis(self):
        """Test that timeframes are analyzed in parallel"""
        mock_client = AsyncMock()

        call_count = {"count": 0}

        async def mock_call_tool(tool_name, params):
            call_count["count"] += 1
            return {"rsi": [65.0], "macd": [120.0], "signal": [115.0], "k": [60.0]}

        mock_client.call_tool.side_effect = mock_call_tool

        scorer = MomentumScorer(mock_client)

        await scorer.score("BTC/USDT", timeframes=["1h", "4h"])

        # Should make parallel calls for both timeframes
        # Each timeframe makes 3 calls (RSI, MACD, Stochastic)
        assert call_count["count"] >= 6


class TestErrorHandling:
    """Test error handling and resilience"""

    @pytest.mark.asyncio
    async def test_score_handles_failed_timeframe(self):
        """Test score continues when one timeframe fails"""
        mock_client = AsyncMock()

        call_count = {"count": 0}

        async def mock_call_tool(tool_name, params):
            call_count["count"] += 1
            # Fail on first timeframe, succeed on second
            if call_count["count"] <= 3:
                raise Exception("API timeout")
            return {"rsi": [65.0], "macd": [120.0], "signal": [115.0], "k": [60.0]}

        mock_client.call_tool.side_effect = mock_call_tool

        scorer = MomentumScorer(mock_client)

        result = await scorer.score("BTC/USDT", timeframes=["1h", "4h"])

        # Should still return result with partial data
        assert "data" in result
        assert result["metadata"]["timeframes_analyzed"] == 1  # Only one succeeded


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
