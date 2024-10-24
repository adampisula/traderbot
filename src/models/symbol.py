from typing import Protocol, TypeVar

from pydantic import BaseModel


class Symbol(BaseModel):
    def __str__(self) -> str:
        raise NotImplementedError
    
    def __eq__(self, other) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.__str__())

T = TypeVar("T", bound=Symbol)

class Pair(Symbol):
    a: str
    b: str

    # def __init__(self, a: str, b: str) -> None:
    #     self.a = a
    #     self.b = b
    
    def __str__(self):
        return f"{self.a}/{self.b}"

    def __eq__(self, other) -> bool:
        return self.a == other.a and self.b == other.b
    
    def __hash__(self) -> int:
        return hash(self.__str__())


class Ticker(Symbol):
    code: str

    def __init__(self, code: str) -> None:
        self.code = code
    
    def __str__(self):
        return self.code
    
    def __eq__(self, other) -> bool:
        return self.code == other.code
