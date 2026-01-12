'''
this script reparses the 401 file to add a role column.
this is the final output file which we will use to create subnets in 208.
again note that the 401 file already has duplicates removed.
'''
import pandas as pd
import re

# --- Configuration ---
INPUT_CSV = r"c:\temp\netbox\401-retail_filtered_subnets.csv"
OUTPUT_CSV = r"c:\temp\netbox\402-retail_filtered_subnets_with_roles.csv"

# Define role patterns (case-insensitive)
ROLE_PATTERNS = {
    "Data-Ascend": re.compile(r"data[-_ ]?ascend|data", re.IGNORECASE),
    "InetOnly": re.compile(r"inet[-_ ]?only|internet|intonly", re.IGNORECASE),
    "Management": re.compile(r"mgmt|management|managment", re.IGNORECASE),
    "Voice": re.compile(r"voice", re.IGNORECASE),
}

def determine_role(vlan_name):
    for role, pattern in ROLE_PATTERNS.items():
        if pattern.search(vlan_name):
            return role
    return "Unknown"

def main():
    try:
        df = pd.read_csv(INPUT_CSV, encoding="latin1")
    except Exception as e:
        print(f"[!] Failed to read CSV file: {e}")
        return

    if 'VLAN Name' not in df.columns:
        print("[!] 'VLAN Name' column not found in CSV.")
        return

    # Apply role detection
    df['Role'] = df['VLAN Name'].apply(lambda name: determine_role(str(name)))

    # Save output
    try:
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"[✔] Output saved to: {OUTPUT_CSV}")
    except Exception as e:
        print(f"[!] Failed to write output CSV: {e}")

if __name__ == "__main__":
    main()
