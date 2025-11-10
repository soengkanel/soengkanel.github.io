# views for dashboard
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from core.decorators import manager_or_admin_required
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib import admin
from django.apps import apps
from django.urls import reverse
from django.core.exceptions import PermissionDenied

# Import models from all apps
from hr.models import Department, Position, Employee, ProbationPeriod, IDCard
from user_management.models import UserRoleAssignment
from zone.models import Building, Floor, Zone, Worker, WorkerProbationPeriod
from cards.models import WorkerIDCard, CardPrintingHistory
from billing.models import Invoice, Service, InvoiceLineItem
from payments.models import Payment
from document_tracking.models import DocumentSubmission, DocumentType
from core.models import Notification
from audit_management.models import AuditSession, AuditTrail

def safe_count(queryset):
    """Safely get count from queryset, return 0 if table doesn't exist."""
    try:
        return queryset.count()
    except Exception:
        return 0

def safe_aggregate(queryset, aggregation):
    """Safely perform aggregation, return 0 if fails."""
    try:
        result = queryset.aggregate(aggregation)
        return result[list(result.keys())[0]] or 0
    except Exception:
        return 0

@login_required
def dashboard_home(request):
    """Comprehensive dashboard view with global system statistics and insights.

    This dashboard is restricted to staff and admin users only.
    Regular employees are redirected to the employee portal.
    """

    # Strict access control: Only staff and superusers can access this dashboard
    # Regular employees must use the employee portal
    if not (request.user.is_staff or request.user.is_superuser):
        # Check if user has any admin permissions
        has_admin_permission = (
            request.user.has_perm('hr.view_employee') or
            request.user.has_perm('dashboard.view_dashboard') or
            request.user.groups.filter(name__in=['Admin', 'Manager', 'HR']).exists()
        )

        if not has_admin_permission:
            return redirect('employee_portal:dashboard')

    # Date calculations for recent data
    today = timezone.now().date()
    this_week = today - timedelta(days=7)
    this_month = today - timedelta(days=30)

    # ============ CORE STATISTICS ============
    # People Management Statistics
    total_employees = safe_count(Employee.objects.all())
    active_employees = safe_count(Employee.objects.filter(employment_status='active'))
    total_workers = safe_count(Worker.objects.all())
    active_workers = safe_count(Worker.objects.filter(status='active'))
    total_vips = safe_count(Worker.objects.filter(is_vip=True))
    active_vips = safe_count(Worker.objects.filter(is_vip=True, status='active'))

    # Infrastructure Statistics
    total_buildings = safe_count(Building.objects.all())
    total_floors = safe_count(Floor.objects.all())
    total_zones = safe_count(Zone.objects.all())
    active_zones = safe_count(Zone.objects.filter(is_active=True))

    # Documents & Cards Statistics
    total_documents = safe_count(DocumentSubmission.objects.all())
    pending_documents = safe_count(DocumentSubmission.objects.filter(status='pending'))
    processed_documents = safe_count(DocumentSubmission.objects.filter(status='processed'))

    total_cards_printed = safe_count(CardPrintingHistory.objects.all())
    recent_cards = safe_count(CardPrintingHistory.objects.filter(created_at__gte=this_week))

    # Financial Statistics
    total_invoices = safe_count(Invoice.objects.all())
    total_revenue = safe_aggregate(Invoice.objects.filter(status='paid'), Sum('total_amount'))
    pending_invoices = safe_count(Invoice.objects.filter(status='pending'))
    pending_amount = safe_aggregate(Invoice.objects.filter(status='pending'), Sum('total_amount'))

    total_payments = safe_count(Payment.objects.all())
    total_payments_amount = safe_aggregate(Payment.objects.all(), Sum('amount'))

    # ============ RECENT ACTIVITY ============
    # Recent employees (last 7 days)
    recent_employees = Employee.objects.filter(
        created_at__gte=this_week
    ).order_by('-created_at')[:5]

    # Recent workers (last 7 days)
    recent_workers = Worker.objects.select_related('zone__created_by', 'building').filter(
        created_at__gte=this_week
    ).order_by('-created_at')[:5]

    # Recent VIPs (last 7 days)
    recent_vips = Worker.objects.filter(
        is_vip=True,
        created_at__gte=this_week
    ).select_related('zone', 'building').order_by('-created_at')[:5]

    # Recent document submissions
    recent_documents = DocumentSubmission.objects.filter(
        created_at__gte=this_week
    ).order_by('-created_at')[:5]

    # Recent invoices
    recent_invoices = Invoice.objects.filter(
        created_at__gte=this_week
    ).order_by('-created_at')[:5]

    # ============ ANALYTICAL DATA ============
    # Department distribution
    department_stats = []
    for dept in Department.objects.all()[:6]:
        employee_count = 0  # No longer have department relationship
        dept.employee_count = employee_count
        department_stats.append(dept)
    department_stats = sorted(department_stats, key=lambda x: x.employee_count, reverse=True)[:6]

    # Building occupancy
    building_stats = []
    for building in Building.objects.all()[:6]:
        worker_count = safe_count(Worker.objects.filter(building=building))
        # Building now belongs to one zone, not multiple zones
        zone_count = 1 if building.zone else 0
        building.worker_count = worker_count
        building.zone_count = zone_count
        building.total_occupancy = worker_count + zone_count
        building_stats.append(building)
    building_stats = sorted(building_stats, key=lambda x: x.total_occupancy, reverse=True)[:6]

    # Document types statistics - using choice field values
    document_type_stats = []
    if DocumentSubmission.objects.exists():
        document_type_counts = DocumentSubmission.objects.values('document_type').annotate(
            count=Count('id')
        ).order_by('-count')[:5]

        # Convert to objects with submission_count attribute for template compatibility
        for item in document_type_counts:
            doc_type_obj = type('DocumentTypeStat', (), {
                'name': dict(DocumentSubmission.DOCUMENT_TYPE_CHOICES).get(item['document_type'], item['document_type']),
                'submission_count': item['count'],
                'document_type': item['document_type']
            })()
            document_type_stats.append(doc_type_obj)

    # ============ STATUS DISTRIBUTIONS ============
    # Worker status distribution
    worker_status_stats = Worker.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count') if Worker.objects.exists() else []

    # VIP status distribution
    vip_type_stats = Worker.objects.filter(is_vip=True).values('status').annotate(
        count=Count('id')
    ).order_by('-count') if Worker.objects.filter(is_vip=True).exists() else []

    # Invoice status distribution
    invoice_status_stats = Invoice.objects.values('status').annotate(
        count=Count('id')
    ).order_by('-count') if Invoice.objects.exists() else []

    # ============ PROBATION TRACKING ============
    # Active probation periods (status is now tracked on Worker model)
    active_probations = safe_count(Worker.objects.filter(status__in=['probation', 'extended']))
    probations_ending_soon = safe_count(
        WorkerProbationPeriod.objects.filter(
            worker__status__in=['probation', 'extended'],
            original_end_date__lte=today + timedelta(days=7)
        )
    )

    # ============ NOTIFICATIONS & ALERTS ============
    unread_notifications = safe_count(Notification.objects.filter(is_read=False))
    recent_notifications = Notification.objects.filter(
        created_at__gte=this_week
    ).order_by('-created_at')[:5]

    # ============ SYSTEM HEALTH INDICATORS ============
    # Calculate system health metrics
    total_people = total_employees + total_workers + total_vips
    active_people = active_employees + active_workers + active_vips
    people_activity_rate = (active_people / total_people * 100) if total_people > 0 else 0

    document_processing_rate = (processed_documents / total_documents * 100) if total_documents > 0 else 0

    invoice_collection_rate = (safe_count(Invoice.objects.filter(status='paid')) / total_invoices * 100) if total_invoices > 0 else 0

    # ============ QUICK ACTIONS DATA ============
    quick_actions = [
        {
            'title': 'New Employee',
            'url': 'hr:employee_create',
            'icon': 'bi-person-plus',
            'color': 'primary',
            'description': 'Add new employee'
        },
        # {
        #     'title': 'New Entry',
        #     'url': 'zone:worker_create',
        #     'icon': 'bi-people',
        #     'color': 'success',
        #     'description': 'Register new worker'
        # },
        # {
        #     'title': 'Process Documents',
        #     'url': 'document_tracking:submission_list',
        #     'icon': 'bi-file-earmark',
        #     'color': 'info',
        #     'description': 'Review submissions'
        # },
        # {
        #     'title': 'Create Invoice',
        #     'url': 'billing:invoice_create',
        #     'icon': 'bi-receipt',
        #     'color': 'dark',
        #     'description': 'Generate invoice'
        # },
        # {
        #     'title': 'ID Cards',
        #     'url': 'cards:id_cards_dashboard',
        #     'icon': 'bi-card-text',
        #     'color': 'secondary',
        #     'description': 'Manage ID cards'
        # },
        # {
        #     'title': 'User Control',
        #     'url': 'user_management:user_list',
        #     'icon': 'bi-person-gear',
        #     'color': 'primary',
        #     'description': 'Manage users & roles'
        # }
    ]

    context = {
        # Core Statistics
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_workers': total_workers,
        'active_workers': active_workers,
        'total_vips': total_vips,
        'active_vips': active_vips,
        'total_buildings': total_buildings,
        'total_floors': total_floors,
        'total_zones': total_zones,
        'active_zones': active_zones,
        'total_documents': total_documents,
        'pending_documents': pending_documents,
        'processed_documents': processed_documents,
        'total_cards_printed': total_cards_printed,
        'recent_cards': recent_cards,
        'total_invoices': total_invoices,
        'total_revenue': total_revenue,
        'pending_invoices': pending_invoices,
        'pending_amount': pending_amount,
        'total_payments': total_payments,
        'total_payments_amount': total_payments_amount,

        # Recent Activity
        'recent_employees': recent_employees,
        'recent_workers': recent_workers,
        'recent_vips': recent_vips,
        'recent_documents': recent_documents,
        'recent_invoices': recent_invoices,

        # Analytical Data
        'department_stats': department_stats,
        'building_stats': building_stats,
        'document_type_stats': document_type_stats,
        'worker_status_stats': worker_status_stats,
        'vip_type_stats': vip_type_stats,
        'invoice_status_stats': invoice_status_stats,

        # Probation & Alerts
        'active_probations': active_probations,
        'probations_ending_soon': probations_ending_soon,
        'unread_notifications': unread_notifications,
        'recent_notifications': recent_notifications,

        # System Health
        'people_activity_rate': round(people_activity_rate, 1),
        'document_processing_rate': round(document_processing_rate, 1),
        'invoice_collection_rate': round(invoice_collection_rate, 1),

        # UI Data
        'quick_actions': quick_actions,
        'total_people': total_people,
        'active_people': active_people,
    }

    response = render(request, 'dashboard/home.html', context)
    response['Content-Type'] = 'text/html; charset=utf-8'
    return response

