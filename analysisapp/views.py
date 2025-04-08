from django.shortcuts import render, redirect, get_object_or_404
from django.template import RequestContext
from django.views.generic import ListView, View,  CreateView, UpdateView, DetailView, DeleteView

from .models import AnalystUser, AssetNote, Company, FinDataA, VerificationToken, FinReport, AssetFilter
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .utils import send_verification_email, VerifiedUserRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.http import JsonResponse

import json
import markdown
import bleach
import html

import pandas as pd
from .forms import (CompanyForm, CustomPasswordResetConfirmForm, CustomPasswordResetForm, FinReportForm, RegistrationForm, 
ProfileForm, CustomLoginForm, AssetNoteForm, AssetFilterForm, CustomPasswordChangeForm)
from .financial_checks import CHECKS_CONFIG


def error(request, error: str = "Error", status: int = 400, meesage: str = ""):
    return render(request, "analysisapp/error.html",  {'error': error, 'status': status, 'message': meesage})

def safe_markdown(text):
    html = markdown.markdown(text, extensions=["extra", "fenced_code", "codehilite", "tables"])
    clean_html = bleach.clean(
        html,
        tags=[
            'p', 'b', 'i', 'strong', 'em', 'a', 'ul', 'ol', 
            'li', 'br', 'blockquote', 'code', 'pre', 'h1', 
            'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'hr'
        ],
        attributes={'a': ['href', 'title'], 'img': ['src', 'alt', 'title']},
        protocols=['http', 'https', 'mailto'],
        strip=True
    )
    return clean_html

class HomeView(View):
    template_name = 'analysisapp/home.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        
        if user.is_authenticated:
            favorite_companies = Company.objects.filter(user=user, favorite=True).order_by("name")
            favorite_notes = AssetNote.objects.filter(company__user=user, favorite=True).order_by("title")
            context = {
                "is_user": True,
                "is_openai_api_key": bool(user.openai_api_key),
                "is_google_api_key": bool(user.google_api_key),
                "is_google_cse_id": bool(user.google_cse_id),
                "favorite_companies": favorite_companies,
                "favorite_notes": favorite_notes,
            }
        else:
            context = {
                "is_user": False,
                "is_openai_api_key": False,
                "is_google_api_key": False,
                "is_google_cse_id": False,
            }

        return render(request, self.template_name, context)

class AboutView(View):
    template_name = 'analysisapp/about.html'
    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {})

class CustomLoginView(LoginView):
    authentication_form = CustomLoginForm  
    template_name = 'analysisapp/registration/login.html'  
    
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm 
    template_name = 'analysisapp/registration/password_reset_form.html'
    email_template_name = 'analysisapp/registration/password_reset_email.html'
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = CustomPasswordResetConfirmForm
    template_name = 'analysisapp/registration/password_reset_confirm.html'



class AnalystUserRegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'analysisapp/registration/register.html'
    success_url = reverse_lazy('login')


class SendVerificationTokenView(View):
    def get_base_url(self, request) -> str:
        scheme = request.scheme
        host = request.get_host()
        return f"{scheme}://{host}"

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and not user.is_verified:
            token, created = VerificationToken.objects.get_or_create(user=user)
            send_verification_email(
                base_url=self.get_base_url(request),
                user=user,
                token=token.token
            )  # Send email with the token
            messages.success(
                request, "Verification link has been sent to your email address.")
        else:
            messages.warning(request, "Your account is already verified.")
        return redirect('home')


class VerifyTokenView(View):
    def get(self, request, token, *args, **kwargs):
        try:
            verification_token = VerificationToken.objects.get(token=token)
            user = verification_token.user
            user.is_verified = True
            user.save()
            verification_token.delete()  # Delete the token after confirmation
            messages.success(
                request, "Your email address has been verified. You can now log in.")
        except VerificationToken.DoesNotExist:
            messages.error(request, "Invalid or expired token.")
        return redirect('login')


class AnalystUserProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'analysisapp/registration/profile.html'
    success_url = reverse_lazy('company_list')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    form_class = CustomPasswordChangeForm
    template_name = 'analysisapp/registration/change_password.html'
    success_url = reverse_lazy('profile')  


class AnalystUserDeleteView(LoginRequiredMixin, DeleteView):
    model = AnalystUser
    template_name = 'analysisapp/registration/user_confirm_delete.html'
    success_url = reverse_lazy('home')
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        user = self.get_object()
        logout(self.request)
        user.delete()
        return redirect(self.success_url)


class CompanyListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'analysisapp/companies/company_list.html'  
    context_object_name = 'companies'

    def get_queryset(self):
        if not self.request.user.is_authenticated or not self.request.user.is_verified:
            return Company.objects.none()
        return Company.objects.filter(user=self.request.user)


class NewCompanyView(LoginRequiredMixin, CreateView):
    model = Company
    template_name = 'analysisapp/companies/company_form.html'
    form_class = CompanyForm
    success_url = reverse_lazy('company_list')

    def form_valid(self, form):
        form.instance.user = self.request.user  
        return super().form_valid(form)


class EditCompanyView(LoginRequiredMixin, UpdateView):
    model = Company
    template_name = 'analysisapp/companies/company_form.html'
    form_class = CompanyForm
    success_url = reverse_lazy('company_list')

    def get_object(self, queryset=None):
        company_id = self.kwargs.get("company_id")
        return get_object_or_404(Company, id=company_id, user=self.request.user)


class DeleteCompanyView(LoginRequiredMixin, DeleteView):
    model = Company
    template_name = 'analysisapp/companies/company_confirm_delete.html'  
    context_object_name = 'company'

    def get_object(self, queryset=None):
        company_id = self.kwargs.get('company_id')
        return get_object_or_404(Company, id=company_id, user=self.request.user)

    def get_success_url(self):
        return reverse_lazy('company_list')


class FinancialDataView(LoginRequiredMixin, ListView):
    model = FinDataA
    template_name = 'analysisapp/financial_data.html'
    context_object_name = 'financial_data'

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return FinDataA.objects.filter(company__id=company_id, company__user=self.request.user).order_by('year')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(id=self.kwargs['company_id'], user=self.request.user)
        context['fields'] = [field.name for field in FinDataA._meta.fields if field.name != 'company']
        return context


class FinancialDataEditView(LoginRequiredMixin, ListView):
    model = FinDataA
    template_name = 'analysisapp/edit_financial_data_list.html'  # Użyj właściwej ścieżki
    context_object_name = 'financial_data'

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return FinDataA.objects.filter(company__id=company_id, company__user=self.request.user).order_by('year')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(
            id=self.kwargs['company_id'], user=self.request.user)
        context['fields'] = [
            field.name for field in FinDataA._meta.fields if field.name != 'company']
        return context


class UploadFileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        company_id = kwargs.get('company_id')
        company = get_object_or_404(
            Company, id=company_id, user=self.request.user)

        if not request.FILES.get('file'):
            return error(request, 'No file uploaded.')

        uploaded_file = request.FILES['file']
        if not uploaded_file.name.endswith('.csv'):
            return error(request, 'Invalid file type. Only CSV files are allowed.')

        try:
            df = pd.read_csv(uploaded_file)
            df = df.fillna("")

            data = df.to_dict(orient='records')
            columns = list(df.columns)

            request.session['csv_data'] = {'columns': columns, 'data': data}

            return redirect('process-financial-data', company_id=company_id)
        except Exception as e:
            return error(request, error="Data cannot be read as a table.", status=400, meesage=str(e))


class ProcessFileView(LoginRequiredMixin, View):
    template_name = 'analysisapp/proscess_financial_data.html'

    def get(self, request, *args, **kwargs):
        company_id = kwargs.get('company_id')
        company = get_object_or_404(
            Company, id=company_id, user=self.request.user)

        csv_data = request.session.get('csv_data')
        if not csv_data:
            return redirect('financial_data', company_id=company_id)

        columns = csv_data['columns']
        data = csv_data['data']

        fields = [field.name for field in FinDataA._meta.get_fields() if field.name not in [
            'company', 'id']]

        return render(request, self.template_name, {
            'company': company,
            'columns': columns,
            'fields': fields,
            'data': data,
        })


class AssetNoteListView(LoginRequiredMixin, ListView):
    model = AssetNote
    template_name = 'analysisapp/notes/assetnote_list.html'
    context_object_name = 'notes'

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return AssetNote.objects.filter(company_id=company_id).order_by('-created')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        company_id = self.kwargs['company_id']
        company = get_object_or_404(
            Company, id=company_id, user=self.request.user)
        context['company'] = company  
        return context


