# I had chatgpt help me out with this script.
# It's not exactly clean.
# what it does:
# create new devices for each device types (randomly)
#   with random rack selection.
#   with random rack postion & face.
#   within AMER-E site.
#   with the provided lat/long for GPS location.
# It's filling the racks to 80% utilization.

import pynetbox
import random
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

# Constants
DEVICE_TYPES = {
    "ASR1002-X": {"role": "Router", "u_height": 2},
    "C9200L-24T-4G-E": {"role": "Access Switch", "u_height": 1},
    "Catalyst 9404R": {"role": "Core Switch", "u_height": 7},
    "Aruba 2530-48G-PoE+": {"role": "Access Switch", "u_height": 1},
    "PA-3440": {"role": "Firewall", "u_height": 2},
}

ROLE_SHORT = {
    "Router": "RTR",
    "Access Switch": "ASW",
    "Core Switch": "CSW",
    "Firewall": "FW",
}

FACE = "front"
MAX_RACK_UNITS = 42
MIN_OCCUPANCY = 34  # ~80%

TENANT_NAME = "WP-Corp"
TENANT = nb.tenancy.tenants.get(name=TENANT_NAME)

TAG = nb.extras.tags.get(name="automation")

# Predefined lat/lon per site
SITE_LOCATIONS = {
    "BR1": {"lat": 40.7128, "lon": -74.0060},   # New York
    "BR2": {"lat": 42.3601, "lon": -71.0589},   # Boston
    "HQ":  {"lat": 39.9526, "lon": -75.1652},   # Philadelphia
}

# Per-role counters per site
device_counters = {
    site: {role: 1 for role in ROLE_SHORT.values()} for site in SITE_LOCATIONS
}

# Track current rack occupancy: {rack_id: current U height used}
rack_occupancy = {}

# Helper: Get site from rack name (e.g., AMER-E-BR1-RCK01 → BR1)


def extract_site_from_rack(rack_name):
    return rack_name.split("-")[2]

# Helper: Generate device name


def generate_device_name(site_code, role_key):
    counter = device_counters[site_code][role_key]
    name = f"AMER-E-{site_code}-{role_key}{counter:02}"
    device_counters[site_code][role_key] += 1
    return name

# Main


def populate_rack(rack):
    rack_id = rack.id
    rack_name = rack.name
    site_code = extract_site_from_rack(rack_name)

    rack_occupancy.setdefault(rack_id, 0)
    used_units = 0
    devices_to_create = []

    while used_units < MIN_OCCUPANCY:
        dtype_name = random.choice(list(DEVICE_TYPES.keys()))
        dtype = nb.dcim.device_types.get(model=dtype_name)
        if not dtype:
            print(f"❌ Device type not found in NetBox: {dtype_name}")
            continue

        u_height = DEVICE_TYPES[dtype_name]["u_height"]
        role_full = DEVICE_TYPES[dtype_name]["role"]
        role_short = ROLE_SHORT[role_full]
        role_obj = nb.dcim.device_roles.get(name=role_full)
        if not role_obj:
            print(f"❌ Role not found: {role_full}")
            continue

        if rack_occupancy[rack_id] + u_height > MAX_RACK_UNITS:
            break

        position = MAX_RACK_UNITS - rack_occupancy[rack_id] - u_height + 1
        device_name = generate_device_name(site_code, role_short)
        lat = SITE_LOCATIONS[site_code]["lat"]
        lon = SITE_LOCATIONS[site_code]["lon"]

        device = {
            "name": device_name,
            "device_type": dtype.id,
            "role": role_obj.id,
            "site": rack.site.id,
            "location": rack.location.id if rack.location else None,
            "rack": rack.id,
            "position": position,
            "face": FACE,
            "status": "active",
            "tenant": TENANT.id if TENANT else None,
            "serial": f"AUTO-{random.randint(100000, 999999)}",
            "latitude": lat,
            "longitude": lon,
            "tags": [TAG.id] if TAG else [],
            "description": f"Auto-populated {role_full}",
        }

        try:
            nb.dcim.devices.create(device)
            print(f"✅ Created {device_name} in {rack_name} at U{position}")
            rack_occupancy[rack_id] += u_height
            used_units += u_height
        except Exception as e:
            print(f"❌ Error creating {device_name} in {rack_name}: {e}")

# we cannot directly pass a site name; we need site ID.


def get_site_id_by_name(site_name):
    site = nb.dcim.sites.get(name=site_name)
    if site is None:
        print("Site not found")
        return
    else:
        return site.id

# Run for all racks under AMER-E


def main():
    site_name = "AMER-E"    # define your own site here.
    site_id = get_site_id_by_name(site_name)
    racks = nb.dcim.racks.filter(site_id=site_id)
    for rack in racks:
        print(f"\n📦 Populating rack: {rack.name}")
        populate_rack(rack)


if __name__ == "__main__":
    main()
