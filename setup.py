"""
Setup configuration for Crypto Skills MCP

Hybrid Claude Skills + Agents crypto analysis system with modular installation.
"""

from setuptools import setup, find_packages

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
    entry_points={
        "console_scripts": [
            "crypto-skills=core.cli:main",
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
