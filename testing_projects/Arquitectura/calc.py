def calc_unit(a, b, op):
    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x / y,
        '**': lambda x, y: x ** y,
        '//': lambda x, y: x // y,
    }
    return operations[op](a, b)


def menu():
    operator = False
    curr_result = 0
    a = None
    b = None
    while 1:
        if operator:
            operator = False
            while 1:

                curr_input = input("Insert an operator (+,-,*,/,**,//,=): ")
                if curr_input == "=":
                    print(curr_result)
                    return
                if curr_input not in ["+", "-", "*", "/", "**", "//"]:
                    print("Invalid operator")
                else:
                    curr_operator = curr_input
                    break
        else:
            operator = True
            while 1:
                curr_input = input("Insert an operand: ")
                if not curr_input.isnumeric() and not curr_input[1:].isnumeric() and curr_input[0] != "-":
                    print("Invalid operand")
                else:
                    if a is None:
                        a = float(curr_input)
                    else:
                        b = float(curr_input)
                        curr_result = calc_unit(a, b, curr_operator)
                        a = curr_result
                    break

def main():
    menu()

if __name__ == '__main__':
    main()