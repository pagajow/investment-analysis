from django.urls import path
from .views import (CompanyListView, FinancialDataListView, FinancialDataListEditView, NewCompanyView, 
                    EditCompanyView, UploadFileView, ProcessFileView, AnalystUserRegisterView)
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', CompanyListView.as_view(), name='company_list'),  # Strona główna z listą firm,
    path('login/', LoginView.as_view(template_name='analysisapp/registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', AnalystUserRegisterView.as_view(), name='register'),
    path('new-company/', NewCompanyView.as_view(), name='new_company'),  
    path('edit-company/<int:company_id>/', EditCompanyView.as_view(), name='edit_company'),  
    path('company/<int:company_id>/financial-data/', FinancialDataListView.as_view(), name='financial_data_list'), 
    path('company/<int:company_id>/edit-financial-data/', FinancialDataListEditView.as_view(), name='edit_financial_data'),
    path('company/<int:company_id>/upload-financial-data/', UploadFileView.as_view(), name='upload-financial-data'),
    path('company/<int:company_id>/process-financial-data/', ProcessFileView.as_view(), name='process-financial-data'),
] 