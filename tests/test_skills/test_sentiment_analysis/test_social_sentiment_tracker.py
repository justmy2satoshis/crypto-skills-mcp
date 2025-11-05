"""
Unit tests for SocialSentimentTracker Skill

Tests social sentiment tracking functionality including:
- Sentiment balance extraction and conversion (-100/+100 to 0-100 scale)
- Social volume extraction and parsing
- Social dominance extraction (percentage)
- Fear & Greed Index integration
- Sentiment categorization (Extreme Greed, Greed, Neutral, Fear, Extreme Fear)
- Trend and momentum calculation
- Volume spike detection
- Fear & Greed alignment checking
- Trading signal generation
- Risk level assessment
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

from skills.sentiment_analysis.social_sentiment_tracker import SocialSentimentTracker


class TestSocialSentimentTrackerInit:
    """Test SocialSentimentTracker initialization"""

    def test_initialization(self):
        """Test tracker initializes with MCP client"""
        mock_client = MagicMock()
        tracker = SocialSentimentTracker(mock_client)

        assert tracker.mcp == mock_client
        assert tracker is not None


class TestTrackMethod:
    """Test main track() method"""

    @pytest.fixture
    def mock_mcp_responses(self):
        """Mock MCP responses for sentiment tracking"""
        return {
            "sentiment_balance": {
                "content": [
                    {"text": "Bitcoin's sentiment balance over the past 7 days is 12.5"}
                ]
            },
            "social_volume": {
                "content": [
                    {"text": "Bitcoin's social volume over the past 7 days is 15,000 mentions"}
                ]
            },
            "social_dominance": {
                "content": [
                    {"text": "Bitcoin's social dominance over the past 7 days is 25.3%"}
                ]
            },
            "fear_greed": {
                "content": [
                    {"text": "Current Fear & Greed Index: 68 (Greed)"}
                ]
            },
        }

    @pytest.mark.asyncio
    async def test_track_basic_call(self, mock_mcp_responses):
        """Test basic track() call returns correct structure"""
        mock_client = AsyncMock()

        # Mock MCP calls
        mock_client.call_tool.side_effect = [
            mock_mcp_responses["sentiment_balance"],
            mock_mcp_responses["social_volume"],
            mock_mcp_responses["social_dominance"],
            mock_mcp_responses["fear_greed"],
        ]

        tracker = SocialSentimentTracker(mock_client)

        result = await tracker.track("BTC", days=7)

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "sentiment-analysis-skill"
        assert "symbol" in result
        assert result["symbol"] == "BTC"
        assert "data_type" in result
        assert result["data_type"] == "social_sentiment_trend"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_track_verbose_true(self, mock_mcp_responses):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()

        mock_client.call_tool.side_effect = [
            mock_mcp_responses["sentiment_balance"],
            mock_mcp_responses["social_volume"],
            mock_mcp_responses["social_dominance"],
            mock_mcp_responses["fear_greed"],
        ]

        tracker = SocialSentimentTracker(mock_client)

        result = await tracker.track("BTC", days=7, verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "symbol" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "days_analyzed" in result["metadata"]
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_track_verbose_false(self, mock_mcp_responses):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        mock_client = AsyncMock()

        mock_client.call_tool.side_effect = [
            mock_mcp_responses["sentiment_balance"],
            mock_mcp_responses["social_volume"],
            mock_mcp_responses["social_dominance"],
            mock_mcp_responses["fear_greed"],
        ]

        tracker = SocialSentimentTracker(mock_client)

        result = await tracker.track("BTC", days=7, verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_track_data_structure(self, mock_mcp_responses):
        """Test data structure contains all required fields"""
        mock_client = AsyncMock()

        mock_client.call_tool.side_effect = [
            mock_mcp_responses["sentiment_balance"],
            mock_mcp_responses["social_volume"],
            mock_mcp_responses["social_dominance"],
            mock_mcp_responses["fear_greed"],
        ]

        tracker = SocialSentimentTracker(mock_client)

        result = await tracker.track("BTC", days=7)
        data = result["data"]

        # Verify all required data fields
        assert "current_sentiment" in data
        assert "sentiment_category" in data
        assert "trend" in data
        assert "momentum" in data
        assert "volume_spike" in data
        assert "social_dominance" in data
        assert "fear_greed_alignment" in data
        assert "trading_signal" in data
        assert "risk_level" in data

        # Verify data types
        assert isinstance(data["current_sentiment"], float)
        assert isinstance(data["sentiment_category"], str)
        assert isinstance(data["trend"], str)
        assert isinstance(data["momentum"], float)
        assert isinstance(data["volume_spike"], bool)
        assert isinstance(data["social_dominance"], float)
        assert isinstance(data["fear_greed_alignment"], bool)
        assert isinstance(data["trading_signal"], str)
        assert isinstance(data["risk_level"], str)


class TestSentimentBalanceExtraction:
    """Test sentiment balance extraction and conversion"""

    def test_extract_sentiment_balance_valid_data(self):
        """Test extracting sentiment balance from valid response"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {
            "content": [
                {"text": "Bitcoin's sentiment balance over the past 7 days is 12.5"}
            ]
        }

        balance = tracker._extract_sentiment_balance(result)
        assert balance == 12.5

    def test_extract_sentiment_balance_negative_value(self):
        """Test extracting negative sentiment balance"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {
            "content": [
                {"text": "Bitcoin's sentiment balance over the past 7 days is -15.3"}
            ]
        }

        balance = tracker._extract_sentiment_balance(result)
        assert balance == -15.3

    def test_extract_sentiment_balance_exception_handling(self):
        """Test sentiment balance extraction handles exceptions"""
        tracker = SocialSentimentTracker(MagicMock())

        result = Exception("API error")
        balance = tracker._extract_sentiment_balance(result)
        assert balance == 0.0

    def test_extract_sentiment_balance_invalid_format(self):
        """Test sentiment balance extraction handles invalid format"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {"invalid": "format"}
        balance = tracker._extract_sentiment_balance(result)
        assert balance == 0.0

    def test_sentiment_conversion_to_0_100_scale(self):
        """Test conversion from -100/+100 to 0-100 scale"""
        tracker = SocialSentimentTracker(MagicMock())

        # Balance of 0 = sentiment 50
        result = {"content": [{"text": "balance is 0"}]}
        balance = tracker._extract_sentiment_balance(result)
        sentiment = 50 + (balance / 2)
        assert sentiment == 50.0

        # Balance of +50 = sentiment 75
        result = {"content": [{"text": "balance is 50"}]}
        balance = tracker._extract_sentiment_balance(result)
        sentiment = 50 + (balance / 2)
        assert sentiment == 75.0

        # Balance of -50 = sentiment 25
        result = {"content": [{"text": "balance is -50"}]}
        balance = tracker._extract_sentiment_balance(result)
        sentiment = 50 + (balance / 2)
        assert sentiment == 25.0


