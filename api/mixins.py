"""
Base mixins for API views in NextHR.

This module contains reusable mixins that provide common functionality
across different API viewsets, particularly for multi-tenant support.
"""
from rest_framework import viewsets
from django.db import connection


class TenantFilterMixin:
    """
    Mixin to automatically filter querysets by current tenant.
    In django-tenants setup, each tenant has its own database schema.

    This mixin ensures that:
        pass
    - All queries are automatically filtered by the current tenant
    - New objects are automatically assigned to the current tenant
    - Response data includes tenant context information
    """

    def get_queryset(self):
        """Override to ensure tenant filtering is applied"""
        queryset = super().get_queryset()

        # Get the current tenant (Company) from the database connection
        current_tenant = connection.tenant

        # Check if model has a company field
        model_fields = [field.name for field in queryset.model._meta.get_fields()]

        if 'company' in model_fields:
            queryset = queryset.filter(company=current_tenant)
        elif 'project' in model_fields:
            # For models related to projects (tasks, milestones, etc.)
            queryset = queryset.filter(project__company=current_tenant)
        elif 'timesheet' in model_fields:
            # For models related to timesheets
            queryset = queryset.filter(timesheet__company=current_tenant)
        elif 'team' in model_fields:
            # For models related to teams
            queryset = queryset.filter(team__company=current_tenant)

        return queryset

    def perform_create(self, serializer):
        """Override to automatically set tenant context when creating objects"""
        current_tenant = connection.tenant

        # Automatically set company and created_by fields
        create_kwargs = {'created_by': self.request.user}

        # Check if model has company field
        model_fields = [field.name for field in serializer.Meta.model._meta.get_fields()]
        if 'company' in model_fields:
            create_kwargs['company'] = current_tenant

        serializer.save(**create_kwargs)

    def list(self, request, *args, **kwargs):
        """Override list to add tenant context to response"""
        response = super().list(request, *args, **kwargs)

        # Add tenant context to response
        current_tenant = connection.tenant
        tenant_info = {
            'tenant_name': current_tenant.name if hasattr(current_tenant, 'name') else str(current_tenant),
            'tenant_schema': current_tenant.schema_name if hasattr(current_tenant, 'schema_name') else 'unknown'
        }

        # Modify response to include tenant context
        if isinstance(response.data, dict):
            response.data['tenant_context'] = tenant_info
            response.data['filtered_by_tenant'] = True
            response.data['total_results'] = len(response.data.get('results', []))

        return response

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add tenant context to response"""
        response = super().retrieve(request, *args, **kwargs)

        # Add tenant context to response
        current_tenant = connection.tenant
        tenant_info = {
            'tenant_name': current_tenant.name if hasattr(current_tenant, 'name') else str(current_tenant),
            'tenant_schema': current_tenant.schema_name if hasattr(current_tenant, 'schema_name') else 'unknown'
        }

        # Add tenant context to single object response
        if isinstance(response.data, dict):
            response.data['tenant_context'] = tenant_info

        return response

    def create(self, request, *args, **kwargs):
        """Override create to add tenant context to response"""
        response = super().create(request, *args, **kwargs)

        # Add tenant context to response
        current_tenant = connection.tenant
        tenant_info = {
            'tenant_name': current_tenant.name if hasattr(current_tenant, 'name') else str(current_tenant),
            'tenant_schema': current_tenant.schema_name if hasattr(current_tenant, 'schema_name') else 'unknown'
        }

        # Add tenant context to created object response
        if isinstance(response.data, dict):
            response.data['tenant_context'] = tenant_info
            response.data['created_for_tenant'] = True

        return response