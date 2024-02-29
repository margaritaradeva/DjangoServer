"""
This custom manager provides helper methods to create regular and superusers, as
the default user model expects a username, which I am not using. The reason to do so is 
because I want email verification and a username becomes obsolete
"""

from django.contrib.auth.base_user import BaseUserManager # Starting point from which I inherit for the manager
from django.utils.translation import gettext_lazy as _ # Translation function


class CustomUserManager(BaseUserManager):
    """
   This manager is a subclass of BaseUserManager and overrides two methods-create user and superuser. This
   is a necessary step as I need to handle the case where the email is the unique identifier.
    """

    def create_user(self, email, password, **kwargs):
        """
        Create and save a user with the provided email and password

        Args:
            email (str): The email address of the user.
            password (str, optional): The password of the user.
            **kwargs: Extra fields and values as a dictionary.
            
        Returns:
            User: The created user instance.
            
        Raises:
            ValueError: If no email is provided.
        """
        if not email:
            # Email field is compulsory
            raise ValueError(_('You must enter an email'))
        # Standardise the domain part of the email to lowercase to prevent case sensitive email issues
        email = self.normalize_email(email)
        # Create a user object
        user = self.model(email=email, **kwargs)
        # Password hashing
        user.set_password(password)
        user.save(using=self._db) # Save the user to the database
        return user
    
    def create_superuser(self, email, password, is_staff=True, is_superuser=True, is_active=True,**kwargs):
        """ 
        Create and save a SUPERuser with the provided email and password. Superusers have all permissions
        by default and can access the admin site (at ..../admin/)

        Args:
            email (str): The email address of the superuser.
            password (str, optional): The password of the superuser.
            **kwargs: Extra fields and values as a dictionary.
            
        Returns:
            User: The created superuser instance.
            
        Raises:
            ValueError: If is_staff or is_superuser is not set to True.
        """

        if is_staff is not True:
            raise ValueError(_('Superuser must have "is_staff" equal to True'))
        if is_superuser is not True:
            raise ValueError(_('Superuser must have "is_superuser" equal to True'))
        return self.create_user(email, password, **kwargs)