def get_model_icon(model_name, verbose_name):
    """Get specific icon for a model based on its name or verbose name"""

    # Model-specific icon mapping
    icon_map = {
        # HR Models
        'employee': 'bi-person-badge-fill',
        'employees': 'bi-person-badge-fill',
        'department': 'bi-diagram-2-fill',
        'departments': 'bi-diagram-2-fill',
        'position': 'bi-award-fill',
        'positions': 'bi-award-fill',
        'probation': 'bi-hourglass-split',
        'probationperiod': 'bi-hourglass-split',
        'onboarding': 'bi-person-plus-fill',
        'promotion': 'bi-arrow-up-circle-fill',
        'exit': 'bi-door-open-fill',

        # Payroll Models
        'salary': 'bi-cash',
        'tax': 'bi-percent',
        'taxslab': 'bi-percent',
        'payroll': 'bi-cash-stack',
        'payrollperiod': 'bi-calendar-range-fill',
        'salarycomponent': 'bi-puzzle-fill',
        'salarystructure': 'bi-diagram-3-fill',
        'advance': 'bi-arrow-up-square-fill',
        'loan': 'bi-bank2',
        'timesheet': 'bi-stopwatch-fill',
        'nssf': 'bi-shield-fill-plus',

        # Attendance Models
        'attendance': 'bi-calendar-check-fill',
        'workschedule': 'bi-calendar3',
        'biometric': 'bi-fingerprint',
        'biometricdevice': 'bi-fingerprint',
        'shift': 'bi-clock-history',

        # Leave Models
        'leave': 'bi-calendar-minus-fill',
        'holiday': 'bi-calendar-heart-fill',
        'leavetype': 'bi-tags-fill',
        'leavebalance': 'bi-speedometer2',

        # Project Models
        'project': 'bi-folder-fill',
        'task': 'bi-check2-square',
        'milestone': 'bi-flag-fill',
        'team': 'bi-people-fill',

        # Zone/Infrastructure Models
        'zone': 'bi-geo-alt-fill',
        'building': 'bi-building-fill',
        'floor': 'bi-layers-fill',
        'worker': 'bi-person-workspace',
        'workerposition': 'bi-briefcase-fill',
        'workerdepartment': 'bi-diagram-3',

        # Document Models
        'document': 'bi-file-earmark-text-fill',
        'submission': 'bi-upload',
        'documenttype': 'bi-file-earmark-medical-fill',
        'documentsubmission': 'bi-cloud-upload-fill',

        # Card Models
        'card': 'bi-credit-card-2-front-fill',
        'idcard': 'bi-person-vcard-fill',
        'printing': 'bi-printer-fill',
        'cardprinting': 'bi-printer-fill',

        # Billing Models
        'invoice': 'bi-receipt',
        'service': 'bi-wrench-adjustable-circle-fill',
        'billing': 'bi-receipt-cutoff',

        # Payment Models
        'payment': 'bi-credit-card-fill',
        'transaction': 'bi-arrow-left-right',

        # Expense Models
        'expense': 'bi-wallet-fill',
        'reimbursement': 'bi-cash-coin',

        # User Management Models
        'user': 'bi-person-fill',
        'group': 'bi-people',
        'permission': 'bi-key-fill',
        'role': 'bi-shield-check',
        'userrole': 'bi-person-gear',

        # Audit Models
        'audit': 'bi-search',
        'log': 'bi-journal-text',
        'trail': 'bi-footprints',
        'session': 'bi-clock-fill',

        # E-form Models
        'form': 'bi-form',
        'eform': 'bi-clipboard-data-fill',
        'extension': 'bi-calendar-plus-fill',
        'request': 'bi-envelope-paper-fill',

        # Company Models
        'company': 'bi-building-gear',
        'organization': 'bi-diagram-2-fill',
        'branch': 'bi-building-add',

        # Core Models
        'notification': 'bi-bell-fill',
        'setting': 'bi-gear-wide',
        'configuration': 'bi-sliders',
        'template': 'bi-file-earmark-code-fill',
    }

    # Check for exact matches first
    if model_name.lower() in icon_map:
        return icon_map[model_name.lower()]

    # Check verbose name
    for key in verbose_name.split():
        if key.lower() in icon_map:
            return icon_map[key.lower()]

    # Check for partial matches in model name
    for key, icon in icon_map.items():
        if key in model_name.lower():
            return icon

    # Check for partial matches in verbose name
    for key, icon in icon_map.items():
        if key in verbose_name.lower():
            return icon

    # Default fallback icon
    return 'bi-table'

