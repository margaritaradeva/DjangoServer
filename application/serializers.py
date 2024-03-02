from application.models import CustomUser
from rest_framework import serializers


class CustomUserUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True) # Shouldn't be able to change an id of a user
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField(write_only=True) # Don't ever want to return a password in an API response 
        
