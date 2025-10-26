"""
Unit Tests for CryptoSentimentAnalyst

Tests the Crypto Sentiment Analyst Agent's functionality including:
- Crowd sentiment analysis
- Sentiment extreme detection
- Whale activity tracking
- News sentiment analysis
- Contrarian signal generation
- Sentiment synthesis
- Metadata and capabilities
"""

import pytest
import asyncio
from agents import (
    CryptoSentimentAnalyst,
    SentimentRegime,
    ContrarianSignal,
    analyze_crypto_sentiment,
)


class TestCryptoSentimentAnalystInit:
    """Test CryptoSentimentAnalyst initialization"""

    def test_init_without_mcp_client(self):
        """Test initialization without MCP client"""
        analyst = CryptoSentimentAnalyst()
        assert analyst.name == "crypto_sentiment_analyst"
        assert analyst.description == "Market psychology and behavioral finance analysis"
        assert analyst.mcp_client is None

    def test_init_with_mcp_client(self):
        """Test initialization with MCP client"""
        mock_client = "mock_mcp_client"
        analyst = CryptoSentimentAnalyst(mcp_client=mock_client)
        assert analyst.mcp_client == mock_client

    def test_required_servers(self):
        """Test required MCP servers list"""
        analyst = CryptoSentimentAnalyst()
        assert "crypto-sentiment-mcp" in analyst.required_servers
        assert "crypto-feargreed-mcp" in analyst.required_servers
        assert "cryptopanic-mcp-server" in analyst.required_servers
        assert len(analyst.required_servers) == 3

    def test_optional_servers(self):
        """Test optional MCP servers list"""
        analyst = CryptoSentimentAnalyst()
        assert "grok-search-mcp" in analyst.optional_servers


class TestAnalyzeCrowdSentiment:
    """Test analyze_crowd_sentiment() method"""

    @pytest.mark.asyncio
    async def test_analyze_crowd_sentiment_default(self):
        """Test crowd sentiment analysis with defaults"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.analyze_crowd_sentiment("bitcoin")

        # Verify structure
        assert "fear_greed_index" in result
        assert "sentiment_regime" in result
        assert "social_metrics" in result
        assert "contrarian_signal" in result
        assert "interpretation" in result

        # Verify Fear & Greed Index
        assert 0 <= result["fear_greed_index"] <= 100

        # Verify sentiment regime is valid enum value
        assert result["sentiment_regime"] in [regime.value for regime in SentimentRegime]

        # Verify social metrics
        social = result["social_metrics"]
        assert "social_volume" in social
        assert "social_dominance" in social
        assert "sentiment_balance" in social
        assert isinstance(social["social_volume"], int)
        assert social["social_volume"] >= 0
        assert 0.0 <= social["social_dominance"] <= 100.0
        assert isinstance(social["sentiment_balance"], (int, float))

        # Verify contrarian signal is valid
        assert result["contrarian_signal"] in ["strong_buy", "buy", "hold", "sell", "strong_sell"]

        # Verify interpretation is non-empty
        assert isinstance(result["interpretation"], str)
        assert len(result["interpretation"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_crowd_sentiment_custom_asset(self):
        """Test crowd sentiment with custom asset"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.analyze_crowd_sentiment("ethereum")

        assert "fear_greed_index" in result
        assert "sentiment_regime" in result

    @pytest.mark.asyncio
    async def test_sentiment_regime_matches_fear_greed(self):
        """Test that sentiment_regime matches fear_greed_index"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.analyze_crowd_sentiment("bitcoin")

        fg_index = result["fear_greed_index"]
        regime = result["sentiment_regime"]

        # Verify logical consistency
        if fg_index <= 25:
            assert regime == "extreme_fear"
        elif fg_index >= 75:
            assert regime == "extreme_greed"
        elif fg_index <= 45:
            assert regime == "fear"
        elif fg_index >= 55:
            assert regime == "greed"
        else:
            assert regime == "neutral"


class TestDetectSentimentExtremes:
    """Test detect_sentiment_extremes() method"""

    @pytest.mark.asyncio
    async def test_detect_sentiment_extremes_default(self):
        """Test sentiment extreme detection with defaults"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.detect_sentiment_extremes("bitcoin")

        # Verify structure
        assert "current_percentile" in result
        assert "current_signal" in result
        assert "extreme_events" in result
        assert "pattern_analysis" in result

        # Verify current percentile
        assert 0 <= result["current_percentile"] <= 100

        # Verify current signal
        assert result["current_signal"] in [
            "extreme_fear_buy",
            "extreme_greed_sell",
            "fear_accumulate",
            "greed_reduce",
            "neutral",
        ]

        # Verify extreme events is a list
        assert isinstance(result["extreme_events"], list)

        # Verify pattern analysis
        pattern = result["pattern_analysis"]
        assert "mean_reversion_timeframe" in pattern
        assert "extreme_frequency" in pattern
        assert "current_deviation" in pattern

    @pytest.mark.asyncio
    async def test_detect_sentiment_extremes_custom_lookback(self):
        """Test sentiment extremes with custom lookback period"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.detect_sentiment_extremes("bitcoin", lookback_days=180)

        assert "current_percentile" in result
        assert "extreme_events" in result

    @pytest.mark.asyncio
    async def test_extreme_events_structure(self):
        """Test that extreme events have correct structure"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.detect_sentiment_extremes("bitcoin")

        if len(result["extreme_events"]) > 0:
            event = result["extreme_events"][0]
            assert "date" in event
            assert "fear_greed" in event
            assert "outcome" in event
            assert 0 <= event["fear_greed"] <= 100


