from typing import AsyncIterator, Protocol

from models.market import MarketFrame, OutputFrame


class Strategy(Protocol):
    def __init__(self, timer: AsyncIterator[MarketFrame]):
        raise NotImplementedError

    async def execute(self, frame: MarketFrame) -> OutputFrame:
        raise NotImplementedError