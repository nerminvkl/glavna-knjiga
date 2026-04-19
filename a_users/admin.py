from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    fieldsets = UserAdmin.fieldsets + (
        ("Extra info", {
            "fields": (
                "displayname",
                "image",
                "info",
                "company_name",
                "location",
            )
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Extra info", {
            "fields": (
                "displayname",
                "image",
                "info",
                "company_name",
                "location",
            )
        }),
    )