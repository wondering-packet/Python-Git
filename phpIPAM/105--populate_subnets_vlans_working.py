#!/usr/bin/env python3

import requests
import time
import urllib3
import json

# Disable SSL warnings for lab
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("/automation/secrets/phpipam.json", "r") as f:
    secret = json.load(f)
    API_BASE_URL = secret["API_BASE_URL"]
    API_TOKEN = secret["API_TOKEN"]

HEADERS = {"token": API_TOKEN, "Content-Type": "application/json"}

SECTION_ID = "1"

# Define a stable mapping for location network blocks
location_networks = {
    1: "172.16.0.0/16", 2: "172.17.0.0/16", 3: "172.18.0.0/16", 4: "172.19.0.0/16",
    5: "172.20.0.0/16", 6: "172.21.0.0/16", 7: "172.22.0.0/16", 8: "172.23.0.0/16",
    9: "172.24.0.0/16", 10: "172.25.0.0/16", 11: "172.26.0.0/16", 12: "172.27.0.0/16",
    13: "172.28.0.0/16", 14: "172.29.0.0/16", 15: "172.30.0.0/16", 16: "172.31.0.0/16"
}

# Your 55+ racks here (sample subset shown for brevity)
racks = [
    {"id": 1, "name": "AMER-E-DC1-R8C1", "size": 42, "location": 1},
    {"id": 2, "name": "AMER-W-DC1-R8C1", "size": 42, "location": 2},
    {"id": 3, "name": "EMEA-DE-DC1-R8C1", "size": 42, "location": 3},
    {"id": 4, "name": "AP-IN-DC1-R8C1", "size": 45, "location": 4},
    # ... Add all 55 locations here ...
]

# Add network block to each rack for clarity
for rack in racks:
    rack["network_block"] = location_networks.get(rack["location"])


def get_existing_subnets():
    used_subnets = set()
    try:
        r = requests.get(f"{API_BASE_URL}/sections/{SECTION_ID}/subnets/",
                         headers=HEADERS, verify=False, timeout=30)
        if r.status_code == 200 and r.json().get("success"):
            for item in r.json()["data"]:
                try:
                    cidr = f"{item['subnet']}/{item['mask']}"
                    used_subnets.add(ipaddress.ip_network(cidr))
                except Exception:
                    continue
    except Exception as e:
        print(f"⚠️ Error fetching existing subnets: {e}")
    return used_subnets


def vlan_exists_and_get_id(vlan_number):
    try:
        r = requests.get(f"{API_BASE_URL}/vlans/search/{vlan_number}",
                         headers=HEADERS, verify=False, timeout=10)
        if r.status_code == 200 and r.json().get("success"):
            data = r.json()["data"]
            if isinstance(data, list) and data:
                return data[0]["id"]
            elif isinstance(data, dict):
                return data["id"]
    except Exception as e:
        print(f"⚠️ VLAN check failed for {vlan_number}: {e}")
    return None


def create_vlan(vlan_number, name):
    payload = {
        "name": f"VLAN {vlan_number}",
        "number": str(vlan_number),
        "description": f"Auto-created VLAN {vlan_number} for {name}",
        "domainId": "1"
    }
    try:
        r = requests.post(f"{API_BASE_URL}/vlans/", headers=HEADERS,
                          json=payload, verify=False, timeout=10)
        if r.status_code in [200, 201]:
            print(f"✅ Created VLAN {vlan_number} for {name}")
            return True
        else:
            print(
                f"❌ VLAN {vlan_number} creation failed: {r.status_code} {r.text}")
    except Exception as e:
        print(f"❌ VLAN creation error for {vlan_number}: {e}")
    return False


def ensure_vlan_and_get_id(vlan_number, name):
    vlan_id = vlan_exists_and_get_id(vlan_number)
    if vlan_id:
        return vlan_id
    if create_vlan(vlan_number, name):
        for _ in range(5):
            vlan_id = vlan_exists_and_get_id(vlan_number)
            if vlan_id:
                print(f"✅ VLAN {vlan_number} now available.")
                return vlan_id
            time.sleep(1)
    print(f"❌ VLAN {vlan_number} unavailable after retries.")
    return None


def create_subnet(subnet, location_id, vlan_id, description, vlan_number):
    payload = {
        "subnet": str(subnet.network_address),
        "mask": str(subnet.prefixlen),
        "description": description,
        "sectionId": SECTION_ID,
        "location": str(location_id),
        "vlanId": str(vlan_id)
    }
    try:
        r = requests.post(f"{API_BASE_URL}/subnets/",
                          headers=HEADERS, json=payload, verify=False, timeout=10)
        if r.status_code in [200, 201]:
            print(
                f"✅ Created {subnet} VLAN-ID {vlan_number} for {description}")
            return True
        else:
            print(
                f"❌ Failed {subnet} VLAN-ID {vlan_number}: {r.status_code} {r.text}")
    except Exception as e:
        print(f"❌ Subnet creation error {subnet}: {e}")
    return False


def find_next_free_subnets(parent_network, prefix, used_subnets, count):
    available = []
    for subnet in parent_network.subnets(new_prefix=prefix):
        if len(available) >= count:
            break
        if any(subnet.overlaps(u) for u in used_subnets):
            continue
        available.append(subnet)
    return available


def populate_subnets():
    used_subnets = get_existing_subnets()
    vlans_per_rack = 5  # Adjust this to 5–10 as needed

    for rack in racks:
        parent_network = ipaddress.ip_network(rack["network_block"])
        prefix = 25 if rack["size"] > 30 else 24
        subnets_to_create = find_next_free_subnets(
            parent_network, prefix, used_subnets, vlans_per_rack)

        for idx, subnet in enumerate(subnets_to_create):
            vlan_number = 2000 + rack["id"] * 10 + \
                idx  # Structured VLAN numbering
            vlan_id = ensure_vlan_and_get_id(vlan_number, rack["name"])
            if not vlan_id:
                print(
                    f"⚠️ Skipping {rack['name']} VLAN {vlan_number} due to VLAN creation failure.")
                continue
            description = f"populateed {rack['name']} VLAN {vlan_number}"
            if create_subnet(subnet, rack["location"], vlan_id, description, vlan_number):
                used_subnets.add(subnet)
            else:
                print(
                    f"❌ Failed to create subnet {subnet} for {rack['name']} VLAN {vlan_number}")


if __name__ == "__main__":
    populate_subnets()
