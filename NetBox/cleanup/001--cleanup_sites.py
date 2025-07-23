import requests

# -------------------------------
# Config
# -------------------------------
NETBOX_URL = "https://netbox.intra.slicesoftech.net/"
API_TOKEN = "1323172662f7d6b44a48e5a4900d8dcf33328c2d"
VERIFY_SSL = False

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# -------------------------------
# Functions
# -------------------------------


def get_region_ids(region_names):
    region_ids = []
    for name in region_names:
        response = requests.get(
            f"{NETBOX_URL}api/dcim/regions/?name={name}", headers=HEADERS, verify=VERIFY_SSL)
        response.raise_for_status()
        results = response.json().get("results", [])
        if results:
            region_ids.append(results[0]["id"])
    return region_ids


def cleanup_sites(region_ids):
    for region_id in region_ids:
        response = requests.get(
            f"{NETBOX_URL}api/dcim/sites/?region_id={region_id}", headers=HEADERS, verify=VERIFY_SSL)
        response.raise_for_status()
        sites = response.json().get("results", [])
        for site in sites:
            site_id = site["id"]
            site_name = site["name"]
            del_resp = requests.delete(
                f"{NETBOX_URL}api/dcim/sites/{site_id}/", headers=HEADERS, verify=VERIFY_SSL)
            if del_resp.status_code == 204:
                print(f"🗑️ Deleted site: {site_name}")
            else:
                print(
                    f"⚠️ Failed to delete site: {site_name} | Status: {del_resp.status_code}")


def main():
    region_names = ["AMER", "AP", "EMEA"]
    region_ids = get_region_ids(region_names)
    cleanup_sites(region_ids)


if __name__ == "__main__":
    main()
