"""
Setup configuration for Crypto Skills MCP

Hybrid Claude Skills + Agents crypto analysis system with modular installation.
"""

from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
import subprocess
import sys
from pathlib import Path

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


# Read requirements
def read_requirements(filename):
    """Read requirements from file, excluding comments and empty lines."""
    with open(filename, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#") and not line.startswith("python>=")
        ]


# Core requirements
install_requires = read_requirements("requirements.txt")

# Optional dependencies for different modes
extras_require = {
    "skills": [
        "numpy>=1.24.0",
        "pandas>=2.0.0",
    ],
    "agents": [
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
    ],
    "dev": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
        "black>=23.0.0",
        "ruff>=0.1.0",
        "mypy>=1.0.0",
    ],
    "test": [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "pytest-mock>=3.10.0",
    ],
}

# All includes everything
extras_require["all"] = list(set(sum(extras_require.values(), [])))


# Custom install commands for auto-configuration
class PostInstallCommand(install):
    """Post-installation for installation mode"""
    def run(self):
        install.run(self)

        # Get absolute path to post-install script
        script_dir = Path(__file__).parent
        post_install_script = script_dir / 'scripts' / 'post_install.py'

        print("\n" + "=" * 70)
        print("🔧 Running post-installation MCP configuration...")
        print("=" * 70)

        try:
            # Verify script exists
            if not post_install_script.exists():
                raise FileNotFoundError(f"Post-install script not found: {post_install_script}")

            # Run configuration script with absolute path
            result = subprocess.call([sys.executable, str(post_install_script)])

            if result == 0:
                print("\n✅ MCP configuration successful!")
                print("   Restart Claude Code to use crypto-skills-mcp")
                print("=" * 70 + "\n")
            else:
                raise RuntimeError(f"Post-install script failed with exit code {result}")

        except Exception as e:
            print("\n" + "=" * 70)
            print("⚠️  MCP CONFIGURATION FAILED")
            print("=" * 70)
            print(f"Error: {e}")
            print(f"\n🔧 To configure manually, run:")
            print(f"    cd {script_dir}")
            print(f"    python scripts/post_install.py")
            print(f"\n   Or use the CLI command:")
            print(f"    crypto-skills configure")
            print("=" * 70 + "\n")

            # Print stack trace for debugging
            import traceback
            traceback.print_exc()


class PostDevelopCommand(develop):
    """Post-installation for development mode"""
    def run(self):
        develop.run(self)

        # Get absolute path to post-install script
        script_dir = Path(__file__).parent
        post_install_script = script_dir / 'scripts' / 'post_install.py'

        print("\n" + "=" * 70)
        print("🔧 Running post-installation MCP configuration (dev mode)...")
        print("=" * 70)

        try:
            # Verify script exists
            if not post_install_script.exists():
                raise FileNotFoundError(f"Post-install script not found: {post_install_script}")

            # Run configuration script with absolute path
            result = subprocess.call([sys.executable, str(post_install_script)])

            if result == 0:
                print("\n✅ MCP configuration successful!")
                print("   Restart Claude Code to use crypto-skills-mcp")
                print("=" * 70 + "\n")
            else:
                raise RuntimeError(f"Post-install script failed with exit code {result}")

        except Exception as e:
            print("\n" + "=" * 70)
            print("⚠️  MCP CONFIGURATION FAILED")
            print("=" * 70)
            print(f"Error: {e}")
            print(f"\n🔧 To configure manually, run:")
            print(f"    cd {script_dir}")
            print(f"    python scripts/post_install.py")
            print(f"\n   Or use the CLI command:")
            print(f"    crypto-skills configure")
            print("=" * 70 + "\n")

            # Print stack trace for debugging
            import traceback
            traceback.print_exc()


setup(
    name="crypto-skills-mcp",
    version="1.0.0",
    author="Crypto Skills Development Team",
    author_email="contact@crypto-skills.dev",
    description="Hybrid Claude Skills + Agents crypto analysis system with 60-65% token reduction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/crypto-skills-mcp",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/crypto-skills-mcp/issues",
        "Source": "https://github.com/yourusername/crypto-skills-mcp",
        "Documentation": "https://github.com/yourusername/crypto-skills-mcp#readme",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "docs"]),
    py_modules=["cli", "mcp_client"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.10",
    install_requires=install_requires,
    extras_require=extras_require,
    cmdclass={
        'install': PostInstallCommand,
        'develop': PostDevelopCommand,
    },
    entry_points={
        "console_scripts": [
            "crypto-skills=cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json", "*.md"],
    },
    keywords=[
        "cryptocurrency",
        "investment",
        "analysis",
        "mcp",
        "model-context-protocol",
        "claude",
        "ai-agents",
        "skills",
        "sentiment-analysis",
        "technical-analysis",
        "fundamental-analysis",
    ],
    zip_safe=False,
)