class TestTrackWhaleActivity:
    """Test track_whale_activity() method"""

    @pytest.mark.asyncio
    async def test_track_whale_activity_default(self):
        """Test whale activity tracking with defaults"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.track_whale_activity("BTC")

        # Verify structure
        assert "large_transactions" in result
        assert "whale_sentiment" in result
        assert "exchange_flows" in result
        assert "interpretation" in result

        # Verify large transactions
        transactions = result["large_transactions"]
        assert "count" in transactions
        assert "total_value" in transactions
        assert "net_direction" in transactions
        assert isinstance(transactions["count"], int)
        assert transactions["count"] >= 0
        assert isinstance(transactions["total_value"], (int, float))
        assert transactions["net_direction"] in ["accumulation", "distribution", "neutral"]

        # Verify whale sentiment
        assert result["whale_sentiment"] in ["bullish", "bearish", "neutral"]

        # Verify exchange flows
        flows = result["exchange_flows"]
        assert "inflow" in flows
        assert "outflow" in flows
        assert "net_flow" in flows
        assert isinstance(flows["inflow"], (int, float))
        assert isinstance(flows["outflow"], (int, float))

        # Verify interpretation
        assert isinstance(result["interpretation"], str)
        assert len(result["interpretation"]) > 0

    @pytest.mark.asyncio
    async def test_track_whale_activity_custom_period(self):
        """Test whale tracking with custom period"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.track_whale_activity("BTC", period_hours=48)

        assert "large_transactions" in result
        assert "whale_sentiment" in result


