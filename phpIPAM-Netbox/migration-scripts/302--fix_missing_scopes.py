#!/usr/bin/env python3
"""
Sync child prefix scopes from supernets:
- If a child prefix has no scope, copy scope_type & scope_id from its supernet.
- If child already has scope set, take no action.
- Supernet scope can be dcim.site, dcim.region, dcim.location, tenancy.tenant, etc.

Reads NETBOX_URL and API_TOKEN from /automation/secrets/netbox.json
NetBox: 4.3.x; pynetbox.
"""

import json
import urllib3
import pynetbox
import keyring

# --- Config ---
API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")
SECRETS_FILE = r"c:\temp-python\phpipam\netbox.json"
VERIFY_SSL = False  # lab: self-signed
DRY_RUN = False     # set True to preview changes without writing

# Your supernets list (CIDRs). The human “Scope” names in your table are informational;
# the script reads the ACTUAL scope from NetBox supernet objects.

INPUT_FILE = r"c:\temp-python\phpipam\migration\top_level_prefix.json"

# Load the JSON data
with open(INPUT_FILE, "r") as f:
    data = json.load(f)

# Extract all prefix values
SUPERNETS = [entry["prefix"] for entry in data]

# --- SSL warnings off for self-signed certs ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Helpers ---


def normalize_scope_type(scope_type):
    """
    NetBox may return scope_type as a string ('dcim.site') or dict
    ({'app_label': 'dcim', 'model': 'site'}). Normalize to 'app_label.model'.
    """
    if not scope_type:
        return None
    if isinstance(scope_type, dict):
        app = scope_type.get("app_label") or scope_type.get("app") or ""
        model = scope_type.get("model") or ""
        key = ".".join([p for p in (app, model) if p])
        return key or None
    return str(scope_type)


def get_scope_name(nb, scope_type, scope_id):
    """Resolve scope_id → human name based on scope_type"""
    if not (scope_type and scope_id):
        return None
    try:
        app, model = scope_type.split(".")
    except Exception:
        return None

    # Map app/model to pynetbox endpoints
    if app == "dcim" and model == "site":
        obj = nb.dcim.sites.get(scope_id)
    elif app == "dcim" and model == "region":
        obj = nb.dcim.regions.get(scope_id)
    elif app == "dcim" and model == "location":
        obj = nb.dcim.locations.get(scope_id)
    elif app == "tenancy" and model == "tenant":
        obj = nb.tenancy.tenants.get(scope_id)
    else:
        return None

    return obj.name if obj else None


def main():

    nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
    nb.http_session.verify = VERIFY_SSL

    total_children = 0
    updated = 0
    skipped_already_scoped = 0
    skipped_missing_supernet_scope = 0
    skipped_supernet_not_found = 0

    print(f"DRY_RUN = {DRY_RUN}")
    print("Starting scope sync from supernets → child prefixes...\n")

    for cidr in SUPERNETS:
        # Fetch supernet by exact prefix
        supernet = nb.ipam.prefixes.get(prefix=cidr)
        if not supernet:
            print(f"❌ Supernet not found in NetBox: {cidr}")
            skipped_supernet_not_found += 1
            continue

        # Read scope from the supernet
        super_scope_type_raw = getattr(supernet, "scope_type", None)
        super_scope_id = getattr(supernet, "scope_id", None)
        super_scope_type = normalize_scope_type(super_scope_type_raw)

        if not (super_scope_type and super_scope_id):
            print(
                f"⚠️  Supernet {cidr} has NO scope set. Skipping its children.")
            skipped_missing_supernet_scope += 1
            continue

        super_scope_name = get_scope_name(nb, super_scope_type, super_scope_id)

        print(
            f"🔎 Supernet {cidr}: scope_type={super_scope_type} "
            f"scope_name={super_scope_name} (id={super_scope_id})"
        )

        # Get all child prefixes within the supernet (including nested)
        children = list(nb.ipam.prefixes.filter(within=cidr))
        # Some APIs include the supernet itself in `within=`; filter it out explicitly
        children = [p for p in children if p.id != supernet.id]

        print(f"  → Found {len(children)} child prefixes")

        for child in children:
            total_children += 1
            c_scope_type_raw = getattr(child, "scope_type", None)
            c_scope_id = getattr(child, "scope_id", None)
            c_scope_type = normalize_scope_type(c_scope_type_raw)

            if c_scope_type and c_scope_id:
                # Already scoped – do nothing
                skipped_already_scoped += 1
                continue

            # Needs scope; set it to the supernet's scope
            payload = {
                "scope_type": super_scope_type,  # e.g., "dcim.site"
                "scope_id": super_scope_id
            }

            if DRY_RUN:
                print(f"   [DRY] Would set scope for {child.prefix} (ID {child.id}) "
                      f"→ {super_scope_type}:{super_scope_name}")
            else:
                try:
                    child.update(payload)
                    updated += 1
                    print(
                        f"   ✅ Scoped {child.prefix} → {super_scope_type}:{super_scope_name}")
                except Exception as e:
                    print(
                        f"   ❌ Failed to update {child.prefix} (ID {child.id}): {e}")

    # --- Summary ---
    print("\n=== Summary ===")
    print(f"Total child prefixes considered : {total_children}")
    print(f"Updated (newly scoped)          : {updated}")
    print(f"Skipped (already scoped)        : {skipped_already_scoped}")
    print(
        f"Skipped (supernet no scope)     : {skipped_missing_supernet_scope}")
    print(f"Supernets not found             : {skipped_supernet_not_found}")


if __name__ == "__main__":
    main()