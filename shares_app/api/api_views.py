import json

import requests
from decouple import config
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from rest_framework import status

from .. import models, helper
from ..models import CustomUser, NewTransaction
from ..serializers import TransactionSerializer


class APIKeysView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        if user:
            return Response(
                data={"code": "0000", "status": "Success", "api_key": user.api_key, "api_secret": user.api_secret},
                status=status.HTTP_200_OK)

    def post(self, request):
        user = CustomUser.objects.get(id=request.user.id)
        if user:
            api_key = get_random_string(32, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$-")
            api_secret = get_random_string(64, allowed_chars="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789$-")
            user.api_key = api_key
            user.api_secret = api_secret
            user.save()
            return Response(
                data={"code": "0000", "status": "Success", "api_key": api_key, "api_secret": api_secret,
                      "message": "API key generation successful"},
                status=status.HTTP_200_OK)


class ValidateAPIKeysView(APIView):
    def post(self, request):
        api_key = request.headers.get("api-key")
        api_secret = request.headers.get("api-secret")

        if api_key is None:
            print("using the if")
            user = CustomUser.objects.get(id=request.user.id)
            print(user.last_name)
            api_key = user.api_key
            api_secret = user.api_secret
            revoked = user.api_revoked
            print(api_key)
            print(api_secret)

            if user:
                print("user dey")
                username = user.username
                if api_key and api_secret and not revoked:
                    print("true api for if")
                    return Response(data={"code": "0000", "message": "Valid API Key", "valid": True, "username": username},
                                    status=status.HTTP_200_OK)
                else:
                    return Response(data={"code": "0001", "status": "Failed", "error": "Authentication Error",
                                          "message": "Authentication Failed for this account.", "valid": False},
                                    status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(
                    data={"code": "0001", "status": "Failed", "error": "Not Found Error",
                          "message": "No user found with this API Key",
                          "valid": False}, status=status.HTTP_200_OK)
        else:
            print("using the else")
            try:
                user = CustomUser.objects.get(api_key=api_key)
            except:
                return Response(
                    data={"code": "0001", "status": "Failed", "error": "Not Found Error",
                          "message": "No user found with this API Key",
                          "valid": False}, status=status.HTTP_200_OK)

            if user:
                username = user.username
                print(user.api_key == api_key)
                if str(user.api_key) == str(api_key) and user.has_valid_api_secret(
                        api_secret) and not user.api_revoked:
                    return Response(data={"code": "0000", "message": "Valid API Key", "valid": True, "username": username},
                                    status=status.HTTP_200_OK)
                else:
                    return Response(data={"code": "0001", "status": "Failed", "error": "Authentication Error",
                                          "message": "Authentication Failed for this account.", "valid": False},
                                    status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(
                    data={"code": "0001", "status": "Failed", "error": "Not Found Error",
                          "message": "No user found with this API Key",
                          "valid": False}, status=status.HTTP_200_OK)

@api_view(["GET"])
def transactions(request):
    all_transactions = NewTransaction.objects.all().order_by("transaction_date").reverse()
    serializer = TransactionSerializer(all_transactions, many=True)
    return JsonResponse({"transactions": serializer.data}, safe=True)


class NewTransactionView(APIView):
    # # serializer = TransactionSerializer(data=request.data)
    # try:
    #     user_token = Token.objects.get(user=request.user)
    # except:
    #     user_token = Token.objects.create(user=request.user)
    def post(self, request):
        data = ValidateAPIKeysView().post(request).data
        print(data)
        if data["valid"]:
            try:
                user = CustomUser.objects.get(api_key=request.headers.get("api-key"))
            except:
                user = CustomUser.objects.get(username=data["username"])
            all_user_transactions = NewTransaction.objects.filter(user=user)
            serializer = TransactionSerializer(data=request.data)
            if serializer.is_valid():
                bundle_amount = serializer.validated_data["bundle_amount"]
                reference = serializer.validated_data["reference"]
                for transaction in all_user_transactions:
                    if transaction.reference == reference:
                        return Response(data={"code": "0001", "status": "Failed", "error": "Duplicate Error",
                                              "message": "Transaction reference already exists"},
                                        status=status.HTTP_400_BAD_REQUEST)
                try:
                    user = CustomUser.objects.get(api_key=request.headers.get("api-key"))
                except:
                    user = user = CustomUser.objects.get(username=data["username"])
                user_profile = models.UserProfile.objects.filter(user=user).first()
                user_bundle_left = user_profile.bundle_amount
                if bundle_amount > user_bundle_left:
                    return Response(data={"code": "0001", "status": "Failed", "error": "Insufficient Balance",
                                          "message": "You do not have enough balance to perform this transaction"},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    response = helper.api_send_bundle(serializer.validated_data)
                    print(response.json())
                    print("this")
                    data = response.json()
                    print(data)
                    if response.status_code == 200:
                        serializer.save(
                            user=user,
                            transaction_status="Completed",
                            batch_id="Null"
                        )
                        print(user_profile.bundle_amount)
                        user_profile.bundle_amount -= bundle_amount
                        user_profile.save()
                        # ver_response = requests.get(url=f"https://console.bestpaygh.com/api/v1/transaction_detail/{batch_id}/")
                        # print(ver_response.json())
                        return Response(
                            data={"code": "0000", "status": "Success", "message": "Transaction was completed successfully",
                                  "reference": reference}, status=status.HTTP_200_OK)
                    else:
                        serializer.save(
                            user=user,
                            transaction_status="Failed",
                        )
                        return Response(data={"code": "0001", "status": "Failed", "error": "Transaction not successful",
                                              "message": "Transaction could not be processed. Try again later."},
                                        status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    data={"code": "0001", "status": "Failed", "error": "Body error",
                          "message": "Body Parameters set not valid. Check and try again."},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={"code": "0001", "error": "Authentication error", "status": "Failed",
                                  "message": "Unable to authenticate using Authentication keys. Check and try again."},
                            status=status.HTTP_401_UNAUTHORIZED)

    def options(self, request, *args, **kwargs):
        print("used options")
        # Handle OPTIONS request for CORS preflight check
        response = super().options(request, *args, **kwargs)

        # Add CORS headers to the OPTIONS response
        response["Access-Control-Allow-Origin"] = "https://test.bestpaygh.com"  # Replace with your allowed origin
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, api-key, api-secret, accept-encoding, Accept-Language, origin, Access-Control-Allow-Methods"  # Allow specific headers

        return response


class TransactionDetail(APIView):
    # print("querying")
    # headers = {
    #     "api-key": request.headers.get("api-key"),
    #     "api-secret": request.headers.get("api-secret")
    # }
    # response = requests.post("https://console.bestpaygh.com/validate-api-keys/", headers=headers)
    # data = response.json()
    # print(response)
    def post(self, request, reference):
        response = ValidateAPIKeysView().post(request)
        print(response.data)

        if response.data["valid"]:
            api_key = request.headers.get("api-key")
            print(api_key)
            if api_key:
                print("yhp")
                user = CustomUser.objects.get(api_key=api_key)
            else:
                print("nope")
                print("using this instead")
                user = CustomUser.objects.get(id=request.user.id)
                print(user)
            wanted_transaction = NewTransaction.objects.filter(reference=reference, user=user).first()
            print(wanted_transaction)
            if wanted_transaction:
                transaction_id = reference  # Replace with the actual transaction ID
                url = f"https://api.hubnet.app/verify?transaction_id={transaction_id}"

                # Header with the API key
                headers = {
                    "X-HUBNET-KEY": config("HUBNET_KEY"),
                }

                # Make the GET request
                response = requests.get(url, headers=headers)

                # Check the response
                if response.status_code == 200:
                    print("Request successful:", response.json())
                    try:
                        return Response(data=response.json(), status=status.HTTP_200_OK)
                    except Exception as e:
                        print(e)
                        return Response(data={}, status=status.HTTP_200_OK)
                else:
                    print("Request failed with status code:", response.status_code)
                    print("Response:", response.text)
                    return Response(data=response.json(), status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(data={"code": "0001", "status": "Failed", "error": "Transaction not found",
                                      "message": "The reference entered matches no transaction"},
                                status=status.HTTP_200_OK)
        else:
            return Response(data={"code": "0001", "error": "Authentication error",
                                  "status": "Failed",
                                  "message": "Unable to authenticate using Authentication keys. Check and try again."},
                            status=status.HTTP_401_UNAUTHORIZED)


@api_view(["GET"])
def user_balance(request):
    response = ValidateAPIKeysView().post(request)
    data = response.data

    if data["valid"]:
        try:
            user = models.CustomUser.objects.get(api_key=request.headers.get("api-key"))
        except models.CustomUser.DoesNotExist:
            return Response(data={"code": "0001", "message": "User not found"}, status=status.HTTP_200_OK)
        user_profile = models.UserProfile.objects.get(user=user)
        print(user_profile)
        user_bundle_balance = user_profile.bundle_amount if user_profile.bundle_amount else 0
        return Response(data={"code": "0000", "user": f"{user.first_name} {user.last_name}", "bundle_balance": user_bundle_balance}, status=status.HTTP_200_OK)
    else:
        return Response(data={"code": "0001", "error": "Authentication error",
                              "status": "Failed",
                              "message": "Unable to authenticate using Authentication keys. Check and try again."},
                        status=status.HTTP_401_UNAUTHORIZED)


@api_view(["POST"])
def null_transaction_query(request):
    return Response(data={"code": "0001", "status": "Failed", "error": "Null Reference", "message": "Provide a valid reference to query"}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_all_transactions(request):
    response = ValidateAPIKeysView().post(request)
    data = response.data

    if data["valid"]:
        user = models.CustomUser.objects.get(api_key=request.headers.get("api-key"))
        user_transactions = models.NewTransaction.objects.filter(user=user).order_by('transaction_date').reverse()
        serializer = TransactionSerializer(user_transactions, many=True)
        return JsonResponse({"transactions": serializer.data})
    else:
        return Response(data={"code": "0001", "error": "Authentication error",
                              "status": "Failed",
                              "message": "Unable to authenticate using Authentication keys. Check and try again."},
                        status=status.HTTP_401_UNAUTHORIZED)