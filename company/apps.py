from django.apps import AppConfig


class CompanyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "company"
    verbose_name = "Company Management"

    def ready(self):
        """
        Initialize the app when Django starts.
        This is where you would import signals or perform other startup tasks.
        """
        from . import signals  # Import signal handlers
