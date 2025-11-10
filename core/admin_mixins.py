"""
Django admin mixins for handling shared models in django_tenants.

This module provides mixins to properly handle Django's built-in models (User, Group, etc.)
that are stored in the public schema but accessed through tenant-specific admin interfaces.
"""

from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django_tenants.utils import get_public_schema_name, schema_context
from django.db import connection
import logging

logger = logging.getLogger(__name__)


class SharedModelAdminMixin:
    """
    Mixin for admin classes that manage shared models (stored in public schema).

    This mixin ensures that operations on shared models like User and Group
    are performed in the correct schema context (public) even when accessed
    from tenant-specific admin interfaces.

    Usage:
        class MyGroupAdmin(SharedModelAdminMixin, admin.ModelAdmin):
            # Your admin configuration
            pass
    """

    def _ensure_public_schema_context(self, operation_name="operation"):
        """
        Ensure we're operating in the public schema context for shared models.

        Args:
            operation_name (str): Name of the operation for logging

        Returns:
            bool: True if we're in public schema, False if we need to switch
        """
        current_schema = getattr(connection, 'schema_name', None)
        public_schema = get_public_schema_name()

        if current_schema != public_schema:
            return False
        return True

    def get_queryset(self, request):
        """
        Override get_queryset to ensure we're in public schema context.
        """
        public_schema = get_public_schema_name()

        with schema_context(public_schema):
            return super().get_queryset(request)

    def save_model(self, request, obj, form, change):
        """
        Override save_model to ensure saves happen in public schema.
        """
        public_schema = get_public_schema_name()

        with schema_context(public_schema):
            with transaction.atomic():
                super().save_model(request, obj, form, change)

        try:
            if change:
                messages.success(request, f"{obj} was updated successfully in public schema.")
            else:
                messages.success(request, f"{obj} was created successfully in public schema.")
        except Exception:
            # Handle case where messages framework is not available (e.g., in tests)
            pass

    def delete_model(self, request, obj):
        """
        Override delete_model to ensure deletions happen in public schema.
        """
        public_schema = get_public_schema_name()

        with schema_context(public_schema):
            with transaction.atomic():
                obj_str = str(obj)
                super().delete_model(request, obj)

        try:
            messages.success(request, f"{obj_str} was deleted successfully from public schema.")
        except Exception:
            # Handle case where messages framework is not available (e.g., in tests)
            pass

    def delete_queryset(self, request, queryset):
        """
        Override delete_queryset for bulk deletions in public schema.
        """
        public_schema = get_public_schema_name()

        # Log the bulk deletion attempt
        count = queryset.count()

        with schema_context(public_schema):
            with transaction.atomic():
                super().delete_queryset(request, queryset)

        try:
            messages.success(request, f"{count} objects were deleted successfully from public schema.")
        except Exception:
            # Handle case where messages framework is not available (e.g., in tests)
            pass

    def response_delete(self, request, obj_display, obj_id):
        """
        Override response_delete to handle post-deletion redirect properly.
        """
        public_schema = get_public_schema_name()

        with schema_context(public_schema):
            return super().response_delete(request, obj_display, obj_id)


class TenantAwareSharedModelAdmin(SharedModelAdminMixin, admin.ModelAdmin):
    """
    Complete admin class for shared models with tenant awareness.

    This class provides a ready-to-use admin configuration for Django's
    built-in shared models like User and Group when accessed through
    tenant-specific admin interfaces.

    Features:
        pass
    - Automatic schema context switching
    - Proper error handling and user feedback
    - Security logging
    - Transaction safety

    Usage:
        # In your admin.py
        from core.admin_mixins import TenantAwareSharedModelAdmin
        from django.contrib.auth.models import Group

        admin.site.unregister(Group)  # Unregister default admin

        @admin.register(Group)
        class CustomGroupAdmin(TenantAwareSharedModelAdmin):
            list_display = ('name',)
            search_fields = ('name',)
    """

    def has_module_permission(self, request):
        """
        Check if user has permission to access this module.
        Only superusers should manage shared models from tenant interfaces.
        """
        return request.user.is_authenticated and request.user.is_superuser

    def has_add_permission(self, request):
        """Only superusers can add shared model instances."""
        return request.user.is_authenticated and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """Only superusers can change shared model instances."""
        return request.user.is_authenticated and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete shared model instances."""
        return request.user.is_authenticated and request.user.is_superuser

    def changelist_view(self, request, extra_context=None):
        """Add context information about schema operations."""
        extra_context = extra_context or {}
        extra_context.update({
            'is_shared_model': True,
            'current_schema': getattr(connection, 'schema_name', 'unknown'),
            'public_schema': get_public_schema_name(),
        })
        return super().changelist_view(request, extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Add context information about schema operations."""
        extra_context = extra_context or {}
        extra_context.update({
            'is_shared_model': True,
            'current_schema': getattr(connection, 'schema_name', 'unknown'),
            'public_schema': get_public_schema_name(),
        })
        return super().change_view(request, object_id, form_url, extra_context)


def register_shared_model_admin(model_class, admin_class=None, **admin_options):
    """
    Utility function to properly register shared model admins.

    This function handles the common pattern of unregistering the default
    admin and registering a tenant-aware version.

    Args:
        model_class: The Django model class to register
        admin_class: The admin class to use (defaults to TenantAwareSharedModelAdmin)
        **admin_options: Additional options to pass to the admin class

    Usage:
        # In your admin.py
        from django.contrib.auth.models import Group, User
        from core.admin_mixins import register_shared_model_admin

        # Register Group with default shared model admin
        register_shared_model_admin(Group)

        # Register User with custom admin
        class CustomUserAdmin(TenantAwareSharedModelAdmin):
            list_display = ('username', 'email', 'is_active')

        register_shared_model_admin(User, CustomUserAdmin)
    """
    if admin_class is None:
        admin_class = TenantAwareSharedModelAdmin

    # Unregister the default admin if it exists
    try:
        admin.site.unregister(model_class)
    except admin.sites.NotRegistered:
        pass  # Model wasn't registered yet

    # Create admin class with options if provided
    if admin_options:
        class ConfiguredAdmin(admin_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                for key, value in admin_options.items():
                    setattr(self, key, value)

        admin.site.register(model_class, ConfiguredAdmin)
    else:
        admin.site.register(model_class, admin_class)


# Pre-configured admin classes for common shared models
class SharedGroupAdmin(TenantAwareSharedModelAdmin):
    """
    Admin configuration for Django's Group model in multi-tenant setup.
    """
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

    fieldsets = (
        (None, {
            'fields': ('name', 'permissions'),
        }),
    )

    filter_horizontal = ('permissions',)


class SharedUserAdmin(TenantAwareSharedModelAdmin):
    """
    Admin configuration for Django's User model in multi-tenant setup.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'email')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    readonly_fields = ('last_login', 'date_joined')
    filter_horizontal = ('groups', 'user_permissions')