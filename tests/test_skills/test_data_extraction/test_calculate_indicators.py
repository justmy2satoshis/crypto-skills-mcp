"""
Unit tests for IndicatorsCalculator Skill

Tests technical indicators calculation functionality including:
- Multi-indicator parallel calculation
- Indicator-specific normalization (RSI, MACD, Bollinger, etc.)
- Interpretation logic with thresholds
- Custom parameters override
- Verbose parameter functionality
- Invalid indicator validation
- Failed indicator handling
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.data_extraction.calculate_indicators import IndicatorsCalculator


class TestIndicatorsCalculatorInit:
    """Test IndicatorsCalculator initialization"""

    def test_initialization(self):
        """Test calculator initializes with MCP client"""
        mock_client = MagicMock()
        calculator = IndicatorsCalculator(mock_client)

        assert calculator.mcp == mock_client
        assert calculator is not None

    def test_supported_indicators(self):
        """Test class has all 9 supported indicators"""
        assert len(IndicatorsCalculator.INDICATORS) == 9
        assert "rsi" in IndicatorsCalculator.INDICATORS
        assert "macd" in IndicatorsCalculator.INDICATORS
        assert "bollinger" in IndicatorsCalculator.INDICATORS
        assert "ema" in IndicatorsCalculator.INDICATORS
        assert "sma" in IndicatorsCalculator.INDICATORS
        assert "stochastic" in IndicatorsCalculator.INDICATORS
        assert "atr" in IndicatorsCalculator.INDICATORS
        assert "adx" in IndicatorsCalculator.INDICATORS
        assert "obv" in IndicatorsCalculator.INDICATORS

    def test_default_parameters(self):
        """Test default parameters are defined"""
        assert IndicatorsCalculator.DEFAULT_PARAMS["rsi"]["period"] == 14
        assert IndicatorsCalculator.DEFAULT_PARAMS["macd"]["fastPeriod"] == 12
        assert IndicatorsCalculator.DEFAULT_PARAMS["macd"]["slowPeriod"] == 26
        assert IndicatorsCalculator.DEFAULT_PARAMS["macd"]["signalPeriod"] == 9
        assert IndicatorsCalculator.DEFAULT_PARAMS["bollinger"]["period"] == 20
        assert IndicatorsCalculator.DEFAULT_PARAMS["bollinger"]["stdDev"] == 2


class TestCalculateMethod:
    """Test main calculate() method"""

    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client with indicator responses"""
        client = AsyncMock()

        # Mock RSI response
        client.call_tool.return_value = {"rsi": [50.0, 55.0, 60.0, 65.3]}

        return client

    @pytest.mark.asyncio
    async def test_calculate_basic_call(self, mock_mcp_client):
        """Test basic calculate() call returns correct structure"""
        calculator = IndicatorsCalculator(mock_mcp_client)

        result = await calculator.calculate(
            "BTC/USDT", ["rsi"], timeframe="1h", limit=100
        )

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "crypto-indicators-mcp"
        assert "symbol" in result
        assert result["symbol"] == "BTC/USDT"
        assert "data_type" in result
        assert result["data_type"] == "technical_indicators"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_calculate_verbose_true(self, mock_mcp_client):
        """Test verbose=True returns full response with metadata"""
        calculator = IndicatorsCalculator(mock_mcp_client)

        result = await calculator.calculate(
            "BTC/USDT", ["rsi"], verbose=True
        )

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "symbol" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "timeframe" in result["metadata"]
        assert "indicators_count" in result["metadata"]
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_calculate_verbose_false(self, mock_mcp_client):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        calculator = IndicatorsCalculator(mock_mcp_client)

        result = await calculator.calculate(
            "BTC/USDT", ["rsi"], verbose=False
        )

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_calculate_data_structure(self, mock_mcp_client):
        """Test data structure contains requested indicators"""
        calculator = IndicatorsCalculator(mock_mcp_client)

        result = await calculator.calculate(
            "BTC/USDT", ["rsi"], timeframe="1h"
        )
        data = result["data"]

        # Verify data structure
        assert "rsi" in data
        assert isinstance(data["rsi"], dict)


