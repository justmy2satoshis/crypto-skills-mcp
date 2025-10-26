"""
Unit Tests for CryptoVCAnalyst

Tests the Crypto VC Analyst Agent's functionality including:
- Tokenomics analysis
- Technical health assessment
- Liquidity analysis
- Development activity tracking
- Risk scoring
- Due diligence reporting
- Metadata and capabilities
"""

import pytest
import asyncio
from agents import (
    CryptoVCAnalyst,
    RiskLevel,
    InvestmentRecommendation,
    analyze_crypto_project,
)


class TestCryptoVCAnalystInit:
    """Test CryptoVCAnalyst initialization"""

    def test_init_without_mcp_client(self):
        """Test initialization without MCP client"""
        analyst = CryptoVCAnalyst()
        assert analyst.name == "crypto_vc_analyst"
        assert analyst.description == "Fundamental analysis and due diligence"
        assert analyst.mcp_client is None

    def test_init_with_mcp_client(self):
        """Test initialization with MCP client"""
        mock_client = "mock_mcp_client"
        analyst = CryptoVCAnalyst(mcp_client=mock_client)
        assert analyst.mcp_client == mock_client

    def test_required_servers(self):
        """Test required MCP servers list"""
        analyst = CryptoVCAnalyst()
        assert "crypto-projects-mcp" in analyst.required_servers
        assert "ccxt-mcp" in analyst.required_servers
        assert "crypto-indicators-mcp" in analyst.required_servers
        assert len(analyst.required_servers) == 3

    def test_optional_servers(self):
        """Test optional MCP servers list"""
        analyst = CryptoVCAnalyst()
        assert len(analyst.optional_servers) == 1  # github-manager is optional
        assert "github-manager" in analyst.optional_servers


class TestAnalyzeTokenomics:
    """Test analyze_tokenomics() method"""

    @pytest.mark.asyncio
    async def test_analyze_tokenomics_default(self):
        """Test tokenomics analysis with defaults"""
        analyst = CryptoVCAnalyst()
        result = await analyst.analyze_tokenomics("BTC")

        # Verify structure
        assert "supply_analysis" in result
        assert "distribution" in result
        assert "utility" in result
        assert "red_flags" in result
        assert "overall_score" in result

        # Verify supply analysis
        supply = result["supply_analysis"]
        assert "score" in supply
        assert "inflation_rate" in supply
        assert "max_supply" in supply
        assert "circulating_supply" in supply
        assert 0 <= supply["score"] <= 100
        assert isinstance(supply["inflation_rate"], (int, float))

        # Verify distribution
        distribution = result["distribution"]
        assert "score" in distribution
        assert "top_10_holders" in distribution
        assert "gini_coefficient" in distribution
        assert 0 <= distribution["score"] <= 100
        assert 0.0 <= distribution["gini_coefficient"] <= 1.0

        # Verify utility
        utility = result["utility"]
        assert "score" in utility
        assert "use_cases" in utility
        assert isinstance(utility["use_cases"], list)
        assert 0 <= utility["score"] <= 100

        # Verify overall score
        assert 0 <= result["overall_score"] <= 100

        # Verify red flags is a list
        assert isinstance(result["red_flags"], list)

    @pytest.mark.asyncio
    async def test_analyze_tokenomics_custom_asset(self):
        """Test tokenomics analysis with custom asset"""
        analyst = CryptoVCAnalyst()
        result = await analyst.analyze_tokenomics("ETH")

        assert "supply_analysis" in result
        assert "overall_score" in result

    @pytest.mark.asyncio
    async def test_tokenomics_scores_valid_range(self):
        """Test that all scores are in valid range 0-100"""
        analyst = CryptoVCAnalyst()
        result = await analyst.analyze_tokenomics("BTC")

        assert 0 <= result["supply_analysis"]["score"] <= 100
        assert 0 <= result["distribution"]["score"] <= 100
        assert 0 <= result["utility"]["score"] <= 100
        assert 0 <= result["overall_score"] <= 100


class TestAssessTechnicalHealth:
    """Test assess_technical_health() method"""

    @pytest.mark.asyncio
    async def test_assess_technical_health_default(self):
        """Test technical health assessment with defaults"""
        analyst = CryptoVCAnalyst()
        result = await analyst.assess_technical_health("BTC")

        # Verify structure
        assert "network_health" in result
        assert "security" in result
        assert "performance" in result
        assert "overall_score" in result

        # Verify network health
        network = result["network_health"]
        assert "score" in network
        assert "active_addresses" in network
        assert "transaction_count" in network
        assert 0 <= network["score"] <= 100

        # Verify security
        security = result["security"]
        assert "score" in security
        assert "hash_rate" in security
        assert "consensus_mechanism" in security
        assert 0 <= security["score"] <= 100

        # Verify performance
        performance = result["performance"]
        assert "score" in performance
        assert "tps" in performance
        assert "block_time" in performance
        assert 0 <= performance["score"] <= 100

        # Verify overall score
        assert 0 <= result["overall_score"] <= 100

    @pytest.mark.asyncio
    async def test_assess_technical_health_custom_asset(self):
        """Test technical health with custom asset"""
        analyst = CryptoVCAnalyst()
        result = await analyst.assess_technical_health("ETH")

        assert "network_health" in result
        assert "overall_score" in result


