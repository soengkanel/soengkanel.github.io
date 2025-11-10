# views for employees
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from core.decorators import manager_or_admin_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
import json
import os
import logging
from datetime import datetime, date
from core.encrypted_fields import FileEncryptionHandler

logger = logging.getLogger(__name__)

from .models import (
    Employee, Department, Position, EmployeeDocument, ProbationPeriod, ProbationExtension,
    EmployeeOnboarding, OnboardingTaskInstance, OnboardingTemplate,
    PromotionTransfer, ExitInterview, ExitChecklist
)
from .forms import (
    EmployeeForm, EmployeeSearchForm, EmployeeDocumentForm,
    DepartmentForm, PositionForm, get_employee_document_formset,
    OnboardingCreateForm, OnboardingTaskCompleteForm,
    PromotionTransferForm, PromotionTransferApprovalForm,
    ExitInterviewForm, ExitChecklistForm
)
from zone.models import Worker

@login_required
def hr_dashboard(request):
    """HR Dashboard with statistics and quick actions."""
    
    # Get HR statistics
    stats = {
        'total_employees': Employee.objects.count(),
        'active_employees': Employee.objects.filter(employment_status='active').count(),
        'on_leave_employees': Employee.objects.filter(employment_status='on_leave').count(),
        'total_departments': Department.objects.count(),
        'total_positions': Position.objects.count(),
    }
    
    # Get recent employees (last 5)
    recent_employees = Employee.objects.order_by('-created_at')[:5]
    
    # Get department statistics
    department_stats = []
    for dept in Department.objects.all()[:5]:
        employee_count = 0  # No department relationship anymore
        dept.employee_count = employee_count
        department_stats.append(dept)
    
    # Sort by employee count
    department_stats = sorted(department_stats, key=lambda x: x.employee_count, reverse=True)[:5]
    
    context = {
        'stats': stats,
        'recent_employees': recent_employees,
        'department_stats': department_stats,
    }
    
    return render(request, 'hr/hr_dashboard.html', context)

@login_required
@permission_required('hr.view_employee', raise_exception=True)
def employee_list(request):
    """List all employees with search, filter, and pagination."""
    
    # Get search form
    search_form = EmployeeSearchForm(request.GET)
    
    # Start with all employees - including ID card data for the new column
    employees = Employee.objects.prefetch_related('employee_id_cards').all()
    
    # Apply search filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        department = search_form.cleaned_data.get('department')
        employment_status = search_form.cleaned_data.get('employment_status')
        gender = search_form.cleaned_data.get('gender')
        
        if search_query:
            employees = employees.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(employee_id__icontains=search_query) |
                Q(email__icontains=search_query)
            )
            
        if department:
            employees = employees.filter(department=department)
            
        if employment_status:
            employees = employees.filter(employment_status=employment_status)
            
        if gender:
            employees = employees.filter(gender=gender)
    
    # Sorting
    sort_by = request.GET.get('sort', 'employee_id')
    order = request.GET.get('order', 'asc')
    
    valid_sort_fields = ['employee_id', 'first_name', 'last_name', 
                        'employment_status', 'hire_date', 'created_at']
    
    if sort_by in valid_sort_fields:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        employees = employees.order_by(sort_by)
    else:
        employees = employees.order_by('employee_id')
    
    # Pagination
    per_page = request.GET.get('per_page', '20')
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 25, 50, 100, 200]:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20
    
    paginator = Paginator(employees, per_page)
    page = request.GET.get('page')
    
    try:
        employees_page = paginator.page(page)
    except PageNotAnInteger:
        employees_page = paginator.page(1)
    except EmptyPage:
        employees_page = paginator.page(paginator.num_pages)
    
    # Calculate additional stats for template
    active_count = Employee.objects.filter(employment_status='active').count()
    departments_count = Department.objects.count()

    context = {
        'employees': employees_page,
        'search_form': search_form,
        'current_sort': request.GET.get('sort', 'employee_id'),
        'current_order': request.GET.get('order', 'asc'),
        'total_count': paginator.count,
        'per_page': per_page,
        'active_count': active_count,
        'departments_count': departments_count,
    }
    
    return render(request, 'hr/employee_list.html', context)

@login_required
@permission_required('hr.view_employee', raise_exception=True)
def employee_detail(request, pk):
    """Display detailed information about an employee."""
    employee = get_object_or_404(Employee, pk=pk)
    documents = employee.documents.all().order_by('-created_at')
    
    # Get audit logs for this employee
    from audit_management.models import AuditTrail
    from auditlog.models import LogEntry
    from django.contrib.contenttypes.models import ContentType
    from itertools import chain
    from operator import attrgetter
    
    # Initialize empty lists for audit logs
    audit_logs = []
    change_logs = []
    employee_history = []
    
    try:
        # Get AuditTrail logs
        audit_logs = list(AuditTrail.objects.filter(
            resource_type='employee',
            resource_id=str(pk)
        ).order_by('-timestamp')[:20])
    except Exception as e:
        pass  # Silently handle missing AuditTrail logs
    
    try:
        # Get django-auditlog LogEntry logs
        employee_content_type = ContentType.objects.get_for_model(Employee)
        change_logs = list(LogEntry.objects.filter(
            content_type=employee_content_type,
            object_pk=str(pk)
        ).order_by('-timestamp')[:20])
    except Exception as e:
        pass  # Silently handle missing LogEntry logs
    
    try:
        # Get employee history
        employee_history = list(employee.history.all().order_by('-date')[:20])
    except Exception as e:
        pass  # Silently handle missing employee history
    
    # Combine all logs and sort by timestamp/date
    all_logs = []
    
    # Add AuditTrail logs with type marker
    for log in audit_logs:
        log.log_type = 'audit_trail'
        log.sort_timestamp = log.timestamp
        all_logs.append(log)
    
    # Add LogEntry logs with type marker  
    for log in change_logs:
        log.log_type = 'change_log'
        log.sort_timestamp = log.timestamp
        
        # Filter out sensitive encrypted fields from display
        excluded_fields = [
            'phone_number', 'email', 'address', 'emergency_phone',
            'photo'  # Exclude photo field that changes every save due to encryption
        ]
        
        # Create filtered changes for display
        log.filtered_changes = {}
        if log.changes:
            for field, change in log.changes.items():
                if field not in excluded_fields:
                    log.filtered_changes[field] = change
        
        # Add method to get action display
        def get_action_display():
            action_map = {
                0: 'Created',
                1: 'Updated', 
                2: 'Deleted'
            }
            return action_map.get(log.action, 'Modified')
        
        log.get_action_display = get_action_display()
        all_logs.append(log)
    
    # Add EmployeeHistory logs with type marker
    for log in employee_history:
        log.log_type = 'employee_history'
        # Convert date to datetime for sorting
        from django.utils import timezone
        log.sort_timestamp = timezone.make_aware(
            timezone.datetime.combine(log.date, timezone.datetime.min.time())
        ) if log.date else timezone.now()
        all_logs.append(log)
    
    # Sort all logs by timestamp (newest first) and limit to 15
    all_logs.sort(key=lambda x: x.sort_timestamp, reverse=True)
    all_logs = all_logs[:15]
    
    context = {
        'employee': employee,
        'documents': documents,
        'today': date.today(),
        'all_logs': all_logs,
        'has_audit_logs': len(all_logs) > 0,
    }
    
    return render(request, 'hr/employee_detail.html', context)