class TestSocialVolumeExtraction:
    """Test social volume extraction"""

    def test_extract_social_volume_valid_data(self):
        """Test extracting social volume from valid response"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {
            "content": [
                {"text": "Bitcoin's social volume over the past 7 days is 15,000 mentions"}
            ]
        }

        volume = tracker._extract_social_volume(result)
        assert volume == 15000

    def test_extract_social_volume_with_commas(self):
        """Test extracting social volume with comma separators"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {
            "content": [
                {"text": "social volume is 1,250,000 mentions"}
            ]
        }

        volume = tracker._extract_social_volume(result)
        assert volume == 1250000

    def test_extract_social_volume_exception_handling(self):
        """Test social volume extraction handles exceptions"""
        tracker = SocialSentimentTracker(MagicMock())

        result = Exception("Network error")
        volume = tracker._extract_social_volume(result)
        assert volume == 0.0

    def test_extract_social_volume_invalid_format(self):
        """Test social volume extraction handles invalid format"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {"content": [{"invalid": "data"}]}
        volume = tracker._extract_social_volume(result)
        assert volume == 0.0


class TestSocialDominanceExtraction:
    """Test social dominance extraction"""

    def test_extract_social_dominance_valid_data(self):
        """Test extracting social dominance from valid response"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {
            "content": [
                {"text": "Bitcoin's social dominance over the past 7 days is 25.3%"}
            ]
        }

        dominance = tracker._extract_social_dominance(result)
        assert dominance == 25.3

    def test_extract_social_dominance_high_value(self):
        """Test extracting high social dominance percentage"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {
            "content": [
                {"text": "social dominance is 68.7%"}
            ]
        }

        dominance = tracker._extract_social_dominance(result)
        assert dominance == 68.7

    def test_extract_social_dominance_exception_handling(self):
        """Test social dominance extraction handles exceptions"""
        tracker = SocialSentimentTracker(MagicMock())

        result = Exception("API error")
        dominance = tracker._extract_social_dominance(result)
        assert dominance == 0.0

    def test_extract_social_dominance_invalid_format(self):
        """Test social dominance extraction handles invalid format"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {"content": [{"text": "no percentage here"}]}
        dominance = tracker._extract_social_dominance(result)
        assert dominance == 0.0


