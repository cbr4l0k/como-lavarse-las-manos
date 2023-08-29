from Operation import Operation


class IntDivide(Operation):
    def __init__(self, a: float, b: float) -> None:
        super().__init__(a, b)

    def calculate(self) -> float:
        if self.b == 0:
            raise ValueError("Can't divide by 0")
        return self.a // self.b
