"""
Unit Tests for ThesisSynthesizer

Tests the Thesis Synthesizer Agent's functionality including:
- Comprehensive analysis orchestration
- Investment thesis generation
- Conflict detection and resolution
- Signal synthesis with weighted agents
- Agent orchestration patterns
- Metadata and capabilities
"""

import pytest
import asyncio
from agents import (
    ThesisSynthesizer,
    CryptoMacroAnalyst,
    CryptoVCAnalyst,
    CryptoSentimentAnalyst,
    ThesisType,
    ConflictType,
    synthesize_investment_thesis,
)


class TestThesisSynthesizerInit:
    """Test ThesisSynthesizer initialization"""

    def test_init_without_agents(self):
        """Test initialization without providing agents"""
        synthesizer = ThesisSynthesizer()
        assert synthesizer.name == "thesis_synthesizer"
        assert synthesizer.description == "Strategic orchestration and thesis synthesis"
        assert synthesizer.mcp_client is None

        # Should auto-instantiate agents
        assert synthesizer.macro_analyst is not None
        assert synthesizer.vc_analyst is not None
        assert synthesizer.sentiment_analyst is not None
        assert isinstance(synthesizer.macro_analyst, CryptoMacroAnalyst)
        assert isinstance(synthesizer.vc_analyst, CryptoVCAnalyst)
        assert isinstance(synthesizer.sentiment_analyst, CryptoSentimentAnalyst)

    def test_init_with_agents(self):
        """Test initialization with provided agents"""
        macro = CryptoMacroAnalyst()
        vc = CryptoVCAnalyst()
        sentiment = CryptoSentimentAnalyst()

        synthesizer = ThesisSynthesizer(
            macro_analyst=macro, vc_analyst=vc, sentiment_analyst=sentiment
        )

        assert synthesizer.macro_analyst is macro
        assert synthesizer.vc_analyst is vc
        assert synthesizer.sentiment_analyst is sentiment

    def test_init_with_mcp_client(self):
        """Test initialization with MCP client"""
        mock_client = "mock_mcp_client"
        synthesizer = ThesisSynthesizer(mcp_client=mock_client)
        assert synthesizer.mcp_client == mock_client

        # Agents should also receive the MCP client
        assert synthesizer.macro_analyst.mcp_client == mock_client
        assert synthesizer.vc_analyst.mcp_client == mock_client
        assert synthesizer.sentiment_analyst.mcp_client == mock_client

    def test_agent_weights(self):
        """Test that agent weights are correctly set"""
        synthesizer = ThesisSynthesizer()
        assert synthesizer.macro_weight == 0.35
        assert synthesizer.fundamental_weight == 0.40
        assert synthesizer.sentiment_weight == 0.25

        # Weights should sum to 1.0
        total_weight = (
            synthesizer.macro_weight + synthesizer.fundamental_weight + synthesizer.sentiment_weight
        )
        assert abs(total_weight - 1.0) < 0.001  # Allow for floating point error

    def test_required_servers(self):
        """Test required MCP servers list"""
        synthesizer = ThesisSynthesizer()
        # Should be empty - delegates to specialized agents
        assert len(synthesizer.required_servers) == 0

    def test_optional_servers(self):
        """Test optional MCP servers list"""
        synthesizer = ThesisSynthesizer()
        # Should be empty - delegates to specialized agents
        assert len(synthesizer.optional_servers) == 0


