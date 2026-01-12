import json
import csv

# Load JSON data from files
with open(r'c:\temp-python\phpipam\new_vlan-usdc1.json') as f:
    dc1_records = json.load(f)

with open(r'c:\temp-python\phpipam\new_vlan-usdc2.json') as f:
    dc2_records = json.load(f)

with open(r'c:\temp-python\phpipam\new_vlans.json') as f:
    vlan_records = json.load(f)

# Create lookup dictionaries
dc1_lookup = {(str(rec["number"]), rec["site_name"]): rec["name"] for rec in dc1_records}
dc2_lookup = {(str(rec["number"]), rec["site_name"]): rec["name"] for rec in dc2_records}

# Prepare output list
combined_table = []
unknown_filtered = []

for vlan in vlan_records:
    number = str(vlan["number"])
    site = vlan["site_name"]
    key = (number, site)

    if key in dc1_lookup:
        combined_table.append([number, site, dc1_lookup[key], vlan["name"]])
    elif key in dc2_lookup:
        combined_table.append([number, site, dc2_lookup[key], vlan["name"]])
    elif site != "Default":
        unknown_filtered.append(vlan)

# Write combined CSV
with open(r"c:\temp-python\phpipam\combined-result.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Number", "Site Name", "Name in DC switches", "Name in phpIPAM"])
    writer.writerows(combined_table)

# Write unknown entries to JSON
with open(r"c:\temp-python\phpipam\unknown-filtered.json", "w") as f:
    json.dump(unknown_filtered, f, indent=2)

# Summary
print("✅ Combined CSV export complete:")
print(f" - combined-result.csv ({len(combined_table)} entries)")
print(f" - unknown-filtered.json ({len(unknown_filtered)} unknown entries)")