class TestAnalyzeLiquidity:
    """Test analyze_liquidity() method"""

    @pytest.mark.asyncio
    async def test_analyze_liquidity_default(self):
        """Test liquidity analysis with defaults"""
        analyst = CryptoVCAnalyst()
        result = await analyst.analyze_liquidity("BTC")

        # Verify structure
        assert "trading_volume" in result
        assert "market_depth" in result
        assert "exchange_availability" in result
        assert "liquidity_score" in result

        # Verify trading volume
        volume = result["trading_volume"]
        assert "24h_volume" in volume
        assert "volume_trend" in volume
        assert isinstance(volume["24h_volume"], (int, float))
        assert volume["24h_volume"] >= 0

        # Verify market depth
        depth = result["market_depth"]
        assert "bid_ask_spread" in depth
        assert "order_book_depth" in depth
        assert isinstance(depth["bid_ask_spread"], (int, float))
        assert depth["bid_ask_spread"] >= 0

        # Verify exchange availability
        exchanges = result["exchange_availability"]
        assert "exchange_count" in exchanges
        assert "major_exchanges" in exchanges
        assert isinstance(exchanges["exchange_count"], int)
        assert exchanges["exchange_count"] >= 0

        # Verify liquidity score
        assert 0 <= result["liquidity_score"] <= 100

    @pytest.mark.asyncio
    async def test_analyze_liquidity_custom_asset(self):
        """Test liquidity analysis with custom asset"""
        analyst = CryptoVCAnalyst()
        result = await analyst.analyze_liquidity("ETH")

        assert "trading_volume" in result
        assert "liquidity_score" in result


class TestTrackDevelopmentActivity:
    """Test track_development_activity() method"""

    @pytest.mark.asyncio
    async def test_track_development_activity_default(self):
        """Test development activity tracking with defaults"""
        analyst = CryptoVCAnalyst()
        result = await analyst.track_development_activity("BTC")

        # Verify structure
        assert "github_metrics" in result
        assert "community_engagement" in result
        assert "activity_score" in result

        # Verify GitHub metrics
        github = result["github_metrics"]
        assert "commits" in github
        assert "contributors" in github
        assert "stars" in github
        assert "forks" in github
        assert isinstance(github["commits"], int)
        assert github["commits"] >= 0
        assert isinstance(github["contributors"], int)
        assert github["contributors"] >= 0

        # Verify community engagement
        community = result["community_engagement"]
        assert "discord_members" in community
        assert "twitter_followers" in community
        assert isinstance(community["discord_members"], int)
        assert isinstance(community["twitter_followers"], int)

        # Verify activity score
        assert 0 <= result["activity_score"] <= 100

    @pytest.mark.asyncio
    async def test_track_development_activity_custom_period(self):
        """Test development tracking with custom period"""
        analyst = CryptoVCAnalyst()
        result = await analyst.track_development_activity("BTC", period_days=90)

        assert "github_metrics" in result
        assert "activity_score" in result


class TestCalculateRiskScore:
    """Test calculate_risk_score() method"""

    @pytest.mark.asyncio
    async def test_calculate_risk_score_default(self):
        """Test risk score calculation with defaults"""
        analyst = CryptoVCAnalyst()
        result = await analyst.calculate_risk_score("BTC")

        # Verify structure
        assert "risk_score" in result
        assert "risk_level" in result
        assert "risk_breakdown" in result
        assert "position_sizing" in result
        assert "warnings" in result

        # Verify risk score
        assert 0 <= result["risk_score"] <= 100

        # Verify risk level is valid enum value
        assert result["risk_level"] in [level.value for level in RiskLevel]

        # Verify risk breakdown
        breakdown = result["risk_breakdown"]
        assert "tokenomics_risk" in breakdown
        assert "technical_risk" in breakdown
        assert "liquidity_risk" in breakdown
        assert "regulatory_risk" in breakdown
        for risk in breakdown.values():
            assert 0 <= risk <= 100

        # Verify position sizing
        sizing = result["position_sizing"]
        assert "max_allocation" in sizing
        assert "recommended_allocation" in sizing
        assert 0.0 <= sizing["max_allocation"] <= 1.0
        assert 0.0 <= sizing["recommended_allocation"] <= 1.0
        assert sizing["recommended_allocation"] <= sizing["max_allocation"]

        # Verify warnings is a list
        assert isinstance(result["warnings"], list)

    @pytest.mark.asyncio
    async def test_calculate_risk_score_custom_asset(self):
        """Test risk calculation with custom asset"""
        analyst = CryptoVCAnalyst()
        result = await analyst.calculate_risk_score("ETH")

        assert "risk_score" in result
        assert "risk_level" in result

    @pytest.mark.asyncio
    async def test_risk_level_matches_score(self):
        """Test that risk_level enum matches risk_score"""
        analyst = CryptoVCAnalyst()
        result = await analyst.calculate_risk_score("BTC")

        score = result["risk_score"]
        level = result["risk_level"]

        # Verify logical consistency between score and level
        if score <= 30:
            assert level == "low"
        elif score >= 70:
            assert level == "high"
        # Medium is between 30-70


