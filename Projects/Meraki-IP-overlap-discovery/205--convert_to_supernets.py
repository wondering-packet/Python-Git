'''
this script processed the output file from 200.
it assumes all /26 are carved out of a respective parent /24 subnet.
supernet = /24
subnet = /26
this final list contains the list of all such /24 supernets.
note that these /24 supernets are filtered. e.g.:
1. unclean subents are not summarized to the supernet. (e.g. it's a /27 instead of a /26)
2. script assumes exactly 4 subents are needed to form a supernet. exceptions are dropped & logged.
'''
import csv
import ipaddress
from collections import defaultdict
import logging

# --- Configuration ---
INPUT_CSV = r"c:\temp\netbox\200-meraki_vlan_details_old.csv"
OUTPUT_CSV = r"c:\temp\netbox\205-meraki_supernet_summary.csv"
FAILURE_LOG_CSV = r"c:\temp\netbox\205-logs-meraki_failed_entries_log.csv"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def extract_subnet(interface_ip):
    """Extracts subnet from CIDR notation (e.g., 192.168.1.1/26 → 192.168.1.0/26)."""
    try:
        ip_net = ipaddress.IPv4Interface(interface_ip).network
        return ip_net
    except Exception as e:
        logging.warning(f"Invalid IP interface '{interface_ip}': {e}")
        return None

def summarize_subnets(subnets):
    """Summarize list of /26 subnets. Returns /24 if clean, else None."""
    try:
        collapsed = list(ipaddress.collapse_addresses(subnets))
        if len(collapsed) == 1 and collapsed[0].prefixlen == 24:
            return str(collapsed[0])
    except Exception as e:
        logging.warning(f"Error summarizing subnets: {e}")
    return None

def main():
    network_subnets = defaultdict(list)
    network_metadata = {}
    failure_log = []

    logging.info(f"📥 Reading input CSV: {INPUT_CSV}")
    with open(INPUT_CSV, mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            interface_ip = row['VLAN Interface IP']
            subnet = extract_subnet(interface_ip)

            if subnet:
                net_id = row['Network ID']
                network_subnets[net_id].append(subnet)
                if net_id not in network_metadata:
                    network_metadata[net_id] = {
                        'org_id': row['Org ID'],
                        'org_name': row['Org Name'],
                        'network_name': row['Network Name'],
                    }
            else:
                # Log failure for invalid IP
                failure_log.append({
                    'Org ID': row['Org ID'],
                    'Org Name': row['Org Name'],
                    'Network ID': row['Network ID'],
                    'Network Name': row['Network Name'],
                    'Reason': f"Invalid IP: {interface_ip}",
                    'Data': interface_ip
                })

    logging.info("🔍 Validating subnet counts and summarizing supernets...\n")
    output = []

    for net_id, subnets in network_subnets.items():
        meta = network_metadata[net_id]
        subnet_count = len(subnets)

        if subnet_count != 4:
            logging.warning(f"⚠️ Network '{meta['network_name']}' has {subnet_count} subnets (expected 4)")
            failure_log.append({
                'Org ID': meta['org_id'],
                'Org Name': meta['org_name'],
                'Network ID': net_id,
                'Network Name': meta['network_name'],
                'Reason': f"Expected 4 subnets, found {subnet_count}",
                'Data': ', '.join(str(s) for s in subnets)
            })

        supernet = summarize_subnets(subnets)
        if not supernet:
            logging.warning(f"⚠️ Network '{meta['network_name']}' subnets do not cleanly summarize to /24: {[str(s) for s in subnets]}")
            failure_log.append({
                'Org ID': meta['org_id'],
                'Org Name': meta['org_name'],
                'Network ID': net_id,
                'Network Name': meta['network_name'],
                'Reason': f"Subnets do not summarize to /24",
                'Data': ', '.join(str(s) for s in subnets)
            })
            supernet = "INVALID"

        output.append({
            'Org ID': meta['org_id'],
            'Org Name': meta['org_name'],
            'Network ID': net_id,
            'Network Name': meta['network_name'],
            'Supernet (/24)': supernet
        })

    # Sort by supernet (put 'INVALID' at bottom)
    output.sort(key=lambda x: (
        ipaddress.IPv4Network(x['Supernet (/24)']) if x['Supernet (/24)'] != "INVALID" else ipaddress.IPv4Network("255.255.255.255")
    ))

    logging.info(f"\n💾 Writing output to {OUTPUT_CSV}")
    with open(OUTPUT_CSV, mode='w', newline='') as out:
        fieldnames = ['Org ID', 'Org Name', 'Network ID', 'Network Name', 'Supernet (/24)']
        writer = csv.DictWriter(out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output)

    if failure_log:
        logging.info(f"🛠 Writing failure log to {FAILURE_LOG_CSV}")
        with open(FAILURE_LOG_CSV, mode='w', newline='') as fail_out:
            fail_fields = ['Org ID', 'Org Name', 'Network ID', 'Network Name', 'Reason', 'Data']
            writer = csv.DictWriter(fail_out, fieldnames=fail_fields)
            writer.writeheader()
            writer.writerows(failure_log)
    else:
        logging.info("✅ No failures to log.")

    logging.info("✅ Done.")

if __name__ == "__main__":
    main()
