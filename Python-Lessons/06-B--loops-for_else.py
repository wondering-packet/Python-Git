"""
for else loop; the idea is execute the "else" loop only if the "for" loop terminates normally.
e.g. an attempt to send 3 messages, under the "for" loop we can implement the logic to send
these 3 messages, if successful then apply a "break" statement which ends the "for" loop.
if all 3 failed, then let the "for" end normally which lets the "else" execute. "else"
will not execute if the "for" loop ends abruptly (i.e. using "break")
"""

print("\n@@@@@@@@--Example 1--@@@@@@@@\n")
# boolean value that can be used in If statement.
successful = False
for number in range(3):
    print("Attempt", number+1)
    if successful:                      # only executes if successful = True
        print("Successful")
        break                           # breaks out for the "for" loop; break stops the parent loop
# "else" will only execute if for the above "for" loop terminates normally (no break).
# "else" executes.
else:
    print("Attempted 3 times, Failed")

print("\n@@@@@@@@--Example 2--@@@@@@@@\n")
for number in range(3):
    print("Attempt", number+1)
    if number == 2:
        successful = True
    if successful:
        print("Successful")
        break
# "else" did not execute since for was successful.
else:
    print("Attempted 3 times, Failed")
