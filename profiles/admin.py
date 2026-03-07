from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("profile_id", "full_name", "contact_number", "company_name", "updated_at")
    search_fields = ("profile_id", "full_name", "contact_number", "email")