"""
Crypto Sentiment Analyst Agent

Specialized Agent for market psychology and behavioral finance analysis.

This Agent provides:
- Crowd sentiment analysis (Fear & Greed, social metrics)
- Contrarian signal identification (extreme sentiment reversals)
- Whale activity and smart money tracking
- News sentiment and narrative analysis
- Market timing based on behavioral finance principles

Data Sources:
- crypto-sentiment-mcp: Social sentiment metrics
- crypto-feargreed-mcp: Fear & Greed Index
- cryptopanic-mcp-server: News sentiment
- grok-search-mcp: Social media and news analysis

Strategic Value:
- Identifies overbought/oversold conditions via sentiment extremes
- Detects smart money vs. dumb money divergences
- Provides contrarian entry/exit signals
- Tracks narrative shifts and FUD/FOMO cycles
"""

from typing import Dict, Any, List
from enum import Enum


class SentimentRegime(Enum):
    """Market sentiment regimes"""

    EXTREME_FEAR = "extreme_fear"  # < 25 Fear & Greed
    FEAR = "fear"  # 25-45
    NEUTRAL = "neutral"  # 45-55
    GREED = "greed"  # 55-75
    EXTREME_GREED = "extreme_greed"  # > 75


class ContrarianSignal(Enum):
    """Contrarian trading signals"""

    STRONG_BUY = "strong_buy"  # Extreme fear = opportunity
    BUY = "buy"  # Fear = accumulation
    HOLD = "hold"  # Neutral sentiment
    SELL = "sell"  # Greed = distribution
    STRONG_SELL = "strong_sell"  # Extreme greed = top signal


