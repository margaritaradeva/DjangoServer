from application.models import CustomUser, UserActivity
from rest_framework import serializers
from .models import validate_password


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model. INcludes comprehensive fields
    for serialization and de-serializing, with specific fields set to read/write
    only to ensure data integrity and security (e.g. passwords handling)
    """

    id = serializers.IntegerField(
        read_only=True
    )  # Shouldn't be able to change an id of a user
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True
    )  # Don't ever want to return a password in an API response
    total_brush_time = serializers.IntegerField()
    current_level = serializers.IntegerField()
    current_level_xp = serializers.IntegerField()
    current_level_max_xp = serializers.IntegerField()
    parent_pin = serializers.CharField(
        write_only=True, required=False, allow_blank=True, max_length=6, min_length=6
    )
    is_pin_set = serializers.BooleanField(read_only=True)
    image_id = serializers.IntegerField()
    current_streak = serializers.IntegerField()
    max_streak = serializers.IntegerField()
    total_brushes = serializers.IntegerField()
    last_active_date = serializers.DateField(read_only=True)
    last_active_morning = serializers.DateTimeField(read_only=True)
    last_active_evening = serializers.DateTimeField(read_only=True)
    streak_morning = serializers.IntegerField(read_only=True)
    streak_evening = serializers.IntegerField(read_only=True)
    max_streak_morning = serializers.IntegerField(read_only=True)
    max_streak_evening = serializers.IntegerField(read_only=True)
    total_brushes_morning = serializers.IntegerField(read_only=True)
    total_brushes_evening = serializers.IntegerField(read_only=True)
    percentage_morning = serializers.FloatField(read_only=True)
    percentage_evening = serializers.FloatField(read_only=True)
    total_brushes_days = serializers.IntegerField(read_only=True)
    character_name = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "password",
            "total_brush_time",
            "current_level",
            "current_level_xp",
            "current_level_max_xp",
            "image_id",
            "current_streak",
            "max_streak",
            "total_brushes",
            "parent_pin",
            "is_pin_set",
            "last_active_date",
            "last_active_morning",
            "last_active_evening",
            "streak_morning",
            "streak_evening",
            "max_streak_morning",
            "max_streak_evening",
            "total_brushes_morning",
            "total_brushes_evening",
            "percentage_morning",
            "percentage_evening",
            "total_brushes_days",
            "character_name",
            "is_char_name_set",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, data):
        """
        Create and return a new CustomUser instance, given the validated data
        """
        parent_pin = data.pop("parent_pin", None)

        user = CustomUser.objects.create_user(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password=data["password"],
            total_brush_time=data.get("total_brush_time", 0),
            current_level=data.get("current_level", 1),
            current_level_xp=data.get("current_level_xp", 0),
            current_level_max_xp=data.get("current_level_max_xp", 120),
            image_id=data.get("image_id", 1),
            current_streak=data.get("current_streak", 0),
            max_streak=data.get("max_streak", 0),
            total_brushes=data.get("total_brushes", 0),
        )

        if parent_pin is not None:
            user.parent_pin = parent_pin
        user.save()

        return user

    def validate_password(self, value):
        """
        Validate the password using the custom validation function in  models.py
        """
        validate_password(value)
        return value

    def validate_parent_pin(self, value):
        """ "
        Validate the parent pin o ensure it is numeric (if provided)
        """
        if value and not value.isdigit():
            raise serializers.ValidationError("PIN must be numeric")
        return value


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for the UserActivity model
    """

    class Meta:
        model = UserActivity
        fields = "__all__"
