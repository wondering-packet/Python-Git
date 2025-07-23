#!/usr/bin/env python3

import ipaddress
import requests
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_BASE_URL = "https://phpipam.intra.slicesoftech.net/api/labmigration"
API_TOKEN = "gwy_aLbX5iEFgNMZAe5ONIWHHuPEocJ7"
HEADERS = {"token": API_TOKEN, "Content-Type": "application/json"}

SECTION_ID = "1"

# Define network blocks per location
location_networks = {
    1: "172.16.0.0/16",
    2: "172.17.0.0/16",
    3: "172.18.0.0/16",
    4: "172.19.0.0/16",
    5: "172.20.0.0/16",
    6: "172.21.0.0/16",
    7: "172.22.0.0/16",
    8: "172.23.0.0/16",
    9: "172.24.0.0/16",
    10: "172.25.0.0/16",
    11: "172.26.0.0/16",
    12: "172.27.0.0/16",
    13: "172.28.0.0/16",
    14: "172.29.0.0/16",
    15: "172.30.0.0/16",
    16: "172.31.0.0/16"
}

racks = [
    {"id": 1, "name": "AMER-E-DC1-R8C1", "size": 42, "location": 1},
    {"id": 2, "name": "AMER-W-DC1-R8C1", "size": 42, "location": 2},
    {"id": 3, "name": "EMEA-DE-DC1-R8C1", "size": 42, "location": 3},
    {"id": 4, "name": "AP-IN-DC1-R8C1", "size": 45, "location": 4},
    {"id": 5, "name": "AMER-E-DC1-R8C2", "size": 42, "location": 1},
    {"id": 6, "name": "AMER-E-DC1-R8C4", "size": 42, "location": 1},
    {"id": 7, "name": "AMER-W-DC1-R8C5", "size": 28, "location": 2},
    {"id": 8, "name": "AP-JP-DC1-R2C3", "size": 21, "location": 5},
    {"id": 9, "name": "AP-JP-DC2-R5C1", "size": 12, "location": 5},
    {"id": 10, "name": "AP-JP-DC1-R7C2", "size": 26, "location": 5},
    {"id": 11, "name": "AP-JP-DC3-R3C4", "size": 9, "location": 5},
    {"id": 12, "name": "AP-SG-DC1-R1C2", "size": 40, "location": 6},
    {"id": 13, "name": "AP-SG-DC2-R4C1", "size": 45, "location": 6},
    {"id": 14, "name": "AP-SG-DC2-R2C3", "size": 16, "location": 6},
    {"id": 15, "name": "AP-SG-DC3-R6C1", "size": 19, "location": 6},
    {"id": 16, "name": "AP-AU-DC1-R3C3", "size": 37, "location": 7},
    {"id": 17, "name": "AP-AU-DC1-R8C2", "size": 42, "location": 7},
    {"id": 18, "name": "AP-AU-DC2-R5C4", "size": 12, "location": 7},
    {"id": 19, "name": "AP-AU-DC3-R2C1", "size": 46, "location": 7},
    {"id": 20, "name": "AP-KR-DC2-R4C2", "size": 25, "location": 8},
    {"id": 21, "name": "AP-KR-DC1-R6C3", "size": 20, "location": 8},
    {"id": 22, "name": "AP-KR-DC3-R3C4", "size": 18, "location": 8},
    {"id": 23, "name": "AP-KR-DC1-R1C1", "size": 22, "location": 8},
    {"id": 24, "name": "AP-HK-DC1-R2C4", "size": 47, "location": 9},
    {"id": 25, "name": "AP-HK-DC2-R3C3", "size": 42, "location": 9},
    {"id": 26, "name": "AP-HK-DC3-R5C1", "size": 24, "location": 9},
    {"id": 27, "name": "AP-HK-DC1-R6C2", "size": 25, "location": 9},
    {"id": 28, "name": "EMEA-IT-DC1-R4C1", "size": 44, "location": 10},
    {"id": 29, "name": "EMEA-IT-DC2-R2C3", "size": 20, "location": 10},
    {"id": 30, "name": "EMEA-IT-DC3-R3C2", "size": 38, "location": 10},
    {"id": 31, "name": "EMEA-IT-DC1-R1C4", "size": 42, "location": 10},
    {"id": 32, "name": "EMEA-ES-DC1-R3C3", "size": 10, "location": 11},
    {"id": 33, "name": "EMEA-ES-DC2-R5C2", "size": 37, "location": 11},
    {"id": 34, "name": "EMEA-ES-DC3-R4C1", "size": 28, "location": 11},
    {"id": 35, "name": "EMEA-ES-DC1-R2C4", "size": 22, "location": 11},
    {"id": 36, "name": "EMEA-FR-DC1-R2C2", "size": 17, "location": 12},
    {"id": 37, "name": "EMEA-FR-DC2-R3C3", "size": 13, "location": 12},
    {"id": 38, "name": "EMEA-FR-DC3-R4C1", "size": 45, "location": 12},
    {"id": 39, "name": "EMEA-FR-DC1-R5C4", "size": 18, "location": 12},
    {"id": 40, "name": "EMEA-NL-DC2-R4C3", "size": 27, "location": 13},
    {"id": 41, "name": "EMEA-NL-DC1-R2C2", "size": 34, "location": 13},
    {"id": 42, "name": "EMEA-NL-DC3-R3C1", "size": 43, "location": 13},
    {"id": 43, "name": "EMEA-NL-DC1-R5C4", "size": 25, "location": 13},
    {"id": 44, "name": "EMEA-SE-DC1-R3C2", "size": 28, "location": 14},
    {"id": 45, "name": "EMEA-SE-DC2-R1C3", "size": 19, "location": 14},
    {"id": 46, "name": "EMEA-SE-DC3-R4C4", "size": 43, "location": 14},
    {"id": 47, "name": "EMEA-SE-DC1-R2C1", "size": 30, "location": 14},
    {"id": 48, "name": "EMEA-NO-DC2-R3C2", "size": 13, "location": 15},
    {"id": 49, "name": "EMEA-NO-DC1-R5C3", "size": 9, "location": 15},
    {"id": 50, "name": "EMEA-NO-DC3-R2C1", "size": 40, "location": 15},
    {"id": 51, "name": "EMEA-NO-DC1-R4C4", "size": 43, "location": 15},
    {"id": 52, "name": "EMEA-PL-DC1-R2C2", "size": 9, "location": 16},
    {"id": 53, "name": "EMEA-PL-DC2-R3C3", "size": 29, "location": 16},
    {"id": 54, "name": "EMEA-PL-DC3-R4C1", "size": 28, "location": 16},
    {"id": 55, "name": "EMEA-PL-DC1-R5C4", "size": 47, "location": 16}
]

