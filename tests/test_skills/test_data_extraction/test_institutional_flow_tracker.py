"""
Unit tests for InstitutionalFlowTracker Skill

Tests institutional capital flow tracking functionality including:
- ETF flow data fetching and processing
- Exchange flow analysis
- Flow classification (direction, strength, trend)
- Institutional conviction calculation
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

from skills.data_extraction.institutional_flow_tracker import InstitutionalFlowTracker


class TestInstitutionalFlowTrackerInit:
    """Test InstitutionalFlowTracker initialization"""

    def test_initialization(self):
        """Test tracker initializes with MCP client"""
        mock_client = MagicMock()
        tracker = InstitutionalFlowTracker(mock_client)

        assert tracker.mcp == mock_client
        assert tracker is not None


class TestTrackMethod:
    """Test main track() method"""

    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client with realistic responses"""
        client = AsyncMock()

        # Mock ETF flow response
        client.call_tool.return_value = {
            "content": [
                {
                    "text": "Date: 2025-01-20 | Flow: $100.5M\n"
                    "Date: 2025-01-21 | Flow: $120.3M\n"
                    "Date: 2025-01-22 | Flow: $95.7M\n"
                    "Date: 2025-01-23 | Flow: $110.2M\n"
                    "Date: 2025-01-24 | Flow: $105.8M\n"
                    "Date: 2025-01-25 | Flow: $115.4M\n"
                    "Date: 2025-01-26 | Flow: $125.6M\n"
                }
            ]
        }

        return client

    @pytest.mark.asyncio
    async def test_track_basic_call(self, mock_mcp_client):
        """Test basic track() call returns correct structure"""
        tracker = InstitutionalFlowTracker(mock_mcp_client)

        result = await tracker.track("BTC", period_days=7)

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "data-extraction-skill"
        assert "asset" in result
        assert result["asset"] == "BTC"
        assert "data_type" in result
        assert result["data_type"] == "institutional_flow"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_track_verbose_true(self, mock_mcp_client):
        """Test verbose=True returns full response with metadata"""
        tracker = InstitutionalFlowTracker(mock_mcp_client)

        result = await tracker.track("BTC", period_days=7, verbose=True)

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
        tracker = InstitutionalFlowTracker(mock_mcp_client)

        result = await tracker.track("BTC", period_days=7, verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_track_data_structure(self, mock_mcp_client):
        """Test data structure contains all required fields"""
        tracker = InstitutionalFlowTracker(mock_mcp_client)

        result = await tracker.track("BTC", period_days=7)
        data = result["data"]

        # Verify all required data fields
        assert "net_flow_usd" in data
        assert "flow_direction" in data
        assert "flow_strength" in data
        assert "etf_net_flow_usd" in data
        assert "etf_flow_trend" in data
        assert "exchange_net_flow_usd" in data
        assert "exchange_flow_trend" in data
        assert "institutional_conviction" in data
        assert "period_days" in data
        assert "trading_signal" in data

        # Verify data types
        assert isinstance(data["net_flow_usd"], (int, float))
        assert isinstance(data["flow_direction"], str)
        assert isinstance(data["flow_strength"], str)
        assert isinstance(data["institutional_conviction"], float)
        assert isinstance(data["period_days"], int)

    @pytest.mark.asyncio
    async def test_track_eth_asset(self, mock_mcp_client):
        """Test tracking ETH asset"""
        tracker = InstitutionalFlowTracker(mock_mcp_client)

        result = await tracker.track("ETH", period_days=7)

        assert result["asset"] == "ETH"
        assert "data" in result


class TestFlowClassification:
    """Test flow classification methods"""

    def test_classify_flow_direction_inflow(self):
        """Test inflow classification"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # Test strong inflow ($150M)
        direction = tracker._classify_flow_direction(150_000_000)
        assert direction == "inflow"

    def test_classify_flow_direction_outflow(self):
        """Test outflow classification"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # Test strong outflow (-$150M)
        direction = tracker._classify_flow_direction(-150_000_000)
        assert direction == "outflow"

    def test_classify_flow_direction_neutral(self):
        """Test neutral classification"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # Test neutral flow ($50M - below $100M threshold)
        direction = tracker._classify_flow_direction(50_000_000)
        assert direction == "neutral"

        # Test zero flow
        direction = tracker._classify_flow_direction(0)
        assert direction == "neutral"

    def test_classify_flow_strength_very_strong(self):
        """Test very_strong strength classification"""
        tracker = InstitutionalFlowTracker(MagicMock())

        strength = tracker._classify_flow_strength(600_000_000)
        assert strength == "very_strong"

        strength = tracker._classify_flow_strength(-600_000_000)
        assert strength == "very_strong"

    def test_classify_flow_strength_strong(self):
        """Test strong strength classification"""
        tracker = InstitutionalFlowTracker(MagicMock())

        strength = tracker._classify_flow_strength(400_000_000)
        assert strength == "strong"

    def test_classify_flow_strength_moderate(self):
        """Test moderate strength classification"""
        tracker = InstitutionalFlowTracker(MagicMock())

        strength = tracker._classify_flow_strength(200_000_000)
        assert strength == "moderate"

    def test_classify_flow_strength_weak(self):
        """Test weak strength classification"""
        tracker = InstitutionalFlowTracker(MagicMock())

        strength = tracker._classify_flow_strength(50_000_000)
        assert strength == "weak"


class TestTrendAnalysis:
    """Test flow trend analysis"""

    def test_analyze_flow_trend_increasing(self):
        """Test increasing trend detection"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # Recent flows higher than earlier (recent first)
        daily_flows = [150, 140, 130, 100, 90, 80, 70]

        trend = tracker._analyze_flow_trend(daily_flows)
        assert trend == "increasing"

    def test_analyze_flow_trend_decreasing(self):
        """Test decreasing trend detection"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # Recent flows lower than earlier (recent first)
        daily_flows = [70, 80, 90, 120, 130, 140, 150]

        trend = tracker._analyze_flow_trend(daily_flows)
        assert trend == "decreasing"

    def test_analyze_flow_trend_stable(self):
        """Test stable trend detection"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # Relatively stable flows
        daily_flows = [100, 105, 98, 102, 99, 103, 101]

        trend = tracker._analyze_flow_trend(daily_flows)
        assert trend == "stable"

    def test_analyze_flow_trend_empty_list(self):
        """Test trend analysis with empty list"""
        tracker = InstitutionalFlowTracker(MagicMock())

        trend = tracker._analyze_flow_trend([])
        assert trend == "stable"

    def test_analyze_flow_trend_single_value(self):
        """Test trend analysis with single value"""
        tracker = InstitutionalFlowTracker(MagicMock())

        trend = tracker._analyze_flow_trend([100])
        assert trend == "stable"


class TestConvictionCalculation:
    """Test institutional conviction calculation"""

    def test_calculate_conviction_aligned_flows(self):
        """Test high conviction when flows are aligned"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # Both flows positive (aligned)
        conviction = tracker._calculate_conviction(
            etf_flow=500_000_000,
            exchange_flow=100_000_000,
            etf_trend="increasing",
            exchange_trend="increasing",
        )

        # Should have high conviction (0.80 base + 0.15 trend alignment)
        assert conviction >= 0.80
        assert conviction <= 1.0

    def test_calculate_conviction_divergent_flows(self):
        """Test lower conviction when flows diverge"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # ETF positive, exchange negative (divergent)
        conviction = tracker._calculate_conviction(
            etf_flow=500_000_000,
            exchange_flow=-100_000_000,
            etf_trend="increasing",
            exchange_trend="decreasing",
        )

        # Should have low conviction (0.40 base)
        assert conviction <= 0.50

    def test_calculate_conviction_neutral_flow(self):
        """Test moderate conviction with one neutral flow"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # ETF positive, exchange neutral
        conviction = tracker._calculate_conviction(
            etf_flow=500_000_000,
            exchange_flow=0,
            etf_trend="increasing",
            exchange_trend="stable",
        )

        # Should have moderate conviction (0.60 base + adjustments)
        assert conviction >= 0.55
        assert conviction <= 0.75

    def test_calculate_conviction_capped_at_one(self):
        """Test conviction is capped at 1.0"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # Maximum possible conviction scenario
        conviction = tracker._calculate_conviction(
            etf_flow=1_000_000_000,
            exchange_flow=500_000_000,
            etf_trend="increasing",
            exchange_trend="increasing",
        )

        assert conviction <= 1.0


class TestTradingSignalGeneration:
    """Test trading signal generation logic"""

    def test_strong_bullish_signal(self):
        """Test strong bullish signal generation"""
        tracker = InstitutionalFlowTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            direction="inflow",
            strength="very_strong",
            conviction=0.85,
            etf_trend="increasing",
        )

        assert "bullish" in signal.lower()
        assert "accumulation" in signal.lower()

    def test_strong_bearish_signal(self):
        """Test strong bearish signal generation"""
        tracker = InstitutionalFlowTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            direction="outflow",
            strength="very_strong",
            conviction=0.85,
            etf_trend="decreasing",
        )

        assert "bearish" in signal.lower()
        assert "distribution" in signal.lower()

    def test_moderate_bullish_signal(self):
        """Test moderate bullish signal"""
        tracker = InstitutionalFlowTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            direction="inflow",
            strength="moderate",
            conviction=0.65,
            etf_trend="stable",
        )

        assert "moderate" in signal.lower()
        assert "bullish" in signal.lower()

    def test_neutral_signal(self):
        """Test neutral/weak signal"""
        tracker = InstitutionalFlowTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            direction="neutral",
            strength="weak",
            conviction=0.50,
            etf_trend="stable",
        )

        assert "retail" in signal.lower() or "mixed" in signal.lower()

    def test_etf_increasing_signal(self):
        """Test signal when ETF flows increasing"""
        tracker = InstitutionalFlowTracker(MagicMock())

        signal = tracker._generate_trading_signal(
            direction="neutral",
            strength="weak",
            conviction=0.50,
            etf_trend="increasing",
        )

        assert "increasing" in signal.lower() or "accumulation" in signal.lower()


