import pynetbox
import json
from pprint import pprint
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
# needed because of self signed cert that i am using.
nb.http_session.verify = False

# we need this function because you cannot pass site_name as an argument in netbox.
# you need the numeric ID instead. it's similar with other netbox objects such as tenant as well.
# note that: i have tried to modularize all my scripts. each function does one task.


def get_site_id_by_name(site_name):
    site = nb.dcim.sites.get(name=site_name)
    if site is None:
        print("Site not found")
        return
    else:
        return site.id


def get_all_locations_for_site(site_name):
    site_id = get_site_id_by_name(site_name)
    all_locations = nb.dcim.locations.filter(site_id=site_id)
    if all_locations is None:
        print("No locations not found for the site")
        return
    else:
        return list(all_locations)


def get_location_id_by_name(location_name):
    location = nb.dcim.locations.get(name=location_name)
    if location is None:
        print("Location not found")
        return
    else:
        return location.id


def get_tenant_id_by_name(tenant_name):
    tenant = nb.tenancy.tenants.get(name=tenant_name)
    if tenant is None:
        print("Tenant not found")
        return
    else:
        return tenant.id


def create_rack(site_name, location_name, tenant_name, n):

    site_id = get_site_id_by_name(site_name)
    location_id = get_location_id_by_name(location_name)
    tenant_id = get_tenant_id_by_name(tenant_name)

    rack_name = f"{location_name}-RCK0{n}"
    # payload
    # notice that "tags" need to passed as a List of tags (each tag is in its own dictionary)
    rack = {
        "name": rack_name,
        "site": site_id,
        "location": location_id,
        "tenant": tenant_id,
        "tags": [{"name": "vg"}]
    }
    try:
        nb.dcim.racks.create(**rack)
        print("Rack created")
        return
    except Exception as e:
        print(f"Error - failed to create rack: {e}")
        return


def main():
    site_name = "AMER-E"
    tenant_name = "WP-Corp"
    total_new_racks_per_location = 2

    all_locations = get_all_locations_for_site(site_name)

    for each_location in all_locations:
        location_name = each_location.name
        for n in range(total_new_racks_per_location):
            n += 1
            create_rack(site_name, location_name, tenant_name, n)


if __name__ == "__main__":
    main()
