from typing import List, Tuple, Dict
from datetime import datetime

from providers.provider import Provider
from strategies.strategy import Strategy
from models.market import FunctionPlot, Log, Market, MarketFrame, OHLCV, OutputFrame
from models.symbol import Symbol
from models.transaction import OperationEnum, Transaction
from providers.ccxt import CCXTProvider


class AverageCrossover(Strategy):
    _history: Market = Market(frames=[])

    _provider: Provider
    _symbols: List[Symbol] = []
    _sma_window: int
    _fma_window: int
    _timeframe_minutes: int
    _jitter: float
    _transaction_cost: float

    _holding: Dict[Symbol, bool] = {}

    def __init__(
        self,
        provider: Provider,
        symbols: List[Symbol],
        sma_window=50,
        fma_window=10,
        timeframe_minutes=1,
        jitter=0.005,
        transaction_cost=0.00075,
    ):
        self._provider = provider
        self._symbols = symbols
        self._sma_window = sma_window
        self._fma_window = fma_window
        self._timeframe_minutes = timeframe_minutes
        self._jitter = jitter
        self._transaction_cost = transaction_cost

    def __calculate_fma(self, values: List[Tuple[datetime, OHLCV]]) -> float:
        ohlcv = [v[1] for v in values]

        fma_closes = [x.close for x in ohlcv][-1*self._fma_window:]
        return sum(fma_closes) / len(fma_closes)

    def __calculate_sma(self, values: List[Tuple[datetime, OHLCV]]) -> float:
        ohlcv = [v[1] for v in values]

        sma_closes = [x.close for x in ohlcv][-1*self._sma_window:]
        return sum(sma_closes) / len(sma_closes)

    # returns (Transactions, Logs, Function plots)
    async def execute(self, frame: MarketFrame) -> OutputFrame:
        transactions: List[Transaction] = []
        logs: List[Log] = []
        function_plots: List[FunctionPlot] = []

        if len(self._history._frames) < self._sma_window:
            print("Getting history")
            self._history = await self._provider.get_history(
                symbols=self._symbols,
                count=self._sma_window,
                timeframe_minutes=self._timeframe_minutes,
            )


        for pair in self._symbols:
            history_ohclv = self._history.get_all_symbol_data(pair)
            timestamp, current_ohclv = frame.get_symbol(pair)

            fma = self.__calculate_fma(
                values=history_ohclv+[(timestamp, current_ohclv)],
            )
            sma = self.__calculate_sma(
                values=history_ohclv+[(timestamp, current_ohclv)],
            )

            function_plots.append(FunctionPlot(
                timestamp=timestamp,
                label=f"{pair} FMA",
                value=fma,
                color="blue",
            ))
            function_plots.append(FunctionPlot(
                timestamp=timestamp,
                label=f"{pair} SMA",
                value=sma,
                color="purple",
            ))

            buy_threshold = sma * (1 + self._transaction_cost + self._jitter)
            # buy_threshold = sma 
            sell_threshold = fma * (1 + self._transaction_cost + self._jitter)
            # sell_threshold = fma

            is_holding = self._holding.get(pair, False)

            if fma > buy_threshold and not is_holding:
                transactions.append(
                    Transaction(
                        timestamp=timestamp,
                        symbol=pair,
                        operation=OperationEnum.BUY,
                        # notes=f"{fma} > {buy_threshold}",
                    )
                )
                self._holding[pair] = True
            elif sma > sell_threshold and is_holding:
                transactions.append(
                    Transaction(
                        timestamp=timestamp,
                        symbol=pair,
                        operation=OperationEnum.SELL,
                        # notes=f"{sell_threshold} < {sma}",
                    )
                )
                self._holding[pair] = False

        self._history._frames = self._history._frames[-1*(self._sma_window-1):] + [frame]

        return OutputFrame(
            timestamp=frame.timestamp,
            logs=logs,
            transactions=transactions,
            function_plots=function_plots,
        )