class TestAnalyzeNewsSentiment:
    """Test analyze_news_sentiment() method"""

    @pytest.mark.asyncio
    async def test_analyze_news_sentiment_default(self):
        """Test news sentiment analysis with defaults"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.analyze_news_sentiment("bitcoin")

        # Verify structure
        assert "overall_sentiment" in result
        assert "sentiment_score" in result
        assert "trending_topics" in result
        assert "key_narratives" in result
        assert "news_volume" in result

        # Verify overall sentiment
        assert result["overall_sentiment"] in ["bullish", "bearish", "neutral"]

        # Verify sentiment score
        assert -1.0 <= result["sentiment_score"] <= 1.0

        # Verify trending topics is a list
        assert isinstance(result["trending_topics"], list)

        # Verify key narratives is a list
        assert isinstance(result["key_narratives"], list)

        # Verify news volume
        assert isinstance(result["news_volume"], int)
        assert result["news_volume"] >= 0

    @pytest.mark.asyncio
    async def test_analyze_news_sentiment_custom_period(self):
        """Test news sentiment with custom period"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.analyze_news_sentiment("bitcoin", period_hours=48)

        assert "overall_sentiment" in result
        assert "sentiment_score" in result

    @pytest.mark.asyncio
    async def test_sentiment_score_matches_overall(self):
        """Test that sentiment_score matches overall_sentiment"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.analyze_news_sentiment("bitcoin")

        score = result["sentiment_score"]
        sentiment = result["overall_sentiment"]

        # Verify logical consistency
        if score > 0.2:
            assert sentiment == "bullish"
        elif score < -0.2:
            assert sentiment == "bearish"
        else:
            assert sentiment == "neutral"


class TestGenerateContrarianSignal:
    """Test generate_contrarian_signal() method"""

    @pytest.mark.asyncio
    async def test_generate_contrarian_signal_default(self):
        """Test contrarian signal generation with defaults"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.generate_contrarian_signal("bitcoin")

        # Verify structure
        assert "signal" in result
        assert "confidence" in result
        assert "entry_timing" in result
        assert "exit_timing" in result
        assert "rationale" in result

        # Verify signal is valid enum value
        assert result["signal"] in [signal.value for signal in ContrarianSignal]

        # Verify confidence
        assert 0.0 <= result["confidence"] <= 1.0

        # Verify entry timing
        assert result["entry_timing"] in [
            "immediate",
            "wait_for_confirmation",
            "dca_over_time",
            "no_action",
        ]

        # Verify exit timing
        assert result["exit_timing"] in [
            "hold",
            "take_partial_profits",
            "exit_on_reversal",
            "no_position",
        ]

        # Verify rationale
        rationale = result["rationale"]
        assert "sentiment_extreme" in rationale
        assert "historical_pattern" in rationale
        assert "risk_reward" in rationale

    @pytest.mark.asyncio
    async def test_generate_contrarian_signal_custom_asset(self):
        """Test contrarian signal with custom asset"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.generate_contrarian_signal("ethereum")

        assert "signal" in result
        assert "confidence" in result


class TestSynthesizeSentimentOutlook:
    """Test synthesize_sentiment_outlook() method"""

    @pytest.mark.asyncio
    async def test_synthesize_sentiment_outlook_default(self):
        """Test sentiment outlook synthesis with defaults"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.synthesize_sentiment_outlook("bitcoin")

        # Verify structure
        assert "sentiment_assessment" in result
        assert "confidence" in result
        assert "crowd_analysis" in result
        assert "whale_analysis" in result
        assert "news_analysis" in result
        assert "contrarian_opportunity" in result
        assert "timing_recommendation" in result
        assert "reasoning" in result

        # Verify sentiment assessment
        assert result["sentiment_assessment"] in [
            "extreme_fear_buy_opportunity",
            "fear_accumulate",
            "neutral",
            "greed_reduce",
            "extreme_greed_sell_signal",
        ]

        # Verify confidence
        assert 0.0 <= result["confidence"] <= 1.0

        # Verify sub-analyses are present
        assert "fear_greed_index" in result["crowd_analysis"]
        assert "whale_sentiment" in result["whale_analysis"]
        assert "overall_sentiment" in result["news_analysis"]

        # Verify contrarian opportunity
        assert isinstance(result["contrarian_opportunity"], bool)

        # Verify timing recommendation
        assert result["timing_recommendation"] in [
            "strong_buy",
            "buy",
            "accumulate",
            "hold",
            "reduce",
            "sell",
            "strong_sell",
        ]

        # Verify reasoning
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0

    @pytest.mark.asyncio
    async def test_synthesize_sentiment_outlook_custom_horizon(self):
        """Test sentiment outlook with custom horizon"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.synthesize_sentiment_outlook("bitcoin", horizon_days=60)

        assert "sentiment_assessment" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_synthesize_calls_sub_methods(self):
        """Test that synthesize calls all sub-methods"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.synthesize_sentiment_outlook("bitcoin")

        # Verify all sub-analyses are included
        assert "crowd_analysis" in result
        assert "whale_analysis" in result
        assert "news_analysis" in result

        # Verify reasoning mentions key concepts
        reasoning = result["reasoning"].lower()
        assert len(reasoning) > 100  # Should be comprehensive


