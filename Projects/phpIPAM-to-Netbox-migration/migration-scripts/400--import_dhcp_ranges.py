import json
import pynetbox
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import csv
import ipaddress
import keyring

API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")

# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

VERBOSE = True
TENANT_NAME = "Corporate"
CSV_FILE = r"c:\Temp\DHCP_Scopes_Report.csv"
PREFIX_CSV = r"c:\Temp\netbox_prefixes.csv"
FAILURE_LOG = r"c:\Temp\failed_dhcp_range_imports.json"

# === Init counters and failure log ===
success_count = 0
failure_count = 0
failures = []

# === Ensure tenant exists ===
def get_or_create_tenant(name):
    tenant = nb.tenancy.tenants.get(name=name)
    if tenant:
        return tenant.id
    return nb.tenancy.tenants.create({"name": name}).id

tenant_id = get_or_create_tenant(TENANT_NAME)

tag = nb.extras.tags.get(name="DHCP-Range")
tag_id = tag.id if tag else None

# === Load prefixes ===
prefixes = []
if not os.path.exists(PREFIX_CSV):
    print(f"❌ Prefix CSV file not found: {PREFIX_CSV}")
    exit(1)

with open(PREFIX_CSV, mode='r', newline='', encoding='utf-8-sig') as pfxfile:
    reader = csv.DictReader(pfxfile)
    for row in reader:
        try:
            cidr = f"{row['Prefix']}/{row['Prefix Length']}"
            prefixes.append(ipaddress.ip_network(cidr))
        except Exception as e:
            print(f"⚠️ Skipping invalid prefix row {row}: {e}")

# Sort prefixes for longest-match lookup
prefixes.sort(key=lambda p: p.prefixlen, reverse=True)

# === Process CSV ===
if not os.path.exists(CSV_FILE):
    print(f"❌ CSV file not found: {CSV_FILE}")
    exit(1)

with open(CSV_FILE, mode='r', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        row = {k.strip(): (v.strip() if v else '') for k, v in row.items()}
        name = row.get("Name")
        start_ip = row.get("Start address")
        end_ip = row.get("End address")

        if not all([name, start_ip, end_ip]):
            reason = "Missing required fields"
            print(f"⚠️ Skipping row: {reason} → {row}")
            failures.append({
                "name": name,
                "start_ip": start_ip,
                "end_ip": end_ip,
                "reason": reason
            })
            failure_count += 1
            continue

        if VERBOSE:
            print(f"➡️ Processing: {name} ({start_ip} - {end_ip})")

        # Single IP? → Create IP Address
        if start_ip == end_ip:
            try:
                ip_obj = ipaddress.ip_address(start_ip)
            except ValueError:
                reason = f"Invalid IP address: {start_ip}"
                print(f"❌ {reason}")
                failures.append({
                    "name": name,
                    "start_ip": start_ip,
                    "end_ip": end_ip,
                    "reason": reason
                })
                failure_count += 1
                continue

            # Longest match
            matched_prefix = None
            for p in prefixes:
                if ip_obj in p:
                    matched_prefix = p
                    break

            if not matched_prefix:
                reason = f"No matching prefix for {start_ip}"
                print(f"❌ {reason}")
                failures.append({
                    "name": name,
                    "start_ip": start_ip,
                    "end_ip": end_ip,
                    "reason": reason
                })
                failure_count += 1
                continue

            ip_with_prefix = f"{start_ip}/{matched_prefix.prefixlen}"

            # Check if already exists
            existing_ip = nb.ipam.ip_addresses.get(address=ip_with_prefix)
            if existing_ip:
                print(f"⚠️ IP already exists: {ip_with_prefix}")
                success_count += 1
                continue

            payload = {
                "address": ip_with_prefix,
                "status": "dhcp",
                "dns_name": name,
                "description": "DHCP range - Single IP. Managed by DHCP server.",
                "tenant": tenant_id,
                "tags": [tag_id] if tag_id else []
            }

            try:
                new_ip = nb.ipam.ip_addresses.create(payload)
                print(f"✅ Created IP: {new_ip.address}")
                success_count += 1
            except Exception as e:
                reason = str(e)
                print(f"❌ Failed to create IP {ip_with_prefix}: {reason}")
                failures.append({
                    "name": name,
                    "start_ip": start_ip,
                    "end_ip": end_ip,
                    "reason": reason
                })
                failure_count += 1

            continue  # Done with this row

        # Else → Create IP Range
        existing_range = nb.ipam.ip_ranges.filter(start_address=start_ip, end_address=end_ip)
        if existing_range:
            print(f"⚠️ Range already exists: {start_ip} - {end_ip}")
            success_count += 1
            continue

        payload = {
            "start_address": start_ip,
            "end_address": end_ip,
            "description": f"DHCP Range for {name}. Managed by DHCP server.",
            "tags": [tag_id] if tag_id else [],
            "tenant": tenant_id,
            "mark_populated": "true",
            "mark_utilized": "true"
        }

        try:
            new_range = nb.ipam.ip_ranges.create(payload)
            print(f"✅ Created Range: {new_range.start_address} - {new_range.end_address}")
            success_count += 1
        except Exception as e:
            reason = str(e)
            print(f"❌ Failed to create range {start_ip} - {end_ip}: {reason}")
            failures.append({
                "name": name,
                "start_ip": start_ip,
                "end_ip": end_ip,
                "reason": reason
            })
            failure_count += 1

# === Write failures to JSON file ===
if failures:
    with open(FAILURE_LOG, "w", encoding='utf-8') as f:
        json.dump(failures, f, indent=4)
    print(f"\n❌ {failure_count} failures logged to: {FAILURE_LOG}")
else:
    print("\n✅ No failures encountered.")

# === Final Summary ===
print(f"\n✅ Summary:")
print(f"    Successful (added or existed): {success_count}")
print(f"    Failed: {failure_count}")
