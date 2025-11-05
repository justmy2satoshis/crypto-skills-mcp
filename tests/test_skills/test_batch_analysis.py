"""
Unit tests for BatchAnalyzer Coordination Skill

Tests batch analysis functionality including:
- Multi-symbol parallel analysis
- Multi-timeframe analysis
- Comprehensive scanning
- Parallel task execution
- Result aggregation
- Error handling
- Verbose parameter functionality
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.batch_analysis import BatchAnalyzer


class TestBatchAnalyzerInit:
    """Test BatchAnalyzer initialization"""

    def test_initialization(self):
        """Test analyzer initializes with MCP client"""
        mock_client = MagicMock()
        analyzer = BatchAnalyzer(mock_client)

        assert analyzer.mcp == mock_client
        assert analyzer is not None


class TestAnalyzeMultiSymbol:
    """Test multi-symbol analysis method"""

    @pytest.fixture
    def mock_skills(self):
        """Mock Skill responses"""
        # Mock sentiment fusion response
        sentiment_response = {
            "data": {
                "combined_score": 68.5,
                "combined_signal": "Buy",
                "sentiment_score": 72.0,
                "technical_score": 65.0,
            }
        }

        # Mock momentum response
        momentum_response = {
            "data": {
                "momentum_score": 72.5,
                "momentum_direction": "bullish",
                "trend_strength": "strong",
            }
        }

        return {
            "sentiment_fusion": sentiment_response,
            "momentum": momentum_response,
        }

    @pytest.mark.asyncio
    async def test_analyze_multi_symbol_basic(self, mock_skills):
        """Test basic multi-symbol analysis"""
        mock_client = AsyncMock()

        # Mock Skill imports and instantiation
        with patch("skills.batch_analysis.SentimentFusionEngine") as MockSentiment, \
             patch("skills.batch_analysis.MomentumScorer") as MockMomentum:

            # Setup mocks
            mock_sentiment = AsyncMock()
            mock_sentiment.fuse.return_value = mock_skills["sentiment_fusion"]
            MockSentiment.return_value = mock_sentiment

            mock_momentum = AsyncMock()
            mock_momentum.score.return_value = mock_skills["momentum"]
            MockMomentum.return_value = mock_momentum

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_symbol(
                symbols=["BTC", "ETH"],
                analysis_types=["sentiment_fusion", "momentum"],
                timeframe="4h",
                verbose=True,
            )

            # Verify structure
            assert "timestamp" in result
            assert "source" in result
            assert result["source"] == "batch-analysis-skill"
            assert "data_type" in result
            assert result["data_type"] == "multi_symbol_analysis"
            assert "data" in result
            assert "metadata" in result

    @pytest.mark.asyncio
    async def test_analyze_multi_symbol_verbose_true(self, mock_skills):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.SentimentFusionEngine") as MockSentiment:
            mock_sentiment = AsyncMock()
            mock_sentiment.fuse.return_value = mock_skills["sentiment_fusion"]
            MockSentiment.return_value = mock_sentiment

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_symbol(
                symbols=["BTC"],
                analysis_types=["sentiment_fusion"],
                verbose=True,
            )

            # Full response should have all fields
            assert "timestamp" in result
            assert "source" in result
            assert "metadata" in result
            assert "symbols_analyzed" in result["metadata"]
            assert "total_analyses" in result["metadata"]
            assert "execution_time_ms" in result["metadata"]
            assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_analyze_multi_symbol_verbose_false(self, mock_skills):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.SentimentFusionEngine") as MockSentiment:
            mock_sentiment = AsyncMock()
            mock_sentiment.fuse.return_value = mock_skills["sentiment_fusion"]
            MockSentiment.return_value = mock_sentiment

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_symbol(
                symbols=["BTC"],
                analysis_types=["sentiment_fusion"],
                verbose=False,
            )

            # Minimal response should only have data
            assert "data" in result
            assert "timestamp" not in result
            assert "source" not in result
            assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_analyze_multi_symbol_data_structure(self, mock_skills):
        """Test data structure aggregates by symbol"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.SentimentFusionEngine") as MockSentiment, \
             patch("skills.batch_analysis.MomentumScorer") as MockMomentum:

            mock_sentiment = AsyncMock()
            mock_sentiment.fuse.return_value = mock_skills["sentiment_fusion"]
            MockSentiment.return_value = mock_sentiment

            mock_momentum = AsyncMock()
            mock_momentum.score.return_value = mock_skills["momentum"]
            MockMomentum.return_value = mock_momentum

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_symbol(
                symbols=["BTC", "ETH"],
                analysis_types=["sentiment_fusion", "momentum"],
            )

            data = result["data"]

            # Verify data structure
            assert "BTC" in data
            assert "ETH" in data
            assert "sentiment_fusion" in data["BTC"]
            assert "momentum" in data["BTC"]
            assert "sentiment_fusion" in data["ETH"]
            assert "momentum" in data["ETH"]


