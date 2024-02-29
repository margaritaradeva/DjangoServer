# urls.py
from django.urls import path, include
from django.contrib import admin
from allauth.account.views import confirm_email
from django.urls.conf import re_path as url

urlpatterns = [
    # Django admin route
    path('admin/', admin.site.urls),

    # URLs for django-rest-auth
    path('rest-auth/', include('rest_auth.urls')),

    # URLs for django-rest-auth registration
    path('rest-auth/registration/', include('rest_auth.registration.urls')),

    # URLs for django-allauth
    path('accounts/', include('allauth.urls')),

    # Custom URL for email confirmation
    url(r'^accounts-rest/registration/account-confirm-email/(?P<key>.+)/$', confirm_email, name='account_confirm_email'),
]
