import json
import secrets

import requests
from decouple import config
from rest_framework import status
from rest_framework.response import Response

from . import models
from .api import api_views


def send_flexi_bundle(request, user_details, current_user, receiver, bundle, reference, doing):
    response = api_views.ValidateAPIKeysView().post(request).data
    print(receiver)
    if response["valid"]:
        user_transactions = models.NewTransaction.objects.filter(user=user_details)
        for transaction in user_transactions:
            if transaction.reference == reference:
                reference = reference = f"{secrets.token_hex(6)}".upper()

        url = "https://console.hubnet.app/live/api/context/business/transaction/at-new-transaction"

        payload = json.dumps({
            "phone": str(receiver),
            "volume": str(int(bundle)),
            "reference": reference
        })

        headers = {
            'token': config("HUBNET_KEYY"),
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        current_user.bundle_amount -= bundle
        current_user.save()

        print(response.text)
        data = response.json()

        # Check the response
        if response.status_code == 200:
            print("Request successful:", response.json())
            data = response.json()
            response_code = data["data"]["response_code"]
            if response_code == "200":
                new_transaction = models.NewTransaction.objects.create(
                    user=user_details,
                    reference=reference,
                    batch_id=reference,
                    receiver=receiver,
                    account_number=current_user.phone,
                    first_name=user_details.first_name,
                    last_name=user_details.last_name,
                    account_email=user_details.email,
                    bundle_amount=bundle,
                    transaction_status="Completed"
                )
                new_transaction.save()
                print(current_user.bundle_amount)
                return Response(
                    data={"code": "0000", "status": "Success", "message": "Transaction was completed successfully",
                          "reference": reference}, status=status.HTTP_200_OK)
            else:
                print("Request failed with status code:", response.status_code)
                print("Response:", response.text)
                print(receiver)
                new_transaction = models.NewTransaction.objects.create(
                    user=user_details,
                    reference=reference,
                    batch_id="Null",
                    receiver=receiver,
                    account_number=current_user.phone,
                    first_name=user_details.first_name,
                    last_name=user_details.last_name,
                    account_email=user_details.email,
                    bundle_amount=bundle,
                    transaction_status="Failed"
                )
                new_transaction.save()
                return Response(data={"code": "0001", "error": response.status_code, "status": "Failed",
                                      "message": "Something went wrong."},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            print("Request failed with status code:", response.status_code)
            print("Response:", response.text)
            print(receiver)
            new_transaction = models.NewTransaction.objects.create(
                user=user_details,
                reference=reference,
                batch_id="Null",
                receiver=receiver,
                account_number=current_user.phone,
                first_name=user_details.first_name,
                last_name=user_details.last_name,
                account_email=user_details.email,
                bundle_amount=bundle,
                transaction_status="Failed"
            )
            new_transaction.save()
            return Response(data={"code": "0001", "error": response.status_code, "status": "Failed",
                                  "message": "Something went wrong."},
                            status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(data={"code": "0001", "error": "Authentication error", "status": "Failed",
                              "message": "Unable to authenticate using Authentication keys. Check and try again."},
                        status=status.HTTP_401_UNAUTHORIZED)
    # response = api_views.NewTransactionView()
    # response.setup(request).
    #
    # # url = "https://console.bestpaygh.com/api/flexi/v1/new_transaction/"
    # # print(user_details.first_name)
    # # print(type(user_details.first_name))
    # # print(current_user.phone)
    # # print(type(current_user.phone))
    # # print(bundle)
    # # print(user_details.email)
    # #
    # # payload =
    # json.dumps({
    #     "first_name": user_details.first_name,
    #     "last_name": user_details.last_name,
    #     "account_number": current_user.phone,
    #     "receiver": str(receiver),
    #     "account_email": user_details.email,
    #     "reference": reference,
    #     "bundle_amount": bundle
    # })
    # # headers = {
    # #     'api-key': user_details.api_key,
    # #     'api-secret': user_details.api_secret,
    # #     'Content-Type': 'application/json',
    # # }
    # #
    # # response = requests.request("POST", url, headers=headers, data=payload)
    # # print("posted in send flexi bundle")
    # # print(response.json())
    # print(response)
    # return response


def api_send_bundle(data):
    bundle = data["bundle_amount"]
    receiver = data["receiver"]
    reference = data['reference']

    print(receiver)
    print(bundle)
    print(reference)
    print(config("HUBNET_KEY"))

    url = "https://console.hubnet.app/live/api/context/business/transaction/at-new-transaction"

    payload = json.dumps({
        "phone": str(receiver),
        "volume": str(int(bundle)),
        "reference": reference
    })

    headers = {
        'token': config("HUBNET_KEYY"),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    data = response.json()
    print(data)

    if response.status_code == 200:
        print("Request successful:", response.json())
    else:
        print("Request failed with status code:", response.status_code)
        print("Response:", response.text)

    return response


def api_verify_transaction(batch_id):
    url = f"https://backend.boldassure.net:445/live/api/context/business/airteltigo-gh/ishare/tranx-status/{batch_id}"

    payload = {}
    headers = {
        'Authorization': config("BEARER_TOKEN")
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    print(response.json())
    return response.json()


def verify_bundle_txn(batch_id):
    url = f"https://backend.boldassure.net:445/live/api/context/business/airteltigo-gh/ishare/tranx-status/{str(batch_id)}"

    payload = {}
    headers = {
        'Authorization': config("BEARER_TOKEN")
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    return response


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
