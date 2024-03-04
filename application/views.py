from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status, permissions
from django.http import HttpResponse
from .serializers import CustomUserSerializer
from . import services, authentication
from rest_framework import exceptions
from django.utils import timezone

def home_view(request):
    return HttpResponse("Welcome to the home page!")


class SignUp(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data
            serializer.instance = services.create_user(dataclass_user=data)
            return Response(data=serializer.data)
        except ValidationError as e:
            return Response(e.detail, status.HTTP_409_CONFLICT)

class SignIn(APIView):
    def post(self, request):
        # not gonna return a dataclass object bc i want to authenticate a user and store that session
        # inside a cookie
        email = request.data["email"]
        password = request.data["password"]
        
        user = services.get_user_by_email(email=email)
        # INvalid credentials for both cases bc we dont wanna tell an attacker which one is wrong
        if user is None:
            raise exceptions.AuthenticationFailed("Invalid credentials")
        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed("Invalid credentials")
        
        token = services.create_jwt_token(id=user.id)
        resp = Response()
        resp.set_cookie(key="jwt", value=token, httponly=True)
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        return resp
        # JWT token
    
class isSignedIn(APIView):
        # can only be used if the user is authenticated
    authentication_classes = (authentication.CustomUserAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user=request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)



class SignOut(APIView):
    authentication_classes = (authentication.CustomUserAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self,request):
        resp = Response()
        resp.delete_cookie("jwt")
        resp.data = {"message":"user logged out"}

        return resp



# class   DeleteUserView(APIView):
#     # permission_classes = [IsAuthenticated]
#     permission_classes = [AllowAny]

#     def delete(self, request, *args, **kwargs):
#         user = request.user
#         user.delete()
#         return Response({"message":"User account has been successfully deleted."})
