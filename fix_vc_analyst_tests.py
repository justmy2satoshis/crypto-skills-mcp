#!/usr/bin/env python3
"""
Fix VC Analyst tests to match current API contracts

Changes needed:
1. Replace "overall_score" with "score" in tokenomics tests
2. Replace RiskLevel.VERY_HIGH with RiskLevel.EXTREME
3. Fix any other enum value changes
4. Update assertion patterns to match actual return structures
"""

import re
from pathlib import Path


def fix_vc_analyst_tests():
    """Fix all VC analyst test expectations"""
    # Get script directory and construct absolute path
    script_dir = Path(__file__).parent
    test_file = script_dir / "tests" / "test_agents" / "test_vc_analyst.py"

    # Read the file
    content = test_file.read_text(encoding="utf-8")
    original = content

    # Fix 1: overall_score -> score in assertions
    content = content.replace('"overall_score" in result', '"score" in result')
    content = content.replace('["overall_score"]', '["score"]')
    content = content.replace("['overall_score']", "['score']")

    # Fix 2: VERY_HIGH -> EXTREME enum value
    content = content.replace("RiskLevel.VERY_HIGH", "RiskLevel.EXTREME")
    content = content.replace('"very_high"', '"extreme"')
    content = content.replace("'very_high'", "'extreme'")

    # Fix 3: Update test_init_without_mcp_client description (already fixed earlier)
    # This should already be correct from earlier fix

    # Fix 4: Update enum member tests
    # Replace expected enum values in test_risk_level_all_members
    content = re.sub(
        r'expected_members\s*=\s*\{[^}]*"LOW"[^}]*"MEDIUM"[^}]*"HIGH"[^}]*"VERY_HIGH"[^}]*\}',
        'expected_members = {"LOW", "MEDIUM", "HIGH", "EXTREME"}',
        content,
    )

    # Fix 5: Update test_risk_level_values assertions
    # Find and replace the VERY_HIGH value assertion
    content = re.sub(
        r'assert RiskLevel\.VERY_HIGH\.value == "very_high"',
        'assert RiskLevel.EXTREME.value == "extreme"',
        content,
    )

    # Write back if changed
    if content != original:
        test_file.write_text(content, encoding="utf-8")
        print(f"[OK] Fixed {test_file}")
        print("  - Replaced 'overall_score' with 'score'")
        print("  - Replaced 'VERY_HIGH' with 'EXTREME'")
        print("  - Updated enum member expectations")
        return True
    else:
        print(f"  No changes needed for {test_file}")
        return False


if __name__ == "__main__":
    print("Fixing VC Analyst tests...")
    if fix_vc_analyst_tests():
        print("\n[OK] Test fixes applied successfully")
    else:
        print("\n  Tests already up to date")
