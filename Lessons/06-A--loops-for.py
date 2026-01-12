# using range().
for number in range(3):
    print(f"Hello, this is loop {number+1}")
# using range() with custom start & end values.
for number in range(1, 4):
    print("Hello", number, number * ".")
# using range() with custom start, end & step values.
for number in range(1, 10, 2):
    print("Iello", number, number * ".")


# example where output is written in the same line.
names = ["pinky", "chinky", "rinky", "shinkyyy"]

# name: len(name) is the output of iteration
dict_example = {name: len(name) for name in names}
print(dict_example)
