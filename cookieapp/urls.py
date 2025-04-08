from django.urls import path

from . import views

urlpatterns = [
    path("manage/", views.CookieManageView.as_view(), name="cookie_manage"),
    path('set/', views.SetCookieView.as_view(), name='cookie_set'),
    path('accept-all/', views.AcceptAllCookieView.as_view(), name='cookie_accept_all'),
    path('decline-all/', views.DeclineAllCookieView.as_view(), name='cookie_decline_all'),
] 