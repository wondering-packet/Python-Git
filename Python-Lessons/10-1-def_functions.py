# a basic function:
def greet():
    print("Hello stranger !!")
# pep8 recommends 2 line breaks after a function ends


greet()


# function that takes arguments:
# first_name & last_name are parameters; used to take input.
def greet(first_name, last_name):
    print(f"Hello {first_name} {last_name} !!")


your_first_name = input("please type your first name: ")
your_last_name = input("please type your last name: ")
# your_first_name & your_last_name are arguments; these are actual values that the parameters take.
greet(your_first_name, your_last_name)
