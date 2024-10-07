from typing import Dict


class Wallet:
    def __init__(self):
        pass

    async def get_balance(self, symbol: str) -> float:
        return 0

    async def get_all(self) -> Dict[str, float]:
        return {}
