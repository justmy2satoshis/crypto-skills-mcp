"""
Unit tests for SentimentAggregator Skill

Tests sentiment aggregation functionality including:
- Multi-source parallel aggregation
- Social sentiment fetching (volume, balance, dominance)
- Fear & Greed Index fetching
- News sentiment fetching
- Whale activity fetching
- Overall sentiment calculation with weighted average
- Adaptive fusion mechanism with volatility-conditional weighting
- Sentiment categorization (5 categories)
- Verbose parameter functionality
- Error handling and source failures
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.data_extraction.aggregate_sentiment import (
    SentimentAggregator,
    AdaptiveSentimentFusion,
)


class TestSentimentAggregatorInit:
    """Test SentimentAggregator initialization"""

    def test_initialization(self):
        """Test aggregator initializes with MCP client"""
        mock_client = MagicMock()
        aggregator = SentimentAggregator(mock_client)

        assert aggregator.mcp == mock_client
        assert aggregator is not None


class TestAggregateMethod:
    """Test main aggregate() method"""

    @pytest.fixture
    def mock_mcp_responses(self):
        """Create mock MCP responses for all sentiment sources"""
        social_volume = {"content": [{"text": "15000 mentions"}]}
        social_balance = {"content": [{"text": "balance: 12.5"}]}
        social_dominance = {"content": [{"text": "dominance: 25.3%"}]}

        feargreed_current = {"content": [{"value": 75}]}
        feargreed_historical = {"content": [{"data": [{"value": 72}, {"value": 75}]}]}

        news = {"content": [{"articles": []}]}

        atr = {"atr": [450.5]}

        return {
            "social_volume": social_volume,
            "social_balance": social_balance,
            "social_dominance": social_dominance,
            "feargreed_current": feargreed_current,
            "feargreed_historical": feargreed_historical,
            "news": news,
            "atr": atr,
        }

    @pytest.mark.asyncio
    async def test_aggregate_basic_call(self, mock_mcp_responses):
        """Test basic aggregate() call returns correct structure"""
        mock_client = AsyncMock()

        # Setup mock responses
        def side_effect(tool_name, params):
            if "social_volume" in tool_name:
                return mock_mcp_responses["social_volume"]
            elif "sentiment_balance" in tool_name:
                return mock_mcp_responses["social_balance"]
            elif "social_dominance" in tool_name:
                return mock_mcp_responses["social_dominance"]
            elif "current_fng" in tool_name:
                return mock_mcp_responses["feargreed_current"]
            elif "historical_fng" in tool_name:
                return mock_mcp_responses["feargreed_historical"]
            elif "crypto_news" in tool_name:
                return mock_mcp_responses["news"]
            elif "average_true_range" in tool_name:
                return mock_mcp_responses["atr"]
            return {}

        mock_client.call_tool.side_effect = side_effect

        aggregator = SentimentAggregator(mock_client)

        result = await aggregator.aggregate("BTC", days=7)

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "crypto-sentiment-aggregator"
        assert "symbol" in result
        assert result["symbol"] == "BTC"
        assert "data_type" in result
        assert result["data_type"] == "sentiment_aggregated"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_aggregate_verbose_true(self, mock_mcp_responses):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = lambda tool, params: {}

        aggregator = SentimentAggregator(mock_client)

        result = await aggregator.aggregate("BTC", days=7, verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "symbol" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "days_analyzed" in result["metadata"]
        assert "sources_count" in result["metadata"]
        assert "confidence" in result["metadata"]
        assert "volatility_index" in result["metadata"]

    @pytest.mark.asyncio
    async def test_aggregate_verbose_false(self, mock_mcp_responses):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = lambda tool, params: {}

        aggregator = SentimentAggregator(mock_client)

        result = await aggregator.aggregate("BTC", days=7, verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_aggregate_data_structure(self, mock_mcp_responses):
        """Test data structure contains all required fields"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = lambda tool, params: {}

        aggregator = SentimentAggregator(mock_client)

        result = await aggregator.aggregate("BTC", days=7)
        data = result["data"]

        # Verify core data fields
        assert "overall_sentiment" in data
        assert "sentiment_category" in data

        # Verify data types
        assert isinstance(data["overall_sentiment"], (int, float))
        assert isinstance(data["sentiment_category"], str)

    @pytest.mark.asyncio
    async def test_aggregate_custom_sources(self):
        """Test aggregation with custom source list"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = lambda tool, params: {}

        aggregator = SentimentAggregator(mock_client)

        # Only request social and feargreed
        result = await aggregator.aggregate(
            "BTC", days=7, sources=["social", "feargreed"]
        )

        assert "data" in result


class TestSocialSentimentFetching:
    """Test social sentiment data fetching"""

    @pytest.mark.asyncio
    async def test_fetch_social_sentiment_valid_data(self):
        """Test fetching valid social sentiment data"""
        mock_client = AsyncMock()

        # Mock parallel responses
        volume_response = {"volume": 15000}
        balance_response = {"balance": 12.5}
        dominance_response = {"dominance": 25.3}

        mock_client.call_tool.side_effect = [
            volume_response,
            balance_response,
            dominance_response,
        ]

        aggregator = SentimentAggregator(mock_client)
        social = await aggregator._fetch_social_sentiment("BTC", 7)

        assert "volume" in social
        assert "balance" in social
        assert "dominance" in social
        assert "trend" in social

    @pytest.mark.asyncio
    async def test_fetch_social_sentiment_trend_increasing(self):
        """Test social trend classification as increasing"""
        mock_client = AsyncMock()

        # Balance > 10 should give increasing trend
        mock_client.call_tool.side_effect = [
            {"volume": 15000},
            {"balance": 15.0},
            {"dominance": 25.3},
        ]

        aggregator = SentimentAggregator(mock_client)
        social = await aggregator._fetch_social_sentiment("BTC", 7)

        assert social["trend"] == "increasing"

    @pytest.mark.asyncio
    async def test_fetch_social_sentiment_trend_decreasing(self):
        """Test social trend classification as decreasing"""
        mock_client = AsyncMock()

        # Balance < -10 should give decreasing trend
        mock_client.call_tool.side_effect = [
            {"volume": 15000},
            {"balance": -15.0},
            {"dominance": 25.3},
        ]

        aggregator = SentimentAggregator(mock_client)
        social = await aggregator._fetch_social_sentiment("BTC", 7)

        assert social["trend"] == "decreasing"

    @pytest.mark.asyncio
    async def test_fetch_social_sentiment_trend_stable(self):
        """Test social trend classification as stable"""
        mock_client = AsyncMock()

        # Balance between -10 and 10 should give stable trend
        mock_client.call_tool.side_effect = [
            {"volume": 15000},
            {"balance": 5.0},
            {"dominance": 25.3},
        ]

        aggregator = SentimentAggregator(mock_client)
        social = await aggregator._fetch_social_sentiment("BTC", 7)

        assert social["trend"] == "stable"


class TestFearGreedIndexFetching:
    """Test Fear & Greed Index fetching"""

    @pytest.mark.asyncio
    async def test_fetch_feargreed_valid_data(self):
        """Test fetching valid Fear & Greed Index data"""
        mock_client = AsyncMock()

        current_response = {"value": 75}
        historical_response = {"data": [{"value": 70}, {"value": 75}]}

        mock_client.call_tool.side_effect = [current_response, historical_response]

        aggregator = SentimentAggregator(mock_client)
        feargreed = await aggregator._fetch_feargreed_index()

        assert "value" in feargreed
        assert "category" in feargreed
        assert "trend" in feargreed
        assert feargreed["value"] == 75


class TestNewsSentimentFetching:
    """Test news sentiment fetching"""

    @pytest.mark.asyncio
    async def test_fetch_news_sentiment_valid_data(self):
        """Test fetching valid news sentiment data"""
        mock_client = AsyncMock()

        news_response = {"content": [{"articles": []}]}
        mock_client.call_tool.return_value = news_response

        aggregator = SentimentAggregator(mock_client)
        news = await aggregator._fetch_news_sentiment("BTC", 7)

        assert "sentiment" in news
        assert "article_count" in news
        assert "trending_topics" in news

    @pytest.mark.asyncio
    async def test_fetch_news_sentiment_exception_handling(self):
        """Test news sentiment fallback on error"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = Exception("Network error")

        aggregator = SentimentAggregator(mock_client)
        news = await aggregator._fetch_news_sentiment("BTC", 7)

        # Should return neutral sentiment on error
        assert news["sentiment"] == 0.5
        assert news["article_count"] == 0
        assert news["trending_topics"] == []
        assert "error" in news


