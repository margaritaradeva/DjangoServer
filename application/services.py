
from typing import TYPE_CHECKING
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from . import models


if TYPE_CHECKING:
    from .models import CustomUser


def create_user(data: dict) -> models.CustomUser:
    try:
        user = models.CustomUser(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"]
        )
        user.set_password(data["password"])
        user.save()

        return user
    except IntegrityError as exc:
        raise ValidationError({"email":"A user with that email already exists"}) from exc

def get_user_by_email(email:str) ->"CustomUser":
    # get a user and their data by email
    user = models.CustomUser.objects.filter(email=email).first()
    return user