class TestInvalidIndicatorValidation:
    """Test invalid indicator validation"""

    @pytest.mark.asyncio
    async def test_invalid_indicator_raises_error(self):
        """Test ValueError raised for invalid indicator"""
        mock_client = AsyncMock()
        calculator = IndicatorsCalculator(mock_client)

        with pytest.raises(ValueError, match="Invalid indicators"):
            await calculator.calculate(
                "BTC/USDT", ["invalid_indicator"]
            )

    @pytest.mark.asyncio
    async def test_invalid_indicator_error_message(self):
        """Test error message lists invalid and supported indicators"""
        mock_client = AsyncMock()
        calculator = IndicatorsCalculator(mock_client)

        with pytest.raises(ValueError) as exc_info:
            await calculator.calculate(
                "BTC/USDT", ["rsi", "invalid1", "invalid2"]
            )

        error_msg = str(exc_info.value)
        assert "invalid1" in error_msg
        assert "invalid2" in error_msg
        assert "Supported" in error_msg


class TestCustomParametersOverride:
    """Test custom parameters override default parameters"""

    @pytest.mark.asyncio
    async def test_custom_rsi_period(self):
        """Test custom RSI period overrides default"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"rsi": [65.3]}

        calculator = IndicatorsCalculator(mock_client)

        await calculator.calculate(
            "BTC/USDT",
            ["rsi"],
            custom_params={"rsi": {"period": 21}},
        )

        # Verify custom period was used
        call_args = mock_client.call_tool.call_args
        assert call_args[0][1]["period"] == 21

    @pytest.mark.asyncio
    async def test_custom_macd_periods(self):
        """Test custom MACD periods override defaults"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "macd": {"MACD": [150.2], "signal": [145.8]}
        }

        calculator = IndicatorsCalculator(mock_client)

        await calculator.calculate(
            "BTC/USDT",
            ["macd"],
            custom_params={
                "macd": {"fastPeriod": 8, "slowPeriod": 21, "signalPeriod": 5}
            },
        )

        # Verify custom periods were used
        call_args = mock_client.call_tool.call_args
        assert call_args[0][1]["fastPeriod"] == 8
        assert call_args[0][1]["slowPeriod"] == 21
        assert call_args[0][1]["signalPeriod"] == 5


class TestRSINormalization:
    """Test RSI indicator normalization"""

    @pytest.mark.asyncio
    async def test_rsi_value_extraction(self):
        """Test RSI value extracted correctly"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"rsi": [50.0, 55.0, 65.3]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["rsi"])

        rsi_data = result["data"]["rsi"]
        assert rsi_data["value"] == 65.3

    @pytest.mark.asyncio
    async def test_rsi_oversold_flag(self):
        """Test RSI oversold flag (<30)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"rsi": [25.5]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["rsi"])

        rsi_data = result["data"]["rsi"]
        assert rsi_data["oversold"] is True
        assert rsi_data["overbought"] is False

    @pytest.mark.asyncio
    async def test_rsi_overbought_flag(self):
        """Test RSI overbought flag (>70)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"rsi": [75.8]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["rsi"])

        rsi_data = result["data"]["rsi"]
        assert rsi_data["oversold"] is False
        assert rsi_data["overbought"] is True

    @pytest.mark.asyncio
    async def test_rsi_neutral_zone(self):
        """Test RSI in neutral zone (40-60)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"rsi": [50.0]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["rsi"])

        rsi_data = result["data"]["rsi"]
        assert rsi_data["oversold"] is False
        assert rsi_data["overbought"] is False


class TestRSIInterpretation:
    """Test RSI interpretation logic"""

    def test_rsi_interpretation_overbought(self):
        """Test RSI interpretation when overbought (>70)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_rsi(75.0)
        assert interpretation == "Overbought - potential bearish reversal"

    def test_rsi_interpretation_oversold(self):
        """Test RSI interpretation when oversold (<30)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_rsi(25.0)
        assert interpretation == "Oversold - potential bullish reversal"

    def test_rsi_interpretation_neutral(self):
        """Test RSI interpretation in neutral zone (40-60)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_rsi(50.0)
        assert interpretation == "Neutral zone - no clear signal"

    def test_rsi_interpretation_trending(self):
        """Test RSI interpretation when trending (not neutral, not extreme)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_rsi(65.0)
        assert interpretation == "Trending"


