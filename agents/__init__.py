"""
Crypto-Skills-MCP Agent Layer

This module provides the Strategic Layer of the hybrid Skills + Agents architecture.

Architecture Overview:
--------------------
The Agent Layer consists of three specialized analytical Agents plus one Strategic
Orchestrator Agent:

1. **Specialized Agents** (15-25% of queries):
   - CryptoMacroAnalyst: Macroeconomic analysis and institutional flow tracking
   - CryptoVCAnalyst: Fundamental analysis and due diligence for crypto projects
   - CryptoSentimentAnalyst: Market psychology and behavioral finance analysis

2. **Strategic Orchestrator** (5% of queries):
   - ThesisSynthesizer: Coordinates all specialized Agents, synthesizes outputs,
     resolves conflicts, and generates unified investment theses

Token Efficiency:
-----------------
Agents provide 0% token reduction (no efficiency gains) but deliver strategic value
through multi-domain reasoning, synthesis, and investment-grade recommendations.

The hybrid architecture balances efficiency (Skills: 73% reduction) with reasoning
(Agents: 0% reduction) to achieve 62.5% overall token reduction while maintaining
strategic analytical capabilities.

Usage Examples:
---------------
    # Macroeconomic Analysis
    >>> from agents import CryptoMacroAnalyst
    >>> analyst = CryptoMacroAnalyst()
    >>> macro_outlook = await analyst.synthesize_macro_outlook("BTC", horizon_days=30)

    # Fundamental Due Diligence
    >>> from agents import CryptoVCAnalyst
    >>> vc_analyst = CryptoVCAnalyst()
    >>> dd_report = await vc_analyst.generate_due_diligence_report("BTC")

    # Sentiment Analysis
    >>> from agents import CryptoSentimentAnalyst
    >>> sentiment_analyst = CryptoSentimentAnalyst()
    >>> sentiment = await sentiment_analyst.synthesize_sentiment_outlook("bitcoin")

    # Strategic Orchestration (recommended for comprehensive analysis)
    >>> from agents import ThesisSynthesizer
    >>> orchestrator = ThesisSynthesizer()
    >>> thesis = await orchestrator.generate_investment_thesis("BTC", horizon_days=30)

    # Convenience Functions
    >>> from agents import synthesize_investment_thesis
    >>> thesis = await synthesize_investment_thesis("BTC", horizon_days=30)

MCP Server Requirements:
-------------------------
Required MCP Servers:
- crypto-sentiment-mcp: Social sentiment metrics
- crypto-feargreed-mcp: Fear & Greed Index
- cryptopanic-mcp-server: News sentiment
- grok-search-mcp: News and economic data
- etf-flow-mcp: ETF flow tracking
- ccxt-mcp: Exchange volume data
- crypto-projects-mcp: Project fundamentals
- crypto-indicators-mcp: Technical indicators

Optional MCP Servers:
- perplexity: Economic research and analysis

Version: 1.0.0
"""

from .crypto_macro_analyst import (
    CryptoMacroAnalyst,
    MacroRegime,
    analyze_crypto_macro,
)

from .crypto_vc_analyst import (
    CryptoVCAnalyst,
    RiskLevel,
    InvestmentRecommendation,
    analyze_crypto_project,
)

from .crypto_sentiment_analyst import (
    CryptoSentimentAnalyst,
    SentimentRegime,
    ContrarianSignal,
    analyze_crypto_sentiment,
)

from .thesis_synthesizer import (
    ThesisSynthesizer,
    ThesisType,
    ConflictType,
    synthesize_investment_thesis,
)

__version__ = "1.0.0"

__all__ = [
    # Specialized Agents
    "CryptoMacroAnalyst",
    "CryptoVCAnalyst",
    "CryptoSentimentAnalyst",
    # Strategic Orchestrator
    "ThesisSynthesizer",
    # Enums - Macro
    "MacroRegime",
    # Enums - Fundamental
    "RiskLevel",
    "InvestmentRecommendation",
    # Enums - Sentiment
    "SentimentRegime",
    "ContrarianSignal",
    # Enums - Thesis
    "ThesisType",
    "ConflictType",
    # Convenience Functions
    "analyze_crypto_macro",
    "analyze_crypto_project",
    "analyze_crypto_sentiment",
    "synthesize_investment_thesis",
]