@login_required
@permission_required('hr.add_employee', raise_exception=True)
def employee_create(request):
    """Create a new employee."""
    # Create document formset
    EmployeeDocumentFormSet = get_employee_document_formset()
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        formset = EmployeeDocumentFormSet(request.POST, request.FILES)
        
        if not form.is_valid():
            messages.error(request, 'Please correct the form errors below.')
        
        if not formset.is_valid():
            messages.error(request, 'Please correct the document errors below.')
        
        if form.is_valid() and formset.is_valid():
            try:
                # Create employee (user account is created in form.save())
                employee = form.save()

                # Provide feedback about user account creation
                if employee.user:
                    messages.success(request, _(f'Employee created successfully. User account created with username: {employee.user.username}'))
                else:
                    messages.success(request, _('Employee created successfully.'))

                # Save documents
                formset.instance = employee
                formset.save()

                return redirect('hr:employee_detail', pk=employee.pk)

            except Exception as e:


                pass
                messages.error(request, f'Error creating employee: {str(e)}')
    else:
        form = EmployeeForm()
        formset = EmployeeDocumentFormSet()
    
    context = {
        'form': form,
        'formset': formset,
        'title': 'Create Employee',
        'submit_text': 'Create Employee'
    }
    
    return render(request, 'hr/employee_form.html', context)

@login_required
@permission_required('hr.change_employee', raise_exception=True)
def employee_update(request, pk):
    """Update an existing employee."""
    employee = get_object_or_404(Employee, pk=pk)
    
    # Create document formset
    EmployeeDocumentFormSet = get_employee_document_formset()
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        formset = EmployeeDocumentFormSet(request.POST, request.FILES, instance=employee)
        
        if form.is_valid() and formset.is_valid():
            try:
                # Check if employee had a user before update
                had_user_before = employee.user is not None

                # Update employee
                employee = form.save()

                # Provide feedback about user account updates
                if not had_user_before and employee.user:
                    # User account was just created for existing employee
                    messages.success(request, _(f'Employee updated successfully. User account created with username: {employee.user.username}'))
                elif employee.user and form.cleaned_data.get('new_password'):
                    messages.success(request, _('Employee and user account updated successfully. Password has been changed.'))
                elif employee.user:
                    messages.success(request, _('Employee and user account updated successfully.'))
                else:
                    messages.success(request, _('Employee updated successfully.'))

                # Save documents
                formset.save()

                return redirect('hr:employee_detail', pk=employee.pk)
                
            except Exception as e:

                
                pass
                messages.error(request, f'Error updating employee: {str(e)}')
    else:
        form = EmployeeForm(instance=employee)
        formset = EmployeeDocumentFormSet(instance=employee)
    
    context = {
        'form': form,
        'formset': formset,
        'employee': employee,
        'title': f'Update Employee - {employee.full_name}',
        'submit_text': 'Update Employee'
    }
    
    return render(request, 'hr/employee_form.html', context)

@login_required
@permission_required('hr.delete_employee', raise_exception=True)
def employee_delete(request, pk):
    """Delete an employee."""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        try:
            employee.delete()
            messages.success(request, _('Employee deleted successfully.'))
            return redirect('hr:employee_list')
        except Exception as e:
            messages.error(request, f'Error deleting employee: {str(e)}')
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'hr/employee_confirm_delete.html', context)

@login_required
def get_positions_by_department(request):
    """AJAX view to get positions by department. (Department-Position relationship removed)"""
    # Since we removed the department-position relationship, always return empty list
    return JsonResponse({'positions': []})


# Document management views
@login_required
def employee_document_create(request, employee_pk):
    """Create a new document for an employee."""
    employee = get_object_or_404(Employee, pk=employee_pk)
    
    if request.method == 'POST':
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.employee = employee
            document.created_by = request.user
            document.save()
            
            messages.success(request, _('Document added successfully.'))
            return redirect('hr:employee_detail', pk=employee.pk)
    else:
        form = EmployeeDocumentForm()
    
    context = {
        'form': form,
        'employee': employee,
        'title': f'Add Document - {employee.full_name}'
    }
    
    return render(request, 'hr/document_form.html', context)

@login_required
def employee_document_delete(request, employee_pk, document_pk):
    """Delete an employee document."""
    employee = get_object_or_404(Employee, pk=employee_pk)
    document = get_object_or_404(EmployeeDocument, pk=document_pk, employee=employee)
    
    if request.method == 'POST':
        document.delete()
        messages.success(request, _('Document deleted successfully.'))
        return redirect('hr:employee_detail', pk=employee.pk)
    
    context = {
        'employee': employee,
        'document': document,
    }
    
    return render(request, 'hr/document_delete.html', context)

# ============================================================================
# DEPARTMENT VIEWS
# ============================================================================

@login_required
# @permission_required('hr.view_department', raise_exception=True)
@manager_or_admin_required("Department Management")
def department_list(request):
    """List all departments with search and pagination."""
    departments = Department.objects.select_related('parent').prefetch_related('children')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        departments = departments.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
        # Pagination
    per_page = request.GET.get('per_page', '20')
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 25, 50, 100, 200]:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20
    
    paginator = Paginator(departments, per_page)
    page = request.GET.get('page')
    try:
        departments = paginator.page(page)
    except PageNotAnInteger:
        departments = paginator.page(1)
    except EmptyPage:
        departments = paginator.page(paginator.num_pages)

    context = {
        'departments': departments,
        'search_query': search_query,
        'per_page': per_page,
    }
    return render(request, 'hr/department_list.html', context)

@login_required
@manager_or_admin_required("Department Management")
def department_detail(request, pk):
    """View department details."""
    department = get_object_or_404(Department, pk=pk)
    positions = department.positions.all()
    employees = []  # No department relationship anymore
    
    context = {
        'department': department,
        'positions': positions,
        'employees': employees,
    }
    return render(request, 'hr/department_detail.html', context)

@login_required
@manager_or_admin_required("Department Management")
def department_create(request):
    """Create a new department."""
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            department = form.save(commit=False)
            department.created_by = request.user
            department.save()
            messages.success(request, _('Department created successfully.'))
            return redirect('hr:department_detail', pk=department.pk)
    else:
        form = DepartmentForm()
    
    context = {'form': form}
    return render(request, 'hr/department_form.html', context)

@login_required
@manager_or_admin_required("Department Management")
def department_edit(request, pk):
    """Edit an existing department."""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, _('Department updated successfully.'))
            return redirect('hr:department_detail', pk=department.pk)
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'department': department,
    }
    return render(request, 'hr/department_form.html', context)

@login_required
@manager_or_admin_required("Department Management")
def department_delete(request, pk):
    """Delete a department with cascade delete."""
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        try:
            department_name = department.name
            department.delete()
            messages.success(request, _(f'Department "{department_name}" deleted successfully.'))
            return redirect('hr:department_list')
        except Exception as e:
            messages.error(request, _(f'Error deleting department: {str(e)}'))
            return redirect('hr:department_delete', pk=pk)
    
    # Get related objects count for display
    employees_count = 0  # No department relationship anymore
    positions_count = Position.objects.filter(department=department).count()
    
    context = {
        'department': department,
        'employees_count': employees_count,
        'positions_count': positions_count,
    }
    return render(request, 'hr/department_delete.html', context)

# ============================================================================
# POSITION VIEWS
# ============================================================================

@login_required
@manager_or_admin_required("Department Management")
def position_list(request):
    """List all positions with search and pagination."""
    positions = Position.objects.select_related('department')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    
    if search_query:
        positions = positions.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if department_filter:
        positions = positions.filter(department_id=department_filter)
    
        # Pagination
    per_page = request.GET.get('per_page', '20')
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 25, 50, 100, 200]:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20
    
    paginator = Paginator(positions, per_page)
    page = request.GET.get('page')
    try:
        positions = paginator.page(page)
    except PageNotAnInteger:
        positions = paginator.page(1)
    except EmptyPage:
        positions = paginator.page(paginator.num_pages)

    departments = Department.objects.all()

    context = {
        'positions': positions,
        'departments': departments,
        'search_query': search_query,
        'department_filter': department_filter,
        'per_page': per_page,
    }
    return render(request, 'hr/position_list.html', context)

