from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Follow, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "id",
        "email",
        "first_name",
        "last_name",
    )
    list_filter = ("email", "username")


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "author",
    )
