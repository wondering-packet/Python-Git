import json


def display_menu():
    print("\nExpense Tracker Menu:")
    print("1. Add expense")
    print("2. View all expenses")
    print("3. View total expenses")
    print("4. Exit")


expenses = []

try:
    with open("Projects/Expense Tracker/expenses.json", "r") as file:
        expenses = json.load(file)
except FileNotFoundError:
    print("\nexpense.json file was not found. starting fresh!\n")
else:
    print("\nListing previous expenses:\n")
    for each_expense in expenses:
        print(
            f"Expense: {each_expense['description']}, Amount: {each_expense['amount']}")
finally:
    print("\n------------------Expense Tracker------------------\n")

while True:
    display_menu()
    choice = input("Enter your choice (1-4): ")

    if choice == "1":
        # Add expense
        description = input("Please enter a description for your expense: ")
        while True:
            try:
                amount = int(
                    input("Please enter the amount spent on the expense: "))
            except ValueError:
                print("\nError: Please enter a valid integer value!")
            else:
                break
        expenses_dict = {"description": description,
                         "amount": amount}
        expenses.append(expenses_dict)
    elif choice == "2":
        # View expenses
        print("\n")
        for each_expense in expenses:
            print(
                f"Expense: {each_expense['description']}, Amount: {each_expense['amount']}")
    elif choice == "3":
        # View total
        print("\n")
        total = 0
        for each_expense in expenses:
            total += each_expense["amount"]
        print(f"Total expense amount: {total}")
    elif choice == "4":
        print("Exiting program. Goodbye!")
        with open("Projects/Expense Tracker/expenses.json", "w") as file:
            json.dump(expenses, file, indent=4)
        break
    else:
        print("Invalid choice. Please enter 1-4.")