class TestGenerateDueDiligenceReport:
    """Test generate_due_diligence_report() method"""

    @pytest.mark.asyncio
    async def test_generate_due_diligence_report_default(self):
        """Test DD report generation with defaults"""
        analyst = CryptoVCAnalyst()
        result = await analyst.generate_due_diligence_report("BTC")

        # Verify structure
        assert "overall_score" in result
        assert "recommendation" in result
        assert "confidence" in result
        assert "strengths" in result
        assert "concerns" in result
        assert "tokenomics" in result
        assert "technical_health" in result
        assert "liquidity" in result
        assert "development_activity" in result
        assert "risk_assessment" in result
        assert "executive_summary" in result

        # Verify overall score
        assert 0 <= result["overall_score"] <= 100

        # Verify recommendation is valid enum value
        assert result["recommendation"] in [rec.value for rec in InvestmentRecommendation]

        # Verify confidence
        assert 0.0 <= result["confidence"] <= 1.0

        # Verify strengths and concerns are lists
        assert isinstance(result["strengths"], list)
        assert isinstance(result["concerns"], list)
        assert len(result["strengths"]) > 0
        assert len(result["concerns"]) > 0

        # Verify sub-analyses are present
        assert "overall_score" in result["tokenomics"]
        assert "overall_score" in result["technical_health"]
        assert "liquidity_score" in result["liquidity"]
        assert "activity_score" in result["development_activity"]
        assert "risk_score" in result["risk_assessment"]

        # Verify executive summary is non-empty
        assert isinstance(result["executive_summary"], str)
        assert len(result["executive_summary"]) > 0

    @pytest.mark.asyncio
    async def test_generate_due_diligence_report_custom_asset(self):
        """Test DD report with custom asset"""
        analyst = CryptoVCAnalyst()
        result = await analyst.generate_due_diligence_report("ETH")

        assert "overall_score" in result
        assert "recommendation" in result

    @pytest.mark.asyncio
    async def test_dd_report_calls_sub_methods(self):
        """Test that DD report incorporates all sub-analyses"""
        analyst = CryptoVCAnalyst()
        result = await analyst.generate_due_diligence_report("BTC")

        # Verify all sub-analyses are included
        assert "tokenomics" in result
        assert "technical_health" in result
        assert "liquidity" in result
        assert "development_activity" in result
        assert "risk_assessment" in result

        # Verify executive summary mentions key concepts
        summary = result["executive_summary"].lower()
        assert len(summary) > 100  # Should be comprehensive


class TestGetCapabilities:
    """Test get_capabilities() method"""

    def test_get_capabilities_structure(self):
        """Test capabilities metadata structure"""
        analyst = CryptoVCAnalyst()
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
        analyst = CryptoVCAnalyst()
        capabilities = analyst.get_capabilities()

        assert capabilities["name"] == "crypto_vc_analyst"
        assert capabilities["type"] == "specialized_agent"
        assert capabilities["domain"] == "fundamental_analysis"
        assert capabilities["token_efficiency"] == 0.0  # Agents have no token reduction

        # Verify capabilities list
        assert "tokenomics_analysis" in capabilities["capabilities"]
        assert "technical_health_assessment" in capabilities["capabilities"]
        assert "liquidity_analysis" in capabilities["capabilities"]
        assert "development_activity_tracking" in capabilities["capabilities"]
        assert "risk_scoring" in capabilities["capabilities"]
        assert "due_diligence_reporting" in capabilities["capabilities"]

        # Verify MCP servers
        assert "crypto-projects-mcp" in capabilities["required_mcps"]
        assert "ccxt-mcp" in capabilities["required_mcps"]
        assert "crypto-indicators-mcp" in capabilities["required_mcps"]

        # Verify use cases
        assert isinstance(capabilities["use_cases"], list)
        assert len(capabilities["use_cases"]) > 0


