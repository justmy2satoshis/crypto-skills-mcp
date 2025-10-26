"""
Production Usage Examples for Crypto Skills MCP

Demonstrates how to use the Agent layer with real MCP client integration
for cryptocurrency investment analysis.
"""

import asyncio
from agents import (
    CryptoMacroAnalyst,
    CryptoVCAnalyst,
    CryptoSentimentAnalyst,
    ThesisSynthesizer,
    synthesize_investment_thesis,
)
from mcp_client import MCPClientWrapper


# ========================
# Example 1: Basic Bitcoin Analysis
# ========================


async def example_basic_btc_analysis():
    """
    Basic example: Analyze Bitcoin with all three specialized agents.
    """
    print("=" * 80)
    print("Example 1: Basic Bitcoin Analysis")
    print("=" * 80)

    # Initialize MCP client wrapper (pass actual MCP client in production)
    mcp_client = MCPClientWrapper()

    # Initialize specialized agents with MCP client
    macro = CryptoMacroAnalyst(mcp_client=mcp_client)
    vc = CryptoVCAnalyst(mcp_client=mcp_client)
    sentiment = CryptoSentimentAnalyst(mcp_client=mcp_client)

    # Run macro analysis
    print("\n1. Macro Analysis:")
    macro_result = await macro.synthesize_macro_outlook("BTC")
    print(f"   Regime: {macro_result['regime']}")
    print(f"   Recommendation: {macro_result['recommendation']}")
    print(f"   Confidence: {macro_result['confidence']:.2f}")

    # Run fundamental analysis
    print("\n2. Fundamental Analysis:")
    vc_result = await vc.generate_due_diligence_report("BTC")
    print(f"   Overall Score: {vc_result['overall_score']}/100")
    print(f"   Recommendation: {vc_result['recommendation']}")
    print(f"   Confidence: {vc_result['confidence']:.2f}")

    # Run sentiment analysis
    print("\n3. Sentiment Analysis:")
    sentiment_result = await sentiment.synthesize_sentiment_outlook("bitcoin")
    print(f"   Assessment: {sentiment_result['sentiment_assessment']}")
    print(f"   Confidence: {sentiment_result['confidence']:.2f}")

    print("\n" + "=" * 80)


# ========================
# Example 2: Complete Investment Thesis
# ========================


async def example_complete_investment_thesis():
    """
    Generate complete investment thesis using ThesisSynthesizer.
    """
    print("=" * 80)
    print("Example 2: Complete Investment Thesis")
    print("=" * 80)

    # Initialize MCP client
    mcp_client = MCPClientWrapper()

    # Initialize synthesizer (will auto-create specialized agents)
    synthesizer = ThesisSynthesizer(mcp_client=mcp_client)

    # Generate complete thesis
    print("\nGenerating investment thesis for Bitcoin...")
    thesis = await synthesizer.generate_investment_thesis("BTC", horizon_days=30)

    print(f"\nThesis Type: {thesis['thesis_type']}")
    print(f"Recommendation: {thesis['recommendation']}")
    print(f"Confidence: {thesis['confidence']:.2f}")

    print(f"\nEntry Range: ${thesis['entry_range']['low']:,.0f} - ${thesis['entry_range']['high']:,.0f}")
    print(f"Position Size: {thesis['position_size'] * 100:.1f}%")
    print(f"Time Horizon: {thesis['time_horizon']}")

    print(f"\nExit Targets:")
    for i, target in enumerate(thesis["exit_targets"], 1):
        print(f"   Target {i}: ${target['price']:,.0f} ({target['reasoning']})")

    print(f"\nStop Loss: ${thesis['stop_loss']['price']:,.0f}")
    print(f"   Reason: {thesis['stop_loss']['reason']}")

    print(f"\nKey Catalysts:")
    for catalyst in thesis["key_catalysts"]:
        print(f"   • {catalyst}")

    print(f"\nKey Risks:")
    for risk in thesis["key_risks"]:
        print(f"   • {risk}")

    if thesis["conflicts_detected"]:
        print(f"\nConflicts Detected: {len(thesis['conflicts_detected'])}")
        print(f"Conflicts Resolved: {len(thesis['conflicts_resolved'])}")

    print(f"\nExecutive Summary:")
    print(f"{thesis['synthesis'][:300]}...")

    print("\n" + "=" * 80)


