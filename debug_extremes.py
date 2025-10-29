"""Debug script to check extremes dict"""

import asyncio
from agents.crypto_sentiment_analyst import CryptoSentimentAnalyst


async def main():
    analyst = CryptoSentimentAnalyst()
    extremes = await analyst.detect_sentiment_extremes("bitcoin")
    print(f"extremes keys: {list(extremes.keys())}")
    print(f"extremes: {extremes}")
    print(f"'is_extreme' in extremes: {'is_extreme' in extremes}")

    if "is_extreme" in extremes:
        print(f"extremes['is_extreme']: {extremes['is_extreme']}")
    else:
        print("ERROR: 'is_extreme' key not found!")


if __name__ == "__main__":
    asyncio.run(main())
