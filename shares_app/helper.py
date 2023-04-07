import json

import requests
from decouple import config


def send_flexi_bundle(current_user, user_details, receiver, bundle):
    url = "https://backend.boldassure.net:445/live/api/context/business/transaction/new-transaction"

    payload = json.dumps({
        "accountNo": f"233{str(user_details.phone)}",
        "accountFirstName": current_user.first_name,
        "accountLastName": current_user.last_name,
        "accountMsisdn": str(receiver).strip(),
        "accountEmail": current_user.email,
        "accountVoiceBalance": 0,
        "accountDataBalance": float(bundle),
        "accountCashBalance": 0,
        "active": True
    })

    headers = {
        'Authorization': config("BEARER_TOKEN"),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    json_data = response.json()
    print(json_data)
    print(json_data)
    return {'response': response, 'json_data': json_data}


def verify_bundle_txn(batch_id):

    url = f"https://backend.boldassure.net:445/live/api/context/business/airteltigo-gh/ishare/tranx-status/{str(batch_id)}"

    payload = {}
    headers = {
        'Authorization': config("BEARER_TOKEN")
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.json())
    return response.json()


def check_network(phone_number):
    if phone_number:
        if str(phone_number)[4] == "4" or str(phone_number)[4] == "5" or str(phone_number)[4] == "9":
            return f"https://cs.hubtel.com/commissionservices/2016884/3e0841e70afc42fb97d13d19abd36384?destination={phone_number}"
        elif str(phone_number)[4] == "7" or str(phone_number)[4] == "6":
            return f"https://cs.hubtel.com/commissionservices/2016884/0d542e644a4440a3ae122adcfbade818?destination={phone_number}"
        elif str(phone_number)[4] == "0":
            return f"https://cs.hubtel.com/commissionservices/2016884/8767ecd553a7415e96c22eb9adae2879?destination={phone_number}"


def display_name(phone_number):
    url = check_network(phone_number)

    payload = json.dumps({
        "destination": phone_number
    })

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': config("HUBTEL_API_KEY")
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()
    customer_name = data["Data"][0]["Value"]
    return customer_name
