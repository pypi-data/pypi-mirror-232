from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = CustomUser
    list_display = [
        "email",
        "first_name",
        "last_name",
        "phone",
        "is_active",
        "is_admin",
    ]
    list_filter = (
        "is_active",
        "is_admin",
    )
    ordering = ("-date_joinded",)

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "address",
                    "nationality",
                    "date_of_birth",
                    "education",
                    "contact_mode",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_admin",
                    "is_active",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            "Basic Information",
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "phone",
                    "address",
                    "nationality",
                    "date_of_birth",
                    "education",
                    "contact_mode",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    search_fields = (
        "email",
        "first_name",
        "last_name",
    )
    ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