class TestMACDNormalization:
    """Test MACD indicator normalization"""

    @pytest.mark.asyncio
    async def test_macd_values_extraction(self):
        """Test MACD value, signal, and histogram extraction"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "macd": {"MACD": [150.2], "signal": [145.8]}
        }

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["macd"])

        macd_data = result["data"]["macd"]
        assert macd_data["value"] == 150.2
        assert macd_data["signal"] == 145.8
        assert macd_data["histogram"] == 4.4  # 150.2 - 145.8

    @pytest.mark.asyncio
    async def test_macd_bullish_crossover(self):
        """Test MACD bullish crossover detection"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "macd": {"MACD": [150.2], "signal": [145.8]}
        }

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["macd"])

        macd_data = result["data"]["macd"]
        assert macd_data["bullish_crossover"] is True
        assert macd_data["bearish_crossover"] is False

    @pytest.mark.asyncio
    async def test_macd_bearish_crossover(self):
        """Test MACD bearish crossover detection"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "macd": {"MACD": [145.8], "signal": [150.2]}
        }

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["macd"])

        macd_data = result["data"]["macd"]
        assert macd_data["bullish_crossover"] is False
        assert macd_data["bearish_crossover"] is True


class TestMACDInterpretation:
    """Test MACD interpretation logic"""

    def test_macd_interpretation_bullish(self):
        """Test MACD interpretation when bullish (value > signal)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_macd(150.0, 145.0)
        assert interpretation == "Bullish - MACD above signal line"

    def test_macd_interpretation_bearish(self):
        """Test MACD interpretation when bearish (value < signal)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_macd(145.0, 150.0)
        assert interpretation == "Bearish - MACD below signal line"

    def test_macd_interpretation_neutral(self):
        """Test MACD interpretation when neutral (value == signal)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_macd(150.0, 150.0)
        assert interpretation == "Neutral - MACD at signal line"


class TestBollingerNormalization:
    """Test Bollinger Bands indicator normalization"""

    @pytest.mark.asyncio
    async def test_bollinger_bands_extraction(self):
        """Test Bollinger Bands upper, middle, lower extraction"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "bollingerBands": {
                "upper": [45000.0],
                "middle": [43500.0],
                "lower": [42000.0],
            }
        }

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["bollinger"])

        bb_data = result["data"]["bollinger"]
        assert bb_data["upper"] == 45000.0
        assert bb_data["middle"] == 43500.0
        assert bb_data["lower"] == 42000.0

    @pytest.mark.asyncio
    async def test_bollinger_width_calculation(self):
        """Test Bollinger Bands width calculation"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "bollingerBands": {
                "upper": [45000.0],
                "middle": [43500.0],
                "lower": [42000.0],
            }
        }

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["bollinger"])

        bb_data = result["data"]["bollinger"]
        assert bb_data["width"] == 3000.0  # 45000 - 42000


