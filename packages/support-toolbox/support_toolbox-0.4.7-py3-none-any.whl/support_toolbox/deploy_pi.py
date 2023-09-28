import json
import requests
import re
import os
import configparser
from support_toolbox.utils.helper import PRIVATE_API_URLS
from support_toolbox.utils.user import get_agent_id
from support_toolbox.deploy_browse_card import deploy_browse_card
from support_toolbox.deploy_integrations import deploy_integrations
from support_toolbox.deploy_service_accounts import deploy_service_accounts
from support_toolbox.utils.org import onboard_org, authorize_access_to_org, deauthorize_access_to_org, validate_org_input
from support_toolbox.deploy_ctk import deploy_ctk, CTK_STACK
from support_toolbox.utils.entitlements import update_org_entitlements, get_entitlements, get_offering_id, update_default_plan, DEFAULT_ENTITLEMENTS

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


def cleanup_site_creation(admin_token):
    agent_id = get_agent_id(admin_token)
    print(f"Cleaning up any resources {agent_id} is in...")

    for org_id in DEFAULT_ORGS:
        if org_id == 'datadotworldsupport':
            continue
        deauthorize_access_to_org(admin_token, agent_id, org_id)

    # TODO: Update this to use whatever org was created during metrics creation
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
