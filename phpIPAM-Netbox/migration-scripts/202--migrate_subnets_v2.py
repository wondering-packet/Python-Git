# 202--migrate_subnets.py

import json
import pynetbox
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from concurrent.futures import ThreadPoolExecutor
from collections import Counter
from threading import Lock
import ipaddress
import keyring

API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")

# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False


# File paths
SUBNETS_FILE = r"c:\temp-python\phpipam\migration\subnets.json"
VLANS_FILE = r"c:\temp-python\phpipam\migration\vlans.json"
SUPERNETS_FILE = r"c:\temp-python\phpipam\migration\top_level_prefix.json"

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
        print(f"\n######--Site not found: {site_name}--######\n")
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

# this script block finds the site for a prefix based on supernets. supernets are loaded from a json.

with open(SUPERNETS_FILE, "r") as f:
    top_level_prefixes = json.load(f)

# Parse prefixes into usable format (list of tuples with ip_network and site)
parsed_prefixes = [
    (ipaddress.ip_network(p['prefix']), p.get('site'))
    for p in top_level_prefixes
]

def find_site_for_subnet(subnet_str):
    """Find the site associated with the longest matching parent prefix."""
    try:
        subnet = ipaddress.ip_network(subnet_str)
    except ValueError as e:
        raise ValueError(f"Invalid subnet '{subnet_str}': {e}")

    # Filter only prefixes that contain the given subnet
    matching_parents = [
        (prefix, site)
        for prefix, site in parsed_prefixes
        if subnet.subnet_of(prefix)
    ]

    if not matching_parents:
        return None  # No match found

    # Return the site of the most specific (longest prefix) match
    best_match = max(matching_parents, key=lambda x: x[0].prefixlen)
    return best_match[1]  # Return the site name

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
        site_name = find_site_for_subnet(prefix)
        if site_name is None:
            nb_prefix = nb.ipam.prefixes.create({
            "prefix": prefix,
            "description": subnet.get("description", ""),
            "tenant": tenant_id,
            "tags": [tag_id]
            })
            print(f"Created prefix: {prefix}")
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
            print(f"Created prefix: {prefix}")
    with counter_lock:
        prefix_counter["created"]+=1
    return

with ThreadPoolExecutor(max_workers=16) as executor: 
    for subnet in subnets:
        executor.submit(create_prefix, subnet)
        total_processed+=1

print(f"Counters:\nTotal Processed: {total_processed}\nExists: {prefix_counter['exists']}\nCreated: {prefix_counter['created']}")