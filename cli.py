#!/usr/bin/env python3
"""
Crypto Skills MCP - Command Line Interface

Production-ready CLI for the crypto-skills-mcp package.
Provides routing, configuration, and validation capabilities.

Usage:
    crypto-skills route "Calculate RSI for BTC"
    crypto-skills config
    crypto-skills validate
    crypto-skills version
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Version info
__version__ = "1.0.0"


def format_routing_result(result: Dict, output_format: str = "text") -> str:
    """
    Format routing result for display

    Args:
        result: Routing decision from router
        output_format: "text" or "json"

    Returns:
        Formatted string for output
    """
    if output_format == "json":
        return json.dumps(result, indent=2)

    # Text format with nice formatting
    lines = [
        "=" * 60,
        "ROUTING DECISION",
        "=" * 60,
        f"Target:      {result['target'].upper()}",
        f"Handler:     {result['handler']}",
        f"Complexity:  {result['complexity']}",
        f"Confidence:  {result['confidence']:.0%}",
        "-" * 60,
        f"Reasoning:   {result['reasoning']}",
        "=" * 60,
    ]
    return "\n".join(lines)


def format_config(config: Dict, output_format: str = "text") -> str:
    """
    Format configuration for display

    Args:
        config: Configuration dictionary
        output_format: "text" or "json"

    Returns:
        Formatted string for output
    """
    if output_format == "json":
        return json.dumps(config, indent=2)

    # Text format
    lines = [
        "=" * 60,
        "CURRENT CONFIGURATION",
        "=" * 60,
        f"Mode:        {config.get('mode', {}).get('name', 'unknown')}",
        f"Description: {config.get('mode', {}).get('description', 'N/A')}",
        f"Routing:     {'enabled' if config.get('routing', {}).get('enabled') else 'disabled'}",
        f"Skills:      {'enabled' if config.get('skills', {}).get('enabled') else 'disabled'}",
        f"Agents:      {'enabled' if config.get('agents', {}).get('enabled') else 'disabled'}",
        "=" * 60,
    ]
    return "\n".join(lines)


def format_validation(results: Dict, output_format: str = "text") -> str:
    """
    Format validation results for display

    Args:
        results: Validation results dictionary
        output_format: "text" or "json"

    Returns:
        Formatted string for output
    """
    if output_format == "json":
        return json.dumps(results, indent=2)

    # Text format with status indicators (using ASCII for Windows compatibility)
    lines = [
        "=" * 60,
        "INSTALLATION VALIDATION",
        "=" * 60,
    ]

    for check, result in results.items():
        status = "[PASS]" if result["passed"] else "[FAIL]"
        lines.append(f"{status} {check}: {result['message']}")

    lines.append("=" * 60)

    all_passed = all(r["passed"] for r in results.values())
    if all_passed:
        lines.append("[PASS] All validation checks passed!")
    else:
        lines.append("[FAIL] Some validation checks failed - see details above")

    lines.append("=" * 60)
    return "\n".join(lines)


def cmd_route(args) -> int:
    """
    Route command - show routing decision for a query

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0=success, 1=error)
    """
    try:
        from core.router import TaskRouter

        router = TaskRouter()
        result = router.route(args.query)

        print(format_routing_result(result, args.format))
        return 0

    except ImportError as e:
        print(f"[ERROR] Failed to import router: {e}", file=sys.stderr)
        print("        Try running: pip install -e .", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] Error routing query: {e}", file=sys.stderr)
        return 1


def cmd_config(args) -> int:
    """
    Config command - show or modify configuration

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0=success, 1=error)
    """
    try:
        from core.config_loader import ConfigLoader

        # Load configuration
        loader = ConfigLoader()

        if args.mode:
            # Switch mode (not yet implemented - Phase 2)
            print(f"[WARN] Mode switching coming in Phase 2", file=sys.stderr)
            print(f"       Requested mode: {args.mode}", file=sys.stderr)
            return 1
        else:
            # Show current config
            config = loader.load_config()
            print(format_config(config, args.format))
            return 0

    except ImportError as e:
        print(f"[ERROR] Failed to import config loader: {e}", file=sys.stderr)
        print("        Try running: pip install -e .", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] Error loading configuration: {e}", file=sys.stderr)
        return 1


def cmd_validate(args) -> int:
    """
    Validate command - check installation integrity

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0=success, 1=error)
    """
    results = {}

    # Check 1: Core packages importable
    try:
        from core.router import TaskRouter
        from core.config_loader import ConfigLoader
        results["Core imports"] = {
            "passed": True,
            "message": "core.router and core.config_loader import successfully"
        }
    except ImportError as e:
        results["Core imports"] = {
            "passed": False,
            "message": f"Failed to import core modules: {e}"
        }

    # Check 2: Agents package exists
    try:
        import agents
        results["Agents package"] = {
            "passed": True,
            "message": "agents package found"
        }
    except ImportError:
        results["Agents package"] = {
            "passed": False,
            "message": "agents package not found"
        }

    # Check 3: Skills package exists
    try:
        import skills
        results["Skills package"] = {
            "passed": True,
            "message": "skills package found"
        }
    except ImportError:
        results["Skills package"] = {
            "passed": False,
            "message": "skills package not found"
        }

    # Check 4: Config files exist
    config_dir = Path(__file__).parent.parent / "config" / "modes"
    required_configs = ["hybrid.yaml", "skills_only.yaml", "agents_only.yaml"]

    missing_configs = [
        cfg for cfg in required_configs
        if not (config_dir / cfg).exists()
    ]

    if not missing_configs:
        results["Config files"] = {
            "passed": True,
            "message": f"All {len(required_configs)} mode config files found"
        }
    else:
        results["Config files"] = {
            "passed": False,
            "message": f"Missing config files: {', '.join(missing_configs)}"
        }

    # Check 5: Router can be initialized
    try:
        from core.router import TaskRouter
        router = TaskRouter()
        test_result = router.route("test query")

        if "target" in test_result and "handler" in test_result:
            results["Router functionality"] = {
                "passed": True,
                "message": "Router initializes and routes successfully"
            }
        else:
            results["Router functionality"] = {
                "passed": False,
                "message": "Router returned unexpected format"
            }
    except Exception as e:
        results["Router functionality"] = {
            "passed": False,
            "message": f"Router initialization failed: {e}"
        }

    # Print results
    print(format_validation(results, args.format))

    # Return exit code based on all checks
    all_passed = all(r["passed"] for r in results.values())
    return 0 if all_passed else 1


def cmd_version(args) -> int:
    """
    Version command - show version and system info

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0=success)
    """
    import platform

    info = {
        "package": "crypto-skills-mcp",
        "version": __version__,
        "python": platform.python_version(),
        "platform": platform.platform(),
    }

    # Try to get current mode
    try:
        from core.config_loader import ConfigLoader
        loader = ConfigLoader()
        config = loader.load_config()
        info["mode"] = config.get("mode", {}).get("name", "unknown")
    except:
        info["mode"] = "unknown"

    if args.format == "json":
        print(json.dumps(info, indent=2))
    else:
        print("=" * 60)
        print("CRYPTO SKILLS MCP")
        print("=" * 60)
        print(f"Package:  {info['package']}")
        print(f"Version:  {info['version']}")
        print(f"Mode:     {info['mode']}")
        print(f"Python:   {info['python']}")
        print(f"Platform: {info['platform']}")
        print("=" * 60)

    return 0


def main():
    """
    Main CLI entry point

    Handles command parsing and routing to appropriate handlers.
    """
    parser = argparse.ArgumentParser(
        description="Crypto Skills MCP - Hybrid Intelligence for Crypto Analysis",
        epilog="""
