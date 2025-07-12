# manage_ssids script contains this logic already, so if you understand that then skip this one

import meraki
import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

with open("../Secrets/keys.json", "r") as temp:
    secret = json.load(temp)
    API_KEY = secret["api_key"]

NETWORK_ID = "L_669910444571378999"


def main():
    try:
        dashboard = meraki.DashboardAPI(
            api_key=API_KEY,
            suppress_logging=True
        )

        ssids = dashboard.wireless.getNetworkWirelessSsids(NETWORK_ID)
        logging.info(f"Found {len(ssids)} SSID(s) in network {NETWORK_ID}.")

        ssid_list = []
        for ssid in ssids:
            info = {
                "number": ssid.get("number"),
                "name": ssid.get("name"),
                "enabled": ssid.get("enabled"),
                "auth_mode": ssid.get("authMode"),
                "psk": ssid.get("psk", "N/A")
            }
            ssid_list.append(info)
            logging.info(
                f"#{info['number']} | {info['name']} | "
                f"Enabled: {info['enabled']} | Auth: {info['auth_mode']} | "
                f"PSK: {info['psk']}"
            )

        # Optional: save to ssids.json
        with open("Python-Meraki/data/ssids.json", "w") as outfile:
            json.dump(ssid_list, outfile, indent=4)
        logging.info("SSID list saved to ssids.json.")

    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()
