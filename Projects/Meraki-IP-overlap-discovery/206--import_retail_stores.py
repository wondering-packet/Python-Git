import re
import pynetbox
import urllib3
import keyring
import csv
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Config Paths ---
RETAIL_STORES_FILE = r"c:\temp\netbox\netbox_retail_stores.csv"

# --- NetBox API Setup ---
API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")

nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)

# Optional: Disable SSL verification if needed (not recommended in production)
nb.http_session.verify = False


def slugify(name):
    # Lowercase the name
    slug = name.lower()
    # Replace spaces and dots with hyphens
    slug = slug.replace(" ", "-").replace(".", "-")
    # Remove invalid characters (keep letters, numbers, -, _)
    slug = re.sub(r"[^a-z0-9-_]", "", slug)
    return slug


TENANT_NAME = "Retail"

# Ensure tenant exists


def get_tenant_id(name):
    tenant = nb.tenancy.tenants.get(name=name)
    if tenant:
        return tenant.id
    else:
        print(f"Tenant '{name}' not found")


tenant_id = get_tenant_id(TENANT_NAME)

tag = nb.extras.tags.get(name="Retail")
tag_id = tag.id
tag_slug = tag.slug
# Create or update site in NetBox

def get_region_id(region_name):
    """
    Get the ID of a region by its name (slug or name).
    """
    region = nb.dcim.regions.get(slug=region_name)
    if not region:
        region = nb.dcim.regions.get(name=region_name)
    if region:
        return region.id
    else:
        print(f"[!] Region '{region_name}' not found.")
        return None

def create_site(name, region_name):
    region_id = get_region_id(region_name)
    if not region_id:
        print(f"[!] Skipping site '{name}' due to missing region.")
        return

    site_data = {
        "name": name,
        "region": region_id,
        "slug": slugify(name),
        "tenant": tenant_id,
        "tags": [tag_id]
    }

    try:
        existing_site = nb.dcim.sites.get(name=name)
        if existing_site:
            print(f"[i] Site '{name}' already exists. Skipping.")
            return

        new_site = nb.dcim.sites.create(site_data)
        if new_site:
            print(f"[+] Created site: {name}")
        else:
            print(f"[!] Failed to create site: {name}")
    except Exception as e:
        print(f"[!] Error creating site '{name}': {e}")

def main():
    with open(RETAIL_STORES_FILE, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            site_name = row['Name'].strip()
            region_name = row['Region'].strip()
            create_site(site_name, region_name)

if __name__ == "__main__":
    main()