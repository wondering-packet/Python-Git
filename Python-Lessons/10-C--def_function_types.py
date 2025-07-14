"""
there are 2 types of functions:
1 - that perform a task.
2 - that returns a value.
"""

### @@@- type 1 -@@@ ###


def greet(name):
    # performing a task. doesn't allow reusing the value.
    print("hello ", name)


greet("VG")
print("all functions by default return \"None\" if nothing is returned: ", greet("VG"))

### @@@- type 2 -@@@ ###


def greet(name):
    # returns a value instead of a fixed output like the print statement.
    return f"hello {name}"


# here we are storing the returned value in a string; we could have used it in many other ways since the value is a reusable piece of info
# that can be processed in other ways; the above type (performing a task) returns a fixed output - makes it rigid; can't reuse.
message = "Welcome to Python, " + greet("VG")
print(message)
