from django.utils.timezone import now
from .models import CookieConsentLog
from .cookiecfg import COOKIE_POLICY_VERSION

def log_cookie_consent(user, accepted_groups, ip_address, user_agent, policy_version=None, consent_id=None):
    user = user if user.is_authenticated else None
    if not consent_id:
        return  
    
    if CookieConsentLog.objects.filter(user=user, consent_id=consent_id).exists():
        return
    
    CookieConsentLog.objects.create(
        user=user,
        accepted_groups=accepted_groups,
        ip_address=ip_address,
        user_agent=user_agent or "",
        policy_version=policy_version or COOKIE_POLICY_VERSION,
        timestamp=now(),
        consent_id=consent_id,
    )