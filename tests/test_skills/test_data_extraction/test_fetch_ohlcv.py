"""
Unit tests for OHLCVFetcher Skill

Tests OHLCV data fetching functionality including:
- Single exchange OHLCV fetching
- Multi-exchange parallel fetching
- Volume-weighted price aggregation
- Caching mechanism
- Data normalization
- Verbose parameter functionality
- Error handling with graceful degradation
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from skills.data_extraction.fetch_ohlcv import OHLCVFetcher


class TestOHLCVFetcherInit:
    """Test OHLCVFetcher initialization"""

    def test_initialization(self):
        """Test fetcher initializes with MCP client"""
        mock_client = MagicMock()
        fetcher = OHLCVFetcher(mock_client)

        assert fetcher.mcp == mock_client
        assert fetcher.cache == {}
        assert fetcher is not None


class TestFetchMethod:
    """Test main fetch() method"""

    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client with OHLCV response"""
        client = AsyncMock()

        # Mock ccxt OHLCV response format: [[timestamp, open, high, low, close, volume], ...]
        client.call_tool.return_value = {
            "data": [
                [1729944000000, 43500.0, 44000.0, 43200.0, 43800.0, 1250000.0],
                [1729947600000, 43800.0, 44200.0, 43600.0, 44100.0, 1180000.0],
                [1729951200000, 44100.0, 44500.0, 43900.0, 44300.0, 1320000.0],
            ]
        }

        return client

    @pytest.mark.asyncio
    async def test_fetch_basic_call(self, mock_mcp_client):
        """Test basic fetch() call returns correct structure"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT", timeframe="1h", limit=100)

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "ccxt-mcp"
        assert "symbol" in result
        assert result["symbol"] == "BTC/USDT"
        assert "data_type" in result
        assert result["data_type"] == "ohlcv"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_fetch_verbose_true(self, mock_mcp_client):
        """Test verbose=True returns full response with metadata"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT", verbose=True)

        # Full response should have all fields
        assert "timestamp" in result
        assert "source" in result
        assert "symbol" in result
        assert "data_type" in result
        assert "data" in result
        assert "metadata" in result
        assert "exchange" in result["metadata"]
        assert "timeframe" in result["metadata"]
        assert "count" in result["metadata"]
        assert "confidence" in result["metadata"]

    @pytest.mark.asyncio
    async def test_fetch_verbose_false(self, mock_mcp_client):
        """Test verbose=False returns minimal response (65.7% size reduction)"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT", verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "source" not in result
        assert "metadata" not in result

    @pytest.mark.asyncio
    async def test_fetch_calls_mcp_with_correct_params(self, mock_mcp_client):
        """Test fetch() calls MCP with correct parameters"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        await fetcher.fetch("BTC/USDT", timeframe="4h", limit=200, exchange="coinbase")

        # Verify MCP call parameters
        mock_mcp_client.call_tool.assert_called_once_with(
            "mcp__ccxt-mcp__fetchOHLCV",
            {
                "exchangeId": "coinbase",
                "symbol": "BTC/USDT",
                "timeframe": "4h",
                "limit": 200,
            },
        )

    @pytest.mark.asyncio
    async def test_fetch_default_parameters(self, mock_mcp_client):
        """Test fetch() uses correct default parameters"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        await fetcher.fetch("BTC/USDT")

        # Verify default parameters
        mock_mcp_client.call_tool.assert_called_once_with(
            "mcp__ccxt-mcp__fetchOHLCV",
            {
                "exchangeId": "binance",  # Default exchange
                "symbol": "BTC/USDT",
                "timeframe": "1h",  # Default timeframe
                "limit": 100,  # Default limit
            },
        )


class TestDataNormalization:
    """Test OHLCV data normalization"""

    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client with raw OHLCV data"""
        client = AsyncMock()
        client.call_tool.return_value = {
            "data": [
                [1729944000000, 43500.0, 44000.0, 43200.0, 43800.0, 1250000.0],
                [1729947600000, 43800.0, 44200.0, 43600.0, 44100.0, 1180000.0],
            ]
        }
        return client

    @pytest.mark.asyncio
    async def test_normalization_extracts_all_fields(self, mock_mcp_client):
        """Test normalization extracts all OHLCV fields correctly"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT")
        candle = result["data"][0]

        # Verify all fields present
        assert "timestamp" in candle
        assert "open" in candle
        assert "high" in candle
        assert "low" in candle
        assert "close" in candle
        assert "volume" in candle

    @pytest.mark.asyncio
    async def test_normalization_correct_values(self, mock_mcp_client):
        """Test normalization converts values correctly"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT")
        candle = result["data"][0]

        # Verify values match raw data
        assert candle["timestamp"] == 1729944000000
        assert candle["open"] == 43500.0
        assert candle["high"] == 44000.0
        assert candle["low"] == 43200.0
        assert candle["close"] == 43800.0
        assert candle["volume"] == 1250000.0

    @pytest.mark.asyncio
    async def test_normalization_converts_types(self, mock_mcp_client):
        """Test normalization converts to correct Python types"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT")
        candle = result["data"][0]

        # Verify types
        assert isinstance(candle["timestamp"], int)
        assert isinstance(candle["open"], float)
        assert isinstance(candle["high"], float)
        assert isinstance(candle["low"], float)
        assert isinstance(candle["close"], float)
        assert isinstance(candle["volume"], float)

    @pytest.mark.asyncio
    async def test_normalization_handles_multiple_candles(self, mock_mcp_client):
        """Test normalization processes multiple candles"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT")

        # Should have 2 candles from mock data
        assert len(result["data"]) == 2
        assert result["metadata"]["count"] == 2

    @pytest.mark.asyncio
    async def test_normalization_skips_incomplete_candles(self):
        """Test normalization skips candles with missing fields"""
        mock_client = AsyncMock()
        # Incomplete candle (only 4 fields instead of 6)
        mock_client.call_tool.return_value = {
            "data": [
                [1729944000000, 43500.0, 44000.0, 43200.0],  # Missing close and volume
                [1729947600000, 43800.0, 44200.0, 43600.0, 44100.0, 1180000.0],  # Complete
            ]
        }

        fetcher = OHLCVFetcher(mock_client)
        result = await fetcher.fetch("BTC/USDT")

        # Should only include complete candle
        assert len(result["data"]) == 1
        assert result["data"][0]["timestamp"] == 1729947600000


