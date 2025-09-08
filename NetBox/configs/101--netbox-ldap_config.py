# /opt/netbox/netbox/netbox/ldap_config.py
import ldap
from django_auth_ldap.config import LDAPSearch, NestedGroupOfNamesType

# --- Server & bind ---
# Use ldaps on 636 or Global Catalog on 3269 if you have multiple domains in a forest
# or "ldaps://gc.example.com:3269"
AUTH_LDAP_SERVER_URI = "ldaps://dc-01.intra.wonderingpacket.com"
AUTH_LDAP_CONNECTION_OPTIONS = {
    ldap.OPT_REFERRALS: 0,  # AD: avoid referral chasing loops
}

# NetBox service account (read-only)
AUTH_LDAP_BIND_DN = "CN=netbox-sa,OU=WP-ServiceAccounts,DC=intra,DC=wonderingpacket,DC=com"
AUTH_LDAP_BIND_PASSWORD = "PASSWORD"

# TLS / certificates
# If you have a proper CA installed on the host, you usually don't need to set these.
# To trust system CAs:
LDAP_CA_CERT_DIR = '/etc/ssl/certs'
# If you need to pin your own CA file instead:
# LDAP_CA_CERT_FILE = '/path/to/your-ca.crt'
# If you're in a lab with self-signed certs and just need to get moving:
# (Not recommended for prod)
# LDAP_IGNORE_CERT_ERRORS = True

# STARTTLS path (only if you're using ldap://, not ldaps://)
# AUTH_LDAP_START_TLS = True

# --- User auth & attributes ---
# Allow login by either sAMAccountName ("username") OR UPN ("username@domain.tld")
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "DC=intra,DC=wonderingpacket,DC=com",
    ldap.SCOPE_SUBTREE,
    "(&(|(userPrincipalName=%(user)s)(sAMAccountName=%(user)s))"
    "(objectCategory=Person)(objectClass=User))"
)
# AD best practice: don't use a DN template when searching by sAMAccountName/UPN
AUTH_LDAP_USER_DN_TEMPLATE = None

# Map AD attrs to Django user fields
AUTH_LDAP_USER_ATTR_MAP = {
    "username": "sAMAccountName",
    "email": "mail",
    "first_name": "givenName",
    "last_name": "sn",
}
# Tell NetBox to query users by the "username" field (populated above)
AUTH_LDAP_USER_QUERY_FIELD = "username"

# --- Groups & permissions ---
# Pull groups from AD, with nested group support
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
    "OU=WP-Groups,DC=intra,DC=wonderingpacket,DC=com",
    ldap.SCOPE_SUBTREE,
    "(&(objectClass=group)(|(cn=ADM-Netbox*)(cn=Netbox*)))"
)
AUTH_LDAP_GROUP_TYPE = NestedGroupOfNamesType()

# Require membership in this AD group to log in (set to a real group DN)
AUTH_LDAP_REQUIRE_GROUP = "CN=Netbox-Users,OU=WP-Groups,DC=intra,DC=wonderingpacket,DC=com"

# Mirror AD group membership into Django (group names will be created if needed)
AUTH_LDAP_MIRROR_GROUPS = True

# Optional: map special flags by group (use with extreme caution)
AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_superuser": "CN=Netbox-SuperAdmins,OU=WP-Groups,DC=intra,DC=wonderingpacket,DC=com",
    "is_active":    "CN=Netbox-Users,OU=WP-Groups,DC=intra,DC=wonderingpacket,DC=com",
}

# Pull fine-grained Django perms from mapped groups
AUTH_LDAP_FIND_GROUP_PERMS = True

# Keep group lookups warm for an hour
AUTH_LDAP_CACHE_TIMEOUT = 0

# Always update user details on login (names, email, groups)
AUTH_LDAP_ALWAYS_UPDATE_USER = True
