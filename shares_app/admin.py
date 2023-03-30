from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models
# Register your models here.


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'first_name', 'last_name', 'email']


class AuthorizationCodesAdmin(admin.ModelAdmin):
    list_display = ['code', 'code_status']


admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.UserProfile)
admin.site.register(models.TransactionHistory)
admin.site.register(models.AuthorizationCodes, AuthorizationCodesAdmin)










