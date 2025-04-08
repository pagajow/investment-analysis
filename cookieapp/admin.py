from django.contrib import admin
from .models import CookieConsentLog


@admin.register(CookieConsentLog)
class CookieConsentLogAdmin(admin.ModelAdmin):
    list_display = (
        "user_display",
        "consent_id",
        "timestamp",
        "policy_version",
        "ip_address",
        "accepted_groups_list",
    )
    list_filter = ("policy_version", "timestamp", "consent_id")
    search_fields = ("user__username", "ip_address", "accepted_groups", "consent_id")
    ordering = ("-timestamp",)

    def user_display(self, obj):
        return obj.user.username if obj.user else "Anonymous"
    user_display.short_description = "User"

    def accepted_groups_list(self, obj):
        return ", ".join(obj.accepted_groups or [])
    accepted_groups_list.short_description = "Accepted Cookies"
