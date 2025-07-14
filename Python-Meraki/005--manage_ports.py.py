import meraki
import json
import logging

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

with open("/automation/secrets/keys.json", "r") as temp:
    secret = json.load(temp)
    API_KEY = secret["api_key"]

NETWORK_ID = "L_669910444571378999"


def get_ports(dashboard, serial):
    try:
        ports = dashboard.switch.getDeviceSwitchPorts(serial)
        logging.info(f"Found {len(ports)} port(s) on device {serial}.")
        port_list = []
        for each_port in ports:
            info = {
                # you will have to be aware of the key names. For a list of keys, check out the API docs.
                "portId": each_port.get("portId"),
                "name": each_port.get("name"),
                "enabled": each_port.get("enabled"),
                "vlan": each_port.get("vlan"),
                "type": each_port.get("type"),
                "poeEnabled": each_port.get("poeEnabled")
                # ^^ add whatever else you need. for a list of all available parameters,
                # you can try printing the each_port object or you can visit:
                # https://developer.cisco.com/meraki/api-v1/
            }
            # print(each_port)
            port_list.append(each_port)
            logging.info(
                f"Port {info['portId']} | Name: {info['name']} | Enabled: {info['enabled']} | "
                f"VLAN: {info['vlan']} | Type: {info['type']} | PoE: {info['poeEnabled']}"

            )
        file_path = f"Python-Meraki/data/ports_{serial}.json"
        with open(file_path, "w") as outfile:
            json.dump(port_list, outfile, indent=4)
        logging.info(f"Saved port list to {file_path}.")

    except Exception as e:
        logging.error(f"Error: {e}")


def update_port(dashboard, serial, port_id, enable=None, vlan=None):
    # this is the dictionary which will passed as a payload.
    payload = {}
    # simple expression to identify whether enable is anything except NONE.
    # the main() function is only passing True or False for this parameter so,
    # enable's value (either True or False) is assigned to the "enabled" key.
    # note that in the if expression, any non-empty value (empty = NONE) becomes True.
    if enable is not None:
        payload["enabled"] = enable
    if vlan:     # no vlan would mean empty string is passed, which would evaluate as False.
        payload["vlan"] = vlan

    if not payload:
        logging.info("No updates requested. Skipping.")
        return

    # in the below api call, there are 2 required arguments. You will have to figure this out for each API call.
    respone = dashboard.switch.updateDeviceSwitchPort(
        serial,
        port_id,
        **payload
    )
    logging.info(f"Updated port {port_id} on {serial}: \n\n{respone}\n\n")


def main():
    try:
        dashboard = meraki.DashboardAPI(
            api_key=API_KEY,
            suppress_logging=True
        )
    except Exception as e:
        logging.error(f"Error: {e}")

    serial = input(
        "Please input the serial number of your Meraki switch: ").strip()
    get_ports(dashboard, serial)

    choice = input("Do you want to update a port (y/n)? ").lower().strip()
    if choice == "y":
        port_id = input("Enter the port ID to modify: ")
        enable_ssid = input(
            "Do you want to enable this port (y/n): ").lower().strip()
        if enable_ssid == "y":
            enable = True
        elif enable_ssid == "n":
            enable = False
        else:
            enable = None
        try:
            vlan = int(input(
                "Enter vlan ID to set (or press Enter to skip): "))
            update_port(dashboard, serial, port_id, enable, vlan)
            get_ports(dashboard, serial)
        except ValueError:
            logging.error(
                f"You have typed a non integer value, pls re run the program.")


if __name__ == "__main__":
    main()