class CryptoSentimentAnalyst:
    """
    Specialized Agent for cryptocurrency market psychology and sentiment analysis

    Analyzes crowd behavior, sentiment extremes, and whale activity to identify
    contrarian opportunities and market timing signals.

    Token Efficiency:
    - This is a Task Agent (NOT a Skill) - no token reduction
    - Provides behavioral finance reasoning and synthesis
    - Use for: sentiment analysis, contrarian signals, market timing
    """

    def __init__(self, mcp_client=None):
        """
        Initialize Crypto Sentiment Analyst

        Args:
            mcp_client: MCP client for accessing data servers
        """
        self.mcp_client = mcp_client
        self.name = "crypto_sentiment_analyst"
        self.description = "Market psychology and behavioral finance analysis"

        # Required MCP servers
        self.required_servers = [
            "crypto-sentiment-mcp",  # Social sentiment
            "crypto-feargreed-mcp",  # Fear & Greed Index
            "cryptopanic-mcp-server",  # News sentiment
        ]

        # Optional MCP servers
        self.optional_servers = [
            "grok-search-mcp",  # Social media analysis
        ]

    async def analyze_crowd_sentiment(self, asset: str = "bitcoin") -> Dict[str, Any]:
        """
        Analyze current crowd sentiment and positioning

        Args:
            asset: Cryptocurrency slug (e.g., 'bitcoin', 'ethereum')

        Returns:
            {
                "asset": str,
                "fear_greed_index": int,  # 0-100
                "sentiment_regime": SentimentRegime,
                "social_metrics": {
                    "sentiment_balance": float,
                    "social_volume": int,
                    "social_dominance": float
                },
                "interpretation": str,
                "contrarian_signal": ContrarianSignal,
                "reasoning": str
            }

        Strategy:
        1. Query crypto-feargreed-mcp for Fear & Greed Index
        2. Query crypto-sentiment-mcp for social metrics
        3. Determine sentiment regime
        4. Generate contrarian signal
        5. Provide interpretation
        """
        # Placeholder for MCP integration
        return {
            "asset": asset,
            "fear_greed_index": 68,  # Greed territory
            "sentiment_regime": SentimentRegime.GREED.value,
            "social_metrics": {
                "sentiment_balance": 12.5,  # Positive sentiment
                "social_volume": 15_000,  # Mentions
                "social_dominance": 25.3,  # % of crypto discussion
            },
            "interpretation": "Market in GREED regime (F&G: 68). Positive sentiment balance "
            "with elevated social volume indicates retail FOMO building. Approaching "
            "overbought territory where contrarian selling signals may emerge.",
            "contrarian_signal": ContrarianSignal.HOLD.value,
            "reasoning": "Greed level of 68 not yet extreme (needs >75 for strong sell signal). "
            "However, rising social volume and positive sentiment suggest caution. "
            "HOLD and monitor for extreme greed (>75) which would trigger SELL signal. "
            "Best contrarian opportunities emerge at extreme fear (<25).",
        }

    async def detect_sentiment_extremes(
        self, asset: str = "bitcoin", lookback_days: int = 90
    ) -> Dict[str, Any]:
        """
        Detect sentiment extremes and historical patterns

        Args:
            asset: Cryptocurrency slug
            lookback_days: Days of historical data to analyze

        Returns:
            {
                "asset": str,
                "current_percentile": float,  # Where current sentiment ranks
                "is_extreme": bool,  # Whether sentiment is at extreme (<25 or >75)
                "extreme_events": List[Dict],
                "pattern_analysis": {
                    "extreme_fear_opportunities": int,
                    "extreme_greed_warnings": int,
                    "mean_reversion_timeframe": str
                },
                "current_signal": str,
                "reasoning": str
            }

        Strategy:
        1. Query historical Fear & Greed data
        2. Calculate sentiment percentiles
        3. Identify past extreme events
        4. Analyze mean reversion patterns
        5. Generate current signal based on extremes
        """
        # Placeholder for MCP integration
        current_percentile = 62  # 62nd percentile (above average)
        is_extreme = current_percentile < 25 or current_percentile > 75

        return {
            "asset": asset,
            "current_percentile": current_percentile,
            "is_extreme": is_extreme,
            "extreme_events": [
                {
                    "date": "2024-11-15",
                    "fear_greed": 82,
                    "regime": "extreme_greed",
                    "outcome": "15% correction within 2 weeks",
                },
                {
                    "date": "2024-08-05",
                    "fear_greed": 22,
                    "regime": "extreme_fear",
                    "outcome": "35% rally within 4 weeks",
                },
            ],
            "pattern_analysis": {
                "extreme_fear_opportunities": 3,  # Last 90 days
                "extreme_greed_warnings": 2,
                "mean_reversion_timeframe": "2-4 weeks",
            },
            "current_signal": "monitor_for_extreme",
            "reasoning": "Current sentiment at 62nd percentile - above average but not extreme. "
            "Historical analysis shows extreme fear (<25) creates 2-4 week buying opportunities "
            "with avg 30%+ gains. Extreme greed (>75) triggers 2-4 week corrections avg 10-15%. "
            "Not at extreme now - monitor for <25 (buy signal) or >75 (sell signal).",
        }

    async def track_whale_activity(self, asset: str = "bitcoin") -> Dict[str, Any]:
        """
        Track whale/smart money activity vs. retail sentiment

        Args:
            asset: Cryptocurrency slug

        Returns:
            {
                "asset": str,
                "whale_sentiment": str,  # "bullish", "bearish", "neutral"
                "retail_sentiment": str,
                "divergence_detected": bool,
                "whale_metrics": {
                    "large_transaction_volume": float,
                    "exchange_whale_ratio": float,
                    "accumulation_distribution": str
                },
                "signal": str,
                "reasoning": str
            }

        Strategy:
        1. Query on-chain metrics for large transactions
        2. Analyze exchange inflow/outflow by wallet size
        3. Compare whale behavior vs. retail sentiment
        4. Detect bullish divergences (whales buying, retail fearful)
        5. Detect bearish divergences (whales selling, retail greedy)
        """
        # Placeholder for MCP integration (would need on-chain MCP server)
        return {
            "asset": asset,
            "whale_sentiment": "bullish",
            "retail_sentiment": "neutral_to_bullish",
            "divergence_detected": False,
            "whale_metrics": {
                "large_transaction_volume": 12_500_000_000,  # $12.5B
                "exchange_whale_ratio": 0.68,  # More off-exchange than on
                "accumulation_distribution": "accumulation",
            },
            "signal": "aligned_bullish",
            "reasoning": "Whales showing accumulation behavior with 68% of large wallets "
            "moving funds off exchanges (self-custody = bullish). Retail sentiment also "
            "bullish (F&G: 68). No divergence detected - both whales and retail aligned "
            "bullish. Strong signal when whales accumulate during retail fear.",
        }

    async def analyze_news_sentiment(
        self, asset: str = "bitcoin", period_days: int = 7
    ) -> Dict[str, Any]:
        """
        Analyze news sentiment and narrative shifts

        Args:
            asset: Cryptocurrency to analyze
            period_days: Days of news to analyze

        Returns:
            {
                "asset": str,
                "news_sentiment": str,  # "bullish", "bearish", "neutral"
                "sentiment_score": float,  # -1 to +1
                "top_narratives": List[str],
                "fud_fomo_index": float,  # Fear vs hype ratio
                "headline_analysis": {
                    "positive_count": int,
                    "negative_count": int,
                    "neutral_count": int
                },
                "narrative_shift": str,
                "reasoning": str
            }

        Strategy:
        1. Query cryptopanic-mcp for recent news
        2. Classify sentiment (bullish/bearish/neutral)
        3. Extract top narratives/themes
        4. Calculate FUD/FOMO ratio
        5. Detect narrative shifts
        """
        # Placeholder for MCP integration
        return {
            "asset": asset,
            "news_sentiment": "bullish",
            "sentiment_score": 0.65,  # Positive
            "top_narratives": [
                "ETF inflows accelerating",
                "Institutional adoption",
                "Halving cycle dynamics",
                "Inflation hedge narrative",
            ],
            "fud_fomo_index": 0.35,  # More FOMO than FUD
            "headline_analysis": {
                "positive_count": 42,
                "negative_count": 18,
                "neutral_count": 30,
            },
            "narrative_shift": "bullish_momentum_building",
            "reasoning": "News sentiment strongly positive (0.65) with 42 bullish vs 18 bearish "
            "headlines over past week. Top narratives focus on institutional adoption and "
            "ETF flows - both fundamental drivers. FUD/FOMO ratio of 0.35 shows FOMO building "
            "but not yet extreme. Narrative shift toward bullish momentum.",
        }

    async def generate_contrarian_signal(self, asset: str = "bitcoin") -> Dict[str, Any]:
        """
        Generate contrarian trading signal based on sentiment analysis

        Args:
            asset: Cryptocurrency slug

        Returns:
            {
                "asset": str,
                "signal": ContrarianSignal,
                "confidence": float,
                "entry_timing": str,
                "exit_timing": str,
                "rationale": {
                    "crowd_sentiment": str,
                    "sentiment_extreme": bool,
                    "whale_divergence": bool,
                    "news_sentiment": str
                },
                "risk_factors": List[str],
                "reasoning": str
            }

        Strategy:
        1. Call analyze_crowd_sentiment()
        2. Call detect_sentiment_extremes()
        3. Call track_whale_activity()
        4. Call analyze_news_sentiment()
        5. Synthesize contrarian signal with confidence
        """
        # In production, calls all analysis methods and synthesizes
        crowd = await self.analyze_crowd_sentiment(asset)
        extremes = await self.detect_sentiment_extremes(asset)
        whales = await self.track_whale_activity(asset)
        news = await self.analyze_news_sentiment(asset)

        return {
            "asset": asset,
            "signal": ContrarianSignal.HOLD.value,
            "confidence": 0.72,
            "entry_timing": "wait_for_extreme_fear",
            "exit_timing": "wait_for_extreme_greed",
            "rationale": {
                "crowd_sentiment": f"{crowd['sentiment_regime']} (F&G: {crowd['fear_greed_index']})",
                "sentiment_extreme": extremes["current_signal"],
                "whale_divergence": whales["divergence_detected"],
                "news_sentiment": news["news_sentiment"],
            },
            "risk_factors": [
                "Sentiment elevated but not extreme",
                "No contrarian divergence detected",
                "FOMO building in retail",
            ],
            "reasoning": f"Current Fear & Greed at {crowd['fear_greed_index']} ({crowd['sentiment_regime']}) - "
            f"above average but not extreme. Best contrarian opportunities emerge at extremes: "
            f"<25 (extreme fear = BUY) or >75 (extreme greed = SELL). "
            f"Current signal: {ContrarianSignal.HOLD.value}. "
            f"Entry timing: Wait for extreme fear (<25) to deploy capital. "
            f"Exit timing: Wait for extreme greed (>75) to take profits. "
            f"No whale divergence detected - whales and retail aligned {whales['whale_sentiment']}.",
        }

    async def synthesize_sentiment_outlook(
        self, asset: str = "bitcoin", horizon_days: int = 30
    ) -> Dict[str, Any]:
        """
        Synthesize comprehensive sentiment outlook for investment decision

        Args:
            asset: Cryptocurrency slug
            horizon_days: Investment horizon in days

        Returns:
            {
                "asset": str,
                "sentiment_assessment": str,
                "contrarian_opportunity": bool,
                "recommended_action": str,
                "confidence": float,
                "key_insights": List[str],
                "monitoring_triggers": {
                    "buy_trigger": str,
                    "sell_trigger": str
                },
                "reasoning": str
            }

        Strategy:
        1. Call all analysis methods
        2. Synthesize sentiment outlook
        3. Identify contrarian opportunities
        4. Provide actionable recommendations
        5. Set monitoring triggers
        """
        # In production, calls all analysis methods and synthesizes
        crowd = await self.analyze_crowd_sentiment(asset)
        extremes = await self.detect_sentiment_extremes(asset)
        whales = await self.track_whale_activity(asset)
        news = await self.analyze_news_sentiment(asset)
        signal = await self.generate_contrarian_signal(asset)

        # Map sentiment regime to assessment
        sentiment_map = {
            "extreme_fear": "contrarian_buy",
            "fear": "bearish",
            "neutral": "neutral",
            "greed": "bullish",
            "extreme_greed": "contrarian_sell",
        }
        sentiment_assessment = sentiment_map.get(crowd['sentiment_regime'], "neutral")

        return {
            "asset": asset,
            "sentiment_assessment": sentiment_assessment,
            "contrarian_opportunity": False,  # Not at sentiment extreme
            "recommended_action": "monitor_and_wait",
            "confidence": 0.76,
            "key_insights": [
                f"Fear & Greed at {crowd['fear_greed_index']} - elevated but not extreme",
                f"Whales {whales['whale_metrics']['accumulation_distribution']} - aligned with retail",
                f"News sentiment {news['news_sentiment']} with {news['sentiment_score']:.2f} score",
                "Best opportunities emerge at F&G <25 (extreme fear) or >75 (extreme greed)",
            ],
            "monitoring_triggers": {
                "buy_trigger": "Fear & Greed drops below 25 (extreme fear)",
                "sell_trigger": "Fear & Greed rises above 75 (extreme greed)",
            },
            "reasoning": f"Current sentiment regime: {crowd['sentiment_regime']} (F&G: {crowd['fear_greed_index']}). "
            f"No contrarian opportunity present - need extreme fear (<25) for buy signal or "
            f"extreme greed (>75) for sell signal. Whales showing {whales['whale_metrics']['accumulation_distribution']} "
            f"behavior, aligned with retail sentiment. News sentiment {news['news_sentiment']} "
            f"with {news['top_narratives'][:2]} as top narratives. "
            f"Recommended action: {signal['signal']} and monitor for sentiment extremes. "
            f"Historical analysis shows {extremes['pattern_analysis']['mean_reversion_timeframe']} "
            f"mean reversion after extremes.",
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
            "domain": "behavioral_finance",
            "capabilities": [
                "crowd_sentiment_analysis",
                "sentiment_extreme_detection",
                "whale_activity_tracking",
                "news_sentiment_analysis",
                "contrarian_signal_generation",
                "sentiment_synthesis",
            ],
            "required_mcps": self.required_servers,
            "optional_mcps": self.optional_servers,
            "token_efficiency": 0.0,  # Agent has no token reduction
            "use_cases": [
                "Contrarian market timing",
                "Sentiment extreme identification",
                "Whale vs. retail divergence",
                "FUD/FOMO cycle tracking",
                "Behavioral finance insights",
            ],
        }


