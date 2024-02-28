from django.urls import path
from .views import SignInView, SignUpView, DeleteUserView


urlpatterns = [
    path('signin/', SignInView.as_view()),
    path('signup/', SignUpView.as_view()),
    path('delete_user/', DeleteUserView.as_view())
]