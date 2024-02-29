from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext as _
from .managers import CustomUserManager


def upload_thumbnail(instance, filename):
    """
    Function to generate the upload path for a user's thumbnail image

    Parameters:
    instance (CustomUser): The instance of the user whose thumbnail ois being set up
    filename (str): The original filename for the thumbnail

    Returns:
    str: A file system path that specifies where the uploadded file will be stored
    """
    path = f'thumbnails/{instance.email}'
    extension = filename.split('.')[-1]
    if extension:
        path = path + '.' + extension
    return path


class CustomUser(AbstractUser):
    """
    Custom user model for the app that uses enmail as the unique identifier as opposed to username

    Attributes:
    email (EmailField): The email field used for authentication
    thumbnail (ImageField): An optional image fielfd for storing user thumbnail (profile pic)
    staff (BooleanField): A Boolean field to indicate if the user is a staff member
    is_admin (BooleanField): A Boolean field to indicate if the user has admin priviliges

    Methods:
    __str__: Returs a string representation of the user, which is the user's email address
    """

    username = None # Remove usrname from the username model as it is not needed
    # If the user wants they can optionally add a thumbnail (profile pic)
    thumbnail = models.ImageField(
        upload_to=upload_thumbnail,
        null=True,
        blank=True
    )
    # Unique = True enforces all users to have unique (different) emails
    email = models.EmailField(_('email address'),unique=True, blank=False, null=False)
    # Specify the unique identifier to be the email not username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Empty as email is already enforced

    # Link the custom user manager to this user model. This manager will understand that email
    # is the unique identifier and will handle user creationappropriately
    objects =CustomUserManager()

    staff = models.BooleanField(default=False) # a staff user; non super-user
    admin = models.BooleanField(default=False) # equivalent to a superuser

    def __str__(self):
        """
        String representation of the CustomUser instance, used in admin and shell

        Returns:
        str: The user's email addresss
        """
        return self.email

  