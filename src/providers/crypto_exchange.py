from typing import List, Tuple
import ccxt.async_support as ccxt
from datetime import datetime, timedelta

from models.market import Market
from models.market_frame import MarketFrame, OHLCV
from models.pair import Pair


class CryptoExchangeProvider:
    def __init__(self, apikey: str, secret: str, verbose=False):
        self._exchange = ccxt.binance(
            {
                "apiKey": apikey,
                "secret": secret,
                "verbose": verbose,
            }
        )

    async def get_current(
        self, pairs: List[Pair], timeframe_minutes=1
    ) -> MarketFrame:
        await self._exchange.load_markets()

        timeframe_str = f"{timeframe_minutes}m"
        since = datetime.now() - timedelta(minutes=timeframe_minutes)
        limit = 1

        market_frame = MarketFrame(
            timestamp=-1,
            ohlcv={},
        )

        for pair in pairs:
            ohlcv = await self._exchange.fetch_ohlcv(
                str(pair),
                timeframe_str,
                int(since.timestamp() * 1000),
                limit,
            )

            if len(ohlcv) != 1:
                raise Exception(
                    f"Incorrect amount of data points: {len(ohlcv)} for {pair}"
                )

            market_frame.timestamp = ohlcv[0][0]

            # Array<Array<int>> -> A list of candles ordered as timestamp, open, high, low, close, volume
            market_frame.ohlcv[str(pair)] = OHLCV(
                open=ohlcv[0][1],
                high=ohlcv[0][2],
                low=ohlcv[0][3],
                close=ohlcv[0][4],
                volume=ohlcv[0][5],
            )

        return market_frame

    async def get_history(
        self, pairs: List[Pair], count: int, timeframe_minutes=1
    ) -> Market:
        await self._exchange.load_markets()

        timeframe_str = f"{timeframe_minutes}m"
        since = datetime.now() - timedelta(minutes=(count + 1) * timeframe_minutes)
        limit = count + 1

        market_frames = [
            MarketFrame(
                timestamp=-1,
                ohlcv={},
            )
            for _ in range(count)
        ]

        for pair in pairs:
            ohlcv = await self._exchange.fetch_ohlcv(
                str(pair),
                timeframe_str,
                int(since.timestamp() * 1000),
                limit,
            )

            if len(ohlcv) != limit:
                raise Exception("Not enough data points")

            for i in range(count):
                market_frames[i].timestamp = ohlcv[i][0]

                # Array<Array<int>> -> A list of candles ordered as timestamp, open, high, low, close, volume
                market_frames[i].ohlcv[str(pair)] = OHLCV(
                    open=ohlcv[i][1],
                    high=ohlcv[i][2],
                    low=ohlcv[i][3],
                    close=ohlcv[i][4],
                    volume=ohlcv[i][5],
                )

        return Market(frames=market_frames)

    def get_ticker(self, symbol):
        return self._exchange.fetch_ticker(symbol)
