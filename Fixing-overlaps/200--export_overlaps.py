'''
export all the vlans data. fetched using meraki API.
the output file will need to be manually renamed to 200-meraki_vlan_details_old.csv later.
'''
import meraki
import csv
import os
from datetime import datetime
import ipaddress
import keyring

# ---- CONFIGURATION ----
API_KEY = keyring.get_password("meraki", "api_key")
OUTPUT_FILE = r"c:\temp\netbox\200-meraki_vlan_details_latest.csv"
LOG_LEVEL = "info"  # 'debug', 'info', 'warning', 'error', 'critical'

# ---- INITIALIZE MERAKI DASHBOARD ----
dashboard = meraki.DashboardAPI(
    api_key=API_KEY,
    output_log=True,
    log_file_prefix='meraki_api_log',
    print_console=True,
    suppress_logging=False,
)

# ---- MAIN FUNCTION ----
def fetch_vlan_details():
    results = []
    stats = {}

    try:
        print("Fetching organizations...")
        organizations = dashboard.organizations.getOrganizations()

        for org in organizations:
            org_id = org['id']
            org_name = org.get('name', 'N/A')
            print(f"\n[ORG] {org_name} (ID: {org_id})")

            # Initialize stats for this org
            stats[org_id] = {
                'org_name': org_name,
                'networks_discovered': 0,
                'vlans_discovered': 0,
                'csv_rows_written': 0,
            }

            try:
                networks = dashboard.organizations.getOrganizationNetworks(org_id)
                stats[org_id]['networks_discovered'] = len(networks)

                for net in networks:
                    network_id = net['id']
                    network_name = net.get('name', 'N/A')
                    print(f"  ↳ [NET] {network_name} (ID: {network_id})")

                    try:
                        vlans = dashboard.appliance.getNetworkApplianceVlans(network_id)
                        stats[org_id]['vlans_discovered'] += len(vlans)

                        for vlan in vlans:
                            vlan_id = vlan.get('id', 'N/A')
                            vlan_name = vlan.get('name', 'N/A')
                            appliance_ip = vlan.get('applianceIp', 'N/A')
                            subnet = vlan.get('subnet', '')

                            interface_ip = "N/A"
                            if appliance_ip != 'N/A' and subnet:
                                try:
                                    net_obj = ipaddress.IPv4Network(subnet, strict=False)
                                    cidr_suffix = net_obj.prefixlen
                                    interface_ip = f"{appliance_ip}/{cidr_suffix}"
                                except Exception as e:
                                    print(f"    [!] Error calculating CIDR for VLAN {vlan_id}: {e}")
                                    interface_ip = appliance_ip

                            results.append({
                                'Org ID': org_id,
                                'Org Name': org_name,
                                'Network ID': network_id,
                                'Network Name': network_name,
                                'VLAN ID': vlan_id,
                                'VLAN Name': vlan_name,
                                'VLAN Interface IP': interface_ip,
                            })

                            stats[org_id]['csv_rows_written'] += 1

                    except meraki.APIError as e:
                        print(f"    [!] Error fetching VLANs for network {network_name}: {e}")
                    except Exception as e:
                        print(f"    [!] Unexpected error for network {network_name}: {e}")

            except meraki.APIError as e:
                print(f"[!] Error fetching networks for org {org_name}: {e}")
            except Exception as e:
                print(f"[!] Unexpected error fetching networks for org {org_name}: {e}")

    except meraki.APIError as e:
        print(f"[!] Error fetching organizations: {e}")
    except Exception as e:
        print(f"[!] Unexpected error fetching organizations: {e}")

    return results, stats

# ---- WRITE TO CSV ----
def write_to_csv(data, filename):
    if not data:
        print("No data to write.")
        return

    fieldnames = list(data[0].keys())

    try:
        with open(filename, mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        print(f"\n✅ Output written to: {filename}")

    except Exception as e:
        print(f"[!] Error writing to CSV: {e}")

def print_stats(stats):
    print("\n\n📊 --- Summary Stats by Organization ---")
    for org_id, data in stats.items():
        print(f"\nOrg: {data['org_name']} (ID: {org_id})")
        print(f"  Networks discovered     : {data['networks_discovered']}")
        print(f"  VLANs discovered        : {data['vlans_discovered']}")
        print(f"  Rows written to CSV     : {data['csv_rows_written']}")

# ---- EXECUTION START ----
if __name__ == "__main__":
    vlan_data, stats = fetch_vlan_details()
    write_to_csv(vlan_data, OUTPUT_FILE)
    print_stats(stats)
