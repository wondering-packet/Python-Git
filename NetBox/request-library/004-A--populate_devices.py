import requests
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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


def create_if_not_exists(endpoint, payload, unique_field):
    resp = requests.get(f"{NETBOX_URL}api/{endpoint}/?{unique_field}={payload[unique_field]}",
                        headers=HEADERS, verify=VERIFY_SSL)
    resp.raise_for_status()
    if resp.json().get("results", []):
        print(
            f"⚠️ {payload[unique_field]} already exists at {endpoint}. Skipping.")
        return
    resp = requests.post(f"{NETBOX_URL}api/{endpoint}/",
                         headers=HEADERS, json=payload, verify=VERIFY_SSL)
    print(resp.text)
    resp.raise_for_status()
    print(f"✅ Created: {payload[unique_field]} at {endpoint}")


def main():
    # Manufacturer
    create_if_not_exists(
        "dcim/manufacturers",
        {"name": "Lab-Manufacturer", "slug": "lab-manufacturer"},
        "name"
    )

    # Device Types
    manufacturer_resp = requests.get(f"{NETBOX_URL}api/dcim/manufacturers/?name=Lab-Manufacturer",
                                     headers=HEADERS, verify=VERIFY_SSL)
    manufacturer_resp.raise_for_status()
    manufacturer_id = manufacturer_resp.json()["results"][0]["id"]

    create_if_not_exists(
        "dcim/device-types",
        {
            "model": "Lab-Switch-Type",
            "slug": "lab-switch-type",
            "manufacturer": manufacturer_id,
            "u_height": 1
        },
        "model"
    )

    create_if_not_exists(
        "dcim/device-types",
        {
            "model": "Lab-Router-Type",
            "slug": "lab-router-type",
            "manufacturer": manufacturer_id,
            "u_height": 1
        },
        "model"
    )

    # Device Roles
    create_if_not_exists(
        "dcim/device-roles",
        {"name": "Switch", "slug": "switch", "color": "00ff00"},
        "name"
    )
    create_if_not_exists(
        "dcim/device-roles",
        {"name": "Router", "slug": "router", "color": "0000ff"},
        "name"
    )


if __name__ == "__main__":
    main()
