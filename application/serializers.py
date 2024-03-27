from django.forms import ValidationError
from application.models import CustomUser
from rest_framework import serializers
from .models import validate_password


class CustomUserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True) # Shouldn't be able to change an id of a user
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True) # Don't ever want to return a password in an API response 
    total_brush_time = serializers.IntegerField()
    current_level = serializers.IntegerField()
    parent_pin = serializers.CharField(write_only=True, required=False, allow_blank=True, max_length=6,min_length=6)
    is_pin_set = serializers.BooleanField(read_only=True)

    class Meta:
        model=CustomUser
        fields = ('id','first_name','last_name','email','password','total_brush_time','current_level','parent_pin','is_pin_set')
        extra_kwargs = {'password': {'write_only':True}}
   
    def create(self, data):
        parent_pin = data.pop('parent_pin', None)

        user = CustomUser.objects.create_user(
            first_name = data['first_name'],
            last_name = data['last_name'],
            email = data['email'],
            password=data['password'],
            total_brush_time = data.get('total_brush_time',0),
            current_level = data.get('current_level', 1)
        )

        if parent_pin is not None:
            user.parent_pin = parent_pin
        user.save()

        return user
    
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def validate_parent_pin(self,value):
        if value and not value.isdigit():
            raise serializers.ValidationError("PIN must be numeric")
        return value
   
    
  