import sys 

#from add import add
#from subtract import subtract
#from multiply import multiply
#from divide import divide

a = int(sys.argv[1])
b = int(sys.argv[2])

def add(a,b):
    return a + b 

def subtract(a,b):
    return a - b 

def multiply(a,b):
    return a * b 

def divide(a,b):
    return a / b 

def operations(a,b):

    my_sum = add(a,b)
    my_subtraction = subtract(a,b)
    my_multiplication = multiply(a,b)
    my_division = divide(a,b)

    print(f"My sum is {my_sum}")
    print(f"My subtraction is {my_subtraction}")
    print(f"My multiplication is {my_multiplication}")
    print(f"My division is {my_division}")

if __name__ == '__main__':
    operations(a,b)