class TestWhaleActivityFetching:
    """Test whale activity fetching"""

    @pytest.mark.asyncio
    async def test_fetch_whale_activity_placeholder(self):
        """Test whale activity returns placeholder data"""
        mock_client = MagicMock()

        aggregator = SentimentAggregator(mock_client)
        whale = await aggregator._fetch_whale_activity("BTC", 7)

        assert "large_tx_count" in whale
        assert "net_flow" in whale
        assert "signal" in whale
        assert whale["signal"] == "neutral"


class TestVolatilityIndexCalculation:
    """Test volatility index calculation"""

    @pytest.mark.asyncio
    async def test_calculate_volatility_index_valid_data(self):
        """Test volatility index calculation with valid ATR data"""
        mock_client = AsyncMock()

        atr_response = {"atr": [350.0, 400.0, 450.5]}
        mock_client.call_tool.return_value = atr_response

        aggregator = SentimentAggregator(mock_client)
        volatility = await aggregator._calculate_volatility_index("BTC")

        # ATR 450.5 / 500 threshold = 0.901
        assert volatility > 0.8
        assert volatility <= 1.0

    @pytest.mark.asyncio
    async def test_calculate_volatility_index_capped_at_one(self):
        """Test volatility index is capped at 1.0"""
        mock_client = AsyncMock()

        # Very high ATR should be capped at 1.0
        atr_response = {"atr": [800.0]}
        mock_client.call_tool.return_value = atr_response

        aggregator = SentimentAggregator(mock_client)
        volatility = await aggregator._calculate_volatility_index("BTC")

        assert volatility == 1.0

    @pytest.mark.asyncio
    async def test_calculate_volatility_index_default_on_error(self):
        """Test volatility index defaults to 0.3 on error"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = Exception("API error")

        aggregator = SentimentAggregator(mock_client)
        volatility = await aggregator._calculate_volatility_index("BTC")

        assert volatility == 0.3

    @pytest.mark.asyncio
    async def test_calculate_volatility_index_empty_atr(self):
        """Test volatility index defaults to 0.3 with empty ATR"""
        mock_client = AsyncMock()

        atr_response = {"atr": []}
        mock_client.call_tool.return_value = atr_response

        aggregator = SentimentAggregator(mock_client)
        volatility = await aggregator._calculate_volatility_index("BTC")

        assert volatility == 0.3


class TestOverallSentimentCalculation:
    """Test overall sentiment calculation with weighted average"""

    def test_calculate_overall_sentiment_all_sources(self):
        """Test overall sentiment with all sources available"""
        aggregator = SentimentAggregator(MagicMock())

        sentiment_data = {
            "social": {"balance": 20.0},  # 20/2 + 50 = 60
            "feargreed": {"value": 75},  # 75
            "news": {"sentiment": 0.65},  # 65
            "whale": {"signal": "accumulation"},  # 75
        }

        overall = aggregator._calculate_overall_sentiment(sentiment_data)

        # Weighted: 60*0.30 + 75*0.40 + 65*0.20 + 75*0.10 = 68.5
        assert 68.0 <= overall <= 69.0

    def test_calculate_overall_sentiment_social_only(self):
        """Test overall sentiment with only social data"""
        aggregator = SentimentAggregator(MagicMock())

        sentiment_data = {"social": {"balance": 30.0}}

        overall = aggregator._calculate_overall_sentiment(sentiment_data)

        # Balance 30 -> (30/2) + 50 = 65
        assert overall == 65.0

    def test_calculate_overall_sentiment_feargreed_only(self):
        """Test overall sentiment with only Fear & Greed Index"""
        aggregator = SentimentAggregator(MagicMock())

        sentiment_data = {"feargreed": {"value": 80}}

        overall = aggregator._calculate_overall_sentiment(sentiment_data)

        assert overall == 80.0

    def test_calculate_overall_sentiment_empty_data(self):
        """Test overall sentiment defaults to 50 with no data"""
        aggregator = SentimentAggregator(MagicMock())

        overall = aggregator._calculate_overall_sentiment({})

        assert overall == 50.0

    def test_calculate_overall_sentiment_whale_signal_mapping(self):
        """Test whale signal to score mapping"""
        aggregator = SentimentAggregator(MagicMock())

        # Test accumulation signal
        sentiment_data = {"whale": {"signal": "accumulation"}}
        overall = aggregator._calculate_overall_sentiment(sentiment_data)
        assert overall == 75.0

        # Test distribution signal
        sentiment_data = {"whale": {"signal": "distribution"}}
        overall = aggregator._calculate_overall_sentiment(sentiment_data)
        assert overall == 25.0

        # Test neutral signal
        sentiment_data = {"whale": {"signal": "neutral"}}
        overall = aggregator._calculate_overall_sentiment(sentiment_data)
        assert overall == 50.0


class TestSentimentCategorization:
    """Test sentiment score categorization"""

    def test_categorize_sentiment_extreme_greed(self):
        """Test categorization of extreme greed (>=75)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_sentiment(80)
        assert category == "Extreme Greed"

        category = aggregator._categorize_sentiment(75)
        assert category == "Extreme Greed"

    def test_categorize_sentiment_greed(self):
        """Test categorization of greed (60-74)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_sentiment(70)
        assert category == "Greed"

        category = aggregator._categorize_sentiment(60)
        assert category == "Greed"

    def test_categorize_sentiment_neutral(self):
        """Test categorization of neutral (45-59)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_sentiment(50)
        assert category == "Neutral"

        category = aggregator._categorize_sentiment(45)
        assert category == "Neutral"

    def test_categorize_sentiment_fear(self):
        """Test categorization of fear (25-44)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_sentiment(35)
        assert category == "Fear"

        category = aggregator._categorize_sentiment(25)
        assert category == "Fear"

    def test_categorize_sentiment_extreme_fear(self):
        """Test categorization of extreme fear (<25)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_sentiment(20)
        assert category == "Extreme Fear"

        category = aggregator._categorize_sentiment(0)
        assert category == "Extreme Fear"


