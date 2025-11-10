"""
Cascade deletion handlers for Company model to handle cross-schema relationships.

This module provides utilities to safely handle deletion of Company objects
that have related objects in tenant-specific schemas (like Project).
"""

from django.db import transaction
from django_tenants.utils import schema_context, get_public_schema_name
import logging

logger = logging.getLogger(__name__)


def delete_tenant_related_objects(company):
    """
    Delete all tenant-specific objects related to a company before deleting the company.

    This function switches to the company's tenant schema and deletes all related
    objects that reference the company.

    Args:
        company: The Company instance being deleted
    """
    if not company.schema_name:
        return

    # Skip if it's the public schema (no tenant-specific data)
    if company.schema_name == get_public_schema_name():
        return

    try:
        # Switch to the company's tenant schema
        with schema_context(company.schema_name):
            # Import models inside schema context to ensure proper initialization
            from project.models import Project, ProjectTeamMember, ProjectTask
            from hr.models import Employee, Department
            from hr.timecard_models import Timecard, TimecardEntry
            from hr.payroll_models import PayrollPeriod, Payroll, PayrollItem

            # Delete projects (this will cascade to related objects due to model definitions)
            project_count = Project.objects.filter(company=company).count()
            if project_count > 0:
                Project.objects.filter(company=company).delete()

            # Note: Employees and Departments don't directly reference Company,
            # but they exist in the tenant schema
            employee_count = Employee.objects.count()
            department_count = Department.objects.count()

    except Exception as e:
        # Re-raise the exception to prevent company deletion if cleanup fails
        raise


def safe_delete_company(company, force=False):
    """
    Safely delete a company and all its related data across schemas.

    Args:
        company: The Company instance to delete
        force: If True, attempt deletion even if there are warnings

    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        with transaction.atomic():
            # First, clean up tenant-specific data
            delete_tenant_related_objects(company)

            # Then delete the company itself (in public schema)
            with schema_context(get_public_schema_name()):
                company_name = company.name
                schema_name = company.schema_name
                company.delete()

            return True, f"Company {company_name} deleted successfully"

    except Exception as e:
        return False, f"Failed to delete company: {str(e)}"


class CompanyCascadeDeleteMixin:
    """
    Mixin for Company model to handle cascade deletion across schemas.

    Add this mixin to the Company model to automatically handle
    cross-schema cascade deletions.
    """

    def delete(self, *args, **kwargs):
        """
        Override delete to handle tenant-specific related objects.
        """
        # Clean up tenant-specific data first
        delete_tenant_related_objects(self)

        # Then proceed with normal deletion
        super().delete(*args, **kwargs)


def get_company_cascade_info(company):
    """
    Get information about what would be deleted if this company is deleted.

    Args:
        company: The Company instance to analyze

    Returns:
        dict: Information about related objects that would be deleted
    """
    info = {
        'company': {
            'name': company.name,
            'schema': company.schema_name,
            'id': company.id
        },
        'public_schema': {},
        'tenant_schema': {}
    }

    # Check public schema relations
    with schema_context(get_public_schema_name()):
        from company.models import Domain

        domain_count = Domain.objects.filter(tenant=company).count()
        info['public_schema']['domains'] = domain_count

    # Check tenant schema relations if applicable
    if company.schema_name and company.schema_name != get_public_schema_name():
        try:
            with schema_context(company.schema_name):
                from project.models import Project, ProjectTask, ProjectTeamMember
                from hr.models import Employee, Department
                from hr.timecard_models import Timecard

                info['tenant_schema'] = {
                    'projects': Project.objects.filter(company=company).count(),
                    'employees': Employee.objects.count(),
                    'departments': Department.objects.count(),
                    'timecards': Timecard.objects.count(),
                }

                # Get project details
                projects = Project.objects.filter(company=company).values_list('project_name', flat=True)[:5]
                if projects:
                    info['tenant_schema']['sample_projects'] = list(projects)

        except Exception as e:
            info['tenant_schema']['error'] = str(e)

    return info