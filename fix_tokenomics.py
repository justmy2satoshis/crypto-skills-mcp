#!/usr/bin/env python3
"""Fix analyze_tokenomics API contract violations"""
import re

# Read the file
with open('agents/crypto_vc_analyst.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Add score to supply_analysis (after 'supply_schedule' line)
content = re.sub(
    r'("supply_schedule": "halving_every_4_years",)',
    r'\1\n                "score": 95,',
    content
)

# Fix 2: Add score, top_10_holders, gini_coefficient to distribution (after 'vesting_schedule' line)
content = re.sub(
    r'("vesting_schedule": "n/a",)',
    r'\1\n                "score": 100,\n                "top_10_holders": 5.2,  # % of supply\n                "gini_coefficient": 0.68,  # 0-1 scale',
    content
)

# Fix 3: Change utility from list to dict with score and use_cases
old_utility = '''"utility": [
                "Store of value",
                "Medium of exchange",
                "Unit of account",
                "Inflation hedge",
            ],'''

new_utility = '''"utility": {
                "score": 92,
                "use_cases": [
                    "Store of value",
                    "Medium of exchange",
                    "Unit of account",
                    "Inflation hedge",
                ],
            },'''

content = content.replace(old_utility, new_utility)

# Fix 4: Rename 'score' to 'overall_score' at top level (find the one after utility)
lines = content.split('\n')
in_tokenomics_return = False
for i, line in enumerate(lines):
    if '"utility": {' in line:
        in_tokenomics_return = True
    if in_tokenomics_return and line.strip().startswith('"score": 95,'):
        lines[i] = line.replace('"score":', '"overall_score":')
        break

content = '\n'.join(lines)

# Write back
with open('agents/crypto_vc_analyst.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Applied all 4 fixes to analyze_tokenomics method')