@login_required
@manager_or_admin_required("Department Management")
def position_detail(request, pk):
    """View position details."""
    position = get_object_or_404(Position, pk=pk)
    employees = []  # No position relationship anymore
    
    # Workers belong to the agent app and use a different Position model
    # We'll try to find workers with positions that have the same name and code
    workers = Worker.objects.filter(
        position__name=position.name,
        position__code=position.code
    )
    
    context = {
        'position': position,
        'employees': employees,
        'workers': workers,
    }
    return render(request, 'hr/position_detail.html', context)


@login_required
@permission_required('zone.view_worker', raise_exception=True)
def worker_reports_dashboard(request):
    """Worker Reports Dashboard - Main grid page."""
    from zone.models import Worker, Building
    from datetime import datetime
    import calendar
    
    # Get current date info
    current_date = datetime.now()
    years = list(range(current_date.year - 5, current_date.year + 2))
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    buildings = Building.objects.filter(is_active=True).order_by('name')
    
    # Get summary statistics
    total_workers = Worker.objects.filter(status='active').count()
    total_employees = Employee.objects.filter(employment_status='active').count()
    total_buildings = buildings.count()
    
    # Get worker count by nationality for foreign/khmer split
    foreign_workers = Worker.objects.filter(status='active').exclude(nationality='KH').count()
    khmer_workers = Worker.objects.filter(status='active', nationality='KH').count()
    
    context = {
        'years': years,
        'months': months,
        'buildings': buildings,
        'current_year': current_date.year,
        'current_month': current_date.month,
        'stats': {
            'total_workers': total_workers,
            'total_employees': total_employees,
            'total_buildings': total_buildings,
            'foreign_workers': foreign_workers,
            'khmer_workers': khmer_workers,
        }
    }
    
    return render(request, 'hr/worker_reports_dashboard.html', context)


@login_required
@permission_required('zone.view_worker', raise_exception=True)
def foreign_khmer_report(request):
    """Foreign and Khmer Worker Report by Building with Date, Zone, Building, and Floor Filters."""
    from zone.models import Worker, Building, Zone, Floor
    from datetime import datetime
    import calendar
    
    # Get filter parameters
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    zone_id = request.GET.get('zone', '')
    building_id = request.GET.get('building', '')
    floor_id = request.GET.get('floor', '')
    
    # Build filter conditions for buildings query
    building_filters = {'is_active': True}
    if zone_id:
        building_filters['zone_id'] = zone_id
    
    # Get all buildings or filter by specific building
    if building_id:
        buildings = Building.objects.filter(id=building_id, is_active=True)
        is_filtered_building = True
        filtered_building = buildings.first()
    else:
        buildings = Building.objects.filter(**building_filters).order_by('name')
        is_filtered_building = False
        filtered_building = None
    
    # Build base worker query with date filtering (by hire date)
    from datetime import datetime, date
    from calendar import monthrange
    
    # Create date range for the selected month/year
    start_date = date(year, month, 1)
    # Get last day of the month
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    # Filter workers by hire date (date_joined) in the selected month/year
    base_worker_query = Worker.objects.filter(
        date_joined__gte=start_date,
        date_joined__lte=end_date
    )
    
    # Add additional filters if specified
    if zone_id:
        base_worker_query = base_worker_query.filter(zone_id=zone_id)
    if floor_id:
        base_worker_query = base_worker_query.filter(floor_id=floor_id)
    
    # Generate report data
    building_data = []
    total_foreign_khmer = 0
    total_foreign = 0
    total_khmer = 0
    
    for building in buildings:
        # Count foreign and khmer workers in this building with the status filter
        foreign_workers = base_worker_query.filter(
            building=building
        ).exclude(nationality='KH').count()
        
        khmer_workers = base_worker_query.filter(
            building=building,
            nationality='KH'
        ).count()
        
        total_building = foreign_workers + khmer_workers
        
        building_data.append({
            'building': building,
            'foreign_workers': foreign_workers,
            'khmer_workers': khmer_workers,
            'total': total_building
        })
        total_foreign_khmer += total_building
        total_foreign += foreign_workers
        total_khmer += khmer_workers
    
    month_name = calendar.month_name[month]
    
    # Get available years, months, zones, buildings, and floors for filters
    current_date = datetime.now()
    years = list(range(current_date.year - 5, current_date.year + 2))
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    all_zones = Zone.objects.filter(is_active=True).order_by('name')
    all_buildings = Building.objects.filter(is_active=True).order_by('name')
    all_floors = Floor.objects.filter(is_active=True).select_related('building').order_by('building__name', 'floor_number')
    
    # Filter buildings and floors based on selected zone/building
    if zone_id:
        filtered_buildings = Building.objects.filter(zone_id=zone_id, is_active=True).order_by('name')
        filtered_floors = Floor.objects.filter(building__zone_id=zone_id, is_active=True).select_related('building').order_by('building__name', 'floor_number')
    else:
        filtered_buildings = all_buildings
        filtered_floors = all_floors
    
    if building_id:
        filtered_floors = Floor.objects.filter(building_id=building_id, is_active=True).order_by('floor_number')

    
    context = {
        'building_data': building_data,
        'total_foreign_khmer': total_foreign_khmer,
        'total_foreign': total_foreign,
        'total_khmer': total_khmer,
        'year': year,
        'month': month,
        'month_name': month_name,
        'report_date': f"{month_name.upper()}-{year}",
        'start_date': start_date,
        'end_date': end_date,
        'is_filtered_building': is_filtered_building,
        'filtered_building': filtered_building,
        'years': years,
        'months': months,
        'zones': all_zones,
        'buildings': all_buildings,
        'floors': all_floors,
        'filtered_buildings': filtered_buildings,
        'filtered_floors': filtered_floors,
        'selected_zone': zone_id,
        'selected_building': building_id,
        'selected_floor': floor_id,
    }
    
    return render(request, 'hr/foreign_khmer_report.html', context)


@login_required
def get_buildings_by_zone(request):
    """API endpoint to get buildings filtered by zone."""
    from django.http import JsonResponse
    from zone.models import Building
    
    zone_id = request.GET.get('zone_id')
    if zone_id:
        buildings = Building.objects.filter(zone_id=zone_id, is_active=True).order_by('name')
    else:
        buildings = Building.objects.filter(is_active=True).order_by('name')
    
    building_list = [{'id': b.id, 'name': b.name} for b in buildings]
    return JsonResponse({'buildings': building_list})


@login_required  
def get_floors_by_building(request):
    """API endpoint to get floors filtered by building."""
    from django.http import JsonResponse
    from zone.models import Floor
    
    building_id = request.GET.get('building_id')
    if building_id:
        floors = Floor.objects.filter(building_id=building_id, is_active=True).order_by('floor_number')
    else:
        floors = Floor.objects.filter(is_active=True).select_related('building').order_by('building__name', 'floor_number')
    
    floor_list = [{'id': f.id, 'name': f.name, 'building_name': f.building.name} for f in floors]
    return JsonResponse({'floors': floor_list})


