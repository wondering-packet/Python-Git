'''
processes the 402 file & creates subnets.
'''
import pynetbox
import pandas as pd
import ipaddress
import logging
import urllib3
import os
import keyring
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# --- CONFIGURATION ---
API_TOKEN = keyring.get_password("netbox", "api_key")
NETBOX_URL = keyring.get_password("netbox_url", "netbox_url")
CSV_FILE = r"c:\temp\netbox\402-retail_filtered_subnets_with_roles.csv"
FAILURE_CSV = r"c:\temp\netbox\208-logs-prefix_creation_failures.csv"
SKIPPED_CSV = r"c:\temp\netbox\208-logs-prefix_skipped_audit.csv"
LOG_FILE = r"c:\temp\netbox\208-logs-prefix_creation_failures.log"
MAX_WORKERS = 10

# --- Setup ---
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
console_log_prefix = "[*]"
start_time = datetime.now()
logging.info("=== Prefix creation script started ===")

# --- Connect to NetBox ---
try:
    nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
    nb.http_session.verify = False
    print(f"{console_log_prefix} Connected to NetBox at {NETBOX_URL}")
except Exception as e:
    logging.error(f"Could not connect to NetBox: {e}")
    print(f"[!] Failed to connect to NetBox: {e}")
    exit(1)

# --- Load CSV ---
if os.path.exists(FAILURE_CSV):
    print(f"{console_log_prefix} Failure CSV detected: {FAILURE_CSV}")
    try:
        df = pd.read_csv(FAILURE_CSV, encoding="latin1")
        print(f"{console_log_prefix} Retrying {len(df)} failed rows.")
    except Exception as e:
        logging.error(f"Error reading failure CSV: {e}")
        print(f"[!] Error reading failure CSV: {e}")
        exit(1)
else:
    print(f"{console_log_prefix} No failure CSV found. Running full import.")
    try:
        df = pd.read_csv(CSV_FILE, encoding="latin1")
        print(f"{console_log_prefix} Loaded {len(df)} rows from full input CSV.")
    except Exception as e:
        logging.error(f"Failed to read input CSV: {e}")
        print(f"[!] Error reading input CSV: {e}")
        exit(1)

# --- Shared Data ---
TENANT_NAME = "Retail"
tenant = nb.tenancy.tenants.get(name=TENANT_NAME)
if not tenant:
    print(f"[!] Tenant '{TENANT_NAME}' not found. Exiting.")
    exit(1)

tag_name = "rt-xyz"
tenant_id = tenant.id
tag = nb.extras.tags.get(name=tag_name)
tag_id = tag.id if tag else None

# --- Thread-safe counters ---
created_count = 0
skipped_count = 0
error_count = 0
lock = threading.Lock()
failed_rows = []
skipped_rows = []

def get_role_id(role_name):
    role = nb.ipam.roles.get(name=role_name)
    if role:
        return role.id
    else:
        print(f"[!] Role '{role_name}' not found.")
        return None

