# @@@-- zip is an iterable like list(), range() etc. ---@@@
# pairs two lists; stores the list in memory (means you can't directly print); the shortest child list is taken.
names = ["pinky", "chinky", "rinky", "shinky"]      # list length = 4
marks = [80, 90, 100, 70, 95]                       # list length = 5

output = zip(names, marks)                          # takes length = 4
for name, mark in output:
    print(name, mark)

# @@@-- enumerate returns a pair of (index, value) in each loop.
# also lets you start the index from a custom value instead of the default 0. e.g. 1 or 2.
# syntax: enumerate(iterable, start=0)

names = ["pinky", "chinky", "rinky", "shinky"]
for i, name in enumerate(names):                    # default start=0
    print(i, name)

for i, name in enumerate(names, 1):
    print(i, name)

# 3. Looping with enumerate() and zip()
# -------------------------------------
# Code:
names = ["Alice", "Bob", "Charlie", "Rahul"]  # List of names
marks = [85, 90, 88]                 # Corresponding marks

# Loop through both lists together using zip(), and enumerate() to get index
for i, (name, mark) in enumerate(zip(names, marks), 1):
    print(f"{i}. {name}: {mark}")
# Output:
"""
1. Alice: 85
2. Bob: 90
3. Charlie: 88
"""
