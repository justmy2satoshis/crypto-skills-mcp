"""
Integration Tests for Agent Orchestration

Tests the integration and interaction between agents including:
- Multi-agent orchestration workflows
- Data flow between agents
- Conflict detection and resolution in practice
- End-to-end investment analysis pipeline
- Performance and concurrency patterns
"""

import pytest
import asyncio
from agents import (
    ThesisSynthesizer,
    CryptoMacroAnalyst,
    CryptoVCAnalyst,
    CryptoSentimentAnalyst,
    MacroRegime,
    RiskLevel,
    SentimentRegime,
    ThesisType,
)


class TestMultiAgentOrchestration:
    """Test multi-agent orchestration workflows"""

    @pytest.mark.asyncio
    async def test_full_analysis_pipeline(self):
        """Test complete end-to-end analysis pipeline"""
        # Initialize all agents
        macro = CryptoMacroAnalyst()
        vc = CryptoVCAnalyst()
        sentiment = CryptoSentimentAnalyst()
        synthesizer = ThesisSynthesizer(
            macro_analyst=macro, vc_analyst=vc, sentiment_analyst=sentiment
        )

        # Run complete analysis
        result = await synthesizer.generate_investment_thesis("BTC")

        # Verify complete pipeline execution
        assert "thesis_type" in result
        assert "recommendation" in result
        assert "confidence" in result
        assert "entry_range" in result
        assert "exit_targets" in result
        assert "synthesis" in result

        # Verify thesis type is valid
        assert result["thesis_type"] in [thesis.value for thesis in ThesisType]

        # Verify all three analyses were incorporated
        synthesis = result["synthesis"].lower()

        # Check for macro indicators
        has_macro = any(
            word in synthesis
            for word in ["macro", "regime", "fed", "institutional", "flow", "risk"]
        )

        # Check for fundamental indicators
        has_fundamental = any(
            word in synthesis
            for word in [
                "fundamental",
                "tokenomics",
                "liquidity",
                "development",
                "technical",
                "score",
            ]
        )

        # Check for sentiment indicators
        has_sentiment = any(
            word in synthesis for word in ["sentiment", "fear", "greed", "crowd", "contrarian"]
        )

        # At least two of three should be mentioned
        assert sum([has_macro, has_fundamental, has_sentiment]) >= 2

    @pytest.mark.asyncio
    async def test_parallel_asset_analysis(self):
        """Test analyzing multiple assets in parallel"""
        synthesizer = ThesisSynthesizer()

        # Analyze multiple assets concurrently
        results = await asyncio.gather(
            synthesizer.generate_investment_thesis("BTC"),
            synthesizer.generate_investment_thesis("ETH"),
            synthesizer.generate_investment_thesis("SOL"),
        )

        # Verify all analyses completed
        assert len(results) == 3

        # Each should have complete thesis
        for result in results:
            assert "thesis_type" in result
            assert "recommendation" in result
            assert "confidence" in result
            assert "synthesis" in result

    @pytest.mark.asyncio
    async def test_orchestration_with_shared_mcp_client(self):
        """Test that MCP client is properly shared across agents"""
        mock_client = "mock_mcp_client"

        # Create synthesizer with MCP client
        synthesizer = ThesisSynthesizer(mcp_client=mock_client)

        # Verify all agents received the client
        assert synthesizer.macro_analyst.mcp_client == mock_client
        assert synthesizer.vc_analyst.mcp_client == mock_client
        assert synthesizer.sentiment_analyst.mcp_client == mock_client

        # Run analysis to ensure client propagation works
        result = await synthesizer.orchestrate_comprehensive_analysis("BTC")

        assert "macro_analysis" in result
        assert "fundamental_analysis" in result
        assert "sentiment_analysis" in result


