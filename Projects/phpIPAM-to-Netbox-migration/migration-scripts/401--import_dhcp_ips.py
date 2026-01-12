import csv
import ipaddress
import pynetbox
import json
import keyring
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === CONFIGURATION ===
API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")

# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

RESERVATION_CSV = r"c:\Temp\DHCP_Reservations_Report.csv"
PREFIX_CSV = r"c:\Temp\netbox_prefixes.csv"

# === Load Prefixes ===
prefixes = []

print("Loading prefixes...")
with open(PREFIX_CSV, mode='r', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            cidr = f"{row['Prefix']}/{row['Prefix Length']}"
            prefixes.append(ipaddress.ip_network(cidr))
        except Exception as e:
            print(f"⚠️ Skipping invalid prefix row: {row} - {e}")

# Sort prefixes by prefix length descending for longest-match lookup
prefixes.sort(key=lambda p: p.prefixlen, reverse=True)

# Ensure tenant exists
TENANT_NAME = "Corporate"

def get_or_create_tenant(name):
    tenant = nb.tenancy.tenants.get(name=name)
    if tenant:
        return tenant.id
    return nb.tenancy.tenants.create({"name": name}).id


tenant_id = get_or_create_tenant(TENANT_NAME)

tag = nb.extras.tags.get(name="DHCP-Reserved")
tag_id = tag.id

# === Load DHCP Reservations ===
print("Loading DHCP reservations...")
with open(RESERVATION_CSV, mode='r', newline='', encoding='utf-8-sig') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        hostname = row.get("Hostname", "").strip()
        mac = row.get("MAC", "").strip()
        ip_str = row.get("IP", "").strip()

        if not (hostname and mac and ip_str):
            print(f"⚠️ Skipping incomplete row: {row}")
            continue

        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            print(f"⚠️ Invalid IP address: {ip_str}")
            continue

        # Find longest matching prefix
        matched_prefix = None
        for p in prefixes:
            if ip_obj in p:
                matched_prefix = p
                break

        if not matched_prefix:
            print(f"❌ No matching prefix found for {ip_str}. Skipping.")
            continue

        ip_with_prefix = f"{ip_str}/{matched_prefix.prefixlen}"

        # Check if IP already exists in NetBox
        existing_ip = nb.ipam.ip_addresses.get(address=ip_with_prefix)
        if existing_ip:
            print(f"⚠️ IP {ip_with_prefix} already exists in NetBox. Skipping.")
            continue

        # Build payload
        payload = {
            "address": ip_with_prefix,
            "status": "dhcp",  # You can verify allowed statuses in your NetBox instance
            "dns_name": mac,
            "description": hostname,
            "tags": [tag_id],
            "tenant": tenant_id
        }

        try:
            created = nb.ipam.ip_addresses.create(payload)
            print(f"✅ Created IP: {created.address} | Hostname: {hostname} | MAC: {mac}")
        except Exception as e:
            print(f"❌ Failed to create IP {ip_with_prefix}: {e}")
