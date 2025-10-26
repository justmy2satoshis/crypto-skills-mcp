"""
Agent Layer Demonstration

This example demonstrates the Strategic Layer (Agents) of the crypto-skills-mcp architecture.

It shows:
1. Using individual specialized Agents (Macro, VC/Fundamental, Sentiment)
2. Using the Strategic Orchestrator (Thesis Synthesizer)
3. Inspecting Agent capabilities and metadata
4. Understanding multi-domain synthesis and conflict resolution
"""

import asyncio
from agents import (
    # Specialized Agents
    CryptoMacroAnalyst,
    CryptoVCAnalyst,
    CryptoSentimentAnalyst,
    # Strategic Orchestrator
    ThesisSynthesizer,
    # Enums
    MacroRegime,
    RiskLevel,
    SentimentRegime,
    ThesisType,
    # Convenience Functions
    analyze_crypto_macro,
    analyze_crypto_sentiment,
    synthesize_investment_thesis,
    # Metadata Functions
    get_agent_metadata,
    list_available_agents,
)


def print_separator(title: str = ""):
    """Print visual separator with optional title"""
    if title:
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}\n")
    else:
        print(f"\n{'='*80}\n")


async def demo_macro_analyst():
    """Demonstrate Crypto Macro Analyst"""
    print_separator("🌐 CRYPTO MACRO ANALYST")

    analyst = CryptoMacroAnalyst()

    print("Agent Capabilities:")
    capabilities = analyst.get_capabilities()
    print(f"  Name: {capabilities['name']}")
    print(f"  Domain: {capabilities['domain']}")
    print(f"  Type: {capabilities['type']}")
    print(f"  Capabilities: {', '.join(capabilities['capabilities'])}")

    print("\n1. Analyzing Macro Regime...")
    regime = await analyst.analyze_macro_regime("BTC", lookback_days=30)
    print(f"  Regime: {regime['regime']}")
    print(f"  Confidence: {regime['confidence']:.0%}")
    print(f"  Fed Policy: {regime['indicators']['fed_policy']}")
    print(f"  Risk Sentiment: {regime['indicators']['risk_sentiment']}")
    print(f"  Institutional Flows: {regime['indicators']['institutional_flows']}")
    print(f"\n  Reasoning: {regime['reasoning']}")

    print("\n2. Tracking Institutional Flows...")
    flows = await analyst.track_institutional_flows("BTC", period_days=7)
    print(f"  Net Flow: ${flows['net_flow']:.1f}M")
    print(f"  Flow Direction: {flows['flow_direction']}")
    print(f"  ETF Daily Average: ${flows['etf_flows']['daily_average']:.1f}M")
    print(f"  ETF Trend: {flows['etf_flows']['trend']}")
    print(f"\n  Interpretation: {flows['interpretation']}")

    print("\n3. Synthesizing Macro Outlook...")
    outlook = await analyst.synthesize_macro_outlook("BTC", horizon_days=30)
    print(f"  Recommendation: {outlook['recommendation'].upper()}")
    print(f"  Confidence: {outlook['confidence']:.0%}")
    print(f"  Regime: {outlook['regime']}")
    print(f"\n  Key Drivers:")
    for driver in outlook["key_drivers"]:
        print(f"    • {driver}")
    print(f"\n  Entry Timing: {outlook['entry_timing']}")
    print(f"  Exit Timing: {outlook['exit_timing']}")


async def demo_vc_analyst():
    """Demonstrate Crypto VC Analyst"""
    print_separator("🔬 CRYPTO VC ANALYST (Fundamental Analysis)")

    analyst = CryptoVCAnalyst()

    print("Agent Capabilities:")
    capabilities = analyst.get_capabilities()
    print(f"  Name: {capabilities['name']}")
    print(f"  Domain: {capabilities['domain']}")
    print(f"  Capabilities: {', '.join(capabilities['capabilities'])}")

    print("\n1. Analyzing Tokenomics (BTC)...")
    tokenomics = await analyst.analyze_tokenomics("BTC")
    print(f"  Supply Score: {tokenomics['supply_analysis']['score']}/100")
    print(f"  Inflation Rate: {tokenomics['supply_analysis']['inflation_rate']}%")
    print(f"  Distribution Score: {tokenomics['distribution']['score']}/100")
    print(f"  Utility Score: {tokenomics['utility']['score']}/100")
    if tokenomics["red_flags"]:
        print(f"\n  ⚠️  Red Flags:")
        for flag in tokenomics["red_flags"]:
            print(f"    • {flag}")

    print("\n2. Calculating Risk Score (BTC)...")
    risk = await analyst.calculate_risk_score("BTC")
    print(f"  Risk Score: {risk['risk_score']}/100")
    print(f"  Risk Level: {risk['risk_level'].upper()}")
    print(f"  Position Sizing: {risk['position_sizing']['max_allocation']*100}%")
    print(f"\n  Risk Breakdown:")
    for category, score in risk["risk_breakdown"].items():
        print(f"    {category.replace('_', ' ').title()}: {score}/100")

    print("\n3. Generating Due Diligence Report (BTC)...")
    dd_report = await analyst.generate_due_diligence_report("BTC")
    print(f"  Overall Score: {dd_report['overall_score']}/100")
    print(f"  Recommendation: {dd_report['recommendation'].upper()}")
    print(f"  Confidence: {dd_report['confidence']:.0%}")
    print(f"\n  Strengths:")
    for strength in dd_report["strengths"][:3]:
        print(f"    ✓ {strength}")
    print(f"\n  Concerns:")
    for concern in dd_report["concerns"][:3]:
        print(f"    ⚠ {concern}")


