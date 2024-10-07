import asyncio
import dotenv
import os
from typing import List

from timers.interval import IntervalTimer
from providers.crypto_exchange import CryptoExchangeProvider
from strategies.average_crossover import AverageCrossover
from models.pair import Pair


async def main():
    dotenv.load_dotenv()
    timer = IntervalTimer(3)
    
    async for val in timer:
        print(val)


async def fetch_market_data():
    dotenv.load_dotenv()

    binance_api_key = os.getenv("BINANCE_API_KEY")
    binance_api_secret = os.getenv("BINANCE_API_SECRET")

    PAIRS: List[Pair] = [
        Pair("BTC", "USDT"),
        Pair("BTC", "USDC"),
        Pair("BTC", "USDC"),
        Pair("ETH", "USDT"),
        Pair("ETH", "USDC"),
        Pair("BNB", "USDT"),
        Pair("ADA", "USDT"),
        Pair("SOL", "USDT"),
        Pair("XRP", "USDT"),
    ]

    provider = CryptoExchangeProvider(
        apikey=binance_api_key,
        secret=binance_api_secret,
    )
    timer = IntervalTimer(
        provider=provider,
        pairs=PAIRS,
        timeframe_minutes=60,
    )
    strategy = AverageCrossover(IntervalTimer(provider=provider, PAIRS, 60), provider)
    await strategy.start()

    await provider._exchange.close()


if __name__ == "__main__":
    asyncio.run(fetch_market_data())
    # if input("F/M? ").lower() == "f":
    #     asyncio.run(fetch_market_data())
    # else:
    #     asyncio.run(main())
