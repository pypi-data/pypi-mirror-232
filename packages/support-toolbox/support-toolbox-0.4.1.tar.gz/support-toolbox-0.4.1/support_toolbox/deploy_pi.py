import json
import requests
from support_toolbox.helper import PRIVATE_API_URLS
from support_toolbox.deploy_browse_card import deploy_browse_card
from support_toolbox.deploy_integrations import deploy_integrations
from support_toolbox.deploy_service_accounts import deploy_service_accounts
import re
from datetime import datetime
import os
import configparser

# Get the path to the user's home directory
user_home = os.path.expanduser("~")

# Construct the full path to the configuration file
tokens_file_path = os.path.join(user_home, ".tokens.ini")

# Initialize the configparser and read the tokens configuration file
config = configparser.ConfigParser()
config.read(tokens_file_path)

# Read tokens/variables for the deploy_service_accounts tool
circleci_api_token = config['deploy_pi']['CIRCLECI_API_TOKEN']

SAML_PLACEHOLDER = {
    "entity_id": "http://www.okta.com/placeholder",
    "sso_url": "https://dev-placeholder.okta.com/app/placeholder/sso/saml",
    "x509_cert": """-----BEGIN CERTIFICATE-----
                MIIDqDCCApCgAwIBAgIGAYDyMs9qMA0GCSqGSIb3DQEBCwUAMIGUMQswCQYDVQQGEwJVUzETMBEG
                A1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzENMAsGA1UECgwET2t0YTEU
                MBIGA1UECwwLU1NPUHJvdmlkZXIxFTATBgNVBAMMDGRldi0xNjk5NDUxNzEcMBoGCSqGSIb3DQEJ
                ARYNaW5mb0Bva3RhLmNvbTAeFw0yMjA1MjMxODMzMTdaFw0zMjA1MjMxODM0MTdaMIGUMQswCQYD
                VQQGEwJVUzETMBEGA1UECAwKQ2FsaWZvcm5pYTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzENMAsG
                A1UECgwET2t0YTEUMBIGA1UECwwLU1NPUHJvdmlkZXIxFTATBgNVBAMMDGRldi0xNjk5NDUxNzEc
                MBoGCSqGSIb3DQEJARYNaW5mb0Bva3RhLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
                ggEBANMQI4i1roai7bnDCAiwDr3FbkKz6RkTOi1Uz1qjnIRfyWIHJRa2yUmjN3+wBmTBHYNkxgMK
                I3g8iElMX3Fz/FFjEYKsCNAq4RZG+sn/zo/8Y6g7bMvz7kc/oXikiuSK/BWFkvx7rSm1fRA+cX6W
                iy3HlsqNPXLUMXlZYV5RK8vF0wxITVJxyvxBaQeKezJD+CNIxVwMBZfgptMxIbKMEHcucVqkp8sa
                aQt0/9Xjser0DbMwPVHKctCyjkXUz/rMfWIw7E6ehL3gFKfHfZn/Mld8PzFg71Ql7AqkYZ8gB9HO
                xUXEeqvIMlqsMu3IlVsEAhF4m+S75TJQJdpvW8NiiRUCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEA
                iOoPf0SRBZE3aE4O65HCYwmCNRBJdbCJqqBEcT1rHUuACCtyq4KB1sOPZfoHURHern7o8jB3UpCV
                aVgdYX05FIkfZnGHYxeZ/7exeDW0kVydhpVouqCqSAdyDhci053Isz2VwAvs5zh2oTa5ChFFZ4bS
                WSmv/eM6RhBePRYe+pExiFhMy2+Rx8O4UV1hTQMr2s3Zp6YYUMqPC23t/3wQaY5YskbZ4E3Qsq6K
                iB7h/2MLj4XZnX+cdmdYmS8K1fPsBPiz5B35v3CqvpzcmfVVyPlIzDVWe87AJneAcqxRrnhHFO3N
                20Qc7OFBZxC0xde8mrIfIaX4y99g4yk8hzHqRQ==
                -----END CERTIFICATE-----"""
}

DEFAULT_ORGS = ["datadotworldsupport", "ddw", "datadotworld-apps"]

DEFAULT_ENTITLEMENTS = {
    "No Personal Datasets": "d9cdbf86-06c4-4e39-8d15-2874e50d2fae",
    "Organization Member Seat Count - Unlimited": "2c20846c-57b2-491f-bbd7-1f32bf0dec2c"
}

