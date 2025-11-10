from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.decorators import manager_or_admin_required

# Import policy models from their respective apps
from leave.models import LeavePolicy
from attendance.models import AttendancePolicy
from hr.models import OvertimePolicy
from hr.payroll_models import PayrollPolicy
from expenses.models import ExpensePolicy

# Import forms
from .forms import (
    LeavePolicyForm, AttendancePolicyForm, OvertimePolicyForm,
    PayrollPolicyForm, ExpensePolicyForm
)


@login_required
@manager_or_admin_required("Policies")
def policy_dashboard(request):
    """Policy management dashboard showing all policy types"""

    # Count policies (with error handling for tables that don't exist)
    def safe_count(model):
        try:
            return model.objects.count()
        except Exception:
            return 0

    leave_policies_count = safe_count(LeavePolicy)
    attendance_policies_count = safe_count(AttendancePolicy)
    overtime_policies_count = safe_count(OvertimePolicy)
    payroll_policies_count = safe_count(PayrollPolicy)
    expense_policies_count = safe_count(ExpensePolicy)

    policy_types = [
        {
            'name': 'Leave Policies',
            'description': 'Configure leave policies and allocations',
            'icon': 'bi-calendar-minus-fill',
            'count': leave_policies_count,
            'url': 'policies:leave_policy_list',
            'color': 'primary'
        },
        {
            'name': 'Attendance Policies',
            'description': 'Configure attendance rules and penalties',
            'icon': 'bi-calendar-check-fill',
            'count': attendance_policies_count,
            'url': 'policies:attendance_policy_list',
            'color': 'success'
        },
        {
            'name': 'Overtime Policies',
            'description': 'Configure overtime rates and rules',
            'icon': 'bi-clock-history',
            'count': overtime_policies_count,
            'url': 'policies:overtime_policy_list',
            'color': 'warning'
        },
        {
            'name': 'Payroll Policies',
            'description': 'Configure payroll calculation methods',
            'icon': 'bi-cash-stack',
            'count': payroll_policies_count,
            'url': 'policies:payroll_policy_list',
            'color': 'info'
        },
        {
            'name': 'Expense Policies',
            'description': 'Configure expense claim limits and rules',
            'icon': 'bi-wallet-fill',
            'count': expense_policies_count,
            'url': 'policies:expense_policy_list',
            'color': 'secondary'
        }
    ]

    context = {
        'policy_types': policy_types,
        'total_policies': sum(p['count'] for p in policy_types)
    }

    return render(request, 'policies/dashboard.html', context)


# Leave Policy Views
@login_required
@manager_or_admin_required("Leave Policies")
def leave_policy_list(request):
    """List all leave policies"""
    policies = LeavePolicy.objects.all().order_by('-created_at')

    context = {
        'policies': policies,
        'policy_type': 'Leave',
        'can_add': True
    }

    return render(request, 'policies/leave_policy_list.html', context)


# Attendance Policy Views
@login_required
@manager_or_admin_required("Attendance Policies")
def attendance_policy_list(request):
    """List all attendance policies"""
    policies = AttendancePolicy.objects.all().order_by('-created_at')

    context = {
        'policies': policies,
        'policy_type': 'Attendance',
        'can_add': True
    }

    return render(request, 'policies/attendance_policy_list.html', context)


# Overtime Policy Views
@login_required
@manager_or_admin_required("Overtime Policies")
def overtime_policy_list(request):
    """List all overtime policies"""
    policies = OvertimePolicy.objects.all().order_by('-created_at')

    context = {
        'policies': policies,
        'policy_type': 'Overtime',
        'can_add': True
    }

    return render(request, 'policies/overtime_policy_list.html', context)


# Payroll Policy Views
@login_required
@manager_or_admin_required("Payroll Policies")
def payroll_policy_list(request):
    """List all payroll policies"""
    policies = PayrollPolicy.objects.all().order_by('-created_at')

    context = {
        'policies': policies,
        'policy_type': 'Payroll',
        'can_add': True
    }

    return render(request, 'policies/payroll_policy_list.html', context)


# Expense Policy Views
@login_required
@manager_or_admin_required("Expense Policies")
def expense_policy_list(request):
    """List all expense policies"""
    try:
        policies = ExpensePolicy.objects.all().order_by('-created_at')
    except Exception:
        policies = []

    context = {
        'policies': policies,
        'policy_type': 'Expense',
        'can_add': True
    }

    return render(request, 'policies/expense_policy_list.html', context)


