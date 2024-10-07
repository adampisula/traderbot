import asyncio

from providers.ccxt import CCXTProvider

PAIRS = [
    ("BTC", "USDT"),
    # ("BTC", "USDC"),
    # ("BTC", "BUSD"),
    ("BTC", "ETH"),
    # ("ETH", "USDT"),
    # ("ETH", "USDC"),
    # ("ETH", "BUSD"),
    # ("BNB", "USDT"),
    # ("ADA", "USDT"),
    # ("SOL", "USDT"),
    # ("XRP", "USDT"),
]


async def main():
    provider = CCXTProvider()
    market_frames = await provider.get_history(PAIRS)
    print(market_frames)


if __name__ == "__main__":
    asyncio.run(main())
