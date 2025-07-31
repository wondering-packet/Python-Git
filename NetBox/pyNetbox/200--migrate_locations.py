import json
import re
import pynetbox
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Config Paths ---
PHPIPAM_LOCATIONS_FILE = "/automation/python-data/phpipam-backups/phpipam_locations.json"

# --- NetBox API Setup ---
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

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

# Create or update site in NetBox


def sync_site(location, tag_id):
    name = location["name"]
    site = netbox.dcim.sites.get(name=name)
    if site:
        print(f"✅ Site exists: {name}, skipping creation.")

    else:
        payload = {
            "name": name,
            "description": location.get("description", "LOCATION_NOT_FOUND_IN_PHPIPAM"),
            "physical_address": location.get("address", "LOCATION_NOT_FOUND_IN_PHPIPAM"),
            "latitude": location.get("lat"),
            "longitude": location.get("long"),
            "tags": [tag_id],
            "slug": slugify(name)
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