def get_admin_models():
    """Get all registered admin models organized by app"""
    admin_models = {}

    # Define app display names and icons
    app_config = {
        'hr': {
            'name': 'Human Resources',
            'icon': 'bi-people-fill',
            'description': 'Employee management and HR operations'
        },
        'payroll': {
            'name': 'Payroll Management',
            'icon': 'bi-cash-stack',
            'description': 'Salary, taxes, and payroll processing'
        },
        'attendance': {
            'name': 'Time & Attendance',
            'icon': 'bi-clock-fill',
            'description': 'Time tracking and attendance management'
        },
        'leave': {
            'name': 'Leave Management',
            'icon': 'bi-calendar-x-fill',
            'description': 'Leave applications and approvals'
        },
        'billing': {
            'name': 'Billing & Invoicing',
            'icon': 'bi-receipt-cutoff',
            'description': 'Billing services and invoice management'
        },
        'payments': {
            'name': 'Payment Processing',
            'icon': 'bi-credit-card-fill',
            'description': 'Payment tracking and processing'
        },
        'expenses': {
            'name': 'Expense Management',
            'icon': 'bi-wallet2',
            'description': 'Employee expenses and reimbursements'
        },
        'project': {
            'name': 'Project Management',
            'icon': 'bi-kanban-fill',
            'description': 'Project tracking and management'
        },
        'zone': {
            'name': 'Zone & Infrastructure',
            'icon': 'bi-buildings-fill',
            'description': 'Buildings, zones, and worker management'
        },
        'cards': {
            'name': 'ID Card Management',
            'icon': 'bi-postcard-fill',
            'description': 'ID card creation and printing'
        },
        'document_tracking': {
            'name': 'Document Tracking',
            'icon': 'bi-folder2-open',
            'description': 'Document submission and tracking'
        },
        'eform': {
            'name': 'Electronic Forms',
            'icon': 'bi-clipboard2-pulse-fill',
            'description': 'Electronic form submissions'
        },
        'company': {
            'name': 'Company Management',
            'icon': 'bi-building-fill-gear',
            'description': 'Company profile and settings'
        },
        'user_management': {
            'name': 'User & Role Management',
            'icon': 'bi-person-fill-gear',
            'description': 'Users, roles, and permissions'
        },
        'audit_management': {
            'name': 'Audit & Compliance',
            'icon': 'bi-shield-fill-check',
            'description': 'System auditing and compliance'
        },
        'shift': {
            'name': 'Shift Management',
            'icon': 'bi-arrow-clockwise',
            'description': 'Work shifts and schedules'
        },
        'core': {
            'name': 'System Core',
            'icon': 'bi-gear-fill',
            'description': 'Core system settings and configurations'
        }
    }

    # Get all registered models from Django admin
    for model, model_admin in admin.site._registry.items():
        app_label = model._meta.app_label

        # Skip Django's built-in apps unless they're useful
        if app_label in ['auth', 'contenttypes', 'sessions', 'messages', 'staticfiles', 'admin']:
            continue

        # Skip external apps that might not be relevant
        if app_label in ['allauth', 'account', 'socialaccount']:
            continue

        if app_label not in admin_models:
            app_info = app_config.get(app_label, {
                'name': app_label.replace('_', ' ').title(),
                'icon': 'bi-gear',
                'description': f'{app_label.replace("_", " ").title()} management'
            })
            admin_models[app_label] = {
                'name': app_info['name'],
                'icon': app_info['icon'],
                'description': app_info['description'],
                'models': []
            }

        model_name = model._meta.verbose_name_plural.title()
        model_url = f'admin:{app_label}_{model._meta.model_name}_changelist'

        # Get specific icon for this model
        model_icon = get_model_icon(model._meta.model_name, model._meta.verbose_name_plural.lower())

        admin_models[app_label]['models'].append({
            'name': model_name,
            'description': f'Manage {model._meta.verbose_name_plural}',
            'url': model_url,
            'icon': model_icon,
            'module': app_label,
            'admin_url': True,
            'model_name': model._meta.model_name
        })

    # Sort models within each app
    for app_data in admin_models.values():
        app_data['models'].sort(key=lambda x: x['name'])

    return admin_models

