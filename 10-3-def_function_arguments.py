# @@@-- a simple function:
def increment(number, by):
    return number+by


# the value of increment() function is temprorily stored in a variable which is used by print().
print(increment(2, 3))

# @@@-- a function which takes in keyword arguments:


def increment(number, by):
    return number+by


# here we are explicity naming the parameters in the argument to help the readability of the code.
# makes it easier to understand what kind of a parameter this argument value will go into.
# this is purely for improving the readabilty of the code.
print(increment(2, by=4))

# @@@-- a function which has a default argument:


# a defualt argument value for "by"; this is an optional parameter.
def increment(number, by=10):
    # note: all optiional parameters must come after all required paramerters. e.g.:
    # def increment (number, by=10, number_2)
    # will not work since number_2 is a required parameter while by=10 is an optional parameter.
    # fix:
    # def increment (number, number_2, by=10)
    return number+by


# if nothing is passed for "by" then the default value takes place.
print(increment(2))
# override the default by explicity passing on an argument.
print(increment(2, 3))
