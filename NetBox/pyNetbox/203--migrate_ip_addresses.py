# 202--migrate_subnets.py

import json
import pynetbox
import urllib3
import time
import datetime
from collections import Counter
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

start_time = time.perf_counter()

with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False


# File paths
IP_ADDRESS_FILE = "/automation/python-data/phpipam-backups/phpipam_ip_addresses.json"
SUBNETS_FILE = "/automation/python-data/phpipam-backups/subnets.json"
IP_IMPORT_FILE = "/automation/python-data/phpipam-backups/ips_import.json"

TENANT_NAME = "WP-Corp"

counter_lock = Lock()
ip_counters = Counter()

total_ips = 0

# Ensure tenant exists


def get_or_create_tenant(name):
    tenant = nb.tenancy.tenants.get(name=name)
    if tenant:
        return tenant.id
    return nb.tenancy.tenants.create({"name": name}).id


tenant_id = get_or_create_tenant(TENANT_NAME)

tag = nb.extras.tags.get(name="phpipam-migrated")
tag_id = tag.id

# Load Subnets
with open(SUBNETS_FILE, "r") as f:
    all_subnet_ids = {}
    subnets = json.load(f)
    for subnet in subnets:
        sid = int(subnet.get("id", "0"))
        all_subnet_ids[sid] = subnet.get("mask")

valid_statuses = {"active", "deprecated", "reserved", "dhcp"}
autodiscovered_ip = "autodiscovered"


def create_ip(ip):
    address = ip.get("ip", "UNKNOWN")   # only IP; no mask.
    try:
        ip_address = ip["ip"]
        subnet_id = all_subnet_ids[ip["subnetId"]]
        if not subnet_id:
            with counter_lock:
                ip_counters["failed"] += 1
            return {"ip": address, "result": "failure", "comment": "could not find subnet ID"}
        address = f"{ip_address}/{subnet_id}"
        if autodiscovered_ip in ip["description"].lower():
            return {"ip": address, "result": "failure", "comment": "autodiscovered IP skipped"}
        if ip["status"] not in valid_statuses:
            # print(
            #     f"Skipping: {address} has invalid status (valid status: active, reserved, deprecated & dhcp)")
            with counter_lock:
                ip_counters["failed"] += 1
            return {"ip": address, "result": "failure", "comment": "invalid status (valid status: active, reserved, deprecated & dhcp)"}
        ip_exists = nb.ipam.ip_addresses.get(address=address)
        if ip_exists:
            # print(f"Skipping: {address} (already exists)")
            with counter_lock:
                ip_counters["success"] += 1
            return {"ip": address, "result": "success", "comment": "already exists"}
        else:
            if ip["hostname"]:
                payload = {
                    "address": address,
                    "status": ip["status"],
                    "tags": [tag_id],
                    "description": ip["description"],
                    "dns_name": ip["hostname"]
                }
                nb.ipam.ip_addresses.create(**payload)
                # print(f"Created IP address: {address}")
                with counter_lock:
                    ip_counters["success"] += 1
                return {"ip": address, "result": "success", "comment": "IP added"}
            else:
                payload = {
                    "address": address,
                    "status": ip["status"],
                    "tags": [tag_id],
                    "description": ip["description"]
                }
                nb.ipam.ip_addresses.create(**payload)
                # print(f"Created IP address: {address}")
                with counter_lock:
                    ip_counters["success"] += 1
                return {"ip": address, "result": "success", "comment": "IP added"}
    except Exception as e:
        # print(
        #     f"Warning: subnet ID {e} for {ip["ip"]} not found in subnets.json file")
        with counter_lock:
            ip_counters["failed"] += 1
        return {"ip": address, "result": "failure", "comment": f"exception occured {e}"}


# Load & create IP addresses

with open(IP_ADDRESS_FILE, "r") as f:
    ip_addresses = json.load(f)
    with ThreadPoolExecutor(max_workers=12) as executor:
        futures = []
        # saving results
        with open(IP_IMPORT_FILE, "a") as logging:
            for ip in ip_addresses:
                total_ips += 1
                future_ip = executor.submit(
                    create_ip, ip)
                futures.append(future_ip)
            for future in as_completed(futures):
                result = future.result()
                print(f"{result['ip']} --> {result['result']}")
                json.dump(result, logging, indent=2)
                logging.write("\n")
                logging.flush()

print(f"\nIP import result saved to: {IP_IMPORT_FILE}")
print(
    f"\nTotal IPs Processed: {total_ips}"
    f"\nTotal Successes: {ip_counters['success']}"
    f"\nTotal Failures: {ip_counters['failed']}"
    f"\n\nFor details, check {IP_IMPORT_FILE}"
)

end_time = time.perf_counter()
total_time = end_time - start_time
formatted_time = str(datetime.timedelta(seconds=int(total_time)))

print(f"Total time taken: {formatted_time}")
