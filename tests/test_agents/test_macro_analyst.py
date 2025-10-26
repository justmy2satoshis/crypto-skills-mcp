"""
Unit Tests for CryptoMacroAnalyst

Tests the Crypto Macro Analyst Agent's functionality including:
- Macro regime assessment
- Institutional flow tracking
- Fed policy analysis
- Risk sentiment analysis
- Macro synthesis
- Metadata and capabilities
"""

import pytest
import asyncio
from agents import CryptoMacroAnalyst, MacroRegime, analyze_crypto_macro


class TestCryptoMacroAnalystInit:
    """Test CryptoMacroAnalyst initialization"""

    def test_init_without_mcp_client(self):
        """Test initialization without MCP client"""
        analyst = CryptoMacroAnalyst()
        assert analyst.name == "crypto_macro_analyst"
        assert analyst.description == "Macroeconomic analysis and institutional flow tracking"
        assert analyst.mcp_client is None

    def test_init_with_mcp_client(self):
        """Test initialization with MCP client"""
        mock_client = "mock_mcp_client"
        analyst = CryptoMacroAnalyst(mcp_client=mock_client)
        assert analyst.mcp_client == mock_client

    def test_required_servers(self):
        """Test required MCP servers list"""
        analyst = CryptoMacroAnalyst()
        assert "grok-search-mcp" in analyst.required_servers
        assert "etf-flow-mcp" in analyst.required_servers
        assert "ccxt-mcp" in analyst.required_servers
        assert len(analyst.required_servers) == 3

    def test_optional_servers(self):
        """Test optional MCP servers list"""
        analyst = CryptoMacroAnalyst()
        assert "perplexity" in analyst.optional_servers


class TestAnalyzeMacroRegime:
    """Test analyze_macro_regime() method"""

    @pytest.mark.asyncio
    async def test_analyze_macro_regime_default_params(self):
        """Test macro regime analysis with default parameters"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.analyze_macro_regime()

        # Verify structure
        assert "regime" in result
        assert "confidence" in result
        assert "indicators" in result
        assert "reasoning" in result
        assert "timestamp" in result

        # Verify regime is valid MacroRegime enum value
        assert result["regime"] in [regime.value for regime in MacroRegime]

        # Verify confidence is between 0 and 1
        assert 0.0 <= result["confidence"] <= 1.0

        # Verify indicators structure
        indicators = result["indicators"]
        assert "fed_policy" in indicators
        assert "risk_sentiment" in indicators
        assert "institutional_flows" in indicators
        assert "correlation_regime" in indicators

        # Verify reasoning is non-empty string
        assert isinstance(result["reasoning"], str)
        assert len(result["reasoning"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_macro_regime_custom_asset(self):
        """Test macro regime analysis with custom asset"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.analyze_macro_regime(asset="ETH", lookback_days=60)

        assert "regime" in result
        assert "confidence" in result
        # Should still return valid structure regardless of asset

    @pytest.mark.asyncio
    async def test_analyze_macro_regime_returns_valid_enum(self):
        """Test that regime is a valid MacroRegime enum value"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.analyze_macro_regime()

        valid_regimes = ["risk_on", "risk_off", "neutral", "transitioning"]
        assert result["regime"] in valid_regimes


class TestTrackInstitutionalFlows:
    """Test track_institutional_flows() method"""

    @pytest.mark.asyncio
    async def test_track_institutional_flows_default(self):
        """Test institutional flow tracking with defaults"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.track_institutional_flows()

        # Verify structure
        assert "net_flow" in result
        assert "flow_direction" in result
        assert "etf_flows" in result
        assert "exchange_flows" in result
        assert "interpretation" in result

        # Verify flow direction is valid
        assert result["flow_direction"] in ["inflow", "outflow", "neutral"]

        # Verify ETF flows structure
        etf_flows = result["etf_flows"]
        assert "total" in etf_flows
        assert "daily_average" in etf_flows
        assert "trend" in etf_flows
        assert isinstance(etf_flows["total"], (int, float))
        assert isinstance(etf_flows["daily_average"], (int, float))

        # Verify exchange flows structure
        exchange_flows = result["exchange_flows"]
        assert "institutional_volume" in exchange_flows
        assert "retail_volume" in exchange_flows
        assert "ratio" in exchange_flows

    @pytest.mark.asyncio
    async def test_track_institutional_flows_custom_period(self):
        """Test institutional flow tracking with custom period"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.track_institutional_flows(asset="ETH", period_days=14)

        assert "net_flow" in result
        assert "interpretation" in result

    @pytest.mark.asyncio
    async def test_institutional_flows_numerical_validity(self):
        """Test that flow numbers are valid"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.track_institutional_flows()

        # Net flow should be a number
        assert isinstance(result["net_flow"], (int, float))

        # Exchange ratio should be positive
        assert result["exchange_flows"]["ratio"] > 0


