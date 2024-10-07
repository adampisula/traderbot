from typing import List, Tuple, Dict
from datetime import datetime

from strategies.strategy import Strategy
from models.market import Market, MarketFrame, OHLCV
from models.pair import Pair
from models.transaction import OperationEnum, Transaction
from providers.ccxt import CCXTProvider


class AverageCrossover(Strategy):
    _history: Market = Market(frames=[])

    _provider: CCXTProvider
    _pairs: List[Pair] = []
    _sma_window: int
    _fma_window: int
    _timeframe_minutes: int
    _jitter: float
    _transaction_cost: float

    _holding: Dict[Pair, bool] = {}

    def __init__(
        self,
        provider: CCXTProvider,
        pairs: List[Pair],
        sma_window=50,
        fma_window=10,
        timeframe_minutes=1,
        jitter=0.005,
        transaction_cost=0.00075,
    ):
        self._provider = provider
        self._pairs = pairs
        self._sma_window = sma_window
        self._fma_window = fma_window
        self._timeframe_minutes = timeframe_minutes
        self._jitter = jitter
        self._transaction_cost = transaction_cost

    def __calculate_fma(self, values: List[Tuple[int, OHLCV]]) -> float:
        ohlcv = [v[1] for v in values]

        fma_closes = [x.close for x in ohlcv][-1*self._fma_window:]
        return sum(fma_closes) / len(fma_closes)

    def __calculate_sma(self, values: List[Tuple[int, OHLCV]]) -> float:
        ohlcv = [v[1] for v in values]

        sma_closes = [x.close for x in ohlcv][-1*self._sma_window:]
        return sum(sma_closes) / len(sma_closes)

    # returns (Transactions, Logs, Function plots)
    async def execute(self, frame: MarketFrame) -> Tuple[List[Transaction], Tuple[datetime, str], List[Tuple[datetime, str, float]]]:
        transactions: List[Transaction] = []
        logs: List[Tuple[datetime, str]] = []
        function_plots: List[Tuple[datetime, str, float]] = []

        if len(self._history.frames) < self._sma_window:
            print("Getting history")
            self._history = await self._provider.get_history(
                pairs=self._pairs,
                count=self._sma_window,
                timeframe_minutes=self._timeframe_minutes,
            )


        for pair in self._pairs:
            history_ohclv = self._history.get_all_for_pair(pair)
            timestamp, current_ohclv = frame.get_pair(pair)

            fma = self.__calculate_fma(
                values=history_ohclv+[(timestamp, current_ohclv)],
            )
            sma = self.__calculate_sma(
                values=history_ohclv+[(timestamp, current_ohclv)],
            )

            function_plots.append((timestamp, f"{pair} FMA", fma))
            function_plots.append((timestamp, f"{pair} SMA", sma))

            buy_threshold = sma * (1 + self._transaction_cost + self._jitter)
            # buy_threshold = sma 
            sell_threshold = fma * (1 + self._transaction_cost + self._jitter)
            # sell_threshold = fma


            is_holding = self._holding.get(pair, False)

            if fma > buy_threshold and not is_holding:
                transactions.append(
                    Transaction(
                        timestamp=timestamp,
                        pair=pair,
                        operation=OperationEnum.BUY,
                        notes=f"{fma} > {buy_threshold}",
                    )
                )
                self._holding[pair] = True
            elif sma > sell_threshold and is_holding:
                transactions.append(
                    Transaction(
                        timestamp=timestamp,
                        pair=pair,
                        operation=OperationEnum.SELL,
                        notes=f"{sell_threshold} < {sma}",
                    )
                )
                self._holding[pair] = False

        self._history.frames = self._history.frames[-1*(self._sma_window-1):] + [frame]

        return transactions, logs, function_plots
