from django import forms
from django.contrib.auth.forms import UserCreationForm

from shares_app.models import CustomUser


class CustomUserForm(UserCreationForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'name', 'placeholder': 'Enter your first name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'name', 'placeholder': 'Enter your last name'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username', 'placeholder': 'Enter your username'}))
    business_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'business', 'placeholder': 'Enter your business name'}))
    email = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'email', 'placeholder': 'Enter your email'}))
    phone = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control', 'id': 'phone', 'placeholder': 'Enter your phone number'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password', 'placeholder': '&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password', 'placeholder': '&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;&#xb7;'}))

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'business_name', 'email', 'phone', 'password1', 'password2']



