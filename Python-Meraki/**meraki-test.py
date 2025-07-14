# 100-compliance_audit.py
# Performs compliance audit:
# ✅ All access switch ports must have "NAC-Test-Policy"
# ✅ All access switch ports must have at least one tag
# ✅ Generates JSON + Teams alert if non-compliance is found
# ✅ Designed for CRON and Git automation

import meraki
import json
import logging
from pathlib import Path
from datetime import datetime
import requests

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Paths ---
base_path = Path("/automation/python-data/")
report_dir = base_path / "compliance_reports"
report_dir.mkdir(parents=True, exist_ok=True)

# --- Load API Key ---
with open("/automation/secrets/keys.json", "r") as f:
    API_KEY = json.load(f)["api_key"]

# --- Teams Webhook ---
TEAMS_WEBHOOK_URL = "https://your-teams-webhook-url"

# --- Initialize Meraki Dashboard ---
dashboard = meraki.DashboardAPI(api_key=API_KEY, suppress_logging=True)

# --- Compliance Logic ---


def check_compliance():
    failures = []
    orgs = dashboard.organizations.getOrganizations()

    for org in orgs:
        org_id = org["id"]
        networks = dashboard.organizations.getOrganizationNetworks(org_id)

        for net in networks:
            network_id = net["id"]
            try:
                ports = dashboard.switch.getNetworkSwitchPorts(network_id)
            except Exception as e:
                logging.warning(f"Skipping network {network_id}: {e}")
                continue

            for port in ports:
                port_id = port["portId"]
                compliance = True
                reasons = []

                # Check if access port
                if port.get("type") == "access":
                    # Check NAC policy
                    policy_name = port.get("accessPolicyType")
                    if policy_name != "NAC-Test-Policy":
                        compliance = False
                        reasons.append(
                            f"Expected NAC-Test-Policy, found {policy_name}")

                    # Check tags
                    tags = port.get("tags", [])
                    if not tags:
                        compliance = False
                        reasons.append("No tags assigned")

                if not compliance:
                    failures.append({
                        "org_name": org["name"],
                        "network_name": net["name"],
                        "network_id": network_id,
                        "port_id": port_id,
                        "reasons": reasons
                    })

    return failures

# --- Save and Notify ---


def save_report_and_notify(failures):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    report_file = report_dir / f"{timestamp}_compliance_report.json"

    with open(report_file, "w") as f:
        json.dump(failures, f, indent=4)

    logging.info(f"Compliance report saved: {report_file}")

    # Send Teams Notification
    if failures:
        summary = f"🚨 Meraki Compliance Audit: {len(failures)} non-compliant ports found."
    else:
        summary = "✅ Meraki Compliance Audit: All ports compliant."

    payload = {
        "text": summary
    }

    try:
        response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
        if response.status_code == 200:
            logging.info("Teams notification sent.")
        else:
            logging.error(
                f"Teams notification failed: {response.status_code} {response.text}")
    except Exception as e:
        logging.error(f"Teams notification error: {e}")


# --- Main ---
if __name__ == "__main__":
    failures = check_compliance()
    save_report_and_notify(failures)
