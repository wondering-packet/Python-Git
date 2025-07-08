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
            print("Already borrowed")
        else:
            self.is_borrowed = True
            print(f"Book {self.title} has been borrowed.")

    def return_book(self):
        if not self.is_borrowed:
            print("Book was not borrowed")
        else:
            self.is_borrowed = False
            print(f"Book {self.title} has been returned")


book1 = Book("Python Basics", "VG", 2020)
book2 = Book("Advance OOP concepts", "Rahul S", 2018)
book1.display_info()
print(book1.title)
