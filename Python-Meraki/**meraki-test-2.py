import meraki
import logging
import json

# --- Setup basic logging; this will be common across all scripts FYI ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- loading key from a file; this will be common across all scripts FYI ---
# you should place your key somewhere safe. my key is not part of the git.

with open("/automation/secrets/keys.json", "r") as temp:
    secret = json.load(temp)
    API_KEY = secret["api_key"]


def main():
    try:
        dashboard = meraki.DashboardAPI(
            api_key=API_KEY,
            suppress_logging=True  # Optional: disables verbose HTTP logs
        )

        orgs = dashboard.organizations.getOrganizations()
        for each_org in orgs:
            org_id = each_org["id"]
            networks = dashboard.organizations.getOrganizationNetworks(
                org_id)
            # --- device ports ---
            for network in networks:
                network_id = network["id"]
                devices = dashboard.switch.getOrganizationSwitchPortsBySwitch(
                    org_id, networkIds=network_id)
                # logging.info(f"@@@---\n{devices}--@@@")
                for device in devices:
                    try:
                        # logging.info(
                        #     f"@@@--device\n{device["serial"]}$${device["name"]}--@\n")
                        device_id = device["serial"]
                        ports = dashboard.switch.getDeviceSwitchPorts(
                            device_id)
                        logging.info(f"@@@---\n{ports}--@@@")
                    except Exception as e:
                        logging.error(f"Error: {e}")
    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()
