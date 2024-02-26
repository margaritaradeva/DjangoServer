from rest_framework import serializers

from .models import User



class SignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
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

    def create(self, validated_data):
        #  clean all vlues, set as lowercase
        username = validated_data['username'].lower()
        email = validated_data['email'].lower()
        first_name = validated_data['first_name'].lower()
        last_name = validated_data['last_name'].lower()
        #  create new user
        user = User.objects.create(
            username=username,
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
        model = User
        fields = [
            'username',
            'email',
            'name',
            'thumbnail'

        ]

    def get_name(self, obj):
        fir_name = obj.first_name.capitalize()
        las_name = obj.last_name.capitalize()

        return fir_name + ' ' + las_name