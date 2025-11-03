#!/usr/bin/env python3
"""
Post-installation configuration for crypto-skills-mcp

Safely adds MCP server configuration to .claude.json without
disrupting existing MCP servers.
"""
import json
import sys
import shutil
from pathlib import Path
from typing import Dict, Any, Optional


def find_claude_config() -> Optional[Path]:
    """Find .claude.json location across platforms"""
    home = Path.home()
    claude_config = home / ".claude.json"

    if not claude_config.exists():
        print(f"[WARN] .claude.json not found at {claude_config}", file=sys.stderr)
        print("       Claude Code may not be installed or configured yet.", file=sys.stderr)
        return None

    return claude_config


def backup_config(config_path: Path) -> Path:
    """Create atomic backup of config file"""
    backup_path = config_path.with_suffix('.json.backup')
    shutil.copy2(config_path, backup_path)
    print(f"[BACKUP] Created backup: {backup_path}")
    return backup_path


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load and validate .claude.json"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {config_path}: {e}", file=sys.stderr)
        raise


def get_project_root() -> Path:
    """Get installed package location"""
    try:
        import mcp_client
        return Path(mcp_client.__file__).parent
    except ImportError:
        # Fallback to current directory if mcp_client not installed yet
        return Path(__file__).parent.parent


def create_mcp_config() -> Dict[str, Any]:
    """Create crypto-skills-mcp server configuration"""
    project_root = get_project_root()

    return {
        "command": sys.executable,
        "args": ["server.py"],
        "cwd": str(project_root),
        "env": {
            "MODE": "hybrid"
        }
    }


def safe_merge_config(config: Dict[str, Any]) -> bool:
    """Safely merge crypto-skills-mcp into mcpServers

    Returns:
        bool: True if configuration was added/updated, False if no change needed
    """
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    new_config = create_mcp_config()
    existing_config = config["mcpServers"].get("crypto-skills-mcp")

    if existing_config:
        # Compare existing with new configuration
        if existing_config == new_config:
            print("[OK] crypto-skills-mcp already up-to-date in .claude.json")
            return False
        else:
            # Update existing configuration
            print("[INFO] Updating crypto-skills-mcp configuration...")
            print(f"[INFO] Old args: {existing_config.get('args')}")
            print(f"[INFO] New args: {new_config.get('args')}")
            config["mcpServers"]["crypto-skills-mcp"] = new_config
            print("[OK] crypto-skills-mcp configuration updated")
            return True
    else:
        # Add new configuration
        existing_count = len(config["mcpServers"])
        print(f"[INFO] Found {existing_count} existing MCP servers")
        config["mcpServers"]["crypto-skills-mcp"] = new_config
        print("[OK] Added crypto-skills-mcp to MCP servers")
        print(f"[OK] All {existing_count} existing MCP servers preserved")
        return True


def atomic_write(config_path: Path, config: Dict[str, Any]):
    """Write config with atomic operation to prevent corruption"""
    temp_path = config_path.with_suffix('.json.tmp')

    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        # Atomic rename
        temp_path.replace(config_path)
        print(f"[OK] Updated {config_path}")
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise e


def configure_mcp():
    """Main configuration function"""
    print("=" * 70)
    print("Configuring crypto-skills-mcp for Claude Code")
    print("=" * 70)

    # Check for skip flag
    if sys.argv and "--skip-autoconfig" in sys.argv:
        print("\n[INFO] Skipping auto-configuration (--skip-autoconfig flag detected)")
        return

    config_path = find_claude_config()
    if not config_path:
        print("\n[WARN] Skipping auto-configuration (Claude Code not detected)", file=sys.stderr)
        print("       Run 'crypto-skills configure' later to set up manually", file=sys.stderr)
        return

    try:
        # Create backup before any modifications
        backup_config(config_path)

        # Load existing configuration
        config = load_config(config_path)

        # Safely merge crypto-skills-mcp configuration
        changed = safe_merge_config(config)

        if changed:
            # Atomic write of updated configuration
            atomic_write(config_path, config)

            print("\n" + "=" * 70)
            print("Configuration Complete!")
            print("=" * 70)
            print(f"\n[OK] crypto-skills-mcp added to .claude.json")
            print(f"[OK] {len(config['mcpServers'])} total MCP servers configured")
            print(f"\nNext Steps:")
            print(f"   1. Restart Claude Code")
            print(f"   2. Verify with: crypto-skills validate")
            print(f"   3. Test agents with crypto analysis queries")
        else:
            print("\n[OK] No configuration changes needed")

    except Exception as e:
        print(f"\n[ERROR] Configuration failed: {e}", file=sys.stderr)
        print(f"        Manual configuration may be required", file=sys.stderr)
        print(f"        Run: crypto-skills configure", file=sys.stderr)
        # Don't raise - installation should succeed even if config fails
        return


if __name__ == "__main__":
    configure_mcp()
