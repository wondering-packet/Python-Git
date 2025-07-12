import meraki
import json
import logging

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Load API Key securely ---
with open("Python-Meraki/keys.json", "r") as temp:
    secret = json.load(temp)
    API_KEY = secret["api_key"]

# --- Replace with your network ID ---
NETWORK_ID = "L_669910444571378999"


def main():
    try:
        dashboard = meraki.DashboardAPI(
            api_key=API_KEY,
            suppress_logging=True
        )

        ssids = dashboard.wireless.getNetworkWirelessSsids(NETWORK_ID)
        ssid_list = []
        for each_ssid in ssids:
            info = {
                "number": each_ssid.get("number"),
                "name": each_ssid.get("name"),
                "enabled": each_ssid.get("enabled"),
                "authMode": each_ssid.get("authMode", "N/A"),
                "psk": each_ssid.get("psk"),
                "encryptionMode": each_ssid.get("encryptionMode")
                # "dot11r": each_ssid.get("dot11r", {}).get("enabled", "N/A")

            }
            print(each_ssid)
            ssid_list.append(info)
            logging.info(
                f"#{info['number']} | {info['name']} | "
                f"Enabled: {info['enabled']} | Auth: {info['auth_mode']} | "
                f"PSK: {info['psk']} | "
                # f"dot11r: {info['dot11r']}"
            )
    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()
