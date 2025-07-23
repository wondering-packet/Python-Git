import requests
import random
import time
import urllib3

# Disable SSL warnings for lab
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_BASE_URL = "https://URL_ADDRESS/api/API_ID"
API_TOKEN = "TOKEN"

# Racks data
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

device_types = [1, 2, 3, 5]
device_type_shortnames = {1: "SW", 2: "RT", 3: "FW", 5: "WL"}

# Per-location /24 blocks
location_blocks = {
    1: "10.10.1",
    2: "10.20.1",
    3: "10.30.1",
    4: "10.40.1",
    5: "10.50.1",
    6: "10.60.1",
    7: "10.70.1",
    8: "10.80.1",
    9: "10.90.1",
    10: "10.100.1",
    11: "10.110.1",
    12: "10.120.1",
    13: "10.130.1",
    14: "10.140.1",
    15: "10.150.1",
    16: "10.160.1",
}


# IP trackers
location_ip_tracker = {loc: 10 for loc in location_blocks.keys()}

# Rack usage tracker
rack_usage = {rack["id"]: [] for rack in racks}


def find_position(rack_id, device_size, rack_size):
    occupied = rack_usage[rack_id]
    for pos in range(1, rack_size - device_size + 2):
        if all(u not in occupied for u in range(pos, pos + device_size)):
            for u in range(pos, pos + device_size):
                occupied.append(u)
            return pos
    return None


def add_device(session, device_data):
    url = f"{API_BASE_URL}/devices/"
    headers = {"token": API_TOKEN, "Content-Type": "application/json",
               "Accept": "application/json"}
    try:
        response = session.post(url, headers=headers,
                                json=device_data, verify=False, timeout=10)
        if response.status_code == 201:
            return True, response.json()
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)


def seed_devices(num_devices=1200):
    session = requests.Session()
    success_count = failure_count = skipped_count = 0

    for i in range(1, num_devices + 1):
        device_added = False

        racks_shuffled = racks[:]
        random.shuffle(racks_shuffled)

        for rack in racks_shuffled:
            rack_id = rack["id"]
            rack_size = rack["size"]
            loc_id = rack["location"]

            device_type = random.choice(device_types)
            device_shortname = device_type_shortnames.get(device_type, "UN")
            device_u_size = random.randint(1, 3)

            pos = find_position(rack_id, device_u_size, rack_size)
            if pos is None:
                continue

            ip_octet = location_ip_tracker[loc_id]
            if ip_octet >= 250:
                continue

            ip_addr = f"{location_blocks[loc_id]}.{ip_octet}"
            location_ip_tracker[loc_id] += 1

            device_name = f"{rack['name']}-{device_shortname}-{i:04d}"
            payload = {
                "hostname": device_name,
                "ip_addr": ip_addr,
                "type": device_type,
                "location": loc_id,
                "rack": rack_id,
                "rack_start": pos,
                "rack_size": device_u_size,
                "description": f"Auto created by API automation, device {i}",
                "sections": [1, 2, 3]
            }

            success, result = add_device(session, payload)
            if success:
                success_count += 1
                print(
                    f"✅ [{i}/{num_devices}] Added {device_name} ({ip_addr}), {device_u_size}U at {pos}")
            else:
                failure_count += 1
                print(
                    f"❌ [{i}/{num_devices}] Failed to add {device_name}. Error: {result}")

            device_added = True
            break

        if not device_added:
            skipped_count += 1
            print(f"⚠️ Skipped device {i}: No available rack space or IPs.")

        if i % 50 == 0:
            print(f"🌿 Progress: {i}/{num_devices} devices seeded.")
            time.sleep(1)

    print(
        f"\n🎯 Complete: {success_count} succeeded, {failure_count} failed, {skipped_count} skipped out of {num_devices} devices.")


if __name__ == "__main__":
    seed_devices(1200)