# Agent metadata for discovery and documentation
AGENT_METADATA = {
    "specialized_agents": {
        "crypto_macro_analyst": {
            "class": CryptoMacroAnalyst,
            "domain": "macroeconomic_analysis",
            "description": "Analyzes macro conditions, institutional flows, Fed policy, and risk sentiment",
            "capabilities": [
                "macro_regime_assessment",
                "institutional_flow_tracking",
                "fed_policy_analysis",
                "risk_sentiment_analysis",
                "macro_synthesis",
            ],
            "required_mcps": ["grok-search-mcp", "etf-flow-mcp", "ccxt-mcp"],
            "optional_mcps": ["perplexity"],
        },
        "crypto_vc_analyst": {
            "class": CryptoVCAnalyst,
            "domain": "fundamental_analysis",
            "description": "Performs due diligence, tokenomics analysis, technical health assessment",
            "capabilities": [
                "tokenomics_analysis",
                "technical_health_assessment",
                "liquidity_analysis",
                "development_activity_tracking",
                "risk_scoring",
                "due_diligence_reporting",
            ],
            "required_mcps": [
                "crypto-projects-mcp",
                "ccxt-mcp",
                "crypto-indicators-mcp",
            ],
            "optional_mcps": [],
        },
        "crypto_sentiment_analyst": {
            "class": CryptoSentimentAnalyst,
            "domain": "behavioral_finance",
            "description": "Analyzes market psychology, sentiment extremes, and contrarian signals",
            "capabilities": [
                "crowd_sentiment_analysis",
                "sentiment_extreme_detection",
                "whale_activity_tracking",
                "news_sentiment_analysis",
                "contrarian_signal_generation",
                "sentiment_synthesis",
            ],
            "required_mcps": [
                "crypto-sentiment-mcp",
                "crypto-feargreed-mcp",
                "cryptopanic-mcp-server",
            ],
            "optional_mcps": ["grok-search-mcp"],
        },
    },
    "orchestrator": {
        "thesis_synthesizer": {
            "class": ThesisSynthesizer,
            "domain": "strategic_orchestration",
            "description": "Coordinates all specialized Agents and synthesizes unified investment theses",
            "capabilities": [
                "multi_agent_orchestration",
                "signal_synthesis",
                "conflict_resolution",
                "investment_thesis_generation",
                "recommendation_generation",
            ],
            "requires_agents": [
                "crypto_macro_analyst",
                "crypto_vc_analyst",
                "crypto_sentiment_analyst",
            ],
            "weights": {"macro": 0.35, "fundamental": 0.40, "sentiment": 0.25},
        }
    },
    "performance": {
        "token_reduction": 0.0,  # Agents provide 0% token reduction
        "strategic_value": "high",  # But high strategic reasoning value
        "query_distribution": {
            "specialized_agents": 0.20,  # 20% of queries in hybrid mode
            "orchestrator": 0.025,  # 2.5% of queries in hybrid mode
        },
    },
}


def get_agent_metadata(agent_name: str = None) -> dict:
    """
    Get metadata for a specific Agent or all Agents

    Args:
        agent_name: Optional agent name (e.g., 'crypto_macro_analyst')
                   If None, returns all metadata

    Returns:
        Agent metadata dictionary

    Example:
        >>> metadata = get_agent_metadata('crypto_macro_analyst')
        >>> print(metadata['description'])
        Analyzes macro conditions, institutional flows, Fed policy, and risk sentiment
    """
    if agent_name is None:
        return AGENT_METADATA

    # Check specialized agents
    if agent_name in AGENT_METADATA["specialized_agents"]:
        return AGENT_METADATA["specialized_agents"][agent_name]

    # Check orchestrator
    if agent_name in AGENT_METADATA["orchestrator"]:
        return AGENT_METADATA["orchestrator"][agent_name]

    raise ValueError(
        f"Unknown agent '{agent_name}'. "
        f"Valid agents: {list(AGENT_METADATA['specialized_agents'].keys()) + list(AGENT_METADATA['orchestrator'].keys())}"
    )


def list_available_agents() -> dict:
    """
    List all available Agents with their capabilities

    Returns:
        Dictionary with agent names and brief descriptions

    Example:
        >>> agents = list_available_agents()
        >>> for name, info in agents.items():
        ...     print(f"{name}: {info['description']}")
    """
    agents = {}

    # Add specialized agents
    for name, metadata in AGENT_METADATA["specialized_agents"].items():
        agents[name] = {
            "type": "specialized",
            "domain": metadata["domain"],
            "description": metadata["description"],
            "capabilities": metadata["capabilities"],
        }

    # Add orchestrator
    for name, metadata in AGENT_METADATA["orchestrator"].items():
        agents[name] = {
            "type": "orchestrator",
            "domain": metadata["domain"],
            "description": metadata["description"],
            "capabilities": metadata["capabilities"],
        }

    return agents
