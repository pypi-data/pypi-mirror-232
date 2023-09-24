import configparser
import os
import requests
import json

# Get the path to the user's home directory
user_home = os.path.expanduser("~")

# Construct the full path to the configuration file
tokens_file_path = os.path.join(user_home, ".tokens.ini")

# Initialize the configparser and read the tokens configuration file
config = configparser.ConfigParser()
config.read(tokens_file_path)

# Read tokens/variables for the deploy_service_accounts tool
circleci_api_token = config['deploy_service_accounts']['CIRCLECI_API_TOKEN']

# Org that will "own" the Service Accounts in a PI
owner = "datadotworldsupport"

# Create Service Account payloads
SERVICE_ACCOUNTS = [
    {
        "desiredUsername": "ctk",
        "displayName": "DDW Catalog Toolkit Service"
    },
    {
        "desiredUsername": "ddwmetrics",
        "displayName": "DDW Platform Metrics Service"
    }
]

CIRCLECI_PROJECTS = ["catalog-config", "mca"]


def create_env_variable(circleci_project, name, value):
    url = f"https://circleci.com/api/v2/project/github/datadotworld/{circleci_project}/envvar"

    headers = {
        "Circle-Token": circleci_api_token
    }

    payload = {
        "name": name,
        "value": value
    }

    response = requests.post(url, payload, headers=headers)

    if response.status_code == 201:
        print(f"Added '{name}' to the '{circleci_project}' project environment variables in CircleCI ")
    else:
        print(f"Error: Unable to create environment variables. Status Code: {response.status_code}")


def deploy_service_account(api_token, payload):
    create_service_account_url = f"https://api.data.world/v0/serviceaccount/{owner}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }

    body = json.dumps(payload)

    # Create the service account
    response = requests.post(create_service_account_url, body, headers=header)

    # Verify the creation
    if response.status_code == 200:
        response_json = response.json()

        service_account = response_json['serviceAccountUsername']
        service_account_token = response_json['token']
        print(f"created service account: {service_account}")
        return service_account_token
    else:
        print(response.text)


def run():
    api_token = input("Enter your API Token for the site you are deploying service accounts to: ")
    site_slug = input("Enter the customer's site slug: ")
    for i, sa in enumerate(SERVICE_ACCOUNTS):
        token = deploy_service_account(api_token, sa)

        # Configure parameters for CircleCI API
        circleci_project = CIRCLECI_PROJECTS[i]
        name = site_slug.upper() + "_API_TOKEN"

        create_env_variable(circleci_project, name, token)
