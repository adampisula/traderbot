class Pair:
    a: str
    b: str

    def __init__(self, a: str, b: str) -> None:
        self.a = a
        self.b = b
    
    def __str__(self):
        return f"{self.a}/{self.b}"
    
    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __hash__(self):
        return hash(self.__str__())