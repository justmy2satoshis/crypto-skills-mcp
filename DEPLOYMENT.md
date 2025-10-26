# Deployment Guide

This document provides instructions for deploying and publishing the crypto-skills-mcp package.

## Repository Status

- **GitHub Repository**: https://github.com/justmy2satoshis/crypto-skills-mcp
- **Current Version**: v1.0.0
- **Release Tag**: v1.0.0 (created 2025-10-26)
- **License**: MIT

## Completed Setup Steps

### ✅ Repository Initialization
- Git repository initialized
- Initial commit with 53 files
- Remote configured: `origin` → `https://github.com/justmy2satoshis/crypto-skills-mcp.git`
- Main branch created and pushed

### ✅ Version Tagging
- Git tag `v1.0.0` created
- Tag pushed to GitHub
- CHANGELOG.md updated with correct repository URLs

### ✅ Code Cleanup
- Removed unused hybrid architecture files:
  - `config/` directory (3 YAML mode configs)
  - `core/` directory (router, config loader)
  - `skills/` directory (21 skill implementation files)
  - `TEST.txt` test file
- Repository now contains only multi-agent implementation

### ✅ Repository Structure (Final)
```
crypto-skills-mcp/
├── .github/
│   └── workflows/
│       ├── tests.yml       # CI testing
│       ├── lint.yml        # Code quality
│       └── release.yml     # PyPI publishing
├── agents/
│   ├── crypto_macro_analyst.py
│   ├── crypto_vc_analyst.py
│   ├── crypto_sentiment_analyst.py
│   └── thesis_synthesizer.py
├── examples/
│   ├── agents_demo.py
│   ├── config_demo.py
│   └── production_usage.py
├── tests/
│   └── test_agents/
│       ├── test_macro_analyst.py
│       ├── test_vc_analyst.py
│       ├── test_sentiment_analyst.py
│       ├── test_thesis_synthesizer.py
│       └── test_agent_integration.py
├── docs/
│   └── PHASE4_COMPLETION_REPORT.md
├── mcp_client.py
├── setup.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── .gitignore
```

## Next Steps (Manual)

### 1. Create GitHub Release (Web UI)

Visit: https://github.com/justmy2satoshis/crypto-skills-mcp/releases/new

**Tag**: v1.0.0 (existing tag)
**Release Title**: 🚀 crypto-skills-mcp v1.0.0

**Release Notes**:
```markdown
# 🚀 crypto-skills-mcp v1.0.0

Multi-Agent cryptocurrency investment analysis system with MCP integration for Claude Desktop/Code.

## ✨ Features

### Multi-Agent Architecture
- **CryptoMacroAnalyst**: Macro regime analysis, Fed policy impact, institutional flows
- **CryptoVCAnalyst**: Fundamental due diligence, tokenomics, technical health, liquidity
- **CryptoSentimentAnalyst**: Crowd sentiment, Fear & Greed Index, whale activity
- **ThesisSynthesizer**: Investment thesis generation with conflict resolution

### MCP Integration
Connects to 10 MCP servers for comprehensive cryptocurrency data:

**Core MCP Servers (Required)**:
- ccxt-mcp: Exchange data (price, OHLCV, order books)
- crypto-indicators-mcp: Technical indicators (RSI, MACD, 70+ indicators)
- crypto-feargreed-mcp: Crypto Fear & Greed Index
- crypto-sentiment-mcp: Social metrics and sentiment analysis
- crypto-projects-mcp: Project fundamentals (6,000+ tokens)
- cryptopanic-mcp-server: Cryptocurrency news aggregation

**Enhanced MCP Servers (Optional)**:
- etf-flow-mcp: Bitcoin/Ethereum ETF flow data
- grok-search-mcp: Web/news search with AI sentiment analysis
- tokenmetrics-mcp: AI trading signals and price predictions
- perplexity-mcp: Economic research and analysis

### Performance
- **70% cache hit rate** - reduces redundant MCP calls
- **Async architecture** - parallel agent execution
- **Smart caching** - configurable TTL per data type
- **Retry logic** - exponential backoff for reliability

## 📦 Installation

```bash
pip install crypto-skills-mcp
```

With all optional dependencies:
```bash
pip install crypto-skills-mcp[all]
```

## 🎯 Quick Start

```python
import asyncio
from agents.thesis_synthesizer import ThesisSynthesizer
from mcp_client import MCPClientWrapper

