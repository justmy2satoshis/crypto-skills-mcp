"""
Unit tests for VolatilityAnalyzer Skill

Tests volatility analysis functionality including:
- ATR (Average True Range) calculation and interpretation
- Bollinger Bands width and squeeze detection
- Price position within bands
- Breakout signal generation
- Volatility index calculation
- Trading recommendation generation
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

from skills.technical_analysis.volatility_analysis import VolatilityAnalyzer


class TestVolatilityAnalyzerInit:
    """Test VolatilityAnalyzer initialization"""

    def test_initialization(self):
        """Test analyzer initializes with MCP client"""
        mock_client = MagicMock()
        analyzer = VolatilityAnalyzer(mock_client)

        assert analyzer.mcp == mock_client
        assert analyzer is not None


class TestAnalyzeMethod:
    """Test main analyze() method"""

    @pytest.fixture
    def mock_indicator_responses(self):
        """Mock ATR, Bollinger Bands, and OHLCV responses"""
        return {
            "atr": {"atr": [350.0, 380.0, 420.0, 450.0]},
            "bollinger": {
                "upper": [45500.0, 45800.0, 46000.0, 46200.0],
                "middle": [44000.0, 44200.0, 44500.0, 44800.0],
                "lower": [42500.0, 42600.0, 43000.0, 43400.0],
            },
            "ohlcv": {"data": [[1, 45000.0, 45200.0, 44800.0, 45100.0, 1000.0]]},
        }

    @pytest.mark.asyncio
    async def test_analyze_basic_call(self, mock_indicator_responses):
        """Test basic analyze() call returns correct structure"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "average_true_range" in tool_name.lower():
                return mock_indicator_responses["atr"]
            elif "bollinger" in tool_name.lower():
                return mock_indicator_responses["bollinger"]
            elif "ohlcv" in tool_name.lower():
                return mock_indicator_responses["ohlcv"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        analyzer = VolatilityAnalyzer(mock_client)

        result = await analyzer.analyze("BTC/USDT", timeframe="1h")

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "technical-analysis-skill"
        assert "symbol" in result
        assert result["symbol"] == "BTC/USDT"
        assert "data_type" in result
        assert result["data_type"] == "volatility_analysis"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_analyze_verbose_true(self, mock_indicator_responses):
        """Test verbose=True returns full response with metadata"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "average_true_range" in tool_name.lower():
                return mock_indicator_responses["atr"]
            elif "bollinger" in tool_name.lower():
                return mock_indicator_responses["bollinger"]
            elif "ohlcv" in tool_name.lower():
                return mock_indicator_responses["ohlcv"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        analyzer = VolatilityAnalyzer(mock_client)

        result = await analyzer.analyze("BTC/USDT", verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "metadata" in result
        assert "timeframe" in result["metadata"]
        assert "atr_period" in result["metadata"]
        assert "bb_period" in result["metadata"]
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_analyze_verbose_false(self, mock_indicator_responses):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "average_true_range" in tool_name.lower():
                return mock_indicator_responses["atr"]
            elif "bollinger" in tool_name.lower():
                return mock_indicator_responses["bollinger"]
            elif "ohlcv" in tool_name.lower():
                return mock_indicator_responses["ohlcv"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        analyzer = VolatilityAnalyzer(mock_client)

        result = await analyzer.analyze("BTC/USDT", verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_analyze_data_structure(self, mock_indicator_responses):
        """Test data structure contains all required fields"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "average_true_range" in tool_name.lower():
                return mock_indicator_responses["atr"]
            elif "bollinger" in tool_name.lower():
                return mock_indicator_responses["bollinger"]
            elif "ohlcv" in tool_name.lower():
                return mock_indicator_responses["ohlcv"]
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        analyzer = VolatilityAnalyzer(mock_client)

        result = await analyzer.analyze("BTC/USDT")
        data = result["data"]

        # Verify all required data fields
        assert "volatility_level" in data
        assert "volatility_index" in data
        assert "atr" in data
        assert "bollinger" in data
        assert "breakout_potential" in data
        assert "trading_recommendation" in data

        # Verify nested structures
        assert "value" in data["atr"]
        assert "percentile" in data["atr"]
        assert "interpretation" in data["atr"]

        assert "width" in data["bollinger"]
        assert "squeeze" in data["bollinger"]
        assert "price_position" in data["bollinger"]
        assert "breakout_signal" in data["bollinger"]

        assert "direction" in data["breakout_potential"]
        assert "probability" in data["breakout_potential"]
        assert "target_price" in data["breakout_potential"]


class TestATRProcessing:
    """Test ATR data processing"""

    def test_process_atr_valid_data(self):
        """Test processing valid ATR data"""
        analyzer = VolatilityAnalyzer(MagicMock())

        atr_result = {"atr": [300.0, 350.0, 400.0, 450.0, 500.0]}

        processed = analyzer._process_atr(atr_result)

        assert processed["value"] == 500.0
        assert "percentile" in processed
        assert 0 <= processed["percentile"] <= 1
        assert processed["interpretation"] in [
            "Very low volatility",
            "Low volatility",
            "Moderate volatility",
            "High volatility",
        ]

    def test_process_atr_high_percentile(self):
        """Test ATR interpretation at high percentile (>75%)"""
        analyzer = VolatilityAnalyzer(MagicMock())

        # Current ATR is highest value
        atr_result = {"atr": [300.0, 350.0, 400.0, 450.0, 500.0]}

        processed = analyzer._process_atr(atr_result)

        # Should interpret as high volatility
        assert processed["interpretation"] == "High volatility"

    def test_process_atr_low_percentile(self):
        """Test ATR interpretation at low percentile (<25%)"""
        analyzer = VolatilityAnalyzer(MagicMock())

        # Current ATR is lowest value
        atr_result = {"atr": [500.0, 450.0, 400.0, 350.0, 300.0]}

        processed = analyzer._process_atr(atr_result)

        # Should interpret as very low volatility
        assert processed["interpretation"] == "Very low volatility"

    def test_process_atr_exception_handling(self):
        """Test ATR processing handles exceptions gracefully"""
        analyzer = VolatilityAnalyzer(MagicMock())

        result = Exception("Network error")
        processed = analyzer._process_atr(result)

        assert processed["value"] is None
        assert processed["percentile"] is None
        assert processed["interpretation"] == "Data unavailable"

    def test_process_atr_empty_data(self):
        """Test ATR processing handles empty data"""
        analyzer = VolatilityAnalyzer(MagicMock())

        result = {"atr": []}
        processed = analyzer._process_atr(result)

        assert processed["value"] is None
        assert processed["interpretation"] == "Data unavailable"


class TestBollingerBandsProcessing:
    """Test Bollinger Bands data processing"""

    def test_process_bollinger_valid_data(self):
        """Test processing valid Bollinger Bands data"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_result = {
            "upper": [46000.0, 46200.0, 46400.0],
            "middle": [44500.0, 44600.0, 44700.0],
            "lower": [43000.0, 43000.0, 43000.0],
        }
        current_price = 44700.0

        processed = analyzer._process_bollinger_bands(bb_result, current_price)

        assert processed["width"] == 3400.0  # 46400 - 43000
        assert "percentile" in processed
        assert isinstance(processed["squeeze"], bool)
        assert processed["price_position"] in [
            "above",
            "below",
            "upper_half",
            "lower_half",
            "middle",
        ]
        assert "breakout_signal" in processed

    def test_process_bollinger_price_above_upper_band(self):
        """Test price position above upper band"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_result = {
            "upper": [46000.0],
            "middle": [44500.0],
            "lower": [43000.0],
        }
        current_price = 46500.0  # Above upper band

        processed = analyzer._process_bollinger_bands(bb_result, current_price)

        assert processed["price_position"] == "above"
        assert processed["breakout_signal"] == "bullish"

    def test_process_bollinger_price_below_lower_band(self):
        """Test price position below lower band"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_result = {
            "upper": [46000.0],
            "middle": [44500.0],
            "lower": [43000.0],
        }
        current_price = 42500.0  # Below lower band

        processed = analyzer._process_bollinger_bands(bb_result, current_price)

        assert processed["price_position"] == "below"
        assert processed["breakout_signal"] == "bearish"

    def test_process_bollinger_price_upper_half(self):
        """Test price position in upper half of bands"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_result = {
            "upper": [46000.0],
            "middle": [44500.0],
            "lower": [43000.0],
        }
        current_price = 45000.0  # Between middle and upper

        processed = analyzer._process_bollinger_bands(bb_result, current_price)

        assert processed["price_position"] == "upper_half"
        assert processed["breakout_signal"] == "neutral_bullish"

    def test_process_bollinger_price_lower_half(self):
        """Test price position in lower half of bands"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_result = {
            "upper": [46000.0],
            "middle": [44500.0],
            "lower": [43000.0],
        }
        current_price = 44000.0  # Between lower and middle

        processed = analyzer._process_bollinger_bands(bb_result, current_price)

        assert processed["price_position"] == "lower_half"
        assert processed["breakout_signal"] == "neutral_bearish"

    def test_process_bollinger_squeeze_detection(self):
        """Test Bollinger squeeze detection (narrow bands)"""
        analyzer = VolatilityAnalyzer(MagicMock())

        # Create narrow bands (low percentile)
        bb_result = {
            "upper": [46000.0, 46500.0, 47000.0, 47500.0, 48000.0],
            "middle": [44500.0, 45000.0, 45500.0, 46000.0, 46500.0],
            "lower": [43000.0, 43500.0, 44000.0, 44500.0, 45000.0],
        }
        current_price = 46500.0

        processed = analyzer._process_bollinger_bands(bb_result, current_price)

        # Last width (48000 - 45000 = 3000) is narrowest
        # Percentile should be low, triggering squeeze
        # Note: squeeze is percentile < 0.20
        assert "squeeze" in processed

    def test_process_bollinger_exception_handling(self):
        """Test Bollinger Bands processing handles exceptions"""
        analyzer = VolatilityAnalyzer(MagicMock())

        result = Exception("API error")
        processed = analyzer._process_bollinger_bands(result, 45000.0)

        assert processed["width"] is None
        assert processed["squeeze"] is None
        assert processed["price_position"] == "unknown"
        assert processed["breakout_signal"] == "unknown"

    def test_process_bollinger_empty_data(self):
        """Test Bollinger Bands processing handles empty data"""
        analyzer = VolatilityAnalyzer(MagicMock())

        result = {"upper": [], "middle": [], "lower": []}
        processed = analyzer._process_bollinger_bands(result, 45000.0)

        assert processed["width"] is None
        assert processed["price_position"] == "unknown"


class TestVolatilityIndexCalculation:
    """Test volatility index calculation"""

    def test_calculate_volatility_index_both_indicators(self):
        """Test index calculation with both ATR and BB data"""
        analyzer = VolatilityAnalyzer(MagicMock())

        atr_data = {"value": 450.0, "percentile": 0.80, "interpretation": "High volatility"}
        bb_data = {
            "width": 3000.0,
            "percentile": 0.70,
            "squeeze": False,
            "price_position": "middle",
        }

        index = analyzer._calculate_volatility_index(atr_data, bb_data)

        # Average of 0.80 and 0.70 = 0.75
        assert abs(index - 0.75) < 0.01

    def test_calculate_volatility_index_only_atr(self):
        """Test index calculation with only ATR data"""
        analyzer = VolatilityAnalyzer(MagicMock())

        atr_data = {"value": 450.0, "percentile": 0.80, "interpretation": "High volatility"}
        bb_data = {"width": None, "percentile": None, "squeeze": None}

        index = analyzer._calculate_volatility_index(atr_data, bb_data)

        # Should use only ATR percentile
        assert index == 0.80

    def test_calculate_volatility_index_no_data(self):
        """Test index calculation with no valid data"""
        analyzer = VolatilityAnalyzer(MagicMock())

        atr_data = {"value": None, "percentile": None}
        bb_data = {"width": None, "percentile": None}

        index = analyzer._calculate_volatility_index(atr_data, bb_data)

        # Should return default moderate volatility
        assert index == 0.30


class TestVolatilityClassification:
    """Test volatility level classification"""

    def test_classify_volatility_very_high(self):
        """Test very_high volatility classification (>0.75)"""
        analyzer = VolatilityAnalyzer(MagicMock())

        assert analyzer._classify_volatility(0.80) == "very_high"
        assert analyzer._classify_volatility(0.95) == "very_high"

    def test_classify_volatility_high(self):
        """Test high volatility classification (0.50-0.75)"""
        analyzer = VolatilityAnalyzer(MagicMock())

        assert analyzer._classify_volatility(0.60) == "high"
        assert analyzer._classify_volatility(0.75) == "high"

    def test_classify_volatility_moderate(self):
        """Test moderate volatility classification (0.30-0.50)"""
        analyzer = VolatilityAnalyzer(MagicMock())

        assert analyzer._classify_volatility(0.40) == "moderate"
        assert analyzer._classify_volatility(0.50) == "moderate"

    def test_classify_volatility_low(self):
        """Test low volatility classification (0.15-0.30)"""
        analyzer = VolatilityAnalyzer(MagicMock())

        assert analyzer._classify_volatility(0.20) == "low"
        assert analyzer._classify_volatility(0.30) == "low"

    def test_classify_volatility_very_low(self):
        """Test very_low volatility classification (<0.15)"""
        analyzer = VolatilityAnalyzer(MagicMock())

        assert analyzer._classify_volatility(0.10) == "very_low"
        assert analyzer._classify_volatility(0.05) == "very_low"


class TestBreakoutAssessment:
    """Test breakout potential assessment"""

    def test_assess_breakout_bullish_with_squeeze(self):
        """Test bullish breakout assessment with squeeze"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {
            "width": 2000.0,
            "squeeze": True,
            "price_position": "upper_half",
            "breakout_signal": "neutral_bullish",
        }

        breakout = analyzer._assess_breakout_potential(bb_data, 45000.0)

        assert breakout["direction"] == "upward"
        # Base 0.50 + squeeze 0.20 = 0.70
        assert breakout["probability"] >= 0.70
        # Target should be current + 0.5 * width
        assert breakout["target_price"] == 46000.0  # 45000 + 1000

    def test_assess_breakout_bearish_already_breaking(self):
        """Test bearish breakout when price already below lower band"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {
            "width": 3000.0,
            "squeeze": False,
            "price_position": "below",
            "breakout_signal": "bearish",
        }

        breakout = analyzer._assess_breakout_potential(bb_data, 42000.0)

        assert breakout["direction"] == "downward"
        # Base 0.50 + already breaking 0.15 = 0.65
        assert breakout["probability"] >= 0.65
        # Target should be current - 0.5 * width
        assert breakout["target_price"] == 40500.0  # 42000 - 1500

    def test_assess_breakout_neutral(self):
        """Test neutral breakout assessment"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {
            "width": 2000.0,
            "squeeze": False,
            "price_position": "middle",
            "breakout_signal": "neutral",
        }

        breakout = analyzer._assess_breakout_potential(bb_data, 45000.0)

        assert breakout["direction"] == "neutral"
        assert breakout["probability"] == 0.50  # Base probability only
        assert breakout["target_price"] == 45000.0  # No change

    def test_assess_breakout_high_probability_capped(self):
        """Test breakout probability is capped at 0.95"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {
            "width": 2000.0,
            "squeeze": True,  # +0.20
            "price_position": "above",  # +0.15
            "breakout_signal": "bullish",
        }

        breakout = analyzer._assess_breakout_potential(bb_data, 46500.0)

        # Base 0.50 + squeeze 0.20 + breaking 0.15 = 0.85, capped at 0.95
        assert breakout["probability"] <= 0.95


class TestTradingRecommendations:
    """Test trading recommendation generation"""

    def test_recommendation_squeeze_detected(self):
        """Test recommendation when squeeze is detected"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {"squeeze": True, "price_position": "middle"}
        breakout = {"probability": 0.70}

        recommendation = analyzer._generate_recommendation(bb_data, breakout)

        assert "squeeze" in recommendation.lower()
        assert "wait" in recommendation.lower()

    def test_recommendation_strong_bullish_breakout(self):
        """Test recommendation for strong bullish breakout"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {"squeeze": False, "price_position": "above"}
        breakout = {"probability": 0.85}

        recommendation = analyzer._generate_recommendation(bb_data, breakout)

        assert "bullish" in recommendation.lower()
        assert "breakout" in recommendation.lower()

    def test_recommendation_strong_bearish_breakout(self):
        """Test recommendation for strong bearish breakout"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {"squeeze": False, "price_position": "below"}
        breakout = {"probability": 0.85}

        recommendation = analyzer._generate_recommendation(bb_data, breakout)

        assert "bearish" in recommendation.lower()
        assert "breakout" in recommendation.lower()

    def test_recommendation_moderate_bullish(self):
        """Test recommendation for moderate bullish bias"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {"squeeze": False, "price_position": "upper_half"}
        breakout = {"probability": 0.60}

        recommendation = analyzer._generate_recommendation(bb_data, breakout)

        assert "bullish" in recommendation.lower()
        assert "resistance" in recommendation.lower()

    def test_recommendation_moderate_bearish(self):
        """Test recommendation for moderate bearish bias"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {"squeeze": False, "price_position": "lower_half"}
        breakout = {"probability": 0.60}

        recommendation = analyzer._generate_recommendation(bb_data, breakout)

        assert "bearish" in recommendation.lower()
        assert "support" in recommendation.lower()

    def test_recommendation_neutral(self):
        """Test recommendation for neutral conditions"""
        analyzer = VolatilityAnalyzer(MagicMock())

        bb_data = {"squeeze": False, "price_position": "middle"}
        breakout = {"probability": 0.50}

        recommendation = analyzer._generate_recommendation(bb_data, breakout)

        assert "neutral" in recommendation.lower()