class TestAnalyzeMultiTimeframe:
    """Test multi-timeframe analysis method"""

    @pytest.fixture
    def mock_momentum_responses(self):
        """Mock momentum responses for different timeframes"""
        return [
            {"data": {"momentum_score": 65.0, "momentum_direction": "bullish"}},
            {"data": {"momentum_score": 72.5, "momentum_direction": "bullish"}},
            {"data": {"momentum_score": 78.0, "momentum_direction": "bullish"}},
        ]

    @pytest.mark.asyncio
    async def test_analyze_multi_timeframe_basic(self, mock_momentum_responses):
        """Test basic multi-timeframe analysis"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.MomentumScorer") as MockMomentum:
            mock_momentum = AsyncMock()
            mock_momentum.score.side_effect = mock_momentum_responses
            MockMomentum.return_value = mock_momentum

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_timeframe(
                symbol="BTC",
                timeframes=["1h", "4h", "1d"],
                analysis_type="momentum",
                verbose=True,
            )

            # Verify structure
            assert "timestamp" in result
            assert "symbol" in result
            assert result["symbol"] == "BTC"
            assert "data" in result
            assert "metadata" in result

    @pytest.mark.asyncio
    async def test_analyze_multi_timeframe_verbose_false(self, mock_momentum_responses):
        """Test verbose=False returns minimal response"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.MomentumScorer") as MockMomentum:
            mock_momentum = AsyncMock()
            mock_momentum.score.side_effect = mock_momentum_responses
            MockMomentum.return_value = mock_momentum

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_timeframe(
                symbol="BTC",
                timeframes=["1h", "4h", "1d"],
                analysis_type="momentum",
                verbose=False,
            )

            # Minimal response should only have data
            assert "data" in result
            assert "timestamp" not in result
            assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_analyze_multi_timeframe_data_structure(self, mock_momentum_responses):
        """Test data structure aggregates by timeframe"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.MomentumScorer") as MockMomentum:
            mock_momentum = AsyncMock()
            mock_momentum.score.side_effect = mock_momentum_responses
            MockMomentum.return_value = mock_momentum

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_timeframe(
                symbol="BTC",
                timeframes=["1h", "4h", "1d"],
                analysis_type="momentum",
            )

            data = result["data"]

            # Verify data structure
            assert "1h" in data
            assert "4h" in data
            assert "1d" in data
            assert "momentum_score" in data["4h"]

    @pytest.mark.asyncio
    async def test_analyze_multi_timeframe_invalid_analysis_type(self):
        """Test error handling for invalid analysis type"""
        mock_client = AsyncMock()
        analyzer = BatchAnalyzer(mock_client)

        with pytest.raises(ValueError, match="Unsupported analysis type"):
            await analyzer.analyze_multi_timeframe(
                symbol="BTC",
                timeframes=["4h"],
                analysis_type="invalid_type",
            )


class TestComprehensiveScan:
    """Test comprehensive scan method"""

    @pytest.mark.asyncio
    async def test_comprehensive_scan_calls_all_analysis_types(self):
        """Test comprehensive scan includes all analysis types"""
        mock_client = AsyncMock()

        with patch.object(BatchAnalyzer, "analyze_multi_symbol", new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = {"data": {}}

            analyzer = BatchAnalyzer(mock_client)

            await analyzer.comprehensive_scan(
                symbols=["BTC", "ETH"],
                primary_timeframe="4h",
                verbose=False,
            )

            # Verify all analysis types requested
            mock_analyze.assert_called_once()
            call_args = mock_analyze.call_args
            analysis_types = call_args[0][1]  # Second positional arg

            assert "sentiment_fusion" in analysis_types
            assert "momentum" in analysis_types
            assert "volatility" in analysis_types
            assert "support_resistance" in analysis_types
            assert "news_sentiment" in analysis_types
            assert "whale_activity" in analysis_types


class TestParallelExecution:
    """Test parallel task execution"""

    @pytest.mark.asyncio
    async def test_parallel_execution_all_succeed(self):
        """Test all parallel tasks succeed"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.SentimentFusionEngine") as MockSentiment:
            mock_sentiment = AsyncMock()
            mock_sentiment.fuse.return_value = {"data": {"combined_score": 70.0}}
            MockSentiment.return_value = mock_sentiment

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_symbol(
                symbols=["BTC", "ETH", "SOL"],
                analysis_types=["sentiment_fusion"],
                verbose=True,
            )

            metadata = result["metadata"]

            # All tasks should succeed
            assert metadata["symbols_analyzed"] == 3
            assert metadata["total_analyses"] == 3
            assert metadata["failed_analyses"] == 0

    @pytest.mark.asyncio
    async def test_parallel_execution_some_fail(self):
        """Test handling of partial failures"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.SentimentFusionEngine") as MockSentiment:
            mock_sentiment = AsyncMock()
            # First call succeeds, second fails, third succeeds
            mock_sentiment.fuse.side_effect = [
                {"data": {"combined_score": 70.0}},
                Exception("Network error"),
                {"data": {"combined_score": 65.0}},
            ]
            MockSentiment.return_value = mock_sentiment

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_symbol(
                symbols=["BTC", "ETH", "SOL"],
                analysis_types=["sentiment_fusion"],
                verbose=True,
            )

            metadata = result["metadata"]

            # 2 should succeed, 1 should fail
            assert metadata["total_analyses"] == 2
            assert metadata["failed_analyses"] == 1


class TestResultAggregation:
    """Test result aggregation logic"""

    @pytest.mark.asyncio
    async def test_result_aggregation_extracts_data_field(self):
        """Test result aggregation extracts 'data' field from verbose=False responses"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.SentimentFusionEngine") as MockSentiment:
            # Return verbose=False response format
            mock_sentiment = AsyncMock()
            mock_sentiment.fuse.return_value = {
                "data": {"combined_score": 68.5, "combined_signal": "Buy"}
            }
            MockSentiment.return_value = mock_sentiment

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_symbol(
                symbols=["BTC"],
                analysis_types=["sentiment_fusion"],
            )

            # Verify data extraction
            assert "BTC" in result["data"]
            assert "sentiment_fusion" in result["data"]["BTC"]
            assert result["data"]["BTC"]["sentiment_fusion"]["combined_score"] == 68.5


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    @pytest.mark.asyncio
    async def test_confidence_increases_with_success_rate(self):
        """Test confidence increases with success rate"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.SentimentFusionEngine") as MockSentiment:
            mock_sentiment = AsyncMock()
            mock_sentiment.fuse.return_value = {"data": {"combined_score": 70.0}}
            MockSentiment.return_value = mock_sentiment

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_symbol(
                symbols=["BTC", "ETH"],
                analysis_types=["sentiment_fusion"],
                verbose=True,
            )

            # 100% success rate should give high confidence
            # Base: 0.70, Success adjustment: 0.25 * 1.0 = 0.25
            # Total: 0.70 + 0.25 = 0.95
            assert result["metadata"]["confidence"] >= 0.90


class TestExecutionTimeTracking:
    """Test execution time tracking"""

    @pytest.mark.asyncio
    async def test_execution_time_recorded(self):
        """Test execution time is recorded in metadata"""
        mock_client = AsyncMock()

        with patch("skills.batch_analysis.SentimentFusionEngine") as MockSentiment:
            mock_sentiment = AsyncMock()
            mock_sentiment.fuse.return_value = {"data": {"combined_score": 70.0}}
            MockSentiment.return_value = mock_sentiment

            analyzer = BatchAnalyzer(mock_client)

            result = await analyzer.analyze_multi_symbol(
                symbols=["BTC"],
                analysis_types=["sentiment_fusion"],
                verbose=True,
            )

            # Execution time should be recorded
            assert "execution_time_ms" in result["metadata"]
            assert isinstance(result["metadata"]["execution_time_ms"], int)
            assert result["metadata"]["execution_time_ms"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
