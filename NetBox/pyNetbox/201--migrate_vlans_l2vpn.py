# 201--migrate_subnets_l2vpn.py

import re
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


# File path
VLANS_FILE = "/automation/python-data/phpipam-backups/vlans.json"

TENANT_NAME = "WP-Corp"
DEFAULT_VLAN_ROLE = "MISC"

# Ensure tenant exists


def get_or_create_tenant(name):
    tenant = nb.tenancy.tenants.get(name=name)
    if tenant:
        return tenant.id
    return nb.tenancy.tenants.create({"name": name}).id


tenant_id = get_or_create_tenant(TENANT_NAME)


def slugify(name):
    # Lowercase the name
    slug = name.lower()
    # Replace spaces and dots with hyphens
    slug = slug.replace(" ", "-").replace(".", "-")
    # Remove invalid characters (keep letters, numbers, -, _)
    slug = re.sub(r"[^a-z0-9-_]", "", slug)
    return slug

# VLAN status mapping


def map_vlan_status(status):
    return {
        "Active": "active",
        "Reserved": "reserved",
        "Deprecated": "deprecated"
    }.get(status, "active")

# Ensure VLAN role exists


def get_or_create_vlan_role(name):
    role = nb.ipam.roles.get(name=name)
    if role:
        return role.id
    return nb.ipam.roles.create({"name": name, "slug": name.lower()}).id


vlan_role_id = get_or_create_vlan_role(DEFAULT_VLAN_ROLE)

tag = nb.extras.tags.get(name="phpipam-migrated")
tag_id = tag.id

# Load VLANs
with open(VLANS_FILE, "r") as f:
    vlans = json.load(f)

for vlan in vlans:
    vlan_id = vlan["number"]
    vlan_name = vlan["name"]
    status = map_vlan_status(vlan.get("custom_Status", "Active"))
    l2vni = vlan.get("custom_L2VNI")
    vlan_exists = nb.ipam.vlans.get(name=vlan_name, vid=vlan_id, tags=[tag_id])
    if vlan_exists:
        print(f"Skipped Vlan: {vlan_name} : {vlan_id} (already exists)")
        continue
    else:
        created_vlan = nb.ipam.vlans.create({
            "name": vlan_name,
            "vid": vlan_id,
            "description": vlan.get("description", ""),
            "status": status,
            "tenant": tenant_id,
            "role": vlan_role_id,
            "tags": [tag_id]
        })

        print(f"Created Vlan: {created_vlan.name} : {created_vlan.vid}")
        # Create L2VPN and termination if L2VNI is present
        if l2vni:
            l2vni_exists = nb.vpn.l2vpns.get(
                name=vlan_name, identifier=l2vni, tags=[tag_id])
            if l2vni_exists:
                print(
                    f"Skipped L2VPN & L2VPN termination: {l2vni} (already exists)")
                continue
            else:
                l2vpn = nb.vpn.l2vpns.create({
                    "name": vlan_name,
                    "slug": slugify(vlan_name),
                    "identifier": l2vni,
                    "type": "vxlan-evpn",
                    "description": f"L2VPN for {vlan_name}",
                    "tags": [tag_id]
                })

                print(f"Created L2VPN: {l2vpn.name} : {l2vpn.identifier}")

                l2vpn_termination = nb.vpn.l2vpn_terminations.create({
                    "l2vpn": l2vpn.id,
                    "vlan": created_vlan.id,
                    "assigned_object_type": "ipam.vlan",
                    "assigned_object_id": created_vlan.id,
                    "name": vlan_name,
                    "tags": [tag_id]
                })

                print(
                    f"Created L2VPN Termination: {l2vpn_termination.display} : Vlan({l2vpn_termination.assigned_object_id})")
