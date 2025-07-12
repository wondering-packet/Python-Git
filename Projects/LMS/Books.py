import json
import os

# class to hold each book


class Book:

    def __init__(self, title, author, year, is_borrowed=False):
        self.title = title
        self.author = author
        self.year = year
        self.is_borrowed = is_borrowed

    def display_info(self):
        print(
            f"Title: {self.title}, Author: {self.author}, Year: {self.year}, Available: {not self.is_borrowed}")

    def borrow_book(self):
        if self.is_borrowed:
            print(f"Book '{self.title}' is already borrowed.")
            return False
        else:
            self.is_borrowed = True
            print(f"Book '{self.title}' has been borrowed.")
            return True

    def return_book(self):
        if not self.is_borrowed:
            print(f"Book '{self.title}' was not borrowed")
            return False
        else:
            self.is_borrowed = False
            print(f"Book '{self.title}' has been returned")
            return True

    def to_dict(self):
        return {"title": self.title,
                "author": self.author,
                "year": self.year,
                "available": not self.is_borrowed}

    # staticmethod is a method in class which doesn't rely on the class.
    @staticmethod
    def from_dict(data):
        return Book(
            title=data["title"],
            author=data["author"],
            year=data["year"],
            is_borrowed=not data["available"]

        )


# book1.display_info()
# book1.borrow_book()
# book1.display_info()
# book1.return_book()
# book1.display_info()
print("-----------------------------------------\n")
# book1.to_dict()
# print(book1.book_dict)
print("-----------------------------------------\n")


class Library:
    total_borrowed_books = 0  # class variable

    def __init__(self):
        self.books = []  # holds Book objects

    def add_book(self, book):
        for existing_book in self.books:        # skipping duplicates
            if (existing_book.title.lower() == book.title.lower() and
                existing_book.author.lower() == book.author.lower() and
                    existing_book.year == book.year):
                print(
                    f"Book '{book.title}' already exists in the library. Skipping.")
                return
        # append book to self.books
        self.books.append(book)

    def display_books(self):
        # loop through self.books and call display_info()
        print("Book list: \n")
        for each_book in self.books:
            each_book.display_info()

    def borrow_book_by_title(self, title):
        # find the book by title, borrow it, increment Library.total_borrowed_books if borrowed
        found = False
        for each_book in self.books:
            if each_book.title.lower().strip() == title.lower().strip():
                if each_book.borrow_book():
                    Library.total_borrowed_books += 1
                found = True
                break
        if not found:
            print(f"Book '{title}' not found in the library.")

    def return_book_by_title(self, title):
        # find the book by title, return it, decrement Library.total_borrowed_books if returned
        found = False
        for each_book in self.books:
            if each_book.title.lower().strip() == title.lower().strip():
                if each_book.return_book():
                    Library.total_borrowed_books -= 1
                found = True
                break
        if not found:
            print(f"Book '{title}' not found in the library.")

    def save_library(self):
        # saves the library into a json file. we are using json because it provides a structured format for file handling.
        with open("Projects/LMS/library.json", "w") as library:
            # inside the dump(), we have a for loop going on, which keeps on feeding each_book until all books have been dumped.
            # chatgpt helped in simplyfying this. it saves having additional dictonary or list to seperately store each_book
            # then dumping it.
            # each_book.to_dict() creates a dictionary for each book. defined in Book class above.
            json.dump([each_book.to_dict()
                      for each_book in self.books], library, indent=4)
        print("INFO: JSON saved")

    def load_library(self):
        if os.path.exists("Projects/LMS/library.json"):
            print("INFO: loading JSON")
            with open("Projects/LMS/library.json", "r") as library:
                json_data = json.load(library)
                # again not using a seperate variable to transfer the data.
                # directly storing the output of for loop (which is a book) into the self.books[]
                # Book.from_dict(each_book) gives us the data in a Book object format.
                # without this our data would be in dictionary format.
                # again this is defined in Book class.
                self.books = [Book.from_dict(each_book)
                              for each_book in json_data]
        else:
            print("INFO: JSON not found")


lib1 = Library()

print("--------------------load library---------------------\n")
lib1.load_library()  # load at startup
print("--------------------dispaly all books---------------------\n")
lib1.display_books()
print("--------------------testing---------------------\n")
book1 = Book("Python Basics", "VG", 2020)
book2 = Book("Advance OOP concepts", "Rahul S", 2018)
book3 = Book("Python OOP concepts", "RS Mehta", 2024)
book5 = Book("Maths Advanced", "HV S.", 2016)

lib1.add_book(book1)
lib1.add_book(book2)
lib1.add_book(book3)
lib1.add_book(book5)

print("--------------------borrow/return logic---------------------\n")
lib1.borrow_book_by_title("Python Basics")
lib1.borrow_book_by_title("Python Basics")
lib1.return_book_by_title("Python Basics")
lib1.return_book_by_title("Python Basicss")
lib1.borrow_book_by_title("Python Basics")
print("--------------------borrowed books---------------------\n")
print(f"\nTotal Borrowed Books: {lib1.total_borrowed_books}")
print("--------------------dispaly all books---------------------\n")
lib1.display_books()
print("--------------------save library---------------------\n")
lib1.save_library()  # save at exit
