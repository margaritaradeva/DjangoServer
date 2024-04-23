from django.contrib import admin

from .models import CustomUser

# Register your models here.


# Admin interface customisation for CustomUser model
class CustomUserAdmin(admin.ModelAdmin):
    """
    CustomUserAdmin defines the representation of the CustomUser model in the Django admin interface
    """

    # Display the following fields in the admin list view (in /admin/)
    list_display = ("id", "first_name", "last_name", "email")


# Register the CustomUser model and CustomerUserAdmin with the admin site
admin.site.register(CustomUser, CustomUserAdmin)