# --- Prefix Creation Logic ---
def process_row(index, row):
    global created_count, skipped_count, error_count

    try:
        site_name = str(row["Network Name"]).strip()
        vlan_id = int(row["VLAN ID"])
        vlan_name = str(row["VLAN Name"]).strip()
        prefix_cidr = str(row["VLAN Network ID"]).strip()
        role = str(row["Role"]).strip()
        role_id = get_role_id(role)

        try:
            ipaddress.IPv4Network(prefix_cidr)
        except Exception as e:
            msg = f"Invalid prefix '{prefix_cidr}' → {e}"
            logging.warning(msg)
            row_copy = row.copy()
            row_copy["Reason"] = f"Invalid prefix: {e}"
            row_copy["skipped_at"] = datetime.now().isoformat()
            with lock:
                skipped_count += 1
                skipped_rows.append(row_copy)
            return f"[!] {msg}"

        site = nb.dcim.sites.get(name=site_name)
        if not site:
            msg = f"Site '{site_name}' not found. Skipping prefix '{prefix_cidr}'."
            logging.warning(msg)
            row_copy = row.copy()
            row_copy["Reason"] = "Site not found"
            row_copy["skipped_at"] = datetime.now().isoformat()
            with lock:
                skipped_count += 1
                skipped_rows.append(row_copy)
            return f"[!] {msg}"

        matching_vlans = nb.ipam.vlans.filter(vid=vlan_id)
        filtered_vlans = [
            vlan for vlan in matching_vlans
            if (vlan.group and vlan.group.name == "Retail-VLANs") or
               (vlan.tenant and vlan.tenant.name == "Retail")
        ]
        if not filtered_vlans:
            msg = f"No matching VLAN found for ID '{vlan_id}' in group 'Retail-VLANs' or tenant 'Retail'. Skipping prefix '{prefix_cidr}'."
            logging.warning(msg)
            row_copy = row.copy()
            row_copy["Reason"] = "VLAN not found in Retail-VLANs or Retail tenant"
            row_copy["skipped_at"] = datetime.now().isoformat()
            with lock:
                skipped_count += 1
                skipped_rows.append(row_copy)
            return f"[!] {msg}"

        vlan = filtered_vlans[0]

        existing = nb.ipam.prefixes.get(prefix=prefix_cidr)
        if existing:
            msg = f"Prefix '{prefix_cidr}' already exists. Skipping."
            row_copy = row.copy()
            row_copy["Reason"] = "Prefix already exists"
            row_copy["skipped_at"] = datetime.now().isoformat()
            with lock:
                skipped_count += 1
                skipped_rows.append(row_copy)
            return f"[-] {msg}"

        prefix_data = {
            "prefix": prefix_cidr,
            "vlan": vlan.id,
            "description": f"{site_name} - {vlan_name}",
            "status": "active",
            "tenant": tenant_id,
            "tags": [tag_id] if tag_id else [],
            "scope_type": "dcim.site",
            "scope_id": site.id,
            "role": role_id,
        }

        new_prefix = nb.ipam.prefixes.create(prefix_data)

        if new_prefix:
            with lock:
                created_count += 1
            return f"[+] Created prefix: {prefix_cidr} ({site_name})"
        else:
            raise Exception("Unknown error: prefix not created.")

    except Exception as e:
        msg = f"Unexpected error processing row {index + 1} → {e}"
        logging.exception(msg)
        with lock:
            error_count += 1
            failed_rows.append(row)
        return f"[!] {msg}"

# --- Threaded Execution ---
def run_multithreaded():
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(process_row, idx, row): idx for idx, row in df.iterrows()
        }
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    print(result)
            except Exception as e:
                logging.error(f"Unhandled error in thread: {e}")

# --- Main ---
if __name__ == "__main__":
    print(f"{console_log_prefix} Starting multithreaded prefix creation...")
    run_multithreaded()

    # --- Write failed rows for retry ---
    if failed_rows:
        failure_df = pd.DataFrame(failed_rows)
        failure_df.to_csv(FAILURE_CSV, index=False, encoding='utf-8')
        print(f"\n[!] {len(failed_rows)} errors logged to: {FAILURE_CSV}")
    else:
        if os.path.exists(FAILURE_CSV):
            os.remove(FAILURE_CSV)
        print(f"\n[✔] No errors. {FAILURE_CSV} removed if it existed.")

    # --- Append skipped rows with reasons and timestamps ---
    if skipped_rows:
        skipped_df = pd.DataFrame(skipped_rows)

        if os.path.exists(SKIPPED_CSV):
            existing_df = pd.read_csv(SKIPPED_CSV, encoding='utf-8', on_bad_lines='skip')
            combined_df = pd.concat([existing_df, skipped_df], ignore_index=True)
            combined_df.drop_duplicates(
                subset=["VLAN Network ID", "Network Name", "VLAN ID"],
                keep="last",
                inplace=True
            )
        else:
            combined_df = skipped_df

        combined_df.to_csv(SKIPPED_CSV, index=False, encoding='utf-8')
        print(f"[ℹ] {len(skipped_rows)} skipped rows appended to: {SKIPPED_CSV}")
    else:
        print(f"[✔] No skipped prefixes this run.")

    # --- Final Summary ---
    end_time = datetime.now()
    duration = end_time - start_time

    print("\n=== Summary ===")
    print(f"[✔] Created: {created_count}")
    print(f"[–] Skipped : {skipped_count}")
    print(f"[✖] Errors  : {error_count}")
    print(f"[🕒] Duration: {duration}")
    print(f"[📄] Log file: {os.path.abspath(LOG_FILE)}")

    logging.info("=== Script completed ===")
    logging.info(f"Created: {created_count}, Skipped: {skipped_count}, Errors: {error_count}")
