import pynetbox
import urllib3
import json
from pprint import pprint
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load credentials
with open("/automation/secrets/netbox.json", "r") as f:
    secrets = json.load(f)
    NETBOX_URL = secrets["NETBOX_URL"]
    API_TOKEN = secrets["API_TOKEN"]

nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)
nb.http_session.verify = False

response = nb.tenancy.tenants.get(name="WP-Corp")

pprint(dir(response))
print(response.rack_count)
print("\n@@1\n")
response = nb.dcim.sites.choices()
pprint(response)
print("\n\n")
for r in response:
    print(r)
pprint(dir(response))
print("\n@@2\n")
response = nb.tenancy.tenants.all()
pprint(response)
for r in response:
    print(r)
pprint(dir(response))
print("\n@@3\n")
pprint(nb.ipam.ip_addresses.choices())
# data = nb.tenancy.tenants.filter(name="WP-Corp")
# response = list(data)
# pprint(dir(response))
# for r in response:
#     print(r.rack_count)

# pprint(dir(nb.tenancy.tenants))