# ========================
# Example 3: Multi-Asset Comparison
# ========================


async def example_multi_asset_comparison():
    """
    Compare investment opportunities across multiple assets.
    """
    print("=" * 80)
    print("Example 3: Multi-Asset Comparison")
    print("=" * 80)

    mcp_client = MCPClientWrapper()
    synthesizer = ThesisSynthesizer(mcp_client=mcp_client)

    # Analyze multiple assets in parallel
    assets = ["BTC", "ETH", "SOL"]
    print(f"\nAnalyzing {len(assets)} assets in parallel...")

    results = await asyncio.gather(
        *[synthesizer.generate_investment_thesis(asset) for asset in assets]
    )

    # Display comparison
    print("\n{:<8} {:<15} {:<12} {:<10} {:<15}".format(
        "Asset", "Thesis", "Confidence", "Position", "Horizon"
    ))
    print("-" * 70)

    for asset, result in zip(assets, results):
        print(
            "{:<8} {:<15} {:<12.2f} {:<10.1f}% {:<15}".format(
                asset,
                result["thesis_type"],
                result["confidence"],
                result["position_size"] * 100,
                result["time_horizon"],
            )
        )

    # Find best opportunity
    best_asset = max(zip(assets, results), key=lambda x: x[1]["confidence"])
    print(f"\nBest Opportunity: {best_asset[0]} (Confidence: {best_asset[1]['confidence']:.2f})")

    print("\n" + "=" * 80)


# ========================
# Example 4: Macro Regime Analysis
# ========================


async def example_macro_regime_analysis():
    """
    Deep dive into macro regime analysis.
    """
    print("=" * 80)
    print("Example 4: Macro Regime Analysis")
    print("=" * 80)

    mcp_client = MCPClientWrapper()
    macro = CryptoMacroAnalyst(mcp_client=mcp_client)

    # Analyze macro regime
    print("\n1. Current Macro Regime:")
    regime = await macro.analyze_macro_regime("BTC")
    print(f"   Regime: {regime['regime']}")
    print(f"   Score: {regime['regime_score']:.2f}")
    print(f"   Indicators:")
    for key, value in regime["regime_indicators"].items():
        print(f"      {key}: {value}")

    # Track institutional flows
    print("\n2. Institutional Flows:")
    flows = await macro.track_institutional_flows("BTC")
    print(f"   ETF Flows: ${flows['etf_flows']['total_flow_7d']:,.0f}")
    print(f"   Exchange Flows: {flows['exchange_flows']['net_flow']}")
    print(f"   Flow Signal: {flows['overall_flow_signal']}")

    # Analyze Fed impact
    print("\n3. Fed Policy Impact:")
    fed = await macro.analyze_fed_impact()
    print(f"   Policy Stance: {fed['policy_stance']}")
    print(f"   Rate Trajectory: {fed['rate_trajectory']}")
    print(f"   Liquidity Trend: {fed['liquidity_trend']}")
    print(f"   Crypto Impact: {fed['crypto_impact']}")

    # Assess risk sentiment
    print("\n4. Risk Sentiment:")
    risk = await macro.assess_risk_sentiment()
    print(f"   Risk Mode: {risk['risk_mode']}")
    print(f"   Correlation BTC/SPX: {risk['btc_correlation']['btc_spx']:.2f}")
    print(f"   VIX Level: {risk['volatility_index']['vix_level']:.1f}")

    print("\n" + "=" * 80)


# ========================
# Example 5: Fundamental Due Diligence
# ========================


