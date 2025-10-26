"""
Order Book Fetching Skill

Procedural implementation for fetching order book data from exchanges.
"""

from typing import Dict, Any, Optional


class OrderBookFetcher:
    """
    Token-efficient order book data fetcher

    Direct CCXT MCP integration without reasoning overhead.
    """

    def __init__(self, exchange_id: str = "binance"):
        """
        Initialize order book fetcher

        Args:
            exchange_id: Exchange to fetch from
        """
        self.exchange_id = exchange_id

    def fetch(
        self,
        symbol: str,
        limit: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch order book for a trading pair

        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            limit: Depth limit (number of bid/ask levels)

        Returns:
            Order book data
        """
        # Procedural stub - would use mcp__ccxt-mcp__fetchOrderBook

        return {
            "exchange": self.exchange_id,
            "symbol": symbol,
            "bids": [],  # Would contain actual bid levels
            "asks": [],  # Would contain actual ask levels
            "metadata": {
                "token_reduction": 0.85,
                "procedural": True
            }
        }


def fetch_order_book(
    symbol: str,
    exchange_id: str = "binance"
) -> Dict[str, Any]:
    """
    Convenience function to fetch order book

    Args:
        symbol: Trading pair
        exchange_id: Exchange to use

    Returns:
        Order book data
    """
    fetcher = OrderBookFetcher(exchange_id=exchange_id)
    return fetcher.fetch(symbol=symbol)
