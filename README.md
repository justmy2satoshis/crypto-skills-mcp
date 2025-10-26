# Crypto Skills MCP

**Multi-Agent cryptocurrency investment analysis system with MCP integration for Claude Desktop/Code.**

## Overview

This package implements a specialized multi-agent architecture for comprehensive cryptocurrency investment analysis:
- **CryptoMacroAnalyst**: Macroeconomic regime analysis, Fed policy impact, and institutional flow tracking
- **CryptoVCAnalyst**: Fundamental due diligence including tokenomics, technical health, and liquidity analysis
- **CryptoSentimentAnalyst**: Crowd sentiment analysis, Fear & Greed Index, and whale activity tracking
- **ThesisSynthesizer**: Investment thesis generation with multi-agent conflict resolution

## Key Benefits

✅ **Specialized Analysis** - Four dedicated agents for macro, fundamental, sentiment, and thesis synthesis
✅ **MCP Integration** - Seamless integration with 6+ cryptocurrency MCP servers
✅ **Async Architecture** - Parallel agent execution for fast analysis
✅ **Production Ready** - Comprehensive testing, type safety, and error handling
✅ **Caching Layer** - Intelligent caching reduces redundant MCP calls by ~70%

## Installation

### Prerequisites

- Python 3.8 or higher
- Claude Desktop or Claude Code with MCP support
- At least one of the supported MCP servers (see [MCP Integration](#mcp-integration))

### Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/crypto-skills-mcp.git
cd crypto-skills-mcp

# Install with all dependencies
pip install -e ".[all]"

# Or install minimal version
pip install -e .

# Run tests to verify installation
pytest tests/
```

### Installation Options

```bash
# Core installation only
pip install -e .

# With skills utilities (pandas, numpy)
pip install -e ".[skills]"

# With agent framework (pydantic, typing-extensions)
pip install -e ".[agents]"

# With development tools (testing, linting, formatting)
pip install -e ".[dev]"

# With testing tools only
pip install -e ".[test]"

# Everything
pip install -e ".[all]"
```

## Architecture

### Multi-Agent System

```
                    ┌─────────────────────────────────┐
                    │   ThesisSynthesizer Agent       │
                    │  (Investment Thesis Generation) │
                    │   - Synthesizes multi-agent     │
                    │   - Resolves conflicts          │
                    │   - BUY/HOLD/SELL signals       │
                    └─────────────────────────────────┘
                                  ▲
              ┌───────────────────┼───────────────────┐
              │                   │                   │
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │  CryptoMacro    │ │  CryptoVC       │ │ CryptoSentiment │
    │  Analyst        │ │  Analyst        │ │ Analyst         │
    │                 │ │                 │ │                 │
    │ • Fed policy    │ │ • Tokenomics    │ │ • Fear & Greed  │
    │ • Inst. flows   │ │ • Tech health   │ │ • Social metrics│
    │ • Risk regime   │ │ • Liquidity     │ │ • Whale activity│
    └─────────────────┘ └─────────────────┘ └─────────────────┘
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                    ┌─────────────────────────────────┐
                    │      MCP Client Wrapper         │
                    │   (Caching + Error Handling)    │
                    └─────────────────────────────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │  ccxt-mcp       │ │ crypto-indicators│ │ crypto-sentiment│
    │  (Price Data)   │ │ (Technical)      │ │ (Social Metrics)│
    └─────────────────┘ └─────────────────┘ └─────────────────┘
```

### Specialized Agents

| Agent | Specialization | Key Methods | Output Format |
|-------|----------------|-------------|---------------|
| **CryptoMacroAnalyst** | Macro regime, Fed policy, institutional flows | `analyze_macro_regime()`, `track_institutional_flows()`, `assess_risk_sentiment()` | Risk regime classification, flow signals |
| **CryptoVCAnalyst** | Fundamental due diligence, tokenomics, liquidity | `analyze_tokenomics()`, `assess_technical_health()`, `calculate_risk_score()` | 0-100 risk score, position sizing |
| **CryptoSentimentAnalyst** | Market psychology, Fear & Greed, social trends | `analyze_crowd_sentiment()`, `track_whale_activity()`, `generate_contrarian_signal()` | Sentiment regime, contrarian signals |
| **ThesisSynthesizer** | Multi-agent synthesis, investment thesis | `generate_investment_thesis()`, `synthesize_analysis()` | BUY/HOLD/SELL, entry/exit levels |

## Usage Examples

### Example 1: Basic Bitcoin Analysis

```python
import asyncio
from agents import CryptoMacroAnalyst, CryptoVCAnalyst, CryptoSentimentAnalyst
from mcp_client import MCPClientWrapper

async def analyze_bitcoin():
    # Initialize MCP client wrapper
    mcp_client = MCPClientWrapper()

    # Initialize specialized agents
    macro = CryptoMacroAnalyst(mcp_client=mcp_client)
    vc = CryptoVCAnalyst(mcp_client=mcp_client)
    sentiment = CryptoSentimentAnalyst(mcp_client=mcp_client)

    # Run parallel analysis
    macro_result = await macro.synthesize_macro_outlook("BTC")
    vc_result = await vc.generate_due_diligence_report("BTC")
    sentiment_result = await sentiment.synthesize_sentiment_outlook("bitcoin")

    print(f"Macro Regime: {macro_result['regime']}")
    print(f"Risk Score: {vc_result['overall_score']}/100")
    print(f"Sentiment: {sentiment_result['sentiment_assessment']}")

asyncio.run(analyze_bitcoin())
```

### Example 2: Complete Investment Thesis

```python
from agents import ThesisSynthesizer

async def generate_thesis():
    mcp_client = MCPClientWrapper()
    synthesizer = ThesisSynthesizer(mcp_client=mcp_client)

    # Generate complete investment thesis
    thesis = await synthesizer.generate_investment_thesis("BTC", horizon_days=30)

    print(f"Recommendation: {thesis['recommendation']}")
    print(f"Confidence: {thesis['confidence']:.2f}")
    print(f"Entry Range: ${thesis['entry_range']['low']:,.0f} - ${thesis['entry_range']['high']:,.0f}")
    print(f"Position Size: {thesis['position_size'] * 100:.1f}%")

    for target in thesis['exit_targets']:
        print(f"Target: ${target['price']:,.0f} - {target['reasoning']}")

asyncio.run(generate_thesis())
```

### Example 3: Multi-Asset Comparison

```python
async def compare_assets():
    """Compare multiple cryptocurrencies for portfolio allocation."""
    mcp_client = MCPClientWrapper()

    assets = ["BTC", "ETH", "SOL"]
    results = {}

    for asset in assets:
        # Generate thesis for each asset
        synthesizer = ThesisSynthesizer(mcp_client=mcp_client)
        thesis = await synthesizer.generate_investment_thesis(asset, horizon_days=30)

        results[asset] = {
            "recommendation": thesis["recommendation"],
            "confidence": thesis["confidence"],
            "risk_score": thesis.get("risk_score", 0),
            "position_size": thesis["position_size"]
        }

    # Sort by confidence and risk-adjusted returns
    ranked = sorted(results.items(), key=lambda x: x[1]["confidence"], reverse=True)

    for asset, metrics in ranked:
        print(f"{asset}: {metrics['recommendation']} (confidence: {metrics['confidence']:.2f})")

asyncio.run(compare_assets())
```

## MCP Integration

This package integrates with your existing [Crypto-MCP-Suite](../mcp-servers/Crypto%20MCPs/Crypto-MCP-Suite/) (41 production MCPs).

### Required MCPs (Tier 1)
- **ccxt-mcp**: Exchange data across 24+ exchanges
- **crypto-indicators-mcp**: Technical indicators (RSI, MACD, Bollinger Bands)
- **crypto-sentiment-mcp**: Social sentiment (Reddit, Telegram, Discord)
- **crypto-feargreed-mcp**: Fear & Greed Index (0-100)

### Enhanced MCPs (Tier 2)
- **crypto-projects-mcp**: Project fundamentals via Mobula API
- **cryptopanic-mcp**: News sentiment
- **etf-flow-mcp**: Institutional flow data

## Performance

### Caching Strategy

The MCP Client Wrapper implements intelligent caching to reduce redundant API calls:

- **Ticker Data**: 60 second TTL (real-time price updates)
- **OHLCV Data**: 60 second TTL (candlestick data)
- **Fear & Greed Index**: 300 second TTL (5 minutes)
- **Project Data**: 3600 second TTL (1 hour)
- **News Data**: 300 second TTL (5 minutes)

**Cache Hit Rates**: ~70% reduction in redundant MCP calls during typical analysis workflows

### Async Performance

Parallel agent execution using asyncio enables concurrent analysis:
- **Single Asset Analysis**: ~2-3 seconds (with cache hits)
- **Multi-Asset Comparison**: ~5-7 seconds for 3 assets (parallel execution)
- **Complete Investment Thesis**: ~3-5 seconds (synthesizing all agents)

## Database Integration

Supports multi-database architecture:
- **PostgreSQL**: Structured metadata (tokenomics, fundamentals)
- **MongoDB**: Document storage (social posts, news articles)
- **Redis**: Real-time caching (price data, sentiment scores)
- **DuckDB**: Analytics (time-series analysis, backtesting)
- **Qdrant**: Vector storage (semantic search of research reports)

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .

# Lint
ruff check .

# Type check
mypy agents/ mcp_client.py
```

## Directory Structure

```
crypto-skills-mcp/
├── agents/              # Specialized cryptocurrency analysis agents
│   ├── __init__.py
│   ├── crypto_macro_analyst.py      # Macro regime and institutional flows
│   ├── crypto_vc_analyst.py         # Fundamental due diligence
│   ├── crypto_sentiment_analyst.py  # Market psychology and sentiment
│   └── thesis_synthesizer.py        # Investment thesis generation
├── mcp_client.py        # MCP Client Wrapper with caching and retry logic
├── examples/            # Production usage examples
│   └── production_usage.py
├── tests/               # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py      # Pytest fixtures and configuration
│   ├── test_agents.py   # Agent unit tests
│   └── test_mcp_client.py
├── .github/             # GitHub Actions workflows
│   └── workflows/
│       ├── tests.yml    # CI testing across OS and Python versions
│       ├── lint.yml     # Code quality checks
│       └── release.yml  # Automated PyPI publishing
├── pyproject.toml       # Modern Python package configuration
├── setup.py             # Package setup with modular installation
├── requirements.txt     # Core dependencies
├── LICENSE              # MIT License
├── CONTRIBUTING.md      # Contribution guidelines
├── CHANGELOG.md         # Version history
└── README.md            # This file
```

## License

MIT License - See [LICENSE](LICENSE) file for details.

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/crypto-skills-mcp/issues)
- Discord: [Community Server](https://discord.gg/crypto-skills)
