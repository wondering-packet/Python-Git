#!/usr/bin/env python

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

# Function to get all devices filtered by tag if needed


def get_devices():
    # Fetch all devices for which you want to create interfaces
    # You may add filters here if needed, e.g., tag='automation'
    return nb.dcim.devices.all()

# Function to get interfaces tagged with 'automation'


def get_automation_interfaces():
    # This now works since the 'automation' tag is created and attached
    return nb.dcim.interfaces.filter(tag='automation')

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
        for i in range(1, 25):
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

# Main logic


def main():
    automation_tag = nb.extras.tags.get(name="automation")
    automation_tag_id = automation_tag.id if automation_tag else None
    if not automation_tag_id:
        print("❌ 'automation' tag not found in NetBox. Please create it first.")
        exit(1)

    devices = get_devices()
    print(f"🔹 Found {len(devices)} devices to process.")

    for device in devices:
        create_interfaces_for_device(device, automation_tag_id)

    print("✅ Interface creation completed.")

    # Optional: list created interfaces tagged with 'automation'
    interfaces = get_automation_interfaces()
    print(f"🔹 Interfaces tagged with 'automation': {len(interfaces)}")
    for iface in interfaces:
        print(f"- {iface.device.name} {iface.name}")


if __name__ == "__main__":
    main()
