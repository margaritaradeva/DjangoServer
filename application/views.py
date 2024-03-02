from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
 
# from .serializers import UserSerializer
# Create your views here.
from django.http import HttpResponse
from .serializers import CustomUserUserSerializer
import services


def home_view(request):
    return HttpResponse("Welcome to the home page!")


class SignUp(APIView):
    def post(self, request):
        serializer = CustomUserUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        serializer.instance = services.create_user(dataclass_user=data)
        return Response(data )

# class SignIn(APIView):
#      def 


# class   DeleteUserView(APIView):
#     # permission_classes = [IsAuthenticated]
#     permission_classes = [AllowAny]

#     def delete(self, request, *args, **kwargs):
#         user = request.user
#         user.delete()
#         return Response({"message":"User account has been successfully deleted."})
