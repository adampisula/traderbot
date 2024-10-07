from datetime import datetime, timedelta
from typing import List, Tuple

from providers.mock_crypto import MockCryptoProvider
from models.market import MarketFrame, Market


class BacktestTimer:
    _index: int 

    def __init__(
        self,
        provider: MockCryptoProvider,
        market: Market,
        starting_index=100,
    ):
        self._provider = provider
        self._index = starting_index
        self._market = market

    def __aiter__(self):
        return self

    def tick(self):
        self._index += 1

    async def __anext__(self) -> MarketFrame:
        try:
            if self._index == len(self._market.frames):
                raise StopIteration

            # return await self._provider.get_current()
            return self._market.frames[self._index]
        except StopIteration:
            raise StopAsyncIteration from None
