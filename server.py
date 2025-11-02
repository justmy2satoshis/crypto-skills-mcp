#!/usr/bin/env python3
"""
Crypto Skills MCP Server

FastMCP-based server providing agent-centric crypto analysis workflows.
Follows MCP-Builder best practices for Claude integration.

Architecture:
- 5 workflow-oriented tools (not API wrappers)
- Token-optimized responses with summaries
- Actionable error messages with examples
- Shared component reuse for efficiency
"""

import asyncio
from typing import Optional, Dict, Any
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# Import our crypto analysis components
from agents import (
    CryptoMacroAnalyst,
    CryptoVCAnalyst,
    CryptoSentimentAnalyst,
    ThesisSynthesizer,
)
from mcp_client import MCPClientWrapper
from core.router import TaskRouter

# Initialize FastMCP server
mcp = FastMCP("crypto-skills-mcp")

# Initialize shared components (reused across requests for efficiency)
router = TaskRouter()
mcp_client = MCPClientWrapper()
macro_agent = CryptoMacroAnalyst(mcp_client=mcp_client)
vc_agent = CryptoVCAnalyst(mcp_client=mcp_client)
sentiment_agent = CryptoSentimentAnalyst(mcp_client=mcp_client)
thesis_agent = ThesisSynthesizer(mcp_client=mcp_client)


# ========================
# Tool 1: Intelligent Query Routing
# ========================


class RouteQueryInput(BaseModel):
    """Input schema for query routing"""

    query: str = Field(
        ...,
        description="Natural language query to route to optimal execution path",
        examples=[
            "Calculate RSI for BTC",
            "Should I buy Ethereum now?",
            "Complete investment thesis for SOL",
        ],
    )


@mcp.tool()
async def route_query(input: RouteQueryInput) -> dict:
    """
    Routes query to optimal execution path (skill/agent/orchestrator).

    Use this to understand which analysis approach is best for your query
    before calling specific analysis tools.

    Returns routing decision with target, complexity, handler, and confidence.
    """
    try:
        decision = router.route(input.query)

        return {
            "success": True,
            "routing": decision,
            "summary": f"{decision['target'].upper()}: {decision['handler']} (confidence: {decision['confidence']:.0%})",
            "recommendation": f"Use {decision['target']} for this query type",
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Routing failed: {str(e)}",
            "fix": "Provide a clear natural language question about crypto analysis",
            "example": 'route_query({"query": "Should I buy Bitcoin?"})',
        }


# ========================
# Tool 2: Macro Analysis
# ========================


class MacroAnalysisInput(BaseModel):
    """Input schema for macroeconomic analysis"""

    symbol: str = Field(
        ...,
        description="Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')",
        examples=["BTC", "ETH", "SOL", "AVAX"],
    )


@mcp.tool()
async def analyze_crypto_macro(input: MacroAnalysisInput) -> dict:
    """
    Complete macroeconomic regime analysis for cryptocurrency.

    Analyzes:
    - Current macro regime (risk-on/risk-off/neutral)
    - Fed policy impact on crypto
    - Institutional flows (ETF, exchange)
    - Risk sentiment and correlations

    Returns comprehensive macro outlook with BUY/HOLD/SELL recommendation.
    """
    try:
        result = await macro_agent.synthesize_macro_outlook(input.symbol.upper())

        return {
            "success": True,
            "data": result,
            "summary": f"Regime: {result['regime']} | Recommendation: {result['recommendation']} | Confidence: {result['confidence']:.0%}",
            "key_insights": [
                f"Macro regime: {result['regime']}",
                f"Fed impact: {result.get('fed_impact', 'N/A')}",
                f"Institutional flows: {result.get('flow_signal', 'N/A')}",
            ],
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Macro analysis failed: {str(e)}",
            "fix": "Use a valid cryptocurrency symbol (BTC, ETH, SOL, etc.)",
            "example": 'analyze_crypto_macro({"symbol": "BTC"})',
        }


# ========================
# Tool 3: Fundamental Analysis
# ========================


class FundamentalAnalysisInput(BaseModel):
    """Input schema for fundamental analysis"""

    symbol: str = Field(
        ...,
        description="Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')",
        examples=["BTC", "ETH", "SOL", "AVAX"],
    )


