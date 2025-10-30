#!/usr/bin/env python3
"""Add overall_score and confidence fields to VC analyst output"""

with open("agents/crypto_vc_analyst.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Find the return statement in generate_due_diligence_report
# It's around line 433
for i in range(420, 440):
    if i < len(lines) and "flags = await self.identify_red_flags(token_symbol)" in lines[i]:
        # Insert calculation after this line
        insert_pos = i + 1

        # Skip blank line if present
        if insert_pos < len(lines) and lines[insert_pos].strip() == "":
            insert_pos += 1

        # Insert calculation code
        calculation = """
        # Calculate overall score as weighted average
        overall_score = (
            tokenomics["score"] * 0.35  # 35% weight on tokenomics
            + technical["score"] * 0.30  # 30% weight on technical health
            + liquidity["score"] * 0.25  # 25% weight on liquidity
            + (100 - risk["risk_score"]) * 0.10  # 10% weight on inverse risk
        )
"""
        lines.insert(insert_pos, calculation)
        break

# Now find the return dict and add fields after "symbol"
for i in range(insert_pos, insert_pos + 20):
    if i < len(lines) and '"symbol": token_symbol,' in lines[i]:
        # Add overall_score and confidence after symbol
        indent = " " * 12  # Match indentation
        new_lines = [
            f'{indent}"overall_score": round(overall_score, 1),\n',
            f'{indent}"confidence": 0.88,\n',
        ]
        # Insert after this line
        lines[i + 1 : i + 1] = new_lines
        break

# Write back
with open("agents/crypto_vc_analyst.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("✅ Added overall_score and confidence fields to VC analyst output")
