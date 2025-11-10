from django.apps import AppConfig
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver


class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'
    verbose_name = 'Human Resources'
    
    def ready(self):
        """Register models with auditlog when the app is ready."""
        from auditlog.registry import auditlog
        from .models import Employee, Department, Position, EmployeeDocument, EmployeeHistory
        
        # Register Employee model for automatic audit logging
        # Exclude photo field that changes every save due to Fernet encryption timestamps
        auditlog.register(Employee, exclude_fields=[
            'photo'
        ])
        
        # Register other HR models for audit logging
        auditlog.register(Department)
        auditlog.register(Position)
        auditlog.register(EmployeeDocument, exclude_fields=['file'])
        auditlog.register(EmployeeHistory)
        
        # Import signals to ensure they are connected
        from . import signals
        
        # Set up custom signal handlers for encrypted field tracking
        self.setup_encrypted_field_tracking()
    
    def setup_encrypted_field_tracking(self):
        """Set up custom signal handlers to properly track encrypted field changes."""
        from .models import Employee
        from .signals import track_encrypted_field_changes
        
        # Connect the signal handler
        pre_save.connect(track_encrypted_field_changes, sender=Employee) 