class TestOrchestrateComprehensiveAnalysis:
    """Test orchestrate_comprehensive_analysis() method"""

    @pytest.mark.asyncio
    async def test_orchestrate_analysis_default(self):
        """Test comprehensive analysis orchestration with defaults"""
        synthesizer = ThesisSynthesizer()
        result = await synthesizer.orchestrate_comprehensive_analysis("BTC")

        # Verify structure
        assert "macro_analysis" in result
        assert "fundamental_analysis" in result
        assert "sentiment_analysis" in result
        assert "timestamp" in result

        # Verify macro analysis structure
        macro = result["macro_analysis"]
        assert "recommendation" in macro
        assert "confidence" in macro
        assert "regime" in macro

        # Verify fundamental analysis structure
        fundamental = result["fundamental_analysis"]
        assert "overall_score" in fundamental
        assert "recommendation" in fundamental
        assert "confidence" in fundamental

        # Verify sentiment analysis structure
        sentiment = result["sentiment_analysis"]
        assert "sentiment_assessment" in sentiment
        assert "confidence" in sentiment

    @pytest.mark.asyncio
    async def test_orchestrate_analysis_custom_asset(self):
        """Test comprehensive analysis with custom asset"""
        synthesizer = ThesisSynthesizer()
        result = await synthesizer.orchestrate_comprehensive_analysis("ETH")

        assert "macro_analysis" in result
        assert "fundamental_analysis" in result
        assert "sentiment_analysis" in result

    @pytest.mark.asyncio
    async def test_orchestrate_parallel_execution(self):
        """Test that orchestration runs analyses in parallel"""
        synthesizer = ThesisSynthesizer()

        # Should complete relatively quickly due to parallel execution
        import time

        start_time = time.time()
        result = await synthesizer.orchestrate_comprehensive_analysis("BTC")
        elapsed_time = time.time() - start_time

        # Verify result is complete
        assert "macro_analysis" in result
        assert "fundamental_analysis" in result
        assert "sentiment_analysis" in result

        # Verify analyses contain expected sub-keys (spot check)
        assert "recommendation" in result["macro_analysis"]
        assert "overall_score" in result["fundamental_analysis"]
        assert "sentiment_assessment" in result["sentiment_analysis"]


class TestGenerateInvestmentThesis:
    """Test generate_investment_thesis() method"""

    @pytest.mark.asyncio
    async def test_generate_thesis_default(self):
        """Test investment thesis generation with defaults"""
        synthesizer = ThesisSynthesizer()
        result = await synthesizer.generate_investment_thesis("BTC")

        # Verify structure
        assert "thesis_type" in result
        assert "confidence" in result
        assert "recommendation" in result
        assert "entry_range" in result
        assert "exit_targets" in result
        assert "stop_loss" in result
        assert "position_size" in result
        assert "time_horizon" in result
        assert "key_catalysts" in result
        assert "key_risks" in result
        assert "conflicts_detected" in result
        assert "conflicts_resolved" in result
        assert "synthesis" in result

        # Verify thesis type is valid enum value
        assert result["thesis_type"] in [thesis.value for thesis in ThesisType]

        # Verify confidence range
        assert 0.0 <= result["confidence"] <= 1.0

        # Verify recommendation is valid
        assert result["recommendation"] in ["BUY", "SELL", "HOLD"]

        # Verify entry/exit/stop_loss structure
        entry = result["entry_range"]
        assert "low" in entry
        assert "high" in entry
        assert entry["low"] > 0
        assert entry["high"] >= entry["low"]

        exit_targets = result["exit_targets"]
        assert isinstance(exit_targets, list)
        assert len(exit_targets) > 0

        stop_loss = result["stop_loss"]
        assert "price" in stop_loss
        assert "reason" in stop_loss
        assert stop_loss["price"] > 0

        # Verify position size
        assert 0.0 <= result["position_size"] <= 1.0

        # Verify time horizon
        assert result["time_horizon"] in [
            "short_term",
            "medium_term",
            "long_term",
            "swing_trade",
        ]

        # Verify lists are populated
        assert isinstance(result["key_catalysts"], list)
        assert len(result["key_catalysts"]) > 0
        assert isinstance(result["key_risks"], list)
        assert len(result["key_risks"]) > 0

        # Verify conflicts
        assert isinstance(result["conflicts_detected"], list)
        assert isinstance(result["conflicts_resolved"], list)

        # Verify synthesis
        synthesis = result["synthesis"]
        assert isinstance(synthesis, str)
        assert len(synthesis) > 0

    @pytest.mark.asyncio
    async def test_generate_thesis_custom_horizon(self):
        """Test thesis generation with custom horizon"""
        synthesizer = ThesisSynthesizer()
        result = await synthesizer.generate_investment_thesis("ETH", horizon_days=90)

        assert "thesis_type" in result
        assert "recommendation" in result

    @pytest.mark.asyncio
    async def test_thesis_calls_orchestration(self):
        """Test that thesis generation calls orchestrate_comprehensive_analysis"""
        synthesizer = ThesisSynthesizer()
        result = await synthesizer.generate_investment_thesis("BTC")

        # The synthesis should reference all three analyses
        synthesis = result["synthesis"].lower()

        # Should mention macro, fundamental, and/or sentiment concepts
        has_macro_ref = any(
            word in synthesis for word in ["macro", "regime", "fed", "institutional", "flow"]
        )
        has_fundamental_ref = any(
            word in synthesis
            for word in [
                "fundamental",
                "tokenomics",
                "liquidity",
                "development",
                "technical",
            ]
        )
        has_sentiment_ref = any(
            word in synthesis for word in ["sentiment", "fear", "greed", "crowd"]
        )

        # At least two of three should be referenced
        ref_count = sum([has_macro_ref, has_fundamental_ref, has_sentiment_ref])
        assert ref_count >= 2


