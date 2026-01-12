import json
import pynetbox
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import csv
import keyring

API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")

# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

OUTPUT_CSV = r"c:\Temp\netbox_prefixes.csv"

def main():
    
    print("Retrieving prefixes from NetBox...")
    try:
        prefixes = nb.ipam.prefixes.all()
    except Exception as e:
        print(f"Failed to retrieve prefixes: {e}")
        return
    
    # Prepare data for CSV
    rows = []
    for prefix in prefixes:
        # prefix.prefix contains the full prefix string, e.g. "192.168.1.0/24"
        # We can split it to get network and prefix length
        try:
            network, prefix_length = prefix.prefix.split('/')
            rows.append({"Prefix": network, "Prefix Length": prefix_length})
        except Exception as e:
            print(f"Skipping invalid prefix {prefix.prefix}: {e}")
    
    # Write to CSV
    with open(OUTPUT_CSV, mode='w', newline='') as csvfile:
        fieldnames = ["Prefix", "Prefix Length"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Export complete: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()