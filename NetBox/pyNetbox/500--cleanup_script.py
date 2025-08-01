import pynetbox
import urllib3
import json
import re

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Connect to NetBox
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False  # Ignore self-signed certs

vlan_id = 15
# vlan_name = "VLAN 2010"
tag = nb.extras.tags.get(name="phpipam-migrated")
tag_id = tag.id
# vlan_exists = nb.ipam.vlans.get(vid=vlan_id, tags=[tag_id])
# print(vlan_exists.description)


del_vlans = nb.ipam.vlans.all()

# for vlan in del_vlans:
#     if vlan.tags:
#         tag_ids = [t.id for t in vlan.tags]
#         if tag_id in tag_ids:
#             try:
#                 vlan.delete()
#                 print(f"✅ Deleted VLAN: {vlan.vid} -- {vlan.name}")
#             except pynetbox.RequestError as e:
#                 if "dependent objects" in str(e.error):
#                     # VLAN has dependent prefixes — remove their association
#                     prefixes = nb.ipam.prefixes.filter(vlan_id=vlan.id)
#                     if prefixes:
#                         print(
#                             f"⚠️  VLAN {vlan.vid} has {len(prefixes)} dependent prefixes. Removing association...")
#                         for prefix in prefixes:
#                             updated = prefix.update({'vlan': None})
#                             if updated:
#                                 print(
#                                     f"   ↪ Cleared VLAN from prefix: {prefix.prefix}")
#                             else:
#                                 print(
#                                     f"   ❌ Failed to update prefix: {prefix.prefix}")
#                         # Retry VLAN deletion
#                         try:
#                             vlan.delete()
#                             print(
#                                 f"✅ Deleted VLAN after clearing dependencies: {vlan.vid} -- {vlan.name}")
#                         except pynetbox.RequestError as e2:
#                             print(
#                                 f"❌ Still failed to delete VLAN {vlan.vid}: {e2.error}")
#                     else:
#                         print(
#                             f"⚠️  Conflict but no prefixes found for VLAN {vlan.vid}")
#                 else:
#                     print(f"❌ Error deleting VLAN {vlan.vid}: {e.error}")


# del_l2vpns = nb.vpn.l2vpns.all()

# for l2vpn in del_l2vpns:
#     if l2vpn.tags:
#         tag_ids = [t.id for t in l2vpn.tags]
#         if tag_id in tag_ids:
#             l2vpn.delete()
#             print(
#                 f"Deleted: {l2vpn.identifier} -- {l2vpn.name} -- {l2vpn.description}")

# del_l2vpns_terminations = nb.vpn.l2vpn_terminations.all()

# for l2vpn in del_l2vpns_terminations:
#     if l2vpn.tags:
#         tag_ids = [t.id for t in l2vpn.tags]
#         if tag_id in tag_ids:
#             l2vpn.delete()
#             print(
#                 f"Deleted termination: {l2vpn.display}")

# del_prefixs = nb.ipam.prefixes.all()

# for prefix in del_prefixs:
#     if prefix.tags:
#         tag_ids = [t.id for t in prefix.tags]
#         if tag_id in tag_ids:
#             prefix.delete()
#             print(
#                 f"Deleted: {prefix.prefix} -- {prefix.description}")

# for vlan in del_vlans:
#     if vlan.id == 15:
#         print(f"{vlan.vid} -- {vlan.name} -- {vlan.description} -- Site: {vlan.site} -- Tenant: {vlan.tenant}")

# del_ips = nb.ipam.ip_addresses.all()

# for ip in del_ips:
#     if ip.tags:
#         tag_ids = [t.id for t in ip.tags]
#         if tag_id in tag_ids:
#             ip.delete()
#             print(
#                 f"Deleted: {ip.address} -- {ip.description}")


# def get_site_id_by_name(site_name):
#     site = nb.dcim.sites.get(name=site_name)
#     if site is None:
#         print("Site not found")
#         return
#     else:
#         return site.id


# tag = nb.extras.tags.get(name="phpipam-migrated")
# tag_id = tag.id
# TENANT_NAME = "WP-Corp"


# def slugify(name):
#     # Lowercase the name
#     slug = name.lower()
#     # Replace spaces and dots with hyphens
#     slug = slug.replace(" ", "-").replace(".", "-")
#     # Remove invalid characters (keep letters, numbers, -, _)
#     slug = re.sub(r"[^a-z0-9-_]", "", slug)
#     return slug


# def get_or_create_tenant(name):
#     tenant = nb.tenancy.tenants.get(name=name)
#     if tenant:
#         return tenant.id
#     return nb.tenancy.tenants.create({"name": name}).id


# tenant_id = get_or_create_tenant(TENANT_NAME)


# def get_or_create_vlan_group(name):
#     vlan_group = nb.ipam.vlan_groups.get(name=f"{name}-VLANs")
#     if vlan_group:
#         print("\n\nexists")
#         return vlan_group.id
#     else:
#         payload = {
#             "name": f"{name}-VLANs",
#             "slug": slugify(name),
#             "scope_id": get_site_id_by_name(name),
#             "scope_type": "dcim.site",
#             "tenant_id": tenant_id,
#             "description": f"VLANS in {name}",
#             "tags": [tag_id]
#         }
#         return nb.ipam.vlan_groups.create(**payload)


# get_or_create_vlan_group("TEST-Site")


tag_name = "phpipam-migrated"

# Get the tag object using name
tag = nb.extras.tags.get(name=tag_name)
tag_id = tag.slug
vlan_exists = list(nb.ipam.vlans.filter(
    name="VLAN 2010", vid=2010, tag=tag_id))
if vlan_exists:
    vlan = vlan_exists[0]  # assuming unique match
    print(vlan.description)
    print(vlan.tags)
else:
    print("No VLAN found with the correct tag.")
##################
tag_id = tag.slug
vlan = nb.ipam.vlans.get(
    name="VLAN 2010", vid=2010, tag=tag_id)
if vlan:
    # vlan = vlan_exists[0]  # assuming unique match
    print(vlan.description)
    print(vlan.tags)
else:
    print("No VLAN found with the correct tag.")