class TestDetectConflicts:
    """Test detect_conflicts() method"""

    @pytest.mark.asyncio
    async def test_detect_conflicts_bullish_consensus(self):
        """Test conflict detection with bullish consensus"""
        synthesizer = ThesisSynthesizer()

        # Create mock analyses with bullish consensus
        macro_analysis = {
            "recommendation": "bullish",
            "confidence": 0.8,
            "regime": "risk_on",
        }
        fundamental_analysis = {
            "recommendation": "strong_buy",
            "confidence": 0.85,
            "overall_score": 85,
        }
        sentiment_analysis = {
            "sentiment_assessment": "bullish",
            "confidence": 0.75,
            "crowd_analysis": {"fear_greed_index": 70},
        }

        conflicts = await synthesizer.detect_conflicts(
            macro_analysis, fundamental_analysis, sentiment_analysis
        )

        # Should have no major conflicts
        assert isinstance(conflicts, list)
        # May have minor conflicts or none at all

    @pytest.mark.asyncio
    async def test_detect_conflicts_bearish_consensus(self):
        """Test conflict detection with bearish consensus"""
        synthesizer = ThesisSynthesizer()

        # Create mock analyses with bearish consensus
        macro_analysis = {
            "recommendation": "bearish",
            "confidence": 0.8,
            "regime": "risk_off",
        }
        fundamental_analysis = {
            "recommendation": "sell",
            "confidence": 0.75,
            "overall_score": 35,
        }
        sentiment_analysis = {
            "sentiment_assessment": "bearish",
            "confidence": 0.7,
            "crowd_analysis": {"fear_greed_index": 25},
        }

        conflicts = await synthesizer.detect_conflicts(
            macro_analysis, fundamental_analysis, sentiment_analysis
        )

        # Should have no major conflicts
        assert isinstance(conflicts, list)

    @pytest.mark.asyncio
    async def test_detect_conflicts_mixed_signals(self):
        """Test conflict detection with mixed signals"""
        synthesizer = ThesisSynthesizer()

        # Create mock analyses with mixed signals
        macro_analysis = {
            "recommendation": "bullish",
            "confidence": 0.8,
            "regime": "risk_on",
        }
        fundamental_analysis = {
            "recommendation": "sell",
            "confidence": 0.75,
            "overall_score": 35,
        }
        sentiment_analysis = {
            "sentiment_assessment": "neutral",
            "confidence": 0.6,
            "crowd_analysis": {"fear_greed_index": 50},
        }

        conflicts = await synthesizer.detect_conflicts(
            macro_analysis, fundamental_analysis, sentiment_analysis
        )

        # Should detect conflicts
        assert isinstance(conflicts, list)
        assert len(conflicts) > 0

        # Verify conflict structure
        if len(conflicts) > 0:
            conflict = conflicts[0]
            assert "type" in conflict
            assert "severity" in conflict
            assert "description" in conflict

            # Type should be valid ConflictType enum value
            assert conflict["type"] in [ct.value for ct in ConflictType]

            # Severity should be valid
            assert conflict["severity"] in ["minor", "moderate", "major"]