@login_required
@permission_required('zone.view_worker', raise_exception=True)
def staff_report(request):
    """Staff Report with Employee Categories by Building with Zone, Building, and Floor Filters."""
    from zone.models import Building, Worker, Zone, Floor
    from datetime import datetime, date
    import calendar
    from django.db.models import Count, Q
    from calendar import monthrange
    
    # Get filter parameters
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    zone_id = request.GET.get('zone', '')
    building_id = request.GET.get('building', '')
    floor_id = request.GET.get('floor', '')
    
    # Create date range for the selected month/year
    start_date = date(year, month, 1)
    # Get last day of the month
    last_day = monthrange(year, month)[1]
    end_date = date(year, month, last_day)
    
    # Debug logging
    if settings.DEBUG:
        pass

    # Control whether to apply date filtering
    # Set to False to show all workers regardless of month/year
    # TEMPORARY: Disable date filter to test if that's the issue
    APPLY_DATE_FILTER = False

    # Start with all workers with related data
    workers_query = Worker.objects.select_related('position', 'zone', 'building', 'floor')

    if APPLY_DATE_FILTER:
        # Apply date filter - workers who joined before or during the selected month
        workers_query = workers_query.filter(
            date_joined__lte=end_date  # Joined before end of selected month
        )

        # For terminated workers, only include if they were terminated after the start of the month
        workers_query = workers_query.filter(
            Q(status='active') |
            Q(status='on_leave') |
            Q(status='extended') |
            Q(status='probation') |
            Q(status='passed') |
            Q(status='inactive') |
            Q(status='terminated', updated_at__gte=start_date) |  # Terminated during or after the month
            Q(status='terminated', updated_at__isnull=True)  # Or no termination date recorded
        )
    else:
        # No date filter - show all workers with these statuses
        workers_query = workers_query.filter(
            Q(status='active') |
            Q(status='on_leave') |
            Q(status='extended') |
            Q(status='probation') |
            Q(status='passed') |
            Q(status='inactive') |
            Q(status='terminated')
        )

    # Apply zone filter
    if zone_id:
        workers_query = workers_query.filter(zone_id=zone_id)

    # Apply building filter
    if building_id:
        try:
            building = Building.objects.get(id=building_id)
            is_filtered_building = True
            workers_query = workers_query.filter(building_id=building_id)
        except Building.DoesNotExist:
            building = None
            is_filtered_building = False
    else:
        building = None
        is_filtered_building = False

    # Apply floor filter
    if floor_id:
        workers_query = workers_query.filter(floor_id=floor_id)
    
    # Create building object for template display
    if not building:
        from collections import namedtuple
        BuildingObj = namedtuple('Building', ['name'])
        
        # Create appropriate display name based on filters applied
        try:
            if zone_id and floor_id:
                # Zone and floor selected but no specific building
                zone_name = Zone.objects.get(id=zone_id).name
                floor_obj = Floor.objects.select_related('building').get(id=floor_id)
                building = BuildingObj(name=f"Zone {zone_name} - {floor_obj.building.name} - {floor_obj.name}")
            elif zone_id:
                # Only zone selected
                zone_name = Zone.objects.get(id=zone_id).name
                building = BuildingObj(name=f"Zone {zone_name} - All Buildings")
            elif floor_id:
                # Only floor selected
                floor_obj = Floor.objects.select_related('building').get(id=floor_id)
                building = BuildingObj(name=f"{floor_obj.building.name} - {floor_obj.name}")
            else:
                # No filters applied
                building = BuildingObj(name="All Buildings")
        except (Zone.DoesNotExist, Floor.DoesNotExist):
            # Fallback if invalid IDs are provided
            building = BuildingObj(name="All Buildings")
    
    # Map position names to staff categories (case-insensitive matching)
    position_mapping = {
        'Staff Online': ['staff online', 'senior online staff', 'online staff', 'online', 'staff_online'],
        'Staff Cleaner': ['staff cleaner', 'housekeeping supervisor', 'cleaner', 'housekeeping', 'staff_cleaner', 'cleaning staff'],
        'Staff Bodyguard': ['staff bodyguard', 'security guard', 'bodyguard', 'security', 'staff_bodyguard', 'security officer'],
        'Driver': ['driver', 'senior driver', 'chauffeur', 'driver staff'],
        'Translator': ['translator', 'interpreter', 'translation staff'],
        'Staff Canteen': ['staff canteen', 'cook', 'canteen', 'kitchen staff', 'chef', 'staff_canteen', 'food service']
    }

    # Optional debug output - comment out in production
    if settings.DEBUG:
        all_positions = set(workers_query.exclude(position__isnull=True).values_list('position__name', flat=True).distinct())

    # Generate staff categories data from real database
    staff_categories = []

    for category_name, position_names in position_mapping.items():
        # Create regex pattern for case-insensitive partial matching
        pattern = '|'.join([f'.*{name}.*' for name in position_names])

        # Count workers in this category (case-insensitive partial matching)
        category_workers = workers_query.filter(
            position__name__iregex=pattern
        )

        male_count = category_workers.filter(sex='M').count()
        female_count = category_workers.filter(sex='F').count()
        total_count = male_count + female_count

        staff_categories.append({
            'name': category_name.upper(),
            'male': male_count,
            'female': female_count,
            'total': total_count,
            'status': 'P'
        })
    
    # Add "Other Staff" category for workers not in specific categories
    categorized_worker_ids = set()
    for category_name, position_names in position_mapping.items():
        # Use the same pattern matching as above
        pattern = '|'.join([f'.*{name}.*' for name in position_names])
        category_workers = workers_query.filter(
            position__name__iregex=pattern
        )
        categorized_worker_ids.update(category_workers.values_list('id', flat=True))

    # Find uncategorized workers (excluding those without position)
    other_workers = workers_query.exclude(id__in=categorized_worker_ids).exclude(position__isnull=True)
    other_male = other_workers.filter(sex='M').count()
    other_female = other_workers.filter(sex='F').count()
    other_total = other_male + other_female

    if other_total > 0:
        staff_categories.append({
            'name': 'OTHER STAFF',
            'male': other_male,
            'female': other_female,
            'total': other_total,
            'status': 'P'
        })

    # Also check for workers without any position
    no_position_workers = workers_query.filter(position__isnull=True)
    no_pos_male = no_position_workers.filter(sex='M').count()
    no_pos_female = no_position_workers.filter(sex='F').count()
    no_pos_total = no_pos_male + no_pos_female

    if no_pos_total > 0:
        staff_categories.append({
            'name': 'UNASSIGNED',
            'male': no_pos_male,
            'female': no_pos_female,
            'total': no_pos_total,
            'status': 'P'
        })
    
    # If no categories have data, show all workers as "All Staff"
    if not any(cat['total'] > 0 for cat in staff_categories):
        all_male = workers_query.filter(sex='M').count()
        all_female = workers_query.filter(sex='F').count()
        all_total = all_male + all_female

        if all_total > 0:
            staff_categories = [{
                'name': 'ALL STAFF',
                'male': all_male,
                'female': all_female,
                'total': all_total,
                'status': 'P'
            }]

    # Calculate totals
    total_male = sum(cat['male'] for cat in staff_categories)
    total_female = sum(cat['female'] for cat in staff_categories)
    grand_total = sum(cat['total'] for cat in staff_categories)
    
    month_name = calendar.month_name[month]
    
    # Get available years, months, zones, buildings, and floors for filters
    current_date = datetime.now()
    years = list(range(current_date.year - 5, current_date.year + 2))
    months = [(i, calendar.month_name[i]) for i in range(1, 13)]
    all_zones = Zone.objects.filter(is_active=True).order_by('name')
    all_buildings = Building.objects.filter(is_active=True).order_by('name')
    all_floors = Floor.objects.filter(is_active=True).select_related('building').order_by('building__name', 'floor_number')
    
    # Filter buildings and floors based on selected zone/building
    if zone_id:
        filtered_buildings = Building.objects.filter(zone_id=zone_id, is_active=True).order_by('name')
        filtered_floors = Floor.objects.filter(building__zone_id=zone_id, is_active=True).select_related('building').order_by('building__name', 'floor_number')
    else:
        filtered_buildings = all_buildings
        filtered_floors = all_floors
    
    if building_id:
        filtered_floors = Floor.objects.filter(building_id=building_id, is_active=True).order_by('floor_number')
    
    context = {
        'building': building,
        'staff_categories': staff_categories,
        'total_male': total_male,
        'total_female': total_female,
        'grand_total': grand_total,
        'year': year,
        'month': month,
        'month_name': month_name,
        'report_date': f"{month_name.upper()}-{year}",
        'is_filtered_building': is_filtered_building,
        'years': years,
        'months': months,
        'zones': all_zones,
        'buildings': all_buildings,
        'floors': all_floors,
        'filtered_buildings': filtered_buildings,
        'filtered_floors': filtered_floors,
        'selected_zone': zone_id,
        'selected_building': building_id,
        'selected_floor': floor_id,
    }
    
    return render(request, 'hr/staff_report.html', context)

