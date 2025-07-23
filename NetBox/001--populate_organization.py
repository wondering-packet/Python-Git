"""
Assumes you already have;

these Tenants (i created in GUI):
WP-Corp
WP-Retail
WP-Lab

these Regions (i created in GUI):
AMER
AP
EMEA
"""

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


def get_object_id(endpoint, name):
    response = requests.get(
        f"{NETBOX_URL}api/{endpoint}/?name={name}", headers=HEADERS, verify=VERIFY_SSL)
    response.raise_for_status()
    results = response.json().get("results", [])
    if results:
        return results[0]["id"]
    else:
        raise Exception(f"{name} not found at {endpoint}")


def create_site(name, region_id, tenant_id):
    # Check if site already exists
    check_resp = requests.get(
        f"{NETBOX_URL}api/dcim/sites/?name={name}", headers=HEADERS, verify=VERIFY_SSL)
    check_resp.raise_for_status()
    if check_resp.json().get("results", []):
        print(f"⚠️ Site '{name}' already exists. Skipping.")
        return

    payload = {
        "name": name,
        "slug": name.lower().replace("-", "_"),
        "region": region_id,
        "tenant": tenant_id,
        "description": f"Site for {name}"
    }
    response = requests.post(
        f"{NETBOX_URL}api/dcim/sites/", headers=HEADERS, json=payload, verify=VERIFY_SSL)
    print(response.text)  # Debug
    response.raise_for_status()
    print(f"✅ Created Site: {name}")

# Main Logic


def main():
    tenants = {
        "WP-Corp": "",
        "WP-Lab": "Lab-",
        "WP-Retail": "Retail-"
    }

    regions = {
        "AMER": ["AMER-E", "AMER-W"],
        "AP": [
            "AP-IN", "AP-SG", "AP-JP", "AP-KR", "AP-AU", "AP-NZ", "AP-TH", "AP-MY", "AP-ID", "AP-PH",
            "AP-VN", "AP-BD", "AP-LK", "AP-PK", "AP-NP", "AP-MM", "AP-KH", "AP-LA", "AP-BN", "AP-MN"
        ],
        "EMEA": [
            "EMEA-UK", "EMEA-DE", "EMEA-FR", "EMEA-IT", "EMEA-ES", "EMEA-NL", "EMEA-SE", "EMEA-NO", "EMEA-DK", "EMEA-FI",
            "EMEA-BE", "EMEA-CH", "EMEA-AT", "EMEA-PL", "EMEA-IE", "EMEA-PT", "EMEA-CZ", "EMEA-HU", "EMEA-GR", "EMEA-RO"
        ]
    }

    for tenant_name, prefix in tenants.items():
        tenant_id = get_object_id("tenancy/tenants", tenant_name)
        for region_name, site_list in regions.items():
            region_id = get_object_id("dcim/regions", region_name)
            for site in site_list:
                site_name = f"{prefix}{site}"
                create_site(site_name, region_id, tenant_id)


if __name__ == "__main__":
    main()
