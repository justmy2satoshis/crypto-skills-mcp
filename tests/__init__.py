"""
Crypto-Skills-MCP Test Suite

This package contains unit tests and integration tests for the crypto-skills-mcp project.

Test Structure:
---------------
- test_agents/: Agent layer unit and integration tests
- test_skills/: Skill layer unit tests (if needed)
- test_core/: Core router and configuration tests

Running Tests:
--------------
    # Run all tests
    pytest

    # Run specific test file
    pytest tests/test_agents/test_macro_analyst.py

    # Run with coverage
    pytest --cov=agents --cov=skills --cov=core

    # Run verbose
    pytest -v

Version: 1.0.0
"""

__version__ = "1.0.0"
