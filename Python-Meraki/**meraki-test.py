import json
from pathlib import Path
from datetime import datetime
from deepdiff import DeepDiff
import logging

# --- Setup logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- Paths ---
# adjust if needed
base_path = Path("/mnt/01D53F0A0F195940/LUFFY/SEIJURO/PYTHON/Python-Git")
data_dir = base_path / "Python-Meraki/data"
diff_dir = data_dir / "diff_logs"
diff_dir.mkdir(parents=True, exist_ok=True)

# --- Identify the latest and previous snapshot folders ---
snapshot_folders = sorted(
    [f for f in data_dir.iterdir() if f.is_dir()], reverse=True)

if len(snapshot_folders) < 2:
    logging.error("Not enough snapshots to perform diff.")
    exit(1)

latest_snapshot = snapshot_folders[0]
previous_snapshot = snapshot_folders[1]

logging.info(
    f"Comparing:\nLATEST: {latest_snapshot}\nPREVIOUS: {previous_snapshot}")

# --- Drift detection ---
diff_report = {}
for latest_file in latest_snapshot.glob("*.json"):
    previous_file = previous_snapshot / latest_file.name
    if previous_file.exists():
        with open(latest_file, "r") as f1, open(previous_file, "r") as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

            diff = DeepDiff(data2, data1, ignore_order=True)
            if diff:
                diff_report[latest_file.name] = diff

# --- Save drift report ---
timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M")
report_file = diff_dir / f"{timestamp}_drift_report.json"

with open(report_file, "w") as f:
    json.dump(diff_report, f, indent=4)

logging.info(f"Drift report saved: {report_file}")

if diff_report:
    logging.info(f"Drifts detected in {len(diff_report)} files.")
else:
    logging.info("No drifts detected.")
