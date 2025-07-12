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

        # below, we are passing NETWORK_ID. this is a required argument for this API call.
        # you will have to figure out the required arguments for each API call.
        # you can find them in below documentation:
        # https://developer.cisco.com/meraki/api-v1/
        # just expand the API tree from left & navigate to the API call.
        devices = dashboard.networks.getNetworkDevices(NETWORK_ID)
        logging.info(
            f"Found {len(devices)} device(s) in network {NETWORK_ID}.")

        device_list = []        # object which will hold our JSON file later.
        for device in devices:
            logging.info(
                f"\n@@@\nRaw data from device_list object: \n{device}\n@@@")
            info = {
                "name": device.get("name", "N/A"),
                "model": device.get("model", "N/A"),
                "mac": device.get("mac", "N/A"),
                "serial": device.get("serial", "N/A"),
                "lan_ip": device.get("lanIp", "N/A"),
                "public_ip": device.get("wan1Ip", "N/A")
            }
            device_list.append(info)
            logging.info(
                f"{info['name']} | {info['model']} | "
                f"MAC: {info['mac']} | Serial: {info['serial']} | "
                f"LAN IP: {info['lan_ip']} | Public IP: {info['public_ip']}"
            )

        # save to devices.json using device_list object
        with open("Python-Meraki/data/devices.json", "w") as outfile:
            json.dump(device_list, outfile, indent=4)
        logging.info("Device list saved to devices.json.")

    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()
