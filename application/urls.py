# application/urls.py
from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    # URLs for django-rest-auth
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('signin/', views.SignIn.as_view(), name = 'signin'),
    path('authenticated/', views.isSignedIn.as_view(), name='authenticatedUser'),
    path('signout/', views.SignOut.as_view(), name='signout'),
]