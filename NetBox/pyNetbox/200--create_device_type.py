import re
import pynetbox
import yaml
import os
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Config
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NB_URL = secrets["NETBOX_URL"]
    NB_TOKEN = secrets["API_TOKEN"]

nb = pynetbox.api(NB_URL, token=NB_TOKEN)
nb.http_session.verify = False  # Ignore self-signed SSL

base_path = "/tmp/devicetype-library/device-types"  # Correct folder


def slugify(value):
    value = value.lower().replace(" ", "-")
    value = re.sub(r"[^a-z0-9_-]", "", value)
    return value


for root, dirs, files in os.walk(base_path):
    for file in files:
        if file.endswith(".yaml") or file.endswith(".yml"):
            with open(os.path.join(root, file)) as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict) or "manufacturer" not in data or "model" not in data:
                    print(f"Skipping {file}: missing required fields.")
                    continue

                # Create or update manufacturer
                manufacturer = nb.dcim.manufacturers.get(
                    name=data["manufacturer"])
                if manufacturer is None:
                    manufacturer = nb.dcim.manufacturers.create({
                        "name": data["manufacturer"],
                        "slug": slugify(data["manufacturer"])
                    })

                # Create device type
                payload = {
                    "model": data["model"],
                    "slug": slugify(data["model"]),
                    "manufacturer": manufacturer.id,
                    "part_number": data.get("part_number", ""),
                    "u_height": data.get("u_height", 1),
                    "is_full_depth": data.get("is_full_depth", True),
                    "comments": data.get("comments", ""),
                }
                device_type = nb.dcim.device_types.get(
                    slug=slugify(data["model"]), manufacturer_id=manufacturer.id)

                device_type = nb.dcim.device_types.get(
                    slug=slugify(data["model"]), manufacturer_id=manufacturer.id)

                try:
                    if device_type is None:
                        nb.dcim.device_types.create(payload)
                        print(
                            f"✅ Imported: {data['manufacturer']} {data['model']}")
                    else:
                        print(
                            f"⏭️ Skipped (exists): {data['manufacturer']} {data['model']}")
                except Exception as e:
                    print(
                        f"❌ Failed to import {data['manufacturer']} {data['model']} : {e}")
