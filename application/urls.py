# application/urls.py
from django.urls import path, include, re_path
from django.contrib import admin
from allauth.account.views import confirm_email

urlpatterns = [
    # URLs for django-rest-auth
    path('rest-auth/', include('rest_auth.urls')),

    # URLs for django-rest-auth registration
    path('rest-auth/registration/', include('rest_auth.registration.urls')),

    # URLs for django-allauth
    path('accounts/', include('allauth.urls')),

    # Custom URL for email confirmation
    re_path(r'^accounts-rest/registration/account-confirm-email/(?P<key>.+)/$', confirm_email, name='account_confirm_email'),
]
