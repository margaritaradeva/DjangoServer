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
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError as DRFValidationError
#from rest_framework_simplejwt.token_blacklist import OutstandingToken, BlacklistedToken
from .managers import CustomUserManager
from .models import CustomUser, get_user_by_email

def home_view(request):
    return HttpResponse("Welcome to the home page!")


class SignUp(APIView):
    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        try:
            if serializer.is_valid(raise_exception=True):
                user = serializer.save()

                refresh_token = RefreshToken.for_user(user)
                access_token = refresh_token.access_token

                data = {
                    'id':user.id,
                    'first_name':user.first_name,
                    'last_name':user.last_name,
                    'email':user.email,
                    'refresh': str(refresh_token),
                    'access': str(access_token),
                }
                return Response(data=data, status=status.HTTP_201_CREATED)
            else:
                return Response({'detail':'Password does not meet the complexity requirements'},status=status.HTTP_400_BAD_REQUEST)
        except DRFValidationError as e:
            return Response(e.detail, status.HTTP_409_CONFLICT)
        except IntegrityError as e:
            # Handle the unique constraint error
            return Response({'detail': 'A user with that email already exists.'}, status=status.HTTP_409_CONFLICT)

class SignIn(APIView):
    def post(self, request):
        # not gonna return a dataclass object bc i want to
        # authenticate a user and store that session
        # inside a cookie
        email = request.data["email"]
        password = request.data["password"]

        user = get_user_by_email(email=email)
        # INvalid credentials for both cases bc we dont wanna tell an attacker which one is wrong
        if user is None:
            raise exceptions.AuthenticationFailed("Invalid credentials")
        if not user.check_password(raw_password=password):
            raise exceptions.AuthenticationFailed("Invalid credentials")
        # Generate access and refresh tokens from JWT

        refresh_token = RefreshToken.for_user(user)
        access = refresh_token.access_token
        response = Response()
        serializer = CustomUserSerializer(user)
        response.data = {
            'refresh': str(refresh_token),
            'access': str(access),
            'user': serializer.data
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
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            if token is None:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

            # token_delete = OutstandingToken.objects.get(token=token) 
            # token_delete.black()
            resp = Response()
            resp.data = {"message":"user logged out"}
           
            return Response(status=status.HTTP_200_OK)
        except KeyError:
         return Response(status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            print(e) 
            return Response(status=status.HTTP_400_BAD_REQUEST) 
        

class DeleteUser(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAuthenticated]
    def post(self,request):
        email = request.data["email"]

        user = get_user_by_email(email=email)

        # user = request.user
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)