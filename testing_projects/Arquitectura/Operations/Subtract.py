from Operation import Operation


class Subtract(Operation):
    def __init__(self, a: float, b: float) -> None:
        super().__init__(a, b)

    def calculate(self):
        return self.a - self.b
