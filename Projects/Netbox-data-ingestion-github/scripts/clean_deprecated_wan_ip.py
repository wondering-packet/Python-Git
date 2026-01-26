# read the instrucitons.md for script overview & logic

import pynetbox
import urllib3
import json
import os
import ipaddress
from datetime import date, datetime
from pprint import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load credentials
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

# intitialze netbox object
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

# counter
records_processed_b = 0

# takes in last_seen value (str), normalizes it & returns how old the last seen is.


def last_seen_in_days(last_seen, address):
    if last_seen is None:
        return None
    else:
        try:
            last_seen_normalized = datetime.fromisoformat(
                str(last_seen)).date()
            return (date.today() - last_seen_normalized).days
        except Exception as e:
            print(
                f"Execption occured during last seen calculation for the address {address}, {type(e)}")
            print(e)
            return None


print("===============================================================")
print("CLEANUP workflow:\n")

for each_ip in nb.ipam.ip_addresses.filter(
        tag="external-sot-github", status="deprecated"):

    address = str(each_ip.address).strip()
    last_seen_days = last_seen_in_days(
        each_ip.custom_fields["last_seen"], str(each_ip.address).strip())
    tags = each_ip.tags
    records_processed_b += 1

    if last_seen_days is None:
        print("-----------------------------------------------------")
        print(
            f"{address} -- Age: UNKNOWN days -- Requires review (last seen missing)")
        existing_slugs = []
        if tags:
            print(f"\t{address} -- existing tags: ")
            for each_tag in tags:
                print(f"\t\t{each_tag}")
                existing_slugs.append(each_tag.slug)
        if not "review-required" in existing_slugs:
            existing_slugs.append("review-required")
        payload = {"tags": [{"slug": each_tag}
                            for each_tag in existing_slugs]}

        each_ip.update(payload)
    elif last_seen_days >= 90:
        each_ip.delete()
        print("-----------------------------------------------------")
        print(
            f"{address} -- Age: {last_seen_days} days -- Deleted")
print("===============================================================")
print(f"Total records processed from NetBox: {records_processed_b}")
print("-----------------------------------------------------")
