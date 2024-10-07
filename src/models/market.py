from pydantic import BaseModel
from typing import List, Tuple, Dict 

from models.pair import Pair


class OHLCV(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float


class MarketFrame(BaseModel):
    timestamp: int
    ohlcv: Dict[str, OHLCV]

    def get_pair(self, symbol: str) -> Tuple[int, OHLCV]:
        return self.timestamp, self.ohlcv[symbol]

    def __str__(self):
        list_ohlcv = [
            f"{pair[0]}/{pair[1]}: {ohlcv}" for pair, ohlcv in self.ohlcv.items()
        ]
        list_str = "\n".join(list_ohlcv)

        return str(self.timestamp) + ":\n" + list_str


class Market(BaseModel):
    frames: List[MarketFrame]

    def get_all_for_pair(self, pair: Pair) -> List[Tuple[int, OHLCV]]:
        return [frame.get_pair() for frame in self.frames]

    def save_to_file(self, filename: str) -> None:

