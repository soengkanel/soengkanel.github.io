from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView
from . import views
from .swagger_ui import swagger_ui_view, swagger_ui_simple, swagger_ui_template, test_view
from .views import tenant_info_api, available_tenants_api, api_login, api_logout, api_user_profile, api_csrf_token
from hr.api_views import EmployeeViewSet, DepartmentViewSet, PositionViewSet, EmployeeDocumentViewSet
from company.api_views import CompanyViewSet, GroupViewSet

router = DefaultRouter()

# Project related endpoints
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'project-types', views.ProjectTypeViewSet, basename='project-type')
router.register(r'project-templates', views.ProjectTemplateViewSet, basename='project-template')
router.register(r'project-tasks', views.ProjectTaskViewSet, basename='project-task')
router.register(r'project-milestones', views.ProjectMilestoneViewSet, basename='project-milestone')
router.register(r'project-expenses', views.ProjectExpenseViewSet, basename='project-expense')

# Timesheet endpoints
router.register(r'timesheets', views.TimesheetViewSet, basename='timesheet')

# Team endpoints
router.register(r'teams', views.TeamViewSet, basename='team')
router.register(r'team-members', views.TeamMemberViewSet, basename='team-member')

# Company Management endpoints
router.register(r'company', CompanyViewSet, basename='company')
router.register(r'groups', GroupViewSet, basename='group')

# HR Management endpoints
router.register(r'employees', EmployeeViewSet, basename='employee')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'positions', PositionViewSet, basename='position')
router.register(r'employee-documents', EmployeeDocumentViewSet, basename='employee-document')

# Timecard Management endpoints
from hr.timecard_api_views import TimecardViewSet, TimecardEntryViewSet
router.register(r'timecards', TimecardViewSet, basename='timecard')
router.register(r'timecard-entries', TimecardEntryViewSet, basename='timecard-entry')

# Overtime Management endpoints
from hr.overtime_api_views import (
    OvertimePolicyViewSet, OvertimeClaimViewSet,
    OvertimeApprovalViewSet, OvertimeReportViewSet
)
router.register(r'overtime-policies', OvertimePolicyViewSet, basename='overtime-policy')
router.register(r'overtime-claims', OvertimeClaimViewSet, basename='overtime-claim')
router.register(r'overtime-approvals', OvertimeApprovalViewSet, basename='overtime-approval')
router.register(r'overtime-reports', OvertimeReportViewSet, basename='overtime-report')

# Payroll Management endpoints (existing app)
from payroll.api_views import (
    PayrollPeriodViewSet, SalaryComponentViewSet, SalaryStructureViewSet,
    EmployeeSalaryStructureViewSet, PayrollViewSet, SalaryAdvanceViewSet,
    EmployeeLoanViewSet, EmployeeSalaryViewSet
)

# Additional HR Payroll features
from hr.payroll_api_views import (
    PayrollPolicyViewSet as HRPayrollPolicyViewSet,
    PayrollUtilityViewSet as HRPayrollUtilityViewSet
)

# Leave Management endpoints
from leave.api_views import (
    LeaveTypeViewSet, LeaveApplicationViewSet, LeaveAllocationViewSet,
    HolidayViewSet, LeaveStatsViewSet
)

# Existing payroll endpoints
router.register(r'payroll/periods', PayrollPeriodViewSet, basename='payroll-period')
router.register(r'payroll/salary-components', SalaryComponentViewSet, basename='salary-component')
router.register(r'payroll/salary-structures', SalaryStructureViewSet, basename='salary-structure')
router.register(r'payroll/employee-salary-structures', EmployeeSalaryStructureViewSet, basename='employee-salary-structure')
router.register(r'payroll/payrolls', PayrollViewSet, basename='payroll')
router.register(r'payroll/salary-advances', SalaryAdvanceViewSet, basename='salary-advance')
router.register(r'payroll/employee-loans', EmployeeLoanViewSet, basename='employee-loan')
router.register(r'payroll/employee-salaries', EmployeeSalaryViewSet, basename='employee-salary')

# Additional HR Payroll endpoints
router.register(r'hr-payroll/policies', HRPayrollPolicyViewSet, basename='hr-payroll-policy')
router.register(r'hr-payroll/utilities', HRPayrollUtilityViewSet, basename='hr-payroll-utility')

# Leave Management router registrations
router.register(r'leave-types', LeaveTypeViewSet, basename='leave-type')
router.register(r'leave-applications', LeaveApplicationViewSet, basename='leave-application')
router.register(r'leave-allocations', LeaveAllocationViewSet, basename='leave-allocation')
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'leave-stats', LeaveStatsViewSet, basename='leave-stats')

# Attendance Management endpoints
from attendance.api_views import (
    BiometricDeviceViewSet, WorkScheduleViewSet, EmployeeScheduleViewSet,
    AttendanceRecordViewSet, BreakRecordViewSet, OvertimeRequestViewSet,
    AttendanceCorrectionViewSet, ActivityTypeViewSet, AttendanceStatsViewSet,
    TimesheetStatsViewSet, ProjectAttendanceViewSet
)

router.register(r'biometric-devices', BiometricDeviceViewSet, basename='biometric-device')
router.register(r'work-schedules', WorkScheduleViewSet, basename='work-schedule')
router.register(r'employee-schedules', EmployeeScheduleViewSet, basename='employee-schedule')
router.register(r'attendance-records', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'break-records', BreakRecordViewSet, basename='break-record')
router.register(r'overtime-requests', OvertimeRequestViewSet, basename='overtime-request')
router.register(r'attendance-corrections', AttendanceCorrectionViewSet, basename='attendance-correction')
router.register(r'project-attendance', ProjectAttendanceViewSet, basename='project-attendance')
router.register(r'activity-types', ActivityTypeViewSet, basename='activity-type')
router.register(r'attendance-stats', AttendanceStatsViewSet, basename='attendance-stats')
router.register(r'timesheet-stats', TimesheetStatsViewSet, basename='timesheet-stats')

urlpatterns = [
    # API Root - show available endpoints
    path('', include(router.urls)),

    # Authentication endpoints
    path('auth/login/', api_login, name='api-login'),
    path('auth/logout/', api_logout, name='api-logout'),
    path('auth/user/', api_user_profile, name='api-user-profile'),
    path('auth/csrf/', api_csrf_token, name='api-csrf-token'),

    # Tenant information endpoints
    path('tenant-info/', tenant_info_api, name='tenant-info'),
    path('available-tenants/', available_tenants_api, name='available-tenants'),

    # Test view to verify routing
    path('test/', test_view, name='test-view'),

    # Working Swagger UI (CDN-based)
    path('docs/', swagger_ui_view, name='swagger-ui'),
    path('swagger/', swagger_ui_template, name='swagger-template'),
    path('swagger-simple/', swagger_ui_simple, name='swagger-simple'),

    # Schema endpoint
    path('schema/', SpectacularAPIView.as_view(), name='api-schema'),

    # API Endpoints
    path('endpoints/', include(router.urls)),
]