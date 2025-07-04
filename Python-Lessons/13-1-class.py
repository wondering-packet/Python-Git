class Book:
    # __init__ always get executed whenever you instantiate this class (i.e. create an object).
    # it is required to initialize your objects; it is called constructor.
    #
    # self refers to the object (instance).
    # you need this because otherwise the class won't know which object you are referencing, e.g.:
    # self.title for book_1 = book1.title
    # self.title for book_2 = book2.title
    # so when you are instantiating book_1:
    #   book1.title = "Water magician"
    #   book1.author = "hiro"
    #   book1.year = 2007
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year
        # because __init__ always gets executed, below line always prints whenever an object is instantiated.
        print(f"Working with a class {self.title} ; __init__ constructor")

    # again self is needed to identify the correct object & the correct attributes of the object.
    def display_info(self):
        # self.title here would mean:
        #   book_1.title for book_1 object.
        #   book_2.title for book_2 object.
        # it changes dynamically depending on which object (i.e. self) is calling it.
        print(f"Title: {self.title}, Author: {self.author}, Year: {self.year}")

    def is_classic(self):
        classic = self.year < 2010      # a simple boolean comparison :)
        print(f"{self.title} is classic: {classic}")


book_1 = Book("Water magician", "hiro", 2007)
book_2 = Book("Regressing mercenary", "wakaba", 2018)
book_1.display_info()   # __init__ is called.
book_2.display_info()
# book_1 as an object, can call a method which has now been instantiated for itself.
book_1.is_classic()
book_2.is_classic()