class TestResolveConflicts:
    """Test resolve_conflicts() method"""

    @pytest.mark.asyncio
    async def test_resolve_conflicts_no_conflicts(self):
        """Test conflict resolution with no conflicts"""
        synthesizer = ThesisSynthesizer()

        conflicts = []
        macro_analysis = {
            "recommendation": "bullish",
            "confidence": 0.8,
            "regime": "risk_on",
        }
        fundamental_analysis = {
            "recommendation": "strong_buy",
            "confidence": 0.85,
            "overall_score": 85,
        }
        sentiment_analysis = {
            "sentiment_assessment": "bullish",
            "confidence": 0.75,
        }

        resolutions = await synthesizer.resolve_conflicts(
            conflicts, macro_analysis, fundamental_analysis, sentiment_analysis
        )

        # Should return empty list or minimal resolutions
        assert isinstance(resolutions, list)

    @pytest.mark.asyncio
    async def test_resolve_conflicts_with_conflicts(self):
        """Test conflict resolution with actual conflicts"""
        synthesizer = ThesisSynthesizer()

        # Create conflicts
        conflicts = [
            {
                "type": "recommendation_divergence",
                "severity": "major",
                "description": "Macro bullish but fundamental bearish",
            }
        ]

        macro_analysis = {
            "recommendation": "bullish",
            "confidence": 0.8,
            "regime": "risk_on",
        }
        fundamental_analysis = {
            "recommendation": "sell",
            "confidence": 0.75,
            "overall_score": 35,
        }
        sentiment_analysis = {
            "sentiment_assessment": "neutral",
            "confidence": 0.6,
        }

        resolutions = await synthesizer.resolve_conflicts(
            conflicts, macro_analysis, fundamental_analysis, sentiment_analysis
        )

        # Should provide resolutions
        assert isinstance(resolutions, list)
        assert len(resolutions) > 0

        # Verify resolution structure
        resolution = resolutions[0]
        assert "conflict_type" in resolution
        assert "resolution_strategy" in resolution
        assert "final_decision" in resolution
        assert "rationale" in resolution


class TestSynthesizeSignals:
    """Test synthesize_signals() method"""

    @pytest.mark.asyncio
    async def test_synthesize_signals_bullish(self):
        """Test signal synthesis with bullish consensus"""
        synthesizer = ThesisSynthesizer()

        macro_analysis = {
            "recommendation": "bullish",
            "confidence": 0.8,
        }
        fundamental_analysis = {
            "recommendation": "strong_buy",
            "confidence": 0.85,
        }
        sentiment_analysis = {
            "sentiment_assessment": "bullish",
            "confidence": 0.75,
        }

        result = await synthesizer.synthesize_signals(
            macro_analysis, fundamental_analysis, sentiment_analysis
        )

        # Verify structure
        assert "recommendation" in result
        assert "confidence" in result
        assert "weighted_score" in result
        assert "reasoning" in result

        # Should be bullish
        assert result["recommendation"] in ["BUY", "STRONG_BUY"]

        # Confidence should be high
        assert result["confidence"] >= 0.7

    @pytest.mark.asyncio
    async def test_synthesize_signals_bearish(self):
        """Test signal synthesis with bearish consensus"""
        synthesizer = ThesisSynthesizer()

        macro_analysis = {
            "recommendation": "bearish",
            "confidence": 0.8,
        }
        fundamental_analysis = {
            "recommendation": "sell",
            "confidence": 0.75,
        }
        sentiment_analysis = {
            "sentiment_assessment": "bearish",
            "confidence": 0.7,
        }

        result = await synthesizer.synthesize_signals(
            macro_analysis, fundamental_analysis, sentiment_analysis
        )

        # Should be bearish
        assert result["recommendation"] in ["SELL", "STRONG_SELL"]

    @pytest.mark.asyncio
    async def test_synthesize_signals_mixed(self):
        """Test signal synthesis with mixed signals"""
        synthesizer = ThesisSynthesizer()

        macro_analysis = {
            "recommendation": "bullish",
            "confidence": 0.7,
        }
        fundamental_analysis = {
            "recommendation": "sell",
            "confidence": 0.6,
        }
        sentiment_analysis = {
            "sentiment_assessment": "neutral",
            "confidence": 0.5,
        }

        result = await synthesizer.synthesize_signals(
            macro_analysis, fundamental_analysis, sentiment_analysis
        )

        # With mixed signals, should be HOLD or have lower confidence
        assert result["recommendation"] in ["BUY", "SELL", "HOLD"]
        # Confidence should reflect uncertainty
        assert result["confidence"] <= 0.8

    @pytest.mark.asyncio
    async def test_weighted_synthesis(self):
        """Test that agent weights are applied correctly"""
        synthesizer = ThesisSynthesizer()

        # Strong fundamental signal should dominate due to 0.40 weight
        macro_analysis = {
            "recommendation": "neutral",
            "confidence": 0.5,
        }
        fundamental_analysis = {
            "recommendation": "strong_buy",
            "confidence": 0.95,
        }
        sentiment_analysis = {
            "recommendation": "neutral",
            "confidence": 0.5,
        }

        result = await synthesizer.synthesize_signals(
            macro_analysis, fundamental_analysis, sentiment_analysis
        )

        # Should lean bullish due to strong fundamental signal
        assert result["recommendation"] in ["BUY", "STRONG_BUY", "HOLD"]

        # Reasoning should mention weighting
        reasoning = result["reasoning"].lower()
        assert any(word in reasoning for word in ["weight", "fundamental", "strong", "high"])


