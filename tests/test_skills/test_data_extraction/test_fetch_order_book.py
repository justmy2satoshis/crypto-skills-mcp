"""
Unit tests for OrderBookFetcher Skill

Tests order book fetching functionality including:
- Order book data structure
- Bid/ask level processing
- Depth limit handling
- Verbose parameter functionality
- Exchange initialization
- Market depth analysis
"""

import pytest
from unittest.mock import MagicMock
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.data_extraction.fetch_order_book import OrderBookFetcher, fetch_order_book


class TestOrderBookFetcherInit:
    """Test OrderBookFetcher initialization"""

    def test_initialization_default_exchange(self):
        """Test fetcher initializes with default exchange"""
        fetcher = OrderBookFetcher()

        assert fetcher.exchange_id == "binance"
        assert fetcher is not None

    def test_initialization_custom_exchange(self):
        """Test fetcher initializes with custom exchange"""
        fetcher = OrderBookFetcher(exchange_id="coinbase")

        assert fetcher.exchange_id == "coinbase"


class TestFetchMethod:
    """Test main fetch() method"""

    def test_fetch_basic_call(self):
        """Test basic fetch() call returns correct structure"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT")

        # Verify structure
        assert "exchange" in result
        assert result["exchange"] == "binance"
        assert "symbol" in result
        assert result["symbol"] == "BTC/USDT"
        assert "bids" in result
        assert "asks" in result
        assert "metadata" in result

    def test_fetch_verbose_true(self):
        """Test verbose=True returns full response with metadata"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=True)

        # Full response should have all fields
        assert "exchange" in result
        assert "symbol" in result
        assert "bids" in result
        assert "asks" in result
        assert "metadata" in result
        assert "token_reduction" in result["metadata"]
        assert "procedural" in result["metadata"]

    def test_fetch_verbose_false(self):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "bids" in result["data"]
        assert "asks" in result["data"]
        assert "exchange" not in result
        assert "symbol" not in result
        assert "metadata" not in result

    def test_fetch_with_limit(self):
        """Test fetch() with depth limit parameter"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", limit=10)

        # Should return structure (limit would be used in actual MCP call)
        assert "bids" in result
        assert "asks" in result

    def test_fetch_different_symbols(self):
        """Test fetch() with different trading pairs"""
        fetcher = OrderBookFetcher()

        btc_result = fetcher.fetch("BTC/USDT")
        eth_result = fetcher.fetch("ETH/USDT")

        assert btc_result["symbol"] == "BTC/USDT"
        assert eth_result["symbol"] == "ETH/USDT"


class TestDataStructure:
    """Test order book data structure"""

    def test_data_structure_bids_array(self):
        """Test bids are returned as array"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT")

        assert isinstance(result["bids"], list)

    def test_data_structure_asks_array(self):
        """Test asks are returned as array"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT")

        assert isinstance(result["asks"], list)

    def test_data_structure_verbose_false_format(self):
        """Test verbose=False has bids/asks under data key"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=False)

        assert "data" in result
        assert isinstance(result["data"]["bids"], list)
        assert isinstance(result["data"]["asks"], list)


class TestMetadata:
    """Test metadata fields"""

    def test_metadata_token_reduction(self):
        """Test metadata includes token_reduction"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT")

        assert "token_reduction" in result["metadata"]
        assert result["metadata"]["token_reduction"] == 0.85

    def test_metadata_procedural_flag(self):
        """Test metadata includes procedural flag"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT")

        assert "procedural" in result["metadata"]
        assert result["metadata"]["procedural"] is True


class TestExchangeHandling:
    """Test exchange ID handling"""

    def test_binance_exchange(self):
        """Test fetcher works with Binance"""
        fetcher = OrderBookFetcher(exchange_id="binance")

        result = fetcher.fetch("BTC/USDT")

        assert result["exchange"] == "binance"

    def test_coinbase_exchange(self):
        """Test fetcher works with Coinbase"""
        fetcher = OrderBookFetcher(exchange_id="coinbase")

        result = fetcher.fetch("BTC/USDT")

        assert result["exchange"] == "coinbase"

    def test_kraken_exchange(self):
        """Test fetcher works with Kraken"""
        fetcher = OrderBookFetcher(exchange_id="kraken")

        result = fetcher.fetch("BTC/USDT")

        assert result["exchange"] == "kraken"


class TestConvenienceFunction:
    """Test convenience function"""

    def test_fetch_order_book_default(self):
        """Test convenience function with defaults"""
        result = fetch_order_book("BTC/USDT")

        assert "exchange" in result
        assert result["exchange"] == "binance"
        assert "symbol" in result
        assert result["symbol"] == "BTC/USDT"

    def test_fetch_order_book_custom_exchange(self):
        """Test convenience function with custom exchange"""
        result = fetch_order_book("BTC/USDT", exchange_id="coinbase")

        assert result["exchange"] == "coinbase"

    def test_fetch_order_book_returns_order_book(self):
        """Test convenience function returns order book structure"""
        result = fetch_order_book("BTC/USDT")

        assert "bids" in result
        assert "asks" in result


