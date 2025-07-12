import meraki
import logging
import json

# --- Setup basic logging; this will be common across all scripts FYI ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# --- loading key from a file; this will be common across all scripts FYI ---
# you should place your key somewhere safe. my key is not part of the git.

with open("../Secrets/keys.json", "r") as temp:
    secret = json.load(temp)
    API_KEY = secret["api_key"]


def main():
    try:
        dashboard = meraki.DashboardAPI(
            api_key=API_KEY,
            suppress_logging=True  # Optional: disables verbose HTTP logs
        )

        orgs = dashboard.organizations.getOrganizations()
        logging.info(f"data from orgs:\n {orgs}\n")
        logging.info(f"Found {len(orgs)} organization(s).")
        logging.info(f"\n@@@\nRaw data from orgs object: \n{orgs}\n@@@")
        for org in orgs:
            org_id = org['id']
            org_name = org['name']
            logging.info(f"Organization: {org_name} (ID: {org_id})")
            networks = dashboard.organizations.getOrganizationNetworks(org_id)
            logging.info(
                f"\n@@@\nRaw data from networks object: \n{networks}\n@@@")
            logging.info(f"  Found {len(networks)} network(s):")
            for net in networks:
                logging.info(f"    - {net['name']} (ID: {net['id']})")

    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()
