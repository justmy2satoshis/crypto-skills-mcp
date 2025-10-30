#!/usr/bin/env python3
import subprocess
import sys

result = subprocess.run(
    [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_agents/test_thesis_synthesizer.py",
        "-v",
        "--tb=short",
        "--cache-clear",
    ],
    cwd="C:\\Users\\User\\crypto-skills-mcp",
    capture_output=True,
    text=True,
)

print(result.stdout)
print(result.stderr)
sys.exit(result.returncode)
