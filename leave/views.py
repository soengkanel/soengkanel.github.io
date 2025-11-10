from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Sum
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import (
    LeaveType, LeaveApplication, LeaveAllocation,
    Holiday, CompensatoryLeaveRequest
)
from .forms import (
    LeaveTypeForm, LeaveApplicationForm, LeaveAllocationForm,
    HolidayForm, LeaveApprovalForm
)


# ==================== LEAVE TYPES ====================

@login_required
def leave_type_list(request):
    """List all leave types"""
    search_query = request.GET.get('search', '')
    leave_types = LeaveType.objects.all()

    if search_query:
        leave_types = leave_types.filter(
            Q(name__icontains=search_query) | Q(code__icontains=search_query)
        )

    paginator = Paginator(leave_types, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'leave/types/list.html', context)


@login_required
def leave_type_create(request):
    """Create a new leave type"""
    if request.method == 'POST':
        form = LeaveTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave type created successfully.')
            return redirect('leave:type_list')
    else:
        form = LeaveTypeForm()

    return render(request, 'leave/types/form.html', {'form': form, 'title': 'Create Leave Type'})


@login_required
def leave_type_edit(request, pk):
    """Edit an existing leave type"""
    leave_type = get_object_or_404(LeaveType, pk=pk)

    if request.method == 'POST':
        form = LeaveTypeForm(request.POST, instance=leave_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave type updated successfully.')
            return redirect('leave:type_list')
    else:
        form = LeaveTypeForm(instance=leave_type)

    return render(request, 'leave/types/form.html', {'form': form, 'title': 'Edit Leave Type', 'leave_type': leave_type})


@login_required
def leave_type_delete(request, pk):
    """Delete a leave type"""
    leave_type = get_object_or_404(LeaveType, pk=pk)
    if request.method == 'POST':
        leave_type.delete()
        messages.success(request, 'Leave type deleted successfully.')
        return redirect('leave:type_list')
    return redirect('leave:type_list')


# ==================== LEAVE APPLICATIONS ====================

@login_required
def leave_application_list(request):
    """List all leave applications"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # Check if user has User role (basic employee)
    is_basic_user = False
    can_approve = False
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.get(
            user=request.user,
            is_active=True
        )
        if role_assignment.role.name == "User":
            is_basic_user = True
        elif role_assignment.role.name in ["HR", "Manager", "Admin"]:
            can_approve = True
    except:
        pass

    # Also check if user is a manager of any employee
    if hasattr(request.user, 'employee') and not can_approve:
        from hr.models import Employee
        if Employee.objects.filter(manager=request.user.employee).exists():
            can_approve = True

    # Base queryset - filter by employee for basic users
    if is_basic_user:
        try:
            employee = request.user.employee
            applications = LeaveApplication.objects.select_related('employee', 'leave_type', 'created_by').filter(employee=employee)
        except:
            messages.error(request, 'Employee profile not found. Please contact HR.')
            return redirect('dashboard:home')
    else:
        applications = LeaveApplication.objects.select_related('employee', 'leave_type', 'created_by').all()

    if search_query:
        applications = applications.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(leave_type__name__icontains=search_query)
        )

    if status_filter:
        applications = applications.filter(status=status_filter)

    applications = applications.order_by('-created_at')

    paginator = Paginator(applications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Status counts for filters - also filter by employee for basic users
    if is_basic_user:
        base_queryset = LeaveApplication.objects.filter(employee=employee)
    else:
        base_queryset = LeaveApplication.objects.all()

    status_counts = {
        'all': base_queryset.count(),
        'pending': base_queryset.filter(status='pending').count(),
        'approved': base_queryset.filter(status='approved').count(),
        'rejected': base_queryset.filter(status='rejected').count(),
    }

    # Get leave balances for basic users
    leave_balances = []
    if is_basic_user:
        try:
            from leave.models import LeaveAllocation
            current_year = timezone.now().year
            allocations = LeaveAllocation.objects.filter(
                employee=employee,
                year=current_year
            ).select_related('leave_type')
            leave_balances = [
                {
                    'leave_type': alloc.leave_type.name,
                    'code': alloc.leave_type.code,
                    'allocated': alloc.allocated_days,
                    'used': alloc.used_days,
                    'remaining': alloc.remaining_days,
                    'color': alloc.leave_type.color,
                }
                for alloc in allocations
            ]
        except:
            pass

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_counts': status_counts,
        'leave_balances': leave_balances,
        'is_basic_user': is_basic_user,
        'can_approve': can_approve,
    }
    return render(request, 'leave/applications/list.html', context)


@login_required
def leave_application_create(request):
    """Create a new leave application"""
    if request.method == 'POST':
        form = LeaveApplicationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Let the form handle employee assignment
            application = form.save(commit=False)

            # Ensure employee is set (form's save method should have done this)
            if not application.employee_id and hasattr(request.user, 'employee'):
                application.employee = request.user.employee

            application.created_by = request.user
            application.status = 'draft'
            application.save()
            messages.success(request, 'Leave application submitted successfully.')
            return redirect('leave:application_list')
    else:
        form = LeaveApplicationForm(user=request.user)

    # Get leave balances for the current user
    leave_balances = {}
    try:
        if hasattr(request.user, 'employee'):
            from leave.models import LeaveAllocation
            import json
            current_year = timezone.now().year
            allocations = LeaveAllocation.objects.filter(
                employee=request.user.employee,
                year=current_year
            ).select_related('leave_type')

            for alloc in allocations:
                leave_balances[str(alloc.leave_type.id)] = {
                    'leave_type': alloc.leave_type.name,
                    'code': alloc.leave_type.code,
                    'allocated': float(alloc.allocated_days),
                    'used': float(alloc.used_days),
                    'remaining': float(alloc.remaining_days),
                }
    except Exception as e:
        # Log errors silently
        pass

    # Convert to JSON for JavaScript
    import json
    leave_balances_json = json.dumps(leave_balances)

    return render(request, 'leave/applications/form.html', {
        'form': form,
        'title': 'Apply for Leave',
        'leave_balances': leave_balances_json,
    })


@login_required
def leave_application_detail(request, pk):
    """View leave application details"""
    # Check if user has User role (basic employee)
    is_basic_user = False
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.get(
            user=request.user,
            is_active=True
        )
        if role_assignment.role.name == "User":
            is_basic_user = True
    except:
        pass

    # Get the application
    application = get_object_or_404(
        LeaveApplication.objects.select_related('employee', 'leave_type', 'created_by', 'approved_by'),
        pk=pk
    )

    # For basic users, verify they own this application
    if is_basic_user:
        try:
            employee = request.user.employee
            if application.employee != employee:
                messages.error(request, 'You do not have permission to view this leave application.')
                return redirect('leave:application_list')
        except:
            messages.error(request, 'Employee profile not found. Please contact HR.')
            return redirect('dashboard:home')

    # Check if user can approve/reject this application
    can_approve = False
    try:
        from user_management.models import UserRoleAssignment

        # Check if user has HR or Manager role
        role_assignment = UserRoleAssignment.objects.filter(
            user=request.user,
            is_active=True
        ).first()

        if role_assignment and role_assignment.role.name in ["HR", "Manager", "Admin"]:
            can_approve = True

        # Also check if user is the direct manager of the employee
        if hasattr(request.user, 'employee'):
            manager_employee = request.user.employee
            if application.employee.manager == manager_employee:
                can_approve = True
    except Exception as e:
        pass

    # Get employee's leave allocation for this leave type
    allocation = LeaveAllocation.objects.filter(
        employee=application.employee,
        leave_type=application.leave_type,
        year=timezone.now().year
    ).first()

    context = {
        'application': application,
        'allocation': allocation,
        'can_approve': can_approve,
    }
    return render(request, 'leave/applications/detail.html', context)


@login_required
def leave_application_approve(request, pk):
    """Approve a leave application"""
    application = get_object_or_404(LeaveApplication, pk=pk)

    # Check if user has permission to approve
    can_approve = False
    try:
        from user_management.models import UserRoleAssignment

        # Check if user has HR or Manager role
        role_assignment = UserRoleAssignment.objects.filter(
            user=request.user,
            is_active=True
        ).first()

        if role_assignment and role_assignment.role.name in ["HR", "Manager", "Admin"]:
            can_approve = True

        # Also check if user is the direct manager of the employee
        if hasattr(request.user, 'employee'):
            manager_employee = request.user.employee
            if application.employee.manager == manager_employee:
                can_approve = True
    except Exception as e:
        pass

    if not can_approve:
        messages.error(request, 'You do not have permission to approve this leave application.')
        return redirect('leave:application_detail', pk=pk)

    if request.method == 'POST':
        application.status = 'approved'
        application.approved_by = request.user
        application.approved_at = timezone.now()
        application.save()

        # Update leave allocation
        allocation = LeaveAllocation.objects.filter(
            employee=application.employee,
            leave_type=application.leave_type,
            year=application.from_date.year
        ).first()

        if allocation:
            allocation.used_days += application.total_leave_days
            allocation.save()

        messages.success(request, 'Leave application approved successfully.')
        return redirect('leave:application_detail', pk=pk)

    return redirect('leave:application_detail', pk=pk)


@login_required
def leave_application_reject(request, pk):
    """Reject a leave application"""
    application = get_object_or_404(LeaveApplication, pk=pk)

    # Check if user has permission to reject
    can_reject = False
    try:
        from user_management.models import UserRoleAssignment

        # Check if user has HR or Manager role
        role_assignment = UserRoleAssignment.objects.filter(
            user=request.user,
            is_active=True
        ).first()

        if role_assignment and role_assignment.role.name in ["HR", "Manager", "Admin"]:
            can_reject = True

        # Also check if user is the direct manager of the employee
        if hasattr(request.user, 'employee'):
            manager_employee = request.user.employee
            if application.employee.manager == manager_employee:
                can_reject = True
    except Exception as e:
        pass

    if not can_reject:
        messages.error(request, 'You do not have permission to reject this leave application.')
        return redirect('leave:application_detail', pk=pk)

    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason', '')
        application.status = 'rejected'
        application.rejection_reason = rejection_reason
        application.approved_by = request.user
        application.approved_at = timezone.now()
        application.save()

        messages.success(request, 'Leave application rejected.')
        return redirect('leave:application_detail', pk=pk)

    return redirect('leave:application_detail', pk=pk)


@login_required
def leave_application_cancel(request, pk):
    """Cancel a leave application"""
    application = get_object_or_404(LeaveApplication, pk=pk)

    # Check if user has User role (basic employee)
    is_basic_user = False
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.get(
            user=request.user,
            is_active=True
        )
        if role_assignment.role.name == "User":
            is_basic_user = True
    except:
        pass

    # For basic users, verify they own this application
    if is_basic_user:
        try:
            employee = request.user.employee
            if application.employee != employee:
                messages.error(request, 'You do not have permission to cancel this leave application.')
                return redirect('leave:application_list')
        except:
            messages.error(request, 'Employee profile not found. Please contact HR.')
            return redirect('dashboard:home')

    if request.method == 'POST':
        if application.status in ['draft', 'pending']:
            application.status = 'cancelled'
            application.save()
            messages.success(request, 'Leave application cancelled.')
        elif application.status == 'approved':
            # If already approved, restore the used days
            allocation = LeaveAllocation.objects.filter(
                employee=application.employee,
                leave_type=application.leave_type,
                year=application.from_date.year
            ).first()

            if allocation:
                allocation.used_days -= application.total_leave_days
                allocation.save()

            application.status = 'cancelled'
            application.save()
            messages.success(request, 'Leave application cancelled and days restored.')

        return redirect('leave:application_list')

    return redirect('leave:application_detail', pk=pk)


# ==================== LEAVE ALLOCATIONS ====================

@login_required
def leave_allocation_list(request):
    """List all leave allocations"""
    search_query = request.GET.get('search', '')
    year = request.GET.get('year', timezone.now().year)

    allocations = LeaveAllocation.objects.select_related('employee', 'leave_type').filter(year=year)

    if search_query:
        allocations = allocations.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(leave_type__name__icontains=search_query)
        )

    allocations = allocations.order_by('employee', 'leave_type')

    # Calculate stats for the year
    year_allocations = LeaveAllocation.objects.filter(year=year)
    stats = {
        'total_allocations': year_allocations.count(),
        'total_days': year_allocations.aggregate(total=Sum('allocated_days'))['total'] or 0,
        'used_days': year_allocations.aggregate(total=Sum('used_days'))['total'] or 0,
        'remaining_days': year_allocations.aggregate(
            total=Sum('allocated_days')
        )['total'] - year_allocations.aggregate(
            total=Sum('used_days')
        )['total'] if year_allocations.exists() else 0,
    }

    # Pagination with per_page support
    per_page = request.GET.get('per_page', '20')
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 25, 50, 100, 200]:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20

    paginator = Paginator(allocations, per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'year': year,
        'stats': stats,
        'per_page': per_page,
        'total_count': paginator.count,
    }
    return render(request, 'leave/allocations/list.html', context)


@login_required
def leave_allocation_create(request):
    """Create a new leave allocation"""
    if request.method == 'POST':
        form = LeaveAllocationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave allocation created successfully.')
            return redirect('leave:allocation_list')
    else:
        form = LeaveAllocationForm()

    return render(request, 'leave/allocations/form.html', {'form': form, 'title': 'Allocate Leave'})


@login_required
def leave_allocation_edit(request, pk):
    """Edit a leave allocation"""
    allocation = get_object_or_404(LeaveAllocation, pk=pk)

    if request.method == 'POST':
        form = LeaveAllocationForm(request.POST, instance=allocation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave allocation updated successfully.')
            return redirect('leave:allocation_list')
    else:
        form = LeaveAllocationForm(instance=allocation)

    return render(request, 'leave/allocations/form.html', {'form': form, 'title': 'Edit Allocation', 'allocation': allocation})


# ==================== HOLIDAYS ====================

@login_required
def holiday_list(request):
    """List all holidays"""
    year = request.GET.get('year', timezone.now().year)
    holidays = Holiday.objects.filter(year=year).order_by('date')

    today = timezone.now().date()

    # Calculate statistics
    total_holidays = holidays.count()
    public_holidays = holidays.filter(is_optional=False).count()
    optional_holidays = holidays.filter(is_optional=True).count()

    # For calendar view, we need all holidays (not paginated)
    context = {
        'page_obj': holidays,  # All holidays for the year
        'year': year,
        'today': today,
        'total_holidays': total_holidays,
        'public_holidays': public_holidays,
        'optional_holidays': optional_holidays,
    }
    return render(request, 'leave/holidays/list.html', context)


@login_required
def holiday_create(request):
    """Create a new holiday"""
    if request.method == 'POST':
        form = HolidayForm(request.POST)
        if form.is_valid():
            use_date_range = form.cleaned_data.get('use_date_range')

            if use_date_range:
                # Create multiple holidays for date range
                from_date = form.cleaned_data.get('from_date')
                to_date = form.cleaned_data.get('to_date')
                name = form.cleaned_data.get('name')
                is_optional = form.cleaned_data.get('is_optional')
                description = form.cleaned_data.get('description')
                applies_to_all = form.cleaned_data.get('applies_to_all')
                regions = form.cleaned_data.get('regions')

                current_date = from_date
                created_count = 0

                while current_date <= to_date:
                    Holiday.objects.create(
                        name=name,
                        date=current_date,
                        year=current_date.year,
                        is_optional=is_optional,
                        description=description,
                        applies_to_all=applies_to_all,
                        regions=regions
                    )
                    current_date += timedelta(days=1)
                    created_count += 1

                messages.success(request, f'{created_count} holidays created successfully.')
            else:
                # Create single holiday
                form.save()
                messages.success(request, 'Holiday created successfully.')

            return redirect('leave:holiday_list')
    else:
        form = HolidayForm()

    return render(request, 'leave/holidays/form.html', {'form': form, 'title': 'Add Holiday'})


@login_required
def holiday_edit(request, pk):
    """Edit a holiday"""
    holiday = get_object_or_404(Holiday, pk=pk)

    if request.method == 'POST':
        form = HolidayForm(request.POST, instance=holiday)
        if form.is_valid():
            form.save()
            messages.success(request, 'Holiday updated successfully.')
            return redirect('leave:holiday_list')
    else:
        form = HolidayForm(instance=holiday)

    return render(request, 'leave/holidays/form.html', {'form': form, 'title': 'Edit Holiday', 'holiday': holiday})


@login_required
def holiday_delete(request, pk):
    """Delete a holiday"""
    holiday = get_object_or_404(Holiday, pk=pk)
    if request.method == 'POST':
        holiday.delete()
        messages.success(request, 'Holiday deleted successfully.')
        return redirect('leave:holiday_list')
    return redirect('leave:holiday_list')


# ==================== DASHBOARD ====================

@login_required
def leave_dashboard(request):
    """Leave management dashboard"""
    current_year = timezone.now().year

    # Statistics
    stats = {
        'total_applications': LeaveApplication.objects.filter(from_date__year=current_year).count(),
        'pending_applications': LeaveApplication.objects.filter(status='pending').count(),
        'approved_applications': LeaveApplication.objects.filter(status='approved', from_date__year=current_year).count(),
        'rejected_applications': LeaveApplication.objects.filter(status='rejected', from_date__year=current_year).count(),
        'total_leave_types': LeaveType.objects.filter(is_active=True).count(),
    }

    # Recent applications
    recent_applications = LeaveApplication.objects.select_related(
        'employee', 'leave_type', 'created_by'
    ).order_by('-created_at')[:5]

    # Pending approvals
    pending_approvals = LeaveApplication.objects.filter(
        status='pending'
    ).select_related('employee', 'leave_type').order_by('-created_at')[:5]

    context = {
        'stats': stats,
        'recent_applications': recent_applications,
        'pending_approvals': pending_approvals,
    }
    return render(request, 'leave/dashboard.html', context)
