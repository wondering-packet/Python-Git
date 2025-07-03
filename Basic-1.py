data_from_api = [
    {"name": "Raj", "region": "north", "sales": 50000},
    {"name": "Simran", "region": "south", "sales": 60000},
    {"name": "Amit", "region": "north", "sales": 45000},
    {"name": "Priya", "region": "west", "sales": 70000},
    {"name": "Karan", "region": "north", "sales": 55000},
]
# filtering north sales only:
sales_north = [
    sale for sale in data_from_api if sale["region"] == "north"]
# print(sales_north)

# total sales for north region:

sales_north_total = sum(sale["sales"] for sale in sales_north)
print("Total sales in north: ", sales_north_total)
sales_north_avg = sales_north_total/len(sales_north)
# average is returing flot so type coverting it.
print("Average sales in north: ", int(sales_north_avg))

# creating a new dictionary for name -> sales:

sales_north_filtered = {sale["name"]: sale["sales"] for sale in sales_north}
# print(sales_north_filtered)

# printing salesperson details from north:

for name, sales in sales_north_filtered.items():
    print(f"{name}: {sales} sales")