Examples:
  # Route a query and see decision
  crypto-skills route "Calculate RSI for BTC"

  # Show current configuration
  crypto-skills config

  # Validate installation
  crypto-skills validate

  # Show version info
  crypto-skills version

  # Get JSON output
  crypto-skills route "BTC sentiment analysis" --json
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Global options
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Route command
    parser_route = subparsers.add_parser(
        "route",
        help="Route a query and show routing decision"
    )
    parser_route.add_argument(
        "query",
        help="Query to route (e.g., 'Calculate RSI for BTC')"
    )

    # Config command
    parser_config = subparsers.add_parser(
        "config",
        help="Show or modify configuration"
    )
    parser_config.add_argument(
        "--mode",
        choices=["hybrid", "skills_only", "agents_only"],
        help="Switch to specified mode (coming in Phase 2)"
    )

    # Validate command
    parser_validate = subparsers.add_parser(
        "validate",
        help="Validate installation and configuration"
    )

    # Version command
    parser_version = subparsers.add_parser(
        "version",
        help="Show version and system information"
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle no command
    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate command handler
    handlers = {
        "route": cmd_route,
        "config": cmd_config,
        "validate": cmd_validate,
        "version": cmd_version,
    }

    handler = handlers.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print("\n[WARN] Operation cancelled by user", file=sys.stderr)
            return 130
        except Exception as e:
            if args.debug:
                raise
            print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
            print("        Use --debug flag for full traceback", file=sys.stderr)
            return 2
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
