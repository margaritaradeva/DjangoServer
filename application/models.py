"""
Models for the User Managegement System

Including custom user model and utility functions as well as a second model to store
information about each user's activity.
The Custom user model extends Django's AbstractUser, replacing the username with an
email as the unique identifier.

Classes:
-CustomUser: Extends Django's AbstractUser
-UserActivity: Extends Django's Model

Functions:
-validate_password(password): validate a user's password (if it is complex enough)

Custom Manager:
-overrides Django's default user model manager to use email as unique identifier
"""

from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.contrib.auth.validators import UnicodeUsernameValidator
from .managers import CustomUserManager
from django.db.models import Manager


def validate_password(password):
    """
    Validates a user's password for the following conditions:
    -At least 8 characters long
    -At least one uppercase letter
    -At least one lowercase letter
    -At least one special character
    -At least one number
    """
    conditions = [
        lambda s: any(x.isupper() for x in s),  # Check for uppercase
        lambda s: any(x.islower() for x in s),  # Lowercase
        lambda s: any(x.isdigit() for x in s),  # Digits
        lambda s: any(not x.isalnum() for x in s),  # Special chars
        lambda s: len(s) >= 8,  # Password length
    ]
    if not all(condition(password) for condition in conditions):
        raise ValidationError("Password does not meet complexity requirements")


def upload_thumbnail(instance, filename):
    """
    Generates a unique file path for storing a user's thumbnail image.

    Args:
        instance (CustomUser):  The instance of the `CustomUser` model for which
                                the thumbnail is being uploaded.
        filename (str): The original name of the uploaded thumbnail file.

    Returns:
        str: A file path within the "thumbnails" directory, including
             the user's email to ensure uniqueness. The path may optionally
             include the file extension.
    """
    path = f"thumbnails/{instance.email}"
    extension = filename.split(".")[-1]
    if extension:
        path = path + "." + extension
    return path


def get_user_by_email(email):
    """
    Get a user by their unique identifier - email.
    This function is used for the views that do not need JWT authentication
    """
    user = CustomUser.objects.filter(email=email).first()
    return user


