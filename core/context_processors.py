from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse, NoReverseMatch
from django.contrib.admin.sites import site
from django.utils import timezone
from datetime import timedelta
from django_tenants.utils import get_tenant_model
import logging
import time
import os

logger = logging.getLogger(__name__)


def user_role_context(request):
    """
    Context processor to provide user role information to all templates.
    """
    if not request.user.is_authenticated:
        return {
            'user_is_manager_or_admin': False,
            'user_role_name': None
        }
    
    # Check if user is superuser
    if request.user.is_superuser:
        return {
            'user_is_manager_or_admin': True,
            'user_role_name': 'Superuser'
        }
    
    # Check user's role assignment
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.get(
            user=request.user,
            is_active=True
        )
        is_manager_or_admin = role_assignment.role.name in ["Manager", "Admin"]
        return {
            'user_is_manager_or_admin': is_manager_or_admin,
            'user_role_name': role_assignment.role.name
        }
    except:
        return {
            'user_is_manager_or_admin': False,
            'user_role_name': None
        }


def tenant_context(request):
    """
    Context processor to provide tenant information to all templates.
    Makes tenant name and system title available globally.
    """
    try:
        # Skip during migrations and when database is not ready
        from django.db import connection
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 LIMIT 1")
        except:
            # Database not ready (during migrations, etc.)
            return {
                'tenant_name': 'LYP',
                'system_title': 'LYP',
                'tenant': None
            }
        
        if hasattr(request, 'tenant') and request.tenant:
            tenant_name = request.tenant.name
            system_title = f"{tenant_name}"
            return {
                'tenant_name': tenant_name,
                'system_title': system_title,
                'tenant': request.tenant
            }
        else:
            # Fallback for public schema or when no tenant is available
            return {
                'tenant_name': 'LYP',
                'system_title': 'LYP',
                'tenant': None
            }
    except Exception as e:
        return {
            'tenant_name': 'LYP',
            'system_title': 'LYP',
            'tenant': None
        }


def sidebar_menu(request):
    """
    Context processor to generate a simple, user-focused sidebar menu
    with essential features easily accessible.
    """
    if not request.user.is_authenticated:
        return {'sidebar_menu': None}
    
    # Skip during migrations and when database is not ready
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM auth_permission LIMIT 1")
    except:
        # Database not ready (during migrations, etc.)
        return {'sidebar_menu': None}
    
    menu_items = []

    # Check if user has "User" role (basic employee) or "Manager" role
    is_basic_user = False
    is_manager = False
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.get(
            user=request.user,
            is_active=True
        )
        if role_assignment.role.name == "User":
            is_basic_user = True
        elif role_assignment.role.name == "Manager":
            is_manager = True
    except:
        pass

    # MAIN SECTIONS (Core functionality - always visible)

    # 1. Operations (Daily tasks)
    operations_items = []
    operations_custom_items = [
        # {'name': 'Entry', 'icon': 'bi-person-plus', 'url_name': 'zone:worker_create', 'permission': 'zone.add_worker'},
        # {'name': 'Workers', 'icon': 'bi-person-gear', 'url': '/zone/workers/?search=&position=&zone=&building=&status=&worker_type=worker', 'permission': 'zone.view_worker'},
        # {'name': 'VIPs', 'icon': 'bi-star-fill', 'url': '/zone/workers/?search=&position=&zone=&building=&status=&worker_type=vip', 'permission': 'zone.view_worker'},
        # {'name': 'Probation', 'icon': 'bi-hourglass', 'url_name': 'zone:probation_list', 'permission': 'zone.view_workerprobationperiod'},
    ]
    
    # Add URLs for operations items (with permission checks)
    try:
        for custom_config in operations_custom_items:
            # Check permission if specified
            if 'permission' in custom_config:
                if not request.user.has_perm(custom_config['permission']):
                    continue  # Skip this item if user doesn't have permission

            if 'url_name' in custom_config:
                try:
                    custom_config['url'] = reverse(custom_config['url_name'])
                    operations_items.append(custom_config)
                except NoReverseMatch:
                    pass
            elif 'url' in custom_config:
                # Item already has a URL defined
                operations_items.append(custom_config)
        
        # Add active state detection for operations items
        for item in operations_items:
            item['is_active'] = False

            if 'url' in item:
                current_path = request.path
                current_params = request.GET

                # Parse the item URL to get path and parameters
                from urllib.parse import urlparse, parse_qs
                parsed_url = urlparse(item['url'])
                item_path = parsed_url.path

                # Check if paths match
                if current_path == item_path:
                    # For worker list pages, check specific parameters
                    if item_path.endswith('/workers/'):
                        worker_type_param = current_params.get('worker_type')
                        if worker_type_param:
                            worker_type_value = worker_type_param[0] if worker_type_param else ''
                        else:
                            worker_type_value = ''

                        # Match based on worker_type parameter
                        if item['name'] == 'Workers' and worker_type_value == 'worker':
                            item['is_active'] = True
                        elif item['name'] == 'VIPs' and worker_type_value == 'vip':
                            item['is_active'] = True
                        elif item['name'] == 'Workers' and (not worker_type_value or worker_type_value == ''):
                            # Default to Workers when no worker_type is specified
                            item['is_active'] = True
                    else:
                        # For other pages, simple path match is enough
                        item['is_active'] = True
                # Special case: highlight "Entry" when on worker create page
                elif item['name'] == 'Entry' and current_path.endswith('/workers/create/'):
                    item['is_active'] = True
        
        if operations_items:
            operations_section = {
                'name': 'Residence',
                'icon': 'bi-clipboard-check',
                'priority': 'main',
                'items': operations_items,
                'subsections': []
            }
            # Hide from basic users and managers
            if not is_basic_user and not is_manager:
                menu_items.append(operations_section)
    except:
        pass

    # 2. Talent Management (Unified HR, Recruitment & Lifecycle - Flat structure)
    talent_items = []
    talent_custom_items = [
        # Recruitment
        {'name': 'Job Postings', 'icon': 'bi-briefcase', 'url_name': 'recruitment:job_list', 'permission': 'recruitment.view_jobposting'},
        {'name': 'Candidates', 'icon': 'bi-file-earmark-person', 'url_name': 'recruitment:candidate_list', 'permission': 'recruitment.view_candidate'},
        {'name': 'Interviews', 'icon': 'bi-calendar-event', 'url_name': 'recruitment:candidate_list', 'url_param': '?status=interviewing', 'permission': 'recruitment.view_interview'},
        # Employee Lifecycle
        {'name': 'Onboarding', 'icon': 'bi-person-check', 'url_name': 'hr:onboarding_list', 'permission': 'hr.view_employeeonboarding'},
        {'name': 'Probation', 'icon': 'bi-hourglass-split', 'url_name': 'hr:probation_list', 'permission': 'hr.view_probationperiod'},
        {'name': 'Transitions', 'icon': 'bi-arrow-up-circle', 'url_name': 'hr:promotion_transfer_list', 'permission': 'hr.view_promotiontransfer'},
        {'name': 'Exit Interviews', 'icon': 'bi-door-open', 'url_name': 'hr:exit_interview_list', 'permission': 'hr.view_exitinterview'},
        # Core HR
        {'name': 'Employees', 'icon': 'bi-people', 'url_name': 'hr:employee_list', 'permission': 'hr.view_employee'},
        {'name': 'Documents', 'icon': 'bi-file-earmark-text', 'url_name': 'document_tracking:submission_list', 'permission': 'zone.view_document'},
        {'name': 'ID Cards', 'icon': 'bi-credit-card', 'url_name': 'cards:id_cards_dashboard', 'permission': 'hr.view_idcard'},
        {'name': 'E-Forms', 'icon': 'bi-list-check', 'url_name': 'eform:operations_dashboard', 'permission': 'eform.view_form'},
    ]

    # Add URLs for talent management items
    try:
        for custom_config in talent_custom_items:
            # Skip permission checks for managers on certain items
            if not is_manager:
                if 'permission' in custom_config and not request.user.has_perm(custom_config['permission']):
                    continue

            if 'url_name' in custom_config:
                try:
                    base_url = reverse(custom_config['url_name'])
                    custom_config['url'] = base_url + custom_config.get('url_param', '')
                    custom_config['is_active'] = False

                    current_path = request.path
                    current_full_path = request.get_full_path()

                    # Active state detection
                    if custom_config['name'] == 'Job Postings' and '/jobs/' in current_path:
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'Candidates' and '/candidates/' in current_path and 'status=' not in current_full_path:
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'Interviews' and '/candidates/' in current_path and 'status=interviewing' in current_full_path:
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'Onboarding' and '/onboarding/' in current_path:
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'Probation' and '/probation/' in current_path:
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'Transitions' and '/promotion-transfer/' in current_path:
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'Exit Interviews' and '/exit-' in current_path:
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'Employees' and current_path.startswith('/hr/employees/'):
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'Documents' and '/document' in current_path:
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'ID Cards' and '/cards/' in current_path:
                        custom_config['is_active'] = True
                    elif custom_config['name'] == 'E-Forms' and '/eform/' in current_path:
                        custom_config['is_active'] = True

                    talent_items.append(custom_config)
                except NoReverseMatch:
                    pass

        if talent_items:
            talent_section = {
                'name': 'Talent Management',
                'icon': 'bi-people-fill',
                'priority': 'main',
                'items': talent_items,
                'subsections': []
            }
            # Hide from basic users and managers
            if not is_basic_user and not is_manager:
                menu_items.append(talent_section)
    except:
        pass

    # 3. Attendance Management
    attendance_items = []
    attendance_custom_items = [
        # Keep only operational attendance items
        {'name': 'Dashboard', 'icon': 'bi-speedometer2', 'url_name': 'attendance:dashboard', 'permission': 'hr.view_employee'},
        {'name': 'Time Cards', 'icon': 'bi-check-circle', 'url_name': 'attendance:mark_attendance', 'permission': 'hr.view_employee'},
        {'name': 'Over Time Cards', 'icon': 'bi-clock-history', 'url_name': 'attendance:overtime_list', 'permission': 'hr.view_employee'},
        # {'name': 'Corrections', 'icon': 'bi-pencil-square', 'url_name': 'attendance:correction_list', 'permission': 'hr.view_employee'},
        # Moved to Reports section: Reports
        # Moved to Settings: Schedules, Devices, Holiday Calendar
    ]

    # Add URLs for attendance items (with permission checks)
    try:
        for custom_config in attendance_custom_items:
            # Skip permission checks for managers - they need access to attendance
            if not is_manager:
                # Check permission if specified (for non-managers)
                if 'permission' in custom_config:
                    if not request.user.has_perm(custom_config['permission']):
                        continue  # Skip this item if user doesn't have permission

            if 'url_name' in custom_config:
                try:
                    custom_config['url'] = reverse(custom_config['url_name'])
                    attendance_items.append(custom_config)
                except NoReverseMatch:
                    pass

        # Add active state detection for attendance items
        for item in attendance_items:
            item['is_active'] = False

            if 'url' in item:
                current_path = request.path

                # Check if current path starts with /attendance/
                if current_path.startswith('/attendance/'):
                    # More specific matching for attendance pages
                    if item['name'] == 'Dashboard' and current_path == '/attendance/':
                        item['is_active'] = True
                    elif item['name'] == 'Mark Attendance' and '/mark/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'OT Request' and '/overtime/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Corrections' and '/corrections/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Devices' and '/devices/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Reports' and '/reports/' in current_path:
                        item['is_active'] = True
                elif current_path == item['url']:
                    item['is_active'] = True

        # Add attendance section only if there are items
        if attendance_items:
            attendance_section = {
                'name': 'Time Cards',
                'icon': 'bi-person-check',
                'priority': 'main',
                'items': attendance_items,
                'subsections': []
            }
            # Show to managers and admins
            if not is_basic_user:
                menu_items.append(attendance_section)
    except:
        pass

    # 4. Projects
    projects_items = []
    projects_custom_items = [
        {'name': 'Dashboard', 'icon': 'bi-speedometer2', 'url_name': 'project:dashboard', 'permission': 'project.view_project'},
        {'name': 'Projects', 'icon': 'bi-kanban', 'url_name': 'project:project_list', 'permission': 'project.view_project'},
        {'name': 'Timesheets', 'icon': 'bi-list-task', 'url_name': 'project:timesheet_list', 'permission': 'project.view_timesheet'},
    ]

    # Add URLs for projects items
    try:
        for custom_config in projects_custom_items:
            # Check permission if specified
            if 'permission' in custom_config:
                if not request.user.has_perm(custom_config['permission']):
                    continue  # Skip this item if user doesn't have permission

            if 'url_name' in custom_config:
                try:
                    custom_config['url'] = reverse(custom_config['url_name'])
                    projects_items.append(custom_config)
                except NoReverseMatch:
                    pass  # Skip if URL name doesn't exist
        
        # Add active state detection for projects items
        for item in projects_items:
            item['is_active'] = False
            
            if 'url' in item:
                current_path = request.path
                
                # Check if current path starts with /project/
                if current_path.startswith('/project/'):
                    if item['name'] == 'Dashboard' and current_path == '/project/dashboard/':
                        item['is_active'] = True
                    elif item['name'] == 'Projects' and current_path != '/project/dashboard/' and '/timesheet' not in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Timesheets' and '/timesheet' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Teams' and '/teams/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Milestones' and '/milestones/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Create Project' and current_path.endswith('/create/'):
                        item['is_active'] = True
                elif current_path == item['url']:
                    item['is_active'] = True
        
        if projects_items:
            projects_section = {
                'name': 'Projects',
                'icon': 'bi-kanban',
                'priority': 'main',
                'items': projects_items,
                'subsections': []
            }
            # Hide from basic users and managers
            if not is_basic_user and not is_manager:
                menu_items.append(projects_section)
    except:
        pass

    # 5. Payroll
    payroll_items = []
    payroll_custom_items = [
        # Core Payroll Operations (keep only operational items)
        {'name': 'Dashboard', 'icon': 'bi-speedometer2', 'url_name': 'payroll:dashboard', 'permission': 'payroll.view_salary'},
        {'name': 'Process Payroll', 'icon': 'bi-play-circle', 'url_name': 'payroll:periods', 'permission': 'payroll.add_salary'},
        {'name': 'Structure', 'icon': 'bi-diagram-3', 'url_name': 'payroll:salary_structure_list', 'permission': 'payroll.view_salarystructure'},
        {'name': 'Assignment', 'icon': 'bi-person-badge', 'url_name': 'payroll:salary_structure_assignment_list', 'permission': 'payroll.view_salarystructureassignment'},
        {'name': 'Payslips', 'icon': 'bi-receipt', 'url_name': 'payroll:salary_list', 'permission': 'payroll.view_salary'},
        {'name': 'Salary Advances', 'icon': 'bi-cash-stack', 'url_name': 'payroll:advances_list', 'permission': 'payroll.view_salaryadvance'},
        {'name': 'Employee Loans', 'icon': 'bi-credit-card-2-front', 'url_name': 'payroll:loans_list', 'permission': 'payroll.view_employeeloan'},
        # Moved to Reports section: Payroll Reports
    ]

    # Add URLs for payroll items
    try:
        for custom_config in payroll_custom_items:
            # Check permission if specified
            if 'permission' in custom_config:
                if not request.user.has_perm(custom_config['permission']):
                    continue  # Skip this item if user doesn't have permission

            if 'url_name' in custom_config:
                try:
                    custom_config['url'] = reverse(custom_config['url_name'])
                    payroll_items.append(custom_config)
                except NoReverseMatch:
                    # Skip URLs that don't exist yet
                    pass

        # Add active state detection for payroll items
        for item in payroll_items:
            item['is_active'] = False

            if 'url' in item:
                current_path = request.path

                # More specific matching for payroll pages
                if current_path.startswith('/payroll/'):
                    if item['name'] == 'Dashboard' and current_path == '/payroll/':
                        item['is_active'] = True
                    elif item['name'] == 'Process Payroll' and '/periods/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Assignment' and '/salary-structure-assignment' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Structure' and '/salary-structure' in current_path and '/salary-structure-assignment' not in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Payslips' and '/salaries/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Salary Advances' and '/advances/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Employee Loans' and '/loans/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Payroll Reports' and '/reports/' in current_path:
                        item['is_active'] = True
                elif current_path == item['url']:
                    item['is_active'] = True

        if payroll_items:
            payroll_section = {
                'name': 'Payroll',
                'icon': 'bi-wallet2',
                'priority': 'main',
                'items': payroll_items,
                'subsections': []
            }
            # Hide from basic users and managers
            if not is_basic_user and not is_manager:
                menu_items.append(payroll_section)
    except:
        pass

    # 6. Leave Management
    leave_items = []
    leave_custom_items = [
        {'name': 'Dashboard', 'icon': 'bi-speedometer2', 'url_name': 'leave:dashboard', 'permission': 'leave.view_leaveapplication'},
        {'name': 'Applications', 'icon': 'bi-file-earmark-text', 'url_name': 'leave:application_list', 'permission': 'leave.view_leaveapplication'},
        {'name': 'Apply Leave', 'icon': 'bi-plus-circle', 'url_name': 'leave:application_create', 'permission': 'leave.add_leaveapplication'},
        {'name': 'Allocations', 'icon': 'bi-calendar2-range', 'url_name': 'leave:allocation_list', 'permission': 'leave.view_leaveallocation'},
        {'name': 'Leave Types', 'icon': 'bi-tag', 'url_name': 'leave:type_list', 'permission': 'leave.view_leavetype'},
        {'name': 'Holidays', 'icon': 'bi-calendar-event', 'url_name': 'leave:holiday_list', 'permission': 'leave.view_holiday'},
    ]

    # Add URLs for leave items
    try:
        for custom_config in leave_custom_items:
            # Skip permission checks for managers - they need access to approve leave
            if not is_manager:
                # Check permission if specified (for non-managers)
                if 'permission' in custom_config:
                    if not request.user.has_perm(custom_config['permission']):
                        continue  # Skip this item if user doesn't have permission

            if 'url_name' in custom_config:
                try:
                    custom_config['url'] = reverse(custom_config['url_name'])
                    leave_items.append(custom_config)
                except NoReverseMatch:
                    pass

        # Add active state detection for leave items
        for item in leave_items:
            item['is_active'] = False

            if 'url' in item:
                current_path = request.path

                # Check if current path starts with /leave/
                if current_path.startswith('/leave/'):
                    if item['name'] == 'Dashboard' and current_path == '/leave/':
                        item['is_active'] = True
                    elif item['name'] == 'Applications' and '/applications/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Apply Leave' and current_path.endswith('/applications/create/'):
                        item['is_active'] = True
                    elif item['name'] == 'Allocations' and '/allocations/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Leave Types' and '/types/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Holidays' and '/holidays/' in current_path:
                        item['is_active'] = True
                elif current_path == item['url']:
                    item['is_active'] = True

        if leave_items:
            leave_section = {
                'name': 'Leave Management',
                'icon': 'bi-calendar-x',
                'priority': 'main',
                'items': leave_items,
                'subsections': []
            }
            # Show to managers and admins
            if not is_basic_user:
                menu_items.append(leave_section)
    except:
        pass

    # 7. Employee Self-Service Portal (visible to all)
    employee_portal_items = []
    employee_portal_custom_items = [
        {'name': 'Attendance', 'icon': 'bi-calendar-check', 'url_name': 'employee_portal:attendance_list', 'permission': 'attendance.view_attendancerecord'},
        {'name': 'Leave', 'icon': 'bi-calendar-x', 'url_name': 'leave:application_list', 'permission': 'leave.view_leaveapplication'},
        {'name': 'Announcements', 'icon': 'bi-megaphone', 'url_name': 'announcements:announcement_list', 'permission': None},
        {'name': 'Overtime Claims', 'icon': 'bi-clock-history', 'url_name': 'employee_portal:overtime_claim_list', 'permission': 'hr.view_overtimeclaim'},
        {'name': 'Payslips', 'icon': 'bi-receipt', 'url_name': 'employee_portal:payslip_list', 'permission': 'payroll.view_salaryslip'},
        {'name': 'Performance & Goals', 'icon': 'bi-graph-up-arrow', 'url_name': 'employee_portal:performance', 'permission': None},
        {'name': 'Documents', 'icon': 'bi-file-earmark-text', 'url_name': 'employee_portal:document_list', 'permission': 'hr.view_employeedocument'},
        {'name': 'Request Forms', 'icon': 'bi-file-earmark-plus', 'url_name': 'eform:operations_dashboard', 'permission': None},
        {'name': 'Holiday Calendar', 'icon': 'bi-calendar-event', 'url_name': 'employee_portal:holiday_calendar', 'permission': None},
        {'name': 'Suggestion Box', 'icon': 'bi-lightbulb', 'url_name': 'suggestions:suggestion_list', 'permission': None},
    ]

    # Check if user has an active onboarding record
    has_active_onboarding = False
    try:
        from hr.models import Employee, EmployeeOnboarding
        if hasattr(request.user, 'employee'):
            employee = request.user.employee
            try:
                onboarding = EmployeeOnboarding.objects.get(employee=employee)
                # Only show if onboarding is not completed or cancelled and within first 90 days
                if onboarding.status not in ['completed', 'cancelled']:
                    days_since_joining = (timezone.now().date() - employee.hire_date).days if employee.hire_date else 999
                    if days_since_joining <= 90:
                        has_active_onboarding = True
            except EmployeeOnboarding.DoesNotExist:
                pass
    except:
        pass

    # Add "My Onboarding" item if employee has active onboarding
    if has_active_onboarding:
        employee_portal_custom_items.insert(0, {
            'name': 'My Onboarding',
            'icon': 'bi-rocket-takeoff',
            'url_name': 'employee_portal:onboarding_overview',
            'permission': None
        })

    try:
        for custom_config in employee_portal_custom_items:
            # Skip permission checks for managers - they should see their own portal
            if not is_manager:
                # Check permission if specified and not None
                if 'permission' in custom_config and custom_config['permission'] is not None:
                    if not request.user.has_perm(custom_config['permission']):
                        continue
            if 'url_name' in custom_config:
                try:
                    custom_config['url'] = reverse(custom_config['url_name'])
                    employee_portal_items.append(custom_config)
                except NoReverseMatch:
                    pass

        for item in employee_portal_items:
            item['is_active'] = False
            if 'url' in item:
                current_path = request.path
                if current_path.startswith('/employee/'):
                    if item['name'] == 'My Onboarding' and '/onboarding/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Attendance' and '/attendance/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Payslips' and '/payslips/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Documents' and '/documents/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Overtime Claims' and '/overtime/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Performance & Goals' and '/performance/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Holiday Calendar' and '/holidays/' in current_path:
                        item['is_active'] = True
                elif current_path.startswith('/eform/'):
                    if item['name'] == 'Request Forms':
                        item['is_active'] = True
                elif current_path.startswith('/leave/'):
                    if item['name'] == 'Leave':
                        item['is_active'] = True
                elif current_path.startswith('/announcements/'):
                    if item['name'] == 'Announcements':
                        item['is_active'] = True
                elif current_path.startswith('/suggestions/'):
                    if item['name'] == 'Suggestion Box':
                        item['is_active'] = True
                elif current_path == item['url']:
                    item['is_active'] = True

        if employee_portal_items:
            employee_portal_section = {
                'name': 'My Portal',
                'icon': 'bi-person-workspace',
                'priority': 'main',
                'items': employee_portal_items,
                'subsections': []
            }
            menu_items.append(employee_portal_section)
    except:
        pass

    # 8. Performance Management
    performance_items = []
    performance_custom_items = [
        {'name': 'Reviews', 'icon': 'bi-star', 'url_name': 'performance:review_list', 'permission': 'performance.view_performancereview'},
        {'name': 'Goals', 'icon': 'bi-bullseye', 'url_name': 'performance:goal_list', 'permission': 'performance.view_goal'},
    ]

    # Add URLs for performance items
    try:
        for custom_config in performance_custom_items:
            # Check permission if specified
            if 'permission' in custom_config:
                if not request.user.has_perm(custom_config['permission']):
                    continue  # Skip this item if user doesn't have permission

            if 'url_name' in custom_config:
                try:
                    custom_config['url'] = reverse(custom_config['url_name'])
                    performance_items.append(custom_config)
                except NoReverseMatch:
                    pass

        # Add active state detection for performance items
        for item in performance_items:
            item['is_active'] = False

            if 'url' in item:
                current_path = request.path

                # Check if current path starts with /performance/
                if current_path.startswith('/performance/'):
                    if item['name'] == 'Reviews' and '/reviews/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Goals' and '/goals/' in current_path:
                        item['is_active'] = True
                elif current_path == item['url']:
                    item['is_active'] = True

        if performance_items:
            performance_section = {
                'name': 'Performance',
                'icon': 'bi-graph-up-arrow',
                'priority': 'main',
                'items': performance_items,
                'subsections': []
            }
            # Hide from basic users and managers
            if not is_basic_user and not is_manager:
                menu_items.append(performance_section)
    except:
        pass

    # 9. Learning Management System (LMS) - Simplified
    lms_items = []

    # Simple flat menu structure - no subsections
    lms_menu_items = [
        {'name': 'My Learning', 'icon': 'bi-mortarboard', 'url_name': 'training:dashboard', 'permission': None},
        {'name': 'Courses', 'icon': 'bi-book', 'url_name': 'training:course_list', 'permission': None},
        {'name': 'Enrollments', 'icon': 'bi-person-check', 'url_name': 'training:enrollment_list', 'permission': 'training.view_courseenrollment', 'admin_only': True},
        {'name': 'Reports', 'icon': 'bi-graph-up', 'url_name': 'training:reports_overview', 'permission': 'training.view_courseenrollment', 'admin_only': True},
    ]

    # Add URLs for LMS items
    try:
        for custom_config in lms_menu_items:
            # Check if item is admin only
            if custom_config.get('admin_only', False):
                if is_basic_user or is_manager:
                    continue  # Skip admin-only items for basic users and managers

            # Check permission if specified
            if 'permission' in custom_config and custom_config['permission']:
                if not request.user.has_perm(custom_config['permission']):
                    continue

            if 'url_name' in custom_config:
                try:
                    custom_config['url'] = reverse(custom_config['url_name'])
                    lms_items.append(custom_config)
                except NoReverseMatch:
                    pass

        # Add active state detection for all items
        for item in lms_items:
            item['is_active'] = False

            if 'url' in item:
                current_path = request.path

                # Check if current path starts with /training/
                if current_path.startswith('/training/'):
                    if item['name'] == 'My Learning' and current_path == '/training/':
                        item['is_active'] = True
                    elif item['name'] == 'Courses' and '/courses/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Enrollments' and '/enrollments/' in current_path:
                        item['is_active'] = True
                    elif item['name'] == 'Reports' and '/reports/' in current_path:
                        item['is_active'] = True
                elif current_path == item['url']:
                    item['is_active'] = True

        if lms_items:
            lms_section = {
                'name': 'Learning',
                'icon': 'bi-mortarboard-fill',
                'priority': 'main',
                'items': lms_items,
                'subsections': []  # No subsections - flat structure
            }
            # Show to everyone (employees, managers, admins)
            menu_items.append(lms_section)
    except:
        pass

    # 10. Reports (Analytics)
    reports_items = []
    reports_custom_items = [
        {'name': 'HR Reports', 'icon': 'bi-people-fill', 'url_name': 'hr:reporting','permission': 'hr.view_worker'},
        # {'name': 'Worker', 'icon': 'bi-building', 'url_name': 'hr:worker_reports_dashboard', 'permission': 'zone.view_worker'},
        {'name': 'Time Cards', 'icon': 'bi-file-text', 'url_name': 'attendance:report', 'permission': 'hr.view_employee'},
        {'name': 'Over Time Cards', 'icon': 'bi-clock-history', 'url_name': 'attendance:overtime_report', 'permission': 'hr.view_employee'},
        {'name': 'Payroll', 'icon': 'bi-wallet2', 'url_name': 'payroll:reports'},
    ]
    
    # Add URLs for reports items

    try:
        for custom_config in reports_custom_items:
            # Skip permission checks for managers - they need access to reports
            if not is_manager:
                # Check permission if specified (for non-managers)
                if 'permission' in custom_config:
                    if not request.user.has_perm(custom_config['permission']):
                        continue  # Skip this item if user doesn't have permission

            if 'url_name' in custom_config:
                try:
                    custom_config['url'] = reverse(custom_config['url_name'])
                    reports_items.append(custom_config)
                except NoReverseMatch:
                    pass
        
        # Add active state detection for operations items
        for item in reports_items:
            item['is_active'] = False
            
            if 'url' in item:
                current_path = request.path
                
                # Simple path match for most operations items
                if current_path == item['url']:
                    item['is_active'] = True
                # Special case: highlight "Entry" when on worker create page
                elif item['name'] == 'Entry' and current_path.endswith('/workers/create/'):
                    item['is_active'] = True
        
        if reports_items:
            reports_section = {
                       'name': 'Reports',
                'icon': 'bi-graph-up',
                'priority': 'main',
                'items': reports_items,
                'subsections': []
            }
            # Show to managers and admins
            if not is_basic_user:
                menu_items.append(reports_section)
    except:
        pass
    
    # Master Data section removed - items are now available in the Settings page

    # 11. SETTINGS SECTION (Simplified single menu item)
    settings_items = []
    settings_custom_items = [
        {'name': 'Settings', 'icon': 'bi-gear', 'url_name': 'dashboard:settings'},
    ]
    
    try:
        # Check if user is manager or admin
        is_manager_or_admin = False
        if request.user.is_superuser:
            is_manager_or_admin = True
        else:
            try:
                from user_management.models import UserRoleAssignment
                role_assignment = UserRoleAssignment.objects.get(
                    user=request.user,
                    is_active=True
                )
                if role_assignment.role.name in ["Manager", "Admin"]:
                    is_manager_or_admin = True
            except:
                pass
        
        if not is_manager_or_admin:
            # Skip settings menu for non-manager/admin users
            settings_items = []
        else:
            for custom_config in settings_custom_items:
                if 'url_name' in custom_config:
                    try:
                        custom_config['url'] = reverse(custom_config['url_name'])
                        settings_items.append(custom_config)
                    except NoReverseMatch:
                        pass
        
        # Add active state detection for operations items
        for item in settings_items:
            item['is_active'] = False
            
            if 'url' in item:
                current_path = request.path
                
                # Simple path match for most operations items
                if current_path == item['url']:
                    item['is_active'] = True
                # Special case: highlight "Entry" when on worker create page
                elif item['name'] == 'Entry' and current_path.endswith('/workers/create/'):
                    item['is_active'] = True
        
        if settings_items:
            settings_section = {
                'name': 'Settings',
                'icon': 'bi-gear',
                'priority': 'main',
                'items': settings_items,
                'subsections': []
            }
            # Hide from basic users and managers (Admin only)
            if not is_basic_user and not is_manager:
                menu_items.append(settings_section)
    except:
        pass

    
    
    return {'sidebar_menu': menu_items}

