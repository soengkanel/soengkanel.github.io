"""
Admin interface for core models and shared model configurations for django_tenants
"""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Notification, Nationality
from .admin_mixins import SharedGroupAdmin, register_shared_model_admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'priority', 'is_read', 'is_dismissed', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'is_dismissed', 'created_at')
    search_fields = ('title', 'message', 'recipient__username', 'recipient__email')
    readonly_fields = ('created_at', 'read_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('title', 'message', 'notification_type', 'priority')
        }),
        ('Recipient', {
            'fields': ('recipient',)
        }),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'is_dismissed', 'read_at')
        }),
        ('Action', {
            'fields': ('action_url', 'action_text'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient')
    
    actions = ['mark_as_read', 'mark_as_unread', 'dismiss_notifications']
    
    def mark_as_read(self, request, queryset):
        count = queryset.filter(is_read=False).update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'Marked {count} notifications as read.')
    mark_as_read.short_description = 'Mark selected notifications as read'
    
    def mark_as_unread(self, request, queryset):
        count = queryset.filter(is_read=True).update(is_read=False, read_at=None)
        self.message_user(request, f'Marked {count} notifications as unread.')
    mark_as_unread.short_description = 'Mark selected notifications as unread'
    
    def dismiss_notifications(self, request, queryset):
        count = queryset.filter(is_dismissed=False).update(is_dismissed=True)
        self.message_user(request, f'Dismissed {count} notifications.')
    dismiss_notifications.short_description = 'Dismiss selected notifications'


@admin.register(Nationality)
class NationalityAdmin(admin.ModelAdmin):
    list_display = ('zip_code', 'country_code', 'country_name', 'nationality', 'region', 'created_at')
    list_filter = ('region', 'created_at')
    search_fields = ('zip_code', 'country_code', 'country_name', 'nationality', 'region')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('country_name',)

    fieldsets = (
        ('Location Information', {
            'fields': ('zip_code', 'country_code', 'country_name', 'region')
        }),
        ('Nationality Information', {
            'fields': ('nationality',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    """Admin interface for Django ContentType model."""
    
    list_display = ('id', 'app_label', 'model', 'get_name')
    list_filter = ('app_label',)
    search_fields = ('app_label', 'model')
    readonly_fields = ('id', 'app_label', 'model')
    ordering = ('app_label', 'model')
    
    fieldsets = (
        ('Content Type Information', {
            'fields': ('id', 'app_label', 'model')
        }),
    )
    
    def get_name(self, obj):
        """Display the human-readable name (model's verbose_name)."""
        return obj.name
    get_name.short_description = 'Name'
    
    def has_add_permission(self, request):
        """Prevent adding new content types through admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow viewing but prevent editing content types through admin."""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deleting content types through admin."""
        return False


class TenantAdminSite(AdminSite):
    """
    Custom admin site that displays tenant-specific titles and headers.
    """
    
    def __init__(self, name='admin'):
        super().__init__(name)
    
    def each_context(self, request):
        """
        Return a dictionary of variables to put in the template context for
        every page in the admin site.
        """
        context = super().each_context(request)
        
        # Get tenant information if available
        if hasattr(request, 'tenant') and request.tenant:
            tenant_name = request.tenant.name
            context.update({
                'site_title': f"{tenant_name} Administration",
                'site_header': f"{tenant_name} Management System",
                'site_url': '/',
                'has_permission': request.user.is_active,
            })
        else:
            # Fallback for public schema
            context.update({
                'site_title': "LYP Administration", 
                'site_header': "NextHR",
                'site_url': '/',
                'has_permission': request.user.is_active,
            })
        
        return context


# Replace the default admin site while preserving existing registrations
original_registry = admin.site._registry.copy()
admin.site = TenantAdminSite()
admin.sites.site = admin.site

# Restore all the previously registered models
for model, model_admin in original_registry.items():
    try:
        admin.site.register(model, model_admin.__class__)
    except admin.sites.AlreadyRegistered:
        pass

# Register shared models with tenant-aware admin classes
# This fixes the "Can't delete tenant outside it's own schema" error
# by ensuring shared models are always operated on in the public schema
try:
    register_shared_model_admin(Group, SharedGroupAdmin)
except Exception as e:
    # If registration fails, don't break the admin
    pass