CTK_STACK = {
    'catalog-config': 'Catalog Config',
    'catalog-sources': 'Catalog Sources',
    'catalog-sandbox': 'Catalog Sandbox',
    'main': 'Main'
}

CTK_STACK_IMAGES = {
      'catalog-config': 'https://media.data.world/iSELaVlgTWeiy2bh2jhw_catalog-config.png',
      'catalog-sources': 'https://media.data.world/uDofsZwIR1SDUgUfEYp7_catalog-sources.png',
      'catalog-sandbox': 'https://media.data.world/Sue4Y8WVSrCqApwtZDvp_catalog-sandbox.png'
}


def validate_org_input(org_name):
    regex = re.compile(r'[^\w\s-]')
    return not regex.search(org_name)


def create_site(admin_token, entity_id, public_slug, sso_url, x509_cert, api_url):
    url = f"{api_url}/admin/sites/create"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    # Prepare the data to be sent in the request
    data = {
        'entityid': entity_id,
        'publicSlug': public_slug,
        'ssoUrl': sso_url,
        'x509Certificate': x509_cert
    }

    body = json.dumps(data)
    response = requests.post(url, body, cookies=cookies, headers=header)

    if response.status_code == 200:
        print(f"Successfully created the site: {response.text}")
    else:
        print(response.text)


def sanitize_public_slug(slug):
    # Convert to lowercase
    slug = slug.lower()

    # Remove spaces, symbols, and numbers
    slug = re.sub(r'[^a-z]+', '', slug)

    return slug


def update_org_entitlements(admin_token, org_id, product_id, order, source, name):
    update_entitlements_url = f"{PRIVATE_API_URLS['MT/PI']}/entitlements"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    # Format the datetime as a string in the expected format
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    data = {
      "agentid": org_id,
      "entitlementItems": [
        {
          "productid": product_id,
          "quantity": "1"
        }
      ],
      "order": order,
      "source": source,
      "startDate": timestamp
    }

    body = json.dumps(data)
    response = requests.post(update_entitlements_url, body, cookies=cookies, headers=header)

    # Verify the update
    if response.status_code == 200:
        print(f"Successfully updated {org_id} with {name}")
    else:
        print(response.text)


def get_entitlements(admin_token, org_id):
    get_entitlements_url = f"{PRIVATE_API_URLS['MT/PI']}/entitlements/{org_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    response = requests.get(get_entitlements_url, cookies=cookies, headers=header)

    # Verify the response
    if response.status_code == 200:
        response_json = response.json()
        return response_json['records'][0]['source']
    else:
        print(response.text)


def get_offering_id(admin_token):
    get_offering_url = f"{PRIVATE_API_URLS['MT/PI']}/offerings/agentTypes/organization"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    response = requests.get(get_offering_url, cookies=cookies, headers=header)

    # Verify the response
    if response.status_code == 200:
        response_json = response.json()
        return response_json['records'][0]['offeringid']
    else:
        print(response.text)


def update_default_plan(admin_token, offering_id):
    update_default_plan_url = f"{PRIVATE_API_URLS['MT/PI']}/offerings/{offering_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    # Format the datetime as a string in the expected format
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    data = {
        "agentType": "ORGANIZATION",
        "defaultOffering": True,
        "offeringSlug": "10745-pi-team-enterprise",
        "offeringid": offering_id,
        "pricingModel": {},
        "productids": [
            "0f0c106c-a264-41ec-a055-d89c12c0123b",
            f"{DEFAULT_ENTITLEMENTS['No Personal Datasets']}",
            f"{DEFAULT_ENTITLEMENTS['Organization Member Seat Count - Unlimited']}"
        ],
        "requiresPayment": False,
        "startDate": timestamp
    }

    body = json.dumps(data)
    response = requests.put(update_default_plan_url, body, cookies=cookies, headers=header)

    # Verify the update
    if response.status_code == 200:
        for name, product_id in DEFAULT_ENTITLEMENTS.items():
            print(f"Successfully updated Organization Default Plan with: {name}")
    else:
        print(response.text)


def config_site(admin_token):
    # Update the orgs that are created by default with the necessary Default Entitlements
    for org_id in DEFAULT_ORGS:
        source = get_entitlements(admin_token, org_id)
        order = 1
        for name, product_id in DEFAULT_ENTITLEMENTS.items():
            update_org_entitlements(admin_token, org_id, product_id, order, source, name)
            order += 1

    # Update Org Default Plan with the necessary Default Entitlements
    offering_id = get_offering_id(admin_token)
    update_default_plan(admin_token, offering_id)

    # Authorize 'datadotworldsupport' access to 'ddw'
    authorize_access_to_org(admin_token, 'ddw')


