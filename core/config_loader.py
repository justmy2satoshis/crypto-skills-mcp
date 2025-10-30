"""
Configuration Loader and Validator

Loads and validates operational mode configurations (hybrid/skills_only/agents_only).

This module provides:
- ConfigLoader: Main configuration loader with validation
- validate_config: Configuration validation function
- get_active_mode: Helper to retrieve active configuration

Supported Modes:
- hybrid: Intelligent routing (default) - 62.5% token reduction
- skills_only: Pure Skills - 73% token reduction
- agents_only: Pure Agents - 0% token reduction (maximum reasoning)
"""

import yaml
import os
from typing import Dict, Optional, List
from pathlib import Path
from enum import Enum


class OperationalMode(Enum):
    """Supported operational modes"""

    HYBRID = "hybrid"
    SKILLS_ONLY = "skills_only"
    AGENTS_ONLY = "agents_only"


class ConfigurationError(Exception):
    """Configuration validation error"""

    pass


class ConfigLoader:
    """
    Configuration loader and validator

    Loads mode configurations from YAML files and validates against schema.
    Provides runtime configuration access for Skills, Agents, and Router.
    """

    def __init__(self, config_dir: Optional[str] = None):
        """
        Initialize config loader

        Args:
            config_dir: Optional config directory path (defaults to package config/)
        """
        if config_dir is None:
            # Default to package config directory
            package_root = Path(__file__).parent.parent
            config_dir = package_root / "config"

        self.config_dir = Path(config_dir)
        self.modes_dir = self.config_dir / "modes"

        # Validate config directory exists
        if not self.config_dir.exists():
            raise ConfigurationError(f"Config directory not found: {self.config_dir}")
        if not self.modes_dir.exists():
            raise ConfigurationError(f"Modes directory not found: {self.modes_dir}")

        # Loaded configurations cache
        self._configs: Dict[str, Dict] = {}
        self._active_mode: Optional[str] = None

    def load_mode(self, mode: str) -> Dict:
        """
        Load configuration for specific mode

        Args:
            mode: Mode name (hybrid, skills_only, agents_only)

        Returns:
            Configuration dictionary

        Raises:
            ConfigurationError: If mode file not found or invalid

        Example:
            >>> loader = ConfigLoader()
            >>> config = loader.load_mode("hybrid")
            >>> print(config["mode"]["name"])
            hybrid
        """
        # Check if already loaded
        if mode in self._configs:
            return self._configs[mode]

        # Validate mode name
        try:
            OperationalMode(mode)
        except ValueError:
            valid_modes = [m.value for m in OperationalMode]
            raise ConfigurationError(f"Invalid mode '{mode}'. Valid modes: {valid_modes}")

        # Load YAML file
        config_file = self.modes_dir / f"{mode}.yaml"
        if not config_file.exists():
            raise ConfigurationError(f"Mode config file not found: {config_file}")

        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Failed to parse YAML config: {e}")

        # Validate configuration
        self._validate_config(config, mode)

        # Cache and return
        self._configs[mode] = config
        return config

    def set_active_mode(self, mode: str) -> Dict:
        """
        Set active operational mode

        Args:
            mode: Mode to activate

        Returns:
            Active configuration

        Example:
            >>> loader = ConfigLoader()
            >>> config = loader.set_active_mode("hybrid")
            >>> loader.get_active_mode_name()
            'hybrid'
        """
        config = self.load_mode(mode)
        self._active_mode = mode
        return config

    def get_active_config(self) -> Dict:
        """
        Get active mode configuration

        Returns:
            Active configuration dictionary

        Raises:
            ConfigurationError: If no mode is active
        """
        if self._active_mode is None:
            # Default to hybrid mode
            return self.set_active_mode("hybrid")

        return self._configs[self._active_mode]

    def get_active_mode_name(self) -> str:
        """Get name of active mode"""
        if self._active_mode is None:
            return "hybrid"  # Default
        return self._active_mode

    def is_routing_enabled(self) -> bool:
        """Check if routing is enabled in active mode"""
        config = self.get_active_config()
        return config.get("routing", {}).get("enabled", False)

    def are_skills_enabled(self) -> bool:
        """Check if Skills are enabled in active mode"""
        config = self.get_active_config()
        return config.get("skills", {}).get("enabled", False)

    def are_agents_enabled(self) -> bool:
        """Check if Agents are enabled in active mode"""
        config = self.get_active_config()
        return config.get("agents", {}).get("enabled", False)

    def get_enabled_skills(self) -> Dict[str, List[str]]:
        """
        Get list of enabled Skills by category

        Returns:
            Dictionary mapping categories to Skill names

        Example:
            >>> loader = ConfigLoader()
            >>> loader.set_active_mode("hybrid")
            >>> skills = loader.get_enabled_skills()
            >>> print(skills["sentiment_analysis"])
            ['social_sentiment_tracker', 'whale_activity_monitor', ...]
        """
        config = self.get_active_config()
        if not self.are_skills_enabled():
            return {}

        skills_config = config.get("skills", {})

        # Extract Skills by category
        enabled_skills = {}
        for category in ["data_extraction", "technical_analysis", "sentiment_analysis"]:
            if category in skills_config:
                enabled_skills[category] = skills_config[category]

        return enabled_skills

    def get_enabled_agents(self) -> List[str]:
        """
        Get list of enabled Agents

        Returns:
            List of Agent names

        Example:
            >>> loader = ConfigLoader()
            >>> loader.set_active_mode("hybrid")
            >>> agents = loader.get_enabled_agents()
            >>> print(agents)
            ['crypto_macro_analyst', 'crypto_vc_analyst', 'crypto_sentiment_analyst']
        """
        config = self.get_active_config()
        if not self.are_agents_enabled():
            return []

        agents_config = config.get("agents", {})
        return agents_config.get("specialized", [])

    def is_orchestrator_enabled(self) -> bool:
        """Check if Strategic Orchestrator is enabled"""
        config = self.get_active_config()
        if not self.are_agents_enabled():
            return False

        agents_config = config.get("agents", {})
        orchestrator_config = agents_config.get("orchestrator", {})
        return orchestrator_config.get("enabled", False)

    def get_mcp_servers(self) -> List[Dict]:
        """
        Get required MCP servers for active mode

        Returns:
            List of MCP server configurations
        """
        config = self.get_active_config()
        return config.get("mcp", {}).get("servers", [])

    def _validate_config(self, config: Dict, mode: str) -> None:
        """
        Validate configuration against schema

        Args:
            config: Configuration dictionary
            mode: Mode name

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Required top-level keys
        required_keys = ["mode", "routing", "skills", "agents", "mcp"]
        missing_keys = [key for key in required_keys if key not in config]
        if missing_keys:
            raise ConfigurationError(f"Missing required config keys: {missing_keys}")

        # Validate mode section
        mode_config = config["mode"]
        if "name" not in mode_config:
            raise ConfigurationError("mode.name is required")
        if mode_config["name"] != mode:
            raise ConfigurationError(
                f"Config mode name '{mode_config['name']}' doesn't match file mode '{mode}'"
            )

        # Validate routing section
        routing_config = config["routing"]
        if "enabled" not in routing_config:
            raise ConfigurationError("routing.enabled is required")

        # If routing enabled, validate router_class
        if routing_config["enabled"] and "router_class" not in routing_config:
            raise ConfigurationError("routing.router_class required when routing is enabled")

        # Validate skills section
        skills_config = config["skills"]
        if "enabled" not in skills_config:
            raise ConfigurationError("skills.enabled is required")

        # If skills enabled, validate skill categories
        if skills_config["enabled"]:
            required_categories = [
                "data_extraction",
                "technical_analysis",
                "sentiment_analysis",
            ]
            for category in required_categories:
                if category not in skills_config:
                    raise ConfigurationError(f"skills.{category} required when skills are enabled")

        # Validate agents section
        agents_config = config["agents"]
        if "enabled" not in agents_config:
            raise ConfigurationError("agents.enabled is required")

        # If agents enabled, validate agent list
        if agents_config["enabled"]:
            if "specialized" not in agents_config:
                raise ConfigurationError("agents.specialized required when agents are enabled")

        # Validate MCP section
        mcp_config = config["mcp"]
        if "servers" not in mcp_config:
            raise ConfigurationError("mcp.servers is required")

        # Validate at least one capability is enabled
        if not skills_config["enabled"] and not agents_config["enabled"]:
            raise ConfigurationError("At least one of skills or agents must be enabled")

    def get_performance_targets(self) -> Dict:
        """
        Get performance targets for active mode

        Returns:
            Performance metrics dictionary
        """
        config = self.get_active_config()
        return config.get("performance", {})


# Convenience function for single-mode loading
def load_config(mode: str = "hybrid") -> Dict:
    """
    Load configuration for specific mode

    Args:
        mode: Mode name (defaults to hybrid)

    Returns:
        Configuration dictionary

    Example:
        >>> config = load_config("hybrid")
        >>> print(config["mode"]["description"])
        Intelligent routing between Skills (70-85%) and Agents (15-25%)
    """
    loader = ConfigLoader()
    return loader.load_mode(mode)


def get_active_mode() -> str:
    """
    Get active operational mode

    Returns:
        Active mode name

    Note: In production, this would check environment variable or config file.
    For now, defaults to hybrid mode.
    """
    # Check environment variable
    env_mode = os.getenv("CRYPTO_SKILLS_MODE", "hybrid")

    # Validate mode
    try:
        OperationalMode(env_mode)
        return env_mode
    except ValueError:
        # Default to hybrid if invalid
        return "hybrid"


def validate_config(config: Dict) -> bool:
    """
    Validate configuration dictionary

    Args:
        config: Configuration to validate

    Returns:
        True if valid

    Raises:
        ConfigurationError: If invalid
    """
    loader = ConfigLoader()
    mode = config.get("mode", {}).get("name", "unknown")
    loader._validate_config(config, mode)
    return True
