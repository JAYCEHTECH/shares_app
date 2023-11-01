import secrets

import requests
from decouple import config

from .api import api_views
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy
from rest_framework.authtoken.models import Token

from shares_app import models, helper, forms
from shares_app.forms import CustomUserForm


# Create your views here.
@login_required(login_url='login')
def home(request):
    user_profile_data = models.UserProfile.objects.filter(user=request.user).first()
    transactions_count = models.NewTransaction.objects.filter(user=request.user).count()
    context = {'data': user_profile_data, 'count': transactions_count}
    return render(request, 'layouts/index.html', context=context)


@login_required(login_url='login')
def user_profile(request):
    if request.method == "POST":
        business_name = request.POST.get("business")
        phone = request.POST.get("phoneNumber")
        sms_name = request.POST.get("smsName")

        updated_user = models.UserProfile.objects.filter(user=request.user).first()
        updated_user.business_name = business_name
        updated_user.phone = phone
        updated_user.sms_sender_name = sms_name

        updated_user.save()
        messages.success(request, "Profile Updated Successfully")
    user_profile_details = models.UserProfile.objects.filter(user=request.user).first()
    context = {'data': user_profile_details}
    return render(request, 'layouts/user_profile.html', context=context)


@login_required(login_url='login')
def send_bundle_page(request):
    if request.method == "POST":
        receiver = request.POST.get("phone")
        amount = int(request.POST.get("amount"))

        reference = f"{request.user.username}-{secrets.token_hex(3)}".upper()
        print(receiver)
        print(amount)

        current_user = models.UserProfile.objects.filter(user=request.user).first()

        if amount > int(current_user.bundle_amount):
            print("small")
            return JsonResponse(
                {"status": "You do not have enough balance to perform this transaction", "icon": "info"})
        else:
            print("moving on to send")
            response = helper.send_flexi_bundle(request, request.user, current_user, receiver, amount, reference, "new")
            data = response.data
            print(data)
            message = data["message"]
            if data["status"] == "Success":
                new_current_user = models.UserProfile.objects.filter(user=request.user).first()
                receiver_message = f"Transaction was completed successfully.\nReference: {reference}\nReceiver:{receiver}\nAmount: {amount}MB\nCurrent Balance:{new_current_user.bundle_amount}MB"
                quicksend_url = "https://uellosend.com/quicksend/"
                data = {
                    'api_key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.=eyJkYXRhIjp7InVzZXJpZCI6MTU5MiwiYXBpU2VjcmV0IjoiaFY2YjNDcHR1PW9wQnB2IiwiaXNzdWVyIjoiVUVMTE9TRU5EIn19',
                    'sender_id': "BESTPAY GH",
                    'message': receiver_message,
                    'recipient': f"0{current_user.phone}"
                }

                headers = {'Content-type': 'application/json'}

                response = requests.post(quicksend_url, headers=headers, json=data)
                print(response.json())
                return JsonResponse({'status': message, "icon": "success"})
            else:
                return JsonResponse({'status': message, "icon": "error"})
    #         response = send_bundle["response"]
    #         json_data = send_bundle["json_data"]
    #         batch_id = json_data["batchId"]
    #
    #         if response.status_code == 200:
    #             current_user.bundle_amount -= amount
    #             current_user.save()
    #
    #             new_transaction = models.TransactionHistory.objects.create(
    #                 user=request.user,
    #                 beneficiary=receiver,
    #                 bundle_amount=amount,
    #                 transaction_status="Success",
    #                 reference=reference,
    #                 batch_id=batch_id
    #             )
    #             new_transaction.save()
    #             print(current_user.sms_sender_name)
    #             receiver_message = f"Your bundle purchase has been completed successfully. {amount}MB has been credited to you.\nReference: {batch_id}\n"
    #             quicksend_url = "https://uellosend.com/quicksend/"
    #             data = {
    #                 'api_key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.=eyJkYXRhIjp7InVzZXJpZCI6MTU5MiwiYXBpU2VjcmV0IjoiaFY2YjNDcHR1PW9wQnB2IiwiaXNzdWVyIjoiVUVMTE9TRU5EIn19',
    #                 'sender_id': current_user.sms_sender_name,
    #                 'message': receiver_message,
    #                 'recipient': receiver
    #             }
    #
    #             headers = {'Content-type': 'application/json'}
    #
    #             response = requests.post(quicksend_url, headers=headers, json=data)
    #             print(response.json())
    #             return JsonResponse({'status': "Transaction Successful", "icon": "failed"})
    #         else:
    #             new_transaction = models.TransactionHistory.objects.create(
    #                 user=request.user,
    #                 beneficiary=receiver,
    #                 bundle_amount=amount,
    #                 transaction_status="Failed",
    #                 reference=reference,
    #                 batch_id=batch_id,
    #             )
    #             new_transaction.save()
    #
    user_profile_data = models.UserProfile.objects.filter(user=request.user).first()
    context = {'data': user_profile_data}

    return render(request, 'layouts/form-layouts-vertical.html', context=context)