class CustomUser(AbstractUser):
    """
    Custom user model for the app that uses email as the unique identifier as opposed to username

    Attributes:
    first_name (CharField): First name of a user
    last_name (CharField): Last name of a user
    password (CharField): User's password-not declared here as it is by dafault from django
    email (EmailField): The email field used for authentication
    thumbnail (ImageField): An optional image fielfd for storing user thumbnail (profile pic)
    total_brush_time(IntegerField): Total amount of time a user has brushed their teeth for
    parent_pin(CharField, max_length=6): Pin to access the parent interface
    total_brush_time(IntegerField): How many seconds has a user brushed their teeth for in total
    current_level_xp(IntegerField): The amount of experience points a user currently has for their level
    current_level_max_xp(IntegerField): The maximum experience points that have to be achieved to progress to the next level
    image_id(IntegerField): Used to indicate which customised character should be rendered
    current_streak(IntegerField): The current number of consecutive days a user has brushed their teeth for
    max_streak(IntegerField): The maximum number of consecutive days a user has brished their teeth for
    total_brushes(IntegerField): Total number of brushing sessions completed
    parent_pin(CharField): Parent PIN to unlock the parent interface
    is_pin_set(BooleanField): Indicates whether a parent PIN is set
    last_active_date(DateField): User's last active date
    last_active_morning(DateTimeField): User's last active brush time in the morning
    last_active_evening(DateTimeField): User's last active brush time in the eveninig
    streak_morning(IntegerField): The current number of consecutive days when a user has brushed their teeth in the morning
    max_streak_morning(IntegerField): The maximum number of consecutive days when a user has brushed their teeth in the morning
    streak_evening(IntegerField): The current number of consecutive days when a user has brushed their teeth in the evening
    max_streak_evening(IntegerField): The maximum number of consecutive days when a user has brushed their teeth in the evening
    total_brushes_morning(IntegerField): Total number of brushes completed in the morning
    total_brushes_evening(IntegerField): Total number of brushes completed in the evening
    total_brushes_days(IntegerField): Total number of days a user has been active
    percentage_morning(FloatField): Percentage of brushes completed in the morning out of the total days they have been active
    percentage_evening(FloatField): Percentage of brushes completed in the evening out of the total days they have been active
    character_name(CharField): Name for the application's character
    is_char_name_set(BooleanField): Indicates whetehr a charatcer name has been set
    Methods:
    __str__: Returs a string representation of the user, which is the user's email address
    """

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = None  # Remove usrname from the username model as it is not needed
    # If the user wants they can optionally add a thumbnail (profile pic)
    thumbnail = models.ImageField(upload_to=upload_thumbnail, null=True, blank=True)
    # Unique = True enforces all users to have unique (different) emails
    email = models.EmailField(unique=True, blank=False, null=False)
    # Specify the unique identifier to be the email not username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]  # Empty as email is already enforced
    # Total amount of time that a user has brushed their teeth
    total_brush_time = models.IntegerField(default=0)
    current_level = models.IntegerField(default=1)
    current_level_xp = models.IntegerField(default=0)
    current_level_max_xp = models.IntegerField(default=120)
    image_id = models.IntegerField(default=1)
    current_streak = models.IntegerField(default=0)
    max_streak = models.IntegerField(default=0)
    total_brushes = models.IntegerField(default=0)
    parent_pin = models.CharField(max_length=6, null=True, blank=True)
    is_pin_set = models.BooleanField(default=False)
    last_active_date = models.DateField(null=True, blank=True)
    last_active_morning = models.DateTimeField(null=True, blank=True)
    last_active_evening = models.DateTimeField(null=True, blank=True)
    streak_morning = models.IntegerField(default=0)
    max_streak_morning = models.IntegerField(default=0)
    streak_evening = models.IntegerField(default=0)
    max_streak_evening = models.IntegerField(default=0)
    total_brushes_morning = models.IntegerField(default=0)
    total_brushes_evening = models.IntegerField(default=0)
    total_brushes_days = models.IntegerField(default=0)
    percentage_morning = models.FloatField(default=0.0)
    percentage_evening = models.FloatField(default=0.0)
    character_name = models.CharField(default="Brushy")
    is_char_name_set = models.BooleanField(default=False)
    # Link the custom user manager to this user model. This manager will understand that email
    # is the unique identifier and will handle user creationappropriately
    objects = CustomUserManager()
    validators = [UnicodeUsernameValidator, validate_password]

    def __str__(self):
        """
        String representation of the CustomUser instance, used in admin and shell

        Returns:
        str: The user's email addresss
        """
        return f"Name: {self.first_name} {self.last_name} \n email: {self.email}"


class UserActivity(models.Model):
    """
    Represents a single brushing activity completed by a user. Stores essenial information
    about the session, including the associated user, date, time and the type of activity.
    """

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="activities"
    )
    """
     Creates a foreign key relationship to the CustomUser model
     * on_delete=models.CASCADE: Ensures that if a user is deleted, all their activity records are deleted as well, maintaining data integrity
     * related name = 'activities': Provides an accessor on the CustomUser model to all associated activity records conveniently
     """

    activity_date = models.DateField(null=True, blank=True)
    """
     Stores the precise time of the brushing activity. Can be null for flexibility.
     """
    activity_time = models.DateTimeField(null=True, blank=True)
    """
     Indicates the type of brushing activity:
     * 'morning': Represents a morning brushing session
     * 'evening': Represents an evening brushing session
     * 'both': Used whem a user brushes bothmorning and evening in a single day
     """
    activity_type = models.CharField(
        max_length=10,
        choices=(("morning", "Morning"), ("evening", "Evening"), ("both", "Both")),
    )
    objects = Manager()

    class Meta:
        """ "
        Provides metadata for the UserActivity model, specifying index and uniqueness constraints
        """

        indexes = [
            models.Index(fields=["user", "activity_date"]),
        ]
        """
          Creates an index on the combination of user and activity_date fields. This can optimise the database
          queries that rely on filtering or sorting by user and date.
          """
        unique_together = (
            "user",
            "activity_date",
            "activity_time",
            "activity_type",
        )  # Ensuring uniqueness
        """
          Enforces uniqueness at the database level. This ensures that a user cannot have any activity records with 
          the same date, time, and activity type, preventing data dublication.
          """

    def __str__(self):
        """ "
        Defines how a UserActivity object is represented as a string.
        """
        return f"{self.user.email} - {self.activity_date} - {self.activity_time} - {self.activity_type}"
