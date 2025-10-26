# Contributing to Crypto Skills MCP

Thank you for your interest in contributing to Crypto Skills MCP! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Code Style](#code-style)
- [Submitting Changes](#submitting-changes)
- [Reporting Bugs](#reporting-bugs)
- [Requesting Features](#requesting-features)

## Code of Conduct

This project adheres to a code of conduct that all contributors are expected to follow. Please be respectful and professional in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/crypto-skills-mcp.git
   cd crypto-skills-mcp
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/crypto-skills-mcp.git
   ```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment tool (venv, virtualenv, or conda)

### Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

   This installs the package in editable mode with all development tools including:
   - pytest (testing framework)
   - black (code formatter)
   - ruff (linter)
   - mypy (type checker)

3. **Verify installation**:
   ```bash
   pytest tests/
   ```

## Making Changes

### Branch Naming

Use descriptive branch names following this pattern:
- `feature/add-new-indicator` - For new features
- `fix/correct-rsi-calculation` - For bug fixes
- `docs/update-installation-guide` - For documentation
- `refactor/simplify-agent-logic` - For refactoring
- `test/add-sentiment-tests` - For adding tests

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(agents): add ethereum sentiment analysis

Implement sentiment analysis specifically for Ethereum using
social metrics and Fear & Greed index.

Closes #123
```

```
fix(mcp-client): correct cache TTL handling

The cache was not properly respecting custom TTL values,
causing stale data to be returned.

Fixes #456
```

## Testing

### Running Tests

Run the full test suite:
```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_agents.py
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html tests/
```

View coverage report:
```bash
# Open htmlcov/index.html in browser
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files with `test_` prefix
- Use descriptive test function names
- Follow AAA pattern: Arrange, Act, Assert
- Mock external dependencies (MCP calls, API requests)

**Example**:
```python
import pytest
from agents import CryptoMacroAnalyst
from mcp_client import MCPClientWrapper

@pytest.mark.asyncio
async def test_macro_analyst_synthesizes_outlook():
    """Test that macro analyst produces valid outlook."""
    # Arrange
    mock_client = MCPClientWrapper()
    analyst = CryptoMacroAnalyst(mcp_client=mock_client)

    # Act
    result = await analyst.synthesize_macro_outlook("BTC")

    # Assert
    assert "regime" in result
    assert "recommendation" in result
    assert 0 <= result["confidence"] <= 1
```

## Code Style

### Formatting

We use **Black** for code formatting:
```bash
black .
```

### Linting

We use **Ruff** for linting:
```bash
ruff check .
```

Fix auto-fixable issues:
```bash
ruff check --fix .
```

### Type Checking

We use **Mypy** for static type checking:
```bash
mypy agents/ mcp_client.py
```

### Pre-commit Checks

Before committing, run:
```bash
# Format code
black .

# Check linting
ruff check .

# Run type checker
mypy agents/ mcp_client.py

# Run tests
pytest tests/
```

## Submitting Changes

1. **Ensure all tests pass**:
   ```bash
   pytest tests/
   ```

2. **Ensure code is formatted and linted**:
   ```bash
   black .
   ruff check .
   mypy agents/ mcp_client.py
   ```

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat(scope): your change description"
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-branch-name
   ```

5. **Create a Pull Request** on GitHub:
   - Use a clear, descriptive title
   - Reference any related issues
   - Describe what changes you made and why
   - Include screenshots if applicable
   - Wait for review and address feedback

### Pull Request Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventional format
- [ ] No merge conflicts with main branch

## Reporting Bugs

When reporting bugs, please include:

1. **Clear description** of the issue
2. **Steps to reproduce** the behavior
3. **Expected behavior** vs actual behavior
4. **Environment details**:
   - Python version
   - Operating system
   - Relevant package versions
5. **Error messages** or stack traces
6. **Minimal code example** that demonstrates the issue

Use the GitHub issue template for bug reports.

## Requesting Features

When requesting features:

1. **Check existing issues** to avoid duplicates
2. **Describe the use case** clearly
3. **Explain the benefit** to users
4. **Propose a solution** if you have ideas
5. **Consider alternatives** you've evaluated

Use the GitHub issue template for feature requests.

## Agent Development Guidelines

When contributing new agents or modifying existing ones:

### Agent Structure

Each agent should:
- Inherit from a base agent class (if applicable)
- Accept `mcp_client` in constructor
- Implement async methods for analysis
- Return structured dictionaries with standardized fields
- Include confidence scores (0.0-1.0)
- Handle errors gracefully with fallback values

### MCP Integration

- Use `MCPClientWrapper` for all MCP tool calls
- Implement proper caching for expensive operations
- Handle MCP call failures with try/except
- Provide mock data fallback for testing
- Document which MCP servers are required

### Documentation

- Add comprehensive docstrings to all methods
- Include usage examples in docstrings
- Update README.md if adding new features
- Add examples to `examples/` directory

## Questions?

If you have questions about contributing:

- Open a GitHub issue with the `question` label
- Check existing issues and discussions
- Review the documentation in `docs/`

Thank you for contributing to Crypto Skills MCP!
