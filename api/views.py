"""
Main API views module for NextHR.

This module has been refactored for better maintainability. The large monolithic
views.py file has been split into logical modules under the views/ package:

    pass
- views/project_views.py: Project-related views (Project, ProjectTask, ProjectMilestone, etc.)
- views/team_views.py: Team-related views (Team, TeamMember)
- views/timesheet_views.py: Timesheet-related views
- views/auth_views.py: Authentication views (login, logout, profile, etc.)
- views/tenant_views.py: Tenant management views
- mixins.py: Base mixins and utilities (TenantFilterMixin)

All views are imported here to maintain backward compatibility with existing code.
"""

# Import all views from the modular structure to maintain backward compatibility
from .views import *
from .mixins import TenantFilterMixin

# The old monolithic views.py has been refactored into smaller, focused modules.
# All existing functionality is preserved and accessible through the same imports.

# Legacy imports for backward compatibility - all views are now available
# from their respective modules under api.views.* but can still be imported
# from api.views as before.

# For new development, consider importing directly from the specific modules:
    pass
# from api.views.project_views import ProjectViewSet
# from api.views.auth_views import api_login
# etc.