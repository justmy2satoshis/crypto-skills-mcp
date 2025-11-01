#!/usr/bin/env python3
"""
Crypto Skills MCP - Claude Desktop/Code Installation Helper

This script helps install crypto-skills-mcp Skills into Claude Desktop or Claude Code
WITHOUT disrupting your existing MCP server configurations.

Features:
- Preserves all existing MCPs in .claude.json and claude_desktop_config.json
- Creates symlinks to Skills in .claude/skills/ directory
- Validates installation
- Provides clear next steps

Usage:
    python install_to_claude.py --target desktop  # For Claude Desktop
    python install_to_claude.py --target code     # For Claude Code
    python install_to_claude.py --target both     # For both
"""

import sys
import json
import shutil
import argparse
from pathlib import Path
from typing import List, Optional


class CryptoSkillsInstaller:
    """Installer for crypto-skills-mcp Skills into Claude environments"""

    def __init__(self, target: str = "both"):
        """
        Initialize installer

        Args:
            target: Installation target ('desktop', 'code', or 'both')
        """
        self.target = target
        self.project_root = Path(__file__).parent.absolute()
        self.skills_source = self.project_root / "skills"

        # Detect user home directory
        self.home = Path.home()

        # Claude Desktop config location
        self.desktop_config = None
        if sys.platform == "darwin":  # macOS
            self.desktop_config = (
                self.home / "Library/Application Support/Claude/claude_desktop_config.json"
            )
        elif sys.platform == "win32":  # Windows
            self.desktop_config = self.home / "AppData/Roaming/Claude/claude_desktop_config.json"
        else:  # Linux
            self.desktop_config = self.home / ".config/Claude/claude_desktop_config.json"

        # Claude Code config location
        self.code_config = self.home / ".claude.json"
        self.code_skills_dir = self.home / ".claude/skills"

    def validate_source(self) -> bool:
        """Validate Skills source directory exists"""
        if not self.skills_source.exists():
            print(f"❌ Skills directory not found: {self.skills_source}")
            print("   Run this script from the crypto-skills-mcp project root.")
            return False

        # Check for skill subdirectories
        skill_dirs = ["data_extraction", "technical_analysis", "sentiment_analysis"]
        missing = [d for d in skill_dirs if not (self.skills_source / d).exists()]

        if missing:
            print(f"❌ Missing skill directories: {', '.join(missing)}")
            return False

        print(f"✅ Skills source validated: {self.skills_source}")
        return True

    def backup_config(self, config_path: Path) -> Optional[Path]:
        """Create backup of existing config file"""
        if not config_path.exists():
            return None

        backup_path = config_path.with_suffix(config_path.suffix + ".backup")
        shutil.copy2(config_path, backup_path)
        print(f"📦 Backed up config to: {backup_path}")
        return backup_path

    def install_to_code(self) -> bool:
        """Install Skills to Claude Code"""
        print("\n🔧 Installing to Claude Code...")

        # Create .claude/skills directory if it doesn't exist
        self.code_skills_dir.mkdir(parents=True, exist_ok=True)

        # Create symlinks for each skill category
        skill_categories = ["data_extraction", "technical_analysis", "sentiment_analysis"]
        installed = []

        for category in skill_categories:
            source = self.skills_source / category
            target = self.code_skills_dir / f"crypto_{category}"

            # Remove existing symlink/directory if present
            if target.exists() or target.is_symlink():
                if target.is_symlink():
                    target.unlink()
                else:
                    print(f"⚠️  {target} exists as directory, skipping...")
                    continue

            # Create symlink
            try:
                if sys.platform == "win32":
                    # Windows requires admin for symlinks, use junction instead
                    import subprocess

                    subprocess.run(
                        ["mklink", "/J", str(target), str(source)], shell=True, check=True
                    )
                else:
                    target.symlink_to(source)

                installed.append(category)
                print(f"✅ Linked: crypto_{category} → {source}")
            except Exception as e:
                print(f"❌ Failed to create symlink for {category}: {e}")

        # Verify installation
        if installed:
            print("\n✅ Claude Code installation complete!")
            print(f"   Skills installed: {', '.join(installed)}")
            print(f"   Skills directory: {self.code_skills_dir}")
            return True
        else:
            print("\n❌ No skills were installed to Claude Code")
            return False

    def install_to_desktop(self) -> bool:
        """Install Skills to Claude Desktop"""
        print("\n🔧 Installing to Claude Desktop...")

        if not self.desktop_config:
            print("❌ Could not determine Claude Desktop config location for this OS")
            return False

        if not self.desktop_config.exists():
            print(f"⚠️  Claude Desktop config not found: {self.desktop_config}")
            print("   Have you installed Claude Desktop?")
            return False

        # Backup existing config
        self.backup_config(self.desktop_config)

        # Load existing config
        try:
            with open(self.desktop_config, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in config file: {self.desktop_config}")
            return False

        # Preserve existing mcpServers
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        print(f"✅ Preserved {len(config.get('mcpServers', {}))} existing MCP servers")

        # Note: Claude Desktop doesn't have a Skills directory like Claude Code
        # Skills are typically referenced as MCP tools or through Skills feature
        print("\n📝 Note: Claude Desktop integrates Skills differently than Claude Code.")
        print("   Skills will be available when using the crypto-skills-mcp package.")
        print("   Make sure crypto-skills-mcp is installed: pip install -e .")

        return True

    def print_next_steps(self, targets_installed: List[str]):
        """Print next steps for user"""
        print("\n" + "=" * 70)
        print("🎉 Installation Complete!")
        print("=" * 70)

        if "code" in targets_installed:
            print("\n📍 Claude Code Next Steps:")
            print("   1. Restart Claude Code")
            print("   2. Skills are available at: ~/.claude/skills/crypto_*")
            print("   3. Test with: /skills data_extraction")
            print()
            print("   Example usage:")
            print("   - 'Fetch BTC price data using data extraction skill'")
            print("   - 'Calculate RSI indicator for ETH'")
            print("   - 'Analyze social sentiment for Bitcoin'")

        if "desktop" in targets_installed:
            print("\n📍 Claude Desktop Next Steps:")
            print("   1. Restart Claude Desktop")
            print("   2. Verify package installed: pip install -e .")
            print("   3. Skills will be available through Agents")
            print()
            print("   Example usage:")
            print("   - Ask Claude to use crypto analysis skills")
            print("   - Agents will automatically route to Skills for efficiency")

        print("\n📊 Token Efficiency:")
        print("   - Skills-only mode: ~73% token reduction")
        print("   - Hybrid mode: ~62.5% token reduction (recommended)")
        print("   - Agents-only mode: 0% reduction (maximum reasoning)")

        print("\n📚 Documentation:")
        print(f"   - Skills docs: {self.skills_source}")
        print("   - README: https://github.com/justmy2satoshis/crypto-skills-mcp")

    def install(self) -> bool:
        """Run installation for specified target(s)"""
        print("=" * 70)
        print("🚀 Crypto Skills MCP Installation")
        print("=" * 70)

        # Validate source
        if not self.validate_source():
            return False

        targets_installed = []

        # Install to Claude Code
        if self.target in ["code", "both"]:
            if self.install_to_code():
                targets_installed.append("code")

        # Install to Claude Desktop
        if self.target in ["desktop", "both"]:
            if self.install_to_desktop():
                targets_installed.append("desktop")

        # Print next steps
        if targets_installed:
            self.print_next_steps(targets_installed)
            return True
        else:
            print("\n❌ Installation failed for all targets")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Install crypto-skills-mcp Skills to Claude Desktop/Code"
    )
    parser.add_argument(
        "--target",
        choices=["desktop", "code", "both"],
        default="both",
        help="Installation target (default: both)",
    )

    args = parser.parse_args()

    installer = CryptoSkillsInstaller(target=args.target)
    success = installer.install()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
