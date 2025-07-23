# run 004-A first.

import requests
import urllib3
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Config
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

VERIFY_SSL = False

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Helper Functions


def get_racks():
    racks = []
    limit = 1000
    offset = 0
    while True:
        resp = requests.get(f"{NETBOX_URL}api/dcim/racks/?limit={limit}&offset={offset}",
                            headers=HEADERS, verify=VERIFY_SSL)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        racks.extend(results)
        if not data.get("next"):
            break
        offset += limit
    return racks


def get_device_type_id(name):
    resp = requests.get(f"{NETBOX_URL}api/dcim/device-types/?model={name}",
                        headers=HEADERS, verify=VERIFY_SSL)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        raise Exception(f"Device Type '{name}' not found in NetBox.")
    return results[0]["id"]


def get_device_role_id(name):
    resp = requests.get(f"{NETBOX_URL}api/dcim/device-roles/?name={name}",
                        headers=HEADERS, verify=VERIFY_SSL)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        raise Exception(f"Device Role '{name}' not found in NetBox.")
    return results[0]["id"]


def create_device(name, device_type_id, device_role_id, site_id, rack_id, tenant_id, location_id):
    try:
        print(f"🔹 Checking device '{name}'...")
        resp = requests.get(f"{NETBOX_URL}api/dcim/devices/?name={name}",
                            headers=HEADERS, verify=VERIFY_SSL)
        resp.raise_for_status()

        if resp.json().get("results", []):
            print(f"⚠️ Device '{name}' already exists. Skipping.")
            return

        print(
            f"DEBUG: device_type_id={device_type_id}, device_role_id={device_role_id}, site_id={site_id}, rack_id={rack_id}, tenant_id={tenant_id}, location_id={location_id}")

        payload = {
            "name": name,
            "device_type": device_type_id,
            "role": device_role_id,
            "site": site_id,
            "rack": rack_id,
            "status": "active"
        }

        if tenant_id is not None:
            payload["tenant"] = tenant_id
        if location_id is not None:
            payload["location"] = location_id

        print(f"➡️ Creating device '{name}'...")
        resp = requests.post(f"{NETBOX_URL}api/dcim/devices/",
                             headers=HEADERS, json=payload, verify=VERIFY_SSL)
        print(resp.text)

        print(f"DEBUG: Payload Sent: {json.dumps(payload)}")
        print(f"DEBUG: Status Code: {resp.status_code}")
        print(f"DEBUG: Response: {resp.text}")

        resp.raise_for_status()
        print(f"✅ Created Device: {name}")
    except Exception as e:
        print(f"❌ Failed to create device '{name}': {e}")

# Main


def main():
    racks = get_racks()
    print(f"🔹 Found {len(racks)} racks to process for devices.")

    switch_type_id = get_device_type_id("Lab-Switch-Type")
    router_type_id = get_device_type_id("Lab-Router-Type")
    switch_role_id = get_device_role_id("Switch")
    router_role_id = get_device_role_id("Router")

    tasks = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        for rack in racks:
            rack_id = rack["id"]
            rack_name = rack["name"]
            site_id = rack["site"]["id"]
            location = rack.get("location")
            location_id = location["id"] if location else None
            tenant = rack.get("tenant")
            tenant_id = tenant["id"] if tenant else None

            # SW01
            device_name_sw = f"{rack_name}-SW01"
            tasks.append(
                executor.submit(create_device, device_name_sw, switch_type_id,
                                switch_role_id, site_id, rack_id, tenant_id, location_id)
            )

            # RTR01
            device_name_rtr = f"{rack_name}-RTR01"
            tasks.append(
                executor.submit(create_device, device_name_rtr, router_type_id,
                                router_role_id, site_id, rack_id, tenant_id, location_id)
            )

        for future in as_completed(tasks):
            _ = future.result()


if __name__ == "__main__":
    main()