class TestBollingerInterpretation:
    """Test Bollinger Bands interpretation logic"""

    def test_bollinger_interpretation_high_volatility(self):
        """Test Bollinger interpretation with high volatility (width > 2000)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_bollinger(46000.0, 43500.0, 41000.0)
        assert interpretation == "High volatility - bands expanding"

    def test_bollinger_interpretation_low_volatility(self):
        """Test Bollinger interpretation with low volatility (width < 500)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_bollinger(43700.0, 43500.0, 43300.0)
        assert interpretation == "Low volatility - bands contracting (breakout potential)"

    def test_bollinger_interpretation_normal_volatility(self):
        """Test Bollinger interpretation with normal volatility"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_bollinger(44500.0, 43500.0, 42500.0)
        assert interpretation == "Normal volatility range"


class TestEMASMANormalization:
    """Test EMA and SMA indicator normalization"""

    @pytest.mark.asyncio
    async def test_ema_value_extraction(self):
        """Test EMA value extraction"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"EMA": [43500.0, 43550.0, 43600.0]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["ema"])

        ema_data = result["data"]["ema"]
        assert ema_data["value"] == 43600.0
        assert "interpretation" in ema_data

    @pytest.mark.asyncio
    async def test_sma_value_extraction(self):
        """Test SMA value extraction"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"SMA": [43400.0, 43450.0, 43500.0]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["sma"])

        sma_data = result["data"]["sma"]
        assert sma_data["value"] == 43500.0
        assert "interpretation" in sma_data


class TestStochasticNormalization:
    """Test Stochastic Oscillator normalization"""

    @pytest.mark.asyncio
    async def test_stochastic_values_extraction(self):
        """Test Stochastic %K and %D extraction"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "stochastic": {"k": [65.0], "d": [60.0]}
        }

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["stochastic"])

        stoch_data = result["data"]["stochastic"]
        assert stoch_data["k"] == 65.0
        assert stoch_data["d"] == 60.0

    @pytest.mark.asyncio
    async def test_stochastic_oversold_flag(self):
        """Test Stochastic oversold flag (k < 20)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "stochastic": {"k": [15.0], "d": [18.0]}
        }

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["stochastic"])

        stoch_data = result["data"]["stochastic"]
        assert stoch_data["oversold"] is True
        assert stoch_data["overbought"] is False

    @pytest.mark.asyncio
    async def test_stochastic_overbought_flag(self):
        """Test Stochastic overbought flag (k > 80)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {
            "stochastic": {"k": [85.0], "d": [82.0]}
        }

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["stochastic"])

        stoch_data = result["data"]["stochastic"]
        assert stoch_data["oversold"] is False
        assert stoch_data["overbought"] is True


class TestStochasticInterpretation:
    """Test Stochastic Oscillator interpretation logic"""

    def test_stochastic_interpretation_overbought(self):
        """Test Stochastic interpretation when overbought (k > 80)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_stochastic(85.0, 82.0)
        assert interpretation == "Overbought - potential reversal"

    def test_stochastic_interpretation_oversold(self):
        """Test Stochastic interpretation when oversold (k < 20)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_stochastic(15.0, 18.0)
        assert interpretation == "Oversold - potential reversal"

    def test_stochastic_interpretation_bullish(self):
        """Test Stochastic interpretation when bullish (k > d)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_stochastic(65.0, 60.0)
        assert interpretation == "Bullish momentum - %K above %D"

    def test_stochastic_interpretation_bearish(self):
        """Test Stochastic interpretation when bearish (k < d)"""
        calculator = IndicatorsCalculator(MagicMock())

        interpretation = calculator._interpret_stochastic(55.0, 60.0)
        assert interpretation == "Bearish momentum - %K below %D"


class TestATRNormalization:
    """Test ATR (Average True Range) normalization"""

    @pytest.mark.asyncio
    async def test_atr_value_extraction(self):
        """Test ATR value extraction"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"atr": [250.0, 275.0, 300.0]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["atr"])

        atr_data = result["data"]["atr"]
        assert atr_data["value"] == 300.0

    @pytest.mark.asyncio
    async def test_atr_high_volatility_classification(self):
        """Test ATR high volatility classification (> 500)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"atr": [600.0]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["atr"])

        atr_data = result["data"]["atr"]
        assert atr_data["volatility"] == "high"

    @pytest.mark.asyncio
    async def test_atr_medium_volatility_classification(self):
        """Test ATR medium volatility classification (200-500)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"atr": [350.0]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["atr"])

        atr_data = result["data"]["atr"]
        assert atr_data["volatility"] == "medium"

    @pytest.mark.asyncio
    async def test_atr_low_volatility_classification(self):
        """Test ATR low volatility classification (< 200)"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"atr": [150.0]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate("BTC/USDT", ["atr"])

        atr_data = result["data"]["atr"]
        assert atr_data["volatility"] == "low"


class TestGenericNormalization:
    """Test generic normalization for unsupported indicators"""

    @pytest.mark.asyncio
    async def test_generic_normalization_fallback(self):
        """Test generic normalization for indicators without specific logic"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"someData": [1, 2, 3]}

        calculator = IndicatorsCalculator(mock_client)

        # Use OBV which doesn't have specific normalization
        result = await calculator.calculate("BTC/USDT", ["obv"])

        obv_data = result["data"]["obv"]
        assert "raw" in obv_data
        assert "interpretation" in obv_data


