from .add import add
from .sub import sub

import argparse


def perform_operation(opr, num1, num2):
    if opr == 'add':
        result = add(num1, num2)
        print(result)
    elif opr == 'sub':
        result = sub(num1, num2)
        print(result)
    else:
        print("Invalid operation. Use 'add' or 'sub'.")


def main():
    parser = argparse.ArgumentParser(description="Sample math library containing add and sub functions")
    parser.add_argument("opr", choices=['add', 'sub'], help="Operation to perform: 'add' or 'sub'")
    parser.add_argument("num1", type=int, help="First number")
    parser.add_argument("num2", type=int, help="Second number")

    args = parser.parse_args()
    perform_operation(args.opr, args.num1, args.num2)


if __name__ == "__main__":
    main()
