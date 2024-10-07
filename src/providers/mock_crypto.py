from typing import List, Optional

from models.market import Market, MarketFrame
from models.pair import Pair
from providers.crypto import CryptoProvider


class MockCryptoProvider(CryptoProvider):
    _market: Market
    _index: int

    def __init__(self, market: Market, starting_index=100):
        self._market = market
        self._index = starting_index

    def tick(self):
        self._index += 1

    async def get_current(
        self, pairs: List[Pair]
    ) -> MarketFrame:
        return self._market.frames[self._index]

    async def get_history(
        self,
        pairs: List[Pair],
        # use this (count)
        count: Optional[int]=None,
        timeframe_minutes=1
    ) -> Market:
        return Market(frames=self._market.frames[-1*count:])
