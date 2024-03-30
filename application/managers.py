"""
This custom manager provides helper methods to create regular and superusers, as
the default user model expects a username, which I am not using. The reason to do so is 
because I want email verification and a username becomes obsolete
"""
from django.contrib.auth.base_user import (
    BaseUserManager,
)  # Starting point from which I inherit for the manager

class CustomUserManager(BaseUserManager):
    """
    This manager is a subclass of BaseUserManager and overrides two methods-create user and superuser. This
    is a necessary step as I need to handle the case where the email is the unique identifier.
    """

    def create_user(self, first_name: str, last_name: str, email: str, password: str, total_brush_time=0, current_level=1, current_level_xp=0, current_level_max_xp=120, is_staff = False, is_superuser = False):
        """
        Create and save a user with the provided email and password

        Args:
            first_name (str): user's first name]
            last_name (str): user's last name
            email (str): The email address of the user.
            password (str): The password of the user.
            is_staff (Boolean, optional): can the user access the admin site
            is_superuser: is the user a superuser with all privilleges

        Returns:
            CustomUser: The created user instance.

        Raises:
            ValueError: If no first name,password, last name or email are provided.
        """
        # Compulsory fields
        if not email:
            raise ValueError("The user must have an email.")
        if not first_name:
            raise ValueError("The user must have a first name.")
        if not last_name:
            raise ValueError("The user must have a last name.")
        if not password:
            raise ValueError("The user must have a password.")
        # Standardise the domain part of the email to lowercase to prevent case sensitive email issues
        email = self.normalize_email(email)
        # Create a user object
        user = self.model(email=email)
        user.first_name = first_name
        user.last_name = last_name
        # Password hashing
        user.set_password(password)
        user.total_brush_time = total_brush_time
        user.current_level = current_level
        user.current_level_xp = current_level_xp
        user.current_level_max_xp = current_level_max_xp
        # Set the remaining fields for the user
        user.is_active = True
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.save()  # Save the user to the database
        return user

    def create_superuser(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
       ):
        """
        Create and save a SUPERuser with the provided email and password. Superusers have all permissions
        by default and can access the admin site (at ..../admin/)

        Args:
            first_name (str): Superusers first name
            last_name (str): Superusers last name
            email (str): The email address of the superuser.
            password (str): The password of the superuser.

        Returns:
            CustomUser: The created superuser instance.

        """
        user = self.create_user(first_name, last_name,email, password,is_staff=True,is_superuser=True)
        user.save()
    