@login_required
@manager_or_admin_required("Settings")
def settings_view(request):
    """Settings page with configuration and system settings only"""

    user = request.user

    # Get user's active role assignment if it exists
    try:
        role_assignment = UserRoleAssignment.objects.get(user=user, is_active=True)
    except UserRoleAssignment.DoesNotExist:
        role_assignment = None

    # Organize settings by functional modules
    settings_modules = {}

    # Add custom configuration views (using existing custom views, not Django admin)
    custom_modules = {
        'Company Settings': [
            {
                'name': 'Company Profile',
                'description': 'Edit company information and details',
                'url': 'company:current_company',
                'icon': 'bi-building-fill-gear',
                'module': 'company'
            }
        ],
        'HR Settings': [
            {
                'name': 'Departments',
                'description': 'Manage company departments',
                'url': 'hr:department_list',
                'icon': 'bi-diagram-2-fill',
                'module': 'hr'
            },
            {
                'name': 'Positions',
                'description': 'Manage employee positions',
                'url': 'hr:position_list',
                'icon': 'bi-award-fill',
                'module': 'hr'
            }
        ],
        'Payroll Settings': [
            {
                'name': 'Salary Components',
                'description': 'Manage salary earnings and deductions',
                'url': 'payroll:salary_component_list',
                'icon': 'bi-puzzle-fill',
                'module': 'payroll'
            },
            {
                'name': 'Tax Slabs',
                'description': 'Manage income tax slabs and rates',
                'url': 'payroll:tax_slab_list',
                'icon': 'bi-percent',
                'module': 'payroll'
            },
            {
                'name': 'NSSF Configuration',
                'description': 'Manage NSSF contribution settings',
                'url': 'payroll:nssf_config_list',
                'icon': 'bi-shield-fill-plus',
                'module': 'payroll'
            }
            # {
            #     'name': 'Salary Structures',
            #     'description': 'Manage salary structure templates',
            #     'url': 'payroll:salary_structure_list',
            #     'icon': 'bi-diagram-3-fill',
            #     'module': 'payroll'
            # }
        ],
        'Attendance Settings': [
            {
                'name': 'Biometric Devices',
                'description': 'Manage biometric attendance devices',
                'url': 'attendance:device_list',
                'icon': 'bi-fingerprint',
                'module': 'attendance'
            }
        ],
        'Leave Settings': [
            {
                'name': 'Leave Types',
                'description': 'Manage leave type configurations',
                'url': 'leave:type_list',
                'icon': 'bi-tags-fill',
                'module': 'leave'
            },
            {
                'name': 'Holidays',
                'description': 'Manage company holidays',
                'url': 'leave:holiday_list',
                'icon': 'bi-calendar-heart-fill',
                'module': 'leave'
            }
        ],
        # 'Infrastructure Settings': [
        #     {
        #         'name': 'Buildings',
        #         'description': 'Manage building information',
        #         'url': 'zone:building_list',
        #         'icon': 'bi-building-fill',
        #         'module': 'zone'
        #     },
        #     {
        #         'name': 'Floors',
        #         'description': 'Manage floor information',
        #         'url': 'zone:floor_list',
        #         'icon': 'bi-layers-fill',
        #         'module': 'zone'
        #     }
        # ],
        'Billing Settings': [
            {
                'name': 'Services',
                'description': 'Manage billable services',
                'url': 'billing:service_list',
                'icon': 'bi-wrench-adjustable-circle-fill',
                'module': 'billing'
            }
        ],
        'User Management': [
            {
                'name': 'Users',
                'description': 'Manage system users and accounts',
                'url': 'user_management:user_list',
                'icon': 'bi-people-fill',
                'module': 'user_management'
            },
            {
                'name': 'Roles',
                'description': 'Manage user roles and permissions',
                'url': 'user_management:role_list',
                'icon': 'bi-shield-check',
                'module': 'user_management'
            }
        ],
        'Policy Settings': [
            {
                'name': 'Policy Management',
                'description': 'Manage all HR and payroll policies',
                'url': 'policies:dashboard',
                'icon': 'bi-file-earmark-text-fill',
                'module': 'policy'
            }
        ]
    }

    # Add custom views to settings
    for module_name, items in custom_modules.items():
        if module_name not in settings_modules:
            settings_modules[module_name] = []
        settings_modules[module_name].extend(items)

    # Add system administration for privileged users
    if request.user.is_superuser or (role_assignment and role_assignment.role.name == "Manager"):
        if 'System Administration' not in settings_modules:
            settings_modules['System Administration'] = []

        settings_modules['System Administration'].extend([
            {
                'name': 'Audit Logs',
                'description': 'System audit logs and monitoring',
                'url': '/audit/',
                'icon': 'bi-shield-fill-exclamation',
                'direct_url': True,
                'module': 'system'
            }
        ])

        # Super admin panel (superuser only)
        if request.user.is_superuser:
            settings_modules['System Administration'].append({
                'name': 'Django Admin Panel',
                'description': 'Full Django administration interface',
                'url': '/admin/',
                'icon': 'bi-terminal-fill',
                'external': True,
                'module': 'system'
            })

    # Remove empty modules
    settings_modules = {k: v for k, v in settings_modules.items() if v}

    # Create flat list for search functionality
    all_items = []
    for module_items in settings_modules.values():
        all_items.extend(module_items)

    context = {
        'settings_items': all_items,
        'settings_modules': settings_modules,
        'role_assignment': role_assignment,
        'total_settings': len(all_items)
    }

    return render(request, 'dashboard/settings.html', context)