class TestMetadata:
    """Test metadata fields"""

    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client"""
        client = AsyncMock()
        client.call_tool.return_value = {
            "data": [
                [1729944000000, 43500.0, 44000.0, 43200.0, 43800.0, 1250000.0],
            ]
        }
        return client

    @pytest.mark.asyncio
    async def test_metadata_exchange(self, mock_mcp_client):
        """Test metadata includes exchange"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT", exchange="kraken")

        assert result["metadata"]["exchange"] == "kraken"

    @pytest.mark.asyncio
    async def test_metadata_timeframe(self, mock_mcp_client):
        """Test metadata includes timeframe"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT", timeframe="4h")

        assert result["metadata"]["timeframe"] == "4h"

    @pytest.mark.asyncio
    async def test_metadata_count(self, mock_mcp_client):
        """Test metadata includes candle count"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT")

        assert result["metadata"]["count"] == 1

    @pytest.mark.asyncio
    async def test_metadata_confidence_default(self, mock_mcp_client):
        """Test metadata includes default confidence (1.0)"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        result = await fetcher.fetch("BTC/USDT")

        assert result["metadata"]["confidence"] == 1.0


class TestCaching:
    """Test caching mechanism"""

    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client"""
        client = AsyncMock()
        client.call_tool.return_value = {
            "data": [
                [1729944000000, 43500.0, 44000.0, 43200.0, 43800.0, 1250000.0],
            ]
        }
        return client

    @pytest.mark.asyncio
    async def test_caching_stores_result(self, mock_mcp_client):
        """Test caching stores fetch result"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        await fetcher.fetch("BTC/USDT", timeframe="1h", limit=100)

        # Verify cache key created
        cache_key = "binance:BTC/USDT:1h:100"
        assert cache_key in fetcher.cache

    @pytest.mark.asyncio
    async def test_caching_returns_cached_data(self, mock_mcp_client):
        """Test caching returns cached data on second call"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        # First call - fetches from MCP
        await fetcher.fetch("BTC/USDT")
        assert mock_mcp_client.call_tool.call_count == 1

        # Second call - should return cached data
        await fetcher.fetch("BTC/USDT")
        # Should not call MCP again (still 1 call)
        assert mock_mcp_client.call_tool.call_count == 1

    @pytest.mark.asyncio
    async def test_caching_different_params_separate_cache(self, mock_mcp_client):
        """Test different parameters create separate cache entries"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        # Different timeframes should cache separately
        await fetcher.fetch("BTC/USDT", timeframe="1h")
        await fetcher.fetch("BTC/USDT", timeframe="4h")

        # Should make 2 MCP calls (different cache keys)
        assert mock_mcp_client.call_tool.call_count == 2
        assert len(fetcher.cache) == 2

    @pytest.mark.asyncio
    async def test_caching_expires_after_15_minutes(self, mock_mcp_client):
        """Test cache expires after 15 minutes TTL"""
        fetcher = OHLCVFetcher(mock_mcp_client)

        # First fetch
        await fetcher.fetch("BTC/USDT")

        # Manually expire cache by setting old timestamp
        cache_key = "binance:BTC/USDT:1h:100"
        old_data, _ = fetcher.cache[cache_key]
        expired_time = datetime.utcnow() - timedelta(minutes=20)
        fetcher.cache[cache_key] = (old_data, expired_time)

        # Second fetch should re-fetch from MCP (cache expired)
        await fetcher.fetch("BTC/USDT")
        assert mock_mcp_client.call_tool.call_count == 2


class TestErrorHandling:
    """Test error handling and graceful degradation"""

    @pytest.mark.asyncio
    async def test_error_with_cached_data_returns_cache(self):
        """Test error returns cached data if available"""
        mock_client = AsyncMock()

        # First call succeeds
        mock_client.call_tool.return_value = {
            "data": [
                [1729944000000, 43500.0, 44000.0, 43200.0, 43800.0, 1250000.0],
            ]
        }

        fetcher = OHLCVFetcher(mock_client)
        await fetcher.fetch("BTC/USDT")

        # Second call fails
        mock_client.call_tool.side_effect = Exception("Network error")

        # Should return cached data instead of raising
        result = await fetcher.fetch("BTC/USDT")

        assert "data" in result
        assert len(result["data"]) == 1
        assert "warning" in result["metadata"]
        assert "Network error" in result["metadata"]["warning"]

    @pytest.mark.asyncio
    async def test_error_with_cached_data_reduces_confidence(self):
        """Test error with cached data reduces confidence to 0.7"""
        mock_client = AsyncMock()

        # First call succeeds
        mock_client.call_tool.return_value = {
            "data": [
                [1729944000000, 43500.0, 44000.0, 43200.0, 43800.0, 1250000.0],
            ]
        }

        fetcher = OHLCVFetcher(mock_client)
        await fetcher.fetch("BTC/USDT")

        # Second call fails
        mock_client.call_tool.side_effect = Exception("API error")

        result = await fetcher.fetch("BTC/USDT")

        # Confidence reduced to 0.7
        assert result["metadata"]["confidence"] == 0.7

    @pytest.mark.asyncio
    async def test_error_without_cache_raises(self):
        """Test error without cached data raises exception"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = Exception("Network error")

        fetcher = OHLCVFetcher(mock_client)

        # Should raise exception (no cached data)
        with pytest.raises(Exception, match="Network error"):
            await fetcher.fetch("BTC/USDT")


