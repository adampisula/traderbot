from typing import List, Optional
import ccxt.async_support as ccxt
from datetime import datetime, timedelta

from models.market import Market, MarketFrame, OHLCV
from models.pair import Pair
from providers.crypto import CryptoProvider


class CCXTProvider(CryptoProvider):
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
        self,
        pairs: List[Pair],
        # use this (count)
        count: Optional[int]=None,
        # or this (since+until)
        since: Optional[datetime]=None,
        until: Optional[datetime]=None,
        timeframe_minutes=1
    ) -> Market:
        ALLOWED_TIMEFRAMES = {
            1: '1m',
            3: '3m',
            5: '5m',
            15: '15m',
            30: '30m',
            60: '1h',
            120: '2h',
            240: '4h',
            360: '6h',
            480: '8h',
            720: '12h',
        }

        timeframe_str = ALLOWED_TIMEFRAMES.get(timeframe_minutes)
        if not timeframe_str:
            raise Exception("Invalid timeframe - see ALLOWED_TIMEFRAMES")

        if since and until:
            count = int((until - since).total_seconds() // (timeframe_minutes * 60))
            print(count)
        elif count:
            since = datetime.now() - timedelta(minutes=(count+1)*timeframe_minutes)  # Fetch one more than needed
            until = datetime.now() - timedelta(minutes=timeframe_minutes)  # Don't include the current frame
        else:
            raise Exception("Invalid arguments")

        limit = count + 1 

        market_frames = [
            MarketFrame(
                timestamp=-1,
                ohlcv={},
            )
            for _ in range(count)
        ]

        await self._exchange.load_markets()
        for pair in pairs:
            ohlcv = await self._exchange.fetch_ohlcv(
                str(pair),
                timeframe_str,
                int(since.timestamp() * 1000),
                limit,
                params={
                    "until": int(until.timestamp() * 1000),
                    "paginate": True,
                },
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