class TestParallelExecution:
    """Test parallel indicator calculation"""

    @pytest.mark.asyncio
    async def test_parallel_execution_multiple_indicators(self):
        """Test multiple indicators calculated in parallel"""
        mock_client = AsyncMock()

        # Mock different responses for different indicators
        mock_client.call_tool.side_effect = [
            {"rsi": [65.3]},
            {"macd": {"MACD": [150.2], "signal": [145.8]}},
            {"bollingerBands": {"upper": [45000.0], "middle": [43500.0], "lower": [42000.0]}},
        ]

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate(
            "BTC/USDT", ["rsi", "macd", "bollinger"], verbose=True
        )

        # All indicators should be present
        assert "rsi" in result["data"]
        assert "macd" in result["data"]
        assert "bollinger" in result["data"]

        # Metadata should reflect 3 indicators
        assert result["metadata"]["indicators_count"] == 3


class TestFailedIndicatorHandling:
    """Test handling of failed indicator calculations"""

    @pytest.mark.asyncio
    async def test_failed_indicator_continues_execution(self):
        """Test failed indicator doesn't stop other calculations"""
        mock_client = AsyncMock()

        # First indicator fails, second succeeds
        mock_client.call_tool.side_effect = [
            Exception("Network error"),
            {"macd": {"MACD": [150.2], "signal": [145.8]}},
        ]

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate(
            "BTC/USDT", ["rsi", "macd"], verbose=True
        )

        # Successful indicator should be present
        assert "macd" in result["data"]
        assert "rsi" not in result["data"]

        # Warnings should be in metadata
        assert "warnings" in result["metadata"]
        assert any("rsi" in w for w in result["metadata"]["warnings"])

    @pytest.mark.asyncio
    async def test_failed_indicator_reduces_confidence(self):
        """Test failed indicator reduces confidence score"""
        mock_client = AsyncMock()

        # 1 out of 2 indicators fails
        mock_client.call_tool.side_effect = [
            Exception("API error"),
            {"macd": {"MACD": [150.2], "signal": [145.8]}},
        ]

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate(
            "BTC/USDT", ["rsi", "macd"], verbose=True
        )

        # Confidence should be 0.50 (1 success / 2 total)
        assert result["metadata"]["confidence"] == 0.5


class TestConfidenceCalculation:
    """Test confidence score calculation"""

    @pytest.mark.asyncio
    async def test_confidence_100_percent_success(self):
        """Test confidence is 1.0 when all indicators succeed"""
        mock_client = AsyncMock()

        mock_client.call_tool.side_effect = [
            {"rsi": [65.3]},
            {"macd": {"MACD": [150.2], "signal": [145.8]}},
        ]

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate(
            "BTC/USDT", ["rsi", "macd"], verbose=True
        )

        # 100% success
        assert result["metadata"]["confidence"] == 1.0

    @pytest.mark.asyncio
    async def test_confidence_partial_success(self):
        """Test confidence reflects partial success rate"""
        mock_client = AsyncMock()

        # 2 out of 3 succeed
        mock_client.call_tool.side_effect = [
            {"rsi": [65.3]},
            Exception("Error"),
            {"bollingerBands": {"upper": [45000.0], "middle": [43500.0], "lower": [42000.0]}},
        ]

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate(
            "BTC/USDT", ["rsi", "macd", "bollinger"], verbose=True
        )

        # 2/3 = 0.67
        assert result["metadata"]["confidence"] == 0.67


class TestMetadata:
    """Test metadata fields"""

    @pytest.mark.asyncio
    async def test_metadata_timeframe(self):
        """Test metadata includes timeframe"""
        mock_client = AsyncMock()
        mock_client.call_tool.return_value = {"rsi": [65.3]}

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate(
            "BTC/USDT", ["rsi"], timeframe="4h", verbose=True
        )

        assert result["metadata"]["timeframe"] == "4h"

    @pytest.mark.asyncio
    async def test_metadata_indicators_count(self):
        """Test metadata includes successful indicators count"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = [
            {"rsi": [65.3]},
            {"macd": {"MACD": [150.2], "signal": [145.8]}},
        ]

        calculator = IndicatorsCalculator(mock_client)
        result = await calculator.calculate(
            "BTC/USDT", ["rsi", "macd"], verbose=True
        )

        assert result["metadata"]["indicators_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
