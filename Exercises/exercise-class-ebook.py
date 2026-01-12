class Book:
    def __init__(self, title, author, year):
        self.title = title
        self.author = author
        self.year = year

    def display_info(self):
        print(f"Title: {self.title}, Author: {self.author}, Year: {self.year}")


class EBook(Book):          # class child_class(parent_class)
    # downloads is an optional parameter. allows default argument.
    # still have the rest of the parameters from parent class.
    def __init__(self, title, author, year, file_size, format, downloads=0):
        # super() is used to initialize the parent class attributes using parent classes's constructor. calls __init__ from parent.
        super().__init__(title, author, year)
        # still have to initialize child class attributes.
        self.file_size = file_size
        self.format = format
        # this is a private attribute ("__" makes it private).
        self.__downloads = downloads

    def display_info(self):
        print(
            f"Title: {self.title}, Author: {self.author}, Year: {self.year}, File Size: {self.file_size} MB, Format: {self.format}")

    def download(self):
        self.__downloads += 1

    def get_downloads(self):
        print(f"Total downloads: {self.__downloads}")


# still have to input all arguments for parent + child. except the default argument (optional).
book_1 = EBook("Water magician", "hiro", 2007, 5, "epub")
book_2 = EBook("Regressing mercenary", "wakaba", 2018, 10, "pdf")
book_1.display_info()
book_2.display_info()
book_1.download()
book_1.download()
book_2.download()
book_2.download()
book_2.download()
book_1.get_downloads()
book_2.get_downloads()
