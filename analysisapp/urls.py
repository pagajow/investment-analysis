from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'), 
    
    path('privacy-policy/', TemplateView.as_view(template_name='analysisapp/legal/privacy_policy.html'), name='privacy_policy'),
    path('terms-of-service/', TemplateView.as_view(template_name='analysisapp/legal/terms_of_service.html'), name='terms_of_service'),
    
    path('about/', views.AboutView.as_view(), name='about'), 
    path('companies/', views.CompanyListView.as_view(), name='company_list'),  
    path('login/', views.CustomLoginView.as_view(template_name='analysisapp/registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.AnalystUserRegisterView.as_view(), name='register'),
    path('profile/', views.AnalystUserProfileView.as_view(), name='profile'),
    path('change-password/', views.CustomPasswordChangeView.as_view(), name='change_password'),
    path('delete-account/', views.AnalystUserDeleteView.as_view(), name='delete_account'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='analysisapp/registration/password_reset_done.html'), 
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='analysisapp/registration/password_reset_complete.html'), 
         name='password_reset_complete'),
    path('finreports/', views.FinReportListView.as_view(), name='finreports_list'),
    path('finreport/<int:pk>/', views.FinReportDetailView.as_view(), name='finreport_detail'),
    path('finreport/add/', views.FinReportCreateView.as_view(), name='finreport_create'),
    path('finreport/<int:pk>/edit/', views.FinReportUpdateView.as_view(), name='finreport_edit'),
    path('finreport/<int:pk>/delete/', views.FinReportDeleteView.as_view(), name='finreport_delete'),
    path('filters/', views.AssetFilterListView.as_view(), name='filter_list'),
    path('filter/add/', views.AssetFilterCreateView.as_view(), name='filter_create'),
    path('filters/<int:pk>/edit/', views.AssetFilterUpdateView.as_view(), name='filter_edit'),
    path('filters/<int:pk>/delete/', views.AssetFilterDeleteView.as_view(), name='filter_delete'),
    path('send-verification-token/', views.SendVerificationTokenView.as_view(), name='send_verification_token'),
    path('verify-email/<str:token>/', views.VerifyTokenView.as_view(), name='verify_email'),
    path('company/add/', views.NewCompanyView.as_view(), name='company_create'),  
    path('company/<int:company_id>/edit/', views.EditCompanyView.as_view(), name='company_edit'),  
    path('company/<int:company_id>/delete/', views.DeleteCompanyView.as_view(), name='company_delete'),
    path('company/<int:company_id>/financial-data/', views.FinancialDataView.as_view(), name='financial_data'), 
    path('company/<int:company_id>/financial-data/edit/', views.FinancialDataEditView.as_view(), name='edit_financial_data'),
    path('company/<int:company_id>/financial-data/upload/', views.UploadFileView.as_view(), name='upload-financial-data'),
    path('company/<int:company_id>/financial-data/process/', views.ProcessFileView.as_view(), name='process-financial-data'),
    path('company/<int:company_id>/notes/', views.AssetNoteListView.as_view(), name='assetnote_list'),
    path('company/<int:company_id>/note/<int:pk>/', views.AssetNoteDetailView.as_view(), name='assetnote_detail'),
    path('company/<int:company_id>/note/add/', views.AssetNoteCreateView.as_view(), name='assetnote_create'),
    path('company/<int:company_id>/note/<int:pk>/edit/', views.AssetNoteUpdateView.as_view(), name='assetnote_edit'),
    path('company/<int:company_id>/note/<int:pk>/delete/', views.AssetNoteDeleteView.as_view(), name='assetnote_delete'),
] 