async def demo_sentiment_analyst():
    """Demonstrate Crypto Sentiment Analyst"""
    print_separator("😊😢 CRYPTO SENTIMENT ANALYST (Market Psychology)")

    analyst = CryptoSentimentAnalyst()

    print("Agent Capabilities:")
    capabilities = analyst.get_capabilities()
    print(f"  Name: {capabilities['name']}")
    print(f"  Domain: {capabilities['domain']}")
    print(f"  Capabilities: {', '.join(capabilities['capabilities'])}")

    print("\n1. Analyzing Crowd Sentiment (bitcoin)...")
    crowd = await analyst.analyze_crowd_sentiment("bitcoin")
    print(f"  Fear & Greed Index: {crowd['fear_greed_index']}")
    print(f"  Sentiment Regime: {crowd['sentiment_regime'].upper()}")
    print(f"  Social Volume: {crowd['social_metrics']['social_volume']:,} mentions")
    print(f"  Social Dominance: {crowd['social_metrics']['social_dominance']:.1f}%")
    print(f"  Contrarian Signal: {crowd['contrarian_signal'].upper()}")
    print(f"\n  Interpretation: {crowd['interpretation']}")

    print("\n2. Detecting Sentiment Extremes (bitcoin)...")
    extremes = await analyst.detect_sentiment_extremes("bitcoin", lookback_days=90)
    print(f"  Current Percentile: {extremes['current_percentile']}th")
    print(f"  Current Signal: {extremes['current_signal']}")
    print(f"\n  Historical Extreme Events:")
    for event in extremes["extreme_events"]:
        print(f"    {event['date']}: F&G {event['fear_greed']} → {event['outcome']}")
    print(f"\n  Mean Reversion: {extremes['pattern_analysis']['mean_reversion_timeframe']}")

    print("\n3. Generating Contrarian Signal (bitcoin)...")
    signal = await analyst.generate_contrarian_signal("bitcoin")
    print(f"  Signal: {signal['signal'].upper()}")
    print(f"  Confidence: {signal['confidence']:.0%}")
    print(f"  Entry Timing: {signal['entry_timing']}")
    print(f"  Exit Timing: {signal['exit_timing']}")
    print(f"\n  Rationale:")
    for key, value in signal["rationale"].items():
        print(f"    {key.replace('_', ' ').title()}: {value}")


async def demo_thesis_synthesizer():
    """Demonstrate Thesis Synthesizer (Strategic Orchestrator)"""
    print_separator("🎯 THESIS SYNTHESIZER (Strategic Orchestrator)")

    orchestrator = ThesisSynthesizer()

    print("Orchestrator Configuration:")
    capabilities = orchestrator.get_capabilities()
    print(f"  Name: {capabilities['name']}")
    print(f"  Type: {capabilities['type']}")
    print(f"  Coordinates: {', '.join(capabilities['coordinates_agents'])}")
    print(f"  Capabilities: {', '.join(capabilities['capabilities'])}")
    print(f"\n  Agent Weights:")
    for agent, weight in orchestrator.weights.items():
        print(f"    {agent.title()}: {weight*100}%")

    print("\n1. Orchestrating Comprehensive Analysis (BTC)...")
    comprehensive = await orchestrator.orchestrate_comprehensive_analysis("BTC", horizon_days=30)
    print(f"  Analysis Complete!")
    print(f"\n  Macro Analysis:")
    print(f"    Recommendation: {comprehensive['macro_analysis']['recommendation']}")
    print(f"    Confidence: {comprehensive['macro_analysis']['confidence']:.0%}")
    print(f"\n  Fundamental Analysis:")
    print(f"    Recommendation: {comprehensive['fundamental_analysis']['recommendation']}")
    print(f"    Overall Score: {comprehensive['fundamental_analysis']['overall_score']}/100")
    print(f"\n  Sentiment Analysis:")
    print(f"    Sentiment: {comprehensive['sentiment_analysis']['sentiment_assessment']}")
    print(f"    Confidence: {comprehensive['sentiment_analysis']['confidence']:.0%}")

    print("\n2. Generating Investment Thesis (BTC)...")
    thesis = await orchestrator.generate_investment_thesis("BTC", horizon_days=30)
    print(f"\n  === INVESTMENT THESIS ===")
    print(f"  Asset: {thesis['asset']}")
    print(f"  Thesis Type: {thesis['thesis_type'].upper()}")
    print(f"  Overall Confidence: {thesis['confidence']:.0%}")
    print(f"\n  Recommendation: {thesis['recommendation'].upper()}")
    print(f"  Horizon: {thesis['investment_horizon_days']} days")

    print(f"\n  Agent Signals:")
    for agent, signal in thesis["agent_signals"].items():
        print(f"    {agent.title()}: {signal}")

    print(f"\n  Conflict Status: {thesis['conflict_analysis']['conflict_type']}")
    if thesis["conflict_analysis"]["conflict_detected"]:
        print(f"  Resolution: {thesis['conflict_analysis']['resolution']}")

    print(f"\n  Key Insights:")
    for insight in thesis["key_insights"][:3]:
        print(f"    • {insight}")

    print(f"\n  Entry Strategy:")
    print(f"    Price Target: ${thesis['entry_strategy']['price_target']:,.2f}")
    print(f"    Position Size: {thesis['entry_strategy']['position_size']*100}%")
    print(f"    Timing: {thesis['entry_strategy']['timing']}")

    print(f"\n  Exit Strategy:")
    print(f"    Target Price: ${thesis['exit_strategy']['target_price']:,.2f}")
    print(
        f"    Stop Loss: ${thesis['exit_strategy']['stop_loss']:,.2f} ({thesis['exit_strategy']['stop_loss_pct']*100}%)"
    )
    print(f"    Take Profit Levels: {len(thesis['exit_strategy']['take_profit_levels'])}")

    print(f"\n  Risk Assessment:")
    print(f"    Overall Risk: {thesis['risk_assessment']['overall_risk'].upper()}")
    print(f"    Risk Score: {thesis['risk_assessment']['risk_score']}/100")

    print(f"\n  Executive Summary:")
    print(f"  {thesis['executive_summary']}")


