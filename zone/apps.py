from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ZoneConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zone'
    verbose_name = 'People Management'
    
    def ready(self):
        """Set up signals and permissions when the app is ready."""
        post_migrate.connect(self.create_custom_permissions, sender=self)
        # Import signals to ensure they are connected
        from . import signals
    
    def create_custom_permissions(self, sender, **kwargs):
        """Create custom permissions for the zone app after migrations."""
        try:
            # Import here to avoid circular imports
            from .models import Zone, Worker
            from django.contrib.auth.models import Permission
            from django.contrib.contenttypes.models import ContentType
            from django.db import connection
            
            # Check if the required tables exist (important for multi-tenant setup)
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'auth_permission'
                    );
                """)
                if not cursor.fetchone()[0]:
                    # Permission table doesn't exist yet, skip for now
                    return

            # Ensure permissions exist for Zone and Worker models
            zone_content_type = ContentType.objects.get_for_model(Zone)
            worker_content_type = ContentType.objects.get_for_model(Worker)

            # Define custom permissions
            custom_permissions = [
                ('can_view_zone_dashboard', 'Can view zone dashboard', zone_content_type),
                ('can_manage_zones', 'Can manage zones', zone_content_type),
                ('can_view_worker_list', 'Can view worker list', worker_content_type),
                ('can_manage_workers', 'Can manage workers', worker_content_type),
                ('can_view_worker_details', 'Can view worker details', worker_content_type),
                ('can_edit_worker_profile', 'Can edit worker profile', worker_content_type),
                ('can_manage_worker_documents', 'Can manage worker documents', worker_content_type),
                ('can_view_worker_reports', 'Can view worker reports', worker_content_type),
                ('can_manage_probation', 'Can manage worker probation', worker_content_type),
                ('can_extend_probation', 'Can extend worker probation', worker_content_type),
                ('can_complete_probation', 'Can complete worker probation', worker_content_type),
            ]

            for codename, name, content_type in custom_permissions:
                Permission.objects.get_or_create(
                    codename=codename,
                    name=name,
                    content_type=content_type,
                )
        except Exception as e:
            # Don't fail migrations if permission creation fails
            pass

        # Import and register custom audit configurations
        self.register_audit_configurations()
    
    def register_audit_configurations(self):
        """Register custom audit logging configurations for encrypted fields"""
        try:
            from auditlog.registry import auditlog
            from .models import Zone, Worker

            # Check if Zone is already registered and unregister it
            if auditlog.contains(Zone):
                auditlog.unregister(Zone)

            # Register Zone with custom field exclusions
            auditlog.register(
                Zone,
                exclude_fields=['phone_number'],  # Exclude encrypted phone number
                mask_fields=['address'],  # Mask address for privacy
            )

            # Check if Worker is already registered and unregister it
            if auditlog.contains(Worker):
                auditlog.unregister(Worker)

            # Register Worker with encrypted field exclusions
            auditlog.register(
                Worker,
                exclude_fields=[
                    'phone_number', 'email', 'address', 'emergency_phone',
                    'passport_number', 'id_card_number', 'notes'
                ],  # Exclude all encrypted fields
                mask_fields=['first_name', 'last_name'],  # Mask names for privacy
            )

        except ImportError:
            # auditlog might not be available during initial migrations
            pass
        except Exception as e:
            # Log the error but don't fail the app startup
            pass 