import secrets

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from shares_app import models, helper
from shares_app.forms import CustomUserForm


# Create your views here.
@login_required(login_url='login')
def home(request):
    user_profile_data = models.UserProfile.objects.filter(user=request.user).first()
    transactions_count = models.TransactionHistory.objects.filter(user=request.user).count()
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
        print("yaya")
        receiver = request.POST.get("phone")
        amount = int(request.POST.get("amount"))

        reference = f"BPS{secrets.token_hex(3)}".upper()

        current_user = models.UserProfile.objects.filter(user=request.user).first()

        if amount > int(current_user.bundle_amount):
            messages.error(request, "Not enough bundle to send")
        elif int(current_user.bundle_amount) <= 0:
            messages.error(request, "Kindly top up", "error")
        else:
            send_bundle = helper.send_flexi_bundle(request.user, current_user, receiver, amount)
            response = send_bundle["response"]
            json_data = send_bundle["json_data"]
            batch_id = json_data["batchId"]

            if response.status_code == 200:
                current_user.bundle_amount -= amount
                current_user.save()

                new_transaction = models.TransactionHistory.objects.create(
                    user=request.user,
                    beneficiary=receiver,
                    bundle_amount=amount,
                    transaction_status="Success",
                    reference=reference,
                    batch_id=batch_id
                )
                new_transaction.save()
                print(current_user.sms_sender_name)
                receiver_message = f"Your bundle purchase has been completed successfully. {amount}MB has been credited to you.\nReference: {batch_id}\n"
                quicksend_url = "https://uellosend.com/quicksend/"
                data = {
                    'api_key': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.=eyJkYXRhIjp7InVzZXJpZCI6MTU5MiwiYXBpU2VjcmV0IjoiaFY2YjNDcHR1PW9wQnB2IiwiaXNzdWVyIjoiVUVMTE9TRU5EIn19',
                    'sender_id': current_user.sms_sender_name,
                    'message': receiver_message,
                    'recipient': receiver
                }

                headers = {'Content-type': 'application/json'}

                response = requests.post(quicksend_url, headers=headers, json=data)
                print(response.json())
                return JsonResponse({'status': "Transaction Successful", "icon": "failed"})
            else:
                new_transaction = models.TransactionHistory.objects.create(
                    user=request.user,
                    beneficiary=receiver,
                    bundle_amount=amount,
                    transaction_status="Failed",
                    reference=reference,
                    batch_id=batch_id,
                )
                new_transaction.save()
                return JsonResponse({'status': "Transaction Failed", "icon": "failed"})
    user_profile_data = models.UserProfile.objects.filter(user=request.user).first()
    context = {'data': user_profile_data}

    return render(request, 'layouts/form-layouts-vertical.html', context=context)


@login_required(login_url='login')
def transaction_history(request):
    transactions = models.TransactionHistory.objects.filter(user=request.user).order_by('transaction_date').reverse()
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
                user = models.CustomUser.objects.get(username=username)
                user.user_id = f"BPS{secrets.token_hex(3)}".upper()
                user_profile_data = models.UserProfile.objects.create(
                    user=user,
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