@login_required(login_url='login')
def transaction_history(request):
    transactions = models.NewTransaction.objects.filter(user=request.user).order_by('transaction_date').reverse()
    user_profile_data = models.UserProfile.objects.filter(user=request.user).first()
    context = {'txns': transactions, 'data': user_profile_data}
    return render(request, 'layouts/txn-tables.html', context=context)


def register(request):
    form = CustomUserForm()
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            code = request.POST.get("code")
            code_needed = models.AuthorizationCodes.objects.filter(code=code, code_status=False).first()
            if code_needed:
                code_needed.code_status = True
                code_needed.save()
                form.save()
                username = form.cleaned_data.get("username")
                phone_number = form.cleaned_data.get("phone")
                business_name = form.cleaned_data.get("business_name")
                user = models.CustomUser.objects.get(username=username)
                user.user_id = f"BPS{secrets.token_hex(3)}".upper()
                user_profile_data = models.UserProfile.objects.create(
                    user=user,
                    phone=phone_number,
                    business_name=business_name,
                    bundle_amount=0
                )
                user.save()
                user_profile_data.save()
                messages.success(request, "Sign Up Successful. Log in to continue.")
                return redirect('login')
            else:
                messages.error(request, "Invalid Authorisation Code")
    context = {'form': form}
    return render(request, 'auth/auth-register-basic.html', context=context)


def loginpage(request):
    if request.user.is_authenticated:
        messages.warning(request, "You are already logged in")
        return redirect('home')
    else:
        if request.method == 'POST':
            name = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=name, password=password)
            if user:
                login(request, user)
                messages.success(request, 'Log in Successful')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
                return redirect('login')
    return render(request, "auth/auth-login-basic.html")


@login_required(login_url='login')
def logout_user(request):
    logout(request)
    messages.success(request, "Log out successful")


