# strings have some built-in methods which can be accessed by appending a "." to the string

course = "  Python programming"

print(course.lower())
# checks to see if the string is uppercase. can do lower as well. returns boolean value.
print((course.upper()).isupper())
# converts first character case of each word to upper.
print(course.title())
# strips whitespaces for both left & right. can do lstrip & rstrip as well.
print(course.strip())
# finds the Index where the text starts.
print(course.find("gra"))
# replace.
print(course.replace("P", "Z"))
# find methods; "in" return true when true; "not in" returns true when false.
print("ramm" in course)
print("zoro" not in course)
