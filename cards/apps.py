from django.apps import AppConfig


class CardsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cards'
    verbose_name = 'ID Card Management'
    
    def ready(self):
        """Register models with auditlog when the app is ready."""
        try:
            from auditlog.registry import auditlog
            from .models import (WorkerIDCard, EmployeeIDCard, CardPrintingHistory, 
                                EmployeeCardPrintingHistory, CardCharge, EmployeeCardCharge, 
                                CardReplacement)
            
            # Register ID Card models for audit logging
            auditlog.register(WorkerIDCard, exclude_fields=['photo'])
            auditlog.register(EmployeeIDCard, exclude_fields=['photo'])
            auditlog.register(CardPrintingHistory)
            auditlog.register(EmployeeCardPrintingHistory)
            auditlog.register(CardCharge)
            auditlog.register(EmployeeCardCharge)
            auditlog.register(CardReplacement)
        except ImportError:
            # auditlog might not be available during initial migrations
            pass 