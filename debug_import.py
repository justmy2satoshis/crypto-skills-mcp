#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

print("Python path:")
for p in sys.path:
    print(f"  {p}")

print("\nImporting agents.crypto_vc_analyst...")
from agents.crypto_vc_analyst import CryptoVCAnalyst

print(f"Module file: {CryptoVCAnalyst.__module__}")

import inspect
print(f"Source file: {inspect.getfile(CryptoVCAnalyst)}")

# Check the actual return statement
import asyncio
analyst = CryptoVCAnalyst()
result = asyncio.run(analyst.analyze_tokenomics("BTC"))

print("\nResult keys:", list(result.keys()))
print("Has 'overall_score':", "overall_score" in result)
print("Has 'score':", "score" in result)

print("\nDistribution keys:", list(result.get("distribution", {}).keys()))
print("\nSupply analysis keys:", list(result.get("supply_analysis", {}).keys()))
