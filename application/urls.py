# application/urls.py
from django.urls import path
from django.contrib import admin
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # URLs for django-rest-auth
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('signin/', views.SignIn.as_view(), name = 'signin'),
    path('authenticated/', views.isSignedIn.as_view(), name='authenticatedUser'),
    path('signout/', views.SignOut.as_view(), name='signout'),
    path('delete/', views.DeleteUser.as_view(), name='delete'),
    path('token/refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('update_brushtime/', views.update_total_brush_time.as_view(), name="update_brush_time"),
    path('setPin/', views.SetParentPin.as_view(), name="set_pin"),
    path('isPinSet/', views.CheckIfPinIsSet.as_view(), name="is_pin_set"),
    path('checkPin/', views.CheckParentPIN.as_view(), name="check_pin"),
]