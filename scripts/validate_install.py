#!/usr/bin/env python3
"""
Installation validation script for crypto-skills-mcp

Verifies that:
1. Package is installed correctly
2. FastMCP dependency is available
3. .claude.json is configured properly
4. MCP server can start successfully
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple


def check_package_installed() -> Tuple[bool, str]:
    """Verify crypto-skills-mcp package is installed"""
    try:
        import mcp_client
        return True, f"✓ Package installed at: {Path(mcp_client.__file__).parent}"
    except ImportError as e:
        return False, f"✗ Package not installed: {e}"


def check_fastmcp_available() -> Tuple[bool, str]:
    """Verify FastMCP dependency is available"""
    try:
        import fastmcp
        return True, f"✓ FastMCP version: {fastmcp.__version__}"
    except ImportError:
        return False, "✗ FastMCP not installed (run: pip install fastmcp>=2.0.0)"


def check_server_file() -> Tuple[bool, str]:
    """Verify server.py exists"""
    try:
        import mcp_client
        project_root = Path(mcp_client.__file__).parent
        server_file = project_root / "server.py"

        if server_file.exists():
            return True, f"✓ server.py found at: {server_file}"
        else:
            return False, f"✗ server.py not found at: {server_file}"
    except Exception as e:
        return False, f"✗ Error checking server.py: {e}"


def find_claude_config() -> Path:
    """Find .claude.json location"""
    home = Path.home()
    return home / ".claude.json"


def check_claude_config() -> Tuple[bool, str]:
    """Verify .claude.json configuration"""
    config_path = find_claude_config()

    if not config_path.exists():
        return False, f"✗ .claude.json not found at: {config_path}"

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        if "mcpServers" not in config:
            return False, "✗ .claude.json missing 'mcpServers' section"

        if "crypto-skills-mcp" not in config["mcpServers"]:
            return False, "✗ crypto-skills-mcp not configured in .claude.json"

        mcp_config = config["mcpServers"]["crypto-skills-mcp"]

        # Validate required fields
        required_fields = {
            "type": "stdio",
            "command": str,
            "args": list,
            "cwd": str,
            "env": dict
        }

        missing = []
        invalid = []

        for field, expected_type in required_fields.items():
            if field not in mcp_config:
                missing.append(field)
            elif expected_type != str and not isinstance(mcp_config[field], expected_type):
                invalid.append(f"{field} (expected {expected_type.__name__})")

        if missing:
            return False, f"✗ Missing required fields: {', '.join(missing)}"

        if invalid:
            return False, f"✗ Invalid field types: {', '.join(invalid)}"

        # Check specific values
        if mcp_config["type"] != "stdio":
            return False, f"✗ type must be 'stdio', got: {mcp_config['type']}"

        if mcp_config["args"] != ["server.py"]:
            return False, f"✗ args should be ['server.py'], got: {mcp_config['args']}"

        if "PYTHONUNBUFFERED" not in mcp_config["env"]:
            return False, "✗ PYTHONUNBUFFERED not set in env (recommended)"

        return True, f"✓ .claude.json configured correctly at: {config_path}"

    except json.JSONDecodeError as e:
        return False, f"✗ Invalid JSON in .claude.json: {e}"
    except Exception as e:
        return False, f"✗ Error reading .claude.json: {e}"


def check_server_starts() -> Tuple[bool, str]:
    """Test if server can start (imports only, doesn't run)"""
    try:
        import mcp_client
        project_root = Path(mcp_client.__file__).parent
        server_file = project_root / "server.py"

        # Try to compile the server file
        with open(server_file, 'r', encoding='utf-8') as f:
            code = f.read()

        compile(code, str(server_file), 'exec')
        return True, "✓ server.py compiles successfully"

    except SyntaxError as e:
        return False, f"✗ Syntax error in server.py: {e}"
    except Exception as e:
        return False, f"✗ Error checking server.py: {e}"


def run_validation():
    """Run all validation checks"""
    print("=" * 70)
    print("crypto-skills-mcp Installation Validation")
    print("=" * 70)
    print()

    checks = [
        ("Package Installation", check_package_installed),
        ("FastMCP Dependency", check_fastmcp_available),
        ("Server File", check_server_file),
        ("Claude Configuration", check_claude_config),
        ("Server Compilation", check_server_starts),
    ]

    results = []
    all_passed = True

    for name, check_func in checks:
        print(f"Checking {name}...", end=" ")
        passed, message = check_func()
        results.append((name, passed, message))
        all_passed = all_passed and passed
        print()
        print(f"  {message}")
        print()

    print("=" * 70)
    if all_passed:
        print("✅ ALL CHECKS PASSED")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Restart Claude Code")
        print("  2. Check MCP server status panel")
        print("  3. crypto-skills-mcp should show: Status: ✓ connected")
        print()
        return 0
    else:
        print("❌ SOME CHECKS FAILED")
        print("=" * 70)
        print()
        print("Failed checks:")
        for name, passed, message in results:
            if not passed:
                print(f"  • {name}")
                print(f"    {message}")
        print()
        print("To fix:")
        print("  1. Reinstall package: pip install -e .")
        print("  2. Run post-install script: python scripts/post_install.py")
        print("  3. Restart Claude Code")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(run_validation())
