# this compliance script checks all the switcheports in all networks in all organizations
# to generate a compliance report which contains data on:
#    all access & enabled ports which:
#       1. do not have a tag assigned.
#       2. do not have org's standard port access policy assigned.

import meraki
import logging
from pathlib import Path
from datetime import datetime
import requests
import json
import subprocess

# --- usual logging ---
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
    # capital letters dont mean static in python unlike some other languages.
    # we are just doing so because that's the norm in programming to denote our intention
    # (which is to keep this variable unchanging)
    TEAMS_WEBHOOK_URL = secret["teams_webhook"]

dashboard = meraki.DashboardAPI(api_key=API_KEY, suppress_logging=True)

# --- complaince object ---
compliance_access_port_policy = "NAC-Test-Policy"
# every access policy has a number which is unique ID.
# you will need this to specify later to assign the correct policy on the port.
# how do i get this? navigate to your access policy in Meraki dashboard
# then note down the number at the end of the URL, that is the policy number.
# why am i doing it like this??
#   because Meraki doesn't expose the policy number cleanly. So this is the workaround.
compliance_access_port_policy_number = 1
default_tag = "user-port"

# below function is auto commiting & pushing to a remote repo
# for how to setup the remote repo,
# read instructions in "98-nightly_snapshot_Github_Integration.txt"

timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")


def remediate_compliance():
    successes = []       # storing all remediated ports here.
    orgs = dashboard.organizations.getOrganizations()

    for each_org in orgs:
        org_id = each_org["id"]
        org_name = each_org["name"]
        networks = dashboard.organizations.getOrganizationNetworks(org_id)
        # --- device ports ---
        for network in networks:
            network_id = network["id"]
            network_name = network["name"]

            # this is the newer call to pull devices.
            devices = dashboard.organizations.getOrganizationDevices(
                org_id, networkIds=network_id)
            for each_device in devices:
                device_id = each_device["serial"]
                # if device_name is empty then default it to "N/A". this is based on truthsy & falsy logic.
                device_name = each_device["name"] or "N/A"
                # using try & catch block because getDeviceSwtichPorts only works for switches.
                # since we are looping over every type of device, we will get warnings.
                # so the except block is taking care of suppressing the warnings more gracefully.
                try:
                    ports = dashboard.switch.getDeviceSwitchPorts(
                        device_id)
                except Exception as e:
                    logging.warning(
                        f"Serial: {device_id} ; Device name: {device_name}; {e}")
                    continue
                for each_port in ports:
                    port_id = each_port["portId"]
                    actions = []        # storing actions performed on a port.

                    # evaluating below block only if the port is access & it's enabled.
                    if each_port.get("type") == "access" and each_port.get("enabled"):
                        remediated = False
                        # i think below attribute used to be able to output actual policy name before
                        # but unfortunately it doesn't work the same way anymore;
                        # it now sends "Custom access policy" for the name instead of the actual policy name.
                        # note that it still ouputs the correct policy name if it finds a built-in one.
                        # e.g. Open is a built in access policy.
                        policy_name = each_port.get("accessPolicyType")
                        policy_num = each_port.get("accessPolicyNumber")
                        # using the if logic to update the policy name if "Custom access policy" is found.
                        if policy_name == "Custom access policy":
                            # this is another API call which can pull the Actual policy name.
                            policy_data = dashboard.switch.getNetworkSwitchAccessPolicy(
                                network_id, policy_num)
                            # updating the policy_name for custom policy
                            policy_name = policy_data["name"]
                        if policy_num != compliance_access_port_policy_number:
                            dashboard.switch.updateDeviceSwitchPort(
                                device_id, port_id, accessPolicyType="Custom access policy",
                                accessPolicyNumber=compliance_access_port_policy_number
                            )
                            actions.append(
                                f"Remdiation: assigned default access policy {compliance_access_port_policy}"

                            )
                            remediated = True
                        # if "tags" is empty then assign an empty list using [].
                        # the reason for using a list is, it's easy to do a If logic to determine if a value
                        # exists in the list. If "tags" did return some value (which means port has at least 1 tag)
                        # then that tag(s) will get assigned to each_port_tags which then will fail our If logic
                        # defined further below.
                        each_port_tags = each_port.get("tags", [])
                        if not each_port_tags:
                            dashboard.switch.updateDeviceSwitchPort(
                                device_id, port_id, tags=[default_tag])
                            actions.append(
                                f"Remdiation: assigned default tag {default_tag}"
                            )
                            remediated = True

                        if remediated:
                            successes.append(
                                {
                                    "org_name": org_name,
                                    "network_name": network_name,
                                    "network_id": network_id,
                                    "device_name": device_name,
                                    "device_id": device_id,
                                    "port_id": port_id,
                                    "action": actions
                                }
                            )
                            logging.info(
                                f"\n> Compliance failed items remediated on device name: {device_name} - serial: {device_id} - port: {port_id}\n\t>> Actions\n\t\t>>> {actions}")
    return successes


def git_commit_snapshots(report_file, tag=None):
    try:
        repo_dir = base_path
        commit_message = f"Auto Remediation report"

        subprocess.run(["git", "-C", repo_dir, "add",
                       f"{report_file}"], check=True)
        subprocess.run(["git", "-C", repo_dir, "commit",
                       "-m", commit_message], check=True)
        subprocess.run(["git", "-C", repo_dir, "push"], check=True)

        if tag:
            tag_name = f"Auto-remediation-{timestamp}"
            subprocess.run(
                ["git", "-C", repo_dir, "tag", tag_name], check=True)
            subprocess.run(["git", "-C", repo_dir, "push",
                            "origin", tag_name], check=True)
            logging.info(f"Tag {tag_name} pushed successfully.")

        logging.info(
            f"Auto Remediation report committed to Git: {report_file}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Git commit failed: {e}")


def save_report_and_notify(successes):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
    report_file = report_dir/f"{timestamp}_remediation_report.json"
    with open(report_file, "w") as f:
        json.dump(successes, f, indent=4)
    logging.info(f"Remediation report saved: {report_file}.")

    if successes:
        logging.info(
            f"#####--Autoremediated non-compliant ports; Check report for details--#####")
        message = f"Meraki Auto Remediation: {len(successes)} non-compliant ports remediated.\nCheck report at {report_file}"
        tag = True
    else:
        logging.info(
            f"#####--No Autoremediation; All ports already compliant--#####")
        message = f"Meraki Auto Remediation: All ports already compliant."
        tag = None

    git_commit_snapshots(report_file, tag)

    if TEAMS_WEBHOOK_URL:     # ensuring webhook_url is present in your keys.json file.
        # json payload. has to be json since Teams expect json payload!
        # your MS teams webhook needs to be setup to accept the payload in this exact format.
        # check the webhook instruction file, you will find the matching schema for it there.
        payload = {"text": message}
        try:
            response = requests.post(TEAMS_WEBHOOK_URL, json=payload)
            # Teams will send 202. we are capturing some other successfull codes as well. might not be needed!
            if response.status_code in [200, 201, 202]:
                logging.info("Teams notification sent successfully.")
            else:
                logging.error(f"Teams notification failed: {response.text}")
        except Exception as e:
            logging.error(f"Teams notification error: {e}")


if __name__ == "__main__":
    successes = remediate_compliance()
    save_report_and_notify(successes)
