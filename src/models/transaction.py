from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import Optional
from datetime import datetime

from models.pair import Pair

class OperationEnum(Enum):
    BUY = "BUY"
    SELL = "SELL"
    SKIP = "SKIP"


class Transaction(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    timestamp: datetime
    operation: OperationEnum
    pair: Pair 
    notes: Optional[str] = None