class TestGetCapabilities:
    """Test get_capabilities() method"""

    def test_get_capabilities_structure(self):
        """Test capabilities metadata structure"""
        analyst = CryptoSentimentAnalyst()
        capabilities = analyst.get_capabilities()

        # Verify required fields
        assert "name" in capabilities
        assert "description" in capabilities
        assert "type" in capabilities
        assert "domain" in capabilities
        assert "capabilities" in capabilities
        assert "required_mcps" in capabilities
        assert "optional_mcps" in capabilities
        assert "token_efficiency" in capabilities
        assert "use_cases" in capabilities

    def test_get_capabilities_values(self):
        """Test capabilities metadata values"""
        analyst = CryptoSentimentAnalyst()
        capabilities = analyst.get_capabilities()

        assert capabilities["name"] == "crypto_sentiment_analyst"
        assert capabilities["type"] == "specialized_agent"
        assert capabilities["domain"] == "behavioral_finance"
        assert capabilities["token_efficiency"] == 0.0  # Agents have no token reduction

        # Verify capabilities list
        assert "crowd_sentiment_analysis" in capabilities["capabilities"]
        assert "sentiment_extreme_detection" in capabilities["capabilities"]
        assert "whale_activity_tracking" in capabilities["capabilities"]
        assert "news_sentiment_analysis" in capabilities["capabilities"]
        assert "contrarian_signal_generation" in capabilities["capabilities"]
        assert "sentiment_synthesis" in capabilities["capabilities"]

        # Verify MCP servers
        assert "crypto-sentiment-mcp" in capabilities["required_mcps"]
        assert "crypto-feargreed-mcp" in capabilities["required_mcps"]
        assert "cryptopanic-mcp-server" in capabilities["required_mcps"]
        assert "grok-search-mcp" in capabilities["optional_mcps"]

        # Verify use cases
        assert isinstance(capabilities["use_cases"], list)
        assert len(capabilities["use_cases"]) > 0


class TestConvenienceFunction:
    """Test analyze_crypto_sentiment() convenience function"""

    @pytest.mark.asyncio
    async def test_analyze_crypto_sentiment_crowd(self):
        """Test convenience function with crowd analysis"""
        result = await analyze_crypto_sentiment("bitcoin", "crowd")
        assert "fear_greed_index" in result
        assert "sentiment_regime" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_sentiment_extremes(self):
        """Test convenience function with extremes analysis"""
        result = await analyze_crypto_sentiment("bitcoin", "extremes")
        assert "current_percentile" in result
        assert "current_signal" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_sentiment_whales(self):
        """Test convenience function with whale analysis"""
        result = await analyze_crypto_sentiment("bitcoin", "whales")
        assert "large_transactions" in result
        assert "whale_sentiment" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_sentiment_news(self):
        """Test convenience function with news analysis"""
        result = await analyze_crypto_sentiment("bitcoin", "news")
        assert "overall_sentiment" in result
        assert "sentiment_score" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_sentiment_signal(self):
        """Test convenience function with contrarian signal"""
        result = await analyze_crypto_sentiment("bitcoin", "signal")
        assert "signal" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_sentiment_full(self):
        """Test convenience function with full synthesis"""
        result = await analyze_crypto_sentiment("bitcoin", "full")
        assert "sentiment_assessment" in result
        assert "confidence" in result
        assert "timing_recommendation" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_sentiment_invalid_type(self):
        """Test convenience function with invalid analysis type"""
        with pytest.raises(ValueError) as exc_info:
            await analyze_crypto_sentiment("bitcoin", "invalid_type")
        assert "Invalid analysis_type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_analyze_crypto_sentiment_with_kwargs(self):
        """Test convenience function with additional kwargs"""
        result = await analyze_crypto_sentiment("ethereum", "extremes", lookback_days=180)
        assert "current_percentile" in result


