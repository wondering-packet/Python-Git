# expanding on 99-config_diffs to:
#   remove noise i.e. frequently changing values
#   integrate MS teams for alerting using webhooks

# this script assumes you already have nightly backups turned on.
import json
from pathlib import Path
from datetime import datetime
from deepdiff import DeepDiff
import logging
import re       # using regular expression to identify noise.
import requests
import subprocess

# -- logging setup --
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- loading webhook URL ---
with open("/automation/secrets/keys.json", "r") as temp:
    secret = json.load(temp)
    TEAMS_WEBHOOK_URL = secret["teams_webhook"]

# -- paths --
base_path = Path("/automation/python-data/")
data_dir = base_path/"99-nightly_snapshot"
diff_dir = base_path/"diff_logs"
diff_dir.mkdir(parents=True, exist_ok=True)

snapshot_folders = sorted(
    [f for f in data_dir.iterdir() if f.is_dir()], reverse=True)

if len(snapshot_folders) < 2:
    logging.error("Not enough backups to produce a diff. Min: 2 required.")
    exit(1)

latest_snapshot = snapshot_folders[0]
previous_snapshot = snapshot_folders[1]

logging.info(f"\nComparing {latest_snapshot} with {previous_snapshot}\n")

# -- paths to ignore ---
# here we are ignoring frequently changing fields since we don't want to consider them for diffs.
exclude_noise = [
    # root['key1']['key2'] is expected format for DeepDiff.
    # so below lines will match e.g. root['devices']['lastSeen']
    # if it is still confusing read up on DeepDiff & regular expression matching.
    r"root\['.*?'\]\['lastSeen'\]",
    r"root\['.*?'\]\['usage'\]",
    r"root\['.*?'\]\['clientCount'\]",
    r"root\['.*?'\]\['firmware'\]",
    r"root\['.*?'\]\['lanIp'\]",
]

diff_report = {}
for latest_file in latest_snapshot.glob("*.json"):
    previous_file = previous_snapshot/latest_file.name
    if previous_file.exists():
        with open(previous_file, "r") as f1, open(latest_file, "r") as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

            diff = DeepDiff(data1, data2, ignore_order=True,
                            exclude_paths=exclude_noise)
            if diff:
                # we have to to the whole json dance here because
                # diff is a DeepDiff object which isn't json serialized by default.
                # so to_json() is converting it to json then
                # json.loads is loading it as a json.
                diff_report[latest_file.name] = json.loads(diff.to_json())

timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
report_file = diff_dir/f"{timestamp}_drift_report.json"

with open(report_file, "w") as f:
    json.dump(diff_report, f, indent=4)

logging.info(f"\nDiff Report generated: {report_file}\n")

# below code is assuming you have gone through "98-nightly_snapshot_Github_Integration.txt"
# repo_dir is the name of current snapshot, tag_name is what will be pushed to Git.
# tag then can be used to track diffs in Git.


def git_tag_only(repo_dir, tag_name=None):
    try:
        subprocess.run(
            ["git", "-C", repo_dir, "tag", tag_name], check=True)
        subprocess.run(["git", "-C", repo_dir, "push",
                        "origin", tag_name], check=True)
        logging.info(f"Tag {tag_name} pushed successfully.")

    except subprocess.CalledProcessError as e:
        logging.error(f"Git operation failed: {e}")

# check out "99-config_diffs_MS_Teams_Integration.txt" file for instructions on how to setup Teams to receive these alerts.


def send_teams_notification(message):
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


# triggers as long as diff_report is not empty (which evaluates to True)
if diff_report:
    logging.info(f"Drifts detected: {len(diff_report)} json files")
    # block 1: MS teams integration
    message = (
        f"⚠️ **Meraki Config Drift Detected**\n"
        f"- Drifts in `{len(diff_report)}` JSON files.\n"
        f"- Report: `{report_file}`\n"
        f"- Time: `{timestamp}`"
    )
    send_teams_notification(message)
    # block 2: Github integration.
    # Pushing tags; this is assuming you have already commited & pushed in your 98 script.
    tag_name = f"drift-{timestamp}"
    repo_dir = "/automation/python-data/99-nightly_snapshot"
    git_tag_only(
        repo_dir=data_dir,
        tag_name=tag_name
    )
else:
    logging.info("No drifts dectected")
