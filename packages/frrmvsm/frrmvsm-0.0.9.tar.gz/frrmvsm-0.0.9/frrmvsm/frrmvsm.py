import sys 
from frrmvsm import *

def operations(a,b):

    my_sum = add.add(a,b)
    my_subtraction = subtract.subtract(a,b)
    my_multiplication = multiply.multiply(a,b)
    my_division = divide.divide(a,b)

    print(f"My sum is {my_sum}")
    print(f"My subtraction is {my_subtraction}")
    print(f"My multiplication is {my_multiplication}")
    print(f"My division is {my_division}")

def main(argv=sys.argv):
    a = int(argv[1])
    b = int(argv[2])
    operations(a,b)

if __name__ == '__main__':
    main()
    