class TestMultiExchangeFetch:
    """Test multi-exchange parallel fetching"""

    @pytest.fixture
    def mock_mcp_client_multi(self):
        """Create mock MCP client for multi-exchange"""
        client = AsyncMock()

        # Different data for each exchange
        def mock_call(tool_name, params):
            exchange = params["exchangeId"]
            if exchange == "binance":
                return {
                    "data": [
                        [1729944000000, 43500.0, 44000.0, 43200.0, 43800.0, 1000000.0],
                    ]
                }
            elif exchange == "coinbase":
                return {
                    "data": [
                        [1729944000000, 43600.0, 44100.0, 43300.0, 43900.0, 800000.0],
                    ]
                }
            elif exchange == "kraken":
                return {
                    "data": [
                        [1729944000000, 43550.0, 44050.0, 43250.0, 43850.0, 600000.0],
                    ]
                }

        client.call_tool.side_effect = mock_call
        return client

    @pytest.mark.asyncio
    async def test_multi_exchange_fetch_calls_all_exchanges(self, mock_mcp_client_multi):
        """Test multi-exchange fetch calls all specified exchanges"""
        fetcher = OHLCVFetcher(mock_mcp_client_multi)

        await fetcher.fetch_multi_exchange(
            "BTC/USDT",
            exchanges=["binance", "coinbase", "kraken"],
        )

        # Should make 3 MCP calls
        assert mock_mcp_client_multi.call_tool.call_count == 3

    @pytest.mark.asyncio
    async def test_multi_exchange_fetch_default_exchanges(self, mock_mcp_client_multi):
        """Test multi-exchange fetch uses default exchanges"""
        fetcher = OHLCVFetcher(mock_mcp_client_multi)

        result = await fetcher.fetch_multi_exchange("BTC/USDT")

        # Default: binance, coinbase, kraken
        assert len(result["metadata"]["exchanges"]) == 3
        assert "binance" in result["metadata"]["exchanges"]
        assert "coinbase" in result["metadata"]["exchanges"]
        assert "kraken" in result["metadata"]["exchanges"]

    @pytest.mark.asyncio
    async def test_multi_exchange_aggregation_structure(self, mock_mcp_client_multi):
        """Test multi-exchange aggregation returns correct structure"""
        fetcher = OHLCVFetcher(mock_mcp_client_multi)

        result = await fetcher.fetch_multi_exchange("BTC/USDT")

        # Verify structure
        assert "timestamp" in result
        assert "source" in result
        assert result["source"] == "ccxt-mcp (multi-exchange)"
        assert "data_type" in result
        assert result["data_type"] == "ohlcv_aggregated"
        assert "data" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_multi_exchange_aggregation_includes_exchanges(self, mock_mcp_client_multi):
        """Test aggregated candles include exchange list"""
        fetcher = OHLCVFetcher(mock_mcp_client_multi)

        result = await fetcher.fetch_multi_exchange("BTC/USDT")

        candle = result["data"][0]

        # Aggregated candle should include exchanges field
        assert "exchanges" in candle
        assert len(candle["exchanges"]) == 3

    @pytest.mark.asyncio
    async def test_multi_exchange_verbose_false(self, mock_mcp_client_multi):
        """Test multi-exchange verbose=False returns minimal response"""
        fetcher = OHLCVFetcher(mock_mcp_client_multi)

        result = await fetcher.fetch_multi_exchange("BTC/USDT", verbose=False)

        # Minimal response should only have data
        assert "data" in result
        assert "timestamp" not in result
        assert "metadata" not in result


