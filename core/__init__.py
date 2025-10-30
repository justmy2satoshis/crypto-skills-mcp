"""
Core Routing and Orchestration

Intelligent routing layer that directs queries to optimal execution paths.

This module provides:
- TaskRouter: Complexity-based query routing to Skills/Agents/Orchestrator
- route_query: Convenience function for single-query routing
- ConfigLoader: Configuration loader and validator for operational modes
- load_config: Convenience function for loading mode configurations

Routing Strategy:
- 70-85% of queries → Skills (procedural, token-efficient)
- 15-25% of queries → Agents (strategic, complex analysis)
- 5% of queries → Orchestrator (multi-domain synthesis)

Operational Modes:
- hybrid: Intelligent routing (default) - 62.5% token reduction
- skills_only: Pure Skills - 73% token reduction
- agents_only: Pure Agents - 0% token reduction (maximum reasoning)
"""

from .router import TaskRouter, RouteTarget, QueryComplexity, route_query
from .config_loader import (
    ConfigLoader,
    OperationalMode,
    ConfigurationError,
    load_config,
    get_active_mode,
    validate_config,
)

__all__ = [
    # Routing
    "TaskRouter",
    "RouteTarget",
    "QueryComplexity",
    "route_query",
    # Configuration
    "ConfigLoader",
    "OperationalMode",
    "ConfigurationError",
    "load_config",
    "get_active_mode",
    "validate_config",
]

__version__ = "1.0.0"