async def analyze_bitcoin():
    mcp_client = MCPClientWrapper()
    synthesizer = ThesisSynthesizer(mcp_client=mcp_client)

    thesis = await synthesizer.generate_investment_thesis("BTC", horizon_days=30)
    print(f"Recommendation: {thesis['recommendation']}")
    print(f"Confidence: {thesis['confidence']:.2f}")

asyncio.run(analyze_bitcoin())
```

## 📚 Documentation

- [README](https://github.com/justmy2satoshis/crypto-skills-mcp/blob/main/README.md) - Full documentation
- [CHANGELOG](https://github.com/justmy2satoshis/crypto-skills-mcp/blob/main/CHANGELOG.md) - Version history
- [CONTRIBUTING](https://github.com/justmy2satoshis/crypto-skills-mcp/blob/main/CONTRIBUTING.md) - Contribution guidelines

## 🔧 Requirements

- Python 3.8+
- Active MCP server connections for real-time data

## 📄 License

MIT License - see [LICENSE](https://github.com/justmy2satoshis/crypto-skills-mcp/blob/main/LICENSE)
```

### 2. Add Repository Topics (GitHub Web UI)

Visit: https://github.com/justmy2satoshis/crypto-skills-mcp

Click **"⚙️ Settings"** → **"Manage topics"** → Add:
- `python`
- `cryptocurrency`
- `bitcoin`
- `ethereum`
- `mcp`
- `claude`
- `claude-desktop`
- `investment-analysis`
- `trading`
- `multi-agent`
- `async`
- `sentiment-analysis`
- `technical-analysis`

### 3. Update Repository Description (GitHub Web UI)

Visit: https://github.com/justmy2satoshis/crypto-skills-mcp

Click **"About"** → **Edit** → Set description:
```
Multi-Agent cryptocurrency investment analysis system with MCP integration for Claude Desktop/Code
```

Website: Leave empty or add documentation URL when available

### 4. Configure PyPI Publishing (Optional)

#### A. Create PyPI Account
1. Register at https://pypi.org/account/register/
2. Verify email address
3. Enable 2FA (required for API token creation)

#### B. Create PyPI API Token
1. Go to https://pypi.org/manage/account/token/
2. Create token with scope: "Entire account (all projects)"
3. Copy token (starts with `pypi-`)

#### C. Add GitHub Secret
1. Visit: https://github.com/justmy2satoshis/crypto-skills-mcp/settings/secrets/actions
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: `pypi-...` (your PyPI token)
5. Click "Add secret"

#### D. Test PyPI Publishing (Optional)
Create a test release to verify the workflow:
```bash
cd ~/crypto-skills-mcp
git tag v1.0.1-rc.1
git push origin v1.0.1-rc.1
```

This will trigger `.github/workflows/release.yml` which will:
- Build the package
- Run tests
- Publish to PyPI (if tag matches `v*` pattern)

## GitHub Actions Workflows

### tests.yml
**Triggers**: Push, Pull Request
**Matrix**: Python 3.8, 3.9, 3.10, 3.11 on ubuntu-latest, macos-latest, windows-latest
**Steps**:
- Install dependencies
- Run pytest with coverage
- Upload coverage to Codecov

### lint.yml
**Triggers**: Push, Pull Request
**Steps**:
- Run Black (code formatting check)
- Run Ruff (linting)
- Run Mypy (type checking)

### release.yml
**Triggers**: Tag push matching `v*` pattern
**Steps**:
- Build package (sdist + wheel)
- Run tests
- Publish to PyPI
- Create GitHub Release

## Maintenance

### Creating New Releases

1. Update version in `setup.py` and `pyproject.toml`
2. Update `CHANGELOG.md` with changes
3. Commit changes:
   ```bash
   git add setup.py pyproject.toml CHANGELOG.md
   git commit -m "chore: bump version to X.Y.Z"
   git push origin main
   ```
4. Create and push tag:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```
5. GitHub Actions will automatically publish to PyPI
6. Create GitHub Release manually with release notes

### Branch Protection (Optional)

To enable branch protection on `main`:
1. Visit: https://github.com/justmy2satoshis/crypto-skills-mcp/settings/branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - Select: `test`, `lint` status checks
5. Save changes

## Support

- **Issues**: https://github.com/justmy2satoshis/crypto-skills-mcp/issues
- **Discussions**: https://github.com/justmy2satoshis/crypto-skills-mcp/discussions
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

MIT License - see [LICENSE](LICENSE) file for details.
