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


def get_devices():
    devices = []
    limit = 1000
    offset = 0
    while True:
        resp = requests.get(f"{NETBOX_URL}api/dcim/devices/?limit={limit}&offset={offset}",
                            headers=HEADERS, verify=VERIFY_SSL)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        devices.extend(results)
        if not data.get("next"):
            break
        offset += limit
    return devices


def interface_exists(device_id, name):
    resp = requests.get(f"{NETBOX_URL}api/dcim/interfaces/?device_id={device_id}&name={name}",
                        headers=HEADERS, verify=VERIFY_SSL)
    resp.raise_for_status()
    return bool(resp.json().get("results", []))


def create_interface(device, name, interface_type="1000base-t", mgmt_only=False):
    try:
        device_id = device["id"]
        device_name = device["name"]

        if interface_exists(device_id, name):
            print(
                f"⚠️ Interface '{name}' on '{device_name}' already exists. Skipping.")
            return

        payload = {
            "device": device_id,
            "name": name,
            "type": interface_type,
            "enabled": True,
            "mgmt_only": mgmt_only,
            "description": f"{device_name} {name}"
        }

        print(f"➡️ Creating interface '{name}' on '{device_name}'...")
        resp = requests.post(f"{NETBOX_URL}api/dcim/interfaces/",
                             headers=HEADERS, json=payload, verify=VERIFY_SSL)
        resp.raise_for_status()
        print(f"✅ Created interface '{name}' on '{device_name}'.")
    except Exception as e:
        print(f"❌ Failed to create interface '{name}' on '{device_name}': {e}")


def main():
    devices = get_devices()
    print(f"🔹 Found {len(devices)} devices to process for interfaces.")

    tasks = []
    with ThreadPoolExecutor(max_workers=16) as executor:
        for device in devices:
            device_name = device["name"]

            # Mgmt0 for all devices
            tasks.append(executor.submit(create_interface, device,
                         "Mgmt0", "1000base-t", mgmt_only=True))

            if "RTR" in device_name:
                # Routers: Gig0/0 - Gig0/3
                for idx in range(4):
                    intf_name = f"Gig0/{idx}"
                    tasks.append(executor.submit(
                        create_interface, device, intf_name))

            elif "SW" in device_name:
                # Switches: Gig0/1 - Gig0/24
                for idx in range(1, 25):
                    intf_name = f"Gig0/{idx}"
                    tasks.append(executor.submit(
                        create_interface, device, intf_name))

        for future in as_completed(tasks):
            _ = future.result()


if __name__ == "__main__":
    main()
