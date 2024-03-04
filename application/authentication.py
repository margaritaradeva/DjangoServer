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
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None # No token provided or wrong scheme
        token = auth_header.split(' ')[1] # Get the token part of the header

        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Token expired, login again")
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Token is invalid')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Invalid token')
        except:
            raise exceptions.AuthenticationFailed('Somethig went wrong during authentication')
        
        user = models.CustomUser.objects.filter(id=payload["id"]).first()
        if user is None:
            raise exceptions.AuthenticationFailed('User not found')
        
        return (user, None)