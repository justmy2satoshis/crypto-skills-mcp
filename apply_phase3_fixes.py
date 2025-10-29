#!/usr/bin/env python3
"""Apply Phase 3 fixes to thesis_synthesizer.py"""
import re

file_path = "agents/thesis_synthesizer.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Change domain
content = content.replace(
    '"domain": "multi_domain_synthesis",', '"domain": "strategic_orchestration",'
)

# Fix 2: Replace capabilities list (more targeted replacement)
old_caps_block = """            "capabilities": [
                "agent_orchestration",
                "multi_domain_synthesis",
                "conflict_resolution",
                "thesis_generation",
                "investment_recommendations",
            ],"""

new_caps_block = """            "capabilities": [
                "comprehensive_analysis_orchestration",
                "conflict_detection_resolution",
                "investment_thesis_generation",
                "weighted_signal_synthesis",
            ],
            "required_mcps": [],  # Orchestrator delegates to specialized agents
            "optional_mcps": [],  # Orchestrator delegates to specialized agents"""

content = content.replace(old_caps_block, new_caps_block)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("✓ Fixed get_capabilities() method")
print("  - Changed domain to 'strategic_orchestration'")
print("  - Replaced capabilities list with 4 specific capabilities")
print("  - Added required_mcps and optional_mcps fields")