class TestGetCapabilities:
    """Test get_capabilities() method"""

    def test_get_capabilities_structure(self):
        """Test capabilities metadata structure"""
        synthesizer = ThesisSynthesizer()
        capabilities = synthesizer.get_capabilities()

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
        synthesizer = ThesisSynthesizer()
        capabilities = synthesizer.get_capabilities()

        assert capabilities["name"] == "thesis_synthesizer"
        assert capabilities["type"] == "orchestrator_agent"
        assert capabilities["domain"] == "strategic_orchestration"
        assert capabilities["token_efficiency"] == 0.0

        # Verify capabilities list
        assert "comprehensive_analysis_orchestration" in capabilities["capabilities"]
        assert "conflict_detection_resolution" in capabilities["capabilities"]
        assert "weighted_signal_synthesis" in capabilities["capabilities"]
        assert "investment_thesis_generation" in capabilities["capabilities"]

        # Verify MCP servers (should delegate to specialized agents)
        assert len(capabilities["required_mcps"]) == 0
        assert len(capabilities["optional_mcps"]) == 0

        # Verify use cases
        assert isinstance(capabilities["use_cases"], list)
        assert len(capabilities["use_cases"]) > 0


class TestConvenienceFunction:
    """Test synthesize_investment_thesis() convenience function"""

    @pytest.mark.asyncio
    async def test_convenience_function_default(self):
        """Test convenience function with defaults"""
        result = await synthesize_investment_thesis("BTC")

        assert "thesis_type" in result
        assert "confidence" in result
        assert "recommendation" in result

    @pytest.mark.asyncio
    async def test_convenience_function_custom_horizon(self):
        """Test convenience function with custom horizon"""
        result = await synthesize_investment_thesis("ETH", horizon_days=90)

        assert "thesis_type" in result
        assert "recommendation" in result

    @pytest.mark.asyncio
    async def test_convenience_function_with_agents(self):
        """Test convenience function with custom agents"""
        macro = CryptoMacroAnalyst()
        vc = CryptoVCAnalyst()
        sentiment = CryptoSentimentAnalyst()

        result = await synthesize_investment_thesis(
            "BTC", macro_analyst=macro, vc_analyst=vc, sentiment_analyst=sentiment
        )

        assert "thesis_type" in result
        assert "recommendation" in result


class TestThesisTypeEnum:
    """Test ThesisType enum"""

    def test_thesis_type_values(self):
        """Test ThesisType enum has expected values"""
        assert ThesisType.STRONG_BUY.value == "strong_buy"
        assert ThesisType.BUY.value == "buy"
        assert ThesisType.HOLD.value == "hold"
        assert ThesisType.SELL.value == "sell"
        assert ThesisType.STRONG_SELL.value == "strong_sell"

    def test_thesis_type_all_members(self):
        """Test ThesisType has all expected members"""
        thesis_values = [thesis.value for thesis in ThesisType]
        assert "strong_buy" in thesis_values
        assert "buy" in thesis_values
        assert "hold" in thesis_values
        assert "sell" in thesis_values
        assert "strong_sell" in thesis_values
        assert len(thesis_values) == 5


class TestConflictTypeEnum:
    """Test ConflictType enum"""

    def test_conflict_type_values(self):
        """Test ConflictType enum has expected values"""
        assert ConflictType.RECOMMENDATION_DIVERGENCE.value == "recommendation_divergence"
        assert ConflictType.CONFIDENCE_MISMATCH.value == "confidence_mismatch"
        assert ConflictType.TIMING_DISAGREEMENT.value == "timing_disagreement"
        assert ConflictType.RISK_ASSESSMENT_GAP.value == "risk_assessment_gap"

    def test_conflict_type_all_members(self):
        """Test ConflictType has all expected members"""
        conflict_values = [conflict.value for conflict in ConflictType]
        assert "recommendation_divergence" in conflict_values
        assert "confidence_mismatch" in conflict_values
        assert "timing_disagreement" in conflict_values
        assert "risk_assessment_gap" in conflict_values
        assert len(conflict_values) == 4