class TestETFFlowProcessing:
    """Test ETF flow data processing"""

    def test_process_etf_flows_valid_data(self):
        """Test processing valid ETF flow data"""
        tracker = InstitutionalFlowTracker(MagicMock())

        result = {
            "content": [
                {
                    "text": "Date: 2025-01-26 | Flow: $100.5M\n"
                    "Date: 2025-01-25 | Flow: $95.3M\n"
                }
            ]
        }

        processed = tracker._process_etf_flows(result, period_days=2)

        assert "net_flow_usd" in processed
        assert "daily_flows" in processed
        assert processed["net_flow_usd"] > 0
        assert len(processed["daily_flows"]) <= 2

    def test_process_etf_flows_billion_suffix(self):
        """Test processing flows with billion suffix"""
        tracker = InstitutionalFlowTracker(MagicMock())

        result = {
            "content": [{"text": "Date: 2025-01-26 | Flow: $1.5B\n"}]
        }

        processed = tracker._process_etf_flows(result, period_days=1)

        # Should convert $1.5B to 1,500,000,000
        assert processed["net_flow_usd"] == 1_500_000_000

    def test_process_etf_flows_exception_handling(self):
        """Test ETF flow processing handles exceptions gracefully"""
        tracker = InstitutionalFlowTracker(MagicMock())

        # Test with Exception
        result = Exception("Network error")
        processed = tracker._process_etf_flows(result, period_days=7)

        assert processed["net_flow_usd"] == 0.0
        assert processed["daily_flows"] == []

    def test_process_etf_flows_invalid_format(self):
        """Test ETF flow processing handles invalid format"""
        tracker = InstitutionalFlowTracker(MagicMock())

        result = {"content": [{"invalid": "data"}]}
        processed = tracker._process_etf_flows(result, period_days=7)

        assert processed["net_flow_usd"] == 0.0
        assert processed["daily_flows"] == []


