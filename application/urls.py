# application/urls.py
from django.urls import path
from django.contrib import admin
from . import views
urlpatterns = [
    # URLs for django-rest-auth
    path("signup/", views.SignUp.as_view(), name="signup")
]