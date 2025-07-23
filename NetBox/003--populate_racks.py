import requests
import urllib3
import json

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


def get_locations():
    locations = []
    limit = 1000
    offset = 0
    while True:
        resp = requests.get(f"{NETBOX_URL}api/dcim/locations/?limit={limit}&offset={offset}",
                            headers=HEADERS, verify=VERIFY_SSL)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        locations.extend(results)
        if not data.get("next"):
            break
        offset += limit
    return locations


def create_rack(name, site_id, location_id, tenant_id):
    # Check if rack already exists
    resp = requests.get(
        f"{NETBOX_URL}api/dcim/racks/?name={name}", headers=HEADERS, verify=VERIFY_SSL)
    resp.raise_for_status()
    if resp.json().get("results", []):
        print(f"⚠️ Rack '{name}' already exists. Skipping.")
        return

    payload = {
        "name": name,
        "site": site_id,
        "location": location_id,
        "tenant": tenant_id,
        "u_height": 42,
        "width": 19,
        "type": "4-post",
        "serial": "",
        "asset_tag": ""
    }
    resp = requests.post(f"{NETBOX_URL}api/dcim/racks/",
                         headers=HEADERS, json=payload, verify=VERIFY_SSL)
    print(resp.text)  # Debug
    resp.raise_for_status()
    print(f"✅ Created Rack: {name}")

# Main


def main():
    locations = get_locations()
    for loc in locations:
        location_id = loc["id"]
        location_name = loc["name"]
        site_id = loc["site"]["id"]
        tenant = loc.get("tenant")
        tenant_id = tenant["id"] if tenant else None

        for idx in range(1, 3):  # RCK-01, RCK-02
            rack_name = f"{location_name}-RCK-{idx:02d}"
            create_rack(rack_name, site_id, location_id, tenant_id)


if __name__ == "__main__":
    main()
