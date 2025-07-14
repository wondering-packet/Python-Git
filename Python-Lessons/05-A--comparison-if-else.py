# @@@@ - 1st example - @@@@

temp = 5

# notice the indentation; ver important in python; pep8 recommends 4 whitespaces.
if temp > 30:                       # end it with a colon :.
    print("it's warm")
elif temp > 20:                     # else if; another if statement; optional.
    print("it's nice out")
# when nothing matches execute this statement; optional.
else:
    print("it's COLD")
print("have a nice day (or not)")   # outside the if/else block.

# @@@@ - 2nd example - @@@@
print("\n")
age = 20

if age >= 18:
    print("Eligible")
else:
    print("Not eligible")

# alternative

if age >= 18:
    message = "Eligible"
else:
    message = "Not eligible"
print(message)

# @@@@ - 3rd example - @@@@
# best version using ternary operator

message = "Eligible" if age >= 18 else "Not eligible"
print(message)

# @@@@ - 4th example - @@@@
# chaining operators:
age = 38
if 18 <= age < 28:
    print(f"Eligible_boy {age}")
elif 50 >= age > 28:
    print(f"Eligible_man {age}")
elif 50 <= age < 65:
    print(f"Eligible_old_man {age}")
else:
    print("error")
