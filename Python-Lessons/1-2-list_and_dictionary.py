"""
list are:
1. orderd, starting from index 0.
2. can contain any type i.e. int, float, string, another list etc.
3. accessing a value via: list[index_number]
4. updating/adding via: list.append("value")
5. removing a value via: list.remove("value")
"""
fav_langs = ["python", "c++", "java"]
"""
dictionary are:
1. unorderd, key-value pairs.
2. can contain any type.
3. accessing a value via: dictionary["key_name"]
4. updating via: dictionary["key_name"] = "new value"
5. adding via: dictionary["key_name] = "value"
6. removing via: del.dictionary["key_name"]
"""
my_dict = {
    "name": "VG",
    "age": 77,
    "favourite language": "Python"
}
print(fav_langs[0])
print(my_dict["name"])

fav_langs.append("javascript")
fav_langs.remove("c++")

my_dict["favourite language"] = "Rust"
del my_dict["age"]

print(fav_langs)
print(my_dict)
