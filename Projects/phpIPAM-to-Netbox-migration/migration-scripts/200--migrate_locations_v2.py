import json
import re
import pynetbox
import urllib3
import keyring
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Config Paths ---
PHPIPAM_LOCATIONS_FILE = r"c:\temp-python\phpipam\migration\phpipam_locations.json"

# --- NetBox API Setup ---
API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")

netbox = pynetbox.api(NETBOX_URL, token=API_TOKEN)

# Optional: Disable SSL verification if needed (not recommended in production)
netbox.http_session.verify = False


def slugify(name):
    # Lowercase the name
    slug = name.lower()
    # Replace spaces and dots with hyphens
    slug = slug.replace(" ", "-").replace(".", "-")
    # Remove invalid characters (keep letters, numbers, -, _)
    slug = re.sub(r"[^a-z0-9-_]", "", slug)
    return slug


TENANT_NAME = "Corporate"

# Ensure tenant exists


def get_tenant_id(name):
    tenant = netbox.tenancy.tenants.get(name=name)
    if tenant:
        return tenant.id
    else:
        print(f"Tenant '{name}' not found")


tenant_id = get_tenant_id(TENANT_NAME)

tag = netbox.extras.tags.get(name="phpipam-migrated")
tag_id = tag.id
tag_slug = tag.slug
# Create or update site in NetBox

def format_coordinates(value, type):
    """
    Rounds latitude and longitude to 6 decimal places
    and returns them as separate key-value pairs.
    """
    try:
        if type == "lat":
            formatted_lat = round(float(value), 6)
            return formatted_lat
        elif type == "long":
            formatted_lon = round(float(value), 6)
            return formatted_lon
    except (TypeError, ValueError):
        raise ValueError("Invalid latitude or longitude input.")


def sync_site(location, tag_id):
    name = location["name"]
    site = netbox.dcim.sites.get(name=name)
    if site:
        print(f"✅ Site exists: {name}, skipping creation.")

    else:
        coord_exists = location.get("lat")
        if location.get("address") is None:
            address_exists = False
        if location.get("description") is None:
            description_exists = False
        if coord_exists and address_exists and description_exists:
            payload = {
                "name": name,
                "description": location.get("description"),
                "physical_address": location.get("address"),
                "latitude": format_coordinates(value=location.get("lat"), type="lat"),
                "longitude": format_coordinates(value=location.get("long"), type="long"),
                "tags": [tag_id],
                "slug": slugify(name),
                "tenant": tenant_id,
                "tags": [tag_id]
            }
        elif address_exists and description_exists:
            payload = {
                "name": name,
                "description": location.get("description"),
                "physical_address": location.get("address"),
                "tags": [tag_id],
                "slug": slugify(name),
                "tenant": tenant_id,
                "tags": [tag_id]
            } 
        else:
            payload = {
                "name": name,
                "tags": [tag_id],
                "slug": slugify(name),
                "tenant": tenant_id,
                "tags": [tag_id]
            }                       
        created_site = netbox.dcim.sites.create(payload)
        if created_site:
            print(f"🆕 Created site: {name}")
        else:
            print(f"❌ Failed to create site: {name}")


# Main logic
if __name__ == "__main__":
    tag = netbox.extras.tags.get(name="phpipam-migrated")
    tag_id = tag.id
    with open(PHPIPAM_LOCATIONS_FILE, "r") as f:
        locations = json.load(f)
    for loc in locations:
        sync_site(loc, tag_id)