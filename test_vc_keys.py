import asyncio
from agents.crypto_vc_analyst import CryptoVCAnalyst


async def main():
    analyst = CryptoVCAnalyst()
    result = await analyst.generate_due_diligence_report("BTC")
    print("Keys in result:", list(result.keys()))
    print("Has overall_score:", "overall_score" in result)


if __name__ == "__main__":
    asyncio.run(main())