@login_required
@manager_or_admin_required("Department Management")
def position_create(request):
    """Create a new position."""
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save(commit=False)
            position.created_by = request.user
            position.save()
            messages.success(request, _('Position created successfully.'))
            return redirect('hr:position_detail', pk=position.pk)
    else:
        form = PositionForm()
    
    context = {'form': form}
    return render(request, 'hr/position_form.html', context)

@login_required
@manager_or_admin_required("Department Management")
def position_edit(request, pk):
    """Edit an existing position."""
    position = get_object_or_404(Position, pk=pk)
    
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            form.save()
            messages.success(request, _('Position updated successfully.'))
            return redirect('hr:position_detail', pk=position.pk)
    else:
        form = PositionForm(instance=position)
    
    context = {
        'form': form,
        'position': position,
    }
    return render(request, 'hr/position_form.html', context)

@login_required
@manager_or_admin_required("Department Management")
def position_delete(request, pk):
    """Delete a position."""
    position = get_object_or_404(Position, pk=pk)
    
    if request.method == 'POST':
        position.delete()
        messages.success(request, _('Position deleted successfully.'))
        return redirect('hr:position_list')
    
    context = {'position': position}
    return render(request, 'hr/position_delete.html', context)

@login_required
@require_http_methods(["GET"])
def serve_employee_photo(request, employee_id):
    """
    Serve employee photo securely - handles encrypted photos.
    """
    try:
        from core.file_encryption import FileEncryptionHandler
        import mimetypes
        import os
        from django.conf import settings
        
        employee = get_object_or_404(Employee, id=employee_id)
        
        # Check if employee has a photo
        if not employee.photo or not employee.photo.name:
            raise Http404("Photo not found")
        
        # Get the file path safely
        try:
            file_path = employee.photo.path
        except (ValueError, AttributeError, OSError) as e:
            # File path is invalid or file system error
            raise Http404("Photo file path is invalid")
        
        if not os.path.exists(file_path):
            raise Http404("Photo file not found on disk")
        
        # Read and decrypt if needed
        try:
            if employee.photo.name.endswith('.enc'):
                # Encrypted file - decrypt it
                with open(file_path, 'rb') as f:
                    encrypted_content = f.read().decode('utf-8')
                
                decrypted_content = FileEncryptionHandler.decrypt_file_content(encrypted_content)
                file_content = decrypted_content
                original_filename = employee.photo.name.replace('.enc', '')
            else:
                # Non-encrypted file - serve directly
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                original_filename = employee.photo.name
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(original_filename)
            if not content_type or not content_type.startswith('image/'):
                content_type = 'image/jpeg'  # Default to JPEG for images
            
            # Create response
            response = HttpResponse(file_content, content_type=content_type)
            
            # Set headers for inline display (not download)
            filename = f"employee_{employee.employee_id}_photo.{original_filename.split('.')[-1]}"
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            response['Content-Length'] = len(file_content)
            
            # Add caching headers for better performance but allow updates
            response['Cache-Control'] = 'private, max-age=300'  # Cache for 5 minutes only
            
            # Add ETag based on file modification time for better cache management
            import os
            try:
                if os.path.exists(file_path):
                    mtime = int(os.path.getmtime(file_path))
                    response['ETag'] = f'"{mtime}"'
            except (OSError, AttributeError):
                pass
            
            return response
            
        except Exception as e:

            
            pass
            raise Http404("Photo could not be processed")
            
    except Employee.DoesNotExist:

            
        pass
        raise Http404("Employee not found")
    except Exception as e:
        raise Http404("Photo not found")


@login_required
@require_http_methods(["GET"])
def serve_employee_document(request, document_id):
    """
    Serve employee document securely - handles encrypted documents.
    """
    try:
        import mimetypes

        document = get_object_or_404(EmployeeDocument, id=document_id)

        # Check if document has a file
        if not document.document_file or not document.document_file.name:
            raise Http404("Document file not found")

        # Get the file path
        file_path = document.document_file.path

        if not os.path.exists(file_path):
            raise Http404("Document file not found on disk")

        # Read and decrypt if needed
        try:
            if document.document_file.name.endswith('.enc'):
                # Encrypted file - decrypt it
                with open(file_path, 'rb') as f:
                    encrypted_content = f.read().decode('utf-8')

                decrypted_content = FileEncryptionHandler.decrypt_file_content(encrypted_content)
                file_content = decrypted_content
                original_filename = document.document_file.name.replace('.enc', '')
            else:
                # Non-encrypted file - serve directly
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                original_filename = document.document_file.name

            # Determine content type
            content_type, _ = mimetypes.guess_type(original_filename)
            if not content_type:
                # Default content types based on file extension
                ext = original_filename.lower().split('.')[-1]
                if ext in ['jpg', 'jpeg']:
                    content_type = 'image/jpeg'
                elif ext == 'png':
                    content_type = 'image/png'
                elif ext == 'pdf':
                    content_type = 'application/pdf'
                else:
                    content_type = 'application/octet-stream'

            # Create response
            response = HttpResponse(file_content, content_type=content_type)

            # Set headers for inline display (not download)
            safe_filename = f"employee_{document.employee.employee_id}_{document.get_document_type_display().replace(' ', '_').lower()}.{original_filename.split('.')[-1]}"
            response['Content-Disposition'] = f'inline; filename="{safe_filename}"'
            response['Content-Length'] = len(file_content)

            # Add caching headers for better performance
            response['Cache-Control'] = 'private, max-age=3600'  # Cache for 1 hour

            return response

        except Exception as e:
            raise Http404("Document could not be processed")

    except EmployeeDocument.DoesNotExist:
        raise Http404("Document not found")
    except Exception as e:
        raise Http404("Document not found")


# ============================================================================
# PROBATION MANAGEMENT VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_probationperiod', raise_exception=True)
def probation_list(request):
    """List all probation periods with search, filter, and pagination."""

    # Base queryset
    probation_periods = ProbationPeriod.objects.select_related('employee').all()

    # Search and filter
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    department_filter = request.GET.get('department', '')

    if search_query:
        probation_periods = probation_periods.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    if status_filter:
        probation_periods = probation_periods.filter(status=status_filter)

    if department_filter:
        probation_periods = probation_periods.filter(employee__department_id=department_filter)

    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    probation_periods = probation_periods.order_by(sort_by)

    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(probation_periods, per_page)
    page = request.GET.get('page')

    try:
        probation_periods_page = paginator.page(page)
    except PageNotAnInteger:
        probation_periods_page = paginator.page(1)
    except EmptyPage:
        probation_periods_page = paginator.page(paginator.num_pages)

    # Stats
    total_count = probation_periods.count()
    active_count = ProbationPeriod.objects.filter(status='active').count()
    completed_count = ProbationPeriod.objects.filter(status='completed').count()

    context = {
        'probation_periods': probation_periods_page,
        'search_query': search_query,
        'status_filter': status_filter,
        'department_filter': department_filter,
        'total_count': total_count,
        'active_count': active_count,
        'completed_count': completed_count,
        'departments': Department.objects.all(),
        'per_page': per_page,
    }

    return render(request, 'hr/probation_list.html', context)


@login_required
@permission_required('hr.view_probationperiod', raise_exception=True)
def probation_detail(request, pk):
    """Display detailed information about a probation period."""
    probation = get_object_or_404(ProbationPeriod, pk=pk)
    extensions = probation.extensions.all().order_by('-created_at')

    context = {
        'probation': probation,
        'extensions': extensions,
        'today': date.today(),
    }

    return render(request, 'hr/probation_detail.html', context)


