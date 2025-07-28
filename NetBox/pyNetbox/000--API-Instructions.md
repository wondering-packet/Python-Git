For detailed instructions, visit the official pynetbox documentation:
[https://pynetbox.readthedocs.io/](https://pynetbox.readthedocs.io/)

Below, I am summarizing the API structure/schema, various calls & methods you can utilize with the `pynetbox` module. These are intended to be a quick reference for myself & help anyone new to quickly get started with `pynetbox`.

---

## 1. Figuring Out the Right API Call

First thing you need to do is figure out what you can do!

* **Pull interfaces:** Figure out the API call for the `interfaces` endpoint (e.g., `nb.dcim.interfaces`).
* **Pull circuits:** Figure out the API call for the `circuits` endpoint (e.g., `nb.circuits.circuits`).
* **And so on...** Apply the same logic for other object types like `devices`, `racks`, `IP addresses`, etc.

So let's start with the root of netbox API.

### a) Root
start from:
`https://NETBOX_URL/api/`

my Netbox url is: `netbox.intra.slicesoftech.net`

you will see the available API app labels you can call at root:

```http
GET /api/
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "circuits": "[https://netbox.intra.slicesoftech.net/api/circuits/](https://netbox.intra.slicesoftech.net/api/circuits/)",
    "core": "[https://netbox.intra.slicesoftech.net/api/core/](https://netbox.intra.slicesoftech.net/api/core/)",
    "dcim": "[https://netbox.intra.slicesoftech.net/api/dcim/](https://netbox.intra.slicesoftech.net/api/dcim/)",
    "extras": "[https://netbox.intra.slicesoftech.net/api/extras/](https://netbox.intra.slicesoftech.net/api/extras/)",
    "ipam": "[https://netbox.intra.slicesoftech.net/api/ipam/](https://netbox.intra.slicesoftech.net/api/ipam/)",
    "plugins": "[https://netbox.intra.slicesoftech.net/api/plugins/](https://netbox.intra.slicesoftech.net/api/plugins/)",
    "status": "[https://netbox.intra.slicesoftech.net/api/status/](https://netbox.intra.slicesoftech.net/api/status/)",
    "tenancy": "[https://netbox.intra.slicesoftech.net/api/tenancy/](https://netbox.intra.slicesoftech.net/api/tenancy/)",
    "users": "[https://netbox.intra.slicesoftech.net/api/users/](https://netbox.intra.slicesoftech.net/api/users/)",
    "virtualization": "[https://netbox.intra.slicesoftech.net/api/virtualization/](https://netbox.intra.slicesoftech.net/api/virtualization/)",
    "vpn": "[https://netbox.intra.slicesoftech.net/api/vpn/](https://netbox.intra.slicesoftech.net/api/vpn/)",
    "wireless": "[https://netbox.intra.slicesoftech.net/api/wireless/](https://netbox.intra.slicesoftech.net/api/wireless/)"
}
````

### b) Apps

for instance if you want information regarding tenancy app then you will goto:
`https://netbox.intra.slicesoftech.net/api/tenancy/`

```http
GET /api/tenancy/
HTTP 200 OK
Allow: GET, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "contact-assignments": "[https://netbox.intra.slicesoftech.net/api/tenancy/contact-assignments/](https://netbox.intra.slicesoftech.net/api/tenancy/contact-assignments/)",
    "contact-groups": "[https://netbox.intra.slicesoftech.net/api/tenancy/contact-groups/](https://netbox.intra.slicesoftech.net/api/tenancy/contact-groups/)",
    "contact-roles": "[https://netbox.intra.slicesoftech.net/api/tenancy/contact-roles/](https://netbox.intra.slicesoftech.net/api/tenancy/contact-roles/)",
    "contacts": "[https://netbox.intra.slicesoftech.net/api/tenancy/contacts/](https://netbox.intra.slicesoftech.net/api/tenancy/contacts/)",
    "tenant-groups": "[https://netbox.intra.slicesoftech.net/api/tenancy/tenant-groups/](https://netbox.intra.slicesoftech.net/api/tenancy/tenant-groups/)",
    "tenants": "[https://netbox.intra.slicesoftech.net/api/tenancy/tenants/](https://netbox.intra.slicesoftech.net/api/tenancy/tenants/)"
}
```

### c) Endpoints

Now suppose you want information on tenants, you goto tenants url (called endpoint):
`https://netbox.intra.slicesoftech.net/api/tenancy/tenants/`

```http
GET /api/tenancy/tenants/
HTTP 200 OK
Allow: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS
Content-Type: application/json
Vary: Accept

{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 4,
            "url": "[https://netbox.intra.slicesoftech.net/api/tenancy/tenants/4/](https://netbox.intra.slicesoftech.net/api/tenancy/tenants/4/)",
            "display_url": "[https://netbox.intra.slicesoftech.net/tenancy/tenants/4/](https://netbox.intra.slicesoftech.net/tenancy/tenants/4/)",
            "display": "WP-Corp",
            "name": "WP-Corp",
            "slug": "wp-corp",
            "group": null,
            "description": "WP corp",
            "comments": "",
            "tags": [],
            "custom_fields": {},
            "created": "2025-07-23T17:10:24.213260Z",
            "last_updated": "2025-07-23T17:10:24.213272Z",
            "circuit_count": 0,
            "device_count": 80,
            "ipaddress_count": 0,
            "prefix_count": 0,
            "rack_count": 40,
            "site_count": 12,
            "virtualmachine_count": 0,
            "vlan_count": 0,
            "vrf_count": 0,
            "cluster_count": 0
        },
        {},
        ....
        {}
    ]
}
```

you can now see actual data in this API call (total 3 tenants are there).
To look into a specific tenant, you pass in the tenant specific lookup fields in your API call.

here is an example code:

```python
# initiliaze netbox object
import pynetbox
from pprint import pprint

# Assuming NETBOX_URL and API_TOKEN are defined elsewhere or passed in
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)

# storing the response. notice the path - this matches with our API path.
# we have passed "name" as a lookup field to identify the tenant we are looking for.
# similarily you can use other field such as description, id or slug.
# note that you cannot use just any field to ID. e.g. vlan_count comes from operations data
# so it cannot be used as an ID; it's not a lookup field in Netbox.

response = nb.tenancy.tenants.get(name="WP-Corp")

print(response.rack_count)      # output: 40
print(response.site_count)      # output: 12
```

### d) Bonus:

`dir(response)` lets you view what can be pulled from this tenant.

```python
pprint(dir(response))
```

```
"""
here is a truncated output:
 'ipaddress_count',
 'last_updated',
 'name',
 'prefix_count',
 'rack_count',
 'save',
 'serialize',
 'site_count',
 'slug',
 'tags',
 'update',
 'updates',
 'url',
 'virtualmachine_count',
 'vlan_count',
 """
```

## 2\. What are the methods available in Netbox?

### a) `get()`: makes a GET call.

In my above exmaple, you can see I used a `get()` method - that's a method used to fetch info.
Fetches a single object (you can pass on multiple match criterias though).
Errors out if multiple objects are returned.

```python
response = nb.tenancy.tenants.get(name="WP-Corp", id=4)
# response = nb.tenancy.tenants.get(name="WP-Corp")

print(response.description)

# output:
# WP corp
```

### b) `filter()`: makes a GET call.

Returns multiple objects matching your filter.
You can pass on multiple match criterias just like `get()`.
Note that, you should only use certain lookup fields to pass.
e.g. using `name="WP-Corp"` doens't make sense since names are unique & will only return one value.
so use lookup fields which can actually return multiple values. e.g. tag.

```python
response = nb.tenancy.tenants.filter(group_id=1, tag="test")
tenants = list(response)

for each_tenant in tenants:
    print(each_tenant.description)

# output:
# WP corp
# WP lab
```

### c) `all()`: makes a GET call.

returns all objects in the endpoint. this can then be iterated using a list & for loop.

```python
response = nb.tenancy.tenants.all()
tenants = list(response)

for each_tenant in tenants:
    print(each_tenant.description)

# output:
# WP corp
# WP lab
# WP retail
```

### d) `create()`: makes a POST call.

creates new object.

```python
new_tenant = {
    "name": "NewCorp",
    "slug": "newcorp",
    "description": "Created via pynetbox"
}
response = nb.tenancy.tenants.create(**new_tenant)
```

### e) `update()`: makes a PATCH or PUT call. typically PATCH.

updates a field on an existing object.

```python
tenant = nb.tenancy.tenants.get(name="NewCorp2")

# you will pass each field as a Key:Value pair in a dictionary.
# you can pass multiple fields.
tenant.update({"description": "corp 2"})
```

### f) `delete()`: makes a DELETE call.

deletes an object.

```python
tenant = nb.tenancy.tenants.get(name="NewCorp2")
tenant.delete()
```

### g) `choices()`: makes a GET call.

returns all choices from an endpoint as a dictionary.
it is usefull when you are trying to determine what choices are available for a field.
e.g. status could be "Active", "Planned", "Staging" etc.
without the `choices()`, you wouldn't know what you can PUT.

```python
response = nb.dcim.sites.choices()
pprint(response)

# output:

# {'status': [{'display_name': 'Planned', 'value': 'planned'},
#             {'display_name': 'Staging', 'value': 'staging'},
#             {'display_name': 'Active', 'value': 'active'},
#             {'display_name': 'Decommissioning', 'value': 'decommissioning'},
#             {'display_name': 'Retired', 'value': 'retired'}]}
```

## 3\. What methods can be called upon each endpoint?

`print(dir(ENDPOINT))`

e.g.

```python
pprint(dir(nb.tenancy.tenants))
```

```
# output:
[
 ...
 'all',
 'choices',
 'create',
 'delete',
 'filter',
 'get',
 'update',
 ...
 ]
```

## 4\. How do i know what fields i need to pass on for POST or other methods?

Goto the API docs.
`https://NETBOX_URL/api/schema/swagger-ui`

#### a) Search for the endpoint you are working with e.g. `racks`.

#### b) Look at the POST call for this endpoint.

#### c) Look at the Request body. anything marked with `*` is a mandatory field.

#### d) Optional, you can also see the Response body to see what will be returned after making the call.

You can also see GET, PUT, PATCH, and DELETE calls here.