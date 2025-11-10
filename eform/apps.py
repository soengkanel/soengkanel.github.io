from django.apps import AppConfig


class EformConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eform"

    def ready(self):
        """Initialize app configurations after all models are loaded"""
        super().ready()
        self.register_audit_configurations()

    def register_audit_configurations(self):
        """Register audit logging configurations for E-Form models"""
        try:
            from auditlog.registry import auditlog
            from .models import ExtensionRequest, CertificateRequest
            
            # Register ExtensionRequest for audit logging
            if not auditlog.contains(ExtensionRequest):
                auditlog.register(
                    ExtensionRequest,
                    # Mask sensitive fields for privacy
                    mask_fields=['passport_number'],
                    # Track all other fields
                )
            
            # Register CertificateRequest for audit logging
            if not auditlog.contains(CertificateRequest):
                auditlog.register(
                    CertificateRequest,
                    # No sensitive fields to mask in certificate requests
                )
            
        except ImportError:

            
            pass
            # auditlog might not be available during initial migrations
            pass
        except Exception as e:
            # Don't fail the app startup
            pass
