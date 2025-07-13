# this script assumes you already have nightly backups turned on.
import json
from pathlib import Path
from datetime import datetime
from deepdiff import DeepDiff
import logging

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

diff_report = {}
for latest_file in latest_snapshot.glob("*.json"):
    previous_file = previous_snapshot/latest_file.name
    if previous_file.exists():
        with open(previous_file, "r") as f1, open(latest_file, "r") as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

            diff = DeepDiff(data1, data2, ignore_order=True)
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