@login_required
@permission_required('hr.add_probationperiod', raise_exception=True)
def probation_create(request):
    """Create a new probation period for an employee."""
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        start_date = request.POST.get('start_date')
        original_end_date = request.POST.get('original_end_date')
        evaluation_notes = request.POST.get('evaluation_notes', '')
        employment_status = request.POST.get('employment_status', 'active')

        try:
            employee = Employee.objects.get(id=employee_id)

            # Check if employee already has an active probation
            if employee.probation_periods.filter(status='active').exists():
                messages.error(request, _('Employee already has an active probation period.'))
                return redirect('hr:probation_create')

            # Update employee's employment status (single source of truth)
            employee.employment_status = employment_status
            employee.save()

            # Determine probation status based on employment status
            if employment_status == 'terminated':
                probation_status = 'failed'
            else:
                probation_status = 'active'

            probation = ProbationPeriod.objects.create(
                employee=employee,
                start_date=start_date,
                original_end_date=original_end_date,
                evaluation_notes=evaluation_notes,
                status=probation_status
            )

            messages.success(request, _('Probation period created successfully.'))
            return redirect('hr:probation_detail', pk=probation.pk)

        except Employee.DoesNotExist:
            messages.error(request, _('Employee not found.'))
        except Exception as e:
            messages.error(request, f'Error creating probation period: {str(e)}')

    # Get employees without active probation
    employees = Employee.objects.filter(
        employment_status='active'
    ).exclude(
        probation_periods__status='active'
    )

    context = {
        'employees': employees,
        'title': 'Create Probation Period',
    }

    return render(request, 'hr/probation_form.html', context)


@login_required
@permission_required('hr.change_probationperiod', raise_exception=True)
def probation_update(request, pk):
    """Update an existing probation period."""
    probation = get_object_or_404(ProbationPeriod, pk=pk)

    if request.method == 'POST':
        probation.evaluation_notes = request.POST.get('evaluation_notes', '')
        employment_status = request.POST.get('employment_status')

        # Update employee's employment status (single source of truth)
        if employment_status:
            probation.employee.employment_status = employment_status

            # Auto-update probation status based on employment status
            if employment_status == 'terminated':
                probation.status = 'failed'
                probation.actual_end_date = date.today()
            elif employment_status in ['suspended', 'on_leave']:
                # Keep current probation status, but don't auto-complete
                pass
            elif employment_status == 'active':
                # If employee returns to active and probation not yet completed/failed
                if probation.status not in ['completed', 'failed']:
                    probation.status = 'active'

        try:
            probation.employee.save()
            probation.save()
            messages.success(request, _('Probation period updated successfully.'))
            return redirect('hr:probation_detail', pk=probation.pk)
        except Exception as e:
            messages.error(request, f'Error updating probation period: {str(e)}')

    context = {
        'probation': probation,
        'title': f'Update Probation - {probation.employee.full_name}',
    }

    return render(request, 'hr/probation_update.html', context)


@login_required
@permission_required('hr.add_probationextension', raise_exception=True)
def probation_extend(request, pk):
    """Extend a probation period."""
    probation = get_object_or_404(ProbationPeriod, pk=pk)

    if request.method == 'POST':
        extension_days = int(request.POST.get('extension_duration_days'))
        reason = request.POST.get('reason')

        try:
            extension = ProbationExtension.objects.create(
                probation_period=probation,
                extension_duration_days=extension_days,
                reason=reason
            )

            messages.success(request, _(f'Probation period extended by {extension_days} days.'))
            return redirect('hr:probation_detail', pk=probation.pk)

        except Exception as e:
            messages.error(request, f'Error extending probation period: {str(e)}')

    context = {
        'probation': probation,
        'title': f'Extend Probation - {probation.employee.full_name}',
    }

    return render(request, 'hr/probation_extend.html', context)


@login_required
@permission_required('hr.delete_probationperiod', raise_exception=True)
def probation_delete(request, pk):
    """Delete a probation period."""
    probation = get_object_or_404(ProbationPeriod, pk=pk)

    if request.method == 'POST':
        try:
            employee_name = probation.employee.full_name
            probation.delete()
            messages.success(request, _(f'Probation period for {employee_name} deleted successfully.'))
            return redirect('hr:probation_list')
        except Exception as e:
            messages.error(request, f'Error deleting probation period: {str(e)}')

    context = {
        'probation': probation,
    }

    return render(request, 'hr/probation_confirm_delete.html', context)


# ============================================================================
# EMPLOYEE LIFECYCLE VIEWS
# ============================================================================

@login_required
def lifecycle_dashboard(request):
    """Employee Lifecycle Dashboard - Overview of all lifecycle stages"""
    from django.db.models import Count, Q

    # Onboarding Statistics
    total_onboarding = EmployeeOnboarding.objects.count()
    active_onboarding = EmployeeOnboarding.objects.filter(status='in_progress').count()
    completed_onboarding = EmployeeOnboarding.objects.filter(status='completed').count()
    overdue_onboarding = EmployeeOnboarding.objects.filter(
        status__in=['in_progress', 'pending'],
        expected_completion_date__lt=date.today()
    ).count()

    # Probation Statistics
    total_probation = ProbationPeriod.objects.count()
    active_probation = ProbationPeriod.objects.filter(status='active').count()
    completed_probation = ProbationPeriod.objects.filter(status='completed').count()

    # Promotion/Transfer Statistics
    total_promotions_transfers = PromotionTransfer.objects.count()
    pending_approval = PromotionTransfer.objects.filter(status='pending').count()
    approved_pending_implementation = PromotionTransfer.objects.filter(status='approved').count()
    implemented = PromotionTransfer.objects.filter(status='implemented').count()

    # Exit Statistics
    total_exits = ExitInterview.objects.count()
    scheduled_exits = ExitInterview.objects.filter(status='scheduled').count()
    completed_exits = ExitInterview.objects.filter(status='completed').count()

    # Recent Activities
    recent_onboarding = EmployeeOnboarding.objects.select_related('employee').order_by('-created_at')[:5]
    recent_promotions = PromotionTransfer.objects.select_related('employee').order_by('-created_at')[:5]
    recent_exits = ExitInterview.objects.select_related('employee').order_by('-created_at')[:5]

    # Employees by lifecycle stage
    employees_in_onboarding = Employee.objects.filter(
        onboarding_record__status__in=['pending', 'in_progress']
    ).count()
    employees_in_probation = Employee.objects.filter(
        probation_periods__status='active'
    ).distinct().count()

    context = {
        # Onboarding
        'total_onboarding': total_onboarding,
        'active_onboarding': active_onboarding,
        'completed_onboarding': completed_onboarding,
        'overdue_onboarding': overdue_onboarding,

        # Probation
        'total_probation': total_probation,
        'active_probation': active_probation,
        'completed_probation': completed_probation,

        # Promotions/Transfers
        'total_promotions_transfers': total_promotions_transfers,
        'pending_approval': pending_approval,
        'approved_pending_implementation': approved_pending_implementation,
        'implemented': implemented,

        # Exits
        'total_exits': total_exits,
        'scheduled_exits': scheduled_exits,
        'completed_exits': completed_exits,

        # Recent Activities
        'recent_onboarding': recent_onboarding,
        'recent_promotions': recent_promotions,
        'recent_exits': recent_exits,

        # Aggregates
        'employees_in_onboarding': employees_in_onboarding,
        'employees_in_probation': employees_in_probation,
    }

    return render(request, 'hr/lifecycle/dashboard.html', context)


# ============================================================================
# ONBOARDING VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_employeeonboarding', raise_exception=True)
def onboarding_list(request):
    """List all onboarding processes"""
    onboardings = EmployeeOnboarding.objects.select_related('employee', 'template').all()

    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        onboardings = onboardings.filter(status=status_filter)

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        onboardings = onboardings.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    onboardings = onboardings.order_by(sort_by)

    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(onboardings, per_page)
    page = request.GET.get('page')

    try:
        onboardings_page = paginator.page(page)
    except PageNotAnInteger:
        onboardings_page = paginator.page(1)
    except EmptyPage:
        onboardings_page = paginator.page(paginator.num_pages)

    context = {
        'onboardings': onboardings_page,
        'status_filter': status_filter,
        'search_query': search_query,
        'per_page': per_page,
    }

    return render(request, 'hr/lifecycle/onboarding_list.html', context)


