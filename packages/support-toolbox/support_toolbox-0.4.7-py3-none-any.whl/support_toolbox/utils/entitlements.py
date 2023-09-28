import json
import requests
from datetime import datetime
from support_toolbox.utils.helper import PRIVATE_API_URLS

DEFAULT_ENTITLEMENTS = {
    "No Personal Datasets": "d9cdbf86-06c4-4e39-8d15-2874e50d2fae",
    "Organization Member Seat Count - Unlimited": "2c20846c-57b2-491f-bbd7-1f32bf0dec2c"
}


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
