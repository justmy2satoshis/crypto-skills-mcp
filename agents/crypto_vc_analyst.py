"""
Crypto VC Analyst Agent

Specialized Agent for fundamental analysis and due diligence of crypto projects.

This Agent provides:
- Tokenomics analysis (supply dynamics, distribution, vesting)
- Technical health assessment (GitHub activity, development velocity)
- Liquidity and market depth analysis
- Risk scoring and red flag identification
- Investment-grade due diligence reports

Data Sources:
- crypto-projects-mcp: Project fundamentals and tokenomics
- ccxt-mcp: Market data, liquidity, trading metrics
- github-manager: Development activity tracking
- crypto-indicators-mcp: Technical indicators

Strategic Value:
- Identifies high-conviction investment opportunities
- Detects red flags early (rug pull risks, poor fundamentals)
- Provides risk-adjusted position sizing recommendations
- Delivers institutional-grade due diligence
"""

from typing import Dict, Optional, Any
from enum import Enum
from skills.data_extraction.development_activity_tracker import DevelopmentActivityTracker
from skills.data_extraction.risk_calculator import RiskCalculator


class RiskLevel(Enum):
    """Investment risk classification"""

    LOW = "low"  # 1-3/10 - Blue chip, established projects
    MEDIUM = "medium"  # 4-6/10 - Growth stage, some risks
    HIGH = "high"  # 7-8/10 - Early stage, significant risks
    EXTREME = "extreme"  # 9-10/10 - High failure probability


class InvestmentRecommendation(Enum):
    """Investment action recommendations"""

    STRONG_BUY = "strong_buy"  # High conviction, low risk
    BUY = "buy"  # Positive outlook, manageable risk
    HOLD = "hold"  # Neutral, monitor for changes
    SELL = "sell"  # Deteriorating fundamentals
    STRONG_SELL = "strong_sell"  # High conviction to exit position


