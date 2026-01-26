# WAN IP Ingestion & Cleanup Workflow

## Overview

This workflow consists of **two core scripts** and **one optional validation script**:

1. **`ingest_wan_ip.py`** – Main worker script responsible for ingesting and reconciling WAN IP data.
2. **`clean_deprecated_wan_ip.py`** – Cleanup script for removing stale WAN IPs.
3. **`netbox_ping.py` (optional)** – Validation script for reachability checks.

---

## Script 1: `ingest_wan_ip.py`

This script compares WAN IP data from an external Source of Truth (SoT) with NetBox and reconciles differences.

### Data Sources

The script operates on two datasets:

- **Dataset A** – WAN IPs sourced from a JSON file stored in GitHub.
- **Dataset B** – Existing IP address objects in NetBox.

---

### Dataset A – Sample JSON Structure (GitHub)

```json
{
  "meraki": [
    {
      "ip": "52.14.210.88",
      "infrastructure_type": "Cloud",
      "provider": "AWS",
      "region": "us-east-2",
      "environment": "Production",
      "purpose": "Public Facing Load Balancer",
      "caption": "AWS-ELB-001"
    }
  ],
  "aruba": [
    {
      "ip": "198.51.100.42",
      "infrastructure_type": "Datacenter",
      "provider": "Equinix-Colocation",
      "region": "Chicago-CH3",
      "environment": "Production",
      "purpose": "Primary Edge Firewall (Cisco ASA)",
      "caption": "DC-FW-01-PRI"
    }
  ]
}
```

Each top-level key represents a **platform** (e.g., `meraki`, `aruba`).

---

### Dataset B – Sample NetBox IP Object

```json
{
  "id": 15560,
  "address": "172.16.32.163/16",
  "status": {
    "value": "deprecated",
    "label": "Deprecated"
  },
  "description": "Auto-generated",
  "tags": [
    {
      "name": "phpipam-migrated",
      "slug": "phpipam-migrated"
    }
  ],
  "custom_fields": {},
  "created": "2025-08-01T19:24:03.079399Z",
  "last_updated": "2025-08-01T19:24:03.079411Z"
}
```

---

### Data Normalization & Mapping

A new working dictionary is built from **Dataset A**, containing only fields relevant to NetBox.

#### Property Mapping

| Dataset A                    | Dataset B     |
| ---------------------------- | ------------- |
| `ip`                         | `address`     |
| `caption`                    | `description` |
| platform (`aruba`, `meraki`) | NetBox tag    |
| raw data                     | `comment`     |

> We are punting raw data for the IP from A as a comment for audit and troubleshooting purposes.

#### Additional NetBox Metadata

Create these in NetBox before the workflow goes live.

- **Tags**
  - `External SoT GitHub`
  - `Review-Required`
- **Custom Field**
  - `last_seen` – Timestamp of when the IP was last observed in Dataset A.

---

### Reconciliation Logic

#### Case 1: Exists in A but not in B
- Create IP in NetBox
  - Tag: `External SoT GitHub`
  - Tag: `Aruba` or `Meraki` or whatever the platform is
  - Set `last_seen`
  - Punt raw data for the IP from A as a comment.

#### Case 2: Exists in both A and B
- Update IP details
  - If `External SoT GitHub` exists → update `last_seen`
  - If `manual` tag exists → skip
  - Else → tag `Review-Required` and update `last_seen`

#### Case 3: Exists in B but not in A
- If `External SoT GitHub` exists → set status `deprecated`
- Do **not** update `last_seen`

---

### Review Required tag

IPs tagged `Review-Required` are conflicting WAN IPs that have been either added manually or imported from somewhere else (not ingested from Dataset A), so must be manually validated.

To stop these WAN IPs from being marked as `Review-Required` in future runs, remove `Review-Required` tag and add `manual` tag. WAN IPs tagged `manual` are treated as exceptions.

Goal: **single external Source of Truth for WAN IP ingestion**.

---

## Script 2: `clean_deprecated_wan_ip.py`

Removes stale WAN IPs from NetBox.

### Cleanup Logic

1. Fetch IPs with:
   - Tag `External SoT GitHub`
   - Status `deprecated`
2. Validate `last_seen`
3. If `last_seen` > 90 days → delete IP
4. Otherwise retain as `deprecated`

## Script 3: `netbox_ping.py`

Does basic reachability test to NetBox & GitHub.