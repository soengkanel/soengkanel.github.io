"""
API Views Package for NextHR.

This package organizes API views into logical modules for better maintainability.
Import all views here to maintain backward compatibility with existing imports.
"""

# Import all viewsets and views from the modular structure
from .project_views import (
    ProjectTypeViewSet,
    ProjectTemplateViewSet,
    ProjectViewSet,
    ProjectTaskViewSet,
    ProjectMilestoneViewSet,
    ProjectExpenseViewSet,
)

from .team_views import (
    TeamViewSet,
    TeamMemberViewSet,
)

from .timesheet_views import (
    TimesheetViewSet,
)

from .auth_views import (
    api_login,
    api_logout,
    api_user_profile,
    api_csrf_token,
)

from .tenant_views import (
    tenant_info_api,
    available_tenants_api,
    api_overview,
)

# Make all views available when importing from api.views
__all__ = [
    # Project views
    'ProjectTypeViewSet',
    'ProjectTemplateViewSet',
    'ProjectViewSet',
    'ProjectTaskViewSet',
    'ProjectMilestoneViewSet',
    'ProjectExpenseViewSet',

    # Team views
    'TeamViewSet',
    'TeamMemberViewSet',

    # Timesheet views
    'TimesheetViewSet',

    # Authentication views
    'api_login',
    'api_logout',
    'api_user_profile',
    'api_csrf_token',

    # Tenant views
    'tenant_info_api',
    'available_tenants_api',
    'api_overview',
]