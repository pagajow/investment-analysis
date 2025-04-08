from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.shortcuts import redirect

from cookieapp.utils import log_cookie_consent
from .cookiecfg import COOKIE_GROUPS, COOKIE_POLICY_VERSION
import uuid

class SetCookieView(View):
    def post(self, request, *args, **kwargs):
        return self.set_selected(request)
    
    def set_selected(self, request):
        consent_id = str(uuid.uuid4())
        
        selected = request.POST.getlist("cookies")
        response = JsonResponse({'status': 'set', 'selected': selected})
        for group in COOKIE_GROUPS:
            if group.varname in selected or group.is_required:
                response.set_cookie(f"cookie_{group.varname}", "1", max_age=31536000)
            else:
                response.set_cookie(f"cookie_{group.varname}", "-1", max_age=31536000)
        response.set_cookie("cookie_policy_version", COOKIE_POLICY_VERSION, max_age=31536000)
        response.set_cookie("cookie_consent_id", consent_id, max_age=31536000)
        
        log_cookie_consent(
            user=request.user,
            accepted_groups=selected,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            consent_id=consent_id,
        )
        
        return response

class AcceptAllCookieView(View):
    def post(self, request, *args, **kwargs):
        return self.accept_all(request)
    
    def accept_all(self, request):
        consent_id = str(uuid.uuid4())
        response = JsonResponse({'status': 'accepted_all'})
        for group in COOKIE_GROUPS:
            response.set_cookie(f"cookie_{group.varname}", "1", max_age=31536000)
        response.set_cookie("cookie_policy_version", COOKIE_POLICY_VERSION, max_age=31536000)
        response.set_cookie("cookie_consent_id", consent_id, max_age=31536000)
        
        log_cookie_consent(
            user=request.user,
            accepted_groups=[group.varname for group in COOKIE_GROUPS],
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            consent_id=consent_id,
        )
        
        return response
    
class DeclineAllCookieView(View):
    def post(self, request, *args, **kwargs):
        return self.decline_all(request)
    
    def decline_all(self, request):
        consent_id = str(uuid.uuid4())
        response = JsonResponse({'status': 'declined_all'})
        for group in COOKIE_GROUPS:
            if not group.is_required:
                response.set_cookie(f"cookie_{group.varname}", "-1", max_age=31536000)
            else:
                response.set_cookie(f"cookie_{group.varname}", "1", max_age=31536000)
        response.set_cookie("cookie_policy_version", COOKIE_POLICY_VERSION, max_age=31536000)
        response.set_cookie("cookie_consent_id", consent_id, max_age=31536000)
        
        log_cookie_consent(
            user=request.user,
            accepted_groups=[group.varname for group in COOKIE_GROUPS if group.is_required],
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            consent_id=consent_id,
        )
        
        return response

from django.views.generic import TemplateView

class CookieManageView(TemplateView):
    template_name = "cookieapp/manage.html"