async def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print_separator("⚡ CONVENIENCE FUNCTIONS")

    print("1. Quick Macro Analysis...")
    result = await analyze_crypto_macro("BTC", "regime")
    print(f"  Regime: {result['regime']}")
    print(f"  Confidence: {result['confidence']:.0%}")

    print("\n2. Quick Sentiment Analysis...")
    result = await analyze_crypto_sentiment("bitcoin", "signal")
    print(f"  Signal: {result['signal']}")
    print(f"  Confidence: {result['confidence']:.0%}")

    print("\n3. Quick Investment Thesis (recommended)...")
    result = await synthesize_investment_thesis("BTC", horizon_days=30)
    print(f"  Thesis: {result['thesis_type']}")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Confidence: {result['confidence']:.0%}")


def demo_agent_metadata():
    """Demonstrate Agent metadata inspection"""
    print_separator("📋 AGENT METADATA & DISCOVERY")

    print("1. List All Available Agents:")
    agents = list_available_agents()
    for name, info in agents.items():
        print(f"\n  {name}:")
        print(f"    Type: {info['type']}")
        print(f"    Domain: {info['domain']}")
        print(f"    Description: {info['description']}")
        print(f"    Capabilities: {len(info['capabilities'])}")

    print("\n\n2. Inspect Specific Agent (crypto_macro_analyst):")
    metadata = get_agent_metadata("crypto_macro_analyst")
    print(f"  Domain: {metadata['domain']}")
    print(f"  Description: {metadata['description']}")
    print(f"  Required MCPs: {', '.join(metadata['required_mcps'])}")
    print(f"  Capabilities:")
    for cap in metadata["capabilities"]:
        print(f"    • {cap}")

    print("\n\n3. Orchestrator Metadata:")
    metadata = get_agent_metadata("thesis_synthesizer")
    print(f"  Domain: {metadata['domain']}")
    print(f"  Description: {metadata['description']}")
    print(f"  Requires Agents: {', '.join(metadata['requires_agents'])}")
    print(f"  Synthesis Weights:")
    for agent, weight in metadata["weights"].items():
        print(f"    {agent.title()}: {weight*100}%")


async def main():
    """Run all demonstrations"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 24 + "CRYPTO-SKILLS-MCP AGENT LAYER" + " " * 24 + "║")
    print("║" + " " * 26 + "Strategic Layer Demonstration" + " " * 23 + "║")
    print("╚" + "═" * 78 + "╝")

    # Metadata (synchronous)
    demo_agent_metadata()

    # Specialized Agents (asynchronous)
    await demo_macro_analyst()
    await demo_vc_analyst()
    await demo_sentiment_analyst()

    # Strategic Orchestrator (asynchronous)
    await demo_thesis_synthesizer()

    # Convenience Functions (asynchronous)
    await demo_convenience_functions()

    print_separator()
    print("✅ Agent Layer demonstration complete!")
    print("\nKey Takeaways:")
    print("  • Specialized Agents provide domain-specific analysis (Macro, Fundamental, Sentiment)")
    print("  • Thesis Synthesizer orchestrates all Agents and resolves conflicts")
    print("  • Agents provide 0% token reduction but deliver strategic value")
    print("  • Hybrid mode balances Skills (73% reduction) with Agents (strategic reasoning)")
    print("\nNext Steps:")
    print("  • Connect MCP servers for live data")
    print("  • Integrate with Skills layer for hybrid routing")
    print("  • Deploy in production with configuration system")
    print()


if __name__ == "__main__":
    asyncio.run(main())