class TestConvenienceFunction:
    """Test analyze_crypto_project() convenience function"""

    @pytest.mark.asyncio
    async def test_analyze_crypto_project_tokenomics(self):
        """Test convenience function with tokenomics analysis"""
        result = await analyze_crypto_project("BTC", "tokenomics")
        assert "supply_analysis" in result
        assert "overall_score" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_project_technical(self):
        """Test convenience function with technical analysis"""
        result = await analyze_crypto_project("BTC", "technical")
        assert "network_health" in result
        assert "overall_score" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_project_liquidity(self):
        """Test convenience function with liquidity analysis"""
        result = await analyze_crypto_project("BTC", "liquidity")
        assert "trading_volume" in result
        assert "liquidity_score" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_project_development(self):
        """Test convenience function with development analysis"""
        result = await analyze_crypto_project("BTC", "development")
        assert "github_metrics" in result
        assert "activity_score" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_project_risk(self):
        """Test convenience function with risk analysis"""
        result = await analyze_crypto_project("BTC", "risk")
        assert "risk_score" in result
        assert "risk_level" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_project_full(self):
        """Test convenience function with full DD report"""
        result = await analyze_crypto_project("BTC", "full")
        assert "overall_score" in result
        assert "recommendation" in result
        assert "confidence" in result
        assert "executive_summary" in result

    @pytest.mark.asyncio
    async def test_analyze_crypto_project_invalid_type(self):
        """Test convenience function with invalid analysis type"""
        with pytest.raises(ValueError) as exc_info:
            await analyze_crypto_project("BTC", "invalid_type")
        assert "Invalid analysis_type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_analyze_crypto_project_with_kwargs(self):
        """Test convenience function with additional kwargs"""
        result = await analyze_crypto_project("ETH", "development", period_days=90)
        assert "github_metrics" in result


class TestRiskLevelEnum:
    """Test RiskLevel enum"""

    def test_risk_level_values(self):
        """Test RiskLevel enum has expected values"""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.VERY_HIGH.value == "very_high"

    def test_risk_level_all_members(self):
        """Test RiskLevel has all expected members"""
        risk_levels = [level.value for level in RiskLevel]
        assert "low" in risk_levels
        assert "medium" in risk_levels
        assert "high" in risk_levels
        assert "very_high" in risk_levels
        assert len(risk_levels) == 4


class TestInvestmentRecommendationEnum:
    """Test InvestmentRecommendation enum"""

    def test_investment_recommendation_values(self):
        """Test InvestmentRecommendation enum has expected values"""
        assert InvestmentRecommendation.STRONG_BUY.value == "strong_buy"
        assert InvestmentRecommendation.BUY.value == "buy"
        assert InvestmentRecommendation.HOLD.value == "hold"
        assert InvestmentRecommendation.SELL.value == "sell"
        assert InvestmentRecommendation.STRONG_SELL.value == "strong_sell"

    def test_investment_recommendation_all_members(self):
        """Test InvestmentRecommendation has all expected members"""
        recommendations = [rec.value for rec in InvestmentRecommendation]
        assert "strong_buy" in recommendations
        assert "buy" in recommendations
        assert "hold" in recommendations
        assert "sell" in recommendations
        assert "strong_sell" in recommendations
        assert len(recommendations) == 5


class TestAsyncPatterns:
    """Test async/await patterns"""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test that multiple async calls can run in parallel"""
        analyst = CryptoVCAnalyst()

        # Run multiple methods in parallel
        results = await asyncio.gather(
            analyst.analyze_tokenomics("BTC"),
            analyst.assess_technical_health("BTC"),
            analyst.analyze_liquidity("BTC"),
        )

        assert len(results) == 3
        assert "supply_analysis" in results[0]
        assert "network_health" in results[1]
        assert "trading_volume" in results[2]

    @pytest.mark.asyncio
    async def test_sequential_execution(self):
        """Test that sequential execution works correctly"""
        analyst = CryptoVCAnalyst()

        # Run methods sequentially
        tokenomics = await analyst.analyze_tokenomics("BTC")
        technical = await analyst.assess_technical_health("BTC")
        liquidity = await analyst.analyze_liquidity("BTC")

        assert "supply_analysis" in tokenomics
        assert "network_health" in technical
        assert "trading_volume" in liquidity

    @pytest.mark.asyncio
    async def test_dd_report_integration(self):
        """Test that DD report correctly integrates all sub-analyses"""
        analyst = CryptoVCAnalyst()
        result = await analyst.generate_due_diligence_report("BTC")

        # Verify all sub-analyses are present and valid
        assert result["tokenomics"]["overall_score"] > 0
        assert result["technical_health"]["overall_score"] > 0
        assert result["liquidity"]["liquidity_score"] > 0
        assert result["development_activity"]["activity_score"] > 0
        assert result["risk_assessment"]["risk_score"] > 0

        # Verify overall score is calculated from sub-scores
        assert result["overall_score"] > 0
 
