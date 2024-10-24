from datetime import datetime
from typing import List, Optional

from models.market import Market, MarketFrame
from models.symbol import Pair
from providers.provider import Provider


class MockCryptoProvider(Provider):
    _market: Market
    _index: int

    def __init__(self, market: Market, starting_index=100):
        self._market = market
        self._index = starting_index

    def tick(self):
        self._index += 1

    async def __get_market_frame(self, pairs: List[Pair], index: int) -> MarketFrame:
        frame_mf_of = self._market._frames[index]
        mf = frame_mf_of[0] if isinstance(frame_mf_of, tuple) else frame_mf_of
        return mf

    async def get_current(
        self,
        symbols: List[Pair]=[],  # unused
        timeframe_minutes: int=1,
    ) -> MarketFrame:
        mf = await self.__get_market_frame(symbols, self._index)
        return mf

    async def get_history(
        self,
        symbols: List[Pair]=[],
        # use this (count)
        count: Optional[int]=None,
        # do NOT use these (since+until)
        since: Optional[datetime]=None,
        until: Optional[datetime]=None,
        timeframe_minutes: int=1,
    ) -> Market:
        if count is None:
            raise Exception("count is required for MockCryptoProvider.get_history")
        
        if since or until:
            raise NotImplementedError("since and until are not supported for MockCryptoProvider.get_history")
        
        return Market(frames=self._market._frames[-1*count:])