class TestAnalyzeFedImpact:
    """Test analyze_fed_impact() method"""

    @pytest.mark.asyncio
    async def test_analyze_fed_impact_without_statement(self):
        """Test Fed analysis without providing statement"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.analyze_fed_impact()

        # Verify structure
        assert "policy_stance" in result
        assert "rate_outlook" in result
        assert "impact_on_crypto" in result
        assert "key_factors" in result
        assert "reasoning" in result

        # Verify policy stance is valid
        valid_stances = ["hawkish", "dovish", "neutral", "neutral_to_dovish", "neutral_to_hawkish"]
        assert any(stance in result["policy_stance"] for stance in valid_stances)

        # Verify crypto impact is valid
        assert result["impact_on_crypto"] in ["bullish", "bearish", "neutral"]

        # Verify key factors is a list
        assert isinstance(result["key_factors"], list)
        assert len(result["key_factors"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_fed_impact_with_statement(self):
        """Test Fed analysis with provided statement"""
        analyst = CryptoMacroAnalyst()
        statement = "The Federal Reserve maintains rates at 5.25-5.50% with no changes signaled."
        result = await analyst.analyze_fed_impact(recent_statement=statement)

        assert "policy_stance" in result
        assert "reasoning" in result


class TestAssessRiskSentiment:
    """Test assess_risk_sentiment() method"""

    @pytest.mark.asyncio
    async def test_assess_risk_sentiment(self):
        """Test risk sentiment assessment"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.assess_risk_sentiment()

        # Verify structure
        assert "sentiment" in result
        assert "confidence" in result
        assert "indicators" in result
        assert "crypto_implication" in result

        # Verify sentiment is valid
        assert result["sentiment"] in ["risk_on", "risk_off", "neutral"]

        # Verify confidence range
        assert 0.0 <= result["confidence"] <= 1.0

        # Verify indicators structure
        indicators = result["indicators"]
        assert "vix" in indicators
        assert "crypto_fear_greed" in indicators
        assert "equity_performance" in indicators
        assert "safe_haven_flows" in indicators

        # Verify VIX is reasonable (typically 10-80)
        assert 5.0 <= indicators["vix"] <= 100.0

        # Verify Fear & Greed is 0-100
        assert 0 <= indicators["crypto_fear_greed"] <= 100