class TestSentimentRegimeEnum:
    """Test SentimentRegime enum"""

    def test_sentiment_regime_values(self):
        """Test SentimentRegime enum has expected values"""
        assert SentimentRegime.EXTREME_FEAR.value == "extreme_fear"
        assert SentimentRegime.FEAR.value == "fear"
        assert SentimentRegime.NEUTRAL.value == "neutral"
        assert SentimentRegime.GREED.value == "greed"
        assert SentimentRegime.EXTREME_GREED.value == "extreme_greed"

    def test_sentiment_regime_all_members(self):
        """Test SentimentRegime has all expected members"""
        regimes = [regime.value for regime in SentimentRegime]
        assert "extreme_fear" in regimes
        assert "fear" in regimes
        assert "neutral" in regimes
        assert "greed" in regimes
        assert "extreme_greed" in regimes
        assert len(regimes) == 5


class TestContrarianSignalEnum:
    """Test ContrarianSignal enum"""

    def test_contrarian_signal_values(self):
        """Test ContrarianSignal enum has expected values"""
        assert ContrarianSignal.STRONG_BUY.value == "strong_buy"
        assert ContrarianSignal.BUY.value == "buy"
        assert ContrarianSignal.HOLD.value == "hold"
        assert ContrarianSignal.SELL.value == "sell"
        assert ContrarianSignal.STRONG_SELL.value == "strong_sell"

    def test_contrarian_signal_all_members(self):
        """Test ContrarianSignal has all expected members"""
        signals = [signal.value for signal in ContrarianSignal]
        assert "strong_buy" in signals
        assert "buy" in signals
        assert "hold" in signals
        assert "sell" in signals
        assert "strong_sell" in signals
        assert len(signals) == 5


class TestAsyncPatterns:
    """Test async/await patterns"""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test that multiple async calls can run in parallel"""
        analyst = CryptoSentimentAnalyst()

        # Run multiple methods in parallel
        results = await asyncio.gather(
            analyst.analyze_crowd_sentiment("bitcoin"),
            analyst.track_whale_activity("BTC"),
            analyst.analyze_news_sentiment("bitcoin"),
        )

        assert len(results) == 3
        assert "fear_greed_index" in results[0]
        assert "large_transactions" in results[1]
        assert "overall_sentiment" in results[2]

    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Test that sequential execution works correctly"""
        analyst = CryptoSentimentAnalyst()

        # Run methods sequentially
        crowd = await analyst.analyze_crowd_sentiment("bitcoin")
        whales = await analyst.track_whale_activity("BTC")
        news = await analyst.analyze_news_sentiment("bitcoin")

        assert "fear_greed_index" in crowd
        assert "large_transactions" in whales
        assert "overall_sentiment" in news

    @pytest.mark.asyncio
    async def test_synthesis_integration(self):
        """Test that synthesis correctly integrates all sub-analyses"""
        analyst = CryptoSentimentAnalyst()
        result = await analyst.synthesize_sentiment_outlook("bitcoin")

        # Verify all sub-analyses are present and valid
        assert 0 <= result["crowd_analysis"]["fear_greed_index"] <= 100
        assert result["whale_analysis"]["whale_sentiment"] in [
            "bullish",
            "bearish",
            "neutral",
        ]
        assert result["news_analysis"]["overall_sentiment"] in [
            "bullish",
            "bearish",
            "neutral",
        ]

        # Verify synthesis produces coherent output
        assert result["sentiment_assessment"] in [
            "extreme_fear_buy_opportunity",
            "fear_accumulate",
            "neutral",
            "greed_reduce",
            "extreme_greed_sell_signal",
        ]
