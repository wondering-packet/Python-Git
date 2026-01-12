import json

# Load JSON data from files
with open(r'c:\temp-python\phpipam\new_vlan-usdc1.json') as f:
    dc1_records = json.load(f)

with open(r'c:\temp-python\phpipam\new_vlan-usdc2.json') as f:
    dc2_records = json.load(f)

with open(r'c:\temp-python\phpipam\new_vlans.json') as f:
    vlan_records = json.load(f)

# Create lookup sets for DC1 and DC2
dc1_keys = {(str(rec["number"]), rec["site_name"]) for rec in dc1_records}
dc2_keys = {(str(rec["number"]), rec["site_name"]) for rec in dc2_records}

# Prepare filtered lists
dc1_filtered = []
dc2_filtered = []
unknown_filtered = []

dc1_counter = 0
dc2_counter = 0
unknown_counter = 0
total_counter = 0

for vlan in vlan_records:
    total_counter+=1
    key = (str(vlan["number"]), vlan["site_name"])
    if key in dc1_keys:
        dc1_filtered.append(vlan)
        dc1_counter+=1
    elif key in dc2_keys:
        dc2_filtered.append(vlan)
        dc2_counter+=1
    elif vlan["site_name"] != "Default":
        unknown_filtered.append(vlan)
        unknown_counter+=1

# Write filtered results to JSON files
with open(r"c:\temp-python\phpipam\dc1-filtered.json", "w") as f:
    json.dump(dc1_filtered, f, indent=2)

with open(r"c:\temp-python\phpipam\dc2-filtered.json", "w") as f:
    json.dump(dc2_filtered, f, indent=2)

with open(r"c:\temp-python\phpipam\unknown-filtered.json", "w") as f:
    json.dump(unknown_filtered, f, indent=2)

print("Filtering complete. Files saved.")
print(f"\nCounters:\nDC1: {dc1_counter}\nDC2: {dc2_counter}\nUnknown: {unknown_counter}")