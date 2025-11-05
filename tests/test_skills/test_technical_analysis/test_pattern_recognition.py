"""
Unit tests for PatternRecognizer Skill

Tests chart pattern recognition functionality including:
- Pattern template matching via correlation
- Head & shoulders, double top/bottom, triangles, flags
- Volume confirmation
- Target price and risk/reward calculation
- Overall bias determination
- Verbose parameter functionality
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.technical_analysis.pattern_recognition import PatternRecognizer


class TestPatternRecognizerInit:
    """Test PatternRecognizer initialization"""

    def test_initialization(self):
        """Test recognizer initializes with MCP client"""
        mock_client = MagicMock()
        recognizer = PatternRecognizer(mock_client)

        assert recognizer.mcp == mock_client
        assert recognizer is not None

    def test_pattern_templates_loaded(self):
        """Test pattern templates are loaded correctly"""
        mock_client = MagicMock()
        recognizer = PatternRecognizer(mock_client)

        # Verify all expected patterns exist
        assert "head_shoulders" in recognizer.PATTERNS
        assert "inverse_head_shoulders" in recognizer.PATTERNS
        assert "double_top" in recognizer.PATTERNS
        assert "double_bottom" in recognizer.PATTERNS
        assert "ascending_triangle" in recognizer.PATTERNS
        assert "descending_triangle" in recognizer.PATTERNS
        assert "bull_flag" in recognizer.PATTERNS
        assert "bear_flag" in recognizer.PATTERNS

        # Verify pattern structure
        for pattern_name, pattern_config in recognizer.PATTERNS.items():
            assert "template" in pattern_config
            assert "min_correlation" in pattern_config
            assert "interpretation" in pattern_config
            assert "confidence_threshold" in pattern_config


class TestRecognizeMethod:
    """Test main recognize() method"""

    @pytest.fixture
    def mock_ohlcv_data(self):
        """Mock OHLCV data with 100 candles"""
        # Generate realistic price data with patterns
        candles = []
        base_price = 45000.0
        for i in range(100):
            # Create variation that could form patterns
            variation = (i % 10) * 200 - 1000
            price = base_price + variation
            candles.append(
                [
                    1640000000000 + i * 3600000,  # timestamp
                    price,  # open
                    price + 100,  # high
                    price - 100,  # low
                    price + 50,  # close
                    1000.0 + i * 10,  # volume
                ]
            )
        return {"data": candles}

    @pytest.mark.asyncio
    async def test_recognize_basic_call(self, mock_ohlcv_data):
        """Test basic recognize() call returns correct structure"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        recognizer = PatternRecognizer(mock_client)

        result = await recognizer.recognize("BTC/USDT", timeframe="4h")

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "technical-analysis-skill"
        assert "symbol" in result
        assert result["symbol"] == "BTC/USDT"
        assert "data_type" in result
        assert result["data_type"] == "chart_patterns"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_recognize_verbose_true(self, mock_ohlcv_data):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        recognizer = PatternRecognizer(mock_client)

        result = await recognizer.recognize("BTC/USDT", verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "symbol" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "timeframe" in result["metadata"]
        assert "lookback_periods" in result["metadata"]
        assert "min_confidence" in result["metadata"]
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_recognize_verbose_false(self, mock_ohlcv_data):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        recognizer = PatternRecognizer(mock_client)

        result = await recognizer.recognize("BTC/USDT", verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_recognize_data_structure(self, mock_ohlcv_data):
        """Test data structure contains all required fields"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        recognizer = PatternRecognizer(mock_client)

        result = await recognizer.recognize("BTC/USDT")
        data = result["data"]

        # Verify all required data fields
        assert "patterns_found" in data
        assert "strongest_pattern" in data
        assert "overall_bias" in data
        assert "pattern_count" in data

        # Verify data types
        assert isinstance(data["patterns_found"], list)
        assert isinstance(data["overall_bias"], str)
        assert isinstance(data["pattern_count"], int)

    @pytest.mark.asyncio
    async def test_recognize_insufficient_data(self):
        """Test error handling for insufficient data"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"data": [[1, 100, 100, 100, 100, 1000]]}

        recognizer = PatternRecognizer(mock_client)

        with pytest.raises(ValueError, match="Insufficient data"):
            await recognizer.recognize("BTC/USDT")

    @pytest.mark.asyncio
    async def test_recognize_custom_parameters(self, mock_ohlcv_data):
        """Test recognize with custom parameters"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = mock_ohlcv_data

        recognizer = PatternRecognizer(mock_client)

        result = await recognizer.recognize(
            "ETH/USDT", timeframe="1h", lookback=50, min_confidence=0.80
        )

        # Verify parameters applied
        assert result["symbol"] == "ETH/USDT"
        assert result["metadata"]["timeframe"] == "1h"
        assert result["metadata"]["lookback_periods"] == 50
        assert result["metadata"]["min_confidence"] == 0.80

        # Verify MCP call received correct parameters
        mock_client.call_tool.assert_called_once()
        call_args = mock_client.call_tool.call_args
        assert call_args[0][1]["symbol"] == "ETH/USDT"
        assert call_args[0][1]["timeframe"] == "1h"
        assert call_args[0][1]["limit"] == 50


class TestPriceNormalization:
    """Test price normalization"""

    def test_normalize_prices_basic(self):
        """Test basic price normalization"""
        recognizer = PatternRecognizer(MagicMock())

        prices = [100.0, 150.0, 200.0, 250.0, 300.0]
        normalized = recognizer._normalize_prices(prices)

        # Should be normalized to 0-1 range
        assert min(normalized) == 0.0
        assert max(normalized) == 1.0
        assert len(normalized) == len(prices)

    def test_normalize_prices_zero_range(self):
        """Test normalization with zero price range"""
        recognizer = PatternRecognizer(MagicMock())

        prices = [100.0, 100.0, 100.0, 100.0]
        normalized = recognizer._normalize_prices(prices)

        # All should be 0.5 when range is zero
        assert all(p == 0.5 for p in normalized)

    def test_normalize_prices_preserves_order(self):
        """Test normalization preserves relative ordering"""
        recognizer = PatternRecognizer(MagicMock())

        prices = [100.0, 200.0, 150.0, 300.0]
        normalized = recognizer._normalize_prices(prices)

        # Verify ordering preserved
        assert normalized[1] > normalized[0]  # 200 > 100
        assert normalized[2] < normalized[1]  # 150 < 200
        assert normalized[3] > normalized[2]  # 300 > 150


class TestPatternMatching:
    """Test pattern matching logic"""

    def test_find_pattern_matches_exact_match(self):
        """Test finding exact pattern match"""
        recognizer = PatternRecognizer(MagicMock())

        # Create data that exactly matches template
        template = [0.0, 0.5, 1.0, 0.5, 0.0]
        normalized_prices = [0.0, 0.5, 1.0, 0.5, 0.0, 0.2, 0.3, 0.4]

        matches = recognizer._find_pattern_matches(normalized_prices, template, 0.90, 0.70)

        # Should find at least one match at start
        assert len(matches) > 0
        assert matches[0]["start_index"] == 0
        assert matches[0]["end_index"] == 4

    def test_find_pattern_matches_no_matches(self):
        """Test when no patterns match"""
        recognizer = PatternRecognizer(MagicMock())

        template = [0.0, 0.5, 1.0, 0.5, 0.0]
        normalized_prices = [0.0, 0.0, 0.0, 0.0, 0.0]

        matches = recognizer._find_pattern_matches(normalized_prices, template, 0.95, 0.70)

        # Should find no matches with very different data
        assert len(matches) == 0

    def test_find_pattern_matches_multiple_windows(self):
        """Test sliding window finds multiple potential matches"""
        recognizer = PatternRecognizer(MagicMock())

        template = [0.0, 1.0, 0.0]
        # Create data with pattern repeated
        normalized_prices = [0.0, 1.0, 0.0, 0.5, 0.0, 1.0, 0.0]

        matches = recognizer._find_pattern_matches(normalized_prices, template, 0.70, 0.65)

        # Should find multiple matches
        assert len(matches) >= 2


class TestCorrelationCalculation:
    """Test correlation calculation"""

    def test_calculate_correlation_perfect_match(self):
        """Test correlation with perfect match"""
        recognizer = PatternRecognizer(MagicMock())

        data = [0.0, 0.5, 1.0, 0.5, 0.0]
        template = [0.0, 0.5, 1.0, 0.5, 0.0]

        correlation = recognizer._calculate_correlation(data, template)

        # Perfect match should give correlation of 1.0
        assert correlation >= 0.99

    def test_calculate_correlation_inverse_pattern(self):
        """Test correlation with inverse pattern"""
        recognizer = PatternRecognizer(MagicMock())

        data = [1.0, 0.5, 0.0, 0.5, 1.0]
        template = [0.0, 0.5, 1.0, 0.5, 0.0]

        correlation = recognizer._calculate_correlation(data, template)

        # Inverse should also give high correlation (absolute value)
        assert correlation >= 0.99

    def test_calculate_correlation_no_match(self):
        """Test correlation with completely different patterns"""
        recognizer = PatternRecognizer(MagicMock())

        data = [0.0, 0.0, 0.0, 0.0, 0.0]
        template = [0.0, 0.5, 1.0, 0.5, 0.0]

        correlation = recognizer._calculate_correlation(data, template)

        # Flat line vs pattern should give low correlation
        assert correlation < 0.5

    def test_calculate_correlation_mismatched_lengths(self):
        """Test correlation with mismatched lengths"""
        recognizer = PatternRecognizer(MagicMock())

        data = [0.0, 0.5, 1.0]
        template = [0.0, 0.5, 1.0, 0.5, 0.0]

        correlation = recognizer._calculate_correlation(data, template)

        # Mismatched lengths should return 0
        assert correlation == 0.0

    def test_calculate_correlation_zero_denominator(self):
        """Test correlation with zero denominator (constant data)"""
        recognizer = PatternRecognizer(MagicMock())

        data = [0.5, 0.5, 0.5, 0.5, 0.5]
        template = [0.0, 0.5, 1.0, 0.5, 0.0]

        correlation = recognizer._calculate_correlation(data, template)

        # Zero denominator should return 0
        assert correlation == 0.0


class TestVolumeValidation:
    """Test volume confirmation"""

    def test_validate_volume_confirmed(self):
        """Test volume confirmation when pattern volume is high"""
        recognizer = PatternRecognizer(MagicMock())

        # Pattern with higher volume than baseline
        volumes = [1000.0] * 20 + [1500.0] * 10

        confirmed = recognizer._validate_volume(volumes, start_index=20, end_index=29)

        # Should be confirmed (pattern volume >= baseline * 0.8)
        assert confirmed is True

    def test_validate_volume_not_confirmed(self):
        """Test volume not confirmed when pattern volume is low"""
        recognizer = PatternRecognizer(MagicMock())

        # Pattern with lower volume than baseline
        volumes = [2000.0] * 20 + [500.0] * 10

        confirmed = recognizer._validate_volume(volumes, start_index=20, end_index=29)

        # Should not be confirmed (pattern volume < baseline * 0.8)
        assert confirmed is False

    def test_validate_volume_boundary_indices(self):
        """Test volume validation with boundary indices"""
        recognizer = PatternRecognizer(MagicMock())

        volumes = [1000.0] * 30

        # Test invalid start index
        confirmed = recognizer._validate_volume(volumes, start_index=-1, end_index=5)
        assert confirmed is False

        # Test invalid end index
        confirmed = recognizer._validate_volume(volumes, start_index=20, end_index=100)
        assert confirmed is False

    def test_validate_volume_zero_baseline(self):
        """Test volume validation with zero baseline volume"""
        recognizer = PatternRecognizer(MagicMock())

        # Start at index 0 (no baseline data)
        volumes = [1000.0] * 30

        confirmed = recognizer._validate_volume(volumes, start_index=0, end_index=9)

        # Should assume true when can't validate
        assert confirmed is True


class TestTargetCalculation:
    """Test target price and risk/reward calculation"""

    def test_calculate_target_bullish_pattern(self):
        """Test target calculation for bullish pattern"""
        recognizer = PatternRecognizer(MagicMock())

        prices = [44000.0] * 50 + [44000.0, 44500.0, 45000.0, 44500.0, 45000.0]
        start_index = 50
        end_index = 54

        target, risk_reward = recognizer._calculate_target(
            prices, start_index, end_index, "Bullish continuation"
        )

        # Target should be above current price
        current_price = prices[-1]
        assert target > current_price

        # Risk/reward should be positive
        assert risk_reward > 0

    def test_calculate_target_bearish_pattern(self):
        """Test target calculation for bearish pattern"""
        recognizer = PatternRecognizer(MagicMock())

        prices = [45000.0] * 50 + [45000.0, 44500.0, 44000.0, 44500.0, 44000.0]
        start_index = 50
        end_index = 54

        target, risk_reward = recognizer._calculate_target(
            prices, start_index, end_index, "Bearish reversal"
        )

        # Target should be below current price
        current_price = prices[-1]
        assert target < current_price

        # Risk/reward should be positive
        assert risk_reward > 0

    def test_calculate_target_zero_risk(self):
        """Test target calculation with zero risk (edge case)"""
        recognizer = PatternRecognizer(MagicMock())

        # All prices the same (zero risk)
        prices = [45000.0] * 60
        start_index = 50
        end_index = 54

        target, risk_reward = recognizer._calculate_target(
            prices, start_index, end_index, "Bullish continuation"
        )

        # Risk/reward should default to 1.0 when risk is zero
        assert risk_reward == 1.0


class TestBiasDetermination:
    """Test overall bias determination"""

    def test_determine_bias_bullish(self):
        """Test bullish bias determination"""
        recognizer = PatternRecognizer(MagicMock())

        patterns = [
            {"interpretation": "Bullish continuation", "confidence": 0.85},
            {"interpretation": "Bullish reversal", "confidence": 0.75},
            {"interpretation": "Bearish continuation", "confidence": 0.60},
        ]

        bias = recognizer._determine_bias(patterns)

        # Should be bullish (weighted by confidence)
        assert bias == "bullish"

    def test_determine_bias_bearish(self):
        """Test bearish bias determination"""
        recognizer = PatternRecognizer(MagicMock())

        patterns = [
            {"interpretation": "Bearish continuation", "confidence": 0.85},
            {"interpretation": "Bearish reversal", "confidence": 0.75},
            {"interpretation": "Bullish continuation", "confidence": 0.60},
        ]

        bias = recognizer._determine_bias(patterns)

        # Should be bearish (weighted by confidence)
        assert bias == "bearish"

    def test_determine_bias_neutral(self):
        """Test neutral bias determination"""
        recognizer = PatternRecognizer(MagicMock())

        patterns = [
            {"interpretation": "Bullish continuation", "confidence": 0.75},
            {"interpretation": "Bearish continuation", "confidence": 0.75},
        ]

        bias = recognizer._determine_bias(patterns)

        # Should be neutral (balanced)
        assert bias == "neutral"

    def test_determine_bias_no_patterns(self):
        """Test bias with no patterns found"""
        recognizer = PatternRecognizer(MagicMock())

        patterns = []

        bias = recognizer._determine_bias(patterns)

        # Should be neutral when no patterns
        assert bias == "neutral"


class TestPatternStructure:
    """Test pattern output structure"""

    @pytest.mark.asyncio
    async def test_pattern_structure_complete(self):
        """Test pattern dict has all required fields"""
        mock_client = AsyncMock()

        # Create OHLCV data that will match bull_flag pattern
        candles = []
        base_price = 45000.0
        for i in range(100):
            price = base_price + (i % 6) * 200
            candles.append([1, price, price + 100, price - 100, price, 1000 + i * 10])

        mock_client.call_tool.return_value = {"data": candles}

        recognizer = PatternRecognizer(mock_client)
        result = await recognizer.recognize("BTC/USDT", min_confidence=0.50)

        # If patterns found, verify structure
        if result["data"]["patterns_found"]:
            pattern = result["data"]["patterns_found"][0]

            assert "name" in pattern
            assert "confidence" in pattern
            assert "interpretation" in pattern
            assert "start_index" in pattern
            assert "end_index" in pattern
            assert "volume_confirmed" in pattern
            assert "target_price" in pattern
            assert "risk_reward" in pattern

            # Verify data types
            assert isinstance(pattern["name"], str)
            assert isinstance(pattern["confidence"], float)
            assert isinstance(pattern["interpretation"], str)
            assert isinstance(pattern["start_index"], int)
            assert isinstance(pattern["end_index"], int)
            assert isinstance(pattern["volume_confirmed"], bool)
            assert isinstance(pattern["target_price"], float)
            assert isinstance(pattern["risk_reward"], float)


class TestConfidenceFiltering:
    """Test confidence-based filtering"""

    @pytest.mark.asyncio
    async def test_confidence_filtering_applied(self):
        """Test patterns below min_confidence are filtered out"""
        mock_client = AsyncMock()

        # Create varied data
        candles = []
        for i in range(100):
            price = 45000.0 + (i % 15) * 150
            candles.append([1, price, price + 100, price - 100, price, 1000 + i * 5])

        mock_client.call_tool.return_value = {"data": candles}

        recognizer = PatternRecognizer(mock_client)

        # Set high confidence threshold
        result = await recognizer.recognize("BTC/USDT", min_confidence=0.95)

        # All found patterns should meet threshold
        for pattern in result["data"]["patterns_found"]:
            assert pattern["confidence"] >= 0.95


class TestConfidenceCalculation:
    """Test overall confidence calculation"""

    @pytest.mark.asyncio
    async def test_confidence_from_strongest_pattern(self):
        """Test confidence is max of pattern confidences"""
        mock_client = AsyncMock()

        # Create data likely to match patterns
        candles = []
        for i in range(100):
            price = 45000.0 + (i % 10) * 200
            candles.append([1, price, price + 100, price - 100, price, 1000 + i * 10])

        mock_client.call_tool.return_value = {"data": candles}

        recognizer = PatternRecognizer(mock_client)
        result = await recognizer.recognize("BTC/USDT", min_confidence=0.50)

        # Confidence should match strongest pattern (if any found)
        if result["data"]["patterns_found"]:
            expected_confidence = max(p["confidence"] for p in result["data"]["patterns_found"])
            assert result["metadata"]["confidence"] == round(expected_confidence, 2)

    @pytest.mark.asyncio
    async def test_confidence_default_when_no_patterns(self):
        """Test confidence defaults to 0.50 when no patterns found"""
        mock_client = AsyncMock()

        # Create flat data unlikely to match any patterns
        candles = []
        for i in range(100):
            price = 45000.0
            candles.append([1, price, price, price, price, 1000])

        mock_client.call_tool.return_value = {"data": candles}

        recognizer = PatternRecognizer(mock_client)
        result = await recognizer.recognize("BTC/USDT", min_confidence=0.95)

        # No patterns should be found
        assert result["data"]["pattern_count"] == 0

        # Confidence should default to 0.50
        assert result["metadata"]["confidence"] == 0.50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
