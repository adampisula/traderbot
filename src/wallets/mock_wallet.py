from typing import Dict

from wallets.wallet import Wallet


class MockWallet(Wallet):
    balances: Dict[str, float] = {}

    def __init__(self):
        self.balances = {}

    async def get_balance(self, symbol: str) -> float:
        return 1000

    async def get_all(self) -> Dict[str, float]:
        return self.balances
