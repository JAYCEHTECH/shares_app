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


class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=100, null=False, blank=False, default="Business")
    sms_sender_name = models.CharField(max_length=100, null=False, blank=False, default="Bundle")
    phone = models.PositiveIntegerField(null=True, blank=True)
    bundle_amount = models.PositiveBigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"


class TransactionHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    beneficiary = models.PositiveBigIntegerField(blank=False, null=False)
    bundle_amount = models.PositiveIntegerField(blank=False, null=False)
    reference = models.CharField(max_length=100, blank=False, null=False, default="Failed")
    batch_id = models.CharField(max_length=100, blank=False, null=False, default="Failed")
    transaction_date = models.DateTimeField(auto_now_add=True)
    transaction_status = models.CharField(max_length=100, blank=False, null=False)
    transaction_status_message = models.CharField(max_length=400, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}"


class AuthorizationCodes(models.Model):
    code = models.CharField(max_length=100, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    code_status = models.BooleanField()

    def __str__(self):
        return f"{self.code}"






