#!/usr/bin/env python3
"""Quick verification of thesis synthesizer fixes"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.thesis_synthesizer import ThesisSynthesizer

# Test 1: Check get_capabilities structure
print("Testing get_capabilities()...")
synthesizer = ThesisSynthesizer()
capabilities = synthesizer.get_capabilities()

required_fields = [
    "name", "description", "type", "domain", "capabilities",
    "required_mcps", "optional_mcps", "token_efficiency", "use_cases"
]

print("\n✅ Field existence checks:")
for field in required_fields:
    exists = field in capabilities
    print(f"  {field}: {'✅' if exists else '❌'}")

print("\n✅ Value checks:")
print(f"  domain: {capabilities.get('domain')} (expected: strategic_orchestration)")
print(f"  required_mcps: {capabilities.get('required_mcps')} (expected: [])")
print(f"  optional_mcps: {capabilities.get('optional_mcps')} (expected: [])")

print("\n✅ Capabilities list:")
expected_caps = [
    "comprehensive_analysis_orchestration",
    "conflict_detection_resolution",
    "weighted_signal_synthesis",
    "investment_thesis_generation"
]
for cap in expected_caps:
    exists = cap in capabilities.get("capabilities", [])
    print(f"  {cap}: {'✅' if exists else '❌'}")

print("\n" + "="*60)
if all(field in capabilities for field in required_fields):
    print("✅ All required fields present!")
else:
    print("❌ Some fields missing")

if capabilities.get("domain") == "strategic_orchestration":
    print("✅ Domain correct!")
else:
    print(f"❌ Domain wrong: {capabilities.get('domain')}")

if all(cap in capabilities.get("capabilities", []) for cap in expected_caps):
    print("✅ All expected capabilities present!")
else:
    print("❌ Some capabilities missing")
