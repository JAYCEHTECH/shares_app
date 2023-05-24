from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    user_id = models.CharField(max_length=100, null=False, blank=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    username = models.CharField(max_length=100, null=False, blank=False, unique=True)
    email = models.EmailField(max_length=250, null=False, blank=False)
    password1 = models.CharField(max_length=100, null=False, blank=False)
    password2 = models.CharField(max_length=100, null=False, blank=False)
    api_key = models.CharField(max_length=120, blank=True, null=True)
    api_secret = models.CharField(max_length=140, blank=True, null=True)
    api_revoked = models.BooleanField(default=False)

    def has_valid_api_secret(self, secret_key: str) -> bool:
        return self.api_secret == secret_key

    def __str__(self):
        return self.username


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100, null=False, blank=False, default="Business")
    sms_sender_name = models.CharField(max_length=100, null=False, blank=False, default="Bundle")
    phone = models.PositiveIntegerField(null=True, blank=True)
    bundle_amount = models.PositiveBigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"


class NewTransaction(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=200, blank=False, null=False)
    first_name = models.CharField(max_length=200, blank=False, null=False)
    last_name = models.CharField(max_length=200, blank=False, null=False)
    account_email = models.EmailField(max_length=200, blank=False, null=False)
    receiver = models.CharField(max_length=200, blank=False, null=False)
    reference = models.CharField(max_length=100, blank=False, null=False, default="Failed")
    bundle_amount = models.FloatField(blank=False, null=False)
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_status = models.CharField(max_length=100, blank=False, null=False, default="Failed")
    batch_id = models.CharField(max_length=100, blank=False, null=False, default="Failed")

    def __str__(self):
        return self.first_name + " " + self.receiver


class CreditingHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount_credited = models.FloatField(null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " " + str(self.amount_credited)


class AuthorizationCodes(models.Model):
    code = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    code_status = models.BooleanField()

    def __str__(self):
        return f"{self.code}"






