import requests
import json
import os
import urllib3

# Disable SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Constants
with open("/automation/secrets/phpipam.json", "r") as f:
    secret = json.load(f)
    API_BASE_URL = secret["API_BASE_URL"]
    API_TOKEN = secret["API_TOKEN"]
HEADERS = {
    "token": API_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}
OUT_DIR = "/automation/python-data/phpipam-backups"

# Ensure output directory exists
os.makedirs(OUT_DIR, exist_ok=True)


def fetch(endpoint):
    url = f"{API_BASE_URL}/{endpoint}/"
    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.RequestException as e:
        print(f"❌ Error fetching {endpoint}: {e}")
        return []


def save_json(data, filename):
    with open(os.path.join(OUT_DIR, filename), "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved: {filename} ({len(data)} records)")


def main():
    print("🔄 Exporting Subnets...")
    subnets = fetch("subnets")
    save_json(subnets, "subnets.json")

    print("🔄 Exporting VLANs...")
    vlans = fetch("vlan")
    save_json(vlans, "vlans.json")


if __name__ == "__main__":
    main()
