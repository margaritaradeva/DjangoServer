from rest_framework import serializers

from .models import CustomUser



class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'email',
            'first_name',
            'last_name',
            'password'
        ]
        extra_kwargs = {
            'password' : {
                # Ensures that when we serialize this field will be excluded
                'write_only': True
            }
        }
    def validate_email(self, value):
        # Convert email to lowercase to ensure uniqueness check is case-insensitive
        lower_email = value.lower()
        if CustomUser.objects.filter(email=lower_email).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return lower_email
    
    def create(self, validated_data):
        #  clean all vlues, set as lowercase
        email = validated_data['email'].lower()
        first_name = validated_data['first_name'].lower()
        last_name = validated_data['last_name'].lower()
        #  create new user
        user = CustomUser.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        password = validated_data['password']
        user.set_password(password)
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'email',
            'name',
            'thumbnail'

        ]

    def get_name(self, obj):
        fir_name = obj.first_name.capitalize()
        las_name = obj.last_name.capitalize()

        return fir_name + ' ' + las_name