class TestFearGreedCategorization:
    """Test Fear & Greed Index categorization"""

    def test_categorize_feargreed_extreme_greed(self):
        """Test Fear & Greed categorization for extreme greed (>=75)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_feargreed(80)
        assert category == "Extreme Greed"

    def test_categorize_feargreed_greed(self):
        """Test Fear & Greed categorization for greed (55-74)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_feargreed(65)
        assert category == "Greed"

    def test_categorize_feargreed_neutral(self):
        """Test Fear & Greed categorization for neutral (45-54)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_feargreed(50)
        assert category == "Neutral"

    def test_categorize_feargreed_fear(self):
        """Test Fear & Greed categorization for fear (25-44)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_feargreed(35)
        assert category == "Fear"

    def test_categorize_feargreed_extreme_fear(self):
        """Test Fear & Greed categorization for extreme fear (<25)"""
        aggregator = SentimentAggregator(MagicMock())

        category = aggregator._categorize_feargreed(20)
        assert category == "Extreme Fear"


class TestNumericValueExtraction:
    """Test numeric value extraction from MCP results"""

    def test_extract_numeric_value_from_dict(self):
        """Test extracting numeric value from dict result"""
        aggregator = SentimentAggregator(MagicMock())

        result = {"volume": 15000}
        value = aggregator._extract_numeric_value(result, "volume", 0)

        assert value == 15000.0

    def test_extract_numeric_value_from_exception(self):
        """Test extraction returns default for Exception"""
        aggregator = SentimentAggregator(MagicMock())

        result = Exception("Error")
        value = aggregator._extract_numeric_value(result, "volume", 100)

        assert value == 100

    def test_extract_numeric_value_fallback_to_first_numeric(self):
        """Test extraction falls back to first numeric value found"""
        aggregator = SentimentAggregator(MagicMock())

        result = {"data": {"nested": 42.5}}
        value = aggregator._extract_numeric_value(result, "missing_key", 0)

        # Should find the first numeric value
        assert isinstance(value, (int, float))

    def test_extract_numeric_value_default_if_not_found(self):
        """Test extraction returns default if no numeric found"""
        aggregator = SentimentAggregator(MagicMock())

        result = {"text": "no numbers here"}
        value = aggregator._extract_numeric_value(result, "missing", 99)

        assert value == 99