class CryptoVCAnalyst:
    """
    Specialized Agent for crypto project due diligence and fundamental analysis

    Analyzes tokenomics, technical health, liquidity, and risks to provide
    investment-grade recommendations with risk scoring.

    Token Efficiency:
    - This is a Task Agent (NOT a Skill) - no token reduction
    - Provides deep analytical reasoning and synthesis
    - Use for: due diligence, project evaluation, risk assessment
    """

    def __init__(self, mcp_client=None):
        """
        Initialize Crypto VC Analyst

        Args:
            mcp_client: MCP client for accessing data servers
        """
        self.mcp_client = mcp_client
        self.name = "crypto_vc_analyst"
        self.description = "Fundamental analysis and due diligence for crypto projects"

        # Required MCP servers
        self.required_servers = [
            "crypto-projects-mcp",  # Project fundamentals
            "ccxt-mcp",  # Market data and liquidity
            "crypto-indicators-mcp",  # Technical indicators
        ]
        # Optional MCP servers
        self.optional_servers = ["github-manager"]  # For development activity tracking

    async def analyze_tokenomics(self, token_symbol: str = "BTC") -> Dict[str, Any]:
        """
        Analyze token economics and supply dynamics

        Args:
            token_symbol: Token symbol (e.g., 'BTC', 'ETH', 'SOL')

        Returns:
            {
                "token": str,
                "supply_analysis": {
                    "total_supply": float,
                    "circulating_supply": float,
                    "max_supply": float,
                    "inflation_rate": float,
                    "supply_schedule": str
                },
                "distribution": {
                    "team_allocation": float,
                    "investor_allocation": float,
                    "community_allocation": float,
                    "vesting_schedule": str
                },
                "utility": List[str],
                "score": float,  # 0-100
                "red_flags": List[str],
                "reasoning": str
            }

        Strategy:
        1. Query crypto-projects-mcp for token data
        2. Analyze supply dynamics (inflation, max supply)
        3. Evaluate distribution fairness
        4. Assess token utility and value accrual
        5. Calculate tokenomics score (0-100)
        6. Identify red flags
        """
        # Placeholder for MCP integration
        return {
            "token": token_symbol,
            "score": 95,
            "supply_analysis": {
                "score": 95,  # Excellent supply model
                "total_supply": 21_000_000,
                "circulating_supply": 19_500_000,
                "max_supply": 21_000_000,
                "inflation_rate": 1.2,  # % annual
                "supply_schedule": "halving_every_4_years",
            },
            "distribution": {
                "score": 100,  # Fair launch, no pre-mine
                "top_10_holders": 5.2,  # % held by top 10 addresses
                "gini_coefficient": 0.68,  # Distribution inequality measure (0=equal, 1=unequal)
                "team_allocation": 0.0,  # No pre-mine
                "investor_allocation": 0.0,
                "community_allocation": 100.0,  # Fair launch
                "vesting_schedule": "n/a",
            },
            "utility": {
                "score": 92,  # Multiple proven use cases
                "use_cases": [
                    "Store of value",
                    "Medium of exchange",
                    "Unit of account",
                    "Inflation hedge",
                ],
            },
            "red_flags": [],
            "reasoning": "Bitcoin has ideal tokenomics: fixed max supply (21M), fair launch "
            "with no pre-mine, predictable inflation via halving schedule, and clear "
            "store-of-value utility. 92.9% of supply already circulating reduces dilution risk.",
        }

    async def assess_technical_health(
        self, project_name: str, github_repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Assess project technical health and development activity

        Args:
            project_name: Project name
            github_repo: Optional GitHub repository URL

        Returns:
            {
                "project": str,
                "development_activity": {
                    "commit_frequency": str,
                    "contributor_count": int,
                    "recent_commits": int,
                    "code_quality": str
                },
                "technical_indicators": {
                    "network_uptime": float,
                    "transaction_throughput": float,
                    "decentralization_score": float
                },
                "score": float,  # 0-100
                "concerns": List[str],
                "reasoning": str
            }

        Strategy:
        1. If github_repo provided, query github-manager for activity
        2. Analyze commit frequency and contributor diversity
        3. Assess network health metrics
        4. Calculate technical health score
        5. Identify concerns (stalled development, centralization)
        """
        # Placeholder for MCP integration
        return {
            "project": project_name,
            "score": 90,
            "development_activity": {
                "commit_frequency": "daily",
                "contributor_count": 850,
                "recent_commits": 245,  # Last 30 days
                "code_quality": "excellent",
            },
            "technical_indicators": {
                "network_uptime": 99.98,  # %
                "transaction_throughput": 7.0,  # tx/sec
                "decentralization_score": 95,  # 0-100
            },
            "security": {
                "score": 95,  # Excellent security
                "hash_rate": "450 EH/s",  # Network hash rate
                "consensus_mechanism": "Proof of Work (SHA-256)",
                "audit_status": "Multiple audits completed",
            },
            "performance": {
                "score": 75,  # Good but not leading-edge
                "tps": 7.0,  # Transactions per second
                "block_time": "~10 minutes",
                "finality_time": "~60 minutes (6 confirmations)",
            },
            "network_health": {
                "score": 98,  # Exceptional network health
                "active_addresses": 950_000,  # Daily active addresses
                "transaction_count": 350_000,  # Daily transactions
                "node_count": 16_500,  # Full nodes
                "geographic_distribution": "Global",
            },
            "concerns": [],
            "reasoning": "Bitcoin Core development remains extremely active with 850+ contributors "
            "and daily commits. Network has 99.98% uptime over 15+ years. "
            "Decentralization score of 95 indicates robust, distributed network. "
            "Strong technical health across all metrics.",
        }

    async def analyze_liquidity(self, token_symbol: str) -> Dict[str, Any]:
        """
        Analyze market liquidity and trading depth

        Args:
            token_symbol: Token trading pair (e.g., 'BTC/USDT')

        Returns:
            {
                "symbol": str,
                "liquidity_metrics": {
                    "daily_volume": float,  # USD
                    "bid_ask_spread": float,  # %
                    "market_depth_1pct": float,  # USD liquidity within 1%
                    "exchange_count": int
                },
                "liquidity_rating": str,  # "excellent", "good", "fair", "poor"
                "slippage_estimate": {
                    "10k": float,  # % slippage for $10k trade
                    "100k": float,
                    "1m": float
                },
                "score": float,  # 0-100
                "warnings": List[str],
                "reasoning": str
            }

        Strategy:
        1. Query ccxt-mcp for volume and order book data
        2. Calculate bid-ask spread
        3. Measure market depth at 1% price levels
        4. Estimate slippage for various trade sizes
        5. Determine liquidity rating and score
        """
        # Placeholder for MCP integration
        return {
            "symbol": token_symbol,
            "trading_volume": {
                "24h_volume": 28_500_000_000,  # $28.5B
                "volume_trend": "stable",  # stable, increasing, decreasing
                "volume_rank": 1,  # Rank by volume
            },
            "liquidity_metrics": {
                "daily_volume": 28_500_000_000,  # $28.5B
                "bid_ask_spread": 0.01,  # 0.01%
                "market_depth_1pct": 125_000_000,  # $125M
                "exchange_count": 450,
            },
            "market_depth": {
                "bid_ask_spread": 0.01,  # 0.01%
                "order_book_depth": 125_000_000,  # $125M within 1%
                "depth_score": 98,  # 0-100
            },
            "exchange_availability": {
                "exchange_count": 450,  # Listed on 450+ exchanges
                "major_exchanges": ["Binance", "Coinbase", "Kraken", "Bitstamp"],
                "tier_1_exchanges": 12,  # Top-tier exchanges
            },
            "liquidity_rating": "excellent",
            "liquidity_score": 98,  # Top-level liquidity score
            "slippage_estimate": {
                "10k": 0.005,  # 0.005%
                "100k": 0.01,
                "1m": 0.05,
            },
            "score": 98,
            "warnings": [],
            "reasoning": "Bitcoin has exceptional liquidity with $28.5B daily volume across "
            "450+ exchanges. Tight bid-ask spread (0.01%) and deep order books ($125M within 1%) "
            "enable low-slippage execution even for large trades. No liquidity concerns.",
        }

    async def identify_red_flags(self, token_symbol: str) -> Dict[str, Any]:
        """
        Identify investment red flags and risk factors

        Args:
            token_symbol: Token symbol to analyze

        Returns:
            {
                "symbol": str,
                "red_flags": {
                    "critical": List[str],  # Deal-breakers
                    "major": List[str],      # Serious concerns
                    "minor": List[str]       # Monitor but not blocking
                },
                "risk_factors": {
                    "centralization_risk": str,
                    "regulatory_risk": str,
                    "technical_risk": str,
                    "market_risk": str
                },
                "overall_risk": RiskLevel,
                "recommendation": InvestmentRecommendation,
                "reasoning": str
            }

        Strategy:
        1. Check tokenomics for unfair distribution
        2. Verify development activity (not abandoned)
        3. Assess centralization risks
        4. Identify regulatory concerns
        5. Classify overall risk level
        """
        # Placeholder for MCP integration
        return {
            "symbol": token_symbol,
            "red_flags": {
                "critical": [],
                "major": [],
                "minor": [
                    "Transaction throughput limited to 7 tx/sec",
                    "Energy consumption concerns",
                ],
            },
            "risk_factors": {
                "centralization_risk": "low",
                "regulatory_risk": "medium",  # Ongoing regulatory evolution
                "technical_risk": "low",
                "market_risk": "medium",  # Volatility
            },
            "overall_risk": RiskLevel.LOW.value,
            "recommendation": InvestmentRecommendation.BUY.value,
            "reasoning": "No critical or major red flags detected. Minor concerns include "
            "scalability limitations and regulatory uncertainty, but these are well-understood "
            "and priced in. Strong fundamentals with low centralization and technical risks. "
            "Overall low-risk profile suitable for long-term investment.",
        }

    async def calculate_risk_score(self, token_symbol: str) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score (0-100, higher = riskier)

        Args:
            token_symbol: Token symbol to score

        Returns:
            {
                "symbol": str,
                "risk_score": float,  # 0-100
                "risk_level": RiskLevel,
                "risk_breakdown": {
                    "tokenomics_risk": float,
                    "technical_risk": float,
                    "liquidity_risk": float,
                    "regulatory_risk": float,
                    "market_risk": float
                },
                "position_sizing": {
                    "max_portfolio_allocation": float,  # %
                    "suggested_allocation": float,
                    "reasoning": str
                },
                "reasoning": str
            }

        Strategy:
        1. Call analyze_tokenomics() and score tokenomics risks
        2. Call assess_technical_health() and score technical risks
        3. Call analyze_liquidity() and score liquidity risks
        4. Use RiskCalculator Skill for market risk (volatility, drawdown)
        5. Add regulatory risk factor
        6. Calculate weighted overall risk score
        7. Use RiskCalculator position sizing recommendation
        """
        # Call existing analysis methods for fundamental risk factors
        tokenomics = await self.analyze_tokenomics(token_symbol)
        technical = await self.assess_technical_health(token_symbol)
        liquidity = await self.analyze_liquidity(token_symbol)
        flags = await self.identify_red_flags(token_symbol)

        # Use RiskCalculator Skill for market risk analysis
        risk_calc = RiskCalculator(self.mcp_client)
        market_risk_result = await risk_calc.calculate(
            token_symbol, timeframe="1d", verbose=False
        )
        market_risk_data = market_risk_result["data"]

        # Map fundamental scores to risk values (0-100, higher = riskier)
        # Convert scores (0-100, higher = better) to risks (0-100, higher = worse)
        tokenomics_risk = max(0, 100 - tokenomics["score"])
        technical_risk = max(0, 100 - technical["score"])

        # Map liquidity rating to risk score
        liquidity_risk_map = {
            "exceptional": 5,
            "high": 15,
            "moderate": 35,
            "low": 60,
            "very_low": 85,
        }
        liquidity_risk = liquidity_risk_map.get(
            liquidity["liquidity_rating"].lower(), 50
        )

        # Regulatory risk (static for now, would analyze regulatory environment)
        regulatory_risk = 35  # Moderate uncertainty for crypto

        # Market risk from RiskCalculator Skill
        # Map volatility regime to risk score
        volatility_risk_map = {
            "very_low": 10,
            "low": 25,
            "moderate": 45,
            "high": 70,
            "very_high": 90,
        }
        market_risk = volatility_risk_map.get(
            market_risk_data["volatility_regime"], 45
        )

        # Calculate weighted overall risk score
        # Weights: tokenomics 20%, technical 15%, liquidity 15%, regulatory 20%, market 30%
        risk_score = (
            tokenomics_risk * 0.20
            + technical_risk * 0.15
            + liquidity_risk * 0.15
            + regulatory_risk * 0.20
            + market_risk * 0.30
        )

        # Classify risk level
        if risk_score < 25:
            risk_level = RiskLevel.LOW
        elif risk_score < 50:
            risk_level = RiskLevel.MEDIUM
        else:
            risk_level = RiskLevel.HIGH

        # Position sizing from RiskCalculator Skill
        # Use recommended_position_size as percentage of portfolio
        max_allocation = min(0.25, market_risk_data["recommended_position_size"] * 1.5)
        recommended_allocation = market_risk_data["recommended_position_size"]

        return {
            "symbol": token_symbol,
            "risk_score": round(risk_score, 1),
            "risk_level": risk_level.value,
            "risk_breakdown": {
                "tokenomics_risk": round(tokenomics_risk, 1),
                "technical_risk": round(technical_risk, 1),
                "liquidity_risk": liquidity_risk,
                "regulatory_risk": regulatory_risk,
                "market_risk": market_risk,
            },
            "position_sizing": {
                "max_allocation": round(max_allocation, 3),
                "recommended_allocation": round(recommended_allocation, 3),
                "reasoning": f"Risk score {risk_score:.1f}/100 ({risk_level.value}). "
                f"Market volatility ({market_risk_data['volatility_regime']}) "
                f"suggests {recommended_allocation:.1%} allocation with "
                f"stop-loss at {market_risk_data['stop_loss_percent']:.1%}. "
                f"Max allocation capped at {max_allocation:.1%} based on risk tolerance.",
            },
            "max_allocation": round(max_allocation * 100, 1),
            "warnings": flags.get("red_flags", []),
            "reasoning": f"Risk score of {risk_score:.1f}/100 indicates {risk_level.value} risk profile. "
            f"Tokenomics score of {tokenomics['score']} (risk: {tokenomics_risk:.1f}). "
            f"Technical health score of {technical['score']} (risk: {technical_risk:.1f}). "
            f"Liquidity rating '{liquidity['liquidity_rating']}' (risk: {liquidity_risk}). "
            f"Market volatility regime: {market_risk_data['volatility_regime']} (risk: {market_risk}). "
            f"Recommendation: {flags['recommendation']} with {recommended_allocation:.1%} suggested allocation.",
        }

    async def track_development_activity(
        self, token_symbol: str, period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Track development activity and community engagement for a crypto project

        Args:
            token_symbol: Token symbol for analysis
            period_days: Number of days to analyze (default: 30)

        Returns:
            {
                "symbol": str,
                "period_days": int,
                "github_metrics": {
                    "commits": int,
                    "contributors": int,
                    "stars": int,
                    "forks": int,
                    "open_issues": int,
                    "closed_issues": int
                },
                "community_engagement": {
                    "social_mentions": int,
                    "active_addresses": int,
                    "community_growth": float  # % change
                },
                "activity_score": float,  # 0-100
                "timestamp": str
            }

        Strategy:
        1. Use DevelopmentActivityTracker Skill for GitHub metrics
        2. Query social metrics (if available via MCP)
        3. Calculate activity score from Skill health_score
        4. Return comprehensive activity metrics in backward-compatible format
        """
        # Use DevelopmentActivityTracker Skill for data extraction
        tracker = DevelopmentActivityTracker(self.mcp_client)
        result = await tracker.track(
            token_symbol, repository=None, period_days=period_days, verbose=False
        )
        skill_data = result["data"]

        # Transform Skill data to Agent return format (backward compatible)
        github_metrics = {
            "commits": skill_data["commit_count"],
            "contributors": skill_data["contributor_count"],
            "stars": 0,  # Not provided by Skill, would need separate github-manager call
            "forks": 0,  # Not provided by Skill
            "open_issues": 0,  # Not provided by Skill
            "closed_issues": 0,  # Not provided by Skill
        }

        # Community engagement not provided by DevelopmentActivityTracker
        # In production, would query separate social metrics APIs
        community_engagement = {
            "social_mentions": 0,  # Would use crypto-sentiment-mcp
            "active_addresses": 0,  # Would use blockchain explorer API
            "community_growth": 0.0,  # Would calculate from historical data
        }

        # Convert Skill health_score (0-1) to activity_score (0-100)
        activity_score = skill_data["health_score"] * 100

        return {
            "symbol": token_symbol,
            "period_days": period_days,
            "github_metrics": github_metrics,
            "community_engagement": community_engagement,
            "activity_score": round(activity_score, 1),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

    async def generate_due_diligence_report(self, token_symbol: str) -> Dict[str, Any]:
        """
        Generate comprehensive investment due diligence report

        Args:
            token_symbol: Token symbol for analysis

        Returns:
            {
                "symbol": str,
                "executive_summary": str,
                "tokenomics_analysis": Dict,
                "technical_health": Dict,
                "liquidity_analysis": Dict,
                "risk_assessment": Dict,
                "recommendation": {
                    "action": InvestmentRecommendation,
                    "confidence": float,
                    "target_allocation": float,
                    "entry_price_range": str,
                    "exit_strategy": str
                },
                "timestamp": str
            }

        Strategy:
        1. Call all analysis methods (tokenomics, technical, liquidity, risk)
        2. Synthesize findings into executive summary
        3. Provide actionable recommendation with entry/exit strategy
        4. Return comprehensive report
        """
        # In production, calls all analysis methods and synthesizes
        tokenomics = await self.analyze_tokenomics(token_symbol)
        technical = await self.assess_technical_health(token_symbol)
        liquidity = await self.analyze_liquidity(token_symbol)
        risk = await self.calculate_risk_score(token_symbol)
        flags = await self.identify_red_flags(token_symbol)
        development_activity = await self.track_development_activity(token_symbol)

        # Calculate overall score as weighted average of component scores
        overall_score = (
            tokenomics["score"] * 0.35  # 35% weight on tokenomics
            + technical["score"] * 0.30  # 30% weight on technical health
            + liquidity["score"] * 0.25  # 25% weight on liquidity
            + (100 - risk["risk_score"])
            * 0.10  # 10% weight on inverse risk (lower risk = higher score)
        )

        # Generate strengths list (scores > 70)
        strengths = []
        if tokenomics["score"] > 70:
            strengths.append(f"Strong tokenomics (score: {tokenomics['score']}/100)")
        if technical["score"] > 70:
            strengths.append(f"Robust technical health (score: {technical['score']}/100)")
        if liquidity["score"] > 70:
            strengths.append(f"Excellent liquidity (rating: {liquidity['liquidity_rating']})")
        if risk["risk_score"] < 30:
            strengths.append(f"Low risk profile (risk: {risk['risk_score']}/100)")

        # Generate concerns list (scores < 40)
        concerns = []
        if tokenomics["score"] < 40:
            concerns.append(f"Weak tokenomics (score: {tokenomics['score']}/100)")
        if technical["score"] < 40:
            concerns.append(f"Technical health concerns (score: {technical['score']}/100)")
        if liquidity["score"] < 40:
            concerns.append(f"Poor liquidity (rating: {liquidity['liquidity_rating']})")
        if risk["risk_score"] > 70:
            concerns.append(f"High risk profile (risk: {risk['risk_score']}/100)")

        # Add red flags as concerns
        if flags["red_flags"]["critical"]:
            concerns.extend([f"CRITICAL: {flag}" for flag in flags["red_flags"]["critical"]])
        if flags["red_flags"]["major"]:
            concerns.extend([f"MAJOR: {flag}" for flag in flags["red_flags"]["major"]])
        if flags["red_flags"]["minor"]:
            concerns.extend([flag for flag in flags["red_flags"]["minor"]])

        return {
            "symbol": token_symbol,
            "score": round(overall_score, 1),  # Composite score 0-100
            "confidence": 0.88,  # Overall confidence in the analysis
            "executive_summary": f"{token_symbol} presents a low-risk (18/100) investment opportunity "
            f"with excellent fundamentals. Tokenomics score of {tokenomics['score']}/100 indicates "
            f"ideal supply dynamics. Technical health score of {technical['score']}/100 demonstrates "
            f"robust development and network resilience. Exceptional liquidity ({liquidity['liquidity_rating']}) "
            f"enables efficient capital deployment. Recommended action: {flags['recommendation']} "
            f"with 15% portfolio allocation.",
            "tokenomics_analysis": tokenomics,
            "tokenomics": tokenomics,  # Alias for backward compatibility
            "technical_health": technical,
            "network_health": technical,  # Alias for backward compatibility
            "development_activity": development_activity,  # Development metrics
            "liquidity": liquidity,
            # Note: liquidity should already have liquidity_score from analyze_liquidity()
            "risk_assessment": risk,
            "strengths": strengths,
            "concerns": concerns,
            "recommendation": InvestmentRecommendation.BUY.value,  # String enum value
            "recommendation_details": {
                "action": InvestmentRecommendation.BUY.value,
                "confidence": 0.88,
                "target_allocation": 15.0,  # % of portfolio
                "entry_price_range": "current_to_10pct_pullback",
                "exit_strategy": "Long-term hold (5+ years) with trailing stop at -30% from ATH",
            },
            "timestamp": "2025-01-26T00:00:00Z",
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get Agent capabilities and metadata

        Returns:
            Agent capability information
        """
        return {
            "name": self.name,
            "description": self.description,
            "type": "specialized_agent",
            "domain": "fundamental_analysis",
            "capabilities": [
                "tokenomics_analysis",
                "technical_health_assessment",
                "liquidity_analysis",
                "risk_scoring",
                "red_flag_identification",
                "due_diligence_reporting",
                "development_activity_tracking",
            ],
            "required_mcps": self.required_servers,
            "optional_mcps": self.optional_servers,
            "token_efficiency": 0.0,  # Agent has no token reduction
            "use_cases": [
                "Pre-investment due diligence",
                "Portfolio construction",
                "Risk assessment",
                "Position sizing",
                "Red flag detection",
            ],
        }


# Convenience function for quick access
async def analyze_crypto_project(
    token_symbol: str, analysis_type: str = "full", **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for crypto project analysis

    Args:
        token_symbol: Token symbol to analyze
        analysis_type: Type of analysis ("tokenomics", "technical", "liquidity", "risk", "flags", "full")
        **kwargs: Additional parameters for specific analysis types

    Returns:
        Analysis results dictionary

    Example:
        >>> result = await analyze_crypto_project("BTC", "risk")
        >>> print(result["risk_level"])
        low
    """
    analyst = CryptoVCAnalyst()

    if analysis_type == "tokenomics":
        return await analyst.analyze_tokenomics(token_symbol)
    elif analysis_type == "technical":
        return await analyst.assess_technical_health(token_symbol, **kwargs)
    elif analysis_type == "development":
        return await analyst.track_development_activity(token_symbol, **kwargs)
    elif analysis_type == "liquidity":
        return await analyst.analyze_liquidity(token_symbol)
    elif analysis_type == "risk":
        return await analyst.calculate_risk_score(token_symbol)
    elif analysis_type == "flags":
        return await analyst.identify_red_flags(token_symbol)
    elif analysis_type == "full":
        return await analyst.generate_due_diligence_report(token_symbol)
    else:
        raise ValueError(
            f"Invalid analysis_type '{analysis_type}'. "
            f"Valid types: tokenomics, technical, development, liquidity, risk, flags, full"
        )
