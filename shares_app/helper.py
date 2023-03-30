import json

import requests
from decouple import config


def send_flexi_bundle(current_user, user_details, receiver, bundle):
    url = "https://backend.boldassure.net:445/live/api/context/business/transaction/new-transaction"

    payload = json.dumps({
        "accountNo": f"233{str(user_details.phone)}",
        "accountFirstName": current_user.first_name,
        "accountLastName": current_user.last_name,
        "accountMsisdn": str(receiver),
        "accountEmail": current_user.email,
        "accountVoiceBalance": 0,
        "accountDataBalance": float(bundle),
        "accountCashBalance": 0,
        "active": True
    })

    headers = {
        'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJkY2I3ZmZiZi1mNWE3LTQ2YjUtOGQyMC0wNWMwYjYyMWY3YWMiLCJhdXRob3JpdGllcyI6W3siYXV0aG9yaXR5IjoiUk9MRV9BRE1JTiJ9XSwiaWF0IjoxNjgwMTc4Nzk3LCJleHAiOjE2ODAyMjA4MDB9.z84drleKn5LVnPFGIWDYJ5sMh70G2QiI-05_dHpjgvrHSSeiAX09_ymipL6cC-3-XDEQmJyG6aTQzTe0SwDrhg',
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
        'Authorization': 'Bearer eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJkY2I3ZmZiZi1mNWE3LTQ2YjUtOGQyMC0wNWMwYjYyMWY3YWMiLCJhdXRob3JpdGllcyI6W3siYXV0aG9yaXR5IjoiUk9MRV9BRE1JTiJ9XSwiaWF0IjoxNjgwMTc4Nzk3LCJleHAiOjE2ODAyMjA4MDB9.z84drleKn5LVnPFGIWDYJ5sMh70G2QiI-05_dHpjgvrHSSeiAX09_ymipL6cC-3-XDEQmJyG6aTQzTe0SwDrhg'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.json())
    return response.json()


