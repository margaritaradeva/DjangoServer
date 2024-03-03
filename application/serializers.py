from application.models import CustomUser
from rest_framework import serializers
from . import services

class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True) # Shouldn't be able to change an id of a user
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField(write_only=True) # Don't ever want to return a password in an API response 
        
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return services.CustomUserDataclass(**data) 
    
  