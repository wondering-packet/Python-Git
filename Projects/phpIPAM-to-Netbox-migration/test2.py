import keyring

# Save your Meraki API key securely
keyring.set_password("netbox", "api_key",
                     "blahblah31dc1f7da76eb32bff43bf9de3cc288")