class TestVolumeWeightedAggregation:
    """Test volume-weighted price aggregation"""

    @pytest.fixture
    def mock_mcp_client_vwap(self):
        """Create mock MCP client for VWAP testing"""
        client = AsyncMock()

        def mock_call(tool_name, params):
            exchange = params["exchangeId"]
            # Exchange A: price 100, volume 1000
            # Exchange B: price 200, volume 500
            # Expected VWAP: (100*1000 + 200*500) / (1000+500) = 133.33
            if exchange == "exchangeA":
                return {
                    "data": [
                        [1729944000000, 100.0, 110.0, 90.0, 105.0, 1000.0],
                    ]
                }
            elif exchange == "exchangeB":
                return {
                    "data": [
                        [1729944000000, 200.0, 210.0, 190.0, 205.0, 500.0],
                    ]
                }

        client.call_tool.side_effect = mock_call
        return client

    @pytest.mark.asyncio
    async def test_vwap_calculation_weighted_by_volume(self, mock_mcp_client_vwap):
        """Test volume-weighted average price calculation"""
        fetcher = OHLCVFetcher(mock_mcp_client_vwap)

        result = await fetcher.fetch_multi_exchange(
            "BTC/USDT",
            exchanges=["exchangeA", "exchangeB"],
        )

        candle = result["data"][0]

        # VWAP open: (100*1000 + 200*500) / 1500 = 133.33
        expected_open = (100.0 * 1000.0 + 200.0 * 500.0) / 1500.0
        assert abs(candle["open"] - expected_open) < 0.01

    @pytest.mark.asyncio
    async def test_vwap_total_volume_sum(self, mock_mcp_client_vwap):
        """Test total volume is sum of all exchanges"""
        fetcher = OHLCVFetcher(mock_mcp_client_vwap)

        result = await fetcher.fetch_multi_exchange(
            "BTC/USDT",
            exchanges=["exchangeA", "exchangeB"],
        )

        candle = result["data"][0]

        # Total volume: 1000 + 500 = 1500
        assert candle["volume"] == 1500.0

    @pytest.mark.asyncio
    async def test_vwap_skips_zero_volume_candles(self):
        """Test aggregation skips candles with zero total volume"""
        mock_client = AsyncMock()

        def mock_call(tool_name, params):
            # Both exchanges return zero volume
            return {
                "data": [
                    [1729944000000, 100.0, 110.0, 90.0, 105.0, 0.0],
                ]
            }

        mock_client.call_tool.side_effect = mock_call

        fetcher = OHLCVFetcher(mock_client)
        result = await fetcher.fetch_multi_exchange(
            "BTC/USDT",
            exchanges=["exchangeA", "exchangeB"],
        )

        # Should skip zero-volume candles
        assert len(result["data"]) == 0


