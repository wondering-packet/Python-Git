# a very basic script to fill in dummy data.
# it creates ip address for the provided prefixes.
# in netbox, each ip has a status e.g. ative, reserved etc.
# status is randomly assigned to each ip.

import pynetbox
import urllib3
import json
import ipaddress
import random
# some multithreading to speed things up.
from concurrent.futures import ThreadPoolExecutor

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

# tagging all IPs for easy identification.
tag = nb.extras.tags.get(name="vg")
tag_id = tag.id

# add or remove as per your environment.
prefixes = [
    '172.16.24.0/24',
    '172.16.29.0/24',
    '172.16.16.0/24',
    '172.16.18.0/24',
    '172.16.21.0/24',
    '172.16.25.0/24',
    '172.16.12.0/24'
]

# you will have to know this beforehand. you can use choices() method to find this info.
ip_status = [
    "active",
    "reserved",
    "deprecated",
    "dhcp"
]


def create_ip(prefix, prefix_len):
    # this converts all hosts into a list that we can itereate.
    total_available_ips = list(prefix.hosts())
    # randomly filling the subnet block with 60-80% utilization.
    percent = random.uniform(0.6, 0.8)
    # applying 60-80% utilization logic.
    sample_size = int(len(total_available_ips)*percent)
    # creating a random sample which contains 60-80% of IPs that we will be creating.
    available_ips = random.sample(total_available_ips, sample_size)
    # iterating over our sample now:
    for each_ip in available_ips:
        # random IP status. e.g. active.
        status = random.choice(ip_status)
        # address needs to be in slash notation.
        address = f"{each_ip}/{prefix_len}"
        exists = nb.ipam.ip_addresses.get(address=address)
        if exists:
            print(f"Duplicate, already exists: {address}")
            continue
        try:
            payload = {
                "address": address,
                "status": status,
                "description": "Created via API",
                "tags": [tag_id]
            }
            nb.ipam.ip_addresses.create(**payload)
            print(f"Created: {each_ip}/{prefix_len}")
        except Exception as e:
            print(f"Error for {address}: {e}")
    print(f"Prefix now populated: {prefix}")


def main():
    # multithreading
    with ThreadPoolExecutor(max_workers=8) as executor:
        for each_prefix in prefixes:
            prefix = ipaddress.ip_network(each_prefix)
            prefix_len = prefix.prefixlen
            executor.submit(create_ip, prefix, prefix_len)


if __name__ == "__main__":
    main()
