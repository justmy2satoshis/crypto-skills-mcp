#!/usr/bin/env python3
"""Fix thesis_synthesizer.py capabilities"""

with open("agents/thesis_synthesizer.py", "r") as f:
    content = f.read()

# Fix domain
content = content.replace(
    '"domain": "multi_domain_synthesis"', '"domain": "strategic_orchestration"'
)

# Fix capabilities - replace the entire list
old_capabilities = """            "capabilities": [
                "agent_orchestration",
                "multi_domain_synthesis",
                "conflict_resolution",
                "thesis_generation",
                "investment_recommendations",
            ],"""

new_capabilities = """            "capabilities": [
                "comprehensive_analysis_orchestration",
                "conflict_detection_resolution",
                "investment_thesis_generation",
                "weighted_signal_synthesis",
            ],
            "required_mcps": [],  # Orchestrator delegates to specialized agents
            "optional_mcps": [],  # Orchestrator delegates to specialized agents"""

content = content.replace(old_capabilities, new_capabilities)

with open("agents/thesis_synthesizer.py", "w") as f:
    f.write(content)

print("Fixed thesis_synthesizer.py")
