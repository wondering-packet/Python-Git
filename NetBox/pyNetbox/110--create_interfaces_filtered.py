# used chatgpt to quickly build this simple script.
# this script creates 4+1(mgmt) interfaces for routers & 24+1(mgmt) interfaces for switches.
# i am using it to feed in dummy data.

import pynetbox
import json
import urllib3

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load credentials and NetBox URL
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False  # Ignore SSL verification


def get_site_id_by_name(site_name):
    site = nb.dcim.sites.get(name=site_name)
    if site is None:
        print("Site not found")
        return
    else:
        return site.id

# Function to get all devices for a site filtered by tag if needed


def get_devices(site_name):
    # Fetch all devices for which you want to create interfaces
    # You may add filters here if needed, e.g., tag='automation'
    site_id = get_site_id_by_name(site_name)
    return nb.dcim.devices.filter(site_id=site_id)


# Function to create interfaces on a device


def create_interfaces_for_device(device, automation_tag_id):
    # Create Mgmt0 if it doesn't exist
    if not nb.dcim.interfaces.filter(device_id=device.id, name="Mgmt0"):
        nb.dcim.interfaces.create({
            "device": device.id,
            "name": "Mgmt0",
            "type": "1000base-t",
            "enabled": True,
            "description": f"{device.name} Mgmt0",
            # Fetch automation tag id once before calling this function
            "tags": [automation_tag_id],

        })
        print(f"✅ Created Mgmt0 on {device.name}")

    if "RTR" in device.name:
        # Create 4 routed interfaces
        for i in range(1, 5):
            iface_name = f"Gig0/{i}"
            # Check if interface already exists
            existing = nb.dcim.interfaces.filter(
                device_id=device.id, name=iface_name)
            if not existing:
                nb.dcim.interfaces.create({
                    "device": device.id,
                    "name": iface_name,
                    "type": "1000base-t",
                    "enabled": True,
                    "description": f"{device.name} {iface_name}",
                    "tags": [automation_tag_id]
                })
                print(f"✅ Created {iface_name} on {device.name}")

    elif "SW" in device.name:
        # Create 24 switchport interfaces
        for i in range(1, 16):
            iface_name = f"Gig0/{i}"
            # Check if interface already exists
            existing = nb.dcim.interfaces.filter(
                device_id=device.id, name=iface_name)
            if not existing:
                nb.dcim.interfaces.create({
                    "device": device.id,
                    "name": iface_name,
                    "type": "1000base-t",
                    "enabled": True,
                    "description": f"{device.name} {iface_name}",
                    "tags": [automation_tag_id]
                })
                print(f"✅ Created {iface_name} on {device.name}")

    elif "FW" in device.name:
        # Create 24 switchport interfaces
        for i in range(1, 8):
            iface_name = f"Gig0/{i}"
            # Check if interface already exists
            existing = nb.dcim.interfaces.filter(
                device_id=device.id, name=iface_name)
            if not existing:
                nb.dcim.interfaces.create({
                    "device": device.id,
                    "name": iface_name,
                    "type": "1000base-t",
                    "enabled": True,
                    "description": f"{device.name} {iface_name}",
                    "tags": [automation_tag_id]
                })
                print(f"✅ Created {iface_name} on {device.name}")

    # you can continue to do this for other device types you may have.

# Main logic


def main():
    automation_tag = nb.extras.tags.get(name="automation")
    automation_tag_id = automation_tag.id if automation_tag else None
    if not automation_tag_id:
        print("❌ 'automation' tag not found in NetBox. Please create it first.")
        exit(1)

    site_name = "AMER-E"
    devices = get_devices(site_name)
    print(f"🔹 Found {len(devices)} devices to process.")

    for device in devices:
        create_interfaces_for_device(device, automation_tag_id)

    print("✅ Interface creation completed.")


if __name__ == "__main__":
    main()