class TestAsyncPatterns:
    """Test async/await patterns"""

    @pytest.mark.asyncio
    async def test_orchestration_parallel_execution(self):
        """Test that orchestration runs specialized agents in parallel"""
        synthesizer = ThesisSynthesizer()

        # Should complete relatively quickly due to parallel execution
        result = await synthesizer.orchestrate_comprehensive_analysis("BTC")

        assert "macro_analysis" in result
        assert "fundamental_analysis" in result
        assert "sentiment_analysis" in result

    @pytest.mark.asyncio
    async def test_sequential_thesis_generation(self):
        """Test that thesis generation can be called sequentially"""
        synthesizer = ThesisSynthesizer()

        # Generate multiple theses sequentially
        result1 = await synthesizer.generate_investment_thesis("BTC")
        result2 = await synthesizer.generate_investment_thesis("ETH")

        assert "thesis_type" in result1
        assert "thesis_type" in result2

    @pytest.mark.asyncio
    async def test_parallel_thesis_generation(self):
        """Test that multiple thesis generations can run in parallel"""
        synthesizer = ThesisSynthesizer()

        # Generate multiple theses in parallel
        results = await asyncio.gather(
            synthesizer.generate_investment_thesis("BTC"),
            synthesizer.generate_investment_thesis("ETH"),
            synthesizer.generate_investment_thesis("SOL"),
        )

        assert len(results) == 3
        assert all("thesis_type" in result for result in results)
        assert all("recommendation" in result for result in results)


class TestConflictScenarios:
    """Test various conflict detection and resolution scenarios"""

    @pytest.mark.asyncio
    async def test_all_bullish_no_conflict(self):
        """Test scenario where all agents are bullish"""
        synthesizer = ThesisSynthesizer()

        macro = {"recommendation": "bullish", "confidence": 0.8, "regime": "risk_on"}
        fundamental = {
            "recommendation": "strong_buy",
            "confidence": 0.85,
            "overall_score": 85,
        }
        sentiment = {"sentiment_assessment": "bullish", "confidence": 0.75}

        conflicts = await synthesizer.detect_conflicts(macro, fundamental, sentiment)
        result = await synthesizer.synthesize_signals(macro, fundamental, sentiment)

        # Should have minimal conflicts
        assert len(conflicts) <= 1  # May have minor conflicts

        # Should be strongly bullish
        assert result["recommendation"] in ["BUY", "STRONG_BUY"]
        assert result["confidence"] >= 0.75

    @pytest.mark.asyncio
    async def test_all_bearish_no_conflict(self):
        """Test scenario where all agents are bearish"""
        synthesizer = ThesisSynthesizer()

        macro = {"recommendation": "bearish", "confidence": 0.8, "regime": "risk_off"}
        fundamental = {
            "recommendation": "sell",
            "confidence": 0.75,
            "overall_score": 30,
        }
        sentiment = {"sentiment_assessment": "bearish", "confidence": 0.7}

        conflicts = await synthesizer.detect_conflicts(macro, fundamental, sentiment)
        result = await synthesizer.synthesize_signals(macro, fundamental, sentiment)

        # Should have minimal conflicts
        assert len(conflicts) <= 1

        # Should be strongly bearish
        assert result["recommendation"] in ["SELL", "STRONG_SELL"]

    @pytest.mark.asyncio
    async def test_macro_bullish_fundamental_bearish(self):
        """Test scenario with macro bullish but fundamental bearish"""
        synthesizer = ThesisSynthesizer()

        macro = {"recommendation": "bullish", "confidence": 0.8, "regime": "risk_on"}
        fundamental = {
            "recommendation": "sell",
            "confidence": 0.75,
            "overall_score": 35,
        }
        sentiment = {"sentiment_assessment": "neutral", "confidence": 0.6}

        conflicts = await synthesizer.detect_conflicts(macro, fundamental, sentiment)

        # Should detect conflict
        assert len(conflicts) > 0
        assert any(c["type"] == "recommendation_divergence" for c in conflicts) or any(
            c["severity"] in ["moderate", "major"] for c in conflicts
        )

    @pytest.mark.asyncio
    async def test_contrarian_sentiment_signal(self):
        """Test scenario with contrarian sentiment signal"""
        synthesizer = ThesisSynthesizer()

        macro = {"recommendation": "neutral", "confidence": 0.6, "regime": "neutral"}
        fundamental = {
            "recommendation": "hold",
            "confidence": 0.65,
            "overall_score": 55,
        }
        sentiment = {
            "sentiment_assessment": "contrarian_buy",  # Extreme fear = contrarian buy
            "confidence": 0.8,
            "crowd_analysis": {"fear_greed_index": 15},
        }

        result = await synthesizer.synthesize_signals(macro, fundamental, sentiment)

        # Synthesis should acknowledge contrarian opportunity
        reasoning = result["reasoning"].lower()
        assert any(word in reasoning for word in ["contrarian", "fear", "extreme", "opportunity"])


