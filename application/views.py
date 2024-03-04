from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework import status, permissions
from django.http import HttpResponse
from .serializers import CustomUserSerializer
from . import services, authentication

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
        # not gonna return a dataclass object bc i want to
        # authenticate a user and store that session
        # inside a cookie
        email = request.data["email"]
        password = request.data["password"]

        user = services.get_user_by_email(email=email)
        # INvalid credentials for both cases bc we dont wanna tell an attacker which one is wrong
        if user is None:
            raise exceptions.AuthenticationFailed("Invalid credentials")
        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed("Invalid credentials")
        # Generate access and refresh tokens from JWT

        refresh_token = RefreshToken.for_user(user)
        access = refresh_token.access_token
        response = Response()
        response.data = {
            'refresh': str(refresh_token),
            'access': str(access),
        }

        response.status_code = status.HTTP_200_OK
        return response
        # JWT token

class isSignedIn(APIView):
        # can only be used if the user is authenticated
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user=request.user
        serializer = CustomUserSerializer(user)
        return Response({"message": "User is authenticated"}, status=status.HTTP_200_OK)



class SignOut(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self,request):
        refresh_token = request.data.get('refresh_token')
        if refresh_token is None:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


        resp = Response()
        resp.data = {"message":"user logged out"}

        return resp

class CustomTokenRefresh(TokenRefreshView):
    def post(self,request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        response.data['status'] = 'success'

        return response
