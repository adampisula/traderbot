from typing import AsyncIterator, Protocol, List
import asyncio

from models.market_frame import MarketFrame
from models.transaction import Transaction


class Strategy(Protocol):
    def __init__(self, timer: AsyncIterator[MarketFrame]):
        pass

    async def execute(self, frame: MarketFrame) -> List[Transaction]:
        await asyncio.sleep(5)
        return []
