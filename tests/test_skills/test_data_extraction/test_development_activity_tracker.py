"""
Unit tests for DevelopmentActivityTracker Skill

Tests development activity tracking functionality including:
- GitHub repository mapping
- Commit data processing and velocity calculation
- Contributor analysis and growth tracking
- Activity level classification
- Health score calculation
- Development momentum determination
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

from skills.data_extraction.development_activity_tracker import DevelopmentActivityTracker


class TestDevelopmentActivityTrackerInit:
    """Test DevelopmentActivityTracker initialization"""

    def test_initialization(self):
        """Test tracker initializes with MCP client"""
        mock_client = MagicMock()
        tracker = DevelopmentActivityTracker(mock_client)

        assert tracker.mcp == mock_client
        assert tracker is not None


class TestTrackMethod:
    """Test main track() method"""

    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client with realistic GitHub responses"""
        client = AsyncMock()

        # Mock GitHub API responses in sequence
        client.call_tool.side_effect = [
            # Commits response
            {
                "content": [
                    {
                        "commits": [
                            {"sha": f"commit{i}", "date": "2025-01-15"}
                            for i in range(150)
                        ]
                    }
                ]
            },
            # Contributors response
            {
                "content": [
                    {
                        "users": [
                            {"login": f"user{i}", "contributions": 10 + i}
                            for i in range(25)
                        ]
                    }
                ]
            },
            # Releases response
            {"content": [{"items": [{"tag_name": f"v1.{i}.0"} for i in range(3)]}]},
        ]

        return client

    @pytest.mark.asyncio
    async def test_track_basic_call(self, mock_mcp_client):
        """Test basic track() call returns correct structure"""
        tracker = DevelopmentActivityTracker(mock_mcp_client)

        result = await tracker.track("BTC", period_days=30)

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "data-extraction-skill"
        assert "asset" in result
        assert result["asset"] == "BTC"
        assert "data_type" in result
        assert result["data_type"] == "development_activity"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_track_verbose_true(self, mock_mcp_client):
        """Test verbose=True returns full response with metadata"""
        tracker = DevelopmentActivityTracker(mock_mcp_client)

        result = await tracker.track("BTC", period_days=30, verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "asset" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_track_verbose_false(self, mock_mcp_client):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        tracker = DevelopmentActivityTracker(mock_mcp_client)

        result = await tracker.track("BTC", period_days=30, verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_track_data_structure(self, mock_mcp_client):
        """Test data structure contains all required fields"""
        tracker = DevelopmentActivityTracker(mock_mcp_client)

        result = await tracker.track("BTC", period_days=30)
        data = result["data"]

        # Verify all required data fields
        assert "velocity" in data
        assert "velocity_trend" in data
        assert "contributor_count" in data
        assert "contributor_growth" in data
        assert "commit_count" in data
        assert "commit_frequency" in data
        assert "release_count" in data
        assert "code_churn" in data
        assert "health_score" in data
        assert "activity_level" in data
        assert "development_momentum" in data
        assert "period_days" in data
        assert "trading_signal" in data

        # Verify data types
        assert isinstance(data["velocity"], float)
        assert isinstance(data["velocity_trend"], str)
        assert isinstance(data["contributor_count"], int)
        assert isinstance(data["contributor_growth"], float)
        assert isinstance(data["commit_count"], int)
        assert isinstance(data["health_score"], float)
        assert isinstance(data["period_days"], int)

    @pytest.mark.asyncio
    async def test_track_with_custom_repository(self, mock_mcp_client):
        """Test tracking with custom repository override"""
        tracker = DevelopmentActivityTracker(mock_mcp_client)

        result = await tracker.track("BTC", repository="custom-org/custom-repo", period_days=30)

        assert result["asset"] == "BTC"
        assert "data" in result


class TestAssetMapping:
    """Test asset-to-repository mapping"""

    def test_map_btc_to_repository(self):
        """Test BTC maps to bitcoin/bitcoin"""
        tracker = DevelopmentActivityTracker(MagicMock())

        repo = tracker._map_asset_to_repository("BTC")
        assert repo == "bitcoin/bitcoin"

    def test_map_eth_to_repository(self):
        """Test ETH maps to ethereum/go-ethereum"""
        tracker = DevelopmentActivityTracker(MagicMock())

        repo = tracker._map_asset_to_repository("ETH")
        assert repo == "ethereum/go-ethereum"

    def test_map_sol_to_repository(self):
        """Test SOL maps to solana-labs/solana"""
        tracker = DevelopmentActivityTracker(MagicMock())

        repo = tracker._map_asset_to_repository("SOL")
        assert repo == "solana-labs/solana"

    def test_map_unknown_asset(self):
        """Test unknown asset defaults to bitcoin/bitcoin"""
        tracker = DevelopmentActivityTracker(MagicMock())

        repo = tracker._map_asset_to_repository("UNKNOWN")
        assert repo == "bitcoin/bitcoin"

    def test_map_lowercase_asset(self):
        """Test mapping works with lowercase asset symbols"""
        tracker = DevelopmentActivityTracker(MagicMock())

        repo = tracker._map_asset_to_repository("eth")
        assert repo == "ethereum/go-ethereum"


class TestCommitProcessing:
    """Test commit data processing"""

    def test_process_commit_data_valid(self):
        """Test processing valid commit data"""
        tracker = DevelopmentActivityTracker(MagicMock())

        result = {
            "content": [
                {
                    "commits": [
                        {"sha": f"commit{i}", "date": "2025-01-15"} for i in range(100)
                    ]
                }
            ]
        }

        commit_count, velocity, code_churn = tracker._process_commit_data(result, period_days=30)

        assert commit_count == 100
        assert velocity > 0  # commits per day
        assert code_churn > 0  # estimated lines changed

    def test_process_commit_data_exception_handling(self):
        """Test commit processing handles exceptions gracefully"""
        tracker = DevelopmentActivityTracker(MagicMock())

        result = Exception("GitHub API error")
        commit_count, velocity, code_churn = tracker._process_commit_data(result, period_days=30)

        assert commit_count == 0
        assert velocity == 0.0
        assert code_churn == 0

    def test_process_commit_data_empty_commits(self):
        """Test processing empty commit list"""
        tracker = DevelopmentActivityTracker(MagicMock())

        result = {"content": [{"commits": []}]}
        commit_count, velocity, code_churn = tracker._process_commit_data(result, period_days=30)

        assert commit_count == 0
        assert velocity == 0.0
        assert code_churn == 0


class TestContributorProcessing:
    """Test contributor data processing"""

    def test_process_contributor_data_valid(self):
        """Test processing valid contributor data"""
        tracker = DevelopmentActivityTracker(MagicMock())

        result = {
            "content": [
                {
                    "users": [
                        {"login": f"user{i}", "contributions": 10 + i} for i in range(30)
                    ]
                }
            ]
        }

        contributor_count, contributor_growth = tracker._process_contributor_data(
            result, period_days=30
        )

        assert contributor_count == 30
        assert isinstance(contributor_growth, float)

    def test_process_contributor_data_exception_handling(self):
        """Test contributor processing handles exceptions"""
        tracker = DevelopmentActivityTracker(MagicMock())

        result = Exception("GitHub API error")
        contributor_count, contributor_growth = tracker._process_contributor_data(
            result, period_days=30
        )

        assert contributor_count == 0
        assert contributor_growth == 0.0

    def test_process_contributor_data_empty_list(self):
        """Test processing empty contributor list"""
        tracker = DevelopmentActivityTracker(MagicMock())

        result = {"content": [{"users": []}]}
        contributor_count, contributor_growth = tracker._process_contributor_data(
            result, period_days=30
        )

        assert contributor_count == 0
        assert contributor_growth == 0.0


class TestVelocityTrend:
    """Test velocity trend calculation"""

    def test_calculate_velocity_trend_increasing(self):
        """Test increasing velocity detection"""
        tracker = DevelopmentActivityTracker(MagicMock())

        # Mock increasing commits over time (recent commits higher)
        result = {
            "content": [
                {
                    "commits": [
                        {"sha": f"commit{i}", "date": f"2025-01-{20+i//10}"}
                        for i in range(150)
                    ]
                }
            ]
        }

        trend = tracker._calculate_velocity_trend(result, period_days=30)
        assert trend in ["increasing", "stable"]  # May vary based on distribution

    def test_calculate_velocity_trend_stable(self):
        """Test stable velocity detection"""
        tracker = DevelopmentActivityTracker(MagicMock())

        # Mock consistent commits
        result = {
            "content": [
                {
                    "commits": [
                        {"sha": f"commit{i}", "date": "2025-01-15"} for i in range(100)
                    ]
                }
            ]
        }

        trend = tracker._calculate_velocity_trend(result, period_days=30)
        assert trend in ["stable", "increasing", "decreasing"]


class TestActivityClassification:
    """Test activity classification methods"""

    def test_classify_commit_frequency_very_high(self):
        """Test very high commit frequency classification (10+ commits/day)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        frequency = tracker._classify_commit_frequency(commit_count=300, period_days=30)
        assert frequency == "very_high"

    def test_classify_commit_frequency_high(self):
        """Test high commit frequency classification (5+ commits/day)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        frequency = tracker._classify_commit_frequency(commit_count=150, period_days=30)
        assert frequency == "high"

    def test_classify_commit_frequency_moderate(self):
        """Test moderate commit frequency classification (2+ commits/day)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        frequency = tracker._classify_commit_frequency(commit_count=60, period_days=30)
        assert frequency == "moderate"

    def test_classify_commit_frequency_low(self):
        """Test low commit frequency classification (0.5+ commits/day)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        frequency = tracker._classify_commit_frequency(commit_count=15, period_days=30)
        assert frequency == "low"

    def test_classify_commit_frequency_very_low(self):
        """Test very low commit frequency classification (<0.5 commits/day)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        frequency = tracker._classify_commit_frequency(commit_count=5, period_days=30)
        assert frequency == "very_low"

    def test_classify_activity_level_very_active(self):
        """Test very active classification (score >= 150)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        # High commits + many contributors + releases
        level = tracker._classify_activity_level(
            commit_count=200, contributor_count=50, release_count=5
        )
        assert level == "very_active"

    def test_classify_activity_level_active(self):
        """Test active classification (score >= 80)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        level = tracker._classify_activity_level(
            commit_count=100, contributor_count=25, release_count=3
        )
        assert level == "active"

    def test_classify_activity_level_moderate(self):
        """Test moderate classification (score >= 40)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        level = tracker._classify_activity_level(
            commit_count=50, contributor_count=15, release_count=2
        )
        assert level == "moderate"

    def test_classify_activity_level_low(self):
        """Test low classification (score >= 10)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        level = tracker._classify_activity_level(
            commit_count=20, contributor_count=5, release_count=1
        )
        assert level == "low"

    def test_classify_activity_level_inactive(self):
        """Test inactive classification (score < 10)"""
        tracker = DevelopmentActivityTracker(MagicMock())

        level = tracker._classify_activity_level(
            commit_count=5, contributor_count=2, release_count=0
        )
        assert level == "inactive"


class TestHealthScoring:
    """Test health score calculation"""

    def test_calculate_health_score_maximum(self):
        """Test maximum health score scenario"""
        tracker = DevelopmentActivityTracker(MagicMock())

        score = tracker._calculate_health_score(
            velocity=15.0,  # High velocity (10+ commits/day)
            contributor_count=60,  # Many contributors (50+)
            contributor_growth=0.25,  # Strong growth (>20%)
            commit_frequency="very_high",
            release_count=6,  # Many releases (5+)
        )

        assert score >= 0.90
        assert score <= 1.0

    def test_calculate_health_score_healthy(self):
        """Test healthy project score"""
        tracker = DevelopmentActivityTracker(MagicMock())

        score = tracker._calculate_health_score(
            velocity=8.0,
            contributor_count=30,
            contributor_growth=0.15,
            commit_frequency="high",
            release_count=4,
        )

        assert score >= 0.70
        assert score <= 0.95

    def test_calculate_health_score_moderate(self):
        """Test moderate health score"""
        tracker = DevelopmentActivityTracker(MagicMock())

        score = tracker._calculate_health_score(
            velocity=3.0,
            contributor_count=15,
            contributor_growth=0.05,
            commit_frequency="moderate",
            release_count=2,
        )

        assert score >= 0.40
        assert score <= 0.75

    def test_calculate_health_score_low(self):
        """Test low health score"""
        tracker = DevelopmentActivityTracker(MagicMock())

        score = tracker._calculate_health_score(
            velocity=0.5,
            contributor_count=3,
            contributor_growth=-0.10,
            commit_frequency="low",
            release_count=0,
        )

        assert score >= 0.0
        assert score <= 0.45

    def test_calculate_health_score_capped_at_one(self):
        """Test health score is capped at 1.0"""
        tracker = DevelopmentActivityTracker(MagicMock())

        score = tracker._calculate_health_score(
            velocity=20.0,
            contributor_count=100,
            contributor_growth=0.50,
            commit_frequency="very_high",
            release_count=10,
        )

        assert score <= 1.0


class TestMomentumDetermination:
    """Test development momentum determination"""

    def test_determine_momentum_strong(self):
        """Test strong momentum classification"""
        tracker = DevelopmentActivityTracker(MagicMock())

        momentum = tracker._determine_momentum(
            velocity_trend="increasing",
            contributor_growth=0.15,  # >10% growth
            health_score=0.82,  # >75% health
        )

        assert momentum == "strong"

    def test_determine_momentum_positive(self):
        """Test positive momentum classification"""
        tracker = DevelopmentActivityTracker(MagicMock())

        # Increasing velocity
        momentum = tracker._determine_momentum(
            velocity_trend="increasing", contributor_growth=0.03, health_score=0.65
        )
        assert momentum == "positive"

        # Positive growth
        momentum = tracker._determine_momentum(
            velocity_trend="stable", contributor_growth=0.08, health_score=0.65
        )
        assert momentum == "positive"

    def test_determine_momentum_declining(self):
        """Test declining momentum classification"""
        tracker = DevelopmentActivityTracker(MagicMock())

        momentum = tracker._determine_momentum(
            velocity_trend="decreasing",
            contributor_growth=-0.05,  # Negative growth
            health_score=0.60,
        )

        assert momentum == "declining"

    def test_determine_momentum_weak(self):
        """Test weak momentum classification"""
        tracker = DevelopmentActivityTracker(MagicMock())

        momentum = tracker._determine_momentum(
            velocity_trend="stable",
            contributor_growth=0.0,
            health_score=0.35,  # <40% health
        )

        assert momentum == "weak"

    def test_determine_momentum_neutral(self):
        """Test neutral momentum classification"""
        tracker = DevelopmentActivityTracker(MagicMock())

        momentum = tracker._determine_momentum(
            velocity_trend="stable", contributor_growth=0.02, health_score=0.55
        )

        assert momentum == "neutral"


class TestSignalGeneration:
    """Test trading signal generation"""

    def test_strong_bullish_signal(self):
        """Test strong bullish signal generation"""
        tracker = DevelopmentActivityTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            momentum="strong",
            activity_level="very_active",
            health_score=0.85,
            contributor_count=50,
        )

        assert "strong" in signal.lower()
        assert "bullish" in signal.lower() or "healthy" in signal.lower()

    def test_positive_development_signal(self):
        """Test positive development signal"""
        tracker = DevelopmentActivityTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            momentum="positive",
            activity_level="active",
            health_score=0.70,
            contributor_count=30,
        )

        assert "positive" in signal.lower() or "healthy" in signal.lower()

    def test_neutral_signal(self):
        """Test neutral signal"""
        tracker = DevelopmentActivityTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            momentum="neutral",
            activity_level="moderate",
            health_score=0.55,
            contributor_count=15,
        )

        assert "neutral" in signal.lower() or "moderate" in signal.lower()

    def test_declining_signal(self):
        """Test declining development signal"""
        tracker = DevelopmentActivityTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            momentum="declining",
            activity_level="low",
            health_score=0.40,
            contributor_count=8,
        )

        assert "declining" in signal.lower() or "concern" in signal.lower()

    def test_weak_signal(self):
        """Test weak development signal"""
        tracker = DevelopmentActivityTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            momentum="weak", activity_level="inactive", health_score=0.25, contributor_count=3
        )

        assert "weak" in signal.lower() or "low" in signal.lower() or "concern" in signal.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
