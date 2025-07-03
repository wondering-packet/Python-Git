high_income = True          # boolean value; not a string.
good_credit = False
us_company = False

if high_income and good_credit:     # comparing boolean values.
    print("Eligible_1")
elif high_income or good_credit:
    print("Eligible_2")
# NOT of us_company which means TRUE; TRUE = execute the statement; FALSE = don't execute the statement.
elif not us_company:
    print("Eligible_3")
else:
    print("Not eligible")

# more complex example
if (high_income or good_credit) and not us_company:
    print("Eligible_4")

# @@@@ - short circuit - @@@@
# i actually didn't understand this concept at all tbh. just remember the braces to avoid issues.

# exmaple 1
if high_income or good_credit or us_company:
    print("Eligible_5")

# example 2
if high_income and good_credit and not us_company:
    print("Eligible_6")
