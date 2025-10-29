"""
Configuration Loader for Hybrid Skills-Agents Architecture

Dynamically loads operational mode configurations (hybrid, skills_only)
and provides runtime mode switching capabilities.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


class ConfigLoader:
    """
    Configuration loader for crypto-skills-mcp operational modes

    Supports two modes:
    - hybrid: Intelligent routing between Skills (80-90% token reduction) and Agents (62.5% token reduction overall)
    - skills_only: Maximum efficiency (73% token reduction, procedural workflows only)

    Note: agents_only mode is intentionally excluded to prevent excessive token consumption.
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize ConfigLoader

        Args:
            config_dir: Custom configuration directory (defaults to package config/)
        """
        if config_dir is None:
            # Default to package config directory
            self.config_dir = Path(__file__).parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)

        self.modes_dir = self.config_dir / "modes"
        self._active_config: Optional[Dict[str, Any]] = None
        self._active_mode: Optional[str] = None

        # Load default mode on initialization
        default_mode = os.getenv("CRYPTO_SKILLS_MODE", "hybrid")
        self.set_active_mode(default_mode)

    def load_mode(self, mode_name: str) -> Dict[str, Any]:
        """
        Load configuration for specified mode

        Args:
            mode_name: Mode to load ('hybrid' or 'skills_only')

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If mode configuration file doesn't exist
            ValueError: If mode configuration is invalid
        """
        # Validate mode name
        valid_modes = ["hybrid", "skills_only"]
        if mode_name not in valid_modes:
            raise ValueError(
                f"Invalid mode '{mode_name}'. " f"Available modes: {', '.join(valid_modes)}"
            )

        mode_file = self.modes_dir / f"{mode_name}.yaml"

        if not mode_file.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {mode_file}\n"
                f"Available modes: {', '.join(valid_modes)}"
            )

        with open(mode_file, "r") as f:
            config = yaml.safe_load(f)

        # Validate configuration structure
        required_keys = ["mode", "routing", "skills", "agents", "performance", "mcp"]
        missing_keys = [k for k in required_keys if k not in config]
        if missing_keys:
            raise ValueError(
                f"Invalid configuration in {mode_file}: "
                f"Missing required keys: {', '.join(missing_keys)}"
            )

        return config

    def set_active_mode(self, mode_name: str) -> None:
        """
        Set the active operational mode

        Args:
            mode_name: Mode to activate
        """
        self._active_config = self.load_mode(mode_name)
        self._active_mode = mode_name

    def get_active_config(self) -> Dict[str, Any]:
        """Get the currently active configuration"""
        if self._active_config is None:
            raise RuntimeError("No active configuration loaded")
        return self._active_config

    def get_active_mode_name(self) -> str:
        """Get the name of the currently active mode"""
        if self._active_mode is None:
            raise RuntimeError("No active mode set")
        return self._active_mode

    def is_routing_enabled(self) -> bool:
        """Check if intelligent routing is enabled in active mode"""
        config = self.get_active_config()
        return config["routing"].get("enabled", False)

    def are_skills_enabled(self) -> bool:
        """Check if Skills are enabled in active mode"""
        config = self.get_active_config()
        return config["skills"].get("enabled", False)

    def are_agents_enabled(self) -> bool:
        """Check if Agents are enabled in active mode"""
        config = self.get_active_config()
        return config["agents"].get("enabled", False)

    def is_orchestrator_enabled(self) -> bool:
        """Check if orchestrator agent is enabled"""
        config = self.get_active_config()
        return config["agents"].get("orchestrator", {}).get("enabled", False)

    def get_enabled_skills(self) -> Dict[str, List[str]]:
        """
        Get dictionary of enabled Skills by category

        Returns:
            Dict mapping category names to lists of enabled Skills
        """
        config = self.get_active_config()
        skills_config = config["skills"]

        enabled_skills = {}
        for category in ["data_extraction", "technical_analysis", "sentiment_analysis"]:
            if category in skills_config:
                enabled_skills[category] = skills_config[category]

        return enabled_skills

    def get_enabled_agents(self) -> List[str]:
        """
        Get list of enabled specialized agents

        Returns:
            List of agent names
        """
        config = self.get_active_config()
        return config["agents"].get("specialized", [])

    def get_performance_targets(self) -> Dict[str, Any]:
        """
        Get performance targets for active mode

        Returns:
            Performance configuration including token reduction targets
        """
        config = self.get_active_config()
        return config.get("performance", {})

    def get_mcp_requirements(self) -> List[Dict[str, Any]]:
        """
        Get MCP server requirements for active mode

        Returns:
            List of required MCP servers with metadata
        """
        config = self.get_active_config()
        return config.get("mcp", {}).get("servers", [])


# Convenience functions for quick access
_global_loader: Optional[ConfigLoader] = None


def load_config(mode_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration (creates global loader if needed)

    Args:
        mode_name: Mode to load (defaults to CRYPTO_SKILLS_MODE env var or 'hybrid')

    Returns:
        Configuration dictionary
    """
    global _global_loader

    if _global_loader is None:
        _global_loader = ConfigLoader()

    if mode_name:
        _global_loader.set_active_mode(mode_name)

    return _global_loader.get_active_config()


def get_active_mode() -> str:
    """
    Get the currently active mode name

    Returns:
        Mode name ('hybrid' or 'skills_only')
    """
    global _global_loader

    if _global_loader is None:
        _global_loader = ConfigLoader()

    return _global_loader.get_active_mode_name()
