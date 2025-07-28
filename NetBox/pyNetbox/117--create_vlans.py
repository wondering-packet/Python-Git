# used chatgpt to help me create random vlans for my dummy data.
# it creates 20 vlans with names (provided) & associate each vlan with a role.

import pynetbox
import urllib3
import json

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Connect to NetBox
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False  # Ignore self-signed certs

# Configuration
TENANT_NAME = "WP-Corp"
TAG = (nb.extras.tags.get(name="vg")).id
DESCRIPTION = "Auto Created via API"

# VLAN roles
fixed_roles = ["AV", "DATA", "PRINTERS", "SERVERS"]
misc_role = "MISC"
custom_names = [
    "HR", "FINANCE", "ENGINEERING", "OPERATIONS", "SALES",
    "SUPPORT", "LEGAL", "SECURITY", "DEVOPS"
]

# Step 1: Get tenant
tenant = nb.tenancy.tenants.get(name=TENANT_NAME)
if not tenant:
    raise ValueError(f"Tenant '{TENANT_NAME}' not found.")

# Step 2: Get existing roles
role_map = {r.slug: r.id for r in nb.ipam.roles.all()}

# Helper to create role if missing


def ensure_role(role_name):
    slug = role_name.lower()
    if slug in role_map:
        return role_map[slug]
    role = nb.ipam.roles.create({"name": role_name, "slug": slug})
    role_map[slug] = role.id
    return role.id


# Step 3: Define all VLANs
vlans = []

# 4 specific roles → same names
for name in fixed_roles:
    vlans.append({
        "name": name,
        "role": ensure_role(name),
    })

# 7 MISC roles
for i in range(1, 8):
    vlans.append({
        "name": f"MISC-{i}",
        "role": ensure_role(misc_role),
    })

# Remaining 9 roles → custom names
for name in custom_names:
    vlans.append({
        "name": name,
        "role": ensure_role(name),
    })

# Step 4: Create VLANs
for i, vlan_data in enumerate(vlans, start=1):
    vlan = {
        "name": vlan_data["name"],
        "vid": 100 + i,
        "tenant": tenant.id,
        "role": vlan_data["role"],
        "tags": [TAG],
        "description": DESCRIPTION,
    }
    try:
        created = nb.ipam.vlans.create(vlan)
        print(f"✅ Created VLAN {created.name} with VID {created.vid}")
    except Exception as e:
        print(f"❌ Failed to create VLAN {vlan['name']}: {e}")
