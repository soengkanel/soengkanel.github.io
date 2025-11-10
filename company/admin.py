from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib import messages
from core.admin_mixins import SharedModelAdminMixin
from .models import Group, Company, Domain, Branch
from .cascade_handlers import delete_tenant_related_objects, get_company_cascade_info
from django_tenants.utils import schema_context, get_public_schema_name
import logging

logger = logging.getLogger(__name__)

@admin.register(Group)
class GroupAdmin(SharedModelAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'headquarters', 'total_companies', 'active_companies', 'is_active', 'created_at')
    list_filter = ('is_active', 'established_date', 'created_at')
    search_fields = ('name', 'headquarters', 'website', 'email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('headquarters', 'phone_number', 'email', 'website'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('established_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def total_companies(self, obj):
        """Get total companies with proper schema context"""
        from django_tenants.utils import get_public_schema_name, schema_context

        with schema_context(get_public_schema_name()):
            return obj.companies.count()
    total_companies.short_description = 'Total Companies'

    def active_companies(self, obj):
        """Get active companies with proper schema context"""
        from django_tenants.utils import get_public_schema_name, schema_context

        with schema_context(get_public_schema_name()):
            return obj.companies.filter(is_active=True).count()
    active_companies.short_description = 'Active Companies'

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete groups due to cascade implications"""
        return request.user.is_authenticated and request.user.is_superuser

    def has_add_permission(self, request):
        """Only staff users can add groups"""
        return request.user.is_authenticated and request.user.is_staff

    def has_change_permission(self, request, obj=None):
        """Only staff users can change groups"""
        return request.user.is_authenticated and request.user.is_staff


@admin.register(Company)
class CompanyAdmin(SharedModelAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'group', 'company_type', 'schema_name', 'is_active')
    list_filter = ('company_type', 'is_active', 'group', 'country')
    search_fields = ('name', 'registration_number', 'tax_id', 'email', 'schema_name')
    readonly_fields = ('schema_name',)
    ordering = ['group__name', 'name']

    def get_queryset(self, request):
        """
        Override to prevent cross-schema queries.

        The Company model has reverse relations from tenant-specific models (Project, etc.)
        which don't exist in the public schema. We must ensure we don't try to access them.
        """
        # Ensure we're in public schema
        with schema_context(get_public_schema_name()):
            # Get base queryset WITHOUT following reverse relations
            qs = super().get_queryset(request)

            # IMPORTANT: Only select_related for models in the public schema
            # Do NOT prefetch_related any tenant models
            qs = qs.select_related('group')

            return qs

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'group', 'company_type', 'description', 'is_active')
        }),
        ('Registration Information', {
            'fields': ('registration_number', 'tax_id', 'established_date'),
            'classes': ('collapse',)
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state_province', 'postal_code', 'country'),
            'classes': ('collapse',)
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'website'),
            'classes': ('collapse',)
        }),
        ('Tenant Information', {
            'fields': ('schema_name',),
            'classes': ('collapse',)
        }),
    )


    def delete_model(self, request, obj):
        """Handle deletion of a company and its tenant-specific data."""
        try:
            # First clean up tenant-specific data
            delete_tenant_related_objects(obj)

            # Then delete the company itself
            with schema_context(get_public_schema_name()):
                super().delete_model(request, obj)

            messages.success(request, f"Company '{obj.name}' and all related data deleted successfully.")
        except Exception as e:
            messages.error(request, f"Error deleting company: {str(e)}")

    def delete_queryset(self, request, queryset):
        """Handle bulk deletion of companies."""
        deleted_count = 0
        errors = []

        for company in queryset:
            try:
                # Clean up tenant-specific data for each company
                delete_tenant_related_objects(company)
                company.delete()
                deleted_count += 1
            except Exception as e:
                errors.append(f"{company.name}: {str(e)}")

        if deleted_count > 0:
            messages.success(request, f"Successfully deleted {deleted_count} companies.")

        if errors:
            messages.error(request, f"Errors occurred: {'; '.join(errors)}")

    # User count removed - users are now tenant-specific


@admin.register(Domain)
class DomainAdmin(SharedModelAdminMixin, admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__name')
    ordering = ['domain']


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'city', 'manager_name', 'employee_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'city', 'country', 'created_at')
    search_fields = ('name', 'code', 'city', 'manager_name', 'email')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Address Information', {
            'fields': ('address', 'city', 'state_province', 'postal_code', 'country'),
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'manager_name'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def employee_count(self, obj):
        """Get total number of employees in this branch"""
        return obj.employees.count()
    employee_count.short_description = 'Employees'


# UserCompanyAccess admin removed - users are now tenant-specific
# Each tenant manages its own users independently
