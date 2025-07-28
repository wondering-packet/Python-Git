# below are some exercises which utilizes some basic API endpoints.
# refere to the file 000 for instructions on API.

import pynetbox
import urllib3
import random
import json
from pprint import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load credentials
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

# initializing netbox object.
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

# Exercise 1: List all tenants and print their name and description
response = nb.tenancy.tenants.all()
all_tenants = list(response)
for each_tenant in all_tenants:
    print(
        f"ID: {each_tenant.id}\tName:{each_tenant.name}\tDescription:{each_tenant.description}")

# Exercise 2: Filter racks by site name and list rack names
site = nb.dcim.sites.get(name="AP-BN")
site_id = site.id

site_racks = nb.dcim.racks.filter(site_id=site_id)
for each_rack in site_racks:
    print(f"Rack name: {each_rack.name}\t Height:{each_rack.u_height}")

# Exercise 3: Create a new tenant

# always create a payload in dictionary if you are passing multiple arguments. makes it easier.
new_tenant = {
    "name": "TestCorp",
    "slug": "testcorp",
    "description": "Temprory test tenant"
}
nb.tenancy.tenants.create(**new_tenant)     # our payload
created_tenant = nb.tenancy.tenants.get(name="TestCorp")
print(f"Name: {created_tenant.name}\tDescription: {created_tenant.description}\t Slug: {created_tenant.slug}")

# Exercise 4: Update a tenant’s description

created_tenant.update({"description": "Updated test tenant description"})
print(f"Name: {created_tenant.name}\tDescription: {created_tenant.description}\t Slug: {created_tenant.slug}")

# Exercise 5: Delete a tenant

created_tenant.delete()

# Exercise 6: Pull interfaces tagged with "automation"

all_interfaces = nb.dcim.interfaces.filter(tag="automation")
for each_interface in all_interfaces:
    print(
        f"Interface: {each_interface.name}\t Device: {each_interface.device.name}")

# Exercise 7: Error handling practice
nonexistant_tenant = nb.tenancy.tenants.get(name="nonexistant_tenant")

if nonexistant_tenant is None:
    print("Tenant not found")

# Exercise 8: Build a reusable utility function


def get_site_by_name(site_name):
    site = nb.dcim.sites.get(name=site_name)
    if site is None:
        return None
    else:
        return site.id

# Exercise x: temp code; pls ignore:

# site_name = "AMER-W"
# print(get_site_by_name(site_name))


# print("##########################################################")
# racks = nb.dcim.devices.filter(site_id=460)
# for rack in racks:
#     if "SW" in rack.name:
#         print(f"\n📦 Populating rack: {rack.name}")
# print("##########################################################")
tag = nb.extras.tags.get(name="vg")
tag_id = tag.id
ip_status = [
    "active",
    "reserved",
    "deprecated",
    "dhcp"
]


address = "172.16.10.40/24"
payload = {
    "address": address,
    "status": "reserved",
    "description": "Created via API",
    "tags": [tag_id]
}
exists = nb.ipam.ip_addresses.get(address=address)
if exists:
    print(f"Duplicate, already exists: {address}")
try:
    nb.ipam.ip_addresses.create(**payload)
    print(f"Created: {address}")
except Exception as e:
    print(f"Error: {e}")
# choices = nb.ipam.ip_addresses.choices()
# pprint(choices)
