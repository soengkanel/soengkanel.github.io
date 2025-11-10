from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from .models import Employee
from core.utils import get_current_employee


@login_required
@permission_required('hr.change_employee')
def employee_user_management(request):
    """Manage Employee-User relationships"""
    employees_with_users = Employee.objects.filter(user__isnull=False).select_related('user')
    employees_without_users = Employee.objects.filter(user__isnull=True)
    users_without_employees = User.objects.filter(employee__isnull=True)

    context = {
        'employees_with_users': employees_with_users,
        'employees_without_users': employees_without_users,
        'users_without_employees': users_without_employees,
        'stats': {
            'total_employees': Employee.objects.count(),
            'employees_with_users': employees_with_users.count(),
            'employees_without_users': employees_without_users.count(),
            'total_users': User.objects.count(),
            'users_with_employees': User.objects.filter(employee__isnull=False).count(),
            'users_without_employees': users_without_employees.count(),
        }
    }

    return render(request, 'hr/employee_user_management.html', context)


@login_required
@permission_required('hr.change_employee')
def create_user_for_employee(request, employee_id):
    """Create a user account for an employee"""
    employee = get_object_or_404(Employee, id=employee_id)

    if employee.user:
        messages.warning(request, _('Employee already has a user account'))
        return redirect('hr:employee_user_management')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        send_welcome_email = request.POST.get('send_welcome_email') == 'on'

        try:
            with transaction.atomic():
                user = employee.create_user_account(
                    username=username or None,
                    email=email or None,
                    password=password or None
                )

                messages.success(
                    request,
                    _('User account created successfully for {}').format(employee.get_full_name())
                )

                # TODO: Send welcome email if requested
                if send_welcome_email:
                    messages.info(request, _('Welcome email will be sent shortly'))

        except Exception as e:
            messages.error(request, _('Failed to create user account: {}').format(str(e)))

        return redirect('hr:employee_user_management')

    context = {
        'employee': employee,
        'suggested_username': employee.employee_id.lower(),
        'suggested_email': str(employee.email) if employee.email else f"{employee.employee_id.lower()}@company.com"
    }

    return render(request, 'hr/create_user_for_employee.html', context)


@login_required
@permission_required('hr.change_employee')
def link_user_to_employee(request, employee_id):
    """Link an existing user to an employee"""
    employee = get_object_or_404(Employee, id=employee_id)

    if employee.user:
        messages.warning(request, _('Employee already has a user account'))
        return redirect('hr:employee_user_management')

    if request.method == 'POST':
        user_id = request.POST.get('user_id')

        if not user_id:
            messages.error(request, _('Please select a user'))
            return redirect('hr:employee_user_management')

        try:
            user = User.objects.get(id=user_id)

            if hasattr(user, 'employee') and user.employee:
                messages.error(request, _('Selected user is already linked to another employee'))
                return redirect('hr:employee_user_management')

            with transaction.atomic():
                employee.user = user
                employee.save()

                # Update user details to match employee
                user.first_name = employee.first_name
                user.last_name = employee.last_name
                if employee.email:
                    user.email = str(employee.email)
                user.is_active = employee.is_active
                user.save()

            messages.success(
                request,
                _('User {} successfully linked to employee {}').format(user.username, employee.get_full_name())
            )

        except User.DoesNotExist:
            messages.error(request, _('Selected user does not exist'))
        except Exception as e:
            messages.error(request, _('Failed to link user: {}').format(str(e)))

        return redirect('hr:employee_user_management')

    available_users = User.objects.filter(employee__isnull=True)
    context = {
        'employee': employee,
        'available_users': available_users
    }

    return render(request, 'hr/link_user_to_employee.html', context)


@login_required
@permission_required('hr.change_employee')
def unlink_user_from_employee(request, employee_id):
    """Unlink user from employee"""
    employee = get_object_or_404(Employee, id=employee_id)

    if not employee.user:
        messages.warning(request, _('Employee does not have a user account'))
        return redirect('hr:employee_user_management')

    if request.method == 'POST':
        user = employee.user
        employee.user = None
        employee.save()

        messages.success(
            request,
            _('User {} successfully unlinked from employee {}').format(user.username, employee.get_full_name())
        )

    return redirect('hr:employee_user_management')


@login_required
def my_profile(request):
    """Show current user's employee profile"""
    employee = get_current_employee(request)

    if not employee:
        messages.warning(request, _('Your user account is not linked to an employee record'))
        return redirect('dashboard')

    context = {
        'employee': employee,
        'user': request.user,
    }

    return render(request, 'hr/my_profile.html', context)