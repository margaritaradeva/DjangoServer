from django.forms import ValidationError
from application.models import CustomUser
from rest_framework import serializers
from .models import validate_password
import re

class CustomUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True) # Shouldn't be able to change an id of a user
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True) # Don't ever want to return a password in an API response 
    total_brush_time = serializers.IntegerField()
    
    class Meta:
        model=CustomUser
        fields = {'id', 'first_name', 'last_name', 'password', 'total_brush_time'}
        extra_kwargs = {'password': {'write_only': True}} 
    
    def create(self, data):
        user = CustomUser.objects.create(
            first_name = data['first_name'],
            last_name = data['last_name'],
            email = data['email']
        )
        user.set_password(data['password'])
        user.save()

        return user
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
   
    def validate(self, data):
        """
        Overrides the default validate method to include password validation
        """
        validate_password(data.get('password', ''))   # Validate if the password is present
        return super().validate(data)
    
    def change(self,atr):
        pass
        
    
  