# Convenience function for quick access
async def analyze_crypto_sentiment(
    asset: str = "bitcoin", analysis_type: str = "full", **kwargs
) -> Dict[str, Any]:
    """
    Convenience function for crypto sentiment analysis

    Args:
        asset: Cryptocurrency slug
        analysis_type: Type of analysis ("crowd", "extremes", "whales", "news", "signal", "full")
        **kwargs: Additional parameters for specific analysis types

    Returns:
        Analysis results dictionary

    Example:
        >>> result = await analyze_crypto_sentiment("bitcoin", "signal")
        >>> print(result["signal"])
        hold
    """
    analyst = CryptoSentimentAnalyst()

    if analysis_type == "crowd":
        return await analyst.analyze_crowd_sentiment(asset)
    elif analysis_type == "extremes":
        return await analyst.detect_sentiment_extremes(asset, **kwargs)
    elif analysis_type == "whales":
        return await analyst.track_whale_activity(asset)
    elif analysis_type == "news":
        return await analyst.analyze_news_sentiment(asset, **kwargs)
    elif analysis_type == "signal":
        return await analyst.generate_contrarian_signal(asset)
    elif analysis_type == "full":
        return await analyst.synthesize_sentiment_outlook(asset, **kwargs)
    else:
        raise ValueError(
            f"Invalid analysis_type '{analysis_type}'. "
            f"Valid types: crowd, extremes, whales, news, signal, full"
        )