@login_required
@permission_required('hr.view_employeeonboarding', raise_exception=True)
def onboarding_detail(request, pk):
    """Display detailed onboarding information with tasks"""
    onboarding = get_object_or_404(EmployeeOnboarding, pk=pk)
    tasks = onboarding.task_instances.all().order_by('due_date', 'priority')

    # Group tasks by status
    pending_tasks = tasks.filter(status='pending')
    in_progress_tasks = tasks.filter(status='in_progress')
    completed_tasks = tasks.filter(status='completed')

    context = {
        'onboarding': onboarding,
        'tasks': tasks,
        'pending_tasks': pending_tasks,
        'in_progress_tasks': in_progress_tasks,
        'completed_tasks': completed_tasks,
        'today': date.today(),
    }

    return render(request, 'hr/lifecycle/onboarding_detail.html', context)


@login_required
@permission_required('hr.add_employeeonboarding', raise_exception=True)
def onboarding_create(request):
    """Create new onboarding process for an employee"""
    if request.method == 'POST':
        form = OnboardingCreateForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            template = form.cleaned_data.get('template')
            start_date = form.cleaned_data['start_date']
            hr_representative = form.cleaned_data.get('hr_representative')
            buddy = form.cleaned_data.get('buddy')
            notes = form.cleaned_data.get('notes')

            # Check if employee already has an onboarding
            if hasattr(employee, 'onboarding_record'):
                messages.error(request, _('Employee already has an onboarding process.'))
                return redirect('hr:onboarding_create')

            try:
                # Create onboarding
                onboarding = EmployeeOnboarding.objects.create(
                    employee=employee,
                    template=template,
                    start_date=start_date,
                    hr_representative=hr_representative,
                    buddy=buddy,
                    notes=notes,
                    created_by=request.user
                )

                # If template exists, create task instances
                if template:
                    from datetime import timedelta
                    for task in template.tasks.filter(is_active=True).order_by('order'):
                        due_date = start_date + timedelta(days=task.due_after_days)
                        OnboardingTaskInstance.objects.create(
                            onboarding=onboarding,
                            task=task,
                            title=task.title,
                            description=task.description,
                            task_type=task.task_type,
                            priority=task.priority,
                            estimated_hours=task.estimated_hours,
                            due_date=due_date,
                            status='pending'
                        )

                messages.success(request, _('Onboarding process created successfully.'))
                return redirect('hr:onboarding_detail', pk=onboarding.pk)

            except Exception as e:
                messages.error(request, f'Error creating onboarding: {str(e)}')
    else:
        form = OnboardingCreateForm()

    context = {
        'form': form,
        'title': 'Create Onboarding Process',
    }

    return render(request, 'hr/lifecycle/onboarding_form.html', context)


@login_required
@permission_required('hr.change_onboardingtaskinstance', raise_exception=True)
def onboarding_task_update_status(request, task_pk):
    """Update onboarding task status"""
    task = get_object_or_404(OnboardingTaskInstance, pk=task_pk)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['pending', 'in_progress', 'completed']:
            task.status = new_status
            if new_status == 'in_progress' and not task.start_date:
                task.start_date = date.today()
            if new_status == 'completed':
                task.mark_completed()
            else:
                task.save()

            messages.success(request, _('Task status updated successfully.'))
        else:
            messages.error(request, _('Invalid status.'))

    return redirect('hr:onboarding_detail', pk=task.onboarding.pk)


@login_required
@permission_required('hr.change_onboardingtaskinstance', raise_exception=True)
def onboarding_task_complete(request, task_pk):
    """Complete an onboarding task with notes"""
    task = get_object_or_404(OnboardingTaskInstance, pk=task_pk)

    if request.method == 'POST':
        form = OnboardingTaskCompleteForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.mark_completed()
            messages.success(request, _('Task marked as completed.'))
            return redirect('hr:onboarding_detail', pk=task.onboarding.pk)
    else:
        form = OnboardingTaskCompleteForm(instance=task)

    context = {
        'form': form,
        'task': task,
        'title': f'Complete Task - {task.title}',
    }

    return render(request, 'hr/lifecycle/onboarding_task_complete.html', context)


@login_required
@permission_required('hr.delete_employeeonboarding', raise_exception=True)
def onboarding_delete(request, pk):
    """Delete an onboarding process"""
    onboarding = get_object_or_404(EmployeeOnboarding, pk=pk)

    if request.method == 'POST':
        try:
            employee_name = onboarding.employee.full_name
            onboarding.delete()
            messages.success(request, _(f'Onboarding process for {employee_name} deleted successfully.'))
            return redirect('hr:onboarding_list')
        except Exception as e:
            messages.error(request, f'Error deleting onboarding process: {str(e)}')
            return redirect('hr:onboarding_list')

    # If GET request, redirect to list (modal handles confirmation)
    return redirect('hr:onboarding_list')


# ============================================================================
# PROMOTION/TRANSFER VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_promotiontransfer', raise_exception=True)
def promotion_transfer_list(request):
    """List all promotions and transfers"""
    promotions_transfers = PromotionTransfer.objects.select_related(
        'employee', 'current_position', 'current_department',
        'new_position', 'new_department'
    ).all()

    # Filters
    change_type_filter = request.GET.get('change_type', '')
    status_filter = request.GET.get('status', '')

    if change_type_filter:
        promotions_transfers = promotions_transfers.filter(change_type=change_type_filter)
    if status_filter:
        promotions_transfers = promotions_transfers.filter(status=status_filter)

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        promotions_transfers = promotions_transfers.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    promotions_transfers = promotions_transfers.order_by(sort_by)

    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(promotions_transfers, per_page)
    page = request.GET.get('page')

    try:
        promotions_transfers_page = paginator.page(page)
    except PageNotAnInteger:
        promotions_transfers_page = paginator.page(1)
    except EmptyPage:
        promotions_transfers_page = paginator.page(paginator.num_pages)

    context = {
        'promotions_transfers': promotions_transfers_page,
        'change_type_filter': change_type_filter,
        'status_filter': status_filter,
        'search_query': search_query,
        'per_page': per_page,
    }

    return render(request, 'hr/lifecycle/promotion_transfer_list.html', context)


@login_required
@permission_required('hr.view_promotiontransfer', raise_exception=True)
def promotion_transfer_detail(request, pk):
    """Display detailed promotion/transfer information"""
    promotion_transfer = get_object_or_404(PromotionTransfer, pk=pk)

    context = {
        'promotion_transfer': promotion_transfer,
        'today': date.today(),
    }

    return render(request, 'hr/lifecycle/promotion_transfer_detail.html', context)


@login_required
@permission_required('hr.add_promotiontransfer', raise_exception=True)
def promotion_transfer_create(request):
    """Create new promotion or transfer request"""
    if request.method == 'POST':
        form = PromotionTransferForm(request.POST)
        if form.is_valid():
            promotion_transfer = form.save(commit=False)

            # Set current position and department from employee
            employee = promotion_transfer.employee
            promotion_transfer.current_position = employee.position
            promotion_transfer.current_department = employee.department
            promotion_transfer.requested_by = request.user
            promotion_transfer.status = 'pending'

            promotion_transfer.save()

            messages.success(request, _('Promotion/Transfer request created successfully.'))
            return redirect('hr:promotion_transfer_detail', pk=promotion_transfer.pk)
    else:
        form = PromotionTransferForm()

    context = {
        'form': form,
        'title': 'Create Promotion/Transfer Request',
    }

    return render(request, 'hr/lifecycle/promotion_transfer_form.html', context)