@mcp.tool()
async def analyze_crypto_fundamental(input: FundamentalAnalysisInput) -> dict:
    """
    Complete fundamental due diligence and risk assessment.

    Analyzes:
    - Tokenomics (supply, distribution, utility)
    - Technical health (network, security)
    - Liquidity (volume, depth)
    - Development activity
    - Risk score and position sizing

    Returns comprehensive fundamental report with risk-adjusted allocation.
    """
    try:
        result = await vc_agent.generate_due_diligence_report(input.symbol.upper())

        return {
            "success": True,
            "data": result,
            "summary": f"Overall Score: {result['overall_score']}/100 | Recommendation: {result['recommendation']} | Risk: {result.get('risk_level', 'N/A')}",
            "key_insights": [
                f"Fundamental score: {result['overall_score']}/100",
                f"Risk level: {result.get('risk_level', 'N/A')}",
                f"Max allocation: {result.get('position_sizing', {}).get('max_allocation', 0) * 100:.1f}%",
            ],
            "position_sizing": result.get("position_sizing", {}),
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Fundamental analysis failed: {str(e)}",
            "fix": "Use a valid cryptocurrency symbol with available fundamental data",
            "example": 'analyze_crypto_fundamental({"symbol": "ETH"})',
        }


# ========================
# Tool 4: Sentiment Analysis
# ========================


class SentimentAnalysisInput(BaseModel):
    """Input schema for sentiment analysis"""

    asset: str = Field(
        ...,
        description="Cryptocurrency name (e.g., 'bitcoin', 'ethereum', 'solana')",
        examples=["bitcoin", "ethereum", "solana", "avalanche"],
    )


@mcp.tool()
async def analyze_crypto_sentiment(input: SentimentAnalysisInput) -> dict:
    """
    Complete market psychology and sentiment analysis.

    Analyzes:
    - Fear & Greed Index
    - Social sentiment and dominance
    - Whale activity patterns
    - News sentiment
    - Contrarian opportunity signals

    Returns comprehensive sentiment outlook with timing insights.
    """
    try:
        result = await sentiment_agent.synthesize_sentiment_outlook(input.asset.lower())

        return {
            "success": True,
            "data": result,
            "summary": f"Sentiment: {result['sentiment_assessment']} | Signal: {result.get('contrarian_signal', 'N/A')} | Confidence: {result['confidence']:.0%}",
            "key_insights": [
                f"Sentiment regime: {result['sentiment_assessment']}",
                f"Fear & Greed: {result.get('fear_greed_level', 'N/A')}",
                f"Contrarian signal: {result.get('contrarian_signal', 'N/A')}",
            ],
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Sentiment analysis failed: {str(e)}",
            "fix": "Use cryptocurrency name in lowercase (e.g., 'bitcoin', not 'BTC')",
            "example": 'analyze_crypto_sentiment({"asset": "bitcoin"})',
        }


# ========================
# Tool 5: Investment Thesis Generation
# ========================


class InvestmentThesisInput(BaseModel):
    """Input schema for investment thesis generation"""

    symbol: str = Field(
        ...,
        description="Cryptocurrency symbol (e.g., 'BTC', 'ETH', 'SOL')",
        examples=["BTC", "ETH", "SOL", "AVAX"],
    )
    horizon_days: int = Field(
        default=30,
        description="Investment time horizon in days (7-365)",
        ge=7,
        le=365,
    )


@mcp.tool()
async def generate_investment_thesis(input: InvestmentThesisInput) -> dict:
    """
    Generate complete investment thesis with actionable recommendations.

    Synthesizes all analyses (macro, fundamental, sentiment) into:
    - BUY/HOLD/SELL recommendation
    - Entry range with specific price levels
    - Exit targets (multiple levels)
    - Stop loss placement
    - Position sizing recommendation
    - Key catalysts and risks
    - Time horizon alignment

    This is the most comprehensive tool - use for investment decisions.
    """
    try:
        result = await thesis_agent.generate_investment_thesis(
            input.symbol.upper(), horizon_days=input.horizon_days
        )

        # Build actionable summary
        entry_range = result.get("entry_range", {})
        exit_targets = result.get("exit_targets", [])
        stop_loss = result.get("stop_loss", {})

        return {
            "success": True,
            "data": result,
            "summary": f"{result['thesis_type']} | {result['recommendation']} | Position: {result['position_size'] * 100:.1f}% | Confidence: {result['confidence']:.0%}",
            "actionable": {
                "recommendation": result["recommendation"],
                "entry_range": f"${entry_range.get('low', 0):,.0f} - ${entry_range.get('high', 0):,.0f}",
                "targets": [f"${t.get('price', 0):,.0f}" for t in exit_targets[:3]],
                "stop_loss": f"${stop_loss.get('price', 0):,.0f}",
                "position_size": f"{result['position_size'] * 100:.1f}%",
                "time_horizon": result["time_horizon"],
            },
            "key_catalysts": result.get("key_catalysts", [])[:3],
            "key_risks": result.get("key_risks", [])[:3],
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Thesis generation failed: {str(e)}",
            "fix": "Use valid symbol and ensure horizon is 7-365 days",
            "example": 'generate_investment_thesis({"symbol": "BTC", "horizon_days": 30})',
        }


# ========================
# Server Entry Point
# ========================

if __name__ == "__main__":
    # Run FastMCP server (stdio transport for Claude Code)
    mcp.run()
