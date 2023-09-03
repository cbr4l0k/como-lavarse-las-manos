import numpy as np 
import  pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
import json
import re
import string

from Operations.Sum import Sum
from Operations.Subtract import Subtract
from Operations.Multiply import Multiply
from Operations.Divide import Divide
from Operations.Power import Power
from Operations.IntDivide import IntDivide
from Puta.mierda import PutaMierda


class ALU:  # Arithmetic Logic Unit
    def __init__(self) -> None:

        self.operations = {
            '+': lambda a, b: Sum(a, b).calculate(),
            '-': lambda a, b: Subtract(a, b).calculate(),
            '*': lambda a, b: Multiply(a, b).calculate(),
            '/': lambda a, b: Divide(a, b).calculate(),
            '**': lambda a, b: Power(a, b).calculate(),
            '//': lambda a, b: IntDivide(a, b).calculate(),
        }
        self.curr_operator: str = None
        self.curr_input: str = None
        self.curr_result: float = 0
        self.finished: bool = False
        self.a: float = None
        self.b: float = None

    def calculate(self, a: float, b: float, op: str) -> float:
        return self.operations[op](a, b)

    def process_operand(self) -> None:
        while 1:
            self.curr_input = input("Insert an operand: ")
            if not self.curr_input.isnumeric() and not self.curr_input[1:].isnumeric() and self.curr_input[0] != "-":
                print("Invalid operand")
            else:
                if self.a is None:
                    self.a = float(self.curr_input)
                else:
                    self.b = float(self.curr_input)
                    self.curr_result = self.calculate(self.a, self.b, self.curr_operator)
                    self.a = self.curr_result
                break

    def process_operator(self) -> bool:
        while 1:
            self.curr_input = input("Insert an operator (+,-,*,/,**,//,=): ")
            if self.curr_input == "=":
                print(self.curr_result)
                self.finished = True
                break
            if self.curr_input not in ["+", "-", "*", "/", "**", "//"]:
                print("Invalid operator")
            else:
                self.curr_operator = self.curr_input
                break
        return self.finished