# Append the network block info
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


def get_master_supernet_id(network_block, location_name):
    network = ipaddress.ip_network(network_block)
    try:
        r = requests.get(f"{API_BASE_URL}/sections/{SECTION_ID}/subnets/",
                         headers=HEADERS, verify=False, timeout=20)
        if r.status_code == 200 and r.json().get("success"):
            for item in r.json()["data"]:
                try:
                    cidr = f"{item['subnet']}/{item['mask']}"
                    if cidr == str(network):
                        return item["id"]
                except Exception:
                    continue
    except Exception as e:
        print(f"⚠️ Supernet check error: {e}")

    # Create supernet if not found
    payload = {
        "subnet": str(network.network_address),
        "mask": str(network.prefixlen),
        "description": f"{location_name.split('-')[0]} - Supernet",
        "sectionId": SECTION_ID,
        "isFolder": "0"
    }
    try:
        r = requests.post(f"{API_BASE_URL}/subnets/",
                          headers=HEADERS, json=payload, verify=False, timeout=20)
        if r.status_code in [200, 201]:
            print(f"✅ Created supernet {network} for {location_name}")
            return int(r.json()["id"])

        else:
            print(
                f"❌ Failed to create supernet {network}: {r.status_code} {r.text}")
    except Exception as e:
        print(f"❌ Supernet creation error: {e}")
    return None


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
        "description": f"Auto-created VLAN {vlan_number}",
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


def create_subnet(subnet, location_id, vlan_id, description, vlan_number, master_subnet_id):
    payload = {
        "subnet": str(subnet.network_address),
        "mask": str(subnet.prefixlen),
        "description": description,
        "sectionId": SECTION_ID,
        "location": str(location_id),
        "vlanId": str(vlan_id),
        "masterSubnetId": master_subnet_id
    }
    try:
        r = requests.post(f"{API_BASE_URL}/subnets/",
                          headers=HEADERS, json=payload, verify=False, timeout=10)
        if r.status_code in [200, 201]:
            print(
                f"✅ Created {subnet} VLAN-ID {vlan_number} under supernet for {description}")
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


def seed_subnets():
    used_subnets = get_existing_subnets()
    vlans_per_rack = 5  # Adjust for 5-10 as needed

    for rack in racks:
        parent_network = ipaddress.ip_network(rack["network_block"])
        prefix = 25 if rack["size"] > 30 else 24

        # Get or create supernet for the location
        master_subnet_id = get_master_supernet_id(
            rack["network_block"], rack["name"])
        if not master_subnet_id:
            print(
                f"⚠️ Skipping rack {rack['name']} due to supernet creation failure.")
            continue

        subnets_to_create = find_next_free_subnets(
            parent_network, prefix, used_subnets, vlans_per_rack)

        for idx, subnet in enumerate(subnets_to_create):
            vlan_number = 2000 + rack["id"] * 10 + idx
            vlan_id = ensure_vlan_and_get_id(vlan_number, rack["name"])
            if not vlan_id:
                print(
                    f"⚠️ Skipping {rack['name']} VLAN {vlan_number} due to VLAN creation failure.")
                continue

            description = f"Auto created {rack['name']} VLAN {vlan_number}"
            if create_subnet(subnet, rack["location"], vlan_id, description, vlan_number, master_subnet_id):
                used_subnets.add(subnet)
            else:
                print(
                    f"❌ Failed to create subnet {subnet} for {rack['name']} VLAN {vlan_number}")


if __name__ == "__main__":
    seed_subnets()
