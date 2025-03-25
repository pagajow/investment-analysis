from django.core.mail import send_mail
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages

def send_verification_email(base_url, user, token):
    subject = "Confirm your email address"
    verification_url = f"{base_url}/verify-email/{token}/"
    message = f"Click the link below to confirm your email address:\n\n{verification_url}"
    send_mail(subject, message, 'noreply@mydomain.com', [user.email])
    
    

class VerifiedUserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_verified

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        else:
            messages.warning(self.request, "Your account has not been verified yet.")
            return redirect('send_verification_token')  