def notifications_context(request):
    """Add user notifications to templates"""
    if not request.user.is_authenticated:
        return {}
    
    # Skip during migrations and when database is not ready
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 LIMIT 1")
    except:
        # Database not ready (during migrations, etc.)
        return {
            'user_notifications': [],
            'critical_notifications': [],
            'unread_notifications_count': 0,
            'notification_summary': {},
            'has_critical_notifications': False,
        }
    
    try:
        from core.models import Notification
        
        # Get unread notifications for the current user
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False,
            is_dismissed=False
        ).exclude(
            expires_at__lt=timezone.now()
        ).order_by('-created_at')[:10]
        
        # Get critical notifications (high priority, recent)
        critical_notifications = Notification.objects.filter(
            recipient=request.user,
            priority__in=['critical', 'high'],
            is_dismissed=False,
            created_at__gte=timezone.now() - timedelta(days=7)
        ).exclude(
            expires_at__lt=timezone.now()
        ).order_by('-created_at')[:5]
        
        # Count unread notifications
        unread_count = unread_notifications.count()
        
        # Get notification summary by type
        notification_summary = {}
        for notification in unread_notifications:
            notification_type = notification.notification_type
            if notification_type not in notification_summary:
                notification_summary[notification_type] = 0
            notification_summary[notification_type] += 1
        
        return {
            'user_notifications': unread_notifications,
            'critical_notifications': critical_notifications,
            'unread_notifications_count': unread_count,
            'notification_summary': notification_summary,
            'has_critical_notifications': critical_notifications.exists(),
        }
        
    except Exception as e:

        
        pass
        return {
            'user_notifications': [],
            'critical_notifications': [],
            'unread_notifications_count': 0,
            'notification_summary': {},
            'has_critical_notifications': False,
        }


def build_time_context(request):
    """Add build time information for dev environment identification"""
    try:
        # Get the server start time (approximation of build time)
        build_timestamp = time.time()
        build_time = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check environment settings
        from django.conf import settings
        is_dev = getattr(settings, 'DEV_ENV', False)
        show_footer = getattr(settings, 'SHOW_ENV_FOOTER', False)
        
        return {
            'build_time': build_time,
            'build_timestamp': build_timestamp,
            'is_dev_env': is_dev,
            'show_env_footer': show_footer,
            'env_name': 'Development' if is_dev else 'Production'
        }
    except Exception as e:
        return {
            'build_time': '',
            'build_timestamp': 0,
            'is_dev_env': False,
            'show_env_footer': False,
            'env_name': 'Unknown'
        }