def onboard_org(admin_token, org_id, org_display_name, avatar_url=''):
    onboard_org_url = f"{PRIVATE_API_URLS['MT/PI']}/organizations/onboard"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    data = {
        "agentid": org_id,
        "avatarUrl": avatar_url,
        "displayName": org_display_name,
        "orgDetails": {
            "allowMembership": True,
            "allowMembershipRequest": False,
            "allowProposals": False,
            "defaultMembershipType": 'PUBLIC'
        },
        "visibility": 'OPEN'
    }

    body = json.dumps(data)
    response = requests.post(onboard_org_url, body, cookies=cookies, headers=header)

    # Verify the creation
    if response.status_code == 200:
        print(f"Successfully created {org_id}")
    else:
        print(response.text)


def authorize_access_to_org(admin_token, org_id):
    authorize_access_to_org_url = f"{PRIVATE_API_URLS['MT/PI']}/admin/organizations/{org_id}/authorizations/group%3Adatadotworldsupport%2Fmembers"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    data = {
        "level": "ADMIN",
        "visibility": "PUBLIC"
    }

    body = json.dumps(data)
    response = requests.put(authorize_access_to_org_url, body, cookies=cookies, headers=header)

    # Verify the authorization
    if response.status_code == 200:
        print(f"Authorized datadotworldsupport ADMIN in {org_id}")
    else:
        print(response.text)


def create_dataset(admin_token, org_id, title):
    create_dataset_url = f"https://api.data.world/v0/datasets/{org_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    payload = {
        "title": title,
        "visibility": "PRIVATE"
    }

    body = json.dumps(payload)

    # Create the service account
    response = requests.post(create_dataset_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        print(f"created dataset: {title}")
    else:
        print(response.text)


def deploy_metrics(admin_token, public_slug):
    existing_customer = None

    # Ask user to select an option
    print("Before we continue, please select an option (1/2): ")
    print("1. Existing customer moving to a PI")
    print("2. New customer PI deployment")
    user_choice = input()

    # Set existing_customer based on user input
    if user_choice == "1":
        existing_customer = True
    elif user_choice == "2":
        existing_customer = False
    else:
        print("Invalid selection.")
        return

    metrics_deployment_choice = input("Start metrics deployment? (y/n): ")

    if metrics_deployment_choice.lower() == 'y':
        org_id = "data-catalog-team"
        org_display_name = "Data Catalog Team"

        standard_org_choice = input("Use the standard Data Catalog Team org (y/n): ")

        if standard_org_choice.lower() == 'n':
            org_id = input("Enter the org id: ")
            org_display_name = input("Enter the org display name: ")

        print(f"Onboarding {org_id}...")
        onboard_org(admin_token, org_id, org_display_name)

        print(f"Authorizing datadotworldsupport access to {org_id}...")
        authorize_access_to_org(admin_token, org_id)

        if existing_customer:
            # Create ddw-metrics-{public_slug} dataset
            create_dataset(admin_token, org_id, title=f"ddw-metrics-{public_slug}")
            public_slug = public_slug + "_PI"

        else:
            all_time_metrics_choice = input("Is the customer paying for the 'All-time' metrics upgrade (y/n): ")

            if all_time_metrics_choice.lower() == 'y':
                # Create ddw-metrics-{public_slug} dataset
                create_dataset(admin_token, org_id, title=f"ddw-metrics-{public_slug}")
            else:
                # Create ddw-metrics-{public_slug}-last-90-days dataset
                create_dataset(admin_token, org_id, title=f"ddw-metrics-{public_slug}-last-90-days")

        # Create the baseplatformdata dataset
        create_dataset(admin_token, org_id, title="baseplatformdata")
        return public_slug

    else:
        metrics_continue_choice = input("Do you want to continue without completing the metrics setup?\n"
                                        "We will skip creating the necessary org and datasets for metric deployment (y/n): ")

        if metrics_continue_choice.lower() == 'n':
            # Restart the metrics deployment process
            deploy_metrics(admin_token, public_slug)
        else:
            print("Continuing without metrics setup...")


def deploy_ctk(admin_token, prefix=None):
    for org_id, org_display_name in CTK_STACK.items():
        if org_id != 'main':
            avatar_url = CTK_STACK_IMAGES[org_id]
        if prefix:
            org_id = f"{prefix} {org_id}"
            org_id = org_id.replace(' ', '-').lower()
            org_display_name = f"{prefix} {org_display_name}"

        onboard_org(admin_token, org_id, org_display_name, avatar_url)
        authorize_access_to_org(admin_token, org_id)


def get_agent_id(admin_token):
    get_user_url = f"{PRIVATE_API_URLS['MT/PI']}/user"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    response = requests.get(get_user_url, cookies=cookies, headers=header)

    # Verify the get
    if response.status_code == 200:
        response_json = response.json()
        agent_id = response_json['agentid']
        return agent_id
    else:
        print(response.text)


def deauthorize_access_to_org(admin_token, agent_id, org_id):
    deauthorize_access_to_org_url = f"{PRIVATE_API_URLS['MT/PI']}/organizations/{org_id}/authorizations/agent%3A{agent_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {admin_token}'
    }

    cookies = {
        'adminToken': admin_token
    }

    response = requests.delete(deauthorize_access_to_org_url, cookies=cookies, headers=header)

    # Verify the authorization
    if response.status_code == 200:
        print(f"Removed {agent_id} from {org_id}")
    else:
        print(response.text)