class TestExchangeFlowProcessing:
    """Test exchange flow data processing"""

    def test_process_exchange_flows_valid_data(self):
        """Test processing valid exchange trade data"""
        tracker = InstitutionalFlowTracker(MagicMock())

        result = {
            "content": [
                {
                    "trades": [
                        {"amount": 2.5, "price": 50000, "side": "buy"},
                        {"amount": 1.8, "price": 50000, "side": "sell"},
                        {"amount": 3.0, "price": 50000, "side": "buy"},
                    ]
                }
            ]
        }

        processed = tracker._process_exchange_flows(result)

        assert "net_flow_usd" in processed
        assert "daily_flows" in processed
        # Net flow should be positive (more buy volume)

    def test_process_exchange_flows_filters_small_trades(self):
        """Test that small trades (<$100K) are filtered out"""
        tracker = InstitutionalFlowTracker(MagicMock())

        result = {
            "content": [
                {
                    "trades": [
                        # Small trade - should be filtered
                        {"amount": 0.001, "price": 50000, "side": "buy"},
                        # Large trade - should be counted
                        {"amount": 3.0, "price": 50000, "side": "buy"},
                    ]
                }
            ]
        }

        processed = tracker._process_exchange_flows(result)

        # Should only count the large trade
        assert processed["net_flow_usd"] == 150_000  # 3.0 * 50000

    def test_process_exchange_flows_exception_handling(self):
        """Test exchange flow processing handles exceptions"""
        tracker = InstitutionalFlowTracker(MagicMock())

        result = Exception("API error")
        processed = tracker._process_exchange_flows(result)

        assert processed["net_flow_usd"] == 0.0
        assert processed["daily_flows"] == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
