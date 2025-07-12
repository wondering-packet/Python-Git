import meraki
import json
import logging
from datetime import datetime
from pathlib import Path

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Load API Key securely ---
with open("../Secrets/keys.json", "r") as f:
    secret = json.load(f)
    API_KEY = secret["api_key"]

# --- Paths ---
today_str = datetime.now().strftime("%Y-%m-%d")
save_dir = Path(f"Python-Meraki/data/{today_str}")
save_dir.mkdir(parents=True, exist_ok=True)

# --- Network ID you are working on ---
NETWORK_ID = "L_669910444571378999"


def save_json(data, filename):
    with open(save_dir / filename, "w") as f:
        json.dump(data, f, indent=4)
    logging.info(f"Saved {filename}")


def snapshot():
    dashboard = meraki.DashboardAPI(api_key=API_KEY, suppress_logging=True)

    # --- Orgs & Networks ---
    orgs = dashboard.organizations.getOrganizations()
    save_json(orgs, "organizations.json")

    for org in orgs:
        org_id = org["id"]
        networks = dashboard.organizations.getOrganizationNetworks(org_id)
        save_json(networks, f"networks_{org_id}.json")

    # --- Devices ---
    devices = dashboard.networks.getNetworkDevices(NETWORK_ID)
    save_json(devices, f"devices_{NETWORK_ID}.json")

    # --- SSIDs ---
    ssids = dashboard.wireless.getNetworkWirelessSsids(NETWORK_ID)
    save_json(ssids, f"ssids_{NETWORK_ID}.json")

    # --- Devices Ports ---
    for device in devices:
        serial = device.get("serial")
        try:
            ports = dashboard.switch.getDeviceSwitchPorts(serial)
            save_json(ports, f"ports_{serial}.json")
        except Exception as e:
            logging.warning(
                f"Skipping ports for {serial} (likely not a switch): {e}")

    logging.info("Nightly snapshot completed successfully.")


if __name__ == "__main__":
    snapshot()
