import subprocess
import meraki
import json
import logging
from pathlib import Path
from datetime import datetime


# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- loading API key ---
with open("/automation/secrets/keys.json", "r") as temp:
    secret = json.load(temp)
    API_KEY = secret["api_key"]

# ---- creating a path to store our backups ---
# strftime formats dattime for us.
current_hr_str = datetime.now().strftime("%y-%m-%d-%H-%M")
# Using Path to join paths.
save_dir = Path(
    f"/automation/python-data/99-nightly_snapshot/{current_hr_str}")
# Path allows mkdir method which lets us create the directory (if it doesn't exist)
save_dir.mkdir(parents=True, exist_ok=True)


def save_json(data, filename):
    # "/" is used to join paths. it's from pathlib.
    with open(save_dir/filename, "w") as f:
        json.dump(data, f, indent=4, sort_keys=True)
    logging.info(f"Saved {filename}")


# below function is auto commiting & pushing to a remote repo
# for how to setup the remote repo,
# read instructions in "098-B--nightly_snapshot_Github_Integration.txt"

def git_commit_snapshots(snapshot_folder):
    try:
        # Move into snapshot base directory
        repo_dir = "/automation/python-data/99-nightly_snapshot"
        commit_message = f"Snapshot taken: {snapshot_folder.name}"

        subprocess.run(["git", "-C", repo_dir, "add", "."], check=True)
        subprocess.run(["git", "-C", repo_dir, "commit",
                       "-m", commit_message], check=True)
        subprocess.run(["git", "-C", repo_dir, "push"], check=True)

        logging.info(f"Snapshot committed to Git: {commit_message}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git commit failed: {e}")


def snapshot():
    try:
        dashboard = meraki.DashboardAPI(
            api_key=API_KEY,
            suppress_logging=True
        )

        # ---- orgs & networks ---
        orgs = dashboard.organizations.getOrganizations()
        # print(f"#### {orgs}")
        save_json(orgs, "organizations.json")     # saving orgs json.
        for org in orgs:
            org_id = org['id']
            networks = dashboard.organizations.getOrganizationNetworks(
                org_id)
            # print(f"#### {networks}")
            # saving networks json.
            save_json(networks, f"networks_{org_id}.json")

            # --- devices ---
            for network in networks:
                network_id = network["id"]
                devices = dashboard.networks.getNetworkDevices(network_id)
                # saving devices json.
                save_json(devices, f"devices_{org_id}_{network_id}.json")

            # ---- ssids ---
            for network in networks:
                network_id = network["id"]
                ssids = dashboard.wireless.getNetworkWirelessSsids(
                    network_id)
                # saving ssids json.
                save_json(ssids, f"ssids_{org_id}_{network_id}.json")

            # --- device ports ---
            for network in networks:
                network_id = network["id"]
                devices = dashboard.networks.getNetworkDevices(network_id)
                for each_device in devices:
                    device_id = each_device["serial"]
                    # using try & catch block because getDeviceSwtichPorts only works for switches.
                    # since we are looping over every type of device, we will get warnings.
                    # so the except block is taking care of suppressing the warnings more gracefully.
                    try:
                        ports = dashboard.switch.getDeviceSwitchPorts(
                            device_id)
                        save_json(
                            # saving device ports json.
                            ports, f"ports_{org_id}_{network_id}_{device_id}.json")
                    except Exception as e:
                        logging.warning(f"{device_id} - skipping ports: {e}")
        git_commit_snapshots(save_dir)

    except Exception as e:
        logging.error(f"Error: {e}")
    logging.info(f"Snapshot completed for {current_hr_str}")


if __name__ == "__main__":
    snapshot()


# Once you've tested this script successfully, you can add a cronjob to automate nightly snapshots:
# crontab -e
# add below line:
# 0 * * * * /path/to/python/venv/Python-Git/Python-Meraki/venv_meraki_automation/bin/python /path/to/script/99-nightly_snapshot.py >> /automation/logs/99-nightly_snapshot.log 2>&1
# explanation:
# 0 2 * * * --> means at 2am (2h 0m) every day every month every day of the week
# /path/to/python/venv/ --> i am using a python venv so i am specifying the path
# /path/to/script/ --> path to this script
# >> /automation/logs/99-nightly_snapshot.log 2>&1
#       --> above line is logging to .log file. 2>&1 is used to also log the errors to the same file.
