# 202--migrate_subnets.py

import json
import pynetbox
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False


# File paths
SUBNETS_FILE = "/automation/python-data/phpipam-backups/subnets.json"
VLANS_FILE = "/automation/python-data/phpipam-backups/vlans.json"

TENANT_NAME = "WP-Corp"

# Ensure tenant exists


def get_or_create_tenant(name):
    tenant = nb.tenancy.tenants.get(name=name)
    if tenant:
        return tenant.id
    return nb.tenancy.tenants.create({"name": name}).id


tenant_id = get_or_create_tenant(TENANT_NAME)

tag = nb.extras.tags.get(name="phpipam-migrated")
tag_id = tag.id

# Load VLANs
all_vlans = {}
with open(VLANS_FILE, "r") as f:
    vlans = json.load(f)
    for vlan in vlans:
        all_vlans[vlan.get("vlanId", "0")] = vlan.get("number", "0")

# Load Subnets
with open(SUBNETS_FILE, "r") as f:
    subnets = json.load(f)


def get_site_id_by_name(site_name):
    site = nb.dcim.sites.get(name=site_name)
    if site is None:
        print("Site not found")
        return
    else:
        return site.id


def get_vlan_id_by_number(vlan_number):
    vlan = nb.ipam.vlans.get(vid=vlan_number)
    if vlan is None:
        print("Vlan not found")
        return
    else:
        return vlan.id


# Create subnets
for subnet in subnets:
    prefix = f"{subnet['subnet']}/{subnet['mask']}"
    location = subnet["location"]
    vlan_id = subnet["vlanId"]
    prefix_exists = nb.ipam.prefixes.get(prefix=prefix)
    if prefix_exists:
        print(f"Skipping: {prefix} (already exists)")
        continue

    if location and vlan_id:
        site_name = location["name"]
        vlan_number = all_vlans[vlan_id]
        netbox_vlan_id = get_vlan_id_by_number(vlan_number)
        site_id = get_site_id_by_name(site_name)
        nb_prefix = nb.ipam.prefixes.create({
            "prefix": prefix,
            "description": subnet.get("description", ""),
            "tenant": tenant_id,
            "tags": [tag_id],
            "scope_type": "dcim.site",
            "scope_id": site_id,
            "vlan": netbox_vlan_id
        })
        print(f"Created prefix: {prefix} in {site_id} with vlan {vlan_id}")

    elif location:
        site_name = location["name"]
        site_id = get_site_id_by_name(site_name)
        nb_prefix = nb.ipam.prefixes.create({
            "prefix": prefix,
            "description": subnet.get("description", ""),
            "tenant": tenant_id,
            "tags": [tag_id],
            "scope_type": "dcim.site",
            "scope_id": site_id
        })
        print(f"Created prefix: {prefix} in {site_id}")
    else:
        nb_prefix = nb.ipam.prefixes.create({
            "prefix": prefix,
            "description": subnet.get("description", ""),
            "tenant": tenant_id,
            "tags": [tag_id]
        })
        print(f"Created prefix: {prefix}")
