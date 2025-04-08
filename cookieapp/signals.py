from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils.timezone import now

from cookieapp.utils import log_cookie_consent
from .models import CookieConsentLog
from .cookiecfg import COOKIE_GROUPS, COOKIE_POLICY_VERSION


@receiver(user_logged_in)
def save_cookie_consent_after_login(sender, request, user, **kwargs):
    consent_id = request.COOKIES.get("cookie_consent_id")
    policy_version = request.COOKIES.get("cookie_policy_version")
 
    accepted_groups = []
    for group in COOKIE_GROUPS:
        val = request.COOKIES.get(f"cookie_{group.varname}")
        if val == "1" or group.is_required:
            accepted_groups.append(group.varname)
            
    existing_log = CookieConsentLog.objects.filter(
        consent_id=consent_id,
        user__isnull=True
    ).first()
            
    if request.user.is_authenticated and existing_log:
        existing_log.user = user
        existing_log.save(update_fields=["user"])
    else:
        log_cookie_consent(
            user=request.user,
            accepted_groups=accepted_groups,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            policy_version=policy_version,
            consent_id=consent_id,
        )
