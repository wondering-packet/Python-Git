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


def get_sites():
    sites = []
    limit = 1000
    offset = 0
    while True:
        resp = requests.get(f"{NETBOX_URL}api/dcim/sites/?limit={limit}&offset={offset}",
                            headers=HEADERS, verify=VERIFY_SSL)
        resp.raise_for_status()
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        sites.extend(results)
        if not data.get("next"):
            break
        offset += limit
    return sites


def create_location(name, site_id, tenant_id, description):
    # Check if location already exists
    resp = requests.get(
        f"{NETBOX_URL}api/dcim/locations/?name={name}", headers=HEADERS, verify=VERIFY_SSL)
    resp.raise_for_status()
    if resp.json().get("results", []):
        print(f"⚠️ Location '{name}' already exists. Skipping.")
        return

    payload = {
        "name": name,
        "slug": name.lower().replace("-", "_"),
        "site": site_id,
        "tenant": tenant_id,
        "description": description
    }
    resp = requests.post(f"{NETBOX_URL}api/dcim/locations/",
                         headers=HEADERS, json=payload, verify=VERIFY_SSL)
    print(resp.text)  # Debug
    resp.raise_for_status()
    print(f"✅ Created Location: {name}")


def get_tenant_id(tenant_name):
    resp = requests.get(
        f"{NETBOX_URL}api/tenancy/tenants/?name={tenant_name}", headers=HEADERS, verify=VERIFY_SSL)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if results:
        return results[0]["id"]
    else:
        raise Exception(f"Tenant '{tenant_name}' not found.")

# Main


def main():
    sites = get_sites()
    for site in sites:
        site_id = site["id"]
        site_name = site["name"]

        # Determine tenant based on site name
        if site_name.startswith("Lab-"):
            tenant_name = "WP-Lab"
        elif site_name.startswith("Retail-"):
            tenant_name = "WP-Retail"
        else:
            tenant_name = "WP-Corp"

        tenant_id = get_tenant_id(tenant_name)

        for loc_suffix in ["BR1", "BR2"]:
            loc_name = f"{site_name}-{loc_suffix}"
            description = f"{loc_name} in {site_name}"
            create_location(loc_name, site_id, tenant_id, description)


if __name__ == "__main__":
    main()