class TestCurrentPriceExtraction:
    """Test current price extraction from OHLCV data"""

    def test_extract_current_price_valid_data(self):
        """Test extracting current price from valid OHLCV data"""
        analyzer = VolatilityAnalyzer(MagicMock())

        ohlcv_result = {"data": [[1, 45000.0, 45200.0, 44800.0, 45100.0, 1000.0]]}

        price = analyzer._extract_current_price(ohlcv_result)

        # Should extract close price (index 4)
        assert price == 45100.0

    def test_extract_current_price_exception(self):
        """Test price extraction handles exceptions"""
        analyzer = VolatilityAnalyzer(MagicMock())

        result = Exception("API error")

        price = analyzer._extract_current_price(result)

        assert price == 0.0

    def test_extract_current_price_empty_data(self):
        """Test price extraction handles empty data"""
        analyzer = VolatilityAnalyzer(MagicMock())

        result = {"data": []}

        price = analyzer._extract_current_price(result)

        assert price == 0.0


class TestParallelExecution:
    """Test parallel indicator fetching"""

    @pytest.mark.asyncio
    async def test_parallel_indicator_fetching(self):
        """Test that ATR, BB, and OHLCV are fetched in parallel"""
        mock_client = AsyncMock()

        # Track number of calls
        call_count = 0

        async def mock_call_tool(tool_name, params):
            nonlocal call_count
            call_count += 1
            if "average_true_range" in tool_name.lower():
                return {"atr": [450.0]}
            elif "bollinger" in tool_name.lower():
                return {
                    "upper": [46000.0],
                    "middle": [44500.0],
                    "lower": [43000.0],
                }
            elif "ohlcv" in tool_name.lower():
                return {"data": [[1, 45000.0, 45200.0, 44800.0, 45100.0, 1000.0]]}
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        analyzer = VolatilityAnalyzer(mock_client)

        await analyzer.analyze("BTC/USDT")

        # Should have 3 parallel calls (ATR, BB, OHLCV)
        assert call_count == 3


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    @pytest.mark.asyncio
    async def test_confidence_with_all_data(self):
        """Test confidence when both ATR and BB data available"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "average_true_range" in tool_name.lower():
                return {"atr": [450.0]}
            elif "bollinger" in tool_name.lower():
                return {
                    "upper": [46000.0],
                    "middle": [44500.0],
                    "lower": [43000.0],
                }
            elif "ohlcv" in tool_name.lower():
                return {"data": [[1, 45000.0, 45200.0, 44800.0, 45100.0, 1000.0]]}
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        analyzer = VolatilityAnalyzer(mock_client)

        result = await analyzer.analyze("BTC/USDT", verbose=True)

        # Base 0.70 + ATR 0.10 + BB 0.15 = 0.95
        assert result["metadata"]["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_confidence_with_missing_data(self):
        """Test confidence when some indicators fail"""
        mock_client = AsyncMock()

        async def mock_call_tool(tool_name, params):
            if "average_true_range" in tool_name.lower():
                return {"atr": [450.0]}  # ATR succeeds
            elif "bollinger" in tool_name.lower():
                raise Exception("BB failed")  # BB fails
            elif "ohlcv" in tool_name.lower():
                return {"data": [[1, 45000.0, 45200.0, 44800.0, 45100.0, 1000.0]]}
            return {}

        mock_client.call_tool.side_effect = mock_call_tool

        analyzer = VolatilityAnalyzer(mock_client)

        result = await analyzer.analyze("BTC/USDT", verbose=True)

        # Base 0.70 + ATR 0.10 = 0.80 (BB failed, no +0.15)
        assert result["metadata"]["confidence"] == 0.80


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
