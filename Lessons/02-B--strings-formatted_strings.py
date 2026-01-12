first_name = "Akashi"
last_name = "Seijuro"

# concatenating strings:
full_name = first_name + " " + last_name
print(full_name)

# using formatted strings. this is preferred way to do concatenation.
# use f"{exp1}{exp2}...{expn}" for the syntax; expressions can be added using {}.
# final expression is evaluated during runtime so whatever you put in all the {} expressions is returned.
# notice the space b/w two {} is returned in the output.
print(f"{first_name} {last_name}")

# directly adding string
print(f"hello, {first_name} {last_name}")

# adding more functions in the {} expression
print(f"{len(first_name)} {last_name[:3]}")

# directly adding integer
print(f"{first_name + " " + last_name} {100+100}")