async def example_fundamental_due_diligence():
    """
    Deep dive into fundamental analysis.
    """
    print("=" * 80)
    print("Example 5: Fundamental Due Diligence")
    print("=" * 80)

    mcp_client = MCPClientWrapper()
    vc = CryptoVCAnalyst(mcp_client=mcp_client)

    # Tokenomics analysis
    print("\n1. Tokenomics Analysis:")
    tokenomics = await vc.analyze_tokenomics("BTC")
    print(f"   Overall Score: {tokenomics['overall_score']}/100")
    print(f"   Supply Score: {tokenomics['supply_analysis']['score']}/100")
    print(f"   Distribution Score: {tokenomics['distribution']['score']}/100")
    print(f"   Utility Score: {tokenomics['utility']['score']}/100")

    # Technical health
    print("\n2. Technical Health:")
    health = await vc.assess_technical_health("BTC")
    print(f"   Network Health Score: {health['network_health']['score']}/100")
    print(f"   Hash Rate Trend: {health['network_health']['hashrate_trend']}")
    print(f"   Security Score: {health['security_metrics']['score']}/100")

    # Liquidity analysis
    print("\n3. Liquidity Analysis:")
    liquidity = await vc.analyze_liquidity("BTC")
    print(f"   Overall Score: {liquidity['overall_score']}/100")
    print(f"   24h Volume: ${liquidity['trading_volume']['volume_24h']:,.0f}")
    print(f"   Market Depth: {liquidity['market_depth']['depth_quality']}")

    # Development activity
    print("\n4. Development Activity:")
    dev = await vc.track_development_activity("BTC")
    print(f"   Activity Score: {dev['activity_score']}/100")
    print(f"   Commits (30d): {dev['github_metrics']['commits_30d']}")
    print(f"   Contributors: {dev['github_metrics']['active_contributors']}")

    # Risk assessment
    print("\n5. Risk Assessment:")
    risk = await vc.calculate_risk_score("BTC")
    print(f"   Risk Level: {risk['risk_level']}")
    print(f"   Risk Score: {risk['risk_score']}/100")
    print(f"   Max Allocation: {risk['position_sizing']['max_allocation'] * 100:.1f}%")
    print(f"   Recommended: {risk['position_sizing']['recommended_allocation'] * 100:.1f}%")

    print("\n" + "=" * 80)


# ========================
# Example 6: Sentiment and Behavioral Analysis
# ========================


async def example_sentiment_behavioral_analysis():
    """
    Deep dive into sentiment and behavioral finance.
    """
    print("=" * 80)
    print("Example 6: Sentiment & Behavioral Analysis")
    print("=" * 80)

    mcp_client = MCPClientWrapper()
    sentiment = CryptoSentimentAnalyst(mcp_client=mcp_client)

    # Crowd sentiment
    print("\n1. Crowd Sentiment:")
    crowd = await sentiment.analyze_crowd_sentiment("bitcoin")
    print(f"   Fear & Greed Index: {crowd['fear_greed_index']}")
    print(f"   Sentiment Regime: {crowd['sentiment_regime']}")
    print(f"   Social Volume: {crowd['social_metrics']['social_volume']:,}")
    print(f"   Social Dominance: {crowd['social_metrics']['social_dominance'] * 100:.1f}%")

    # Sentiment extremes
    print("\n2. Sentiment Extremes:")
    extremes = await sentiment.detect_sentiment_extremes("bitcoin")
    print(f"   Current Signal: {extremes['current_signal']}")
    print(f"   Percentile: {extremes['current_percentile']}")
    if extremes["extreme_events"]:
        print(f"   Recent Extreme Events: {len(extremes['extreme_events'])}")

    # Whale activity
    print("\n3. Whale Activity:")
    whales = await sentiment.track_whale_activity("BTC")
    print(f"   Whale Sentiment: {whales['whale_sentiment']}")
    print(f"   Large Transactions (7d): {whales['large_transactions']['count_7d']}")
    print(f"   Accumulation Signal: {whales['accumulation_distribution']['signal']}")

    # News sentiment
    print("\n4. News Sentiment:")
    news = await sentiment.analyze_news_sentiment("bitcoin")
    print(f"   Overall Sentiment: {news['overall_sentiment']}")
    print(f"   Positive: {news['sentiment_breakdown']['positive']}%")
    print(f"   Neutral: {news['sentiment_breakdown']['neutral']}%")
    print(f"   Negative: {news['sentiment_breakdown']['negative']}%")

    # Contrarian signals
    print("\n5. Contrarian Opportunity:")
    contrarian = await sentiment.generate_contrarian_signal("bitcoin")
    print(f"   Signal: {contrarian['signal']}")
    print(f"   Confidence: {contrarian['confidence']:.2f}")
    print(f"   Rationale: {contrarian['rationale']['sentiment_extreme']}")

    print("\n" + "=" * 80)