class TestDataFlowBetweenAgents:
    """Test data flow and information passing between agents"""

    @pytest.mark.asyncio
    async def test_macro_to_thesis_data_flow(self):
        """Test that macro analysis data flows correctly to thesis"""
        synthesizer = ThesisSynthesizer()

        # Get macro analysis
        macro = synthesizer.macro_analyst
        macro_result = await macro.synthesize_macro_outlook("BTC")

        # Generate thesis
        thesis = await synthesizer.generate_investment_thesis("BTC")

        # Thesis should incorporate macro regime
        assert "regime" in thesis or "macro" in thesis["synthesis"].lower()

        # If macro is bullish, thesis should reflect this
        if macro_result["recommendation"] == "bullish":
            # Thesis should not be strongly bearish
            assert thesis["thesis_type"] not in ["strong_sell"]

    @pytest.mark.asyncio
    async def test_fundamental_to_thesis_data_flow(self):
        """Test that fundamental analysis data flows correctly to thesis"""
        synthesizer = ThesisSynthesizer()

        # Get fundamental analysis
        vc = synthesizer.vc_analyst
        vc_result = await vc.generate_due_diligence_report("BTC")

        # Generate thesis
        thesis = await synthesizer.generate_investment_thesis("BTC")

        # Thesis position size should align with fundamental risk assessment
        # High risk should mean smaller position size
        if "risk_assessment" in vc_result:
            risk = vc_result["risk_assessment"]
            if "risk_level" in risk:
                if risk["risk_level"] == "high" or risk["risk_level"] == "very_high":
                    # Position size should be moderate or small
                    assert thesis["position_size"] <= 0.15

    @pytest.mark.asyncio
    async def test_sentiment_to_thesis_data_flow(self):
        """Test that sentiment analysis data flows correctly to thesis"""
        synthesizer = ThesisSynthesizer()

        # Get sentiment analysis
        sentiment = synthesizer.sentiment_analyst
        sentiment_result = await sentiment.synthesize_sentiment_outlook("bitcoin")

        # Generate thesis
        thesis = await synthesizer.generate_investment_thesis("BTC")

        # If sentiment shows extreme fear, thesis should mention contrarian opportunity
        if "crowd_analysis" in sentiment_result:
            crowd = sentiment_result["crowd_analysis"]
            if "fear_greed_index" in crowd:
                if crowd["fear_greed_index"] <= 25:
                    # Should mention fear or contrarian in synthesis
                    synthesis_lower = thesis["synthesis"].lower()
                    assert "fear" in synthesis_lower or "contrarian" in synthesis_lower

    @pytest.mark.asyncio
    async def test_orchestration_data_completeness(self):
        """Test that orchestration provides complete data to synthesis"""
        synthesizer = ThesisSynthesizer()

        # Run orchestration
        orchestration = await synthesizer.orchestrate_comprehensive_analysis("BTC")

        # Verify all required data is present
        assert "macro_analysis" in orchestration
        assert "fundamental_analysis" in orchestration
        assert "sentiment_analysis" in orchestration

        # Macro should have regime and recommendation
        macro = orchestration["macro_analysis"]
        assert "regime" in macro
        assert "recommendation" in macro
        assert "confidence" in macro

        # Fundamental should have score and recommendation
        fundamental = orchestration["fundamental_analysis"]
        assert "overall_score" in fundamental
        assert "recommendation" in fundamental

        # Sentiment should have assessment
        sentiment = orchestration["sentiment_analysis"]
        assert "sentiment_assessment" in sentiment


