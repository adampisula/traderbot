from datetime import datetime, timedelta
import asyncio
from typing import List, Tuple

from models.symbol import Symbol
from providers.ccxt import CCXTProvider
from models.market import MarketFrame


class IntervalTimer:
    last_run: datetime | None = None
    _symbols: List[Symbol]

    def __init__(
        self,
        provider: CCXTProvider,
        symbols: List[Symbol],
        timeframe_minutes=1,
    ):
        self._timeframe_minutes = timeframe_minutes
        self._provider = provider
        self._symbols = symbols

    def __aiter__(self):
        return self

    async def __anext__(self) -> MarketFrame:
        try:
            if self.last_run is None:
                self.last_run = datetime.now()
            else:
                next_run = self.last_run + timedelta(minutes=self._timeframe_minutes)
                while next_run > datetime.now():
                    await asyncio.sleep(1)

            frame = await self._provider.get_current(
                self._symbols, timeframe_minutes=self._timeframe_minutes
            )
            self.last_run = datetime.now()

            return frame
        except StopIteration:
            raise StopAsyncIteration from None
