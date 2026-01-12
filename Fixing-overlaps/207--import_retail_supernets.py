'''
netbox_retail_stores_prefixes.csv is the input file which contains lists of all supernets (/24).
also this retail list doesn't have duplicate subnets as it's already processed (manually).
this script creates the subnets (/24).
'''
import pynetbox
import urllib3
import keyring
import csv
import logging
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Config ---
RETAIL_STORES_PREFIXES_FILE = r"c:\temp\netbox\netbox_retail_stores_prefixes.csv"
LOG_FILE = r"c:\temp\netbox\207-logs-netbox_retail_prefixes.log"
MAX_THREADS = 10
TENANT_NAME = "Retail"
TAG_NAME = "Retail"

# --- Logging setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# --- Disable SSL Warnings ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- NetBox API Setup ---
try:
    API_TOKEN = keyring.get_password("netbox", "api_key")
    NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")
    if not API_TOKEN or not NETBOX_URL:
        logging.error("API_TOKEN or NETBOX_URL not found in keyring.")
        sys.exit(1)
except Exception as e:
    logging.error(f"Error retrieving API credentials: {e}")
    sys.exit(1)

nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

# --- Global tenant and tag IDs ---
try:
    tenant = nb.tenancy.tenants.get(name=TENANT_NAME)
    if not tenant:
        logging.error(f"Tenant '{TENANT_NAME}' not found. Exiting.")
        sys.exit(1)
    tenant_id = tenant.id

    tag = nb.extras.tags.get(name=TAG_NAME)
    if not tag:
        logging.error(f"Tag '{TAG_NAME}' not found. Exiting.")
        sys.exit(1)
    tag_id = tag.id
except Exception as e:
    logging.error(f"Error fetching tenant or tag info: {e}")
    sys.exit(1)

# --- Thread-safe site ID cache ---
site_id_cache = {}
site_cache_lock = threading.Lock()

def get_site_id(site_name):
    """Thread-safe site ID lookup with caching."""
    with site_cache_lock:
        if site_name in site_id_cache:
            return site_id_cache[site_name]

    try:
        site = nb.dcim.sites.get(name=site_name)
        if site:
            site_id = site.id
            with site_cache_lock:
                site_id_cache[site_name] = site_id
            return site_id
        else:
            logging.warning(f"Site not found: '{site_name}'")
            return None
    except Exception as e:
        logging.error(f"Error fetching site '{site_name}': {e}")
        return None

# --- Prefix creation task ---
def process_row(row):
    site_name = row.get('name', '').strip()
    prefix_cidr = row.get('prefix', '').strip()

    if not site_name or not prefix_cidr:
        logging.warning(f"Invalid data: site='{site_name}', prefix='{prefix_cidr}'")
        return

    site_id = get_site_id(site_name)
    if not site_id:
        return

    try:
        if nb.ipam.prefixes.get(prefix=prefix_cidr):
            logging.info(f"Prefix already exists: {prefix_cidr} (Site: {site_name})")
            return
    except Exception as e:
        logging.error(f"Error checking existing prefix '{prefix_cidr}': {e}")
        return

    prefix_data = {
        "prefix": prefix_cidr,
        "description": f"{site_name} - Supernet",
        "status": "container",
        "tenant": tenant_id,
        "tags": [tag_id],
        "scope_type": "dcim.site",
        "scope_id": site_id
    }

    try:
        result = nb.ipam.prefixes.create(prefix_data)
        if result:
            logging.info(f"✅ Created prefix: {prefix_cidr} (Site: {site_name})")
        else:
            logging.error(f"❌ Failed to create prefix: {prefix_cidr} (Site: {site_name})")
    except Exception as e:
        logging.error(f"Error creating prefix '{prefix_cidr}' for site '{site_name}': {e}")

# --- Main logic ---
def main():
    try:
        with open(RETAIL_STORES_PREFIXES_FILE, newline='', encoding='latin1') as csvfile:
            reader = list(csv.DictReader(csvfile))
            logging.info(f"📄 Loaded {len(reader)} rows from CSV.")

            with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
                futures = [executor.submit(process_row, row) for row in reader]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f"Threaded task exception: {e}")

    except FileNotFoundError:
        logging.error(f"File not found: {RETAIL_STORES_PREFIXES_FILE}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    logging.info("=== Script started ===")
    main()
    logging.info("=== Script finished ===")