class AssetNoteDetailView(LoginRequiredMixin, DetailView):
    model = AssetNote
    template_name = 'analysisapp/notes/assetnote_detail.html'
    context_object_name = 'note'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rendered_markdown"] = safe_markdown(self.object.content)
        return context


class AssetNoteCreateView(LoginRequiredMixin, CreateView):
    model = AssetNote
    form_class = AssetNoteForm
    template_name = 'analysisapp/notes/assetnote_form.html'

    def form_valid(self, form):
        company = get_object_or_404(Company, pk=self.kwargs['company_id'])
        form.instance.company = company
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('assetnote_list', kwargs={'company_id': self.kwargs['company_id']})


class AssetNoteUpdateView(LoginRequiredMixin, UpdateView):
    model = AssetNote
    form_class = AssetNoteForm
    template_name = 'analysisapp/notes/assetnote_form.html'

    def get_success_url(self):
        return reverse_lazy('assetnote_list', kwargs={'company_id': self.kwargs['company_id']})

class AssetNoteDeleteView(LoginRequiredMixin, DeleteView):
    model = AssetNote
    template_name = 'analysisapp/notes/assetnote_confirm_delete.html'
    context_object_name = 'note'
    
    def get_success_url(self):
        company_id = self.kwargs['company_id']
        return reverse_lazy('assetnote_list', kwargs={'company_id': company_id})
    
    
    

class FinReportListView(LoginRequiredMixin, ListView):
    model = FinReport
    template_name = 'analysisapp/reports/finreport_list.html'
    context_object_name = 'reports'

    def get_queryset(self):
        user = self.request.user
        return FinReport.objects.filter(user=user).order_by('-created')
    
class FinReportCreateView(LoginRequiredMixin, CreateView):
    model = FinReport
    form_class = FinReportForm
    template_name = 'analysisapp/reports/finreport_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('finreports_list', kwargs={})


class FinReportUpdateView(LoginRequiredMixin, UpdateView):
    model = FinReport
    form_class = FinReportForm
    template_name = 'analysisapp/reports/finreport_form.html'

    def get_success_url(self):
        return reverse_lazy('finreports_list', kwargs={})


class FinReportDetailView(LoginRequiredMixin, DetailView):
    model = FinReport
    template_name = 'analysisapp/reports/finreport_detail.html'
    context_object_name = 'report'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["rendered_markdown"] = safe_markdown(self.object.content)
        
        return context


class FinReportDeleteView(LoginRequiredMixin, DeleteView):
    model = FinReport
    template_name = 'analysisapp/reports/finreport_confirm_delete.html'
    context_object_name = 'report'
    
    def get_success_url(self):
        return reverse_lazy('finreports_list', kwargs={})
    
class AssetFilterListView(LoginRequiredMixin, ListView):
    model = AssetFilter
    template_name = 'analysisapp/filters/assetfilter_list.html'
    context_object_name = 'filters'

    def get_queryset(self):
        return AssetFilter.objects.filter(user=self.request.user).order_by('-weight')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["config"] = json.dumps(CHECKS_CONFIG)  # Przekazujemy konfigurację do szablonu
        return context

class AssetFilterCreateView(LoginRequiredMixin, CreateView):
    model = AssetFilter
    form_class = AssetFilterForm
    template_name = 'analysisapp/filters/assetfilter_form.html'
    success_url = reverse_lazy('filter_list')

    def form_valid(self, form):
        form.instance.user = self.request.user  # Ustawiamy użytkownika jako właściciela filtra
        return super().form_valid(form)
    
class AssetFilterUpdateView(LoginRequiredMixin, UpdateView):
    model = AssetFilter
    form_class = AssetFilterForm
    template_name = 'analysisapp/filters/assetfilter_form.html'
    success_url = reverse_lazy('filter_list')

    def get_queryset(self):
        return AssetFilter.objects.filter(user=self.request.user)  # Zapewniamy, że użytkownik może edytować tylko swoje filtry

class AssetFilterDeleteView(LoginRequiredMixin, DeleteView):
    model = AssetFilter
    template_name = 'analysisapp/filters/assetfilter_confirm_delete.html'
    success_url = reverse_lazy('filter_list')

    def get_queryset(self):
        return AssetFilter.objects.filter(user=self.request.user)  # Zapewniamy, że użytkownik usuwa tylko swoje filtry