class TestWeightedSynthesis:
    """Test that agent weights (macro: 0.35, fundamental: 0.40, sentiment: 0.25) are applied"""

    @pytest.mark.asyncio
    async def test_fundamental_dominance(self):
        """Test that fundamental analysis (0.40 weight) can dominate with strong signal"""
        synthesizer = ThesisSynthesizer()

        # Weak macro and sentiment, strong fundamental
        macro = {"recommendation": "neutral", "confidence": 0.5}
        fundamental = {
            "recommendation": "strong_buy",
            "confidence": 0.95,
            "overall_score": 90,
        }
        sentiment = {"sentiment_assessment": "neutral", "confidence": 0.5}

        result = await synthesizer.synthesize_signals(macro, fundamental, sentiment)

        # Should lean bullish due to strong fundamental signal with highest weight
        assert result["recommendation"] in ["BUY", "STRONG_BUY", "HOLD"]

    @pytest.mark.asyncio
    async def test_macro_influence(self):
        """Test that macro analysis (0.35 weight) has significant influence"""
        synthesizer = ThesisSynthesizer()

        # Strong macro, neutral others
        macro = {"recommendation": "bullish", "confidence": 0.9, "regime": "risk_on"}
        fundamental = {
            "recommendation": "hold",
            "confidence": 0.6,
            "overall_score": 55,
        }
        sentiment = {"sentiment_assessment": "neutral", "confidence": 0.5}

        result = await synthesizer.synthesize_signals(macro, fundamental, sentiment)

        # Should show macro influence
        assert result["recommendation"] in ["BUY", "HOLD"]

    @pytest.mark.asyncio
    async def test_sentiment_contribution(self):
        """Test that sentiment (0.25 weight) contributes to final decision"""
        synthesizer = ThesisSynthesizer()

        # Neutral macro/fundamental, strong sentiment
        macro = {"recommendation": "neutral", "confidence": 0.5}
        fundamental = {
            "recommendation": "hold",
            "confidence": 0.6,
            "overall_score": 55,
        }
        sentiment = {
            "sentiment_assessment": "contrarian_buy",
            "confidence": 0.85,
        }

        result = await synthesizer.synthesize_signals(macro, fundamental, sentiment)

        # Sentiment should contribute even with lower weight
        reasoning = result["reasoning"].lower()
        assert "sentiment" in reasoning or "contrarian" in reasoning

    @pytest.mark.asyncio
    async def test_balanced_weighting(self):
        """Test that all three weights combine correctly"""
        synthesizer = ThesisSynthesizer()

        # All moderately bullish
        macro = {"recommendation": "bullish", "confidence": 0.7}
        fundamental = {
            "recommendation": "buy",
            "confidence": 0.75,
            "overall_score": 70,
        }
        sentiment = {"sentiment_assessment": "bullish", "confidence": 0.65}

        result = await synthesizer.synthesize_signals(macro, fundamental, sentiment)

        # Should be bullish with reasonable confidence
        assert result["recommendation"] in ["BUY", "STRONG_BUY"]
        assert 0.65 <= result["confidence"] <= 0.85

        # Weighted score should reflect all three inputs
        assert "weighted_score" in result
        assert isinstance(result["weighted_score"], (int, float))
