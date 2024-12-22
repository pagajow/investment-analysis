from django.urls import path, include

from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, FinDataViewSet, OverrideFinDataAView, AnalizeFinDataAView

router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'financial-data', FinDataViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('company/<int:company_id>/override-financial-data/', OverrideFinDataAView.as_view(), name='api_override_financial_data'),
    path('company/<int:company_id>/analize-financial-data/', AnalizeFinDataAView.as_view(), name='api_analize_financial_data'),
] 