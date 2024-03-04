"""
Custom user authentication class
"""

from django.conf import settings
from rest_framework import authentication, exceptions
import jwt
from . import models

class CustomUserAuthentication(authentication.BaseAuthentication):
    """
    Django REST does not come with a class to autheticate a user together with a cookie
    (jwt token) so it has to be done manually
    """
    def authenticate(self, request):
        token = request.COOKIES.get("jwt")
        if not token:
            # if not authenticated
            return None
        
        try:
            data = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except:
            raise exceptions.AuthenticationFailed("Unauthorised")
        
        user = models.CustomUser.objects.filter(id=data["id"]).first()

        return (user, None)