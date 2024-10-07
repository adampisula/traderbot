from typing import Protocol, List, Optional
from datetime import datetime

from models.pair import Pair
from models.market import MarketFrame, Market

class CryptoProvider(Protocol):
    async def get_current(self, pairs: List[Pair], timeframe_minutes: int) -> MarketFrame:
        raise NotImplemented

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
        raise NotImplemented