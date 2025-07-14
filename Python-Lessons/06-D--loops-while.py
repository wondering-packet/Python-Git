# while loop keeps executing until the condition becomes False or break is encountered.

# @@@---Option 1---@@@
# exiting using conditon statement:

command = ""
while command != "quit" and command != "QUIT":
    command = input(">")
    print("echo", command)

# @@@---Option 2---@@@
# exiting using break statement; produces a cleaner code:

while True:
    command = input(">>")
    # is able handle mixed case, uppercase & lowercase; command is a string character so you can use string functions.
    if command.lower() == "quit":
        # break is another way to end a While loop.
        break
    print(command)
