import requests
import random
import time
import urllib3
import json

# Disable SSL warnings for lab
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("/automation/secrets/phpipam.json", "r") as f:
    secret = json.load(f)
    API_BASE_URL = secret["API_BASE_URL"]
    API_TOKEN = secret["API_TOKEN"]


# ====== DISABLE SSL WARNINGS ======
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ====== TEST FUNCTION ======


def test_phpipam_api():
    headers = {
        "token": API_TOKEN,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    url = f"{API_BASE_URL}/sections/"

    try:
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            print("[✅] API connection successful. Token and URL are valid.")
            print(f"Returned: {len(data.get('data', []))} sections found.")
        else:
            print("[⚠️] API responded but returned an error:")
            print(data)
    except requests.exceptions.RequestException as e:
        print("[❌] API connection failed:")
        print(e)


if __name__ == "__main__":
    test_phpipam_api()
