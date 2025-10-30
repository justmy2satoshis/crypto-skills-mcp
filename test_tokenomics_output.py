#!/usr/bin/env python3
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from agents.crypto_vc_analyst import CryptoVCAnalyst

async def test():
    analyst = CryptoVCAnalyst()
    result = await analyst.analyze_tokenomics('BTC')

    print('Keys in result:', list(result.keys()))
    print('Has overall_score:', 'overall_score' in result)
    print('Has score:', 'score' in result)

    if 'overall_score' in result:
        print('✅ overall_score found:', result['overall_score'])
    if 'score' in result:
        print('❌ score found (should be overall_score):', result['score'])

    print('\nSupply analysis keys:', list(result.get('supply_analysis', {}).keys()))
    print('Distribution keys:', list(result.get('distribution', {}).keys()))
    print('Utility keys:', list(result.get('utility', {}).keys()))

asyncio.run(test())