# ========== CREATE VIEWS ==========

@login_required
@manager_or_admin_required("Leave Policies")
def leave_policy_create(request):
    """Create a new leave policy"""
    if request.method == 'POST':
        form = LeavePolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave policy created successfully.')
            return redirect('policies:leave_policy_list')
    else:
        form = LeavePolicyForm()

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Leave',
        'action': 'Create'
    })


@login_required
@manager_or_admin_required("Attendance Policies")
def attendance_policy_create(request):
    """Create a new attendance policy"""
    if request.method == 'POST':
        form = AttendancePolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance policy created successfully.')
            return redirect('policies:attendance_policy_list')
    else:
        form = AttendancePolicyForm()

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Attendance',
        'action': 'Create'
    })


@login_required
@manager_or_admin_required("Overtime Policies")
def overtime_policy_create(request):
    """Create a new overtime policy"""
    if request.method == 'POST':
        form = OvertimePolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Overtime policy created successfully.')
            return redirect('policies:overtime_policy_list')
    else:
        form = OvertimePolicyForm()

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Overtime',
        'action': 'Create'
    })


@login_required
@manager_or_admin_required("Payroll Policies")
def payroll_policy_create(request):
    """Create a new payroll policy"""
    if request.method == 'POST':
        form = PayrollPolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll policy created successfully.')
            return redirect('policies:payroll_policy_list')
    else:
        form = PayrollPolicyForm()

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Payroll',
        'action': 'Create'
    })


@login_required
@manager_or_admin_required("Expense Policies")
def expense_policy_create(request):
    """Create a new expense policy"""
    if request.method == 'POST':
        form = ExpensePolicyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense policy created successfully.')
            return redirect('policies:expense_policy_list')
    else:
        form = ExpensePolicyForm()

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Expense',
        'action': 'Create'
    })


# ========== EDIT VIEWS ==========

@login_required
@manager_or_admin_required("Leave Policies")
def leave_policy_edit(request, pk):
    """Edit a leave policy"""
    policy = get_object_or_404(LeavePolicy, pk=pk)
    if request.method == 'POST':
        form = LeavePolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave policy updated successfully.')
            return redirect('policies:leave_policy_list')
    else:
        form = LeavePolicyForm(instance=policy)

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Leave',
        'action': 'Edit',
        'policy': policy
    })


@login_required
@manager_or_admin_required("Attendance Policies")
def attendance_policy_edit(request, pk):
    """Edit an attendance policy"""
    policy = get_object_or_404(AttendancePolicy, pk=pk)
    if request.method == 'POST':
        form = AttendancePolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Attendance policy updated successfully.')
            return redirect('policies:attendance_policy_list')
    else:
        form = AttendancePolicyForm(instance=policy)

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Attendance',
        'action': 'Edit',
        'policy': policy
    })


@login_required
@manager_or_admin_required("Overtime Policies")
def overtime_policy_edit(request, pk):
    """Edit an overtime policy"""
    policy = get_object_or_404(OvertimePolicy, pk=pk)
    if request.method == 'POST':
        form = OvertimePolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Overtime policy updated successfully.')
            return redirect('policies:overtime_policy_list')
    else:
        form = OvertimePolicyForm(instance=policy)

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Overtime',
        'action': 'Edit',
        'policy': policy
    })


@login_required
@manager_or_admin_required("Payroll Policies")
def payroll_policy_edit(request, pk):
    """Edit a payroll policy"""
    policy = get_object_or_404(PayrollPolicy, pk=pk)
    if request.method == 'POST':
        form = PayrollPolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Payroll policy updated successfully.')
            return redirect('policies:payroll_policy_list')
    else:
        form = PayrollPolicyForm(instance=policy)

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Payroll',
        'action': 'Edit',
        'policy': policy
    })


@login_required
@manager_or_admin_required("Expense Policies")
def expense_policy_edit(request, pk):
    """Edit an expense policy"""
    policy = get_object_or_404(ExpensePolicy, pk=pk)
    if request.method == 'POST':
        form = ExpensePolicyForm(request.POST, instance=policy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense policy updated successfully.')
            return redirect('policies:expense_policy_list')
    else:
        form = ExpensePolicyForm(instance=policy)

    return render(request, 'policies/policy_form.html', {
        'form': form,
        'policy_type': 'Expense',
        'action': 'Edit',
        'policy': policy
    })
