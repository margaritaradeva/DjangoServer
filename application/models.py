"""
Models for the User Managegement System

Including custom user model and utility functions.
This module extends Django's AbstractUser, replacing the username with an
email as the unique identifier.

The module also includes a function to generate filepaths for user
thumbnail pictures, making sure each thumbnail is stored in a unique directory
based on the email address

Classes:
-CustomUser: Extends Django's AbstractUser

Functions:
-upload_thumbnail(instance, filename): unique upload path for thumbnail pictures
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
from datetime import timedelta
from django.utils import timezone
from django.db.models import Manager 

def upload_thumbnail(instance, filename):
    """
    Function to generate the upload path for a user's thumbnail image

    Parameters:
    instance (CustomUser): Who the thumbnail is being set up
    filename (str): The original filename for the thumbnail

    Returns:
    str: A file system path that specifies where the uploadded file will be stored
    """
    path = f"thumbnails/{instance.email}"
    extension = filename.split(".")[-1]
    if extension:
        path = path + "." + extension
    return path


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
        lambda s: any(x.isupper() for x in s), # Check for uppercase
        lambda s: any(x.islower() for x in s), # Lowercase
        lambda s: any(x.isdigit() for x in s), # Digits
        lambda s: any(not x.isalnum() for x in s), # Special chars
        lambda s: len(s) >= 8, # Password length
        ]
    if not all(condition(password) for condition in conditions):
        raise ValidationError("Password does not meet complexity requirements")

def get_user_by_email(email):
        # get a user and their data by email
        user = CustomUser.objects.filter(email=email).first()
        return user

class CustomUser(AbstractUser):
    """
    Custom user model for the app that uses enmail as the unique identifier as opposed to username

    Attributes:
    first_name (CharField): First name of a user
    last_name (CharField): Last name of a user
    password (CharField): User's password-not declared here as it is by dafault from django
    email (EmailField): The email field used for authentication
    thumbnail (ImageField): An optional image fielfd for storing user thumbnail (profile pic)
    total_brush_time(IntegerField): Total amount of time a user has brushed their teeth for
    parent_pin(CharField, max_length=6): Pin to access the parent interface
    Methods:
    __str__: Returs a string representation of the user, which is the user's email address
    """
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = None  # Remove usrname from the username model as it is not needed
    # If the user wants they can optionally add a thumbnail (profile pic)
    thumbnail = models.ImageField(upload_to= upload_thumbnail, null=True, blank=True)
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

    percentage_morning = models.IntegerField(default=0)
    percentage_evening = models.IntegerField(default=0)
   # is_verified = models.BooleanField(default=False)
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
     
     user=models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
     activity_date = models.DateField(null=True, blank=True)
     activity_time = models.DateTimeField(null=True, blank=True)

     activity_type = models.CharField(max_length=10, choices=(('morning', 'Morning'), ('evening', 'Evening'), ('both', 'Both')))
     objects = Manager()
     class Meta:
          indexes = [
               models.Index(fields=['user','activity_date']),
          ]
          unique_together = ('user', 'activity_date','activity_time', 'activity_type')  # Ensuring uniqueness
          
     def __str__(self):
          return f"{self.user.email} - {self.activity_date} - {self.activity_time} - {self.activity_type}"