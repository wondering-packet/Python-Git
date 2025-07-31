import requests
import urllib3
import json
import os

# Suppress SSL warnings for self-signed certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API connection details
with open("/automation/secrets/phpipam.json", "r") as f:
    secret = json.load(f)
    API_BASE_URL = secret["API_BASE_URL"]
    API_TOKEN = secret["API_TOKEN"]

OUTPUT_DIR = "/automation/python-data/phpipam-backups"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "phpipam_ip_addresses.json")

# Static tag-to-status mapping from your environment
TAG_ID_TO_STATUS = {
    1: "deprecated",
    2: "active",
    3: "reserved",
    4: "dhcp"
}

url = f"{API_BASE_URL}/addresses/"
HEADERS = {
    "token": API_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def get_all_addresses():

    try:
        response = requests.get(url, headers=HEADERS, verify=False)
        response.raise_for_status()
        data = response.json().get("data", [])

        # Annotate each address with readable status
        for entry in data:
            tag_id = entry.get("tag")
            entry["status"] = TAG_ID_TO_STATUS.get(tag_id, "Unknown")

        return data

    except requests.RequestException as e:
        print(f"Error fetching addresses: {e}")
        return []


def save_to_file(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(data)} IP addresses to {filename}")


if __name__ == "__main__":
    addresses = get_all_addresses()
    save_to_file(addresses, OUTPUT_FILE)
