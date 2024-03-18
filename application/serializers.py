from django.forms import ValidationError
from application.models import CustomUser
from rest_framework import serializers
from .models import validate_password
import re

class CustomUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True) # Shouldn't be able to change an id of a user
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True) # Don't ever want to return a password in an API response 
    total_brush_time = serializers.IntegerField()
    
    def create(self, data):
        user = CustomUser.objects.create(
            first_name = data['first_name'],
            last_name = data['last_name'],
            email = data['email'],
            total_brush_time = data.get('total_brush_time',0)
        )
        user.set_password(data['password'])
        user.save()

        return user
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
   
    
    def change(self,atr):
        pass
        
    
  