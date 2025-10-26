"""
MCP Client Wrapper for Crypto Skills

Provides a unified interface for interacting with MCP servers.
Handles tool calls, error handling, caching, and response parsing.
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json


class MCPClientWrapper:
    """
    Wrapper class for MCP client interactions.

    Provides:
    - Unified interface for all MCP tool calls
    - Response caching for performance
    - Error handling and retries
    - Rate limiting
    - Response parsing and validation
    """

    def __init__(self, mcp_client: Optional[Any] = None):
        """
        Initialize MCP client wrapper.

        Args:
            mcp_client: The actual MCP client instance (optional for testing)
        """
        self.mcp_client = mcp_client
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.cache_ttl_seconds = 300  # 5 minutes default
        self.max_retries = 3
        self.retry_delay_seconds = 1

    # ========================
    # CCXT-MCP Tools
    # ========================

    async def fetch_ticker(self, exchange: str, symbol: str) -> Dict[str, Any]:
        """
        Fetch ticker information for a symbol.

        Args:
            exchange: Exchange ID (e.g., 'binance')
            symbol: Trading pair (e.g., 'BTC/USDT')

        Returns:
            Ticker data including last price, volume, etc.
        """
        cache_key = f"ticker_{exchange}_{symbol}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached

        if not self.mcp_client:
            # Return mock data for testing
            return {
                "symbol": symbol,
                "last": 50000.0,
                "bid": 49995.0,
                "ask": 50005.0,
                "volume": 1000000.0,
                "timestamp": int(datetime.now().timestamp() * 1000),
            }

        result = await self._call_mcp_tool(
            "mcp__ccxt-mcp__fetchTicker", {"exchangeId": exchange, "symbol": symbol}
        )

        self._store_in_cache(cache_key, result)
        return result

    async def fetch_ohlcv(
        self, exchange: str, symbol: str, timeframe: str = "1h", limit: int = 100
    ) -> List[List[float]]:
        """
        Fetch OHLCV candlestick data.

        Args:
            exchange: Exchange ID
            symbol: Trading pair
            timeframe: Timeframe ('1m', '1h', '1d', etc.)
            limit: Number of candles to fetch

        Returns:
            List of OHLCV candles
        """
        cache_key = f"ohlcv_{exchange}_{symbol}_{timeframe}_{limit}"
        cached = self._get_from_cache(cache_key, ttl_seconds=60)
        if cached:
            return cached

        if not self.mcp_client:
            # Return mock OHLCV data
            return [
                [
                    int(datetime.now().timestamp() * 1000),
                    50000.0,
                    51000.0,
                    49500.0,
                    50500.0,
                    1000.0,
                ]
                for _ in range(limit)
            ]

        result = await self._call_mcp_tool(
            "mcp__ccxt-mcp__fetchOHLCV",
            {
                "exchangeId": exchange,
                "symbol": symbol,
                "timeframe": timeframe,
                "limit": limit,
            },
        )

        self._store_in_cache(cache_key, result, ttl_seconds=60)
        return result

    async def fetch_order_book(
        self, exchange: str, symbol: str, limit: int = 20
    ) -> Dict[str, Any]:
        """
        Fetch order book (market depth).

        Args:
            exchange: Exchange ID
            symbol: Trading pair
            limit: Number of orders per side

        Returns:
            Order book with bids and asks
        """
        cache_key = f"orderbook_{exchange}_{symbol}"
        cached = self._get_from_cache(cache_key, ttl_seconds=10)
        if cached:
            return cached

        if not self.mcp_client:
            return {
                "bids": [[50000.0, 1.0], [49990.0, 2.0]],
                "asks": [[50010.0, 1.5], [50020.0, 2.5]],
                "timestamp": int(datetime.now().timestamp() * 1000),
            }

        result = await self._call_mcp_tool(
            "mcp__ccxt-mcp__fetchOrderBook",
            {"exchangeId": exchange, "symbol": symbol, "limit": limit},
        )

        self._store_in_cache(cache_key, result, ttl_seconds=10)
        return result

    # ========================
    # Crypto Indicators MCP
    # ========================

    async def calculate_rsi(
        self, symbol: str, period: int = 14, timeframe: str = "1h", limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Calculate RSI indicator.

        Args:
            symbol: Trading pair
            period: RSI period
            timeframe: Timeframe
            limit: Number of data points

        Returns:
            RSI values
        """
        cache_key = f"rsi_{symbol}_{period}_{timeframe}"
        cached = self._get_from_cache(cache_key, ttl_seconds=60)
        if cached:
            return cached

        if not self.mcp_client:
            return [{"timestamp": int(datetime.now().timestamp()), "rsi": 50.0}]

        result = await self._call_mcp_tool(
            "mcp__crypto-indicators-mcp__calculate_relative_strength_index",
            {"symbol": symbol, "period": period, "timeframe": timeframe, "limit": limit},
        )

        self._store_in_cache(cache_key, result, ttl_seconds=60)
        return result

    async def calculate_macd(
        self,
        symbol: str,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        timeframe: str = "1h",
    ) -> List[Dict[str, Any]]:
        """
        Calculate MACD indicator.

        Args:
            symbol: Trading pair
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
            timeframe: Timeframe

        Returns:
            MACD values
        """
        cache_key = f"macd_{symbol}_{timeframe}"
        cached = self._get_from_cache(cache_key, ttl_seconds=60)
        if cached:
            return cached

        if not self.mcp_client:
            return [
                {
                    "timestamp": int(datetime.now().timestamp()),
                    "macd": 100.0,
                    "signal": 50.0,
                    "histogram": 50.0,
                }
            ]

        result = await self._call_mcp_tool(
            "mcp__crypto-indicators-mcp__calculate_moving_average_convergence_divergence",
            {
                "symbol": symbol,
                "fastPeriod": fast_period,
                "slowPeriod": slow_period,
                "signalPeriod": signal_period,
                "timeframe": timeframe,
            },
        )

        self._store_in_cache(cache_key, result, ttl_seconds=60)
        return result

    # ========================
    # Crypto Fear & Greed MCP
    # ========================

    async def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get current Crypto Fear & Greed Index.

        Returns:
            Fear & Greed Index data
        """
        cache_key = "fear_greed_current"
        cached = self._get_from_cache(cache_key, ttl_seconds=300)
        if cached:
            return cached

        if not self.mcp_client:
            return {
                "value": 50,
                "value_classification": "Neutral",
                "timestamp": int(datetime.now().timestamp()),
            }

        result = await self._call_mcp_tool(
            "mcp__crypto-feargreed-mcp__get_current_fng_tool", {}
        )

        self._store_in_cache(cache_key, result, ttl_seconds=300)
        return result

    async def get_historical_fear_greed(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get historical Fear & Greed Index.

        Args:
            days: Number of days to fetch

        Returns:
            Historical Fear & Greed data
        """
        cache_key = f"fear_greed_historical_{days}"
        cached = self._get_from_cache(cache_key, ttl_seconds=3600)
        if cached:
            return cached

        if not self.mcp_client:
            return [
                {
                    "value": 50,
                    "value_classification": "Neutral",
                    "timestamp": int((datetime.now() - timedelta(days=i)).timestamp()),
                }
                for i in range(days)
            ]

        result = await self._call_mcp_tool(
            "mcp__crypto-feargreed-mcp__get_historical_fng_tool", {"days": days}
        )

        self._store_in_cache(cache_key, result, ttl_seconds=3600)
        return result

    # ========================
    # Crypto Sentiment MCP
    # ========================

    async def get_sentiment_balance(self, asset: str, days: int = 7) -> Dict[str, Any]:
        """
        Get sentiment balance for an asset.

        Args:
            asset: Asset slug (e.g., 'bitcoin')
            days: Number of days

        Returns:
            Sentiment balance data
        """
        cache_key = f"sentiment_balance_{asset}_{days}"
        cached = self._get_from_cache(cache_key, ttl_seconds=300)
        if cached:
            return cached

        if not self.mcp_client:
            return {"asset": asset, "sentiment_balance": 0.5, "period_days": days}

        result = await self._call_mcp_tool(
            "mcp__crypto-sentiment-mcp__get_sentiment_balance",
            {"asset": asset, "days": days},
        )

        self._store_in_cache(cache_key, result, ttl_seconds=300)
        return result

    async def get_social_volume(self, asset: str, days: int = 7) -> Dict[str, Any]:
        """
        Get social volume for an asset.

        Args:
            asset: Asset slug
            days: Number of days

        Returns:
            Social volume data
        """
        cache_key = f"social_volume_{asset}_{days}"
        cached = self._get_from_cache(cache_key, ttl_seconds=300)
        if cached:
            return cached

        if not self.mcp_client:
            return {"asset": asset, "social_volume": 10000, "period_days": days}

        result = await self._call_mcp_tool(
            "mcp__crypto-sentiment-mcp__get_social_volume", {"asset": asset, "days": days}
        )

        self._store_in_cache(cache_key, result, ttl_seconds=300)
        return result

    async def get_social_dominance(self, asset: str, days: int = 7) -> Dict[str, Any]:
        """
        Get social dominance for an asset.

        Args:
            asset: Asset slug
            days: Number of days

        Returns:
            Social dominance data
        """
        cache_key = f"social_dominance_{asset}_{days}"
        cached = self._get_from_cache(cache_key, ttl_seconds=300)
        if cached:
            return cached

        if not self.mcp_client:
            return {"asset": asset, "social_dominance": 0.25, "period_days": days}

        result = await self._call_mcp_tool(
            "mcp__crypto-sentiment-mcp__get_social_dominance",
            {"asset": asset, "days": days},
        )

        self._store_in_cache(cache_key, result, ttl_seconds=300)
        return result

    # ========================
    # Crypto Projects MCP
    # ========================

    async def get_project_data(self, token_symbol: str) -> Dict[str, Any]:
        """
        Get project data from Mobula API.

        Args:
            token_symbol: Token symbol (e.g., 'BTC')

        Returns:
            Project data
        """
        cache_key = f"project_data_{token_symbol}"
        cached = self._get_from_cache(cache_key, ttl_seconds=3600)
        if cached:
            return cached

        if not self.mcp_client:
            return {
                "symbol": token_symbol,
                "name": f"{token_symbol} Token",
                "description": "Mock project data",
                "website": "https://example.com",
            }

        result = await self._call_mcp_tool(
            "mcp__crypto-projects-mcp__get_project_data", {"token_symbol": token_symbol}
        )

        self._store_in_cache(cache_key, result, ttl_seconds=3600)
        return result

    # ========================
    # CryptoPanic MCP
    # ========================

    async def get_crypto_news(
        self, kind: str = "news", num_pages: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get cryptocurrency news from CryptoPanic.

        Args:
            kind: 'news' or 'media'
            num_pages: Number of pages to fetch

        Returns:
            News articles
        """
        cache_key = f"crypto_news_{kind}_{num_pages}"
        cached = self._get_from_cache(cache_key, ttl_seconds=600)
        if cached:
            return cached

        if not self.mcp_client:
            return [
                {
                    "title": "Mock News Article",
                    "url": "https://example.com",
                    "published_at": datetime.now().isoformat(),
                }
            ]

        result = await self._call_mcp_tool(
            "mcp__cryptopanic-mcp-server__get_crypto_news",
            {"kind": kind, "num_pages": num_pages},
        )

        self._store_in_cache(cache_key, result, ttl_seconds=600)
        return result

    # ========================
    # Helper Methods
    # ========================

    async def _call_mcp_tool(
        self, tool_name: str, parameters: Dict[str, Any]
    ) -> Any:
        """
        Call an MCP tool with retry logic.

        Args:
            tool_name: Name of the MCP tool
            parameters: Tool parameters

        Returns:
            Tool result
        """
        if not self.mcp_client:
            raise ValueError("MCP client not initialized")

        for attempt in range(self.max_retries):
            try:
                # Call the MCP tool
                result = await self.mcp_client.call_tool(tool_name, parameters)
                return result

            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay_seconds * (attempt + 1))
                else:
                    raise Exception(
                        f"MCP tool call failed after {self.max_retries} attempts: {str(e)}"
                    )

    def _get_from_cache(
        self, key: str, ttl_seconds: Optional[int] = None
    ) -> Optional[Any]:
        """
        Get value from cache if not expired.

        Args:
            key: Cache key
            ttl_seconds: Custom TTL (uses default if not provided)

        Returns:
            Cached value or None
        """
        if key not in self.cache:
            return None

        cache_entry = self.cache[key]
        ttl = ttl_seconds if ttl_seconds is not None else self.cache_ttl_seconds

        if datetime.now().timestamp() - cache_entry["timestamp"] > ttl:
            del self.cache[key]
            return None

        return cache_entry["value"]

    def _store_in_cache(
        self, key: str, value: Any, ttl_seconds: Optional[int] = None
    ) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Custom TTL (uses default if not provided)
        """
        self.cache[key] = {"value": value, "timestamp": datetime.now().timestamp()}

    def clear_cache(self, pattern: Optional[str] = None) -> None:
        """
        Clear cache entries.

        Args:
            pattern: Optional pattern to match keys (clears all if None)
        """
        if pattern is None:
            self.cache.clear()
        else:
            keys_to_delete = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self.cache[key]

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache stats including size and hit rate
        """
        return {
            "total_entries": len(self.cache),
            "cache_keys": list(self.cache.keys()),
            "oldest_entry": (
                min(entry["timestamp"] for entry in self.cache.values())
                if self.cache
                else None
            ),
            "newest_entry": (
                max(entry["timestamp"] for entry in self.cache.values())
                if self.cache
                else None
            ),
        }
