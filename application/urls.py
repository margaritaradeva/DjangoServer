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
    path('reauthenticate/', views.Reuthenticate.as_view(), name="reauthenticate"),
    path('levelUp/', views.UpdateLevel.as_view(), name="update_level"),
    path('updateUserXP/', views.UpdateLevelXP.as_view(), name="update_level_xp"),
    path('updateCurrentLevelMaxXP/', views.UpdateLevelMaxXP.as_view(), name="update_level_max_xp"),
    path('miniShop/', views.MiniShopPhoto().as_view(), name="mini_shop"),
    path('updateStreak/', views.UpdateStreak.as_view(), name="update_streak"),
    path('updateActivity/', views.UpdateActivity.as_view(), name="update_activity"),
    path('activities/',views.UserActivities.as_view(), name="user_activities"),
    path('modify/', views.ChangeUserTesting.as_view(), name="test"),
    path('updateCharacterName/', views.SetCharterName.as_view(), name="char_name"),
]