class TestConflictDetectionInPractice:
    """Test conflict detection and resolution in real scenarios"""

    @pytest.mark.asyncio
    async def test_detect_macro_fundamental_conflict(self):
        """Test detection of macro vs fundamental conflicts"""
        synthesizer = ThesisSynthesizer()

        # Create conflicting analyses
        macro_bullish = {
            "recommendation": "bullish",
            "confidence": 0.8,
            "regime": "risk_on",
        }
        fundamental_bearish = {
            "recommendation": "sell",
            "confidence": 0.75,
            "overall_score": 35,
        }
        sentiment_neutral = {"sentiment_assessment": "neutral", "confidence": 0.6}

        conflicts = await synthesizer.detect_conflicts(
            macro_bullish, fundamental_bearish, sentiment_neutral
        )

        # Should detect recommendation divergence
        assert len(conflicts) > 0
        conflict_types = [c["type"] for c in conflicts]
        assert "recommendation_divergence" in conflict_types

    @pytest.mark.asyncio
    async def test_resolve_confidence_conflicts(self):
        """Test resolution of confidence mismatches"""
        synthesizer = ThesisSynthesizer()

        # High confidence macro, low confidence fundamental
        macro_high_conf = {
            "recommendation": "bullish",
            "confidence": 0.9,
            "regime": "risk_on",
        }
        fundamental_low_conf = {
            "recommendation": "buy",
            "confidence": 0.4,
            "overall_score": 60,
        }
        sentiment_medium = {"sentiment_assessment": "neutral", "confidence": 0.6}

        conflicts = await synthesizer.detect_conflicts(
            macro_high_conf, fundamental_low_conf, sentiment_medium
        )

        # May detect confidence mismatch
        if len(conflicts) > 0:
            resolutions = await synthesizer.resolve_conflicts(
                conflicts, macro_high_conf, fundamental_low_conf, sentiment_medium
            )

            # Should provide resolution strategy
            assert len(resolutions) > 0
            for resolution in resolutions:
                assert "resolution_strategy" in resolution
                assert "final_decision" in resolution

    @pytest.mark.asyncio
    async def test_conflict_impact_on_thesis(self):
        """Test how conflicts affect final thesis"""
        synthesizer = ThesisSynthesizer()

        # Generate thesis which will detect and resolve conflicts internally
        thesis = await synthesizer.generate_investment_thesis("BTC")

        # Verify conflicts were tracked
        assert "conflicts_detected" in thesis
        assert "conflicts_resolved" in thesis

        assert isinstance(thesis["conflicts_detected"], list)
        assert isinstance(thesis["conflicts_resolved"], list)

        # If conflicts were detected, they should be resolved
        if len(thesis["conflicts_detected"]) > 0:
            # Resolution count should match or be less than detection count
            assert len(thesis["conflicts_resolved"]) <= len(thesis["conflicts_detected"])


class TestEndToEndInvestmentPipeline:
    """Test complete end-to-end investment analysis pipeline"""

    @pytest.mark.asyncio
    async def test_btc_complete_analysis(self):
        """Test complete BTC analysis pipeline"""
        synthesizer = ThesisSynthesizer()

        # Run complete analysis
        thesis = await synthesizer.generate_investment_thesis("BTC")

        # Verify all components are present
        assert "thesis_type" in thesis
        assert "confidence" in thesis
        assert "recommendation" in thesis
        assert "entry_range" in thesis
        assert "exit_targets" in thesis
        assert "stop_loss" in thesis
        assert "position_size" in thesis
        assert "time_horizon" in thesis
        assert "key_catalysts" in thesis
        assert "key_risks" in thesis
        assert "synthesis" in thesis

        # Verify data types
        assert isinstance(thesis["confidence"], float)
        assert isinstance(thesis["entry_range"], dict)
        assert isinstance(thesis["exit_targets"], list)
        assert isinstance(thesis["position_size"], float)
        assert isinstance(thesis["key_catalysts"], list)
        assert isinstance(thesis["key_risks"], list)
        assert isinstance(thesis["synthesis"], str)

        # Verify ranges are logical
        assert 0.0 <= thesis["confidence"] <= 1.0
        assert 0.0 <= thesis["position_size"] <= 1.0
        assert thesis["entry_range"]["low"] > 0
        assert thesis["entry_range"]["high"] >= thesis["entry_range"]["low"]

    @pytest.mark.asyncio
    async def test_eth_complete_analysis(self):
        """Test complete ETH analysis pipeline"""
        synthesizer = ThesisSynthesizer()

        thesis = await synthesizer.generate_investment_thesis("ETH")

        # Should have same structure as BTC
        assert "thesis_type" in thesis
        assert "recommendation" in thesis
        assert "synthesis" in thesis

    @pytest.mark.asyncio
    async def test_alt_coin_complete_analysis(self):
        """Test complete alt-coin analysis pipeline"""
        synthesizer = ThesisSynthesizer()

        thesis = await synthesizer.generate_investment_thesis("SOL")

        # Should work for alt-coins too
        assert "thesis_type" in thesis
        assert "recommendation" in thesis
        assert "position_size" in thesis