class TestSynthesizeMacroOutlook:
    """Test synthesize_macro_outlook() method"""

    @pytest.mark.asyncio
    async def test_synthesize_macro_outlook_default(self):
        """Test macro outlook synthesis with defaults"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.synthesize_macro_outlook()

        # Verify structure
        assert "recommendation" in result
        assert "confidence" in result
        assert "regime" in result
        assert "key_drivers" in result
        assert "risks" in result
        assert "entry_timing" in result
        assert "exit_timing" in result
        assert "reasoning" in result

        # Verify recommendation is valid
        assert result["recommendation"] in ["bullish", "bearish", "neutral"]

        # Verify confidence range
        assert 0.0 <= result["confidence"] <= 1.0

        # Verify regime is valid
        assert result["regime"] in [regime.value for regime in MacroRegime]

        # Verify lists are populated
        assert isinstance(result["key_drivers"], list)
        assert len(result["key_drivers"]) > 0
        assert isinstance(result["risks"], list)
        assert len(result["risks"]) > 0

    @pytest.mark.asyncio
    async def test_synthesize_macro_outlook_custom_horizon(self):
        """Test macro outlook with custom horizon"""
        analyst = CryptoMacroAnalyst()
        result = await analyst.synthesize_macro_outlook(asset="ETH", horizon_days=90)

        assert "recommendation" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_synthesize_calls_sub_methods(self):
        """Test that synthesize calls analyze_macro_regime, track_institutional_flows, etc."""
        analyst = CryptoMacroAnalyst()
        result = await analyst.synthesize_macro_outlook()

        # The result should incorporate data from all sub-methods
        # We can verify this by checking that the reasoning mentions key concepts
        reasoning = result["reasoning"].lower()

        # Should mention regime
        assert "regime" in reasoning or "risk" in reasoning

        # Should mention flows
        assert "flow" in reasoning or "institutional" in reasoning


class TestGetCapabilities:
    """Test get_capabilities() method"""

    def test_get_capabilities_structure(self):
        """Test capabilities metadata structure"""
        analyst = CryptoMacroAnalyst()
        capabilities = analyst.get_capabilities()

        # Verify required fields
        assert "name" in capabilities
        assert "description" in capabilities
        assert "type" in capabilities
        assert "domain" in capabilities
        assert "capabilities" in capabilities
        assert "required_mcps" in capabilities
        assert "optional_mcps" in capabilities
        assert "token_efficiency" in capabilities
        assert "use_cases" in capabilities

    def test_get_capabilities_values(self):
        """Test capabilities metadata values"""
        analyst = CryptoMacroAnalyst()
        capabilities = analyst.get_capabilities()

        assert capabilities["name"] == "crypto_macro_analyst"
        assert capabilities["type"] == "specialized_agent"
        assert capabilities["domain"] == "macroeconomic_analysis"
        assert capabilities["token_efficiency"] == 0.0  # Agents have no token reduction

        # Verify capabilities list
        assert "macro_regime_assessment" in capabilities["capabilities"]
        assert "institutional_flow_tracking" in capabilities["capabilities"]
        assert "fed_policy_analysis" in capabilities["capabilities"]

        # Verify MCP servers
        assert "grok-search-mcp" in capabilities["required_mcps"]
        assert "etf-flow-mcp" in capabilities["required_mcps"]
        assert "ccxt-mcp" in capabilities["required_mcps"]
        assert "perplexity" in capabilities["optional_mcps"]

        # Verify use cases
        assert isinstance(capabilities["use_cases"], list)
        assert len(capabilities["use_cases"]) > 0


class TestConvenienceFunction:
    """Test analyze_crypto_macro() convenience function"""

    @pytest.mark.asyncio
    async def test_analyze_crypto_macro_regime(self):
        """Test convenience function with regime analysis"""
        result = await analyze_crypto_macro("BTC", "regime")
        assert "regime" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_macro_flows(self):
        """Test convenience function with flows analysis"""
        result = await analyze_crypto_macro("BTC", "flows")
        assert "net_flow" in result
        assert "flow_direction" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_macro_fed(self):
        """Test convenience function with Fed analysis"""
        result = await analyze_crypto_macro("BTC", "fed")
        assert "policy_stance" in result
        assert "impact_on_crypto" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_macro_sentiment(self):
        """Test convenience function with sentiment analysis"""
        result = await analyze_crypto_macro("BTC", "sentiment")
        assert "sentiment" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_macro_full(self):
        """Test convenience function with full analysis"""
        result = await analyze_crypto_macro("BTC", "full")
        assert "recommendation" in result
        assert "confidence" in result
        assert "regime" in result
        assert "key_drivers" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_macro_invalid_type(self):
        """Test convenience function with invalid analysis type"""
        with pytest.raises(ValueError) as exc_info:
            await analyze_crypto_macro("BTC", "invalid_type")
        assert "Invalid analysis_type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_analyze_crypto_macro_with_kwargs(self):
        """Test convenience function with additional kwargs"""
        result = await analyze_crypto_macro("ETH", "regime", lookback_days=60)
        assert "regime" in result


class TestMacroRegimeEnum:
    """Test MacroRegime enum"""

    def test_macro_regime_values(self):
        """Test MacroRegime enum has expected values"""
        assert MacroRegime.RISK_ON.value == "risk_on"
        assert MacroRegime.RISK_OFF.value == "risk_off"
        assert MacroRegime.NEUTRAL.value == "neutral"
        assert MacroRegime.TRANSITIONING.value == "transitioning"

    def test_macro_regime_all_members(self):
        """Test MacroRegime has all expected members"""
        regime_values = [regime.value for regime in MacroRegime]
        assert "risk_on" in regime_values
        assert "risk_off" in regime_values
        assert "neutral" in regime_values
        assert "transitioning" in regime_values
        assert len(regime_values) == 4


class TestAsyncPatterns:
    """Test async/await patterns"""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test that multiple async calls can run in parallel"""
        analyst = CryptoMacroAnalyst()

        # Run multiple methods in parallel
        results = await asyncio.gather(
            analyst.analyze_macro_regime(),
            analyst.track_institutional_flows(),
            analyst.assess_risk_sentiment(),
        )

        assert len(results) == 3
        assert "regime" in results[0]
        assert "net_flow" in results[1]
        assert "sentiment" in results[2]

    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Test that sequential execution works correctly"""
        analyst = CryptoMacroAnalyst()

        # Run methods sequentially
        regime = await analyst.analyze_macro_regime()
        flows = await analyst.track_institutional_flows()
        sentiment = await analyst.assess_risk_sentiment()

        assert "regime" in regime
        assert "net_flow" in flows
        assert "sentiment" in sentiment
