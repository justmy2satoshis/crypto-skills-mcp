"""
Core infrastructure for crypto-skills-mcp

Provides configuration management and routing between Skills and Agents.
"""

from .config_loader import ConfigLoader, load_config, get_active_mode

__all__ = ["ConfigLoader", "load_config", "get_active_mode"]
__version__ = "1.0.0"
