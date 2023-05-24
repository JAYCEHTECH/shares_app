from rest_framework.serializers import ModelSerializer
from .models import CustomUser, NewTransaction


class UserSerializer(ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'username', 'api_key', 'api_secret']


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = NewTransaction
        fields = ["id", 'first_name', 'last_name', 'account_number', 'account_email', 'receiver', 'reference', 'bundle_amount', 'transaction_date', 'transaction_status']
