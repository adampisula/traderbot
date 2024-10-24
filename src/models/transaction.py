from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional
from datetime import datetime

from models.symbol import Symbol

class OperationEnum(Enum):
    BUY = "BUY"
    SELL = "SELL"
    SKIP = "SKIP"

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        return False


class Transaction(BaseModel):
    timestamp: datetime
    operation: OperationEnum
    symbol: Symbol 
    notes: Optional[str] = None
