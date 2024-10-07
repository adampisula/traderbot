import asyncio
import dotenv
import os
from typing import List
from datetime import datetime
import plotly.graph_objects as go

from timers.interval import IntervalTimer
from timers.backtest import BacktestTimer
from providers.crypto import CryptoProvider
from providers.ccxt import CCXTProvider
from providers.mock_crypto import MockCryptoProvider
from strategies.average_crossover import AverageCrossover
from models.pair import Pair
from models.market import Market

dotenv.load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

TIMEFRAME_MINUTES = 5
SINCE = datetime(day=7, month=9, year=2024)
UNTIL = datetime(day=1, month=10, year=2024)
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
FILENAME = f"/home/apisula/Documents/traderbot/data/{SINCE.day}-{SINCE.month}-{SINCE.year}_{UNTIL.day}-{UNTIL.month}-{UNTIL.year}_{TIMEFRAME_MINUTES}m"

async def fetch_data():
    ce = CCXTProvider(apikey=API_KEY, secret=API_SECRET)
    try:
        market = await ce.get_history(PAIRS, since=SINCE, until=UNTIL, timeframe_minutes=TIMEFRAME_MINUTES)
        market.save_to_file(FILENAME)
    finally:
        await ce._exchange.close()

async def import_from_file():
    m = Market()
    m.import_from_file(FILENAME)

    m.logs += [(datetime(day=1, month=10, year=2024, hour=8), "Test log")]
    m.logs += [(datetime(day=2, month=10, year=2024, hour=13), "Other log")]

    p = Pair("ETH", "USDC")
    f = m.plot_for_pair(p, display=False)

    ohlcv = m.get_all_for_pair(p)

    timestamps = [datetime.fromtimestamp(x[0] // 1000) for x in ohlcv]
    closes = [x[1].close for x in ohlcv]

    fma = [sum(closes[i-10:i])/10 for i in range(10, len(closes))]
    sma = [sum(closes[i-50:i])/50 for i in range(50, len(closes))]

    f.add_trace(go.Scatter(x=timestamps[10:], y=fma, name="FMA", line=go.scatter.Line(color="blue")))
    f.add_trace(go.Scatter(x=timestamps[50:], y=sma, name="SMA", line=go.scatter.Line(color="purple")))
        
    f.show()

async def backtest():
    provider: CryptoProvider

    history_market = Market()
    history_market.import_from_file(FILENAME)

    STARTING_INDEX = 0

    provider = MockCryptoProvider(
        market=history_market,
        starting_index=STARTING_INDEX,
    )
    timer = BacktestTimer(
        market=history_market,
        provider=provider,
        starting_index=STARTING_INDEX
    )
    strategy = AverageCrossover(
        provider=provider,
        pairs=PAIRS,
        sma_window=50,
        fma_window=10,
        timeframe_minutes=TIMEFRAME_MINUTES,
        jitter=0.0005,
    )

    all_transactions = []
    all_logs = []
    all_function_plots = []

    async for frame in timer:
        transactions, logs, function_plots = await strategy.execute(frame)

        all_transactions += transactions
        all_logs += logs
        all_function_plots += function_plots

        provider.tick()
        timer.tick()

    p = Pair("ETH", "USDC")

    figure = history_market.plot_for_pair(p, display=False)

    fma_x: List[datetime] = []
    fma_y: List[float] = []
    sma_x: List[datetime] = []
    sma_y: List[float] = []

    for function_plot in all_function_plots:
        if function_plot[1] == f"{p} FMA":
            fma_x.append(function_plot[0])
            fma_y.append(function_plot[2])
        elif function_plot[1] == f"{p} SMA":
            sma_x.append(function_plot[0])
            sma_y.append(function_plot[2])

    figure.add_trace(go.Scatter(x=fma_x, y=fma_y, name="FMA", line=go.scatter.Line(color="blue")))
    figure.add_trace(go.Scatter(x=sma_x, y=sma_y, name="SMA", line=go.scatter.Line(color="purple")))

    for transaction in all_transactions:
        if transaction.pair != p:
            continue

        print(f"{transaction.pair}: {transaction.operation} at {transaction.timestamp} (note: {transaction.notes})")
        figure.add_vline(
            x=transaction.timestamp.timestamp() * 1000,
            line_width=1,
            line_color="black",
            annotation_text=f"{transaction.operation.value}<br>{transaction.timestamp.strftime("%H:%M:%S")}",
            annotation_align="left",
        )

    figure.show()



async def main():
    provider: CryptoProvider

    provider = CCXTProvider(apikey=API_KEY, secret=API_SECRET)
    timer = IntervalTimer(
        provider=provider,
        pairs=PAIRS,
        timeframe_minutes=TIMEFRAME_MINUTES,
    )
    strategy = AverageCrossover(
        provider=provider,
        pairs=PAIRS,
        sma_window=50,
        fma_window=10,
        timeframe_minutes=TIMEFRAME_MINUTES,
        jitter=0.001,
    )

    async for frame in timer:
        transactions, logs, function_plots = await strategy.execute(frame)
        for transaction in transactions:
            print(transaction)

# async def fetch_market_data():
#     dotenv.load_dotenv()

#     binance_api_key = os.getenv("BINANCE_API_KEY")
#     binance_api_secret = os.getenv("BINANCE_API_SECRET")

#     PAIRS: List[Pair] = [
#         Pair("BTC", "USDT"),
#         Pair("BTC", "USDC"),
#         Pair("BTC", "USDC"),
#         Pair("ETH", "USDT"),
#         Pair("ETH", "USDC"),
#         Pair("BNB", "USDT"),
#         Pair("ADA", "USDT"),
#         Pair("SOL", "USDT"),
#         Pair("XRP", "USDT"),
#     ]

#     provider = CryptoExchangeProvider(
#         apikey=binance_api_key,
#         secret=binance_api_secret,
#     )
#     timer = IntervalTimer(
#         provider=provider,
#         pairs=PAIRS,
#         timeframe_minutes=60,
#     )
#     strategy = AverageCrossover(IntervalTimer(provider=provider, PAIRS, 60), provider)
#     await strategy.start()

#     await provider._exchange.close()


if __name__ == "__main__":
    asyncio.run(backtest())
    # asyncio.run(import_from_file())
    # asyncio.run(fetch_data())