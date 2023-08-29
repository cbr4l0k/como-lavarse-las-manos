from ALU import ALU


class Calculator:
    def __init__(self) -> None:
        self.alu: ALU = ALU()
        self.operator: bool = False

    def menu(self) -> None:
        finished: bool = False
        while 1:
            if self.operator:
                self.operator = False
                finished = self.alu.process_operator()
                if finished:
                    break
            else:
                self.operator = True
                self.alu.process_operand()

    def main(self) -> None:
        self.menu()


if __name__ == '__main__':
    calc = Calculator()
    calc.main()
