# 201--migrate_subnets_l2vpn.py

import re
import json
import pynetbox
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


with open(r"c:\temp-python\phpipam\netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]


# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False


# File path
VLANS_FILE = r"c:\temp-python\phpipam\migration\vlans.json"

TENANT_NAME = "Corporate"
DEFAULT_VLAN_ROLE = "MISC"

# Ensure tenant exists


def get_or_create_tenant(name):
    tenant = nb.tenancy.tenants.get(name=name)
    if tenant:
        return tenant.id
    return nb.tenancy.tenants.create({"name": name}).id


tenant_id = get_or_create_tenant(TENANT_NAME)

tag = nb.extras.tags.get(name="phpipam-migrated")
tag_id = tag.id
tag_slug = tag.slug


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


def get_site_id_by_name(site_name):
    site = nb.dcim.sites.get(name=site_name)
    if site is None:
        print(f"Site not found {site_name}")
        return
    else:
        return site.id


def get_or_create_vlan_group(name):
    vlan_group = nb.ipam.vlan_groups.get(name=f"{name}-VLANs")
    if vlan_group:
        return vlan_group.id
    else:
        if name == "Global":
            payload = {
                "name": f"{name}-VLANs",
                "slug": slugify(name),
                "tenant": tenant_id,
                "description": f"VLANS in {name}",
                "tags": [tag_id]
            }
        else:
            payload = {
                "name": f"{name}-VLANs",
                "slug": slugify(name),
                "scope_id": get_site_id_by_name(name),
                "scope_type": "dcim.site",
                "tenant": tenant_id,
                "description": f"VLANS in {name}",
                "tags": [tag_id]
            }
        return (nb.ipam.vlan_groups.create(**payload)).id


vlan_role_id = get_or_create_vlan_role(DEFAULT_VLAN_ROLE)

AMUSDC2_vlan_counter = 0
AMUSDC1_vlan_counter = 0
GLOBAL_vlan_counter = 0
UNKNOWN_vlan_counter = 0
# Load VLANs
with open(VLANS_FILE, "r") as f:
    vlans = json.load(f)

for vlan in vlans:
    ipam_vid = int(vlan["vlanId"])
    vlan_id = vlan["number"]
    vlan_name = vlan["name"]
    domain_id = int(vlan["domainId"])
    if domain_id == 2:
        vlan_group = "AMUSDC1"
        AMUSDC1_vlan_counter+=1
    elif domain_id == 3:
        vlan_group = "AMUSDC2"
        AMUSDC2_vlan_counter+=1
    elif domain_id == 1:
        vlan_group = "Global"
        GLOBAL_vlan_counter+=1
    else:
        print(f"Skipped Vlan: {vlan_name} : {vlan_id} (Unknown domain)")
        UNKNOWN_vlan_counter+=1
        continue
    vlan_group_id = get_or_create_vlan_group(vlan_group)
    status = map_vlan_status(vlan.get("custom_Status", "Active"))
    l2vni = vlan.get("custom_L2VNI")
    vlan_exists = nb.ipam.vlans.filter(
        name=vlan_name, vid=vlan_id, tag=tag_slug)
    if vlan_exists:
        print(f"Skipped Vlan: {vlan_name} : {vlan_id} (already exists)")
    else:
        try:
            description_exists = True
            if vlan.get("description") is None:
                description_exists = False
            if description_exists:
                created_vlan = nb.ipam.vlans.create({
                    "name": vlan_name,
                    "vid": vlan_id,
                    "description": vlan.get("description", ""),
                    "status": status,
                    "tenant": tenant_id,
                    "role": vlan_role_id,
                    "tags": [tag_id],
                    "group": vlan_group_id,
                    "custom_fields": {"IPAM_vid": ipam_vid}
                })
            else:
                created_vlan = nb.ipam.vlans.create({
                    "name": vlan_name,
                    "vid": vlan_id,
                    "status": status,
                    "tenant": tenant_id,
                    "role": vlan_role_id,
                    "tags": [tag_id],
                    "group": vlan_group_id,
                    "custom_fields": {"IPAM_vid": ipam_vid}
                })
            print(
                f"Created Vlan: {created_vlan.name} : {created_vlan.vid} : {created_vlan.group}")
        except Exception as e:
            print(
                f"Skipped Vlan: {vlan_name} : {vlan_id} (likely already exists in the group: {vlan_group}-VLANs)\nError: {e}\n")
            continue
    # Create L2VPN and termination if L2VNI is present
    if l2vni:
        vlan = nb.ipam.vlans.get(vid=vlan["number"], group_id=get_or_create_vlan_group(vlan_group))
        l2vni_exists = nb.vpn.l2vpns.filter(
            name=vlan_name, identifier=l2vni, tag=tag_slug)
        if l2vni_exists:
            print(
                f"Skipped L2VPN creation: {l2vni} (already exists)")
            try:
                l2vpn = nb.vpn.l2vpns.get(identifier=l2vni)
                l2vpn_termination = nb.vpn.l2vpn_terminations.create({
                    "l2vpn": l2vpn.id,
                    "vlan": vlan.id,
                    "assigned_object_type": "ipam.vlan",
                    "assigned_object_id": vlan.id,
                    "name": vlan_name,
                    "tags": [tag_id],
                    "tenant": tenant_id
                })

                print(
                    f"Created L2VPN Termination: {l2vpn_termination.display} : Vlan({l2vpn_termination.assigned_object_id})")
            except Exception as e:
                print(f"Exception occured (L2VPN: {l2vpn.id}) in Block1; Error: {e}")
            continue
        else:
            try:
                l2vpn = nb.vpn.l2vpns.create({
                    "name": vlan_name,
                    "slug": slugify(vlan_name),
                    "identifier": l2vni,
                    "type": "vxlan-evpn",
                    "description": f"L2VPN for {vlan_name}",
                    "tags": [tag_id],
                    "tenant": tenant_id
                })

                print(f"Created L2VPN: {l2vpn.name} : {l2vpn.identifier}")

                l2vpn_termination = nb.vpn.l2vpn_terminations.create({
                    "l2vpn": l2vpn.id,
                    "vlan": vlan.id,
                    "assigned_object_type": "ipam.vlan",
                    "assigned_object_id": vlan.id,
                    "name": vlan_name,
                    "tags": [tag_id],
                    "tenant": tenant_id
                })

                print(
                    f"Created L2VPN Termination: {l2vpn_termination.display} : Vlan({l2vpn_termination.assigned_object_id})")
            except Exception as e:
                print(f"Exception occured (L2VPN: {l2vpn.id}) in Block2; Error: {e}")
print(
    f"AMUSDC1 vlans imported: {AMUSDC1_vlan_counter}\n"
      f"AMUSDC2 vlans imported: {AMUSDC2_vlan_counter}\n"
      f"Global vlans imported: {GLOBAL_vlan_counter}\n"
      f"Unknown vlans (failed to import): {UNKNOWN_vlan_counter}\n"
      )