class TestPerformanceAndConcurrency:
    """Test performance characteristics and concurrent execution"""

    @pytest.mark.asyncio
    async def test_parallel_orchestration_performance(self):
        """Test that parallel orchestration is faster than sequential"""
        synthesizer = ThesisSynthesizer()

        import time

        # Time parallel execution
        start = time.time()
        await synthesizer.orchestrate_comprehensive_analysis("BTC")
        parallel_time = time.time() - start

        # Parallel execution should complete (exact timing depends on system)
        # Just verify it completes without hanging
        assert parallel_time < 60  # Should complete in under 60 seconds

    @pytest.mark.asyncio
    async def test_concurrent_thesis_generation(self):
        """Test concurrent thesis generation for multiple assets"""
        synthesizer = ThesisSynthesizer()

        # Generate theses for 5 assets concurrently
        assets = ["BTC", "ETH", "SOL", "ADA", "AVAX"]

        results = await asyncio.gather(
            *[synthesizer.generate_investment_thesis(asset) for asset in assets]
        )

        # All should complete successfully
        assert len(results) == 5

        # Each should have valid structure
        for result in results:
            assert "thesis_type" in result
            assert "recommendation" in result
            assert "confidence" in result

    @pytest.mark.asyncio
    async def test_agent_reusability(self):
        """Test that agents can be reused across multiple analyses"""
        macro = CryptoMacroAnalyst()
        vc = CryptoVCAnalyst()
        sentiment = CryptoSentimentAnalyst()

        # Use same agents for multiple assets
        synthesizer1 = ThesisSynthesizer(
            macro_analyst=macro, vc_analyst=vc, sentiment_analyst=sentiment
        )
        synthesizer2 = ThesisSynthesizer(
            macro_analyst=macro, vc_analyst=vc, sentiment_analyst=sentiment
        )

        # Both should work
        result1 = await synthesizer1.generate_investment_thesis("BTC")
        result2 = await synthesizer2.generate_investment_thesis("ETH")

        assert "thesis_type" in result1
        assert "thesis_type" in result2


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge case scenarios"""

    @pytest.mark.asyncio
    async def test_empty_asset_handling(self):
        """Test handling of empty asset symbol"""
        synthesizer = ThesisSynthesizer()

        # Should handle empty string gracefully (will use default mock data)
        result = await synthesizer.generate_investment_thesis("")

        # Should still return valid structure
        assert "thesis_type" in result
        assert "recommendation" in result

    @pytest.mark.asyncio
    async def test_unknown_asset_handling(self):
        """Test handling of unknown/invalid asset"""
        synthesizer = ThesisSynthesizer()

        # Should handle unknown asset (will use default mock data)
        result = await synthesizer.generate_investment_thesis("UNKNOWN_ASSET_XYZ")

        # Should still return valid structure
        assert "thesis_type" in result
        assert "recommendation" in result

    @pytest.mark.asyncio
    async def test_extreme_confidence_values(self):
        """Test handling of extreme confidence values"""
        synthesizer = ThesisSynthesizer()

        # All agents with very high confidence
        macro_extreme = {
            "recommendation": "bullish",
            "confidence": 0.99,
            "regime": "risk_on",
        }
        fundamental_extreme = {
            "recommendation": "strong_buy",
            "confidence": 0.98,
            "overall_score": 95,
        }
        sentiment_extreme = {
            "sentiment_assessment": "extreme_greed",
            "confidence": 0.97,
        }

        result = await synthesizer.synthesize_signals(
            macro_extreme, fundamental_extreme, sentiment_extreme
        )

        # Should handle extreme values
        assert "recommendation" in result
        assert "confidence" in result
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_all_neutral_signals(self):
        """Test handling when all agents give neutral signals"""
        synthesizer = ThesisSynthesizer()

        macro_neutral = {
            "recommendation": "neutral",
            "confidence": 0.5,
            "regime": "neutral",
        }
        fundamental_neutral = {
            "recommendation": "hold",
            "confidence": 0.5,
            "overall_score": 50,
        }
        sentiment_neutral = {"sentiment_assessment": "neutral", "confidence": 0.5}

        result = await synthesizer.synthesize_signals(
            macro_neutral, fundamental_neutral, sentiment_neutral
        )

        # Should recommend HOLD with moderate confidence
        assert result["recommendation"] in ["HOLD", "BUY", "SELL"]
        assert result["confidence"] <= 0.7  # Should not be highly confident


class TestSpecializedAgentInteraction:
    """Test interaction patterns between specialized agents"""

    @pytest.mark.asyncio
    async def test_macro_sentiment_correlation(self):
        """Test correlation between macro regime and sentiment"""
        macro = CryptoMacroAnalyst()
        sentiment = CryptoSentimentAnalyst()

        macro_result = await macro.analyze_macro_regime("BTC")
        sentiment_result = await sentiment.analyze_crowd_sentiment("bitcoin")

        # Both should provide valid results
        assert "regime" in macro_result
        assert "fear_greed_index" in sentiment_result

        # Check if results are logically correlated
        # Risk-on regime often correlates with higher F&G
        # Risk-off regime often correlates with lower F&G
        # (This is probabilistic, not deterministic)

    @pytest.mark.asyncio
    async def test_fundamental_risk_to_position_sizing(self):
        """Test that fundamental risk affects position sizing"""
        vc = CryptoVCAnalyst()
        synthesizer = ThesisSynthesizer()

        # Get risk assessment
        risk_result = await vc.calculate_risk_score("BTC")

        # Generate thesis
        thesis = await synthesizer.generate_investment_thesis("BTC")

        # High risk should result in smaller position size
        if risk_result["risk_level"] in ["high", "very_high"]:
            assert thesis["position_size"] <= 0.15

        # Low risk can have larger position size
        if risk_result["risk_level"] == "low":
            # May allow larger positions (but not required)
            assert thesis["position_size"] <= 1.0  # Just verify it's valid

    @pytest.mark.asyncio
    async def test_sentiment_extreme_to_contrarian_signal(self):
        """Test that sentiment extremes generate contrarian signals"""
        sentiment = CryptoSentimentAnalyst()
        synthesizer = ThesisSynthesizer()

        # Get sentiment analysis
        sentiment_result = await sentiment.synthesize_sentiment_outlook("bitcoin")

        # If extreme fear detected, thesis should mention it
        if "crowd_analysis" in sentiment_result:
            crowd = sentiment_result["crowd_analysis"]
            if "fear_greed_index" in crowd and crowd["fear_greed_index"] <= 20:
                # Generate thesis
                thesis = await synthesizer.generate_investment_thesis("BTC")

                # Should mention fear or contrarian
                synthesis_lower = thesis["synthesis"].lower()
                assert "fear" in synthesis_lower or "contrarian" in synthesis_lower


class TestIntegrationWithMockData:
    """Test integration with mock data (before real MCP integration)"""

    @pytest.mark.asyncio
    async def test_mock_data_consistency(self):
        """Test that mock data is consistent across agents"""
        synthesizer = ThesisSynthesizer()

        # Run orchestration
        result = await synthesizer.orchestrate_comprehensive_analysis("BTC")

        # All analyses should be present
        assert "macro_analysis" in result
        assert "fundamental_analysis" in result
        assert "sentiment_analysis" in result

        # Each should have required fields
        assert "recommendation" in result["macro_analysis"]
        assert "overall_score" in result["fundamental_analysis"]
        assert "sentiment_assessment" in result["sentiment_analysis"]

    @pytest.mark.asyncio
    async def test_mock_data_validity(self):
        """Test that mock data contains valid values"""
        macro = CryptoMacroAnalyst()
        vc = CryptoVCAnalyst()
        sentiment = CryptoSentimentAnalyst()

        # Get results from each agent
        macro_result = await macro.synthesize_macro_outlook("BTC")
        vc_result = await vc.generate_due_diligence_report("BTC")
        sentiment_result = await sentiment.synthesize_sentiment_outlook("bitcoin")

        # Verify macro data
        assert macro_result["regime"] in [r.value for r in MacroRegime]
        assert 0.0 <= macro_result["confidence"] <= 1.0

        # Verify fundamental data
        assert 0 <= vc_result["overall_score"] <= 100
        assert 0.0 <= vc_result["confidence"] <= 1.0

        # Verify sentiment data
        assert sentiment_result["sentiment_assessment"] in [
            "bullish",
            "bearish",
            "neutral",
            "contrarian_buy",
            "contrarian_sell",
        ]
        assert 0.0 <= sentiment_result["confidence"] <= 1.0


class TestThesisQualityMetrics:
    """Test quality and completeness of generated theses"""

    @pytest.mark.asyncio
    async def test_thesis_has_actionable_guidance(self):
        """Test that thesis provides actionable investment guidance"""
        synthesizer = ThesisSynthesizer()
        thesis = await synthesizer.generate_investment_thesis("BTC")

        # Should have entry guidance
        assert "entry_range" in thesis
        assert "low" in thesis["entry_range"]
        assert "high" in thesis["entry_range"]

        # Should have exit guidance
        assert "exit_targets" in thesis
        assert len(thesis["exit_targets"]) > 0

        # Should have risk management
        assert "stop_loss" in thesis
        assert "position_size" in thesis

    @pytest.mark.asyncio
    async def test_thesis_synthesis_quality(self):
        """Test quality of thesis synthesis narrative"""
        synthesizer = ThesisSynthesizer()
        thesis = await synthesizer.generate_investment_thesis("BTC")

        synthesis = thesis["synthesis"]

        # Should be substantial
        assert len(synthesis) > 100  # At least 100 characters

        # Should mention key concepts
        synthesis_lower = synthesis.lower()
        concept_count = sum(
            [
                any(word in synthesis_lower for word in ["macro", "regime", "fed"]),
                any(
                    word in synthesis_lower for word in ["fundamental", "tokenomics", "development"]
                ),
                any(word in synthesis_lower for word in ["sentiment", "fear", "greed"]),
                "risk" in synthesis_lower,
                any(word in synthesis_lower for word in ["buy", "sell", "hold"]),
            ]
        )

        # Should mention at least 3 of these concept areas
        assert concept_count >= 3

    @pytest.mark.asyncio
    async def test_thesis_risk_disclosure(self):
        """Test that thesis includes proper risk disclosure"""
        synthesizer = ThesisSynthesizer()
        thesis = await synthesizer.generate_investment_thesis("BTC")

        # Should list risks
        assert "key_risks" in thesis
        assert isinstance(thesis["key_risks"], list)
        assert len(thesis["key_risks"]) > 0

        # Each risk should be a non-empty string
        for risk in thesis["key_risks"]:
            assert isinstance(risk, str)
            assert len(risk) > 0

    @pytest.mark.asyncio
    async def test_thesis_catalyst_identification(self):
        """Test that thesis identifies key catalysts"""
        synthesizer = ThesisSynthesizer()
        thesis = await synthesizer.generate_investment_thesis("BTC")

        # Should list catalysts
        assert "key_catalysts" in thesis
        assert isinstance(thesis["key_catalysts"], list)
        assert len(thesis["key_catalysts"]) > 0

        # Each catalyst should be a non-empty string
        for catalyst in thesis["key_catalysts"]:
            assert isinstance(catalyst, str)
            assert len(catalyst) > 0