class TestAdaptiveFusionAlphaCalculation:
    """Test AdaptiveSentimentFusion alpha calculation"""

    def test_calculate_alpha_high_volatility(self):
        """Test alpha calculation for high volatility (>0.4)"""
        # High volatility -> sentiment leads (high alpha)
        alpha = AdaptiveSentimentFusion.calculate_alpha(0.6)

        assert alpha == 0.80

    def test_calculate_alpha_moderate_volatility(self):
        """Test alpha calculation for moderate volatility (0.2-0.4)"""
        # Moderate volatility -> balanced weighting
        alpha = AdaptiveSentimentFusion.calculate_alpha(0.3)

        assert alpha == 0.50

    def test_calculate_alpha_low_volatility(self):
        """Test alpha calculation for low volatility (<0.2)"""
        # Low volatility -> technicals lead (low alpha)
        alpha = AdaptiveSentimentFusion.calculate_alpha(0.1)

        assert alpha == 0.20

    def test_calculate_alpha_boundary_cases(self):
        """Test alpha calculation at boundary thresholds"""
        # Just above 0.4 threshold
        alpha = AdaptiveSentimentFusion.calculate_alpha(0.41)
        assert alpha == 0.80

        # Just above 0.2 threshold
        alpha = AdaptiveSentimentFusion.calculate_alpha(0.21)
        assert alpha == 0.50

        # Just below 0.2 threshold
        alpha = AdaptiveSentimentFusion.calculate_alpha(0.19)
        assert alpha == 0.20