class TestMultiExchangeErrorHandling:
    """Test multi-exchange error handling"""

    @pytest.mark.asyncio
    async def test_multi_exchange_filters_failed_exchanges(self):
        """Test multi-exchange filters out exchanges that fail"""
        mock_client = AsyncMock()

        def mock_call(tool_name, params):
            exchange = params["exchangeId"]
            if exchange == "binance":
                return {
                    "data": [
                        [1729944000000, 43500.0, 44000.0, 43200.0, 43800.0, 1000000.0],
                    ]
                }
            elif exchange == "coinbase":
                # Coinbase fails
                raise Exception("Exchange API error")
            elif exchange == "kraken":
                return {
                    "data": [
                        [1729944000000, 43550.0, 44050.0, 43250.0, 43850.0, 600000.0],
                    ]
                }

        mock_client.call_tool.side_effect = mock_call

        fetcher = OHLCVFetcher(mock_client)
        result = await fetcher.fetch_multi_exchange(
            "BTC/USDT",
            exchanges=["binance", "coinbase", "kraken"],
        )

        # Should only include binance and kraken (coinbase failed)
        assert len(result["metadata"]["exchanges"]) == 2

    @pytest.mark.asyncio
    async def test_multi_exchange_raises_if_all_fail(self):
        """Test multi-exchange raises if all exchanges fail"""
        mock_client = AsyncMock()
        mock_client.call_tool.side_effect = Exception("All exchanges down")

        fetcher = OHLCVFetcher(mock_client)

        # Should raise ValueError
        with pytest.raises(ValueError, match="Failed to fetch from all exchanges"):
            await fetcher.fetch_multi_exchange(
                "BTC/USDT",
                exchanges=["binance", "coinbase"],
            )


class TestTimestampAlignment:
    """Test timestamp alignment across exchanges"""

    @pytest.mark.asyncio
    async def test_timestamp_alignment_groups_by_timestamp(self):
        """Test candles are grouped by timestamp across exchanges"""
        mock_client = AsyncMock()

        def mock_call(tool_name, params):
            exchange = params["exchangeId"]
            if exchange == "exchangeA":
                return {
                    "data": [
                        [1729944000000, 100.0, 110.0, 90.0, 105.0, 1000.0],
                        [1729947600000, 105.0, 115.0, 95.0, 110.0, 1100.0],
                    ]
                }
            elif exchange == "exchangeB":
                return {
                    "data": [
                        [1729944000000, 200.0, 210.0, 190.0, 205.0, 500.0],
                        [1729947600000, 205.0, 215.0, 195.0, 210.0, 550.0],
                    ]
                }

        mock_client.call_tool.side_effect = mock_call

        fetcher = OHLCVFetcher(mock_client)
        result = await fetcher.fetch_multi_exchange(
            "BTC/USDT",
            exchanges=["exchangeA", "exchangeB"],
        )

        # Should have 2 aggregated candles (both timestamps aligned)
        assert len(result["data"]) == 2
        assert result["data"][0]["timestamp"] == 1729944000000
        assert result["data"][1]["timestamp"] == 1729947600000

    @pytest.mark.asyncio
    async def test_timestamp_alignment_sorted_output(self):
        """Test aggregated candles are sorted by timestamp"""
        mock_client = AsyncMock()

        def mock_call(tool_name, params):
            # Return timestamps in different order per exchange
            return {
                "data": [
                    [1729951200000, 100.0, 110.0, 90.0, 105.0, 1000.0],
                    [1729944000000, 105.0, 115.0, 95.0, 110.0, 1100.0],
                ]
            }

        mock_client.call_tool.side_effect = mock_call

        fetcher = OHLCVFetcher(mock_client)
        result = await fetcher.fetch_multi_exchange(
            "BTC/USDT",
            exchanges=["exchangeA"],
        )

        # Should be sorted by timestamp (ascending)
        assert result["data"][0]["timestamp"] < result["data"][1]["timestamp"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
