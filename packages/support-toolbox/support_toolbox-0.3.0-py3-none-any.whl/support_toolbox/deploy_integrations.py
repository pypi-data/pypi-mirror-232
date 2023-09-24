import requests
import json
import subprocess
import os

INTEGRATIONS = [
    "athena", "azure-synapse", "bigquery", "denodo",
    "ibm-db2", "infor-ion", "java-jdbc", "microsoft-sql-server",
    "mysql", "oracle-database", "postgresql",
    "python", "redshift", "snowflake"
]


def push_integration(integration):
    command = f"bin/apply {integration}.template"

    directory_path = os.path.expanduser("~/integration-templates")

    # Execute the terminal command in the specified directory
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            cwd=directory_path)

    # Check the result
    if result.returncode == 0:
        print("Command executed successfully:")
        print(result.stdout)
    else:
        print("Command failed:")
        print(result.stderr)


def add_discoverable_to_integration(org, dataset_id, api_token):
    update_dataset = f"https://api.data.world/v0/datasets/{org}/{dataset_id}"

    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_token}'
    }

    payload = {
        "visibility": "DISCOVERABLE"
    }
    body = json.dumps(payload)

    # Update a specific dataset
    response = requests.patch(update_dataset, body, headers=header)

    # Verify the update
    if response.status_code == 200:
        response_json = response.json()
        print(response_json)
    else:
        print(response.text)


def run():
    api_token = input("Enter your API Token for the site you are deploying integrations to: ")
    os.environ["DW_AUTH_TOKEN"] = api_token

    for integration in INTEGRATIONS:
        print(integration)
    selection = input("Enter '1' to deploy the default list of integrations, or '2' to specify an integration outside the list: ")

    if selection == '1':
        # Deploy all specific integrations in the INTEGRATIONS list
        for integration_name in INTEGRATIONS:
            push_integration(integration_name)
            add_discoverable_to_integration("datadotworld-apps", integration_name, api_token)
    elif selection == '2':
        # Deploy a custom integration
        integration_name = input("Enter the name of the custom integration you want to deploy: ")
        push_integration(integration_name)
        add_discoverable_to_integration("datadotworld-apps", integration_name, api_token)
    else:
        print("Invalid selection. Please enter '1' to deploy all specific integrations or '2' to deploy a custom integration.")
