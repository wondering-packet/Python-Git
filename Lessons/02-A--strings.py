course_name = "Python Programming"

# length of a string.
print(len(course_name))

# character from left (default behaviour); starts from index 0.
print(course_name[0])

# character from right (adding minus); 2nd character (not index).
print(course_name[-2])

# slicing; before colon is the index value; after colon is the character number from index 0 (e.g. 1=P, 2=y).
print(course_name[0:6])     # index 0 to 6th character
print(course_name[0:])      # index 0 to end
print(course_name[:3])      # start to 3rd character
print(course_name[:])       # start to end
print(course_name[2:4])     # index 2 to 4th character
# index 1 from left & index 1 from right. TBH this one is hard to remember.
print(course_name[1:-1])
