from django.urls import path, include

from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'companies', views.CompanyViewSet)
router.register(r'financial-data', views.FinDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('company/<int:company_id>/override-financial-data/', views.OverrideFinDataAView.as_view(), name='api_override_financial_data'),
    path('company/<int:company_id>/analize-financial-data/', views.AnalizeFinDataAView.as_view(), name='api_analize_financial_data'),
    path('company/<int:company_id>/download-financial-data/', views.DownloadFinDataAView.as_view(), name='api_download_financial_data'),
    path('company/<int:company_id>/dcf-valuation/', views.DCFValuationView.as_view(), name='api_dcf_valuation'),
] 