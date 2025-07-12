file = "test_dir"
try:
    with open(file, "r") as temp_file:
        print(temp_file.read())
except FileNotFoundError:
    print("\nError: File not found")
except Exception as e:
    print(type(e))
    print(e)
finally:
    print("\nInfo: Operation completed")
