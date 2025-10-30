#!/usr/bin/env python3
"""Apply test fixes for VC analyst tests"""
import re


def fix_tests():
    test_file = "tests/test_agents/test_vc_analyst.py"

    with open(test_file, "r", encoding="utf-8") as f:
        content = f.read()

    original = content

    # Fix 1: VERY_HIGH -> EXTREME
    content = content.replace("RiskLevel.VERY_HIGH", "RiskLevel.EXTREME")
    content = content.replace('"very_high"', '"extreme"')
    content = content.replace("'very_high'", "'extreme'")

    # Fix 2: overall_score -> score
    content = content.replace('"overall_score"', '"score"')
    content = content.replace("'overall_score'", "'score'")

    if content != original:
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ Fixed {test_file}")
        print("  - Replaced VERY_HIGH with EXTREME")
        print("  - Replaced overall_score with score")
    else:
        print(f"  No changes needed")


if __name__ == "__main__":
    fix_tests()
