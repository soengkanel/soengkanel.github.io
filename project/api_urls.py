from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'project-types', api_views.ProjectTypeViewSet)
router.register(r'project-templates', api_views.ProjectTemplateViewSet)
router.register(r'projects', api_views.ProjectViewSet)
router.register(r'tasks', api_views.ProjectTaskViewSet)
router.register(r'team-members', api_views.ProjectTeamMemberViewSet)
router.register(r'timesheets', api_views.TimesheetViewSet)
router.register(r'timesheet-details', api_views.TimesheetDetailViewSet)
router.register(r'project-time-tracking', api_views.ProjectTimeTrackingViewSet)
router.register(r'activity-types', api_views.ActivityTypeMasterViewSet)
router.register(r'milestones', api_views.ProjectMilestoneViewSet)

app_name = 'project_api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),

    # Custom API endpoints
    path('dashboard/stats/', api_views.dashboard_stats, name='dashboard_stats'),

    # Timesheet system endpoints (ERPNext-style)
    path('reports/project-time/', api_views.project_time_report, name='project_time_report'),
    path('timesheets/bulk-operations/', api_views.timesheet_bulk_operations, name='timesheet_bulk_operations'),
    path('timesheets/stats/', api_views.timesheet_stats, name='timesheet_stats'),

    # Additional endpoints following the API structure document
    # These can be implemented as needed based on the API structure
]