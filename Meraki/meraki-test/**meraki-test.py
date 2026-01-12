# 101--compliance_audit_auto_remediation.py
# Meraki compliance script to remediate:
# 1) untagged access+enabled ports
# 2) ports not having org standard port access policy

import meraki
import logging
from pathlib import Path
from datetime import datetime
import requests
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# --- logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- paths ---
base_path = Path("/automation/python-data/meraki-compliance-local")
report_dir = base_path / "remediation_reports"
report_dir.mkdir(parents=True, exist_ok=True)

# --- Load API Key ---
with open("/automation/secrets/keys.json", "r") as temp:
    secret = json.load(temp)
    API_KEY = secret["api_key"]
    TEAMS_WEBHOOK_URL = secret["teams_webhook"]

dashboard = meraki.DashboardAPI(api_key=API_KEY, suppress_logging=True)

# --- compliance config ---
compliance_access_port_policy = "NAC-Test-Policy"
default_tag = "user-port"
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")


def process_device_ports(dashboard, network_id, network_name, each_device,
                         compliance_access_port_policy_number, default_tag, org_name):
    ports_checked = 0
    ports_remediated = 0
    ports_skipped_compliant = 0
    successes = []

    device_id = each_device["serial"]
    device_name = each_device["name"] or "N/A"

    try:
        ports = dashboard.switch.getDeviceSwitchPorts(device_id)
    except Exception as e:
        logging.warning(f"Serial: {device_id} ; Device: {device_name} ; {e}")
        return {"checked": 0, "remediated": 0, "skipped": 0, "successes": []}

    for each_port in ports:
        ports_checked += 1
        port_id = each_port["portId"]
        actions = []
        remediated = False

        if each_port.get("type") == "access" and each_port.get("enabled"):
            policy_num = each_port.get("accessPolicyNumber")

            if policy_num != int(compliance_access_port_policy_number):
                dashboard.switch.updateDeviceSwitchPort(
                    device_id, port_id,
                    accessPolicyType="Custom access policy",
                    accessPolicyNumber=compliance_access_port_policy_number
                )
                actions.append(
                    f"Remediation: assigned default access policy {compliance_access_port_policy}"
                )
                remediated = True

            each_port_tags = each_port.get("tags", [])
            if not each_port_tags:
                dashboard.switch.updateDeviceSwitchPort(
                    device_id, port_id, tags=[default_tag]
                )
                actions.append(
                    f"Remediation: assigned default tag {default_tag}"
                )
                remediated = True

            if remediated:
                ports_remediated += 1
                successes.append({
                    "org_name": org_name,
                    "network_name": network_name,
                    "network_id": network_id,
                    "device_name": device_name,
                    "device_id": device_id,
                    "port_id": port_id,
                    "action": actions
                })
                logging.info(
                    f"\n> Remediated on device: {device_name} - serial: {device_id} - port: {port_id}\n\t>> {actions}"
                )
            else:
                ports_skipped_compliant += 1
        else:
            ports_skipped_compliant += 1

    return {
        "checked": ports_checked,
        "remediated": ports_remediated,
        "skipped": ports_skipped_compliant,
        "successes": successes
    }


def remediate_compliance():
    successes = []
    ports_checked = 0
    ports_skipped_compliant = 0
    ports_remediated = 0

    orgs = dashboard.organizations.getOrganizations()

    for each_org in orgs:
        org_id = each_org["id"]
        org_name = each_org["name"]
        networks = dashboard.organizations.getOrganizationNetworks(org_id)

        for network in networks:
            network_id = network["id"]
            network_name = network["name"]

            devices = dashboard.organizations.getOrganizationDevices(
                org_id, networkIds=network_id
            )

            policies = dashboard.switch.getNetworkSwitchAccessPolicies(
                network_id)
            compliance_access_port_policy_number = None

            for p in policies:
                if p["name"] == compliance_access_port_policy:
                    compliance_access_port_policy_number = p["accessPolicyNumber"]
                    break

            if compliance_access_port_policy_number is None:
                logging.error(
                    f"NAC policy '{compliance_access_port_policy}' not found in '{network_name}'. Skipping."
                )
                continue

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [
                    executor.submit(
                        process_device_ports,
                        dashboard,
                        network_id,
                        network_name,
                        each_device,
                        compliance_access_port_policy_number,
                        default_tag,
                        org_name
                    )
                    for each_device in devices
                ]

                for future in as_completed(futures):
                    res = future.result()
                    ports_checked += res["checked"]
                    ports_remediated += res["remediated"]
                    ports_skipped_compliant += res["skipped"]
                    successes.extend(res["successes"])

    logging.info(
        f"Summary: Ports checked={ports_checked}, Remediated={ports_remediated}, Skipped={ports_skipped_compliant}"
    )
    return successes


def git_commit_snapshots(report_file, tag=None):
    try:
        repo_dir = base_path
        subprocess.run(["git", "-C", repo_dir, "add",
                       str(report_file)], check=True)
        subprocess.run(["git", "-C", repo_dir, "commit", "-m",
                       "Auto Remediation report"], check=True)
        subprocess.run(["git", "-C", repo_dir, "push"], check=True)
        if tag:
            tag_name = f"Auto-remediation-{timestamp}"
            subprocess.run(
                ["git", "-C", repo_dir, "tag", tag_name], check=True)
            subprocess.run(["git", "-C", repo_dir, "push",
                           "origin", tag_name], check=True)
            logging.info(f"Tag {tag_name} pushed.")
        logging.info(f"Committed remediation report to Git: {report_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git commit failed: {e}")


def save_report_and_notify(successes):
    timestamp_now = datetime.now().strftime("%Y-%m-%d-%H-%M")
    report_file = report_dir / f"{timestamp_now}_remediation_report.json"
    with open(report_file, "w") as f:
        json.dump(successes, f, indent=4)
    logging.info(f"Remediation report saved: {report_file}")

    if successes:
        message = f"✅ Meraki Auto Remediation: {len(successes)} ports remediated.\nCheck: {report_file}"
        tag = True
    else:
        message = "✅ Meraki Auto Remediation: All ports already compliant."
        tag = None

    git_commit_snapshots(report_file, tag)

    if TEAMS_WEBHOOK_URL:
        payload = {"text": message}
        try:
            response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
            if response.status_code in [200, 201, 202]:
                logging.info("Teams notification sent.")
            else:
                logging.error(f"Teams notification failed: {response.text}")
        except Exception as e:
            logging.error(f"Teams notification error: {e}")


if __name__ == "__main__":
    start_time = time.perf_counter()
    successes = remediate_compliance()
    save_report_and_notify(successes)
    end_time = time.perf_counter()
    total_time = end_time-start_time
    logging.info(
        f"Time taken (with multi-threading):\n\t<{total_time:.2f}sec>")
