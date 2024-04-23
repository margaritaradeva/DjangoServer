from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    """ "
    Configuration for the application app.

    Attributes:
    default_auto_field (str): Specifies the type of auto field to use as a primary key
    nae (str): Defines the full Python path to the application
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "application"
