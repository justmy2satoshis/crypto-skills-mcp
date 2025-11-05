"""
Unit tests for SentimentFusionEngine Advanced Skill

Tests sentiment fusion functionality including:
- Volatility-conditional weighting
- Signal fusion (sentiment + technical)
- Adaptive alpha calculation
- Score classification and signal generation
- Verbose parameter functionality
- Conviction scoring
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.sentiment_analysis.sentiment_fusion import SentimentFusionEngine


class TestSentimentFusionEngineInit:
    """Test SentimentFusionEngine initialization"""

    def test_initialization(self):
        """Test engine initializes with MCP client"""
        mock_client = MagicMock()
        engine = SentimentFusionEngine(mock_client)

        assert engine.mcp == mock_client
        assert engine is not None


class TestFuseMethod:
    """Test main fuse() method"""

    @pytest.fixture
    def mock_mcp_responses(self):
        """Mock MCP client responses"""
        # Mock Fear & Greed Index
        fear_greed_response = {
            "content": [{"text": "Current index: 68 (Greed)"}]
        }

        # Mock News Sentiment
        news_response = {
            "content": [
                {
                    "sentiment": "positive",
                    "title": "Bitcoin rallies on institutional adoption",
                }
            ]
        }

        # Mock Technical Indicators
        rsi_response = {"content": [{"rsi": [65.0]}]}
        macd_response = {
            "content": [{"macd": [120.5], "signal": [115.2], "histogram": [5.3]}]
        }
        atr_response = {"content": [{"atr": [1200.0]}]}

        return {
            "fear_greed": fear_greed_response,
            "news": news_response,
            "rsi": rsi_response,
            "macd": macd_response,
            "atr": atr_response,
        }

    @pytest.mark.asyncio
    async def test_fuse_basic_call(self, mock_mcp_responses):
        """Test basic fuse() call returns correct structure"""
        mock_client = AsyncMock()

        # Configure mock responses
        async def mock_call_tool(tool_name, params):
            if "fear" in tool_name.lower():
                return mock_mcp_responses["fear_greed"]
            elif "news" in tool_name.lower():
                return mock_mcp_responses["news"]
            elif "rsi" in tool_name.lower():
                return mock_mcp_responses["rsi"]
            elif "macd" in tool_name.lower():
                return mock_mcp_responses["macd"]
            elif "atr" in tool_name.lower():
                return mock_mcp_responses["atr"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        engine = SentimentFusionEngine(mock_client)

        result = await engine.fuse("BTC", timeframe="4h")

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "sentiment-analysis-skill"
        assert "asset" in result
        assert result["asset"] == "BTC"
        assert "data_type" in result
        assert result["data_type"] == "sentiment_fusion"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_fuse_verbose_true(self, mock_mcp_responses):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "fear" in tool_name.lower():
                return mock_mcp_responses["fear_greed"]
            elif "news" in tool_name.lower():
                return mock_mcp_responses["news"]
            elif "rsi" in tool_name.lower():
                return mock_mcp_responses["rsi"]
            elif "macd" in tool_name.lower():
                return mock_mcp_responses["macd"]
            elif "atr" in tool_name.lower():
                return mock_mcp_responses["atr"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        engine = SentimentFusionEngine(mock_client)

        result = await engine.fuse("BTC", timeframe="4h", verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "asset" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_fuse_verbose_false(self, mock_mcp_responses):
        """Test verbose=False returns minimal response (70% size reduction)"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "fear" in tool_name.lower():
                return mock_mcp_responses["fear_greed"]
            elif "news" in tool_name.lower():
                return mock_mcp_responses["news"]
            elif "rsi" in tool_name.lower():
                return mock_mcp_responses["rsi"]
            elif "macd" in tool_name.lower():
                return mock_mcp_responses["macd"]
            elif "atr" in tool_name.lower():
                return mock_mcp_responses["atr"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        engine = SentimentFusionEngine(mock_client)

        result = await engine.fuse("BTC", timeframe="4h", verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_fuse_data_structure(self, mock_mcp_responses):
        """Test data structure contains all required fields"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "fear" in tool_name.lower():
                return mock_mcp_responses["fear_greed"]
            elif "news" in tool_name.lower():
                return mock_mcp_responses["news"]
            elif "rsi" in tool_name.lower():
                return mock_mcp_responses["rsi"]
            elif "macd" in tool_name.lower():
                return mock_mcp_responses["macd"]
            elif "atr" in tool_name.lower():
                return mock_mcp_responses["atr"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        engine = SentimentFusionEngine(mock_client)

        result = await engine.fuse("BTC", timeframe="4h")
        data = result["data"]

        # Verify all required data fields
        assert "combined_score" in data
        assert "combined_signal" in data
        assert "sentiment_score" in data
        assert "technical_score" in data
        assert "alpha" in data
        assert "volatility_regime" in data
        assert "signal_alignment" in data
        assert "conviction" in data
        assert "trading_recommendation" in data

        # Verify data types
        assert isinstance(data["combined_score"], (int, float))
        assert isinstance(data["combined_signal"], str)
        assert isinstance(data["sentiment_score"], (int, float))
        assert isinstance(data["technical_score"], (int, float))
        assert isinstance(data["alpha"], float)
        assert isinstance(data["volatility_regime"], str)
        assert isinstance(data["conviction"], float)


class TestVolatilityIndexCalculation:
    """Test volatility index calculation from ATR"""

    def test_calculate_volatility_index_high(self):
        """Test high volatility calculation"""
        engine = SentimentFusionEngine(MagicMock())

        # High ATR relative to price
        volatility_index = engine._calculate_volatility_index(
            atr=2500.0, current_price=50000.0
        )

        # 2500 / 50000 = 0.05 (5% daily range)
        assert volatility_index == 0.05

    def test_calculate_volatility_index_low(self):
        """Test low volatility calculation"""
        engine = SentimentFusionEngine(MagicMock())

        # Low ATR relative to price
        volatility_index = engine._calculate_volatility_index(
            atr=500.0, current_price=50000.0
        )

        # 500 / 50000 = 0.01 (1% daily range)
        assert volatility_index == 0.01

    def test_calculate_volatility_index_zero_price(self):
        """Test volatility index with zero price (edge case)"""
        engine = SentimentFusionEngine(MagicMock())

        volatility_index = engine._calculate_volatility_index(atr=1000.0, current_price=0)

        # Should return 0.0 to avoid division by zero
        assert volatility_index == 0.0


class TestVolatilityRegimeClassification:
    """Test volatility regime classification"""

    def test_classify_volatility_very_high(self):
        """Test very_high volatility classification"""
        engine = SentimentFusionEngine(MagicMock())

        regime = engine._classify_volatility_regime(0.06)  # 6% daily range
        assert regime == "very_high"

    def test_classify_volatility_high(self):
        """Test high volatility classification"""
        engine = SentimentFusionEngine(MagicMock())

        regime = engine._classify_volatility_regime(0.045)  # 4.5% daily range
        assert regime == "high"

    def test_classify_volatility_moderate(self):
        """Test moderate volatility classification"""
        engine = SentimentFusionEngine(MagicMock())

        regime = engine._classify_volatility_regime(0.03)  # 3% daily range
        assert regime == "moderate"

    def test_classify_volatility_low(self):
        """Test low volatility classification"""
        engine = SentimentFusionEngine(MagicMock())

        regime = engine._classify_volatility_regime(0.015)  # 1.5% daily range
        assert regime == "low"


class TestAdaptiveAlphaCalculation:
    """Test adaptive alpha calculation based on volatility"""

    def test_calculate_alpha_high_volatility(self):
        """Test alpha for high volatility (sentiment leads)"""
        engine = SentimentFusionEngine(MagicMock())

        # High volatility (>0.4) -> sentiment leads
        alpha = engine._calculate_adaptive_alpha(0.5)
        assert alpha == 0.80

    def test_calculate_alpha_moderate_volatility(self):
        """Test alpha for moderate volatility (balanced)"""
        engine = SentimentFusionEngine(MagicMock())

        # Moderate volatility (0.2-0.4) -> balanced
        alpha = engine._calculate_adaptive_alpha(0.3)
        assert alpha == 0.50

    def test_calculate_alpha_low_volatility(self):
        """Test alpha for low volatility (technical leads)"""
        engine = SentimentFusionEngine(MagicMock())

        # Low volatility (<0.2) -> technical leads
        alpha = engine._calculate_adaptive_alpha(0.1)
        assert alpha == 0.20


class TestSignalFusion:
    """Test signal fusion formula"""

    def test_fuse_signals_high_volatility(self):
        """Test fusion with high volatility (80% sentiment)"""
        engine = SentimentFusionEngine(MagicMock())

        # α = 0.80 (high volatility)
        combined = engine._fuse_signals(
            sentiment_score=75.0, technical_score=50.0, alpha=0.80
        )

        # combined = 0.80 * 75 + 0.20 * 50 = 60 + 10 = 70
        assert combined == 70.0

    def test_fuse_signals_balanced(self):
        """Test fusion with moderate volatility (50/50)"""
        engine = SentimentFusionEngine(MagicMock())

        # α = 0.50 (moderate volatility)
        combined = engine._fuse_signals(
            sentiment_score=80.0, technical_score=60.0, alpha=0.50
        )

        # combined = 0.50 * 80 + 0.50 * 60 = 40 + 30 = 70
        assert combined == 70.0

    def test_fuse_signals_low_volatility(self):
        """Test fusion with low volatility (80% technical)"""
        engine = SentimentFusionEngine(MagicMock())

        # α = 0.20 (low volatility)
        combined = engine._fuse_signals(
            sentiment_score=60.0, technical_score=80.0, alpha=0.20
        )

        # combined = 0.20 * 60 + 0.80 * 80 = 12 + 64 = 76
        assert combined == 76.0


class TestScoreClassification:
    """Test combined score classification"""

    def test_classify_score_strong_buy(self):
        """Test Strong Buy classification"""
        engine = SentimentFusionEngine(MagicMock())

        signal = engine._classify_combined_score(82.0)
        assert signal == "Strong Buy"

    def test_classify_score_buy(self):
        """Test Buy classification"""
        engine = SentimentFusionEngine(MagicMock())

        signal = engine._classify_combined_score(68.0)
        assert signal == "Buy"

    def test_classify_score_hold(self):
        """Test Hold classification"""
        engine = SentimentFusionEngine(MagicMock())

        signal = engine._classify_combined_score(50.0)
        assert signal == "Hold"

    def test_classify_score_sell(self):
        """Test Sell classification"""
        engine = SentimentFusionEngine(MagicMock())

        signal = engine._classify_combined_score(35.0)
        assert signal == "Sell"

    def test_classify_score_strong_sell(self):
        """Test Strong Sell classification"""
        engine = SentimentFusionEngine(MagicMock())

        signal = engine._classify_combined_score(15.0)
        assert signal == "Strong Sell"


class TestSignalAlignment:
    """Test signal alignment assessment"""

    def test_assess_alignment_strongly_aligned(self):
        """Test strongly aligned signals"""
        engine = SentimentFusionEngine(MagicMock())

        # Both signals very close (within 5 points)
        alignment = engine._assess_signal_alignment(
            sentiment_score=72.0, technical_score=70.0
        )

        assert alignment == "strongly_aligned"

    def test_assess_alignment_aligned(self):
        """Test aligned signals"""
        engine = SentimentFusionEngine(MagicMock())

        # Signals moderately close (within 10 points)
        alignment = engine._assess_signal_alignment(
            sentiment_score=75.0, technical_score=68.0
        )

        assert alignment == "aligned"

    def test_assess_alignment_weakly_aligned(self):
        """Test weakly aligned signals"""
        engine = SentimentFusionEngine(MagicMock())

        # Signals somewhat close (within 20 points)
        alignment = engine._assess_signal_alignment(
            sentiment_score=70.0, technical_score=55.0
        )

        assert alignment == "weakly_aligned"

    def test_assess_alignment_divergent(self):
        """Test divergent signals"""
        engine = SentimentFusionEngine(MagicMock())

        # Signals far apart (>20 points)
        alignment = engine._assess_signal_alignment(
            sentiment_score=80.0, technical_score=35.0
        )

        assert alignment == "divergent"


class TestConvictionCalculation:
    """Test conviction scoring based on alignment and volatility"""

    def test_calculate_conviction_strongly_aligned(self):
        """Test high conviction with strongly aligned signals"""
        engine = SentimentFusionEngine(MagicMock())

        conviction = engine._calculate_conviction(
            alignment="strongly_aligned", volatility_regime="moderate"
        )

        # Strongly aligned -> high base conviction
        assert conviction >= 0.85
        assert conviction <= 1.0

    def test_calculate_conviction_divergent(self):
        """Test low conviction with divergent signals"""
        engine = SentimentFusionEngine(MagicMock())

        conviction = engine._calculate_conviction(
            alignment="divergent", volatility_regime="moderate"
        )

        # Divergent -> low conviction
        assert conviction <= 0.50

    def test_calculate_conviction_high_volatility_boost(self):
        """Test volatility boost for high volatility regimes"""
        engine = SentimentFusionEngine(MagicMock())

        # High volatility should boost conviction
        high_vol_conviction = engine._calculate_conviction(
            alignment="aligned", volatility_regime="very_high"
        )

        moderate_vol_conviction = engine._calculate_conviction(
            alignment="aligned", volatility_regime="moderate"
        )

        assert high_vol_conviction > moderate_vol_conviction

    def test_calculate_conviction_capped_at_one(self):
        """Test conviction is capped at 1.0"""
        engine = SentimentFusionEngine(MagicMock())

        # Maximum possible conviction scenario
        conviction = engine._calculate_conviction(
            alignment="strongly_aligned", volatility_regime="very_high"
        )

        assert conviction <= 1.0


class TestTradingRecommendation:
    """Test trading recommendation generation"""

    def test_generate_recommendation_strong_buy(self):
        """Test Strong Buy recommendation"""
        engine = SentimentFusionEngine(MagicMock())

        recommendation = engine._generate_trading_recommendation(
            combined_signal="Strong Buy",
            conviction=0.88,
            alignment="strongly_aligned",
            volatility_regime="moderate",
        )

        assert "high conviction" in recommendation.lower()
        assert "buy" in recommendation.lower()

    def test_generate_recommendation_strong_sell(self):
        """Test Strong Sell recommendation"""
        engine = SentimentFusionEngine(MagicMock())

        recommendation = engine._generate_trading_recommendation(
            combined_signal="Strong Sell",
            conviction=0.85,
            alignment="strongly_aligned",
            volatility_regime="moderate",
        )

        assert "high conviction" in recommendation.lower()
        assert "sell" in recommendation.lower()

    def test_generate_recommendation_divergent_signals(self):
        """Test recommendation with divergent signals"""
        engine = SentimentFusionEngine(MagicMock())

        recommendation = engine._generate_trading_recommendation(
            combined_signal="Buy",
            conviction=0.45,
            alignment="divergent",
            volatility_regime="moderate",
        )

        assert "caution" in recommendation.lower() or "divergent" in recommendation.lower()

    def test_generate_recommendation_high_volatility(self):
        """Test recommendation mentions high volatility"""
        engine = SentimentFusionEngine(MagicMock())

        recommendation = engine._generate_trading_recommendation(
            combined_signal="Buy",
            conviction=0.75,
            alignment="aligned",
            volatility_regime="very_high",
        )

        assert "volatility" in recommendation.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
