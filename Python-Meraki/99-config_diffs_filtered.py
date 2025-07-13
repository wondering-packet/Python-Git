# expanding on 99-config_diffs to remove noise & frequently changing values

# this script assumes you already have nightly backups turned on.
import json
from pathlib import Path
from datetime import datetime
from deepdiff import DeepDiff
import logging
import re       # using regular expression to identify noise.

# -- logging setup --
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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

if diff_report:
    logging.info(f"Drifts detected: {len(diff_report)} json files")
else:
    logging.info("No drifts dectected")
