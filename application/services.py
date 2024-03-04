import dataclasses
from typing import TYPE_CHECKING
from . import models 
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
import jwt
import datetime
from django.conf import settings


if TYPE_CHECKING:
    from .models import CustomUser

@dataclasses.dataclass
class CustomUserDataclass:
    first_name: str
    last_name: str
    email: str
    password: str = None
    id: int = None

    @classmethod
    def from_instance(cls, dataclass_user: "CustomUser") -> "CustomUserDataclass":
       # Now we can do sth like data.first_name rather than
        # data["first_name"]
        return cls(
            first_name=dataclass_user.first_name,
            last_name=dataclass_user.last_name,
            email=dataclass_user.email,
            id=dataclass_user.id
        )

    def to_dict(self):
        return dataclasses.asdict(self)

def create_user(dataclass_user: "CustomUserDataclass") -> "CustomUserDataclass":
    try:
        instance = models.CustomUser(
            first_name=dataclass_user.first_name,
            last_name=dataclass_user.last_name,
            email=dataclass_user.email
        ) 
        if dataclass_user.password is not None:
            instance.set_password(dataclass_user.password)

            instance.save()

            return CustomUserDataclass.from_instance(instance)
    except IntegrityError:
        raise ValidationError({"email":"A user with that email already exists"})

def get_user_by_email(email:str) ->"CustomUser":
    # get a user and their data by email
    user = models.CustomUser.objects.filter(email=email).first()
    return user

def create_jwt_token(id: int)-> str:
    data = dict(
        id=id,
        # CHANGE LATER to higer expiration time for the tojen
        expiration_time=(datetime.datetime.utcnow() + datetime.timedelta(minutes=1)).isoformat(),
        time_of_creation = datetime.datetime.utcnow().isoformat(),
    )
    token = jwt.encode(data, settings.JWT_SECRET, algorithm="HS256")

    return token