def cleanup_site_creation(admin_token):
    agent_id = get_agent_id(admin_token)
    print(f"Cleaning up any resources {agent_id} is in...")

    for org_id in DEFAULT_ORGS:
        if org_id == 'datadotworldsupport':
            continue
        deauthorize_access_to_org(admin_token, agent_id, org_id)

    for org_id in CTK_STACK:
        deauthorize_access_to_org(admin_token, agent_id, org_id)

    # Update this to use whatever org was created during metrics creation
    deauthorize_access_to_org(admin_token, agent_id, "data-catalog-team")


def run():
    api_url = PRIVATE_API_URLS['MT/PI']

    while True:
        user_input = input("Enter the URL slug: ")
        public_slug = sanitize_public_slug(user_input)

        if not public_slug:
            print("Invalid slug. Please enter a valid URL slug.")
            continue

        preview_url = f"https://{public_slug}.app.data.world"
        selection = input(f"Here is a preview of the URL: {preview_url}\nDoes this look correct? (y/n): ")

        if selection == 'y':
            saml_choice = input("Do you want to use placeholder values for SAML? (y/n): ")
            if saml_choice == 'y':
                entity_id = SAML_PLACEHOLDER['entity_id']
                sso_url = SAML_PLACEHOLDER['sso_url']
                x509_cert = SAML_PLACEHOLDER['x509_cert']

            else:
                sso_url = input("Enter the SSO URL: ")
                entity_id = input("Enter the Entity ID: ")
                x509_cert = input("Enter the X.509 Certificate: ")

            # Final verification before creating site
            print(f"\n{preview_url} will deploy with the following SAML values")
            print(f"SSO URL: {sso_url}")
            print(f"ENTITY ID: {entity_id}")
            print(f"x509 CERTIFICATE: {x509_cert}")

            # Create site
            admin_token = input("Enter your active admin token for the community site: ")
            create_site(admin_token, entity_id, public_slug, sso_url, x509_cert, api_url)

            # Get the users active admin_token to complete the deployment using Private APIs
            admin_token = input(f"Enter your active admin token for the {public_slug} site: ")

            # Configure site with default entitlements, update org entitlements, update permissions
            config_site(admin_token)

            # Deploy CTK using the entered 'main' org as the Display Name
            while True:
                main_display_name = input("What will the Display Name for the 'main' org be called? (CASE SENSITIVE): ")
                if validate_org_input(main_display_name):
                    CTK_STACK['main'] = main_display_name
                    break
                else:
                    print('Invalid organization name. Please try again.')
            deploy_ctk(admin_token)

            # Deploy Metrics and return the altered public_slug used to create service accounts
            public_slug = deploy_metrics(admin_token, public_slug)

            print("Deploying browse card...")
            deploy_browse_card(admin_token, 'n')

            print("Deploying integrations...")
            deploy_integrations(admin_token, '1')

            print("Deploying service accounts...")
            deploy_service_accounts(admin_token, public_slug, circleci_api_token=circleci_api_token)

            cleanup_site_creation(admin_token)
            break

        # URL Value denied
        elif selection == 'n':
            continue

        # URL Value invalid
        else:
            print("Enter a valid option: 'y'/'n'")
