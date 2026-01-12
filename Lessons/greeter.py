def greet(name):
    print(f"Hello {name} !!")


# below block is generally added to modules.
# it means, if you are running this python file directly then the code under "if" block executes.
# if you are calling this python file as a module in another file then the code doesn't execute.
if __name__ == "__main__":
    greet("Learner")


# note: i ran into issues when i had the module name contain hyphens.
