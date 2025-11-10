from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'billing'
    verbose_name = 'Billing and Invoicing'
    
    def ready(self):
        """Register models with auditlog when the app is ready."""
        try:
            from auditlog.registry import auditlog
            from .models import (Service, Invoice, InvoiceLineItem, OfficialReceipt, 
                                CashChequeReceipt, PaymentVoucher, ServiceHistory,
                                ServiceCategory, VisaServiceRecord)
            
            # Register billing models for audit logging
            auditlog.register(Service)
            auditlog.register(Invoice)
            auditlog.register(InvoiceLineItem)
            auditlog.register(OfficialReceipt)
            auditlog.register(CashChequeReceipt)
            auditlog.register(PaymentVoucher)
            auditlog.register(ServiceHistory)
            auditlog.register(ServiceCategory)
            auditlog.register(VisaServiceRecord)
        except ImportError:
            # auditlog might not be available during initial migrations
            pass
