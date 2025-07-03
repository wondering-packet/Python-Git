# input() function is used to take input from the user. input is always returned as a string.

x = input("x: ")
# y = x + 1           # returns error because x is a string.

print(type(x))        # lists the type.

y = int(x)+1            # type conversion to int.
print(f"x: {x}, y: {y}")

# you can also use:
# str()
# flot()

# bool() is special. It returns output based on truthy & falsy.
# false values are:
# ""
# 0
# None
# everything else is true.

print(bool(0))
print(bool(""))
print(bool(None))
print(bool("False"))
print(bool(10))