class TestFearGreedExtraction:
    """Test Fear & Greed Index extraction"""

    def test_extract_fear_greed_valid_data(self):
        """Test extracting Fear & Greed Index from valid response"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {
            "content": [
                {"text": "Current Fear & Greed Index: 68 (Greed)"}
            ]
        }

        value = tracker._extract_fear_greed(result)
        assert value == 68.0

    def test_extract_fear_greed_extreme_fear(self):
        """Test extracting extreme fear value"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {
            "content": [
                {"text": "Fear & Greed Index: 15 (Extreme Fear)"}
            ]
        }

        value = tracker._extract_fear_greed(result)
        assert value == 15.0

    def test_extract_fear_greed_extreme_greed(self):
        """Test extracting extreme greed value"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {
            "content": [
                {"text": "Fear & Greed Index: 92 (Extreme Greed)"}
            ]
        }

        value = tracker._extract_fear_greed(result)
        assert value == 92.0

    def test_extract_fear_greed_exception_handling(self):
        """Test Fear & Greed extraction handles exceptions"""
        tracker = SocialSentimentTracker(MagicMock())

        result = Exception("Network error")
        value = tracker._extract_fear_greed(result)
        assert value == 50.0  # Default neutral

    def test_extract_fear_greed_invalid_format(self):
        """Test Fear & Greed extraction handles invalid format"""
        tracker = SocialSentimentTracker(MagicMock())

        result = {"content": [{"text": "no numbers here"}]}
        value = tracker._extract_fear_greed(result)
        assert value == 50.0  # Default neutral


class TestSentimentCategorization:
    """Test sentiment score categorization"""

    def test_categorize_sentiment_extreme_greed(self):
        """Test extreme greed categorization"""
        tracker = SocialSentimentTracker(MagicMock())

        category = tracker._categorize_sentiment(80.0)
        assert category == "Extreme Greed"

        category = tracker._categorize_sentiment(75.0)
        assert category == "Extreme Greed"

    def test_categorize_sentiment_greed(self):
        """Test greed categorization"""
        tracker = SocialSentimentTracker(MagicMock())

        category = tracker._categorize_sentiment(65.0)
        assert category == "Greed"

        category = tracker._categorize_sentiment(60.0)
        assert category == "Greed"

    def test_categorize_sentiment_neutral(self):
        """Test neutral categorization"""
        tracker = SocialSentimentTracker(MagicMock())

        category = tracker._categorize_sentiment(50.0)
        assert category == "Neutral"

        category = tracker._categorize_sentiment(45.0)
        assert category == "Neutral"

    def test_categorize_sentiment_fear(self):
        """Test fear categorization"""
        tracker = SocialSentimentTracker(MagicMock())

        category = tracker._categorize_sentiment(35.0)
        assert category == "Fear"

        category = tracker._categorize_sentiment(25.0)
        assert category == "Fear"

    def test_categorize_sentiment_extreme_fear(self):
        """Test extreme fear categorization"""
        tracker = SocialSentimentTracker(MagicMock())

        category = tracker._categorize_sentiment(20.0)
        assert category == "Extreme Fear"

        category = tracker._categorize_sentiment(10.0)
        assert category == "Extreme Fear"


class TestTrendMomentumCalculation:
    """Test sentiment trend and momentum calculation"""

    def test_calculate_trend_momentum_strong_increasing(self):
        """Test strong increasing trend calculation"""
        tracker = SocialSentimentTracker(MagicMock())

        trend, momentum = tracker._calculate_trend_momentum(20.0, 7)
        assert trend == "increasing"
        assert momentum == 0.20

    def test_calculate_trend_momentum_moderate_increasing(self):
        """Test moderate increasing trend calculation"""
        tracker = SocialSentimentTracker(MagicMock())

        trend, momentum = tracker._calculate_trend_momentum(10.0, 7)
        assert trend == "increasing"
        assert momentum == 0.10

    def test_calculate_trend_momentum_strong_decreasing(self):
        """Test strong decreasing trend calculation"""
        tracker = SocialSentimentTracker(MagicMock())

        trend, momentum = tracker._calculate_trend_momentum(-20.0, 7)
        assert trend == "decreasing"
        assert momentum == -0.20

    def test_calculate_trend_momentum_moderate_decreasing(self):
        """Test moderate decreasing trend calculation"""
        tracker = SocialSentimentTracker(MagicMock())

        trend, momentum = tracker._calculate_trend_momentum(-10.0, 7)
        assert trend == "decreasing"
        assert momentum == -0.10

    def test_calculate_trend_momentum_stable(self):
        """Test stable trend calculation"""
        tracker = SocialSentimentTracker(MagicMock())

        trend, momentum = tracker._calculate_trend_momentum(0.0, 7)
        assert trend == "stable"
        assert momentum == 0.0

        trend, momentum = tracker._calculate_trend_momentum(3.0, 7)
        assert trend == "stable"
        assert momentum == 0.0


class TestVolumeSpikeDetection:
    """Test volume spike detection"""

    def test_detect_volume_spike_above_threshold(self):
        """Test volume spike detection when above threshold"""
        tracker = SocialSentimentTracker(MagicMock())

        # Threshold 2.0 = baseline * 3 = 30,000
        spike = tracker._detect_volume_spike(35000, threshold=2.0)
        assert spike is True

    def test_detect_volume_spike_below_threshold(self):
        """Test volume spike detection when below threshold"""
        tracker = SocialSentimentTracker(MagicMock())

        # Threshold 2.0 = baseline * 3 = 30,000
        spike = tracker._detect_volume_spike(25000, threshold=2.0)
        assert spike is False

    def test_detect_volume_spike_at_threshold(self):
        """Test volume spike detection at exact threshold"""
        tracker = SocialSentimentTracker(MagicMock())

        # At threshold should not trigger
        spike = tracker._detect_volume_spike(30000, threshold=2.0)
        assert spike is False

    def test_detect_volume_spike_custom_threshold(self):
        """Test volume spike detection with custom threshold"""
        tracker = SocialSentimentTracker(MagicMock())

        # Threshold 1.5 = baseline * 2.5 = 25,000
        spike = tracker._detect_volume_spike(26000, threshold=1.5)
        assert spike is True

        spike = tracker._detect_volume_spike(24000, threshold=1.5)
        assert spike is False


class TestFearGreedAlignment:
    """Test Fear & Greed alignment checking"""

    def test_check_alignment_aligned(self):
        """Test alignment when values are close"""
        tracker = SocialSentimentTracker(MagicMock())

        # Within 20 points
        aligned = tracker._check_alignment(65.0, 70.0)
        assert aligned is True

        aligned = tracker._check_alignment(70.0, 65.0)
        assert aligned is True

        aligned = tracker._check_alignment(50.0, 55.0)
        assert aligned is True

    def test_check_alignment_not_aligned(self):
        """Test alignment when values diverge"""
        tracker = SocialSentimentTracker(MagicMock())

        # More than 20 points apart
        aligned = tracker._check_alignment(60.0, 85.0)
        assert aligned is False

        aligned = tracker._check_alignment(30.0, 60.0)
        assert aligned is False

    def test_check_alignment_exactly_20_points(self):
        """Test alignment at exact 20 point threshold"""
        tracker = SocialSentimentTracker(MagicMock())

        # Exactly 20 points should not be aligned (< 20, not <=)
        aligned = tracker._check_alignment(50.0, 70.0)
        assert aligned is False

    def test_check_alignment_identical(self):
        """Test alignment when values are identical"""
        tracker = SocialSentimentTracker(MagicMock())

        aligned = tracker._check_alignment(65.0, 65.0)
        assert aligned is True


class TestTradingSignalGeneration:
    """Test trading signal generation"""

    def test_generate_trading_signal_extreme_greed_fomo(self):
        """Test FOMO warning signal"""
        tracker = SocialSentimentTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            sentiment=80.0,
            trend="increasing",
            momentum=0.20,
            volume_spike=True,
            alignment=True,
        )

        assert "extreme greed" in signal.lower()
        assert "fomo" in signal.lower()
        assert "profit" in signal.lower()

    def test_generate_trading_signal_bullish_building(self):
        """Test bullish sentiment building signal"""
        tracker = SocialSentimentTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            sentiment=65.0,
            trend="increasing",
            momentum=0.10,
            volume_spike=False,
            alignment=True,
        )

        assert "bullish" in signal.lower()
        assert "fomo" in signal.lower()

    def test_generate_trading_signal_neutral_wait(self):
        """Test neutral wait signal"""
        tracker = SocialSentimentTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            sentiment=50.0,
            trend="stable",
            momentum=0.0,
            volume_spike=False,
            alignment=False,
        )

        assert "neutral" in signal.lower()
        assert "wait" in signal.lower()

    def test_generate_trading_signal_bearish_caution(self):
        """Test bearish caution signal"""
        tracker = SocialSentimentTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            sentiment=35.0,
            trend="decreasing",
            momentum=-0.10,
            volume_spike=False,
            alignment=True,
        )

        assert "bearish" in signal.lower()
        assert "caution" in signal.lower()

    def test_generate_trading_signal_extreme_fear_capitulation(self):
        """Test extreme fear capitulation signal"""
        tracker = SocialSentimentTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            sentiment=20.0,
            trend="decreasing",
            momentum=-0.20,
            volume_spike=True,
            alignment=False,
        )

        assert "extreme fear" in signal.lower()
        assert "capitulation" in signal.lower()
        assert "reversal" in signal.lower()

    def test_generate_trading_signal_mixed(self):
        """Test mixed signals default"""
        tracker = SocialSentimentTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            sentiment=55.0,
            trend="stable",
            momentum=0.05,
            volume_spike=False,
            alignment=False,
        )

        assert "mixed" in signal.lower()


class TestRiskLevelAssessment:
    """Test trading risk level assessment"""

    def test_assess_risk_level_high_risk(self):
        """Test high risk assessment"""
        tracker = SocialSentimentTracker(MagicMock())

        # Extreme sentiment + high momentum + volume spike
        risk = tracker._assess_risk_level(
            sentiment=80.0,
            momentum=0.20,
            volume_spike=True,
        )
        assert risk == "high"

        # Extreme fear scenario
        risk = tracker._assess_risk_level(
            sentiment=20.0,
            momentum=-0.20,
            volume_spike=True,
        )
        assert risk == "high"

    def test_assess_risk_level_moderate_risk(self):
        """Test moderate risk assessment"""
        tracker = SocialSentimentTracker(MagicMock())

        # Extreme sentiment without volume spike
        risk = tracker._assess_risk_level(
            sentiment=80.0,
            momentum=0.10,
            volume_spike=False,
        )
        assert risk == "moderate"

        # High momentum without extreme sentiment
        risk = tracker._assess_risk_level(
            sentiment=60.0,
            momentum=0.20,
            volume_spike=False,
        )
        assert risk == "moderate"

    def test_assess_risk_level_low_risk(self):
        """Test low risk assessment"""
        tracker = SocialSentimentTracker(MagicMock())

        # Normal sentiment and momentum
        risk = tracker._assess_risk_level(
            sentiment=50.0,
            momentum=0.05,
            volume_spike=False,
        )
        assert risk == "low"


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    @pytest.mark.asyncio
    async def test_confidence_with_alignment(self):
        """Test confidence increases with Fear & Greed alignment"""
        mock_client = AsyncMock()

        # Mock aligned sentiment and Fear & Greed
        mock_client.call_tool.side_effect = [
            {"content": [{"text": "balance is 20"}]},  # sentiment = 60
            {"content": [{"text": "volume is 15000"}]},
            {"content": [{"text": "dominance is 25%"}]},
            {"content": [{"text": "Fear & Greed: 65"}]},  # Within 20 points
        ]

        tracker = SocialSentimentTracker(mock_client)
        result = await tracker.track("BTC", verbose=True)

        # Base 0.75 + 0.10 alignment = 0.85
        assert result["metadata"]["confidence"] >= 0.85

    @pytest.mark.asyncio
    async def test_confidence_with_strong_momentum(self):
        """Test confidence increases with strong momentum"""
        mock_client = AsyncMock()

        # Mock strong positive momentum
        mock_client.call_tool.side_effect = [
            {"content": [{"text": "balance is 25"}]},  # Strong positive
            {"content": [{"text": "volume is 15000"}]},
            {"content": [{"text": "dominance is 25%"}]},
            {"content": [{"text": "Fear & Greed: 50"}]},
        ]

        tracker = SocialSentimentTracker(mock_client)
        result = await tracker.track("BTC", verbose=True)

        # Base 0.75 + 0.05 strong momentum = 0.80
        assert result["metadata"]["confidence"] >= 0.80

    @pytest.mark.asyncio
    async def test_confidence_capped_at_095(self):
        """Test confidence is capped at 0.95"""
        mock_client = AsyncMock()

        # Mock maximum confidence scenario
        mock_client.call_tool.side_effect = [
            {"content": [{"text": "balance is 30"}]},  # Strong momentum
            {"content": [{"text": "volume is 15000"}]},
            {"content": [{"text": "dominance is 25%"}]},
            {"content": [{"text": "Fear & Greed: 65"}]},  # Aligned
        ]

        tracker = SocialSentimentTracker(mock_client)
        result = await tracker.track("BTC", verbose=True)

        # Should be capped at 0.95
        assert result["metadata"]["confidence"] <= 0.95


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
