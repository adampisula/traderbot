from typing import List, AsyncIterator

from strategies.strategy import Strategy
from models.market_frame import MarketFrame
from models.market import Market
from models.transaction import OperationEnum, Transaction
from providers.crypto_exchange import CryptoExchangeProvider


class AverageCrossover(Strategy):
    _past_window: Market = Market(frames=[])
    _PAST_WINDOW_SIZE = 100
    _provider: CryptoExchangeProvider

    _PAIRS = [
        ("BTC", "USDT"),
        ("BTC", "USDC"),
        # ("BTC", "BUSD"),
        ("BTC", "USDC"),
        ("ETH", "USDT"),
        ("ETH", "USDC"),
        # ("ETH", "BUSD"),
        ("BNB", "USDT"),
        ("ADA", "USDT"),
        ("SOL", "USDT"),
        ("XRP", "USDT"),
    ]

    def __init__(
        self,
        timer: AsyncIterator[MarketFrame],
        provider: CryptoExchangeProvider,
        pairs: List[]
    ):
        self.timer = timer
        self._provider = provider

    async def start(self):
        async for frame in self.timer:
            transactions = await self.execute(frame)
            for transaction in transactions:
                print(transaction)

    async def execute(self, frame: MarketFrame) -> List[Transaction]:
        if len(self._past_window.frames) < self._PAST_WINDOW_SIZE:
            self._past_window = await self._provider.get_history(
                self._PAIRS, self._PAST_WINDOW_SIZE, 1
            )

        transaction_list: List[Transaction] = []

        for pair in self._PAIRS:
            # implement get_history in Market, then fetch last N frames for FMA and SMA

            fma_closes = [x.close for x in ohclv][self._PAST_WINDOW_SIZE - 9 :]
            fma_closes = fma_closes + [frame.get_pair(f"{pair[0]}/{pair[1]}")[1].close]
            fma_closes_mean = sum(fma_closes) / len(fma_closes)

            sma_closes = [x.close for x in ohclv][self._PAST_WINDOW_SIZE - 49 :]
            sma_closes = sma_closes + [frame.get_pair(f"{pair[0]}/{pair[1]}")[1].close]
            sma_closes_mean = sum(sma_closes) / len(sma_closes)

            transaction_cost = 0.00075
            jitter = 0.005

            if fma_closes_mean > sma_closes_mean * (1 + transaction_cost + jitter):
                transaction_list.append(
                    Transaction(
                        code=f"{pair[0]}/{pair[1]}",
                        operation=OperationEnum.BUY,
                        amount=1,
                        notes=f"Comparing {fma_closes_mean} and {sma_closes_mean} + {sma_closes_mean * transaction_cost}",
                    )
                )
            elif fma_closes_mean * (1 + transaction_cost + jitter) < sma_closes_mean:
                transaction_list.append(
                    Transaction(
                        code=f"{pair[0]}/{pair[1]}",
                        operation=OperationEnum.SELL,
                        amount=1,
                        notes=f"Comparing {fma_closes_mean} and {sma_closes_mean} + {sma_closes_mean * transaction_cost}",
                    )
                )
            else:
                print(f"skipped {pair}")

        return transaction_list
