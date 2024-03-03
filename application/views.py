from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError

from django.http import HttpResponse
from .serializers import CustomUserSerializer
from . import services


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
            return Response(e.detail)

class SignIn(APIView):
    def post(self, request):
        # email=request.data["email"]
        # password=request.data["password"]
        
        # if not user.check_password(raw)
        pass

# class   DeleteUserView(APIView):
#     # permission_classes = [IsAuthenticated]
#     permission_classes = [AllowAny]

#     def delete(self, request, *args, **kwargs):
#         user = request.user
#         user.delete()
#         return Response({"message":"User account has been successfully deleted."})