# ========================
# Example 7: Convenience Functions
# ========================


async def example_convenience_functions():
    """
    Use convenience functions for quick analysis.
    """
    print("=" * 80)
    print("Example 7: Convenience Functions")
    print("=" * 80)

    mcp_client = MCPClientWrapper()

    # Quick investment thesis
    print("\nGenerating quick investment thesis...")
    thesis = await synthesize_investment_thesis(
        "ETH", horizon_days=90, mcp_client=mcp_client
    )

    print(f"Thesis: {thesis['thesis_type']}")
    print(f"Recommendation: {thesis['recommendation']}")
    print(f"Confidence: {thesis['confidence']:.2f}")
    print(f"Position Size: {thesis['position_size'] * 100:.1f}%")

    print("\n" + "=" * 80)


# ========================
# Example 8: Error Handling
# ========================


async def example_error_handling():
    """
    Demonstrate proper error handling.
    """
    print("=" * 80)
    print("Example 8: Error Handling")
    print("=" * 80)

    mcp_client = MCPClientWrapper()
    synthesizer = ThesisSynthesizer(mcp_client=mcp_client)

    try:
        # Try analyzing with unknown asset
        result = await synthesizer.generate_investment_thesis("UNKNOWN_TOKEN")
        print(f"\nAnalysis completed for unknown token")
        print(f"Recommendation: {result['recommendation']}")

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("Falling back to default analysis...")

    print("\n" + "=" * 80)


# ========================
# Example 9: Cache Management
# ========================


async def example_cache_management():
    """
    Demonstrate cache management for performance.
    """
    print("=" * 80)
    print("Example 9: Cache Management")
    print("=" * 80)

    mcp_client = MCPClientWrapper()

    # First call - will fetch from MCP
    print("\nFirst call (fetching from MCP)...")
    import time

    start = time.time()
    data1 = await mcp_client.get_fear_greed_index()
    time1 = time.time() - start
    print(f"Time: {time1:.3f}s")

    # Second call - will use cache
    print("\nSecond call (using cache)...")
    start = time.time()
    data2 = await mcp_client.get_fear_greed_index()
    time2 = time.time() - start
    print(f"Time: {time2:.3f}s")

    print(f"\nSpeedup: {time1 / time2:.1f}x faster")

    # Get cache stats
    stats = mcp_client.get_cache_stats()
    print(f"\nCache Stats:")
    print(f"   Total Entries: {stats['total_entries']}")

    # Clear specific cache
    print("\nClearing Fear & Greed cache...")
    mcp_client.clear_cache(pattern="fear_greed")

    print("\n" + "=" * 80)


# ========================
# Main Runner
# ========================


async def main():
    """Run all examples."""
    examples = [
        ("Basic Bitcoin Analysis", example_basic_btc_analysis),
        ("Complete Investment Thesis", example_complete_investment_thesis),
        ("Multi-Asset Comparison", example_multi_asset_comparison),
        ("Macro Regime Analysis", example_macro_regime_analysis),
        ("Fundamental Due Diligence", example_fundamental_due_diligence),
        ("Sentiment & Behavioral Analysis", example_sentiment_behavioral_analysis),
        ("Convenience Functions", example_convenience_functions),
        ("Error Handling", example_error_handling),
        ("Cache Management", example_cache_management),
    ]

    print("\n" + "=" * 80)
    print(" " * 20 + "CRYPTO SKILLS MCP - PRODUCTION USAGE")
    print("=" * 80)
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")

    print("\nRunning all examples...\n")

    for name, example_func in examples:
        await example_func()
        await asyncio.sleep(0.5)  # Small delay between examples

    print("\n" + "=" * 80)
    print(" " * 25 + "ALL EXAMPLES COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
