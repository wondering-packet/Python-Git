For detailed instructions, visit the official pynetbox documentation:
[https://pynetbox.readthedocs.io/](https://pynetbox.readthedocs.io/)

What I have below are some instructions I found useful for myself while working with the `pynetbox` module.

---

## 1. Figuring Out the Right API Call

Understanding the NetBox API structure is key to using `pynetbox` effectively. The API follows a logical hierarchy that mirrors the NetBox UI.

### a) Discovering Top-Level Apps

Start by exploring the root of your NetBox API:

`https://NETBOX_URL/api/`

For instance, with my NetBox URL: `netbox.intra.slicesoftech.net`, I would visit:
`https://netbox.intra.slicesoftech.net/api/`

You will see the available API app labels you can call at this root:

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

### b) Diving Into a Specific App

If you want information regarding the `tenancy` app, you would then navigate to its API endpoint:
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

### c) Accessing Specific Endpoints (Objects)

Now, suppose you want information on `tenants`. You navigate to the `tenants` URL (which is often called an "endpoint"):
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
        ...
        {}
    ]
}
```

You can now see actual data in this API call (total 3 tenants are there). To look into a specific tenant, you pass in the tenant-specific lookup fields in your API call.

Here is an example `pynetbox` code:

```python
import pynetbox
from pprint import pprint

# Initialize netbox object
# Replace NETBOX_URL and API_TOKEN with your actual values
NETBOX_URL = "[https://netbox.intra.slicesoftech.net](https://netbox.intra.slicesoftech.net)"
API_TOKEN = "YOUR_NETBOX_API_TOKEN" # Always keep your token secure!

nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)

# Storing the response. Notice the path - this matches with our API path.
# We have passed "name" as a lookup field to identify the tenant we are looking for.
# Similarly, you can use other fields such as description, id, or slug.
# Note that you cannot use just any field to ID. E.g., 'vlan_count' comes from
# operational data, so it cannot be used as an ID; it's not a lookup field in Netbox.
response = nb.tenancy.tenants.get(name="WP-Corp")

if response:
    print(f"Rack Count for WP-Corp: {response.rack_count}")      # output: 40
    print(f"Site Count for WP-Corp: {response.site_count}")      # output: 12
else:
    print("Tenant 'WP-Corp' not found.")

# Bonus:
# dir(response) lets you view what can be pulled from this tenant.
print("\nAvailable attributes for the tenant object:")
pprint(dir(response))
```

Truncated output of `pprint(dir(response))`:

```
[
 ...,
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
 ...
]
```

## 2\. Common Methods Available in `pynetbox`

The `pynetbox` module provides convenient methods that map directly to standard REST API operations.

### a) `get()`: Fetch a Single Object (GET Call)

  * Fetches a single object matching your criteria.
  * Errors out if multiple objects are returned (use `filter()` for multiple results).
  * You can pass on multiple match criteria.

<!-- end list -->

```python
# Example of 'get()'
response = nb.tenancy.tenants.get(name="WP-Corp", id=4) # Multiple criteria
# response = nb.tenancy.tenants.get(name="WP-Corp") # Single criterion

if response:
    print(f"Description of tenant: {response.description}")
# Output:
# WP corp
```

### b) `filter()`: Fetch Multiple Objects (GET Call)

  * Returns a list of objects matching your filter.
  * You can pass on multiple match criteria, just like `get()`.
  * **Note:** You should only use certain lookup fields to pass. For example, using `name="WP-Corp"` doesn't make sense if names are unique, as it will only return one value. Use lookup fields that can actually return multiple values (e.g., `tag`, `group_id`).

<!-- end list -->

```python
# Example of 'filter()'
response = nb.tenancy.tenants.filter(group_id=1, tag="test")
tenants = list(response) # Convert the generator to a list to iterate multiple times

print("\nTenants found by filter:")
for each_tenant in tenants:
    print(each_tenant.description)
# Output:
# WP corp
# WP lab
```

### c) `all()`: Fetch All Objects (GET Call)

  * Returns all objects from the specified endpoint.
  * This can then be iterated using a `list` conversion and a `for` loop.

<!-- end list -->

```python
# Example of 'all()'
response = nb.tenancy.tenants.all()
tenants = list(response)

