from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View,  CreateView, UpdateView
from .models import Company, FinDataA, AnalystUser
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

import pandas as pd
from .forms import CompanyForm, RegistrationForm


def error(request, error:str="Error", status:int=400, meesage:str=""):
    return render(request, "analysisapp/error.html",  {'error': error, 'status': status, 'message': meesage})


class AnalystUserRegisterView(CreateView):
    form_class = RegistrationForm
    template_name = 'analysisapp/registration/register.html'
    success_url = reverse_lazy('login')


class CompanyListView(ListView):
    model = Company
    template_name = 'analysisapp/company_list.html'  # Nazwa szablonu
    context_object_name = 'companies'  
    
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Company.objects.none() 
        return Company.objects.filter(user=self.request.user)
    

class NewCompanyView(LoginRequiredMixin, CreateView):
    model = Company
    template_name = 'analysisapp/new_company.html'
    form_class = CompanyForm 
    success_url = reverse_lazy('company_list') 
    
    def form_valid(self, form):
        form.instance.user = self.request.user  # Przypisanie użytkownika
        return super().form_valid(form)

class EditCompanyView(LoginRequiredMixin, UpdateView):
    model = Company
    template_name = 'analysisapp/edit_company.html'
    form_class = CompanyForm 
    success_url = reverse_lazy('company_list') 
    
    def get_object(self, queryset=None):
        company_id = self.kwargs.get("company_id")
        return get_object_or_404(Company, id=company_id, user=self.request.user)
    

class FinancialDataListView(LoginRequiredMixin, ListView):
    model = FinDataA
    template_name = 'analysisapp/financial_data_list.html'  # Użyj właściwej ścieżki
    context_object_name = 'financial_data'

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return FinDataA.objects.filter(company__id=company_id, company__user=self.request.user).order_by('year')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(id=self.kwargs['company_id'], user=self.request.user)
        context['fields'] = [field.name for field in FinDataA._meta.fields if field.name != 'company']
        return context

class FinancialDataListEditView(LoginRequiredMixin, ListView):
    model = FinDataA
    template_name = 'analysisapp/edit_financial_data_list.html'  # Użyj właściwej ścieżki
    context_object_name = 'financial_data'

    def get_queryset(self):
        company_id = self.kwargs['company_id']
        return FinDataA.objects.filter(company__id=company_id, company__user=self.request.user).order_by('year')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = Company.objects.get(id=self.kwargs['company_id'], user=self.request.user)
        context['fields'] = [field.name for field in FinDataA._meta.fields if field.name != 'company']
        return context

class UploadFileView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        company_id = kwargs.get('company_id')  
        company = get_object_or_404(Company, id=company_id, user=self.request.user)
        
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
            return error(request, error="Data cannot be read as a table.", status=400 ,meesage=str(e))



class ProcessFileView(LoginRequiredMixin, View):
    template_name = 'analysisapp/proscess_financial_data.html'
    
    def get(self, request, *args, **kwargs):
        company_id = kwargs.get('company_id')
        company = get_object_or_404(Company, id=company_id, user=self.request.user)

        csv_data = request.session.get('csv_data')
        if not csv_data:
            return redirect('financial_data_list', company_id=company_id)

        columns = csv_data['columns']
        data = csv_data['data']

        fields = [field.name for field in FinDataA._meta.get_fields() if field.name not in ['company', 'id']]
        
        return render(request, self.template_name, {
            'company': company,
            'columns': columns,
            'fields': fields,
            'data': data,
        })