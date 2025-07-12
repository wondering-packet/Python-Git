import meraki
import json
import logging

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

with open("Python-Meraki/keys.json", "r") as temp:
    secret = json.load(temp)
    API_KEY = secret["api_key"]

NETWORK_ID = "L_669910444571378999"


def get_ssids(dashboard):
    try:
        ssids = dashboard.wireless.getNetworkWirelessSsids(NETWORK_ID)
        ssid_list = []
        for each_ssid in ssids:
            info = {
                # you will have to be aware of the key names. For a list of keys, check out the API docs.
                "number": each_ssid.get("number"),
                "name": each_ssid.get("name"),
                "enabled": each_ssid.get("enabled"),
                "authMode": each_ssid.get("authMode"),
                "psk": each_ssid.get("psk"),
                "encryptionMode": each_ssid.get("encryptionMode", "N/A"),
                "dot11r": each_ssid.get("dot11r", {}).get("enabled", "N/A")
                # ^^ add whatever else you need. for a list of all available parameters,
                # you can try printing the each_ssid object or you can visit:
                # https://developer.cisco.com/meraki/api-v1/get-network-wireless-ssids/
            }
            # print(each_ssid)
            ssid_list.append(each_ssid)
            logging.info(
                f"#{info['number']} | {info['name']} | "
                f"Enabled: {info['enabled']} | Auth: {info['authMode']} | "
                f"PSK: {info['psk']} | encryptionMode: {info['encryptionMode']} | "
                f"dot11r: {info['dot11r']}"
            )
    except Exception as e:
        logging.error(f"Error: {e}")


def update_ssid(dashboard, ssid_num, enable=None, new_psk=None):
    # this is the dictionary which will passed as a payload.
    payload = {}
    # simple expression to identify whether enable is anything except NONE.
    # the main() function is only passing True or False for this parameter so,
    # enable's value (either True or False) is assigned to the "enabled" key.
    # note that in the if expression, any non-empty value (empty = NONE) becomes True.
    if enable is not None:
        payload["enabled"] = enable
    if new_psk:     # no psk would mean empty string is passed, which would evaluate as False.
        payload["psk"] = new_psk

    if not payload:
        logging.info("No updates requested. Skipping.")
        return

    # in the below api call, there are 2 required arguments. You will have to figure this out for each API call.
    respone = dashboard.wireless.updateNetworkWirelessSsid(
        NETWORK_ID,     # 1st required argument.
        # 2nd required argument. 3rd & so on are optional arguments.
        ssid_num,
        # ** is used to send the payload dictionary.
        # meraki module will convert this to a proper json before pushing to the meraki dashboard.
        **payload
    )
    logging.info(f"Updated SSID #{ssid_num}: \n\n{respone}\n\n")


def main():
    try:
        dashboard = meraki.DashboardAPI(
            api_key=API_KEY,
            suppress_logging=True
        )
    except Exception as e:
        logging.error(f"Error: {e}")

    get_ssids(dashboard)

    choice = input("Do you want to update an SSID (y/n)? ").lower().strip()
    if choice == "y":
        ssid_num = input("Enter the SSID number to modify: ")
        enable_ssid = input(
            "Do you want to enable this SSID (y/n): ").lower().strip()
        if enable_ssid == "y":
            enable = True
        elif enable_ssid == "n":
            enable = False
        else:
            enable = None
        new_psk = input(
            "Enter new PSK for the SSID (or press Enter to skip): ")
        update_ssid(dashboard, ssid_num, enable, new_psk)


if __name__ == "__main__":
    main()