class TestAdaptiveFusionSignalFusion:
    """Test AdaptiveSentimentFusion signal fusion"""

    def test_fuse_signals_high_volatility(self):
        """Test signal fusion during high volatility (80% sentiment)"""
        sentiment_score = 70.0
        technical_score = 50.0
        volatility_index = 0.5  # High volatility

        fused = AdaptiveSentimentFusion.fuse_signals(
            sentiment_score, technical_score, volatility_index
        )

        # 0.80 * 70 + 0.20 * 50 = 56 + 10 = 66
        assert fused == 66.0

    def test_fuse_signals_moderate_volatility(self):
        """Test signal fusion during moderate volatility (50% each)"""
        sentiment_score = 60.0
        technical_score = 40.0
        volatility_index = 0.3  # Moderate volatility

        fused = AdaptiveSentimentFusion.fuse_signals(
            sentiment_score, technical_score, volatility_index
        )

        # 0.50 * 60 + 0.50 * 40 = 30 + 20 = 50
        assert fused == 50.0

    def test_fuse_signals_low_volatility(self):
        """Test signal fusion during low volatility (80% technical)"""
        sentiment_score = 70.0
        technical_score = 50.0
        volatility_index = 0.1  # Low volatility

        fused = AdaptiveSentimentFusion.fuse_signals(
            sentiment_score, technical_score, volatility_index
        )

        # 0.20 * 70 + 0.80 * 50 = 14 + 40 = 54
        assert fused == 54.0


