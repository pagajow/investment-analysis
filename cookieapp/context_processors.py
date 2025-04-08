from .cookiecfg import COOKIE_GROUPS, COOKIE_POLICY_VERSION

def cookie_context(request):
    cookie_groups_info = []
    cookie_acceptance_required = False
    
    consent_id = request.COOKIES.get("cookie_consent_id")
    if consent_id is None:
        cookie_acceptance_required = True
    
    policy_version = request.COOKIES.get("cookie_policy_version")
    if policy_version != COOKIE_POLICY_VERSION:
        cookie_acceptance_required = True
    
    for group in COOKIE_GROUPS:
        raw_value = request.COOKIES.get(f"cookie_{group.varname}")
        if raw_value is None:
            cookie_acceptance_required = True
        accepted = raw_value == "1" or group.is_required  # domyślnie zaakceptowane jeśli wymagane

        cookie_groups_info.append({
            "varname": group.varname,
            "full_name": group.full_name,
            "description": group.description,
            "is_required": group.is_required,
            "accepted": accepted,
            "policy_version": COOKIE_POLICY_VERSION,
        })

    return {
        "cookie_groups_info": cookie_groups_info,
        "cookie_acceptance_required": cookie_acceptance_required,
    }