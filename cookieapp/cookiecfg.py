from dataclasses import dataclass

@dataclass
class CookieGroup:
    varname: str         
    full_name: str       
    is_required: bool    
    description: str     

# Default cookie groups

COOKIE_POLICY_VERSION = "1.0"

COOKIE_GROUPS = [
    CookieGroup(
        varname="essential",
        full_name="Essential cookies",
        is_required=True,
        description="These cookies are required for the website to function properly."
    ),
    CookieGroup(
        varname="analytics",
        full_name="Analytics cookies",
        is_required=False,
        description="They help us analyze website traffic."
    ),
    CookieGroup(
        varname="marketing",
        full_name="Marketing cookies",
        is_required=False,
        description="They allow us to personalize advertisements."
    ),
]
