#!/usr/bin/env python3
"""Run Black formatter on the entire codebase"""
import subprocess
import sys

try:
    result = subprocess.run(
        ["python", "-m", "black", "."],
        cwd="/c/Users/User/crypto-skills-mcp",
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
except Exception as e:
    print(f"Error running Black: {e}")
    sys.exit(1)
