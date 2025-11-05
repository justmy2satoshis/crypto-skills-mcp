"""
Unit tests for WhaleActivityMonitor Skill

Tests whale activity monitoring functionality including:
- Whale transaction identification (threshold filtering)
- Price extraction from ticker data
- Net flow calculation (buy inflow - sell outflow)
- Flow direction classification
- Activity level classification (very_high/high/moderate/low)
- Accumulation pattern detection (>70% buys + $10M+ inflow)
- Distribution pattern detection (>70% sells + $10M+ outflow)
- Position bias determination (accumulating/distributing/bullish/bearish/neutral)
- Conviction calculation (consistency + magnitude adjustments)
- Trading signal generation (7 distinct signals)
- Confidence calculation
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

from skills.sentiment_analysis.whale_activity_monitor import WhaleActivityMonitor


class TestWhaleActivityMonitorInit:
    """Test WhaleActivityMonitor initialization"""

    def test_initialization(self):
        """Test monitor initializes with MCP client"""
        mock_client = MagicMock()
        monitor = WhaleActivityMonitor(mock_client)

        assert monitor.mcp == mock_client
        assert monitor is not None


class TestMonitorMethod:
    """Test main monitor() method"""

    @pytest.fixture
    def mock_mcp_responses(self):
        """Create mock MCP responses for whale activity"""
        # Mock ticker response (price data)
        ticker_response = {
            "content": [
                {
                    "last": 50000.0,  # Current BTC price
                    "bid": 49980.0,
                    "ask": 50020.0,
                }
            ]
        }

        # Mock trades response (whale transactions)
        trades_response = {
            "content": [
                {
                    "trades": [
                        # Large buy (whale accumulation)
                        {"amount": 25.0, "price": 50000, "side": "buy", "timestamp": 1706227200000},
                        # Large buy (whale accumulation)
                        {"amount": 30.0, "price": 50000, "side": "buy", "timestamp": 1706227300000},
                        # Large sell (whale distribution)
                        {"amount": 18.0, "price": 50000, "side": "sell", "timestamp": 1706227400000},
                        # Large buy (whale accumulation)
                        {"amount": 22.0, "price": 50000, "side": "buy", "timestamp": 1706227500000},
                        # Small trade - below threshold
                        {"amount": 0.5, "price": 50000, "side": "buy", "timestamp": 1706227600000},
                    ]
                }
            ]
        }

        return {
            "ticker": ticker_response,
            "trades": trades_response,
        }

    @pytest.mark.asyncio
    async def test_monitor_basic_call(self, mock_mcp_responses):
        """Test basic monitor() call returns correct structure"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = [
            mock_mcp_responses["trades"],  # fetchTrades
            mock_mcp_responses["ticker"],  # fetchTicker
        ]

        monitor = WhaleActivityMonitor(mock_client)

        result = await monitor.monitor("BTC", threshold_usd=1_000_000)

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "sentiment-analysis-skill"
        assert "symbol" in result
        assert result["symbol"] == "BTC"
        assert "data_type" in result
        assert result["data_type"] == "whale_activity"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_monitor_verbose_true(self, mock_mcp_responses):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = [
            mock_mcp_responses["trades"],
            mock_mcp_responses["ticker"],
        ]

        monitor = WhaleActivityMonitor(mock_client)

        result = await monitor.monitor("BTC", threshold_usd=1_000_000, verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "symbol" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "threshold_usd" in result["metadata"]
        assert "lookback_hours" in result["metadata"]
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_monitor_verbose_false(self, mock_mcp_responses):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = [
            mock_mcp_responses["trades"],
            mock_mcp_responses["ticker"],
        ]

        monitor = WhaleActivityMonitor(mock_client)

        result = await monitor.monitor("BTC", threshold_usd=1_000_000, verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_monitor_data_structure(self, mock_mcp_responses):
        """Test data structure contains all required fields"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = [
            mock_mcp_responses["trades"],
            mock_mcp_responses["ticker"],
        ]

        monitor = WhaleActivityMonitor(mock_client)

        result = await monitor.monitor("BTC", threshold_usd=1_000_000)
        data = result["data"]

        # Verify all required data fields
        assert "net_flow_usd" in data
        assert "flow_direction" in data
        assert "activity_level" in data
        assert "accumulation_signal" in data
        assert "distribution_signal" in data
        assert "large_transactions" in data
        assert "total_volume_usd" in data
        assert "position_bias" in data
        assert "conviction" in data
        assert "trading_signal" in data

        # Verify data types
        assert isinstance(data["net_flow_usd"], (int, float))
        assert isinstance(data["flow_direction"], str)
        assert isinstance(data["activity_level"], str)
        assert isinstance(data["accumulation_signal"], bool)
        assert isinstance(data["distribution_signal"], bool)
        assert isinstance(data["large_transactions"], int)
        assert isinstance(data["total_volume_usd"], (int, float))
        assert isinstance(data["position_bias"], str)
        assert isinstance(data["conviction"], float)
        assert isinstance(data["trading_signal"], str)


class TestPriceExtraction:
    """Test price extraction from ticker data"""

    def test_extract_price_valid_data(self):
        """Test price extraction from valid ticker data"""
        monitor = WhaleActivityMonitor(MagicMock())

        ticker_result = {
            "content": [
                {
                    "last": 50000.0,
                    "bid": 49980.0,
                    "ask": 50020.0,
                }
            ]
        }

        price = monitor._extract_price(ticker_result)
        assert price == 50000.0

    def test_extract_price_exception(self):
        """Test price extraction handles exceptions"""
        monitor = WhaleActivityMonitor(MagicMock())

        price = monitor._extract_price(Exception("API error"))
        assert price == 0.0

    def test_extract_price_invalid_format(self):
        """Test price extraction handles invalid format"""
        monitor = WhaleActivityMonitor(MagicMock())

        # Missing 'content' key
        invalid_result = {"invalid": "data"}
        price = monitor._extract_price(invalid_result)
        assert price == 0.0

        # Empty content list
        empty_result = {"content": []}
        price = monitor._extract_price(empty_result)
        assert price == 0.0

    def test_extract_price_missing_last_field(self):
        """Test price extraction when 'last' field is missing"""
        monitor = WhaleActivityMonitor(MagicMock())

        ticker_result = {
            "content": [
                {
                    "bid": 49980.0,
                    "ask": 50020.0,
                    # 'last' missing
                }
            ]
        }

        price = monitor._extract_price(ticker_result)
        assert price == 0.0


class TestWhaleTransactionIdentification:
    """Test whale transaction identification"""

    def test_identify_whale_transactions_above_threshold(self):
        """Test identification of transactions above threshold"""
        monitor = WhaleActivityMonitor(MagicMock())

        trades_result = {
            "content": [
                {
                    "trades": [
                        # $1.5M - above $1M threshold
                        {"amount": 30.0, "price": 50000, "side": "buy", "timestamp": 1706227200000},
                        # $500K - below $1M threshold
                        {"amount": 10.0, "price": 50000, "side": "sell", "timestamp": 1706227300000},
                        # $2M - above $1M threshold
                        {"amount": 40.0, "price": 50000, "side": "buy", "timestamp": 1706227400000},
                    ]
                }
            ]
        }

        whale_txs = monitor._identify_whale_transactions(
            trades_result, current_price=50000, threshold_usd=1_000_000
        )

        # Should identify 2 whale transactions
        assert len(whale_txs) == 2
        assert whale_txs[0]["value_usd"] == 1_500_000  # 30 * 50000
        assert whale_txs[1]["value_usd"] == 2_000_000  # 40 * 50000

    def test_identify_whale_transactions_custom_threshold(self):
        """Test whale identification with custom threshold"""
        monitor = WhaleActivityMonitor(MagicMock())

        trades_result = {
            "content": [
                {
                    "trades": [
                        # $750K - above $500K threshold
                        {"amount": 15.0, "price": 50000, "side": "buy", "timestamp": 1706227200000},
                        # $250K - below $500K threshold
                        {"amount": 5.0, "price": 50000, "side": "sell", "timestamp": 1706227300000},
                    ]
                }
            ]
        }

        whale_txs = monitor._identify_whale_transactions(
            trades_result, current_price=50000, threshold_usd=500_000
        )

        # Should identify 1 whale transaction
        assert len(whale_txs) == 1
        assert whale_txs[0]["value_usd"] == 750_000

    def test_identify_whale_transactions_exception_handling(self):
        """Test whale identification handles exceptions"""
        monitor = WhaleActivityMonitor(MagicMock())

        whale_txs = monitor._identify_whale_transactions(
            Exception("API error"), current_price=50000, threshold_usd=1_000_000
        )

        assert whale_txs == []

    def test_identify_whale_transactions_preserves_metadata(self):
        """Test whale identification preserves transaction metadata"""
        monitor = WhaleActivityMonitor(MagicMock())

        trades_result = {
            "content": [
                {
                    "trades": [
                        {
                            "amount": 30.0,
                            "price": 50000,
                            "side": "buy",
                            "timestamp": 1706227200000,
                        },
                    ]
                }
            ]
        }

        whale_txs = monitor._identify_whale_transactions(
            trades_result, current_price=50000, threshold_usd=1_000_000
        )

        assert len(whale_txs) == 1
        assert "value_usd" in whale_txs[0]
        assert "amount" in whale_txs[0]
        assert "price" in whale_txs[0]
        assert "side" in whale_txs[0]
        assert "timestamp" in whale_txs[0]


class TestNetFlowCalculation:
    """Test net flow calculation"""

    def test_calculate_net_flow_inflow(self):
        """Test net flow calculation with more buys than sells"""
        monitor = WhaleActivityMonitor(MagicMock())

        transactions = [
            {"value_usd": 10_000_000, "side": "buy"},  # $10M buy
            {"value_usd": 8_000_000, "side": "buy"},  # $8M buy
            {"value_usd": 3_000_000, "side": "sell"},  # $3M sell
        ]

        net_flow, direction = monitor._calculate_net_flow(transactions)

        # Net flow = 10M + 8M - 3M = 15M (inflow)
        assert net_flow == 15_000_000
        assert direction == "inflow"  # >$5M threshold

    def test_calculate_net_flow_outflow(self):
        """Test net flow calculation with more sells than buys"""
        monitor = WhaleActivityMonitor(MagicMock())

        transactions = [
            {"value_usd": 2_000_000, "side": "buy"},  # $2M buy
            {"value_usd": 8_000_000, "side": "sell"},  # $8M sell
            {"value_usd": 6_000_000, "side": "sell"},  # $6M sell
        ]

        net_flow, direction = monitor._calculate_net_flow(transactions)

        # Net flow = 2M - 8M - 6M = -12M (outflow)
        assert net_flow == -12_000_000
        assert direction == "outflow"  # <-$5M threshold

    def test_calculate_net_flow_neutral(self):
        """Test net flow calculation with balanced flows"""
        monitor = WhaleActivityMonitor(MagicMock())

        transactions = [
            {"value_usd": 3_000_000, "side": "buy"},  # $3M buy
            {"value_usd": 2_500_000, "side": "sell"},  # $2.5M sell
        ]

        net_flow, direction = monitor._calculate_net_flow(transactions)

        # Net flow = 3M - 2.5M = 500K (neutral)
        assert net_flow == 500_000
        assert direction == "neutral"  # Within -$5M to +$5M threshold

    def test_calculate_net_flow_empty_list(self):
        """Test net flow calculation with empty transaction list"""
        monitor = WhaleActivityMonitor(MagicMock())

        net_flow, direction = monitor._calculate_net_flow([])

        assert net_flow == 0.0
        assert direction == "neutral"

    def test_calculate_net_flow_threshold_boundary(self):
        """Test net flow calculation at threshold boundaries"""
        monitor = WhaleActivityMonitor(MagicMock())

        # Exactly at +$5M threshold
        transactions_at_threshold = [{"value_usd": 5_000_001, "side": "buy"}]
        net_flow, direction = monitor._calculate_net_flow(transactions_at_threshold)
        assert direction == "inflow"

        # Just below -$5M threshold
        transactions_below_threshold = [{"value_usd": 4_999_999, "side": "sell"}]
        net_flow, direction = monitor._calculate_net_flow(transactions_below_threshold)
        assert direction == "neutral"


class TestActivityLevelClassification:
    """Test activity level classification"""

    def test_classify_activity_very_high_by_count(self):
        """Test very_high classification by transaction count"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 15+ transactions = very_high
        level = monitor._classify_activity_level(
            transaction_count=15, total_volume_usd=50_000_000
        )
        assert level == "very_high"

    def test_classify_activity_very_high_by_volume(self):
        """Test very_high classification by volume"""
        monitor = WhaleActivityMonitor(MagicMock())

        # $200M+ volume = very_high
        level = monitor._classify_activity_level(
            transaction_count=5, total_volume_usd=200_000_000
        )
        assert level == "very_high"

    def test_classify_activity_high(self):
        """Test high classification"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 10+ transactions OR $100M+ volume = high
        level = monitor._classify_activity_level(
            transaction_count=10, total_volume_usd=50_000_000
        )
        assert level == "high"

        level = monitor._classify_activity_level(
            transaction_count=5, total_volume_usd=100_000_000
        )
        assert level == "high"

    def test_classify_activity_moderate(self):
        """Test moderate classification"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 5+ transactions OR $50M+ volume = moderate
        level = monitor._classify_activity_level(
            transaction_count=5, total_volume_usd=25_000_000
        )
        assert level == "moderate"

        level = monitor._classify_activity_level(
            transaction_count=3, total_volume_usd=50_000_000
        )
        assert level == "moderate"

    def test_classify_activity_low(self):
        """Test low classification"""
        monitor = WhaleActivityMonitor(MagicMock())

        # <5 transactions AND <$50M volume = low
        level = monitor._classify_activity_level(
            transaction_count=4, total_volume_usd=40_000_000
        )
        assert level == "low"

        level = monitor._classify_activity_level(
            transaction_count=1, total_volume_usd=10_000_000
        )
        assert level == "low"


class TestAccumulationDetection:
    """Test accumulation pattern detection"""

    def test_detect_accumulation_pattern(self):
        """Test detection of clear accumulation pattern"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 8 buys, 2 sells = 80% buy ratio
        transactions = [
            {"side": "buy"} for _ in range(8)
        ] + [{"side": "sell"} for _ in range(2)]

        # Net flow > $10M required
        accumulation = monitor._detect_accumulation(transactions, net_flow_usd=15_000_000)
        assert accumulation is True

    def test_detect_accumulation_insufficient_buy_ratio(self):
        """Test accumulation not detected with low buy ratio"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 6 buys, 4 sells = 60% buy ratio (below 70% threshold)
        transactions = [
            {"side": "buy"} for _ in range(6)
        ] + [{"side": "sell"} for _ in range(4)]

        accumulation = monitor._detect_accumulation(transactions, net_flow_usd=15_000_000)
        assert accumulation is False

    def test_detect_accumulation_insufficient_flow(self):
        """Test accumulation not detected with low net flow"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 8 buys, 2 sells = 80% buy ratio (sufficient)
        transactions = [
            {"side": "buy"} for _ in range(8)
        ] + [{"side": "sell"} for _ in range(2)]

        # Net flow < $10M threshold
        accumulation = monitor._detect_accumulation(transactions, net_flow_usd=8_000_000)
        assert accumulation is False

    def test_detect_accumulation_negative_flow(self):
        """Test accumulation not detected with negative flow"""
        monitor = WhaleActivityMonitor(MagicMock())

        transactions = [{"side": "buy"} for _ in range(8)]

        # Negative net flow
        accumulation = monitor._detect_accumulation(transactions, net_flow_usd=-5_000_000)
        assert accumulation is False

    def test_detect_accumulation_empty_transactions(self):
        """Test accumulation detection with empty transactions"""
        monitor = WhaleActivityMonitor(MagicMock())

        accumulation = monitor._detect_accumulation([], net_flow_usd=15_000_000)
        assert accumulation is False


class TestDistributionDetection:
    """Test distribution pattern detection"""

    def test_detect_distribution_pattern(self):
        """Test detection of clear distribution pattern"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 2 buys, 8 sells = 80% sell ratio
        transactions = [
            {"side": "buy"} for _ in range(2)
        ] + [{"side": "sell"} for _ in range(8)]

        # Net flow < -$10M required
        distribution = monitor._detect_distribution(transactions, net_flow_usd=-15_000_000)
        assert distribution is True

    def test_detect_distribution_insufficient_sell_ratio(self):
        """Test distribution not detected with low sell ratio"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 4 buys, 6 sells = 60% sell ratio (below 70% threshold)
        transactions = [
            {"side": "buy"} for _ in range(4)
        ] + [{"side": "sell"} for _ in range(6)]

        distribution = monitor._detect_distribution(transactions, net_flow_usd=-15_000_000)
        assert distribution is False

    def test_detect_distribution_insufficient_flow(self):
        """Test distribution not detected with insufficient outflow"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 2 buys, 8 sells = 80% sell ratio (sufficient)
        transactions = [
            {"side": "buy"} for _ in range(2)
        ] + [{"side": "sell"} for _ in range(8)]

        # Net flow > -$10M threshold
        distribution = monitor._detect_distribution(transactions, net_flow_usd=-8_000_000)
        assert distribution is False

    def test_detect_distribution_positive_flow(self):
        """Test distribution not detected with positive flow"""
        monitor = WhaleActivityMonitor(MagicMock())

        transactions = [{"side": "sell"} for _ in range(8)]

        # Positive net flow
        distribution = monitor._detect_distribution(transactions, net_flow_usd=5_000_000)
        assert distribution is False


class TestPositionBiasDetermination:
    """Test position bias determination"""

    def test_position_bias_accumulating(self):
        """Test accumulating position bias"""
        monitor = WhaleActivityMonitor(MagicMock())

        bias = monitor._determine_position_bias(
            net_flow_usd=15_000_000,
            accumulation=True,
            distribution=False,
        )
        assert bias == "accumulating"

    def test_position_bias_distributing(self):
        """Test distributing position bias"""
        monitor = WhaleActivityMonitor(MagicMock())

        bias = monitor._determine_position_bias(
            net_flow_usd=-15_000_000,
            accumulation=False,
            distribution=True,
        )
        assert bias == "distributing"

    def test_position_bias_bullish(self):
        """Test bullish position bias without accumulation signal"""
        monitor = WhaleActivityMonitor(MagicMock())

        bias = monitor._determine_position_bias(
            net_flow_usd=8_000_000,  # >$5M but no accumulation signal
            accumulation=False,
            distribution=False,
        )
        assert bias == "bullish"

    def test_position_bias_bearish(self):
        """Test bearish position bias without distribution signal"""
        monitor = WhaleActivityMonitor(MagicMock())

        bias = monitor._determine_position_bias(
            net_flow_usd=-8_000_000,  # <-$5M but no distribution signal
            accumulation=False,
            distribution=False,
        )
        assert bias == "bearish"

    def test_position_bias_neutral(self):
        """Test neutral position bias"""
        monitor = WhaleActivityMonitor(MagicMock())

        bias = monitor._determine_position_bias(
            net_flow_usd=2_000_000,  # Within -$5M to +$5M
            accumulation=False,
            distribution=False,
        )
        assert bias == "neutral"


class TestConvictionCalculation:
    """Test conviction calculation"""

    def test_conviction_high_buy_ratio(self):
        """Test conviction with high buy ratio"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 9 buys, 1 sell = 90% buy ratio
        transactions = [
            {"side": "buy"} for _ in range(9)
        ] + [{"side": "sell"} for _ in range(1)]

        conviction = monitor._calculate_conviction(transactions, net_flow_usd=30_000_000)

        # Base 0.9 + 0.10 (>$20M) = 1.0 (capped)
        assert conviction >= 0.90
        assert conviction <= 1.0

    def test_conviction_high_sell_ratio(self):
        """Test conviction with high sell ratio"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 1 buy, 9 sells = 90% sell ratio
        transactions = [
            {"side": "buy"} for _ in range(1)
        ] + [{"side": "sell"} for _ in range(9)]

        conviction = monitor._calculate_conviction(transactions, net_flow_usd=-30_000_000)

        # Base 0.9 + 0.10 (>$20M) = 1.0 (capped)
        assert conviction >= 0.90
        assert conviction <= 1.0

    def test_conviction_balanced_ratio(self):
        """Test conviction with balanced buy/sell ratio"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 5 buys, 5 sells = 50% ratio
        transactions = [
            {"side": "buy"} for _ in range(5)
        ] + [{"side": "sell"} for _ in range(5)]

        conviction = monitor._calculate_conviction(transactions, net_flow_usd=1_000_000)

        # Base 0.5 (neutral)
        assert conviction == 0.5

    def test_conviction_large_flow_bonus(self):
        """Test conviction bonus for large flows"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 7 buys, 3 sells = 70% buy ratio
        transactions = [
            {"side": "buy"} for _ in range(7)
        ] + [{"side": "sell"} for _ in range(3)]

        # Test $50M+ flow (should get +0.15 bonus)
        conviction_large = monitor._calculate_conviction(transactions, net_flow_usd=60_000_000)
        assert conviction_large >= 0.85  # 0.70 + 0.15

        # Test $20M-$50M flow (should get +0.10 bonus)
        conviction_medium = monitor._calculate_conviction(transactions, net_flow_usd=30_000_000)
        assert conviction_medium >= 0.80  # 0.70 + 0.10

    def test_conviction_empty_transactions(self):
        """Test conviction with empty transactions"""
        monitor = WhaleActivityMonitor(MagicMock())

        conviction = monitor._calculate_conviction([], net_flow_usd=0)
        assert conviction == 0.0

    def test_conviction_capped_at_one(self):
        """Test conviction is capped at 1.0"""
        monitor = WhaleActivityMonitor(MagicMock())

        # 10 buys, 0 sells = 100% buy ratio
        transactions = [{"side": "buy"} for _ in range(10)]

        conviction = monitor._calculate_conviction(transactions, net_flow_usd=100_000_000)
        assert conviction <= 1.0


class TestTradingSignalGeneration:
    """Test trading signal generation"""

    def test_signal_strong_bullish(self):
        """Test strong bullish signal generation"""
        monitor = WhaleActivityMonitor(MagicMock())

        signal = monitor._generate_trading_signal(
            position_bias="accumulating",
            activity_level="high",
            conviction=0.85,
        )

        assert "strong bullish signal" in signal.lower()
        assert "accumulating" in signal.lower()

    def test_signal_moderate_bullish(self):
        """Test moderate bullish signal generation"""
        monitor = WhaleActivityMonitor(MagicMock())

        # accumulating without high conviction
        signal = monitor._generate_trading_signal(
            position_bias="accumulating",
            activity_level="moderate",
            conviction=0.65,
        )

        assert "bullish signal" in signal.lower()
        assert "accumulating" in signal.lower()

        # bullish bias
        signal = monitor._generate_trading_signal(
            position_bias="bullish",
            activity_level="moderate",
            conviction=0.60,
        )

        assert "bullish signal" in signal.lower()

    def test_signal_strong_bearish(self):
        """Test strong bearish signal generation"""
        monitor = WhaleActivityMonitor(MagicMock())

        signal = monitor._generate_trading_signal(
            position_bias="distributing",
            activity_level="high",
            conviction=0.85,
        )

        assert "strong bearish signal" in signal.lower()
        assert "distributing" in signal.lower()

    def test_signal_moderate_bearish(self):
        """Test moderate bearish signal generation"""
        monitor = WhaleActivityMonitor(MagicMock())

        # distributing without high conviction
        signal = monitor._generate_trading_signal(
            position_bias="distributing",
            activity_level="moderate",
            conviction=0.65,
        )

        assert "bearish signal" in signal.lower()
        assert "distributing" in signal.lower()

        # bearish bias
        signal = monitor._generate_trading_signal(
            position_bias="bearish",
            activity_level="moderate",
            conviction=0.60,
        )

        assert "bearish signal" in signal.lower()

    def test_signal_high_activity_neutral(self):
        """Test signal for high activity with neutral bias"""
        monitor = WhaleActivityMonitor(MagicMock())

        signal = monitor._generate_trading_signal(
            position_bias="neutral",
            activity_level="high",
            conviction=0.55,
        )

        assert "high whale activity" in signal.lower()
        assert "monitor" in signal.lower()

        signal = monitor._generate_trading_signal(
            position_bias="neutral",
            activity_level="very_high",
            conviction=0.55,
        )

        assert "high whale activity" in signal.lower()

    def test_signal_low_activity(self):
        """Test signal for low whale activity"""
        monitor = WhaleActivityMonitor(MagicMock())

        signal = monitor._generate_trading_signal(
            position_bias="neutral",
            activity_level="low",
            conviction=0.50,
        )

        assert "low whale activity" in signal.lower()
        assert "retail" in signal.lower()

        signal = monitor._generate_trading_signal(
            position_bias="neutral",
            activity_level="moderate",
            conviction=0.50,
        )

        assert "low whale activity" in signal.lower()

    def test_signal_default_mixed(self):
        """Test default mixed signal"""
        monitor = WhaleActivityMonitor(MagicMock())

        # This shouldn't match any specific condition
        # (implementation may vary, but should return a valid signal)
        signal = monitor._generate_trading_signal(
            position_bias="neutral",
            activity_level="high",
            conviction=0.50,
        )

        assert isinstance(signal, str)
        assert len(signal) > 0


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    @pytest.mark.asyncio
    async def test_confidence_base_level(self):
        """Test base confidence level"""
        mock_client = AsyncMock()

        # Mock minimal whale activity
        mock_client.call_tool.side_effect = [
            {"content": [{"trades": []}]},  # Empty trades
            {"content": [{"last": 50000}]},  # Price
        ]

        monitor = WhaleActivityMonitor(mock_client)
        result = await monitor.monitor("BTC", threshold_usd=1_000_000, verbose=True)

        # Base confidence = 0.60
        assert result["metadata"]["confidence"] >= 0.60

    @pytest.mark.asyncio
    async def test_confidence_with_transaction_count_bonus(self):
        """Test confidence bonus for transaction count >= 10"""
        mock_client = AsyncMock()

        # Mock 10+ whale transactions
        trades = [
            {"amount": 25.0, "price": 50000, "side": "buy", "timestamp": i}
            for i in range(10)
        ]
        mock_client.call_tool.side_effect = [
            {"content": [{"trades": trades}]},
            {"content": [{"last": 50000}]},
        ]

        monitor = WhaleActivityMonitor(mock_client)
        result = await monitor.monitor("BTC", threshold_usd=1_000_000, verbose=True)

        # Base 0.60 + 0.10 (transaction count)
        assert result["metadata"]["confidence"] >= 0.70

    @pytest.mark.asyncio
    async def test_confidence_capped_at_ninety(self):
        """Test confidence is capped at 0.90"""
        mock_client = AsyncMock()

        # Mock scenario with all bonuses
        trades = [
            {"amount": 30.0, "price": 50000, "side": "buy", "timestamp": i}
            for i in range(15)
        ]  # 15 buys = high conviction
        mock_client.call_tool.side_effect = [
            {"content": [{"trades": trades}]},
            {"content": [{"last": 50000}]},
        ]

        monitor = WhaleActivityMonitor(mock_client)
        result = await monitor.monitor("BTC", threshold_usd=1_000_000, verbose=True)

        # Should be capped at 0.90
        assert result["metadata"]["confidence"] <= 0.90


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_monitor_with_api_errors(self):
        """Test monitor handles API errors gracefully"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = [
            Exception("Trades API error"),
            Exception("Ticker API error"),
        ]

        monitor = WhaleActivityMonitor(mock_client)
        result = await monitor.monitor("BTC", threshold_usd=1_000_000)

        # Should return valid structure with zero flows
        assert "data" in result
        assert result["data"]["net_flow_usd"] == 0.0
        assert result["data"]["large_transactions"] == 0

    @pytest.mark.asyncio
    async def test_monitor_with_empty_trades(self):
        """Test monitor with no whale transactions"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = [
            {"content": [{"trades": []}]},  # Empty trades
            {"content": [{"last": 50000}]},
        ]

        monitor = WhaleActivityMonitor(mock_client)
        result = await monitor.monitor("BTC", threshold_usd=1_000_000)

        # Should handle empty data
        assert result["data"]["net_flow_usd"] == 0.0
        assert result["data"]["flow_direction"] == "neutral"
        assert result["data"]["large_transactions"] == 0

    @pytest.mark.asyncio
    async def test_monitor_eth_symbol(self):
        """Test monitoring ETH symbol"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = [
            {"content": [{"trades": []}]},
            {"content": [{"last": 3000}]},
        ]

        monitor = WhaleActivityMonitor(mock_client)
        result = await monitor.monitor("ETH", threshold_usd=1_000_000)

        assert result["symbol"] == "ETH"

    @pytest.mark.asyncio
    async def test_monitor_custom_threshold(self):
        """Test monitoring with custom threshold"""
        mock_client = AsyncMock()

        trades = [
            {"amount": 10.0, "price": 50000, "side": "buy", "timestamp": 1706227200000},
        ]  # $500K
        mock_client.call_tool.side_effect = [
            {"content": [{"trades": trades}]},
            {"content": [{"last": 50000}]},
        ]

        monitor = WhaleActivityMonitor(mock_client)

        # $500K should be whale with $250K threshold
        result = await monitor.monitor("BTC", threshold_usd=250_000)
        assert result["data"]["large_transactions"] == 1

        # $500K should NOT be whale with $750K threshold
        mock_client.call_tool.side_effect = [
            {"content": [{"trades": trades}]},
            {"content": [{"last": 50000}]},
        ]
        result = await monitor.monitor("BTC", threshold_usd=750_000)
        assert result["data"]["large_transactions"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
