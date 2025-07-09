fav_langs = ["python", "c++", "java"]
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
