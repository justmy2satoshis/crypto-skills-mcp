"""
Unit tests for NewsSentimentScorer Skill

Tests news sentiment analysis functionality including:
- News article processing and filtering
- Relevance calculation (symbol matching, keyword matching)
- Sentiment analysis (positive/negative/neutral classification)
- Overall sentiment scoring (0-100 scale)
- Sentiment momentum calculation
- Topic extraction from article titles
- Dominant narrative determination
- News velocity assessment
- Impact score calculation
- Trading signal generation
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

from skills.sentiment_analysis.news_sentiment_scorer import NewsSentimentScorer


class TestNewsSentimentScorerInit:
    """Test NewsSentimentScorer initialization"""

    def test_initialization(self):
        """Test scorer initializes with MCP client"""
        mock_client = MagicMock()
        scorer = NewsSentimentScorer(mock_client)

        assert scorer.mcp == mock_client
        assert scorer is not None


class TestScoreMethod:
    """Test main score() method"""

    @pytest.fixture
    def mock_news_data(self):
        """Mock news data from cryptopanic-mcp"""
        return {
            "content": [
                {
                    "text": "- Bitcoin ETF approval fuels rally to new highs\n"
                    "- Ethereum surges as institutional adoption grows\n"
                    "- Crypto market crash fears as regulation tightens\n"
                    "- Blockchain technology sees breakthrough development\n"
                    "- Bitcoin price gains 5% in bullish momentum\n"
                    "- DeFi protocols see record growth this quarter\n"
                    "- Cryptocurrency ban discussed in major economy\n"
                    "- Altcoin rally continues with strong gains\n"
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_score_basic_call(self, mock_news_data):
        """Test basic score() call returns correct structure"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_news_data

        scorer = NewsSentimentScorer(mock_client)

        result = await scorer.score("BTC", lookback_hours=24)

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "sentiment-analysis-skill"
        assert "symbol" in result
        assert result["symbol"] == "BTC"
        assert "data_type" in result
        assert result["data_type"] == "news_sentiment"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_score_verbose_true(self, mock_news_data):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_news_data

        scorer = NewsSentimentScorer(mock_client)

        result = await scorer.score("BTC", lookback_hours=24, verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "symbol" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "lookback_hours" in result["metadata"]
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_score_verbose_false(self, mock_news_data):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_news_data

        scorer = NewsSentimentScorer(mock_client)

        result = await scorer.score("BTC", lookback_hours=24, verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_score_data_structure(self, mock_news_data):
        """Test data structure contains all required fields"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_news_data

        scorer = NewsSentimentScorer(mock_client)

        result = await scorer.score("BTC", lookback_hours=24)
        data = result["data"]

        # Verify all required data fields
        assert "overall_sentiment" in data
        assert "sentiment_category" in data
        assert "article_count" in data
        assert "positive_count" in data
        assert "negative_count" in data
        assert "neutral_count" in data
        assert "sentiment_momentum" in data
        assert "impact_score" in data
        assert "top_topics" in data
        assert "dominant_narrative" in data
        assert "news_velocity" in data
        assert "trading_signal" in data

        # Verify data types
        assert isinstance(data["overall_sentiment"], (int, float))
        assert isinstance(data["sentiment_category"], str)
        assert isinstance(data["article_count"], int)
        assert isinstance(data["sentiment_momentum"], (int, float))
        assert isinstance(data["impact_score"], (int, float))
        assert isinstance(data["top_topics"], list)

    @pytest.mark.asyncio
    async def test_score_no_relevant_news(self):
        """Test behavior when no relevant news found"""
        mock_client = AsyncMock()
        # Return news with no symbol mentions
        mock_client.call_tool.return_value = {
            "content": [{"text": "- Generic blockchain news\n- Tech stock updates\n"}]
        }

        scorer = NewsSentimentScorer(mock_client)

        result = await scorer.score("BTC", min_relevance=0.8)
        data = result["data"]

        # Should return neutral response
        assert data["overall_sentiment"] == 50.0
        assert data["sentiment_category"] == "Neutral"
        assert data["article_count"] == 0


class TestNewsProcessing:
    """Test news article processing"""

    def test_process_news_articles_valid_data(self):
        """Test processing valid news data"""
        scorer = NewsSentimentScorer(MagicMock())

        news_result = {
            "content": [
                {
                    "text": "- Bitcoin rally continues\n"
                    "- Ethereum sees institutional adoption\n"
                    "- Crypto market crash fears\n"
                }
            ]
        }

        articles = scorer._process_news_articles(news_result, "BTC")

        # Should extract 3 articles
        assert len(articles) == 3
        assert all("title" in a for a in articles)
        assert all("sentiment" in a for a in articles)
        assert all("relevance" in a for a in articles)

    def test_process_news_articles_exception_handling(self):
        """Test news processing handles exceptions gracefully"""
        scorer = NewsSentimentScorer(MagicMock())

        # Test with Exception
        result = Exception("Network error")
        articles = scorer._process_news_articles(result, "BTC")

        assert articles == []

    def test_process_news_articles_invalid_format(self):
        """Test news processing handles invalid format"""
        scorer = NewsSentimentScorer(MagicMock())

        result = {"content": [{"invalid": "data"}]}
        articles = scorer._process_news_articles(result, "BTC")

        assert isinstance(articles, list)


class TestRelevanceCalculation:
    """Test article relevance calculation"""

    def test_calculate_relevance_direct_symbol_match(self):
        """Test relevance with direct symbol mention"""
        scorer = NewsSentimentScorer(MagicMock())

        # Direct symbol mention
        relevance = scorer._calculate_relevance("BTC rallies to new high", "BTC")
        assert relevance == 1.0

    def test_calculate_relevance_full_name_match(self):
        """Test relevance with cryptocurrency full name"""
        scorer = NewsSentimentScorer(MagicMock())

        # Full name mention
        relevance = scorer._calculate_relevance("Bitcoin adoption grows", "BTC")
        assert relevance == 1.0

        relevance = scorer._calculate_relevance("Ethereum upgrade launches", "ETH")
        assert relevance == 1.0

    def test_calculate_relevance_crypto_keywords(self):
        """Test relevance with crypto keywords"""
        scorer = NewsSentimentScorer(MagicMock())

        # Crypto keyword mention
        relevance = scorer._calculate_relevance(
            "Cryptocurrency market sees growth", "SOL"
        )
        assert relevance == 0.6

        relevance = scorer._calculate_relevance("Blockchain innovation advances", "ADA")
        assert relevance == 0.6

    def test_calculate_relevance_no_match(self):
        """Test relevance with no crypto mentions"""
        scorer = NewsSentimentScorer(MagicMock())

        # No crypto mentions
        relevance = scorer._calculate_relevance("Tech stocks rally", "BTC")
        assert relevance == 0.3


class TestSentimentAnalysis:
    """Test sentiment analysis of article titles"""

    def test_analyze_sentiment_positive(self):
        """Test positive sentiment detection"""
        scorer = NewsSentimentScorer(MagicMock())

        # Positive keywords
        sentiment = scorer._analyze_sentiment("Bitcoin rally drives surge to new high")
        assert sentiment == "positive"

        sentiment = scorer._analyze_sentiment("Bullish momentum as adoption grows")
        assert sentiment == "positive"

    def test_analyze_sentiment_negative(self):
        """Test negative sentiment detection"""
        scorer = NewsSentimentScorer(MagicMock())

        # Negative keywords
        sentiment = scorer._analyze_sentiment("Market crash as prices plunge")
        assert sentiment == "negative"

        sentiment = scorer._analyze_sentiment("Bearish outlook amid ban fears")
        assert sentiment == "negative"

    def test_analyze_sentiment_neutral(self):
        """Test neutral sentiment detection"""
        scorer = NewsSentimentScorer(MagicMock())

        # Neutral (no strong keywords)
        sentiment = scorer._analyze_sentiment("Bitcoin price remains stable")
        assert sentiment == "neutral"

        sentiment = scorer._analyze_sentiment("Cryptocurrency market analysis")
        assert sentiment == "neutral"

    def test_analyze_sentiment_mixed_keywords(self):
        """Test sentiment with equal positive and negative keywords"""
        scorer = NewsSentimentScorer(MagicMock())

        # Equal positive and negative
        sentiment = scorer._analyze_sentiment("Rally follows crash in volatile market")
        assert sentiment in ["positive", "negative", "neutral"]


class TestOverallSentimentCalculation:
    """Test overall sentiment score calculation"""

    def test_calculate_overall_sentiment_all_positive(self):
        """Test calculation with all positive articles"""
        scorer = NewsSentimentScorer(MagicMock())

        score = scorer._calculate_overall_sentiment(
            positive_count=10, negative_count=0, neutral_count=0
        )

        assert score == 100.0

    def test_calculate_overall_sentiment_all_negative(self):
        """Test calculation with all negative articles"""
        scorer = NewsSentimentScorer(MagicMock())

        score = scorer._calculate_overall_sentiment(
            positive_count=0, negative_count=10, neutral_count=0
        )

        assert score == 0.0

    def test_calculate_overall_sentiment_all_neutral(self):
        """Test calculation with all neutral articles"""
        scorer = NewsSentimentScorer(MagicMock())

        score = scorer._calculate_overall_sentiment(
            positive_count=0, negative_count=0, neutral_count=10
        )

        assert score == 50.0

    def test_calculate_overall_sentiment_mixed(self):
        """Test calculation with mixed sentiment"""
        scorer = NewsSentimentScorer(MagicMock())

        # 6 positive, 2 negative, 2 neutral
        # = (6*100 + 2*0 + 2*50) / 10 = 700 / 10 = 70.0
        score = scorer._calculate_overall_sentiment(
            positive_count=6, negative_count=2, neutral_count=2
        )

        assert score == 70.0

    def test_calculate_overall_sentiment_zero_articles(self):
        """Test calculation with zero articles"""
        scorer = NewsSentimentScorer(MagicMock())

        score = scorer._calculate_overall_sentiment(
            positive_count=0, negative_count=0, neutral_count=0
        )

        assert score == 50.0


class TestSentimentMomentum:
    """Test sentiment momentum calculation"""

    def test_calculate_sentiment_momentum_strong_positive(self):
        """Test momentum with strong positive sentiment"""
        scorer = NewsSentimentScorer(MagicMock())

        articles = []  # Not used in simplified implementation
        momentum = scorer._calculate_sentiment_momentum(articles, current_sentiment=75.0)

        assert momentum == 0.15  # Strong positive momentum

    def test_calculate_sentiment_momentum_slight_positive(self):
        """Test momentum with slight positive sentiment"""
        scorer = NewsSentimentScorer(MagicMock())

        momentum = scorer._calculate_sentiment_momentum([], current_sentiment=60.0)

        assert momentum == 0.08  # Slight positive momentum

    def test_calculate_sentiment_momentum_strong_negative(self):
        """Test momentum with strong negative sentiment"""
        scorer = NewsSentimentScorer(MagicMock())

        momentum = scorer._calculate_sentiment_momentum([], current_sentiment=30.0)

        assert momentum == -0.15  # Strong negative momentum

    def test_calculate_sentiment_momentum_slight_negative(self):
        """Test momentum with slight negative sentiment"""
        scorer = NewsSentimentScorer(MagicMock())

        momentum = scorer._calculate_sentiment_momentum([], current_sentiment=40.0)

        assert momentum == -0.08  # Slight negative momentum

    def test_calculate_sentiment_momentum_neutral(self):
        """Test momentum with neutral sentiment"""
        scorer = NewsSentimentScorer(MagicMock())

        momentum = scorer._calculate_sentiment_momentum([], current_sentiment=50.0)

        assert momentum == 0.0  # Neutral momentum


class TestTopicExtraction:
    """Test topic extraction from article titles"""

    def test_extract_top_topics_etf(self):
        """Test extraction of ETF-related topics"""
        scorer = NewsSentimentScorer(MagicMock())

        articles = [
            {"title": "Bitcoin ETF approval drives rally"},
            {"title": "SEC considers ETF applications"},
            {"title": "Institutional adoption grows"},
        ]

        topics = scorer._extract_top_topics(articles)

        assert "ETF Approval" in topics

    def test_extract_top_topics_regulation(self):
        """Test extraction of regulation-related topics"""
        scorer = NewsSentimentScorer(MagicMock())

        articles = [
            {"title": "New cryptocurrency regulations announced"},
            {"title": "Government regulatory framework proposed"},
        ]

        topics = scorer._extract_top_topics(articles)

        assert "Regulation" in topics

    def test_extract_top_topics_max_three(self):
        """Test that only top 3 topics are returned"""
        scorer = NewsSentimentScorer(MagicMock())

        articles = [
            {"title": "ETF approval news"},
            {"title": "ETF applications surge"},
            {"title": "Regulation updates"},
            {"title": "Regulatory framework"},
            {"title": "Market crash fears"},
            {"title": "Bull run begins"},
            {"title": "Institutional adoption"},
        ]

        topics = scorer._extract_top_topics(articles)

        assert len(topics) <= 3

    def test_extract_top_topics_no_matches(self):
        """Test topic extraction with no keyword matches"""
        scorer = NewsSentimentScorer(MagicMock())

        articles = [{"title": "Generic news article"}, {"title": "Unrelated content"}]

        topics = scorer._extract_top_topics(articles)

        assert topics == []


class TestDominantNarrative:
    """Test dominant narrative determination"""

    def test_determine_dominant_narrative_bullish(self):
        """Test bullish narrative determination"""
        scorer = NewsSentimentScorer(MagicMock())

        narrative = scorer._determine_dominant_narrative(
            positive_count=8, negative_count=1, neutral_count=1
        )

        assert narrative == "bullish"

    def test_determine_dominant_narrative_bearish(self):
        """Test bearish narrative determination"""
        scorer = NewsSentimentScorer(MagicMock())

        narrative = scorer._determine_dominant_narrative(
            positive_count=1, negative_count=8, neutral_count=1
        )

        assert narrative == "bearish"

    def test_determine_dominant_narrative_slightly_bullish(self):
        """Test slightly bullish narrative"""
        scorer = NewsSentimentScorer(MagicMock())

        narrative = scorer._determine_dominant_narrative(
            positive_count=5, negative_count=3, neutral_count=2
        )

        assert narrative == "slightly_bullish"

    def test_determine_dominant_narrative_slightly_bearish(self):
        """Test slightly bearish narrative"""
        scorer = NewsSentimentScorer(MagicMock())

        narrative = scorer._determine_dominant_narrative(
            positive_count=3, negative_count=5, neutral_count=2
        )

        assert narrative == "slightly_bearish"

    def test_determine_dominant_narrative_neutral(self):
        """Test neutral narrative"""
        scorer = NewsSentimentScorer(MagicMock())

        narrative = scorer._determine_dominant_narrative(
            positive_count=3, negative_count=3, neutral_count=4
        )

        assert narrative == "neutral"


class TestNewsVelocity:
    """Test news velocity assessment"""

    def test_assess_news_velocity_very_high(self):
        """Test very high velocity classification"""
        scorer = NewsSentimentScorer(MagicMock())

        velocity = scorer._assess_news_velocity(article_count=25)
        assert velocity == "very_high"

    def test_assess_news_velocity_high(self):
        """Test high velocity classification"""
        scorer = NewsSentimentScorer(MagicMock())

        velocity = scorer._assess_news_velocity(article_count=15)
        assert velocity == "high"

    def test_assess_news_velocity_moderate(self):
        """Test moderate velocity classification"""
        scorer = NewsSentimentScorer(MagicMock())

        velocity = scorer._assess_news_velocity(article_count=8)
        assert velocity == "moderate"

    def test_assess_news_velocity_low(self):
        """Test low velocity classification"""
        scorer = NewsSentimentScorer(MagicMock())

        velocity = scorer._assess_news_velocity(article_count=3)
        assert velocity == "low"


class TestImpactScore:
    """Test impact score calculation"""

    def test_calculate_impact_score_high_sentiment_high_volume(self):
        """Test impact with high sentiment and volume"""
        scorer = NewsSentimentScorer(MagicMock())

        # High positive sentiment (80), many articles (20), positive momentum (0.15)
        impact = scorer._calculate_impact_score(
            sentiment=80.0, article_count=20, momentum=0.15
        )

        assert impact > 0.70  # Should have high impact

    def test_calculate_impact_score_low_sentiment_low_volume(self):
        """Test impact with low sentiment and volume"""
        scorer = NewsSentimentScorer(MagicMock())

        # Neutral sentiment (50), few articles (3), no momentum (0.0)
        impact = scorer._calculate_impact_score(
            sentiment=50.0, article_count=3, momentum=0.0
        )

        assert impact < 0.30  # Should have low impact

    def test_calculate_impact_score_negative_sentiment(self):
        """Test impact calculation with negative sentiment"""
        scorer = NewsSentimentScorer(MagicMock())

        # Negative sentiment (20), high volume (18), negative momentum (-0.15)
        impact = scorer._calculate_impact_score(
            sentiment=20.0, article_count=18, momentum=-0.15
        )

        # Impact should be high (sentiment impact is absolute value)
        assert impact > 0.60

    def test_calculate_impact_score_capped_at_one(self):
        """Test impact score is capped at 1.0"""
        scorer = NewsSentimentScorer(MagicMock())

        # Extreme values
        impact = scorer._calculate_impact_score(
            sentiment=100.0, article_count=100, momentum=1.0
        )

        assert impact <= 1.0


class TestSentimentCategorization:
    """Test sentiment score categorization"""

    def test_categorize_sentiment_very_positive(self):
        """Test very positive categorization"""
        scorer = NewsSentimentScorer(MagicMock())

        category = scorer._categorize_sentiment(75.0)
        assert category == "Very Positive"

    def test_categorize_sentiment_positive(self):
        """Test positive categorization"""
        scorer = NewsSentimentScorer(MagicMock())

        category = scorer._categorize_sentiment(60.0)
        assert category == "Positive"

    def test_categorize_sentiment_neutral(self):
        """Test neutral categorization"""
        scorer = NewsSentimentScorer(MagicMock())

        category = scorer._categorize_sentiment(50.0)
        assert category == "Neutral"

    def test_categorize_sentiment_negative(self):
        """Test negative categorization"""
        scorer = NewsSentimentScorer(MagicMock())

        category = scorer._categorize_sentiment(35.0)
        assert category == "Negative"

    def test_categorize_sentiment_very_negative(self):
        """Test very negative categorization"""
        scorer = NewsSentimentScorer(MagicMock())

        category = scorer._categorize_sentiment(25.0)
        assert category == "Very Negative"


class TestTradingSignalGeneration:
    """Test trading signal generation"""

    def test_generate_trading_signal_strong_bullish(self):
        """Test strong bullish signal generation"""
        scorer = NewsSentimentScorer(MagicMock())

        signal = scorer._generate_trading_signal(
            sentiment=75.0, narrative="bullish", velocity="high", momentum=0.15
        )

        assert "bullish" in signal.lower()
        assert "strong" in signal.lower()

    def test_generate_trading_signal_bullish_momentum(self):
        """Test bullish momentum signal"""
        scorer = NewsSentimentScorer(MagicMock())

        signal = scorer._generate_trading_signal(
            sentiment=60.0,
            narrative="slightly_bullish",
            velocity="moderate",
            momentum=0.12,
        )

        assert "bullish" in signal.lower()
        assert "momentum" in signal.lower()

    def test_generate_trading_signal_strong_bearish(self):
        """Test strong bearish signal generation"""
        scorer = NewsSentimentScorer(MagicMock())

        signal = scorer._generate_trading_signal(
            sentiment=25.0, narrative="bearish", velocity="very_high", momentum=-0.15
        )

        assert "bearish" in signal.lower()
        assert "strong" in signal.lower()

    def test_generate_trading_signal_bearish_momentum(self):
        """Test bearish momentum signal"""
        scorer = NewsSentimentScorer(MagicMock())

        signal = scorer._generate_trading_signal(
            sentiment=40.0,
            narrative="slightly_bearish",
            velocity="moderate",
            momentum=-0.12,
        )

        assert "bearish" in signal.lower()

    def test_generate_trading_signal_neutral(self):
        """Test neutral signal generation"""
        scorer = NewsSentimentScorer(MagicMock())

        signal = scorer._generate_trading_signal(
            sentiment=50.0, narrative="neutral", velocity="low", momentum=0.0
        )

        assert "neutral" in signal.lower()

    def test_generate_trading_signal_mixed(self):
        """Test mixed signal generation"""
        scorer = NewsSentimentScorer(MagicMock())

        signal = scorer._generate_trading_signal(
            sentiment=52.0,
            narrative="slightly_bullish",
            velocity="moderate",
            momentum=0.05,
        )

        assert "mixed" in signal.lower() or "monitor" in signal.lower()


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    @pytest.mark.asyncio
    async def test_confidence_high_article_count(self):
        """Test confidence increases with article count"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "content": [
                {
                    "text": "\n".join(
                        [f"- Bitcoin news article {i}" for i in range(15)]
                    )
                }
            ]
        }

        scorer = NewsSentimentScorer(mock_client)

        result = await scorer.score("BTC", verbose=True)

        # Should have high confidence with 15 articles
        assert result["metadata"]["confidence"] >= 0.75

    @pytest.mark.asyncio
    async def test_confidence_strong_momentum(self):
        """Test confidence increases with strong momentum"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "content": [
                {
                    "text": "- Bitcoin rally continues with strong gains\n"
                    "- Bullish momentum drives surge\n"
                    "- Positive sentiment fuels growth\n"
                    "- Record high achieved\n"
                    "- Adoption surges\n"
                }
            ]
        }

        scorer = NewsSentimentScorer(mock_client)

        result = await scorer.score("BTC", verbose=True)

        # Should have high confidence with strong positive sentiment (momentum)
        assert result["metadata"]["confidence"] >= 0.70


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
