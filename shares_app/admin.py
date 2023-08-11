from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models
# Register your models here.


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'first_name', 'last_name', 'email']


class AuthorizationCodesAdmin(admin.ModelAdmin):
    list_display = ['code', 'code_status']


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'business_name', 'phone', 'bundle_amount']


class CreditingHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "amount_credited"]
    search_fields = ["user"]


class NewTransactionAdmin(admin.ModelAdmin):
    list_per_page = 1000
    list_display = ["user", "receiver", "reference", "bundle_amount", "batch_id", "transaction_date", "transaction_status"]
    search_fields = ["receiver", 'reference', "bundle_amount", "batch_id"]


admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.UserProfile, UserProfileAdmin)
admin.site.register(models.AuthorizationCodes, AuthorizationCodesAdmin)
admin.site.register(models.NewTransaction, NewTransactionAdmin)
admin.site.register(models.CreditingHistory, CreditingHistoryAdmin)










