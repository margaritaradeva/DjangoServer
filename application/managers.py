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
    is a necessary step as I need to handle the case where the email is the unique authentication identifier.
    """

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        total_brush_time=0,
        current_level=1,
        current_level_xp=0,
        current_level_max_xp=120,
        image_id=1,
        current_streak=0,
        max_streak=0,
        total_brushes=0,
        is_staff=False,
        is_superuser=False,
    ):
        """
        Create and save a user with the provided email and password

        Parameters:
            first_name (str): user's first name]
            last_name (str): user's last name
            email (str): The email address of the user.
            password (str): The password of the user.
            total_brush_time (int): The total number of seconds a user has brushed their teeth for
            current_level (int): A user's current level
            current_level_xp (int): Current level experience points acquired by a user
            current_level_max_xp (int): Current level's maximum experience points possible
            image_id (int): Used to indicate which customised character should be rendered
            current_streak (int): User's current number of consecutive days that they have brushed their teeth
            max_streak (int): User's maximum number of consecutive days they have brushed their teeth
            total_brushes (int): Total number of brushes completed by a user
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
        # Set the values to the associated user fields and set to the deault ones if not provided
        user.total_brush_time = total_brush_time
        user.current_level = current_level
        user.current_level_xp = current_level_xp
        user.current_level_max_xp = current_level_max_xp
        user.image_id = image_id
        user.current_streak = current_streak
        user.max_streak = max_streak
        user.total_brushes = total_brushes
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
        Create and save a superuser with the provided email and password. Superusers have all permissions
        by default and can access the admin site (at ..../admin/)

        Parameters:
            first_name (str): Superusers first name
            last_name (str): Superusers last name
            email (str): The email address of the superuser.
            password (str): The password of the superuser.

        Returns:
            CustomUser: The created superuser instance with full persmissions.

        """
        user = self.create_user(
            first_name, last_name, email, password, is_staff=True, is_superuser=True
        )
        user.save()
