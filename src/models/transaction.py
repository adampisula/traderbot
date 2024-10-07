from pydantic import BaseModel
from enum import Enum
from typing import Optional


class OperationEnum(Enum):
    BUY = "BUY"
    SELL = "SELL"
    SKIP = "SKIP"


class Transaction(BaseModel):
    operation: OperationEnum
    amount: float
    code: str
    notes: Optional[str] = None