class TestVerboseParameter:
    """Test verbose parameter across different scenarios"""

    def test_verbose_true_includes_exchange(self):
        """Test verbose=True includes exchange field"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=True)

        assert "exchange" in result

    def test_verbose_true_includes_symbol(self):
        """Test verbose=True includes symbol field"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=True)

        assert "symbol" in result

    def test_verbose_true_includes_metadata(self):
        """Test verbose=True includes metadata"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=True)

        assert "metadata" in result

    def test_verbose_false_excludes_exchange(self):
        """Test verbose=False excludes exchange field"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=False)

        assert "exchange" not in result

    def test_verbose_false_excludes_symbol(self):
        """Test verbose=False excludes symbol field"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=False)

        assert "symbol" not in result

    def test_verbose_false_excludes_metadata(self):
        """Test verbose=False excludes metadata"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=False)

        assert "metadata" not in result

    def test_verbose_false_has_data_key(self):
        """Test verbose=False wraps result in data key"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", verbose=False)

        assert "data" in result
        assert "bids" in result["data"]
        assert "asks" in result["data"]


class TestLimitParameter:
    """Test depth limit parameter"""

    def test_limit_none_default(self):
        """Test limit=None uses default behavior"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", limit=None)

        assert "bids" in result
        assert "asks" in result

    def test_limit_numeric_value(self):
        """Test limit with numeric value"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", limit=20)

        # Should accept limit parameter (actual limiting would happen in MCP call)
        assert "bids" in result
        assert "asks" in result

    def test_limit_small_value(self):
        """Test limit with small depth value"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", limit=5)

        assert "bids" in result
        assert "asks" in result

    def test_limit_large_value(self):
        """Test limit with large depth value"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT", limit=100)

        assert "bids" in result
        assert "asks" in result


class TestSymbolHandling:
    """Test different trading pair symbols"""

    def test_btc_usdt_symbol(self):
        """Test BTC/USDT symbol"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT")

        assert result["symbol"] == "BTC/USDT"

    def test_eth_usdt_symbol(self):
        """Test ETH/USDT symbol"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("ETH/USDT")

        assert result["symbol"] == "ETH/USDT"

    def test_sol_usdt_symbol(self):
        """Test SOL/USDT symbol"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("SOL/USDT")

        assert result["symbol"] == "SOL/USDT"

    def test_btc_usd_symbol(self):
        """Test BTC/USD symbol (different quote currency)"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USD")

        assert result["symbol"] == "BTC/USD"


class TestResponseConsistency:
    """Test response format consistency"""

    def test_verbose_true_always_has_exchange(self):
        """Test verbose=True consistently includes exchange"""
        fetcher = OrderBookFetcher()

        result1 = fetcher.fetch("BTC/USDT", verbose=True)
        result2 = fetcher.fetch("ETH/USDT", verbose=True)

        assert "exchange" in result1
        assert "exchange" in result2

    def test_verbose_true_always_has_symbol(self):
        """Test verbose=True consistently includes symbol"""
        fetcher = OrderBookFetcher()

        result1 = fetcher.fetch("BTC/USDT", verbose=True)
        result2 = fetcher.fetch("ETH/USDT", verbose=True)

        assert "symbol" in result1
        assert "symbol" in result2

    def test_verbose_false_always_minimal(self):
        """Test verbose=False consistently returns minimal format"""
        fetcher = OrderBookFetcher()

        result1 = fetcher.fetch("BTC/USDT", verbose=False)
        result2 = fetcher.fetch("ETH/USDT", verbose=False)

        # Both should have only data key
        assert set(result1.keys()) == {"data"}
        assert set(result2.keys()) == {"data"}

    def test_bids_asks_always_present(self):
        """Test bids and asks are always present"""
        fetcher = OrderBookFetcher()

        verbose_result = fetcher.fetch("BTC/USDT", verbose=True)
        minimal_result = fetcher.fetch("BTC/USDT", verbose=False)

        # Verbose format
        assert "bids" in verbose_result
        assert "asks" in verbose_result

        # Minimal format (under data key)
        assert "bids" in minimal_result["data"]
        assert "asks" in minimal_result["data"]


class TestTokenReduction:
    """Test token reduction metadata"""

    def test_token_reduction_value(self):
        """Test token reduction is 85% (0.85)"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT")

        assert result["metadata"]["token_reduction"] == 0.85

    def test_token_reduction_consistent(self):
        """Test token reduction value is consistent across calls"""
        fetcher = OrderBookFetcher()

        result1 = fetcher.fetch("BTC/USDT")
        result2 = fetcher.fetch("ETH/USDT")

        assert result1["metadata"]["token_reduction"] == result2["metadata"]["token_reduction"]


class TestProceduralFlag:
    """Test procedural implementation flag"""

    def test_procedural_flag_true(self):
        """Test procedural flag is True"""
        fetcher = OrderBookFetcher()

        result = fetcher.fetch("BTC/USDT")

        assert result["metadata"]["procedural"] is True

    def test_procedural_flag_consistent(self):
        """Test procedural flag is consistent"""
        fetcher = OrderBookFetcher()

        result1 = fetcher.fetch("BTC/USDT")
        result2 = fetcher.fetch("ETH/USDT")

        assert result1["metadata"]["procedural"] == result2["metadata"]["procedural"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
