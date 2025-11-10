from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Import user utilities to add helper methods to User model
        try:
            from . import utils
        except ImportError:
            pass