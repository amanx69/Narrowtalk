# admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = ("email", "is_staff", "is_active", "is_verify", "created_at")
    list_filter = ("is_staff", "is_active", "is_verify", "created_at")
    search_fields = ("email",)
    ordering = ("-created_at",)   
    readonly_fields = ("id", "created_at")

   
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_verify", "is_superuser", "groups", "user_permissions"),
        }),
        (_("Important dates"), {"fields": ("last_login", "created_at")}),
    )

  
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active"),
        }),
    )

    filter_horizontal = ("groups", "user_permissions")