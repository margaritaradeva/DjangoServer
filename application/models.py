from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


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


class CustomUser(AbstractUser):
    """
    Custom user model for the app that uses enmail as the unique identifier as opposed to username

    Attributes:
    first_name (CharField): First name of a user
    last_name (CharField): Last name of a user
    password (CharField): User's password-not declared here as it is by dafault from django
    email (EmailField): The email field used for authentication
    thumbnail (ImageField): An optional image fielfd for storing user thumbnail (profile pic)
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

    # Link the custom user manager to this user model. This manager will understand that email
    # is the unique identifier and will handle user creationappropriately
    objects = CustomUserManager()

    def __str__(self):
        """
        String representation of the CustomUser instance, used in admin and shell

        Returns:
        str: The user's email addresss
        """
        return f"{self.first_name} {self.last_name} {self.email}"
