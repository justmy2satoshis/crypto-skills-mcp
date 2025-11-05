"""
Unit tests for SupportResistanceIdentifier Skill

Tests support/resistance level identification functionality including:
- Pivot point detection (local extrema)
- Price level clustering with tolerance
- Level strength calculation (touches + volume weighting)
- Nearest level identification
- Verbose parameter functionality
- Edge case handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.technical_analysis.support_resistance import SupportResistanceIdentifier


class TestSupportResistanceIdentifierInit:
    """Test SupportResistanceIdentifier initialization"""

    def test_initialization(self):
        """Test identifier initializes with MCP client"""
        mock_client = MagicMock()
        identifier = SupportResistanceIdentifier(mock_client)

        assert identifier.mcp == mock_client
        assert identifier is not None


class TestIdentifyMethod:
    """Test main identify() method"""

    @pytest.fixture
    def mock_ohlcv_data(self):
        """Create mock OHLCV data with clear support/resistance levels"""
        # Generate 100 candles with identifiable patterns
        candles = []
        base_price = 42000.0

        for i in range(100):
            # Create price pattern with support at 41000 and resistance at 45000
            if i % 20 < 5:
                # Test support level ~41000
                high = base_price - 800 + (i % 5) * 50
                low = base_price - 1200 + (i % 5) * 50
                close = base_price - 1000 + (i % 5) * 50
            elif i % 20 < 10:
                # Mid-range
                high = base_price + 200
                low = base_price - 200
                close = base_price
            else:
                # Test resistance level ~45000
                high = base_price + 3200 - (i % 5) * 50
                low = base_price + 2800 - (i % 5) * 50
                close = base_price + 3000 - (i % 5) * 50

            volume = 1000000 * (1 + (i % 10) / 10)  # Varying volume

            candles.append([
                i * 86400000,  # timestamp
                base_price,     # open
                high,           # high
                low,            # low
                close,          # close
                volume,         # volume
            ])

        return {"data": candles}

    @pytest.mark.asyncio
    async def test_identify_basic_call(self, mock_ohlcv_data):
        """Test basic identify() call returns correct structure"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify("BTC/USDT", "1d", lookback=100)

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "technical-analysis-skill"
        assert "symbol" in result
        assert result["symbol"] == "BTC/USDT"
        assert "data_type" in result
        assert result["data_type"] == "support_resistance"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_identify_verbose_true(self, mock_ohlcv_data):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify("BTC/USDT", "1d", verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "symbol" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "timeframe" in result["metadata"]
        assert "lookback_periods" in result["metadata"]
        assert "tolerance" in result["metadata"]
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_identify_verbose_false(self, mock_ohlcv_data):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify("BTC/USDT", "1d", verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_identify_data_structure(self, mock_ohlcv_data):
        """Test data structure contains all required fields"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify("BTC/USDT", "1d", lookback=100)
        data = result["data"]

        # Verify all required data fields
        assert "support_levels" in data
        assert "resistance_levels" in data
        assert "current_price" in data
        assert "nearest_support" in data
        assert "nearest_resistance" in data
        assert "support_distance" in data
        assert "resistance_distance" in data

        # Verify data types
        assert isinstance(data["support_levels"], list)
        assert isinstance(data["resistance_levels"], list)
        assert isinstance(data["current_price"], (int, float))

    @pytest.mark.asyncio
    async def test_identify_level_structure(self, mock_ohlcv_data):
        """Test individual level structure"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify("BTC/USDT", "1d", lookback=100)
        data = result["data"]

        # Check support level structure
        if data["support_levels"]:
            level = data["support_levels"][0]
            assert "price" in level
            assert "strength" in level
            assert "touches" in level
            assert "volume_weight" in level
            assert isinstance(level["price"], (int, float))
            assert isinstance(level["strength"], float)
            assert isinstance(level["touches"], int)
            assert isinstance(level["volume_weight"], float)

    @pytest.mark.asyncio
    async def test_identify_insufficient_data_error(self):
        """Test ValueError when insufficient data (<20 candles)"""
        mock_client = AsyncMock()
        # Return only 15 candles
        mock_client.call_tool.return_value = {"data": [[0, 100, 105, 95, 100, 1000]] * 15}

        identifier = SupportResistanceIdentifier(mock_client)

        with pytest.raises(ValueError, match="Insufficient data"):
            await identifier.identify("BTC/USDT", "1d", lookback=100)

    @pytest.mark.asyncio
    async def test_identify_custom_parameters(self, mock_ohlcv_data):
        """Test identify with custom parameters"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify(
            "ETH/USDT",
            timeframe="4h",
            lookback=50,
            tolerance=0.02,
            top_n=3,
        )

        # Verify parameters were used
        assert result["symbol"] == "ETH/USDT"
        assert result["metadata"]["timeframe"] == "4h"
        assert result["metadata"]["lookback_periods"] == 50
        assert result["metadata"]["tolerance"] == 0.02
        assert len(result["data"]["support_levels"]) <= 3
        assert len(result["data"]["resistance_levels"]) <= 3


class TestPivotDetection:
    """Test pivot point detection methods"""

    def test_find_pivot_highs_basic(self):
        """Test basic pivot high detection"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # Create highs with clear pivot at index 10
        highs = [100] * 5 + [105, 110, 115, 120, 125, 130, 125, 120, 115, 110] + [105] * 5

        pivots = identifier._find_pivot_highs(highs, window=5)

        assert 10 in pivots  # Index 10 has value 130, highest in window

    def test_find_pivot_highs_no_pivots(self):
        """Test no pivots found in monotonic sequence"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # Strictly increasing - no local maxima
        highs = list(range(100, 200))

        pivots = identifier._find_pivot_highs(highs, window=5)

        assert len(pivots) == 0

    def test_find_pivot_highs_multiple_pivots(self):
        """Test multiple pivot detection"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # Create multiple peaks
        highs = [100, 105, 110, 105, 100, 95, 100, 105, 110, 105, 100, 95, 100, 105, 110, 105, 100]

        pivots = identifier._find_pivot_highs(highs, window=2)

        # Should detect peaks at indices with local maxima
        assert len(pivots) > 0

    def test_find_pivot_lows_basic(self):
        """Test basic pivot low detection"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # Create lows with clear pivot at index 10
        lows = [100] * 5 + [95, 90, 85, 80, 75, 70, 75, 80, 85, 90] + [95] * 5

        pivots = identifier._find_pivot_lows(lows, window=5)

        assert 10 in pivots  # Index 10 has value 70, lowest in window

    def test_find_pivot_lows_no_pivots(self):
        """Test no pivots found in monotonic sequence"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # Strictly decreasing - no local minima
        lows = list(range(200, 100, -1))

        pivots = identifier._find_pivot_lows(lows, window=5)

        assert len(pivots) == 0

    def test_pivot_detection_edge_of_range(self):
        """Test pivots at edges are not detected (need window space)"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # Peak at start and end
        highs = [130] + [100] * 10 + [130]

        pivots = identifier._find_pivot_highs(highs, window=5)

        # Should not detect peaks too close to edges
        assert 0 not in pivots
        assert len(highs) - 1 not in pivots


class TestPriceClustering:
    """Test price level clustering"""

    def test_cluster_price_levels_basic(self):
        """Test basic price clustering within tolerance"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # Prices within 1% of 42000
        prices = [42000, 42100, 42200, 42300, 42400]

        clusters = identifier._cluster_price_levels(prices, tolerance=0.01)

        # Should form single cluster (all within 1% of mean)
        assert len(clusters) == 1
        cluster_price, touches = clusters[0]
        assert touches == 5

    def test_cluster_price_levels_multiple_clusters(self):
        """Test multiple distinct clusters"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # Two distinct price levels: ~42000 and ~45000
        prices = [42000, 42100, 42200, 45000, 45100, 45200]

        clusters = identifier._cluster_price_levels(prices, tolerance=0.01)

        # Should form two clusters
        assert len(clusters) == 2

    def test_cluster_price_levels_tolerance_effect(self):
        """Test tolerance parameter affects clustering"""
        identifier = SupportResistanceIdentifier(MagicMock())

        prices = [42000, 42500, 43000]

        # Tight tolerance - should create separate clusters
        clusters_tight = identifier._cluster_price_levels(prices, tolerance=0.005)

        # Loose tolerance - should merge into single cluster
        clusters_loose = identifier._cluster_price_levels(prices, tolerance=0.02)

        assert len(clusters_tight) > len(clusters_loose)

    def test_cluster_price_levels_empty_input(self):
        """Test clustering with empty input"""
        identifier = SupportResistanceIdentifier(MagicMock())

        clusters = identifier._cluster_price_levels([], tolerance=0.01)

        assert clusters == []

    def test_cluster_price_levels_single_price(self):
        """Test clustering with single price"""
        identifier = SupportResistanceIdentifier(MagicMock())

        clusters = identifier._cluster_price_levels([42000], tolerance=0.01)

        assert len(clusters) == 1
        assert clusters[0][1] == 1  # Single touch


class TestLevelStrengthCalculation:
    """Test level strength calculation (60% touches + 40% volume)"""

    def test_calculate_level_strength_basic(self):
        """Test basic strength calculation"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # Single cluster with 3 touches
        clusters = [(42000, 3)]
        prices = [42000] * 10
        volumes = [1000000] * 10

        levels = identifier._calculate_level_strength(
            clusters, prices, volumes, is_resistance=True
        )

        assert len(levels) == 1
        level = levels[0]
        assert level["price"] == 42000
        assert level["touches"] == 3
        assert 0.0 <= level["strength"] <= 1.0
        assert 0.0 <= level["volume_weight"] <= 1.0

    def test_calculate_level_strength_formula(self):
        """Test strength formula: 0.6 * touch_score + 0.4 * volume_weight"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # 5 touches = max touch score (1.0)
        clusters = [(42000, 5)]
        # High volume at this level
        prices = [42000] * 10 + [40000] * 90
        volumes = [1000000] * 10 + [100000] * 90  # 10x higher volume at level

        levels = identifier._calculate_level_strength(
            clusters, prices, volumes, is_resistance=False
        )

        level = levels[0]
        # Touch score = min(5/5, 1.0) = 1.0
        # Volume weight should be high
        # Strength = 0.6 * 1.0 + 0.4 * volume_weight
        assert level["strength"] > 0.6  # At minimum 0.6 from touches

    def test_calculate_level_strength_low_touches(self):
        """Test strength with low touch count"""
        identifier = SupportResistanceIdentifier(MagicMock())

        # 2 touches (touch_score = 2/5 = 0.4)
        clusters = [(42000, 2)]
        prices = [42000] * 2
        volumes = [1000000] * 2

        levels = identifier._calculate_level_strength(
            clusters, prices, volumes, is_resistance=True
        )

        level = levels[0]
        assert level["touches"] == 2
        # Strength should be lower with fewer touches
        assert level["strength"] < 0.8


class TestVolumeWeighting:
    """Test volume weighting calculation"""

    def test_calculate_volume_at_level_high_volume(self):
        """Test high volume concentration at level"""
        identifier = SupportResistanceIdentifier(MagicMock())

        target_price = 42000
        # 10 prices at target, 90 elsewhere
        prices = [42000] * 10 + [40000] * 90
        # 10x volume at target level
        volumes = [10000000] * 10 + [1000000] * 90

        volume_weight = identifier._calculate_volume_at_level(
            target_price, prices, volumes, tolerance=0.01
        )

        # Should have high volume weight
        assert volume_weight > 0.5

    def test_calculate_volume_at_level_low_volume(self):
        """Test low volume at level"""
        identifier = SupportResistanceIdentifier(MagicMock())

        target_price = 42000
        # Only 1 price at target
        prices = [42000] * 1 + [40000] * 99
        volumes = [1000000] * 100

        volume_weight = identifier._calculate_volume_at_level(
            target_price, prices, volumes, tolerance=0.01
        )

        # Should have low volume weight
        assert volume_weight < 0.3

    def test_calculate_volume_at_level_zero_total_volume(self):
        """Test zero total volume edge case"""
        identifier = SupportResistanceIdentifier(MagicMock())

        volume_weight = identifier._calculate_volume_at_level(
            42000, [42000] * 10, [0] * 10, tolerance=0.01
        )

        assert volume_weight == 0.0

    def test_calculate_volume_at_level_normalization(self):
        """Test volume weight capped at 1.0 (10% of total = max)"""
        identifier = SupportResistanceIdentifier(MagicMock())

        target_price = 42000
        # All volume at target level
        prices = [42000] * 100
        volumes = [1000000] * 100

        volume_weight = identifier._calculate_volume_at_level(
            target_price, prices, volumes, tolerance=0.01
        )

        # Should be capped at 1.0
        assert volume_weight <= 1.0


class TestNearestLevelFinding:
    """Test finding nearest support/resistance levels"""

    def test_find_nearest_level_support(self):
        """Test finding nearest support (below current price)"""
        identifier = SupportResistanceIdentifier(MagicMock())

        levels = [
            {"price": 41000, "strength": 0.8},
            {"price": 40000, "strength": 0.7},
            {"price": 39000, "strength": 0.6},
        ]
        current_price = 42000

        nearest = identifier._find_nearest_level(levels, current_price, below=True)

        assert nearest == 41000  # Highest level below current

    def test_find_nearest_level_resistance(self):
        """Test finding nearest resistance (above current price)"""
        identifier = SupportResistanceIdentifier(MagicMock())

        levels = [
            {"price": 45000, "strength": 0.8},
            {"price": 46000, "strength": 0.7},
            {"price": 47000, "strength": 0.6},
        ]
        current_price = 42000

        nearest = identifier._find_nearest_level(levels, current_price, below=False)

        assert nearest == 45000  # Lowest level above current

    def test_find_nearest_level_no_levels_below(self):
        """Test no support levels below current price"""
        identifier = SupportResistanceIdentifier(MagicMock())

        levels = [
            {"price": 45000, "strength": 0.8},
            {"price": 46000, "strength": 0.7},
        ]
        current_price = 42000

        nearest = identifier._find_nearest_level(levels, current_price, below=True)

        assert nearest is None

    def test_find_nearest_level_no_levels_above(self):
        """Test no resistance levels above current price"""
        identifier = SupportResistanceIdentifier(MagicMock())

        levels = [
            {"price": 40000, "strength": 0.8},
            {"price": 39000, "strength": 0.7},
        ]
        current_price = 42000

        nearest = identifier._find_nearest_level(levels, current_price, below=False)

        assert nearest is None

    def test_find_nearest_level_empty_list(self):
        """Test with empty levels list"""
        identifier = SupportResistanceIdentifier(MagicMock())

        nearest = identifier._find_nearest_level([], 42000, below=True)

        assert nearest is None


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    @pytest.mark.asyncio
    async def test_confidence_base_value(self, mock_ohlcv_data):
        """Test base confidence is 0.70"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify("BTC/USDT", "1d", top_n=5)

        # Base confidence is 0.70
        assert result["metadata"]["confidence"] >= 0.70

    @pytest.mark.asyncio
    async def test_confidence_capped_at_095(self, mock_ohlcv_data):
        """Test confidence capped at 0.95"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify("BTC/USDT", "1d", top_n=5)

        # Confidence should never exceed 0.95
        assert result["metadata"]["confidence"] <= 0.95


class TestDistanceCalculation:
    """Test support/resistance distance calculation"""

    @pytest.mark.asyncio
    async def test_support_distance_calculation(self, mock_ohlcv_data):
        """Test support distance is negative (below current)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify("BTC/USDT", "1d")
        data = result["data"]

        if data["nearest_support"] is not None:
            # Support distance should be negative (support below current)
            assert data["support_distance"] < 0
            # Verify calculation
            expected_distance = data["nearest_support"] - data["current_price"]
            assert abs(data["support_distance"] - expected_distance) < 0.01

    @pytest.mark.asyncio
    async def test_resistance_distance_calculation(self, mock_ohlcv_data):
        """Test resistance distance is positive (above current)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        identifier = SupportResistanceIdentifier(mock_client)

        result = await identifier.identify("BTC/USDT", "1d")
        data = result["data"]

        if data["nearest_resistance"] is not None:
            # Resistance distance should be positive (resistance above current)
            assert data["resistance_distance"] > 0
            # Verify calculation
            expected_distance = data["nearest_resistance"] - data["current_price"]
            assert abs(data["resistance_distance"] - expected_distance) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