def display_name(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        name = helper.display_name(phone)

        return JsonResponse({'status': f"{name}"})


@login_required(login_url='login')
def api_page(request):
    if request.method == 'POST':
        response = api_views.APIKeysView().post(request).data
        print(response)
        return redirect("api_mgt")
        # if user_token:
        #     print("yhp, user token")
        #     print(user_token)
        #     header = {
        #         "Authorization": f"Token {user_token}"
        #     }
        #     response = requests.post(url="https://console.bestpaygh.com/api_keys/", headers=header)
        #     print("response needed")
        #     print(response.json())
        #     return redirect("api_mgt")
        # else:
        #     user_token = Token.objects.create(user=request.user)
        #     header = {
        #         "Authorization": f"Token {user_token}"
        #     }
        #     print(header)
        #     response = requests.post(url="https://console.bestpaygh.com/api_keys/", headers=header)
        #     print(response.status_code)
        #     print(response.json())
        #     return redirect('api_mgt')

    try:
        user_token = Token.objects.get(user=request.user)
    except:
        user_token = Token.objects.create(user=request.user)
    print(user_token)
    user_profile_data = models.CustomUser.objects.get(id=request.user.id)
    # api = user_profile_data.api_key
    # secret = user_profile_data.api_secret
    # print(api)
    # print(secret)
    # print(user_profile_data.username)
    # url = "https://console.bestpaygh.com/api_keys/"
    # print(url)
    # payload = {}
    # headers = {
    #     'Authorization': f'Token {user_token}'
    # }
    # print(headers)
    response = api_views.APIKeysView().get(request).data
    print(response)
    data = response
    api = data["api_key"]
    secret = data["api_secret"]
    print(api)
    print(secret)
    context = {'data': user_profile_data, "api": api, "secret": secret}
    return render(request, "layouts/api_page.html", context=context)


@login_required(login_url='login')
def crediting_page(request):
    form = forms.CreditingForm()
    if request.user.is_staff:
        if request.method == "POST":
            form = forms.CreditingForm(request.POST)
            user = form["user"]
            amount = form["credit_amount"]
            user_credited = models.CustomUser.objects.get(id=user.value())
            print(user_credited.username)
            user_profile_credited = models.UserProfile.objects.get(user=user.value())
            previous_balance = user_profile_credited.bundle_amount
            user_profile_credited.bundle_amount += float(amount.value())
            user_profile_credited.save()
            new_credit = models.CreditingHistory(user=user_credited, amount_credited=amount.value())
            new_credit.save()
            receiver_message = f"Your BestPay console account has been successfully credited with {amount.value()}MB.\nPrev Balance: {previous_balance}MB\nNew Balance:{user_profile_credited.bundle_amount}MB"
            quicksend_url = "https://uellosend.com/quicksend/"
            data = {
                'api_key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.=eyJkYXRhIjp7InVzZXJpZCI6MTU5MiwiYXBpU2VjcmV0IjoiaFY2YjNDcHR1PW9wQnB2IiwiaXNzdWVyIjoiVUVMTE9TRU5EIn19',
                'sender_id': "BESTPAY GH",
                'message': receiver_message,
                'recipient': f"0{user_profile_credited.phone}"
            }

            headers = {'Content-type': 'application/json'}

            response = requests.post(quicksend_url, headers=headers, json=data)
            print(response.json())
            messages.success(request,
                             f"{user_credited.username}'s account credited successfully with {amount.value()}MB")
            return redirect("crediting")
        context = {"form": form}
        return render(request, "layouts/crediting_page.html", context=context)
    else:
        reverse_lazy('home')


@login_required(login_url='login')
def credit_history(request):
    credits_txn = models.CreditingHistory.objects.filter(user=request.user).order_by('date').reverse()
    user_profile_data = models.UserProfile.objects.filter(user=request.user).first()
    context = {'credits': credits_txn, 'data': user_profile_data}
    return render(request, 'layouts/credit-tables.html', context=context)


@login_required(login_url='login')
def query_transaction(request):
    if request.method == "POST":
        reference = request.POST.get("ref")

        user = models.CustomUser.objects.get(id=request.user.id)
        print(user.username)
        headers = {
            "api-key": user.api_key,
            "api-secret": user.api_secret
        }
        # response = requests.get(url=f"https://console.bestpaygh.com/flexi/v1/transaction_detail/{reference.strip()}/", headers=headers)
        # data = response.json()
        # print(data)
        response = api_views.TransactionDetail().post(request, reference.strip()).data
        print("query response")
        print(response)
        if response["code"] == "0000":
            messages.info(request,
                          f"Message: {response['api_response']['message']} - {response['api_response']['recipient']} - {response['api_response']['shared_bundle']}MB")
        else:
            messages.info(request, f"Message: {response['message']}")
        return redirect("query_transaction")
    return render(request, "layouts/query-txn.html")


@login_required(login_url='login')
def all_transactions(request):
    all_users_transactions = models.NewTransaction.objects.all().order_by("transaction_date").reverse()
    context = {"txns": all_users_transactions}
    return render(request, "layouts/admin-all-txns.html", context=context)


@login_required(login_url='login')
def fix_transaction(request, ref):
    current_user = models.UserProfile.objects.filter(user=request.user).first()
    transaction_referenced = models.NewTransaction.objects.filter(reference=ref).first()
    number = transaction_referenced.receiver
    batch_id = transaction_referenced.batch_id

    print(number)
    print(batch_id)

    if batch_id == "Failed":
        print("moving on to send")
        response = helper.send_flexi_bundle(request, request.user, current_user, number,
                                            transaction_referenced.bundle_amount, ref, "fixing")
        data = response.data
        print(data)
        message = data["message"]
        if data["status"] == "Success":
            new_current_user = models.UserProfile.objects.filter(user=request.user).first()
            receiver_message = f"Transaction was completed successfully.\nReference: {ref}\nReceiver:{number}\nAmount: {transaction_referenced.bundle_amount}MB\nCurrent Balance:{new_current_user.bundle_amount}MB"
            quicksend_url = "https://uellosend.com/quicksend/"
            data = {
                'api_key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.=eyJkYXRhIjp7InVzZXJpZCI6MTU5MiwiYXBpU2VjcmV0IjoiaFY2YjNDcHR1PW9wQnB2IiwiaXNzdWVyIjoiVUVMTE9TRU5EIn19',
                'sender_id': "BESTPAY GH",
                'message': receiver_message,
                'recipient': f"0{current_user.phone}"
            }

            headers = {'Content-type': 'application/json'}

            response = requests.post(quicksend_url, headers=headers, json=data)
            print(response.json())
            messages.success(request, message=message)
            return redirect("txn_history")
        else:
            messages.error(request, message)
            return redirect("txn_history")

    url = f"https://backend.boldassure.net:445/live/api/context/business/airteltigo-gh/ishare/tranx-status/{batch_id}"

    payload = {}
    headers = {
        'Authorization': config("BEARER_TOKEN")
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()
    print(data)
    api_message = data["flexiIshareTranxStatus"]["flexiIshareTranxStatusResult"]["apiResponse"]["responseMsg"]
    ishare_response = \
        data["flexiIshareTranxStatus"]["flexiIshareTranxStatusResult"]["ishareApiResponseData"]["apiResponseData"][
            0][
            "responseMsg"]
    ishare_response_code = \
        data["flexiIshareTranxStatus"]["flexiIshareTranxStatusResult"]["ishareApiResponseData"]["apiResponseData"][
            0][
            "responseCode"]
    print(ishare_response)
    print(api_message)

    if ishare_response == "Crediting Successful.":
        messages.success(request, "Transaction was successful")
    elif api_message == "Transaction Failed" and ishare_response_code == "306":
        messages.error(request, ishare_response)
        return redirect("txn_history")
    elif api_message == "Transaction Failed" and ishare_response_code == "311":
        messages.error(request, ishare_response)
        return redirect("txn_history")
    elif api_message == "Transaction Failed":
        print("moving on to send")
        response = helper.send_flexi_bundle(request, request.user, current_user, number,
                                            transaction_referenced.bundle_amount, ref, "fixing")
        data = response.data
        print(data)
        message = data["message"]
        if data["status"] == "Success":
            new_current_user = models.UserProfile.objects.filter(user=request.user).first()
            receiver_message = f"Transaction was completed successfully.\nReference: {ref}\nReceiver:{number}\nAmount: {transaction_referenced.bundle_amount}MB\nCurrent Balance:{new_current_user.bundle_amount}MB"
            quicksend_url = "https://uellosend.com/quicksend/"
            data = {
                'api_key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.=eyJkYXRhIjp7InVzZXJpZCI6MTU5MiwiYXBpU2VjcmV0IjoiaFY2YjNDcHR1PW9wQnB2IiwiaXNzdWVyIjoiVUVMTE9TRU5EIn19',
                'sender_id': "BESTPAY GH",
                'message': receiver_message,
                'recipient': f"0{current_user.phone}"
            }

            headers = {'Content-type': 'application/json'}

            response = requests.post(quicksend_url, headers=headers, json=data)
            print(response.json())
            messages.success(request, f"{message}. {ishare_response}")
            return redirect("txn_history")
        else:
            messages.error(request, message)
            return redirect("txn_history")
    else:
        messages.success(request, api_message)
        return redirect("txn_history")
    return redirect('txn_history')
