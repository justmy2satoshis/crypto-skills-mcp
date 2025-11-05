"""
Unit tests for RiskCalculator Skill

Tests risk calculation functionality including:
- ATR and volatility index calculation
- Volatility regime classification
- Value at Risk (VaR) calculation at 95% and 99% confidence
- Maximum drawdown estimation
- Risk category classification
- Position size calculation
- Risk-reward ratio estimation
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

from skills.data_extraction.risk_calculator import RiskCalculator


class TestRiskCalculatorInit:
    """Test RiskCalculator initialization"""

    def test_initialization(self):
        """Test calculator initializes with MCP client"""
        mock_client = MagicMock()
        calculator = RiskCalculator(mock_client)

        assert calculator.mcp == mock_client
        assert calculator is not None


class TestCalculateMethod:
    """Test main calculate() method"""

    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client with realistic indicator responses"""
        client = AsyncMock()

        # Mock MCP responses in sequence
        client.call_tool.side_effect = [
            # Ticker response (current price)
            {"content": [{"last": 43850.00}]},
            # ATR response
            {"content": [{"atr": [1250.50, 1240.30, 1260.80, 1255.20, 1248.90]}]},
            # Bollinger Bands response
            {
                "content": [
                    {
                        "upper": [45100, 45050, 45000],
                        "lower": [42600, 42650, 42700],
                        "middle": [43850, 43850, 43850],
                    }
                ]
            },
        ]

        return client

    @pytest.mark.asyncio
    async def test_calculate_basic_call(self, mock_mcp_client):
        """Test basic calculate() call returns correct structure"""
        calculator = RiskCalculator(mock_mcp_client)

        result = await calculator.calculate("BTC", timeframe="4h")

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "data-extraction-skill"
        assert "asset" in result
        assert result["asset"] == "BTC"
        assert "data_type" in result
        assert result["data_type"] == "risk_metrics"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_calculate_verbose_true(self, mock_mcp_client):
        """Test verbose=True returns full response with metadata"""
        calculator = RiskCalculator(mock_mcp_client)

        result = await calculator.calculate("BTC", timeframe="4h", verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "asset" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_calculate_verbose_false(self, mock_mcp_client):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        calculator = RiskCalculator(mock_mcp_client)

        result = await calculator.calculate("BTC", timeframe="4h", verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_calculate_data_structure(self, mock_mcp_client):
        """Test data structure contains all required fields"""
        calculator = RiskCalculator(mock_mcp_client)

        result = await calculator.calculate("BTC", timeframe="4h")
        data = result["data"]

        # Verify all required data fields
        assert "volatility" in data
        assert "volatility_regime" in data
        assert "atr" in data
        assert "atr_percent" in data
        assert "var_95" in data
        assert "var_99" in data
        assert "max_drawdown" in data
        assert "risk_category" in data
        assert "current_price" in data
        assert "stop_loss_price" in data
        assert "stop_loss_percent" in data
        assert "position_risk" in data
        assert "risk_reward_ratio" in data
        assert "timeframe" in data
        assert "trading_signal" in data

        # Verify data types
        assert isinstance(data["volatility"], float)
        assert isinstance(data["volatility_regime"], str)
        assert isinstance(data["atr"], float)
        assert isinstance(data["atr_percent"], float)
        assert isinstance(data["var_95"], float)
        assert isinstance(data["var_99"], float)
        assert isinstance(data["max_drawdown"], float)
        assert isinstance(data["risk_category"], str)

    @pytest.mark.asyncio
    async def test_calculate_with_position_sizing(self, mock_mcp_client):
        """Test calculate with account balance for position sizing"""
        calculator = RiskCalculator(mock_mcp_client)

        result = await calculator.calculate(
            "BTC", timeframe="4h", account_balance=100000.0, risk_tolerance=0.02
        )
        data = result["data"]

        # Should include position sizing fields
        assert "recommended_position_size" in data
        assert "position_risk_usd" in data
        assert data["recommended_position_size"] > 0


class TestATRExtraction:
    """Test ATR value extraction from MCP results"""

    def test_extract_atr_valid_data(self):
        """Test extracting ATR from valid indicator result"""
        calculator = RiskCalculator(MagicMock())

        result = {"content": [{"atr": [1250.50, 1240.30, 1260.80]}]}
        atr = calculator._extract_atr(result)

        assert atr == 1250.50  # Latest ATR value

    def test_extract_atr_exception_handling(self):
        """Test ATR extraction handles exceptions"""
        calculator = RiskCalculator(MagicMock())

        result = Exception("Indicator error")
        atr = calculator._extract_atr(result)

        assert atr == 0.0

    def test_extract_atr_invalid_format(self):
        """Test ATR extraction handles invalid format"""
        calculator = RiskCalculator(MagicMock())

        result = {"content": [{"invalid": "data"}]}
        atr = calculator._extract_atr(result)

        assert atr == 0.0


class TestVolatilityMetrics:
    """Test volatility index calculation"""

    def test_calculate_volatility_index_high(self):
        """Test high volatility index calculation"""
        calculator = RiskCalculator(MagicMock())

        # Wide Bollinger Bands indicate high volatility
        atr_result = {"content": [{"atr": [2500.0]}]}
        bb_result = {
            "content": [
                {
                    "upper": [50000],
                    "lower": [40000],  # Wide band (10,000 range)
                    "middle": [45000],
                }
            ]
        }

        volatility = calculator._calculate_volatility_index(atr_result, bb_result)

        assert volatility > 0.5  # High volatility
        assert volatility <= 1.0

    def test_calculate_volatility_index_low(self):
        """Test low volatility index calculation"""
        calculator = RiskCalculator(MagicMock())

        # Narrow Bollinger Bands indicate low volatility
        atr_result = {"content": [{"atr": [500.0]}]}
        bb_result = {
            "content": [
                {
                    "upper": [44000],
                    "lower": [43000],  # Narrow band (1,000 range)
                    "middle": [43500],
                }
            ]
        }

        volatility = calculator._calculate_volatility_index(atr_result, bb_result)

        assert volatility >= 0.0
        assert volatility < 0.5  # Low volatility

    def test_classify_volatility_regime_extreme(self):
        """Test extreme volatility regime classification"""
        calculator = RiskCalculator(MagicMock())

        regime = calculator._classify_volatility_regime(0.75)
        assert regime == "extreme"

    def test_classify_volatility_regime_very_high(self):
        """Test very high volatility regime classification"""
        calculator = RiskCalculator(MagicMock())

        regime = calculator._classify_volatility_regime(0.60)
        assert regime == "very_high"

    def test_classify_volatility_regime_high(self):
        """Test high volatility regime classification"""
        calculator = RiskCalculator(MagicMock())

        regime = calculator._classify_volatility_regime(0.45)
        assert regime == "high"

    def test_classify_volatility_regime_moderate(self):
        """Test moderate volatility regime classification"""
        calculator = RiskCalculator(MagicMock())

        regime = calculator._classify_volatility_regime(0.28)
        assert regime == "moderate"

    def test_classify_volatility_regime_low(self):
        """Test low volatility regime classification"""
        calculator = RiskCalculator(MagicMock())

        regime = calculator._classify_volatility_regime(0.15)
        assert regime == "low"


class TestVaRCalculation:
    """Test Value at Risk calculation"""

    def test_calculate_var_95_confidence(self):
        """Test VaR calculation at 95% confidence"""
        calculator = RiskCalculator(MagicMock())

        current_price = 50000.0
        volatility_index = 0.40  # Moderate volatility

        var_95 = calculator._calculate_var(current_price, volatility_index, confidence=0.95)

        # VaR should be positive
        assert var_95 > 0
        # VaR should be reasonable percentage of price
        assert var_95 < current_price * 0.10  # <10% of price

    def test_calculate_var_99_confidence(self):
        """Test VaR calculation at 99% confidence"""
        calculator = RiskCalculator(MagicMock())

        current_price = 50000.0
        volatility_index = 0.40

        var_99 = calculator._calculate_var(current_price, volatility_index, confidence=0.99)

        # VaR 99% should be higher than VaR 95%
        var_95 = calculator._calculate_var(current_price, volatility_index, confidence=0.95)
        assert var_99 > var_95

    def test_calculate_var_high_volatility(self):
        """Test VaR is higher with higher volatility"""
        calculator = RiskCalculator(MagicMock())

        current_price = 50000.0

        var_low = calculator._calculate_var(current_price, volatility_index=0.20)
        var_high = calculator._calculate_var(current_price, volatility_index=0.70)

        assert var_high > var_low


class TestDrawdownEstimation:
    """Test maximum drawdown estimation"""

    def test_estimate_max_drawdown_high_volatility(self):
        """Test max drawdown with high volatility"""
        calculator = RiskCalculator(MagicMock())

        drawdown = calculator._estimate_max_drawdown(volatility_index=0.70)

        # High volatility should have higher drawdown
        assert drawdown > 0.30
        assert drawdown <= 0.50  # Capped at 50%

    def test_estimate_max_drawdown_low_volatility(self):
        """Test max drawdown with low volatility"""
        calculator = RiskCalculator(MagicMock())

        drawdown = calculator._estimate_max_drawdown(volatility_index=0.15)

        # Low volatility should have lower drawdown
        assert drawdown >= 0.0
        assert drawdown < 0.15

    def test_estimate_max_drawdown_capped(self):
        """Test max drawdown is capped at 50%"""
        calculator = RiskCalculator(MagicMock())

        # Even with extreme volatility, cap at 50%
        drawdown = calculator._estimate_max_drawdown(volatility_index=1.0)

        assert drawdown <= 0.50


class TestRiskClassification:
    """Test risk category classification"""

    def test_classify_risk_category_extreme(self):
        """Test extreme risk classification"""
        calculator = RiskCalculator(MagicMock())

        category = calculator._classify_risk_category(
            volatility_index=0.75, atr_percent=8.0, max_drawdown=0.45
        )

        assert category == "extreme"

    def test_classify_risk_category_high(self):
        """Test high risk classification"""
        calculator = RiskCalculator(MagicMock())

        category = calculator._classify_risk_category(
            volatility_index=0.55, atr_percent=5.0, max_drawdown=0.30
        )

        assert category == "high"

    def test_classify_risk_category_moderate(self):
        """Test moderate risk classification"""
        calculator = RiskCalculator(MagicMock())

        category = calculator._classify_risk_category(
            volatility_index=0.35, atr_percent=3.0, max_drawdown=0.20
        )

        assert category == "moderate"

    def test_classify_risk_category_low(self):
        """Test low risk classification"""
        calculator = RiskCalculator(MagicMock())

        category = calculator._classify_risk_category(
            volatility_index=0.15, atr_percent=1.5, max_drawdown=0.08
        )

        assert category == "low"


class TestPositionSizing:
    """Test position size calculation"""

    def test_calculate_position_size_2_percent_risk(self):
        """Test position sizing with 2% risk tolerance"""
        calculator = RiskCalculator(MagicMock())

        position_size = calculator._calculate_position_size(
            account_balance=100000.0,
            entry_price=50000.0,
            stop_loss_price=48000.0,  # $2000 risk per unit
            risk_tolerance=0.02,  # 2% risk
        )

        # Max loss = $100,000 * 0.02 = $2,000
        # Risk per unit = $50,000 - $48,000 = $2,000
        # Position size = $2,000 / $2,000 = 1.0
        assert position_size == 1.0

    def test_calculate_position_size_1_percent_risk(self):
        """Test position sizing with 1% risk tolerance"""
        calculator = RiskCalculator(MagicMock())

        position_size = calculator._calculate_position_size(
            account_balance=100000.0,
            entry_price=50000.0,
            stop_loss_price=48000.0,
            risk_tolerance=0.01,  # 1% risk
        )

        # Max loss = $100,000 * 0.01 = $1,000
        # Position size = $1,000 / $2,000 = 0.5
        assert position_size == 0.5

    def test_calculate_position_size_invalid_stop_loss(self):
        """Test position sizing with invalid stop-loss (above entry)"""
        calculator = RiskCalculator(MagicMock())

        position_size = calculator._calculate_position_size(
            account_balance=100000.0,
            entry_price=50000.0,
            stop_loss_price=51000.0,  # Invalid: above entry
            risk_tolerance=0.02,
        )

        # Should return 0 for invalid stop-loss
        assert position_size == 0.0

    def test_calculate_position_size_larger_account(self):
        """Test position sizing scales with account size"""
        calculator = RiskCalculator(MagicMock())

        small_account = calculator._calculate_position_size(
            account_balance=50000.0,
            entry_price=50000.0,
            stop_loss_price=48000.0,
            risk_tolerance=0.02,
        )

        large_account = calculator._calculate_position_size(
            account_balance=200000.0,
            entry_price=50000.0,
            stop_loss_price=48000.0,
            risk_tolerance=0.02,
        )

        # Larger account should allow larger position
        assert large_account > small_account
        assert large_account == small_account * 4  # 4x account size


class TestRiskRewardEstimation:
    """Test risk-reward ratio estimation"""

    def test_estimate_risk_reward_extreme_volatility(self):
        """Test risk-reward for extreme volatility"""
        calculator = RiskCalculator(MagicMock())

        ratio = calculator._estimate_risk_reward_ratio(
            volatility_regime="extreme", atr_percent=8.0
        )

        assert ratio == 3.5  # High potential reward

    def test_estimate_risk_reward_very_high_volatility(self):
        """Test risk-reward for very high volatility"""
        calculator = RiskCalculator(MagicMock())

        ratio = calculator._estimate_risk_reward_ratio(
            volatility_regime="very_high", atr_percent=6.0
        )

        assert ratio == 3.0

    def test_estimate_risk_reward_high_volatility(self):
        """Test risk-reward for high volatility"""
        calculator = RiskCalculator(MagicMock())

        ratio = calculator._estimate_risk_reward_ratio(
            volatility_regime="high", atr_percent=4.0
        )

        assert ratio == 2.5

    def test_estimate_risk_reward_moderate_volatility(self):
        """Test risk-reward for moderate volatility"""
        calculator = RiskCalculator(MagicMock())

        ratio = calculator._estimate_risk_reward_ratio(
            volatility_regime="moderate", atr_percent=2.5
        )

        assert ratio == 2.0

    def test_estimate_risk_reward_low_volatility(self):
        """Test risk-reward for low volatility"""
        calculator = RiskCalculator(MagicMock())

        ratio = calculator._estimate_risk_reward_ratio(volatility_regime="low", atr_percent=1.5)

        assert ratio == 1.5  # Lower potential reward


class TestSignalGeneration:
    """Test trading signal generation"""

    def test_extreme_risk_signal(self):
        """Test extreme risk signal generation"""
        calculator = RiskCalculator(MagicMock())

        signal = calculator._generate_trading_signal(
            volatility_regime="extreme",
            risk_category="extreme",
            atr_percent=8.0,
            position_risk=0.10,
            recommended_position_size=0.25,
            account_balance=100000.0,
        )

        assert "extreme" in signal.lower()
        assert "reduce" in signal.lower() or "avoid" in signal.lower()

    def test_high_risk_signal(self):
        """Test high risk signal generation"""
        calculator = RiskCalculator(MagicMock())

        signal = calculator._generate_trading_signal(
            volatility_regime="very_high",
            risk_category="high",
            atr_percent=6.0,
            position_risk=0.06,
            recommended_position_size=0.5,
            account_balance=100000.0,
        )

        assert "high" in signal.lower()
        assert "reduce" in signal.lower() or "25%" in signal.lower()

    def test_moderate_risk_signal(self):
        """Test moderate risk signal generation"""
        calculator = RiskCalculator(MagicMock())

        signal = calculator._generate_trading_signal(
            volatility_regime="moderate",
            risk_category="moderate",
            atr_percent=3.0,
            position_risk=0.03,
            recommended_position_size=1.0,
            account_balance=100000.0,
        )

        assert "moderate" in signal.lower()

    def test_low_risk_signal(self):
        """Test low risk signal generation"""
        calculator = RiskCalculator(MagicMock())

        signal = calculator._generate_trading_signal(
            volatility_regime="low",
            risk_category="low",
            atr_percent=1.5,
            position_risk=0.015,
            recommended_position_size=1.5,
            account_balance=100000.0,
        )

        assert "low" in signal.lower()
        assert "full" in signal.lower() or "tight" in signal.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
