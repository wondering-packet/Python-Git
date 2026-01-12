import requests
import json
import os
import urllib3
import keyring

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# API connection details
API_TOKEN = keyring.get_password("phpipam", "api_key")
API_BASE_URL = keyring.get_password("phpipam_url", "phpipam_url")
    
# Output file path
OUTPUT_DIR = r"c:\temp-python\phpipam\migration"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "phpipam_locations.json")

# Headers
HEADERS = {
    "token": API_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}

# Fetch locations


def fetch_locations():
    url = f"{API_BASE_URL}/tools/locations/"
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    return response.json()["data"]

# Save to JSON


def save_to_file(data):
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Exported {len(data)} locations to: {OUTPUT_FILE}")


if __name__ == "__main__":
    locations = fetch_locations()
    save_to_file(locations)