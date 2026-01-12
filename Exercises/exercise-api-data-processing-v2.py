data_from_api = [
    {"name": "Raj", "region": "region", "sales": 50000},
    {"name": "Simran", "region": "south", "sales": 60000},
    {"name": "Amit", "region": "region", "sales": 45000},
    {"name": "Priya", "region": "west", "sales": 70000},
    {"name": "Karan", "region": "region", "sales": 55000},
]


def sales_data(region):

    # filtering region sales only:
    sales_region = [sale for sale in data_from_api if sale["region"] == region]
    # print(sales_region)

    # total sales for region region:

    sales_region_total = sum(sale["sales"] for sale in sales_region)
    print(f"Total sales in {region}: ", sales_region_total)
    sales_region_avg = sales_region_total/len(sales_region)
    # average is returing flot so type coverting it.
    print(f"Average sales in {region}: ", int(sales_region_avg))

    # creating a new dictionary for name -> sales:

    sales_region_filtered = {sale["name"]: sale["sales"]
                             for sale in sales_region}
    # print(sales_region_filtered)

    # printing salesperson details from region:

    for name, sales in sales_region_filtered.items():
        print(f"{name}: {sales} sales")


region = input("please type in region: ")
print(f"Below are the details for {region} region: \n")
sales_data(region)
