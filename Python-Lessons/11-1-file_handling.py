# syntax:
#    open("file_name", "mode")
# modes:
#   "r" = read
#   "w" = write
#   "a" = append
#   "rb"/"wb" = read/write in binary

# @@@--- writing to a file:

my_file = open("my_file.txt", "w")
my_file.write("Hello, i am trying to learn python! \n")
my_file.write(
    "it turns out chatgpt is a great teacher when it comes to coding :)\n")
my_file.write("\nHappy learning!")
my_file.write("\nVG")
my_file.close()         # always close your file to free up the system memory.

# @@@--- reading a file: method 1

my_file = open("my_file.txt", "r")
content = my_file.read()    # read() method to read the file.
my_file.close()
print(content)

# @@@--- reading a file: method 2
print("----------------------------------------------------------------------\n")
my_file = open("my_file.txt", "r")
for each_line in my_file:
    # without strip(), you get a newline after each line
    print(each_line.strip())
my_file.close()

# @@@--- appending to a file:

my_file = open("my_file.txt", "a")
my_file.write(" | vg-training@outlook.com")
# content = my_file.read()      <<--- throws error because you can't read an append file.
print(content)
my_file.close()

print("----------------------------------------------------------------------\n")

# @@@--- best practice is to use a "with" block; this auto closes the file.

with open("my_file.txt", "a") as my_file:
    my_file.write("\n:)")
with open("my_file.txt", "r") as my_file:
    print(my_file.read())
