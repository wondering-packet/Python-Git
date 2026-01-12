# prompted chatgpt to help me write this simple script which backs up entire IPAM app.

import pynetbox
import os
import json
from datetime import datetime
import urllib3
import keyring
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Config ---
API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")

BACKUP_BASE_DIR = r"c:\temp-python\phpipam\migration\netbox-backups"

# --- Setup ---
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup_dir = os.path.join(BACKUP_BASE_DIR, f"netbox-ipam-{timestamp}")
os.makedirs(backup_dir, exist_ok=True)

# --- Define resources ---
resources = {
    "prefixes": nb.ipam.prefixes,
    "ip_addresses": nb.ipam.ip_addresses,
    "vlans": nb.ipam.vlans,
    "vlan_groups": nb.ipam.vlan_groups,
    "rir": nb.ipam.rirs,
    "aggregates": nb.ipam.aggregates,
    "ipam_roles": nb.ipam.roles,
    "vrfs": nb.ipam.vrfs,
    "services": nb.ipam.services,
}

# --- Backup each resource ---
for name, endpoint in resources.items():
    print(f"Backing up: {name} ...")
    try:
        records = [r.serialize() for r in endpoint.all()]
        with open(os.path.join(backup_dir, f"{name}.json"), "w") as f:
            json.dump(records, f, indent=2)
        print(f"✔️  {name} → saved {len(records)} records.")
    except Exception as e:
        print(f"❌  Failed to back up {name}: {e}")

print(f"\n✅ Backup completed. Files saved to: {backup_dir}")