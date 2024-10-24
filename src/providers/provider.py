from typing import Protocol, List, Optional
from datetime import datetime

from models.symbol import T, Symbol
from models.market import MarketFrame, Market

class Provider(Protocol):
    async def get_current(self, symbols: List[Symbol], timeframe_minutes: int) -> MarketFrame:
        raise NotImplemented

    async def get_history(
        self,
        symbols: List[Symbol],
        # use this (count)
        count: Optional[int]=None,
        # or this (since+until)
        since: Optional[datetime]=None,
        until: Optional[datetime]=None,
        timeframe_minutes=1
    ) -> Market:
        raise NotImplemented