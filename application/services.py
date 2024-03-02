import dataclasses
from typing import TYPE_CHECKING
from . import models 

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
    
    @classmethod
    def create_user(dataclass_user: "CustomUserDataclass") -> "CustomUserDataclass":
        instance = models.CustomUser(
            first_name=dataclass_user.first_name,
            last_name=dataclass_user.last_name,
            email=dataclass_user.email
        )
        if dataclass_user.password is not None:
            instance.set_password(dataclass_user.password)

        instance.save()

        return CustomUserDataclass.from_instance(instance)