@login_required
@permission_required('hr.change_promotiontransfer', raise_exception=True)
def promotion_transfer_approve(request, pk):
    """Approve or reject a promotion/transfer request"""
    promotion_transfer = get_object_or_404(PromotionTransfer, pk=pk)

    if request.method == 'POST':
        form = PromotionTransferApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']

            if action == 'approve':
                promotion_transfer.status = 'approved'
                promotion_transfer.approved_by = request.user
                promotion_transfer.approved_at = timezone.now()
                promotion_transfer.save()
                messages.success(request, _('Promotion/Transfer approved successfully.'))
            else:  # reject
                promotion_transfer.status = 'rejected'
                promotion_transfer.rejection_reason = form.cleaned_data['rejection_reason']
                promotion_transfer.save()
                messages.success(request, _('Promotion/Transfer rejected.'))

            return redirect('hr:promotion_transfer_detail', pk=promotion_transfer.pk)
    else:
        form = PromotionTransferApprovalForm()

    context = {
        'form': form,
        'promotion_transfer': promotion_transfer,
        'title': f'Approve/Reject - {promotion_transfer.employee.full_name}',
    }

    return render(request, 'hr/lifecycle/promotion_transfer_approve.html', context)


@login_required
@permission_required('hr.change_promotiontransfer', raise_exception=True)
def promotion_transfer_implement(request, pk):
    """Implement an approved promotion/transfer"""
    promotion_transfer = get_object_or_404(PromotionTransfer, pk=pk)

    if promotion_transfer.status != 'approved':
        messages.error(request, _('Only approved promotion/transfers can be implemented.'))
        return redirect('hr:promotion_transfer_detail', pk=pk)

    if request.method == 'POST':
        try:
            # Update employee record
            employee = promotion_transfer.employee
            employee.position = promotion_transfer.new_position
            employee.department = promotion_transfer.new_department

            if promotion_transfer.salary_change:
                employee.salary = promotion_transfer.salary_change

            employee.save()

            # Update promotion/transfer status
            promotion_transfer.status = 'implemented'
            promotion_transfer.implemented_by = request.user
            promotion_transfer.implemented_at = timezone.now()
            promotion_transfer.save()

            messages.success(request, _('Promotion/Transfer implemented successfully.'))
            return redirect('hr:promotion_transfer_detail', pk=pk)

        except Exception as e:
            messages.error(request, f'Error implementing promotion/transfer: {str(e)}')

    context = {
        'promotion_transfer': promotion_transfer,
    }

    return render(request, 'hr/lifecycle/promotion_transfer_implement.html', context)


# ============================================================================
# EXIT MANAGEMENT VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_exitinterview', raise_exception=True)
def exit_interview_list(request):
    """List all exit interviews"""
    exit_interviews = ExitInterview.objects.select_related('employee', 'interviewer').all()

    # Filters
    status_filter = request.GET.get('status', '')
    exit_reason_filter = request.GET.get('exit_reason', '')

    if status_filter:
        exit_interviews = exit_interviews.filter(status=status_filter)
    if exit_reason_filter:
        exit_interviews = exit_interviews.filter(exit_reason=exit_reason_filter)

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        exit_interviews = exit_interviews.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    exit_interviews = exit_interviews.order_by(sort_by)

    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(exit_interviews, per_page)
    page = request.GET.get('page')

    try:
        exit_interviews_page = paginator.page(page)
    except PageNotAnInteger:
        exit_interviews_page = paginator.page(1)
    except EmptyPage:
        exit_interviews_page = paginator.page(paginator.num_pages)

    context = {
        'exit_interviews': exit_interviews_page,
        'status_filter': status_filter,
        'exit_reason_filter': exit_reason_filter,
        'search_query': search_query,
        'per_page': per_page,
    }

    return render(request, 'hr/lifecycle/exit_interview_list.html', context)


@login_required
@permission_required('hr.view_exitinterview', raise_exception=True)
def exit_interview_detail(request, pk):
    """Display detailed exit interview information"""
    exit_interview = get_object_or_404(ExitInterview, pk=pk)

    # Try to get exit checklist
    try:
        exit_checklist = ExitChecklist.objects.get(employee=exit_interview.employee)
    except ExitChecklist.DoesNotExist:
        exit_checklist = None

    context = {
        'exit_interview': exit_interview,
        'exit_checklist': exit_checklist,
        'today': date.today(),
    }

    return render(request, 'hr/lifecycle/exit_interview_detail.html', context)


@login_required
@permission_required('hr.add_exitinterview', raise_exception=True)
def exit_interview_create(request):
    """Create new exit interview"""
    if request.method == 'POST':
        form = ExitInterviewForm(request.POST)
        if form.is_valid():
            exit_interview = form.save(commit=False)
            exit_interview.status = 'scheduled'
            exit_interview.created_by = request.user
            exit_interview.save()

            messages.success(request, _('Exit interview created successfully.'))
            return redirect('hr:exit_interview_detail', pk=exit_interview.pk)
    else:
        form = ExitInterviewForm()

    context = {
        'form': form,
        'title': 'Create Exit Interview',
    }

    return render(request, 'hr/lifecycle/exit_interview_form.html', context)


@login_required
@permission_required('hr.change_exitinterview', raise_exception=True)
def exit_interview_update(request, pk):
    """Update exit interview"""
    exit_interview = get_object_or_404(ExitInterview, pk=pk)

    if request.method == 'POST':
        form = ExitInterviewForm(request.POST, instance=exit_interview)
        if form.is_valid():
            exit_interview = form.save(commit=False)
            # If all ratings are filled, mark as completed
            if all([
                exit_interview.job_satisfaction_rating,
                exit_interview.work_environment_rating,
                exit_interview.management_quality_rating,
                exit_interview.career_development_rating,
                exit_interview.work_life_balance_rating,
                exit_interview.compensation_benefits_rating
            ]):
                exit_interview.status = 'completed'
            exit_interview.save()

            messages.success(request, _('Exit interview updated successfully.'))
            return redirect('hr:exit_interview_detail', pk=exit_interview.pk)
    else:
        form = ExitInterviewForm(instance=exit_interview)

    context = {
        'form': form,
        'exit_interview': exit_interview,
        'title': f'Update Exit Interview - {exit_interview.employee.full_name}',
    }

    return render(request, 'hr/lifecycle/exit_interview_form.html', context)


@login_required
@permission_required('hr.view_exitchecklist', raise_exception=True)
def exit_checklist_detail(request, employee_pk):
    """Display exit checklist for an employee"""
    employee = get_object_or_404(Employee, pk=employee_pk)

    try:
        exit_checklist = ExitChecklist.objects.get(employee=employee)
    except ExitChecklist.DoesNotExist:
        exit_checklist = None

    context = {
        'employee': employee,
        'exit_checklist': exit_checklist,
    }

    return render(request, 'hr/lifecycle/exit_checklist_detail.html', context)


@login_required
@permission_required('hr.change_exitchecklist', raise_exception=True)
def exit_checklist_update(request, employee_pk):
    """Update or create exit checklist"""
    employee = get_object_or_404(Employee, pk=employee_pk)

    try:
        exit_checklist = ExitChecklist.objects.get(employee=employee)
    except ExitChecklist.DoesNotExist:
        exit_checklist = None

    if request.method == 'POST':
        form = ExitChecklistForm(request.POST, instance=exit_checklist)
        if form.is_valid():
            exit_checklist = form.save(commit=False)
            exit_checklist.employee = employee
            exit_checklist.save()

            messages.success(request, _('Exit checklist updated successfully.'))
            return redirect('hr:exit_checklist_detail', employee_pk=employee.pk)
    else:
        form = ExitChecklistForm(instance=exit_checklist)

    context = {
        'form': form,
        'employee': employee,
        'exit_checklist': exit_checklist,
        'title': f'Exit Checklist - {employee.full_name}',
    }

    return render(request, 'hr/lifecycle/exit_checklist_form.html', context)