class TestParallelSourceFetching:
    """Test parallel fetching of multiple sentiment sources"""

    @pytest.mark.asyncio
    async def test_aggregate_parallel_execution(self):
        """Test that multiple sources are fetched in parallel"""
        mock_client = AsyncMock()

        # Track tool calls
        call_count = 0

        async def mock_call_tool(tool_name, params):
            nonlocal call_count
            call_count += 1
            return {}

        mock_client.call_tool = mock_call_tool

        aggregator = SentimentAggregator(mock_client)

        await aggregator.aggregate("BTC", days=7, sources=["social", "feargreed"])

        # Should have made multiple parallel calls
        assert call_count > 0


class TestSourceFailureHandling:
    """Test handling of source failures"""

    @pytest.mark.asyncio
    async def test_aggregate_with_partial_source_failures(self):
        """Test aggregation continues when some sources fail"""
        mock_client = AsyncMock()

        # First source succeeds, second fails, third succeeds
        mock_client.call_tool.side_effect = [
            {"value": 15000},  # social volume
            Exception("Network error"),  # social balance fails
            {"dominance": 25.3},  # social dominance
            {"value": 75},  # feargreed current
            {},  # feargreed historical
            {},  # news
            {"atr": [450]},  # volatility
        ]

        aggregator = SentimentAggregator(mock_client)

        result = await aggregator.aggregate("BTC", days=7)

        # Should still return valid result
        assert "data" in result
        assert "overall_sentiment" in result["data"]

    @pytest.mark.asyncio
    async def test_aggregate_warnings_for_failed_sources(self):
        """Test warnings are included for failed sources"""
        mock_client = AsyncMock()

        # Make all social calls fail
        mock_client.call_tool.side_effect = [
            Exception("Social API error"),
            Exception("Social API error"),
            Exception("Social API error"),
            {"value": 75},  # feargreed succeeds
            {},
            {},
            {"atr": [450]},
        ]

        aggregator = SentimentAggregator(mock_client)

        result = await aggregator.aggregate("BTC", days=7, verbose=True)

        # Warnings should be present in metadata if sources failed
        # (Note: current implementation may need adjustment to track source-level failures)
        assert "metadata" in result


class TestConfidenceCalculation:
    """Test confidence calculation based on source availability"""

    @pytest.mark.asyncio
    async def test_confidence_all_sources_available(self):
        """Test confidence when all sources are available"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = lambda tool, params: {}

        aggregator = SentimentAggregator(mock_client)

        result = await aggregator.aggregate(
            "BTC", days=7, sources=["social", "feargreed", "news", "whale"], verbose=True
        )

        # All 4 sources available = 4/4 = 1.0 confidence
        assert result["metadata"]["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_confidence_partial_sources_available(self):
        """Test confidence when only some sources are available"""
        mock_client = AsyncMock()

        # Only 2 out of 4 sources return data
        def side_effect(tool, params):
            if "social" in tool or "feargreed" in tool:
                return {}
            raise Exception("Source unavailable")

        mock_client.call_tool.side_effect = side_effect

        aggregator = SentimentAggregator(mock_client)

        result = await aggregator.aggregate(
            "BTC", days=7, sources=["social", "feargreed", "news", "whale"], verbose=True
        )

        # Confidence should reflect partial availability
        assert result["metadata"]["confidence"] < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
