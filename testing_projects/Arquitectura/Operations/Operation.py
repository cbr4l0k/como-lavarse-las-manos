from abc import ABC, abstractmethod, abstractstaticmethod


class Operation(ABC):
    def __init__(self, a: float, b: float) -> None:
        self.a = a
        self.b = b

    @abstractmethod
    def calculate(self):
        pass
