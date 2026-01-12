import pynetbox
import json
import urllib3
import keyring

# --- NetBox API Setup ---
API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")

nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)

# Optional: Disable SSL verification if needed (not recommended in production)
nb.http_session.verify = False
# --- SSL warnings off for self-signed certs ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# Retrieve all prefixes
all_prefixes = nb.ipam.prefixes.all()

# Filter prefixes with _depth == 0
top_level_prefixes = [p for p in all_prefixes if getattr(p, "_depth", None) == 0]

# Prepare JSON data and counters
json_data = []
with_scope = 0
without_scope = 0

OUTPUT_FILE = r"c:\temp-python\phpipam\migration\top_level_prefix.json"

for prefix in top_level_prefixes:
    scope_name = getattr(prefix.scope, 'name', None)
    if scope_name:
        with_scope += 1
    else:
        without_scope += 1
    json_data.append({
        "prefix": prefix.prefix,
        "site": scope_name
    })

# Write to JSON file
with open(OUTPUT_FILE, "w") as f:
    json.dump(json_data, f, indent=4)

# Output result summary
print(f"\nExported {len(json_data)} top-level prefixes to '{OUTPUT_FILE}'")
print(f"Prefixes without scope: {without_scope}")
print(f"Prefixes with scope   : {with_scope}")
