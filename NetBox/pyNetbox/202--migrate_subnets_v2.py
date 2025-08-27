# 202--migrate_subnets.py

import json
import pynetbox
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from threading import Lock

with open(r"c:\temp-python\phpipam\netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False


# File paths
SUBNETS_FILE = r"c:\temp-python\phpipam\migration\subnets.json"
VLANS_FILE = r"c:\temp-python\phpipam\migration\vlans.json"

TENANT_NAME = "Corporate"

# Ensure tenant exists
def get_or_create_tenant(name):
    tenant = nb.tenancy.tenants.get(name=name)
    if tenant:
        return tenant.id
    return nb.tenancy.tenants.create({"name": name}).id


tenant_id = get_or_create_tenant(TENANT_NAME)

tag = nb.extras.tags.get(name="phpipam-migrated")
tag_id = tag.id

# counter
counter_lock = Lock()
prefix_counter = Counter()
total_processed = 0

# Load VLANs
all_vlans = {}
with open(VLANS_FILE, "r") as f:
    vlans = json.load(f)
    for vlan in vlans:
        all_vlans[vlan.get("vlanId")] = vlan.get("number")

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

def get_vlan_id_by_number(ipam_vid, prefix):
    # Pull all VLANs (optionally, filter by site/group if needed)
    all_vlans = nb.ipam.vlans.all()

    # Filter manually based on the custom field
    for vlan in all_vlans:
        if vlan.custom_fields.get("IPAM_vid") == int(ipam_vid):
            print(f"Found VLAN: {vlan.name} (VID: {vlan.vid})")
            return vlan.id

    print(f"VLAN not found for prefix, likely default VLAN. prefix: {prefix} & IPAM_vid: {ipam_vid}")
    return None


# Create subnets
def create_prefix(subnet):
    prefix = f"{subnet['subnet']}/{subnet['mask']}"
    location = subnet["location"]
    ipam_id = subnet["vlanId"]
    prefix_exists = nb.ipam.prefixes.get(prefix=prefix)
    if prefix_exists:
        print(f"Skipping: {prefix} (already exists)")
        with counter_lock:
            prefix_counter["exists"]+=1
        return
    if location and ipam_id:
        site_name = location["name"]
        vlan_number = all_vlans.get(ipam_id, None)
        if vlan_number is not None:
            netbox_vlan_id = get_vlan_id_by_number(ipam_id, prefix)
            site_id = get_site_id_by_name(site_name)
            if netbox_vlan_id is not None:
                nb_prefix = nb.ipam.prefixes.create({
                    "prefix": prefix,
                    "description": subnet.get("description", ""),
                    "tenant": tenant_id,
                    "tags": [tag_id],
                    "scope_type": "dcim.site",
                    "scope_id": site_id,
                    "vlan": netbox_vlan_id
                })
                print(f"Created prefix: {prefix} in {site_name} ({site_id}) with vlan {ipam_id}")
            else:
                nb_prefix = nb.ipam.prefixes.create({
                    "prefix": prefix,
                    "description": subnet.get("description", ""),
                    "tenant": tenant_id,
                    "tags": [tag_id],
                    "scope_type": "dcim.site",
                    "scope_id": site_id
                })
                print(f"Created prefix: {prefix} in {site_name} ({site_id}) (associated vlan does not exist in Netbox)")                
        else:
            site_id = get_site_id_by_name(site_name)
            nb_prefix = nb.ipam.prefixes.create({
                "prefix": prefix,
                "description": subnet.get("description", ""),
                "tenant": tenant_id,
                "tags": [tag_id],
                "scope_type": "dcim.site",
                "scope_id": site_id
            })
            print(f"Created prefix: {prefix} in {site_name} ({site_id}) (no vlan association found in phpIPAM)")
        
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
    with counter_lock:
        prefix_counter["created"]+=1
    return

with ThreadPoolExecutor(max_workers=16) as executor: 
    for subnet in subnets:
        executor.submit(create_prefix, subnet)
        total_processed+=1

print(f"Counters:\nTotal Processed: {total_processed}\nExists: {prefix_counter['exists']}\nCreated: {prefix_counter['created']}")