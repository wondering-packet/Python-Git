import csv
import requests
import json

# --- Config ---
with open("", "r") as f:
    secret = json.load(f)
    API_URL = secret["API_BASE_URL"]
    API_TOKEN = secret["API_TOKEN"]

CSV_FILE = "location_rename.csv"

# Disable SSL warnings (for self-signed certs)
requests.packages.urllib3.disable_warnings()

HEADERS = {
    "token": API_TOKEN,
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def load_rename_map(csv_path):
    rename_map = {}
    with open(csv_path, "r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            old_name = row["Name in phpIPAM"].strip()
            new_name = row["Name in DC switches"].strip()
            if old_name and new_name:
                rename_map[old_name] = new_name
    return rename_map


def get_all_locations():
    url = f"{API_URL}/locations/"
    response = requests.get(url, headers=HEADERS, verify=False)
    response.raise_for_status()
    return response.json().get("data", [])


def update_location_name(location_id, new_name):
    url = f"{API_URL}/locations/{location_id}/"
    payload = {"name": new_name}
    response = requests.patch(url, headers=HEADERS, json=payload, verify=False)
    return response.status_code == 200


def main():
    rename_map = load_rename_map(CSV_FILE)
    locations = get_all_locations()

    updated = 0
    skipped = 0

    for loc in locations:
        loc_id = loc["id"]
        current_name = loc["name"]

        if current_name in rename_map:
            new_name = rename_map[current_name]
            if current_name == new_name:
                print(f"[SKIP] '{current_name}' already has correct name.")
                skipped += 1
            else:
                success = update_location_name(loc_id, new_name)
                if success:
                    print(f"[OK] Renamed '{current_name}' → '{new_name}'")
                    updated += 1
                else:
                    print(f"[FAIL] Failed to update '{current_name}'")
        else:
            skipped += 1

    print(f"\nCompleted. Updated: {updated}, Skipped: {skipped}")


if __name__ == "__main__":
    main()
