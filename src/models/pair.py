class Pair:
    a: str
    b: str

    def __init__(self, a: str, b: str) -> None:
        self.a = a
        self.b = b
    
    def __str__(self):
        return f"{self.a}/{self.b}"