print("\nAll tenants:")
for each_tenant in tenants:
    print(each_tenant.description)
# Output:
# WP corp
# WP lab
# WP retail
```

### d) `create()`: Create a New Object (POST Call)

  * Makes a POST call to create a new object.

<!-- end list -->

```python
# Example of 'create()'
new_tenant_data = {
    "name": "NewCorp",
    "slug": "newcorp",
    "description": "Created via pynetbox"
}
try:
    response = nb.tenancy.tenants.create(**new_tenant_data)
    print(f"\nCreated new tenant: {response.name} (ID: {response.id})")
except pynetbox.RequestError as e:
    print(f"\nError creating tenant: {e.error}")
```

### e) `update()`: Update an Existing Object (PATCH or PUT Call)

  * Updates fields on an existing object. Typically makes a PATCH call by default.
  * You pass each field as a `Key:Value` pair in a dictionary. You can pass multiple fields.

<!-- end list -->

```python
# Example of 'update()'
try:
    tenant_to_update = nb.tenancy.tenants.get(name="NewCorp") # Using the tenant created above
    if tenant_to_update:
        # You will pass each field as a Key:Value pair in a dictionary.
        # You can pass multiple fields.
        tenant_to_update.update({"description": "NewCorp updated via pynetbox"})
        print(f"\nUpdated tenant '{tenant_to_update.name}'. New description: {tenant_to_update.description}")
    else:
        print("\nTenant 'NewCorp' not found for update.")
except pynetbox.RequestError as e:
    print(f"\nError updating tenant: {e.error}")
```

### f) `delete()`: Delete an Object (DELETE Call)

  * Deletes an existing object.

<!-- end list -->

```python
# Example of 'delete()'
try:
    tenant_to_delete = nb.tenancy.tenants.get(name="NewCorp") # Using the tenant we just updated
    if tenant_to_delete:
        tenant_to_delete.delete()
        print(f"\nDeleted tenant: {tenant_to_delete.name}")
    else:
        print("\nTenant 'NewCorp' not found for deletion.")
except pynetbox.RequestError as e:
    print(f"\nError deleting tenant: {e.error}")
```

### g) `choices()`: Get Field Choices (GET Call)

  * Returns all available choices for a field from an endpoint as a dictionary.
  * It's useful when you are trying to determine what valid choices are available for a field (e.g., `status` could be "Active", "Planned", "Staging" etc.). Without `choices()`, you wouldn't know what values you can use for `create()` or `update()`.

<!-- end list -->

```python
# Example of 'choices()'
response_choices = nb.dcim.sites.choices()
print("\nChoices for DCIM Sites:")
pprint(response_choices)
# Output:

# {'status': [{'display_name': 'Planned', 'value': 'planned'},
#             {'display_name': 'Staging', 'value': 'staging'},
#             {'display_name': 'Active', 'value': 'active'},
#             {'display_name': 'Decommissioning', 'value': 'decommissioning'},
#             {'display_name': 'Retired', 'value': 'retired'}]}
```

## 3\. What Methods Can Be Called Upon Each Endpoint?

You can dynamically inspect the available methods (like `get`, `filter`, `create`, etc.) on any `pynetbox` endpoint object using the `dir()` function.

```python
print("\nMethods available for `nb.tenancy.tenants` endpoint:")
pprint(dir(nb.tenancy.tenants))
```

Example truncated output:

```
[
 ...,
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

## 4\. How to Know What Fields to Pass for POST or Other Methods?

The NetBox API schema (Swagger/OpenAPI UI) is your best friend for this\!

Visit the API documentation at:
`https://NETBOX_URL/api/schema/swagger-ui`

For example: `https://netbox.intra.slicesoftech.net/api/schema/swagger-ui`

Follow these steps:

a)  **Search for the endpoint** you are working with (e.g., `racks`).
b)  Look at the **POST call** section for this endpoint.
c)  Examine the **Request body**. Anything marked with an asterisk (`*`) is a **mandatory field**.
d)  (Optional) You can also see the **Response body** to understand what will be returned after making the API call.

You can also view the details for GET, PUT, PATCH, and DELETE calls for each endpoint on this page.

```
```