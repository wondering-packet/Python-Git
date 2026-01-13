# read the instrucitons.md for script overview & logic

import pynetbox
import urllib3
import json
import os
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

# load data to build A
with open("./Projects/Netbox-data-ingestion-github/data/wan_ips.json", "r") as f:
    dataset_a_source = json.load(f)
    # pprint(dataset_a)

# loading relevent data from the source data into the dataset A list.
# this list will be used to create/update IP in netbox.
dataset_a = []
records_processed = 0
for platform, ip_data in dataset_a_source.items():
    if platform in {"meraki", "aruba"}:
        for each_ip in ip_data:
            each_ip_filtered = {}
            each_ip_filtered["platform"] = platform
            each_ip_filtered["address"] = each_ip["ip"]
            each_ip_filtered["description"] = each_ip["caption"]
            each_ip_filtered["raw_data"] = each_ip.copy()
            dataset_a.append(each_ip_filtered)
            records_processed += 1

pprint(dataset_a)
print(f"\n\nTotal records processed: {records_processed}")

# load data to build B:
dataset_b_source = nb.ipam.ip_addresses.all()
for each_ip in dataset_b_source:
    pprint(each_ip)
    break
