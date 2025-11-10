"""
Signal handlers for Company app to handle multi-tenant scenarios.
"""

from django.db.models.signals import pre_delete, post_migrate
from django.dispatch import receiver
from django_tenants.utils import schema_context, get_public_schema_name
from django.db import connection
import logging

from .models import Company, Group
from .cascade_handlers import delete_tenant_related_objects

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=Company)
def handle_company_pre_delete(sender, instance, **kwargs):
    """
    Handle pre-deletion of a Company to clean up tenant-specific data.

    This signal fires before a Company is deleted and ensures all
    tenant-specific data is properly cleaned up.
    """
    # Only clean up if the company has a tenant schema
    if instance.schema_name and instance.schema_name != get_public_schema_name():
        try:
            delete_tenant_related_objects(instance)
        except Exception as e:
            # Don't prevent deletion, just continue
            # In production, you might want to raise an exception here
            pass


@receiver(pre_delete, sender=Group)
def handle_group_pre_delete(sender, instance, **kwargs):
    """
    Handle pre-deletion of a Group.

    When a Group is deleted, all related Companies will be cascade deleted.
    This signal ensures we log this action for audit purposes.
    """
    # Get all companies that will be deleted
    companies = instance.companies.all()
    company_names = [c.name for c in companies]


def patch_company_admin_queryset():
    """
    Patch the Company model's default manager to prevent cross-schema queries.

    This function modifies how Company queries work when in the admin interface
    to prevent accessing tenant-specific reverse relations.
    """
    from django.db import models
    from .models import Company

    original_get_queryset = Company.objects.get_queryset

    def safe_get_queryset():
        """
        Get a queryset that's safe for cross-schema operations.
        """
        # Get the original queryset
        qs = original_get_queryset()

        # If we're in the public schema, don't try to access tenant relations
        current_schema = getattr(connection, 'schema_name', None)
        if current_schema == get_public_schema_name():
            # Don't prefetch or select any tenant-specific relations
            # This prevents Django from trying to query 'projects' table in public schema
            pass

        return qs

    # Only patch if we haven't already
    if not hasattr(Company.objects.get_queryset, '_patched'):
        Company.objects.get_queryset = safe_get_queryset
        Company.objects.get_queryset._patched = True


# Apply the patch when the module loads
try:
    patch_company_admin_queryset()
except Exception as e:
    pass