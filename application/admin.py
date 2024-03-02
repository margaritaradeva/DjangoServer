from django.contrib import admin

from .models import CustomUser

# Register your models here.


admin.site.register(CustomUser)
class Admin(admin.ModelAdmin):
    list_display = (
        "id",
        "first_name",
        "last_name",
        "email",
        "password"
    )

admin.site.register(CustomUser,Admin)