# 101--compliance_audit_auto_remediation.py

import meraki
import logging
import json
from pathlib import Path
from datetime import datetime
import requests

# --- Setup ---
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

base_path = Path("/automation/python-data/")
report_dir = base_path / "compliance_reports"
report_dir.mkdir(parents=True, exist_ok=True)

with open("/automation/secrets/keys.json", "r") as f:
    secret = json.load(f)
    API_KEY = secret["api_key"]
    TEAMS_WEBHOOK_URL = secret["teams_webhook"]

dashboard = meraki.DashboardAPI(api_key=API_KEY, suppress_logging=True)

compliance_access_port_policy = "NAC-Test-Policy"
default_tag = "user-port"


def remediate_compliance():
    remediated_ports = []
    orgs = dashboard.organizations.getOrganizations()

    for org in orgs:
        org_id = org["id"]
        org_name = org["name"]
        networks = dashboard.organizations.getOrganizationNetworks(org_id)

        for network in networks:
            network_id = network["id"]
            network_name = network["name"]
            devices = dashboard.organizations.getOrganizationDevices(
                org_id, networkIds=network_id)

            for device in devices:
                device_id = device["serial"]
                device_name = device["name"] or "N/A"

                try:
                    ports = dashboard.switch.getDeviceSwitchPorts(device_id)
                except Exception as e:
                    logging.warning(
                        f"Serial: {device_id} ; Device: {device_name} ; {e}")
                    continue

                for port in ports:
                    if port.get("type") != "access" or not port.get("enabled", True):
                        continue  # skip non-access or disabled ports

                    port_id = port["portId"]
                    actions = []

                    # --- Check & remediate tag ---
                    tags = port.get("tags", [])
                    if not tags:
                        try:
                            dashboard.switch.updateDeviceSwitchPort(
                                device_id, port_id, tags=[default_tag])
                            actions.append("Assigned default tag 'user-port'")
                        except Exception as e:
                            logging.error(
                                f"Failed to assign tag on {device_name} {port_id}: {e}")

                    # --- Check & remediate access policy ---
                    policy_name = port.get("accessPolicyType")
                    if policy_name == "Custom access policy":
                        policy_num = port.get("accessPolicyNumber")
                        policy_data = dashboard.switch.getNetworkSwitchAccessPolicy(
                            network_id, policy_num)
                        policy_name = policy_data["name"]

                    if policy_name != compliance_access_port_policy:
                        try:
                            dashboard.switch.updateDeviceSwitchPort(
                                device_id, port_id, accessPolicyType=compliance_access_port_policy
                            )
                            actions.append(
                                f"Assigned access policy '{compliance_access_port_policy}'")
                        except Exception as e:
                            logging.error(
                                f"Failed to assign policy on {device_name} {port_id}: {e}")

                    if actions:
                        remediated_ports.append({
                            "org_name": org_name,
                            "network_name": network_name,
                            "device_name": device_name,
                            "device_id": device_id,
                            "port_id": port_id,
                            "actions": actions
                        })
    return remediated_ports


def save_remediation_report_and_notify(remediated_ports):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    report_file = report_dir / f"{timestamp}_remediation_report.json"
    with open(report_file, "w") as f:
        json.dump(remediated_ports, f, indent=4)

    logging.info(f"Remediation report saved: {report_file}")

    if remediated_ports:
        message = f"Meraki Auto-Remediation: {len(remediated_ports)} ports remediated."
    else:
        message = "Meraki Auto-Remediation: No remediation required."

    if TEAMS_WEBHOOK_URL:
        payload = {"text": message}
        try:
            response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
            if response.status_code in [200, 201, 202]:
                logging.info("Teams notification sent successfully.")
            else:
                logging.error(f"Teams notification failed: {response.text}")
        except Exception as e:
            logging.error(f"Teams notification error: {e}")


if __name__ == "__main__":
    remediated_ports = remediate_compliance()
    save_remediation_report_and_notify(remediated_ports)
