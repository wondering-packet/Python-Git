#!/usr/bin/env python3
"""
Extended Prefix scope report (NetBox 4.3.x + pynetbox)

- Totals with/without scope_type
- Breakdown by scope_type (e.g., dcim.site, dcim.region, tenancy.tenant, dcim.location)
- Per-object breakdown for Sites, Regions, Tenants, and Locations
- At the end, list all prefixes without a scope so you can fix them.

Reads NETBOX_URL and API_TOKEN from /automation/secrets/netbox.json
"""

import json
import urllib3
from collections import Counter
import pynetbox

# --- SSL warnings off for self-signed certs ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- Config: secrets file ---
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"].rstrip("/")
    API_TOKEN = secrets["API_TOKEN"]

# --- Connect ---
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

# --- Helpers ---


def normalize_scope_type(scope_type):
    if not scope_type:
        return None
    if isinstance(scope_type, dict):
        app = scope_type.get("app_label") or scope_type.get("app") or ""
        model = scope_type.get("model") or ""
        return ".".join([p for p in (app, model) if p]) or None
    return str(scope_type)


def build_lookup(endpoint, name_attr="name"):
    mapping = {}
    for obj in endpoint.all():
        display = getattr(obj, name_attr, None) or getattr(
            obj, "display", None) or str(obj.id)
        mapping[obj.id] = display
    return mapping


def main():
    prefixes = list(nb.ipam.prefixes.all())

    total = len(prefixes)
    with_scope = 0
    without_scope = 0
    scope_counter = Counter()

    per_site = Counter()
    per_region = Counter()
    per_tenant = Counter()
    per_location = Counter()

    site_lookup = build_lookup(nb.dcim.sites)
    region_lookup = build_lookup(nb.dcim.regions)
    tenant_lookup = build_lookup(nb.tenancy.tenants)
    location_lookup = build_lookup(nb.dcim.locations)

    no_scope_prefixes = []

    for p in prefixes:
        st_raw = getattr(p, "scope_type", None)
        sid = getattr(p, "scope_id", None)
        st = normalize_scope_type(st_raw)

        if st and sid:
            with_scope += 1
            scope_counter[st] += 1

            if st == "dcim.site":
                per_site[sid] += 1
            elif st == "dcim.region":
                per_region[sid] += 1
            elif st == "tenancy.tenant":
                per_tenant[sid] += 1
            elif st == "dcim.location":
                per_location[sid] += 1
        else:
            without_scope += 1
            no_scope_prefixes.append(p)

    print("=== Prefix Scope Report ===")
    print(f"Total prefixes         : {total}")
    print(f"With scope_type set    : {with_scope}")
    print(f"Without scope_type     : {without_scope}")
    pct = (with_scope / total * 100.0) if total else 0.0
    print(f"Percent scoped         : {pct:.2f}%\n")

    print("Breakdown by scope_type:")
    if scope_counter:
        for scope_type, count in scope_counter.most_common():
            print(f"  {scope_type:20s} : {count}")
    else:
        print("  (none)")
    print()

    print("Per-Site scoped prefixes:")
    for sid, count in sorted(per_site.items(), key=lambda kv: (-kv[1], site_lookup.get(kv[0], str(kv[0])))):
        print(f"  {site_lookup.get(sid, f'id={sid}'):30s} : {count}")
    print()

    print("Per-Region scoped prefixes:")
    for rid, count in sorted(per_region.items(), key=lambda kv: (-kv[1], region_lookup.get(kv[0], str(kv[0])))):
        print(f"  {region_lookup.get(rid, f'id={rid}'):30s} : {count}")
    print()

    print("Per-Tenant scoped prefixes:")
    for tid, count in sorted(per_tenant.items(), key=lambda kv: (-kv[1], tenant_lookup.get(kv[0], str(kv[0])))):
        print(f"  {tenant_lookup.get(tid, f'id={tid}'):30s} : {count}")
    print()

    print("Per-Location scoped prefixes:")
    for lid, count in sorted(per_location.items(), key=lambda kv: (-kv[1], location_lookup.get(kv[0], str(kv[0])))):
        print(f"  {location_lookup.get(lid, f'id={lid}'):30s} : {count}")
    print()

    print("=== Prefixes WITHOUT scope_type ===")
    if no_scope_prefixes:
        for p in no_scope_prefixes:
            print(f"- {p.prefix:20s}  (ID {p.id}, Description='{p.description}')")
    else:
        print("All prefixes have scope_type set ✅")


if __name__ == "__main__":
    main()
