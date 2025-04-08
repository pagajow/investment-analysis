from django.db import models
from django.conf import settings


class CookieConsentLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        help_text="Logged-in user, if available."
    )
    consent_id = models.CharField(
        max_length=64,
        help_text="Unique identifier for consent (e.g., UUID stored in a cookie)."
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    accepted_groups = models.JSONField(
        help_text="List of accepted cookie groups (e.g., ['essential', 'analytics'])"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    policy_version = models.CharField(
        max_length=20,
        default="1.0",
        help_text="Version of the privacy or cookie policy"
    )
    

    def __str__(self):
        if self.user:
            return f"Consent by {self.user.username} at {self.timestamp}"
        return f"Anonymous consent at {self.timestamp}"
