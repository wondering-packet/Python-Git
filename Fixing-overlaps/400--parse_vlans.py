'''
this script processes 2 csv files: retail_supernets & retail_vlans.
both of these files have duplicate entries.
what this script does is - it only keeps the vlans which belong to at least one supernet.
so the output list is basically a filtered list of retail_vlans.
'''
import pandas as pd
import ipaddress
import csv

# --- Input files ---
SUPERNET_FILE = r"c:\temp\netbox\retail_supernets.csv"
VLAN_FILE = r"c:\temp\netbox\retail_vlans.csv"
OUTPUT_FILE = r"c:\temp\netbox\400-retail_filtered_vlans.csv"
LOG_FILE = r"c:\temp\netbox\400-logs-retail_unmatched_vlans.log"

# --- Load Supernet Data ---
supernet_df = pd.read_csv(SUPERNET_FILE, encoding='latin1')
supernet_df.dropna(subset=["Supernet (/24)"], inplace=True)

# Convert supernet strings to IPv4Network objects
supernets = []
for _, row in supernet_df.iterrows():
    try:
        net = ipaddress.IPv4Network(row["Supernet (/24)"].strip())
        supernets.append(net)
    except Exception as e:
        print(f"[!] Invalid supernet '{row['Supernet (/24)']}': {e}")

# --- Load VLAN Data ---
vlan_df = pd.read_csv(VLAN_FILE, encoding='latin1')

# --- Output lists ---
valid_rows = []
invalid_rows = []

# --- Check VLAN IPs ---
for _, row in vlan_df.iterrows():
    vlan_ip_raw = str(row.get("VLAN Interface IP", "")).strip()
    matched = False

    try:
        # Parse interface IP with subnet
        interface = ipaddress.IPv4Interface(vlan_ip_raw)
        ip = interface.ip
        vlan_network_id = str(interface.network)  # This gives you "10.x.x.0/24"

        # Check if IP is inside any supernet
        for supernet in supernets:
            if ip in supernet:
                valid_rows.append({
                    "Network Name": row["Network Name"],
                    "VLAN ID": row["VLAN ID"],
                    "VLAN Name": row["VLAN Name"],
                    "VLAN Network ID": vlan_network_id
                })
                matched = True
                break

        if not matched:
            invalid_rows.append({
                "Network Name": row["Network Name"],
                "VLAN ID": row["VLAN ID"],
                "VLAN Name": row["VLAN Name"],
                "VLAN Interface IP": vlan_ip_raw
            })

    except Exception as e:
        invalid_rows.append({
            "Network Name": row.get("Network Name", "UNKNOWN"),
            "VLAN ID": row.get("VLAN ID", "UNKNOWN"),
            "VLAN Name": row.get("VLAN Name", "UNKNOWN"),
            "VLAN Interface IP": vlan_ip_raw,
            "Error": f"Invalid IP format: {e}"
        })

# --- Write valid VLANs to output CSV ---
with open(OUTPUT_FILE, "w", newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["Network Name", "VLAN ID", "VLAN Name", "VLAN Network ID"])
    writer.writeheader()
    writer.writerows(valid_rows)

print(f"[+] Created filtered VLAN CSV: {OUTPUT_FILE} ({len(valid_rows)} entries)")

# --- Write unmatched entries to log ---
with open(LOG_FILE, "w", encoding="utf-8") as logfile:
    logfile.write("⚠️ VLAN Interface IPs that did NOT match any Supernet:\n\n")
    for entry in invalid_rows:
        line = f"- VLAN '{entry['VLAN Name']}' (ID: {entry['VLAN ID']}), Network: '{entry['Network Name']}', IP: {entry['VLAN Interface IP']}"
        if "Error" in entry:
            line += f" --> Error: {entry['Error']}"
        logfile.write(line + "\n")

print(f"[!] Logged {len(invalid_rows)} unmatched VLANs to: {LOG_FILE}")
