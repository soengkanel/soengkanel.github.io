from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django.template.loader import get_template
from datetime import datetime, date
from decimal import Decimal
import json

from hr.models import Employee
from .models import (
    PayrollPeriod, Payroll, EmployeeSalary, SalaryAdvance,
    EmployeeLoan, PayslipTemplate, SalaryComponent, TaxSlab, NSSFConfiguration
)


@login_required
def payroll_dashboard(request):
    """Payroll dashboard with overview statistics"""
    current_month = date.today().replace(day=1)

    context = {
        'total_employees': Employee.objects.filter(employment_status='active').count(),
        'total_processed': Payroll.objects.filter(
            payroll_period__start_date__month=current_month.month,
            status='PAID'
        ).count(),
        'pending_advances': SalaryAdvance.objects.filter(status='PENDING').count(),
        'active_loans': EmployeeLoan.objects.filter(status='ACTIVE').count(),
        'current_period': PayrollPeriod.objects.filter(
            start_date__lte=current_month,
            end_date__gte=current_month
        ).first(),
    }

    # Recent payroll periods
    context['recent_periods'] = PayrollPeriod.objects.all()[:5]

    return render(request, 'payroll/dashboard.html', context)


@login_required
def payroll_periods(request):
    """List all payroll periods"""
    periods = PayrollPeriod.objects.all()

    # Status filter
    status_filter = request.GET.get('status', '').upper()
    if status_filter and status_filter in ['DRAFT', 'PROCESSING', 'APPROVED', 'PAID', 'CANCELLED']:
        periods = periods.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        periods = periods.filter(
            Q(name__icontains=search_query) |
            Q(status__icontains=search_query)
        )

    # Calculate statistics based on filtered periods
    stats = {
        'total': periods.count(),
        'draft': periods.filter(status='DRAFT').count(),
        'processing': periods.filter(status='PROCESSING').count(),
        'approved': periods.filter(status='APPROVED').count(),
        'paid': periods.filter(status='PAID').count(),
        'cancelled': periods.filter(status='CANCELLED').count(),
    }

    # Pagination
    paginator = Paginator(periods, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/periods/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': request.GET.get('status', ''),
        'stats': stats,
    })


@login_required
def create_payroll_period(request):
    """Create new payroll period"""
    if request.method == 'POST':
        try:
            name = request.POST['name']
            period_type = request.POST['period_type']
            status = request.POST.get('status', 'DRAFT')
            start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').date()
            payment_date = datetime.strptime(request.POST['payment_date'], '%Y-%m-%d').date()

            # Check for overlapping periods
            overlapping = PayrollPeriod.objects.filter(
                Q(start_date__lte=start_date, end_date__gte=start_date) |
                Q(start_date__lte=end_date, end_date__gte=end_date)
            ).exists()

            if overlapping:
                messages.error(request, 'This period overlaps with an existing period.')
                return render(request, 'payroll/periods/create.html')

            period = PayrollPeriod.objects.create(
                name=name,
                period_type=period_type,
                status=status,
                start_date=start_date,
                end_date=end_date,
                payment_date=payment_date,
                created_by=request.user
            )

            messages.success(request, f'Payroll period "{name}" created successfully.')
            return redirect('payroll:period_detail', period_id=period.id)

        except Exception as e:
            messages.error(request, f'Error creating period: {str(e)}')

    return render(request, 'payroll/periods/create.html')


@login_required
def edit_payroll_period(request, period_id):
    """Edit existing payroll period"""
    period = get_object_or_404(PayrollPeriod, id=period_id)

    if request.method == 'POST':
        try:
            name = request.POST['name']
            period_type = request.POST['period_type']
            status = request.POST.get('status', 'DRAFT')
            start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').date()
            payment_date = datetime.strptime(request.POST['payment_date'], '%Y-%m-%d').date()

            # Check for overlapping periods (excluding current period)
            overlapping = PayrollPeriod.objects.filter(
                Q(start_date__lte=start_date, end_date__gte=start_date) |
                Q(start_date__lte=end_date, end_date__gte=end_date)
            ).exclude(id=period_id).exists()

            if overlapping:
                messages.error(request, 'This period overlaps with an existing period.')
                return render(request, 'payroll/periods/edit.html', {'period': period})

            # Update period
            period.name = name
            period.period_type = period_type
            period.status = status
            period.start_date = start_date
            period.end_date = end_date
            period.payment_date = payment_date
            period.save()

            messages.success(request, f'Payroll period "{name}" updated successfully.')
            return redirect('payroll:period_detail', period_id=period.id)

        except Exception as e:
            messages.error(request, f'Error updating period: {str(e)}')

    return render(request, 'payroll/periods/edit.html', {'period': period})


@login_required
def payroll_period_detail(request, period_id):
    """View payroll period details"""
    from .models import SalaryStructure, SalaryStructureAssignment

    period = get_object_or_404(PayrollPeriod, id=period_id)
    payrolls = period.salary_slips.all()

    # Update summary if requested or if summary is empty
    if request.GET.get('refresh') or period.total_employees == 0:
        period.update_summary()

    # Check prerequisites for payroll generation
    prerequisites = {
        'salary_components': SalaryComponent.objects.filter(is_active=True).count(),
        'salary_structures': SalaryStructure.objects.filter(is_active=True).count(),
        'active_employees': Employee.objects.filter(employment_status='active').count(),
        'employees_with_assignments': SalaryStructureAssignment.objects.filter(
            employee__employment_status='active',
            from_date__lte=period.end_date,
            is_active=True,
            docstatus=1
        ).values('employee').distinct().count()
    }

    # Calculate readiness
    prerequisites['is_ready'] = (
        prerequisites['salary_components'] > 0 and
        prerequisites['salary_structures'] > 0 and
        prerequisites['active_employees'] > 0 and
        prerequisites['employees_with_assignments'] > 0
    )

    # Statistics - use cached summary from period model
    stats = {
        'total_employees': period.total_employees,
        'processed_employees': period.processed_employees,
        'total_gross': period.total_gross_pay,
        'total_deductions': period.total_deductions,
        'total_net': period.total_net_pay,
        'working_days': period.working_days,
        'is_current': period.is_current,
        'status_counts': payrolls.values('status').annotate(count=Count('status'))
    }

    return render(request, 'payroll/periods/detail.html', {
        'period': period,
        'payrolls': payrolls,
        'stats': stats,
        'prerequisites': prerequisites
    })


@login_required
def payroll_period_delete(request, period_id):
    """Delete a payroll period with cascade deletion"""
    period = get_object_or_404(PayrollPeriod, id=period_id)

    # Prevent deletion of APPROVED or PAID periods for safety
    if period.status in ['APPROVED', 'PAID']:
        messages.error(request, f'Cannot delete {period.name}. {period.get_status_display()} periods cannot be deleted.')
        return redirect('payroll:periods')

    if request.method == 'POST':
        # Get counts of related records that will be cascade deleted
        salary_slips_count = period.salary_slips.count()

        # Count benefits related to this period
        from payroll.models import EmployeeBenefit
        benefits_count = EmployeeBenefit.objects.filter(payroll_period=period).count()

        period_name = period.name

        # Perform cascade delete
        period.delete()

        # Show detailed success message
        deleted_items = []
        if salary_slips_count > 0:
            deleted_items.append(f'{salary_slips_count} salary slip(s)')
        if benefits_count > 0:
            deleted_items.append(f'{benefits_count} employee benefit(s)')

        if deleted_items:
            details = ' and '.join(deleted_items)
            messages.success(request, f'Payroll period "{period_name}" and {details} have been deleted successfully.')
        else:
            messages.success(request, f'Payroll period "{period_name}" has been deleted successfully.')

        return redirect('payroll:periods')

    # GET request - redirect to list
    return redirect('payroll:periods')


@login_required
def generate_payroll(request, period_id):
    """Generate payroll for all employees in a period"""
    from .models import SalaryStructure, SalaryStructureAssignment

    period = get_object_or_404(PayrollPeriod, id=period_id)

    if request.method == 'POST':
        try:
            # === PREREQUISITE CHECKS ===

            # Check 1: Verify salary components exist
            component_count = SalaryComponent.objects.filter(is_active=True).count()
            if component_count == 0:
                messages.error(
                    request,
                    'No salary components found! Please set up salary components first. '
                    'Go to Payroll > Salary Components to create basic salary, allowances, and deductions.'
                )
                return redirect('payroll:period_detail', period_id=period_id)

            # Check 2: Verify at least one salary structure exists
            structure_count = SalaryStructure.objects.filter(is_active=True).count()
            if structure_count == 0:
                messages.error(
                    request,
                    'No salary structures found! Please create at least one salary structure first. '
                    'Go to Payroll > Salary Structures to define salary structures with components.'
                )
                return redirect('payroll:period_detail', period_id=period_id)

            # Check 3: Get all active employees
            employees = Employee.objects.filter(employment_status='active')

            if employees.count() == 0:
                messages.warning(request, 'No active employees found to generate payroll for.')
                return redirect('payroll:period_detail', period_id=period_id)

            # Check 4: Count employees with salary structure assignments
            employees_with_assignments = SalaryStructureAssignment.objects.filter(
                employee__in=employees,
                from_date__lte=period.end_date,
                is_active=True,
                docstatus=1
            ).values_list('employee_id', flat=True).distinct()

            employees_without_assignments = employees.exclude(id__in=employees_with_assignments)

            if employees_without_assignments.count() == employees.count():
                # NO employees have assignments
                messages.error(
                    request,
                    f'None of the {employees.count()} active employees have salary structure assignments! '
                    'Please assign salary structures to employees first. '
                    'Go to Payroll > Salary Structure Assignments.'
                )
                return redirect('payroll:period_detail', period_id=period_id)

            # === GENERATE PAYROLL ===

            created_count = 0
            updated_count = 0
            skipped_count = 0
            skipped_employees = []

            # Calculate working days from period (excluding weekends)
            working_days = period.working_days

            for employee in employees:
                # Check if employee has salary structure assignment
                has_assignment = SalaryStructureAssignment.objects.filter(
                    employee=employee,
                    from_date__lte=period.end_date,
                    is_active=True,
                    docstatus=1
                ).exists()

                if not has_assignment:
                    skipped_count += 1
                    skipped_employees.append(employee.get_full_name())
                    continue

                # Check if salary slip already exists
                existing_slip = Payroll.objects.filter(
                    payroll_period=period,
                    employee=employee
                ).first()

                if existing_slip:
                    # Update existing slip
                    existing_slip.total_working_days = working_days
                    existing_slip.payment_days = working_days
                    existing_slip.calculate_from_salary_structure()
                    updated_count += 1
                else:
                    # Create new salary slip
                    salary_slip = Payroll.objects.create(
                        employee=employee,
                        payroll_period=period,
                        start_date=period.start_date,
                        end_date=period.end_date,
                        total_working_days=working_days,
                        payment_days=working_days,
                        created_by=request.user
                    )

                    # Calculate salary from structure
                    salary_slip.calculate_from_salary_structure()
                    created_count += 1

            # Update period status and summary metrics
            period.status = 'PROCESSING'
            period.processed_by = request.user
            period.processed_at = timezone.now()
            period.save()

            # Update summary totals from generated salary slips
            period.update_summary()

            # Show results
            success_msg = f'Payroll generated: {created_count} new, {updated_count} updated. Working days: {working_days}'

            if skipped_count > 0:
                messages.warning(
                    request,
                    f'{success_msg} | {skipped_count} employees skipped (no salary structure assignment): '
                    f'{", ".join(skipped_employees[:5])}'
                    f'{"..." if len(skipped_employees) > 5 else ""}'
                )
            else:
                messages.success(request, success_msg)

        except Exception as e:
            messages.error(request, f'Error generating payroll: {str(e)}')

    return redirect('payroll:period_detail', period_id=period_id)


@login_required
def payroll_detail(request, payroll_id):
    """View individual payroll details"""
    payroll = get_object_or_404(Payroll, id=payroll_id)

    # Get earnings and deductions from SalarySlipDetail
    earnings = payroll.details.filter(
        salary_component__component_type='EARNING',
        salary_component__is_statistical_component=False
    ).select_related('salary_component').order_by('salary_component__display_order')

    deductions = payroll.details.filter(
        salary_component__component_type='DEDUCTION',
        salary_component__is_statistical_component=False
    ).select_related('salary_component').order_by('salary_component__display_order')

    # Calculate employer NSSF
    try:
        _, employer_nssf = payroll.calculate_nssf()
    except:
        employer_nssf = Decimal('0')

    return render(request, 'payroll/payroll_detail.html', {
        'payroll': payroll,
        'earnings': earnings,
        'deductions': deductions,
        'employer_nssf': employer_nssf,
    })


@login_required
def employee_salary_list(request):
    """List all employee salary configurations - using SalaryStructureAssignment"""
    from .models import SalaryStructureAssignment

    # Get period filter
    period_id = request.GET.get('period')
    selected_period = None

    # Get base query for salary assignments
    base_query = SalaryStructureAssignment.objects.select_related(
        'employee', 'salary_structure'
    ).filter(is_active=True)

    # Filter by period if selected
    if period_id:
        selected_period = get_object_or_404(PayrollPeriod, id=period_id)
        # Filter assignments that were active during the period
        base_query = base_query.filter(
            from_date__lte=selected_period.end_date
        ).filter(
            Q(to_date__isnull=True) | Q(to_date__gte=selected_period.start_date)
        )

    # Get all assignments (filtered by period if applicable)
    all_assignments = base_query

    # Calculate statistics based on filtered data
    active_assignments = all_assignments.filter(employee__employment_status='active')

    stats = {
        'total': all_assignments.count(),
        'active_employees': active_assignments.count(),
        'bank_transfer': 0,  # SalaryStructureAssignment doesn't have payment_method
        'cash': 0,
        'timesheet_based': active_assignments.filter(salary_structure__salary_slip_based_on_timesheet=True).count(),
        'attendance_based': active_assignments.filter(salary_structure__salary_slip_based_on_timesheet=False).count(),
    }

    # Calculate total payroll and average (using base_salary from filtered assignments)
    total_payroll = sum(assignment.base_salary for assignment in active_assignments)
    total_count = active_assignments.count()
    average_salary = total_payroll / total_count if total_count > 0 else 0

    # Use active employees for the main list
    assignments = active_assignments

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        assignments = assignments.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    # Create wrapper objects that match template expectations
    class SalaryWrapper:
        """Wrapper to make SalaryStructureAssignment compatible with EmployeeSalary template"""
        def __init__(self, assignment):
            from .models import SalarySlip

            self.id = assignment.id
            self.employee = assignment.employee
            self.is_active = assignment.is_active
            self.salary_structure = assignment.salary_structure  # Add salary structure for template access
            # For SalaryStructureAssignment, base_salary is the main salary
            self.basic_salary = assignment.base_salary
            # Calculate allowances from salary structure (simplified - use 15% for housing, fixed for others)
            self.housing_allowance = assignment.base_salary * Decimal('0.15')
            self.transport_allowance = Decimal('100000')  # KHR 100,000
            self.meal_allowance = Decimal('50000')  # KHR 50,000
            self.phone_allowance = Decimal('0')
            self.seniority_allowance = Decimal('0')
            self.gross_salary = (self.basic_salary + self.housing_allowance +
                               self.transport_allowance + self.meal_allowance)
            self.payment_method = 'BANK_TRANSFER'  # Default

            # Fetch latest salary slip for this employee
            self.latest_slip = SalarySlip.objects.filter(
                employee=assignment.employee
            ).order_by('-payroll_period__end_date').first()

        def get_payment_method_display(self):
            return 'Bank Transfer'

    # Wrap assignments
    wrapped_assignments = [SalaryWrapper(assignment) for assignment in assignments]

    # Pagination with per_page handling
    per_page = request.GET.get('per_page', '20')
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 25, 50, 100, 200]:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20

    paginator = Paginator(wrapped_assignments, per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Get all payroll periods for filter dropdown
    periods = PayrollPeriod.objects.all().order_by('-start_date')[:12]  # Last 12 periods

    return render(request, 'payroll/salary/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'stats': stats,
        'total_payroll': total_payroll,
        'average_salary': average_salary,
        'periods': periods,
        'selected_period': selected_period,
        'per_page': per_page,
    })


@login_required
def salary_advances_list(request):
    """List salary advances"""
    advances = SalaryAdvance.objects.select_related('employee').all()

    # Calculate statistics
    stats = {
        'total': advances.count(),
        'pending': advances.filter(status='PENDING').count(),
        'approved': advances.filter(status='APPROVED').count(),
        'rejected': advances.filter(status='REJECTED').count(),
        'paid': advances.filter(status='PAID').count(),
    }

    # Calculate total amounts
    total_pending_amount = advances.filter(status='PENDING').aggregate(Sum('amount'))['amount__sum'] or 0
    total_approved_amount = advances.filter(status='APPROVED').aggregate(Sum('amount'))['amount__sum'] or 0

    # Filter by status
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        advances = advances.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        advances = advances.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(advances, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/advances/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'stats': stats,
        'total_pending_amount': total_pending_amount,
        'total_approved_amount': total_approved_amount,
    })


@login_required
def salary_advance_create(request):
    """Create a new salary advance"""
    if request.method == 'POST':
        try:
            employee_id = request.POST['employee']
            amount = Decimal(request.POST['amount'])
            request_date = datetime.strptime(request.POST['request_date'], '%Y-%m-%d').date()
            repayment_method = request.POST['repayment_method']
            installment_months = int(request.POST.get('installment_months', 1))
            reason = request.POST['reason']
            remarks = request.POST.get('remarks', '')

            employee = Employee.objects.get(id=employee_id)

            advance = SalaryAdvance.objects.create(
                employee=employee,
                amount=amount,
                request_date=request_date,
                repayment_method=repayment_method,
                installment_months=installment_months,
                reason=reason,
                remarks=remarks,
                status='PENDING',
                requested_by=request.user
            )

            messages.success(request, f'Salary advance for {employee.get_full_name()} created successfully.')
            return redirect('payroll:salary_advance_detail', advance_id=advance.id)

        except Exception as e:
            messages.error(request, f'Error creating salary advance: {str(e)}')

    # Get active employees
    employees = Employee.objects.filter(employment_status='active').order_by('first_name', 'last_name')

    return render(request, 'payroll/advances/create.html', {
        'employees': employees
    })


@login_required
def salary_advance_detail(request, advance_id):
    """View salary advance details"""
    advance = get_object_or_404(SalaryAdvance, id=advance_id)

    return render(request, 'payroll/advances/detail.html', {
        'advance': advance
    })


@login_required
def salary_advance_edit(request, advance_id):
    """Edit a salary advance"""
    advance = get_object_or_404(SalaryAdvance, id=advance_id)

    if request.method == 'POST':
        try:
            advance.amount = Decimal(request.POST['amount'])
            advance.request_date = datetime.strptime(request.POST['request_date'], '%Y-%m-%d').date()
            advance.repayment_method = request.POST['repayment_method']
            advance.installment_months = int(request.POST.get('installment_months', 1))
            advance.reason = request.POST['reason']
            advance.remarks = request.POST.get('remarks', '')
            advance.save()

            messages.success(request, 'Salary advance updated successfully.')
            return redirect('payroll:salary_advance_detail', advance_id=advance.id)

        except Exception as e:
            messages.error(request, f'Error updating salary advance: {str(e)}')

    return render(request, 'payroll/advances/edit.html', {
        'advance': advance
    })


@login_required
def salary_advance_approve(request, advance_id):
    """Approve a salary advance"""
    advance = get_object_or_404(SalaryAdvance, id=advance_id)

    if request.method == 'POST':
        try:
            approval_date = datetime.strptime(request.POST.get('approval_date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date()

            advance.status = 'APPROVED'
            advance.approval_date = approval_date
            advance.approved_by = request.user
            advance.save()

            messages.success(request, f'Salary advance for {advance.employee.get_full_name()} approved successfully.')
            return redirect('payroll:salary_advance_detail', advance_id=advance.id)

        except Exception as e:
            messages.error(request, f'Error approving salary advance: {str(e)}')

    return render(request, 'payroll/advances/approve.html', {
        'advance': advance
    })


@login_required
def salary_advance_reject(request, advance_id):
    """Reject a salary advance"""
    advance = get_object_or_404(SalaryAdvance, id=advance_id)

    if request.method == 'POST':
        try:
            remarks = request.POST.get('remarks', '')

            advance.status = 'REJECTED'
            advance.remarks = remarks
            advance.approved_by = request.user
            advance.save()

            messages.success(request, f'Salary advance for {advance.employee.get_full_name()} rejected.')
            return redirect('payroll:salary_advance_detail', advance_id=advance.id)

        except Exception as e:
            messages.error(request, f'Error rejecting salary advance: {str(e)}')

    return render(request, 'payroll/advances/reject.html', {
        'advance': advance
    })


@login_required
def salary_advance_delete(request, advance_id):
    """Delete a salary advance"""
    advance = get_object_or_404(SalaryAdvance, id=advance_id)

    if request.method == 'POST':
        employee_name = advance.employee.get_full_name()
        advance.delete()
        messages.success(request, f'Salary advance for {employee_name} deleted successfully.')
        return redirect('payroll:advances_list')

    return render(request, 'payroll/advances/delete_confirm.html', {
        'advance': advance
    })


@login_required
def employee_loans_list(request):
    """List employee loans"""
    loans = EmployeeLoan.objects.select_related('employee').all()

    # Calculate statistics
    all_loans = EmployeeLoan.objects.all()
    stats = {
        'total': all_loans.count(),
        'pending': all_loans.filter(status='PENDING').count(),
        'approved': all_loans.filter(status='APPROVED').count(),
        'active': all_loans.filter(status='ACTIVE').count(),
        'completed': all_loans.filter(status='COMPLETED').count(),
        'defaulted': all_loans.filter(status='DEFAULTED').count(),
    }

    # Calculate total active loan amount
    total_active_amount = all_loans.filter(status='ACTIVE').aggregate(
        total=Sum('remaining_balance')
    )['total'] or 0

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        loans = loans.filter(status=status_filter)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        loans = loans.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(loans, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/loans/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'stats': stats,
        'total_active_amount': total_active_amount,
    })


@login_required
def employee_loan_create(request):
    """Create a new employee loan"""
    if request.method == 'POST':
        try:
            from dateutil.relativedelta import relativedelta

            employee_id = request.POST['employee']
            loan_amount = Decimal(request.POST['loan_amount'])
            interest_rate = Decimal(request.POST.get('interest_rate', '0'))
            loan_term_months = int(request.POST['loan_term_months'])
            start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
            purpose = request.POST['purpose']
            remarks = request.POST.get('remarks', '')

            employee = Employee.objects.get(id=employee_id)

            # Calculate end date
            end_date = start_date + relativedelta(months=loan_term_months)

            # Create temporary loan object to calculate monthly installment
            temp_loan = EmployeeLoan(
                employee=employee,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                loan_term_months=loan_term_months,
                start_date=start_date,
                end_date=end_date,
                purpose=purpose
            )
            monthly_installment = temp_loan.calculate_monthly_installment()

            # Create the actual loan
            loan = EmployeeLoan.objects.create(
                employee=employee,
                loan_amount=loan_amount,
                interest_rate=interest_rate,
                loan_term_months=loan_term_months,
                monthly_installment=monthly_installment,
                start_date=start_date,
                end_date=end_date,
                total_paid=Decimal('0.00'),
                remaining_balance=loan_amount,
                purpose=purpose,
                remarks=remarks,
                status='PENDING',
                requested_by=request.user
            )

            messages.success(request, f'Loan for {employee.get_full_name()} created successfully.')
            return redirect('payroll:employee_loan_detail', loan_id=loan.id)

        except Exception as e:
            messages.error(request, f'Error creating loan: {str(e)}')

    # Get active employees
    employees = Employee.objects.filter(employment_status='active').order_by('first_name', 'last_name')

    return render(request, 'payroll/loans/create.html', {
        'employees': employees
    })


@login_required
def employee_loan_detail(request, loan_id):
    """View employee loan details"""
    loan = get_object_or_404(EmployeeLoan, id=loan_id)

    return render(request, 'payroll/loans/detail.html', {
        'loan': loan
    })


@login_required
def employee_loan_edit(request, loan_id):
    """Edit an employee loan"""
    loan = get_object_or_404(EmployeeLoan, id=loan_id)

    if request.method == 'POST':
        try:
            from dateutil.relativedelta import relativedelta

            loan.loan_amount = Decimal(request.POST['loan_amount'])
            loan.interest_rate = Decimal(request.POST.get('interest_rate', '0'))
            loan.loan_term_months = int(request.POST['loan_term_months'])
            loan.start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
            loan.purpose = request.POST['purpose']
            loan.remarks = request.POST.get('remarks', '')

            # Recalculate end date
            loan.end_date = loan.start_date + relativedelta(months=loan.loan_term_months)

            # Recalculate monthly installment
            loan.monthly_installment = loan.calculate_monthly_installment()

            # Update remaining balance
            loan.remaining_balance = loan.loan_amount - loan.total_paid

            loan.save()

            messages.success(request, 'Employee loan updated successfully.')
            return redirect('payroll:employee_loan_detail', loan_id=loan.id)

        except Exception as e:
            messages.error(request, f'Error updating loan: {str(e)}')

    return render(request, 'payroll/loans/edit.html', {
        'loan': loan
    })


@login_required
def employee_loan_approve(request, loan_id):
    """Approve an employee loan"""
    loan = get_object_or_404(EmployeeLoan, id=loan_id)

    if request.method == 'POST':
        try:
            loan.status = 'APPROVED'
            loan.approved_by = request.user
            loan.save()

            messages.success(request, f'Loan for {loan.employee.get_full_name()} approved successfully.')
            return redirect('payroll:employee_loan_detail', loan_id=loan.id)

        except Exception as e:
            messages.error(request, f'Error approving loan: {str(e)}')

    return render(request, 'payroll/loans/approve.html', {
        'loan': loan
    })


@login_required
def employee_loan_activate(request, loan_id):
    """Activate an approved loan"""
    loan = get_object_or_404(EmployeeLoan, id=loan_id)

    if request.method == 'POST':
        try:
            if loan.status != 'APPROVED':
                messages.error(request, 'Only approved loans can be activated.')
                return redirect('payroll:employee_loan_detail', loan_id=loan.id)

            loan.status = 'ACTIVE'
            loan.save()

            messages.success(request, f'Loan for {loan.employee.get_full_name()} activated successfully.')
            return redirect('payroll:employee_loan_detail', loan_id=loan.id)

        except Exception as e:
            messages.error(request, f'Error activating loan: {str(e)}')

    return render(request, 'payroll/loans/activate.html', {
        'loan': loan
    })


@login_required
def employee_loan_cancel(request, loan_id):
    """Cancel an employee loan"""
    loan = get_object_or_404(EmployeeLoan, id=loan_id)

    if request.method == 'POST':
        try:
            remarks = request.POST.get('remarks', '')

            loan.status = 'CANCELLED'
            loan.remarks = remarks
            loan.save()

            messages.success(request, f'Loan for {loan.employee.get_full_name()} cancelled.')
            return redirect('payroll:employee_loan_detail', loan_id=loan.id)

        except Exception as e:
            messages.error(request, f'Error cancelling loan: {str(e)}')

    return render(request, 'payroll/loans/cancel.html', {
        'loan': loan
    })


@login_required
def employee_loan_delete(request, loan_id):
    """Delete an employee loan"""
    loan = get_object_or_404(EmployeeLoan, id=loan_id)

    if request.method == 'POST':
        employee_name = loan.employee.get_full_name()
        loan.delete()
        messages.success(request, f'Loan for {employee_name} deleted successfully.')
        return redirect('payroll:loans_list')

    return render(request, 'payroll/loans/delete_confirm.html', {
        'loan': loan
    })


@login_required
def payroll_reports(request):
    """Payroll reports page"""
    periods = PayrollPeriod.objects.all().order_by('-start_date')[:12]  # Last 12 periods

    # Get all payrolls
    payrolls = Payroll.objects.select_related('employee', 'payroll_period').all()

    # Filter by period
    period_id = request.GET.get('period')
    selected_period = None
    if period_id:
        payrolls = payrolls.filter(payroll_period_id=period_id)
        selected_period = PayrollPeriod.objects.filter(id=period_id).first()

    # Filter by employee search
    search_query = request.GET.get('search', '')
    if search_query:
        payrolls = payrolls.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        payrolls = payrolls.filter(status=status_filter)

    # Order by most recent
    payrolls = payrolls.order_by('-payroll_period__start_date', 'employee__first_name')

    # Pagination
    paginator = Paginator(payrolls, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/reports/index.html', {
        'periods': periods,
        'payrolls': page_obj,
        'selected_period': selected_period,
        'search_query': search_query,        
        'status_filter': status_filter,     
    })


@login_required
def generate_payslip(request, payroll_id):
    """Generate payslip PDF for a specific payroll"""
    payroll = get_object_or_404(Payroll, id=payroll_id)

    # Get payslip template
    template = PayslipTemplate.objects.filter(is_default=True, is_active=True).first()

    if not template:
        messages.error(request, 'No payslip template found. Please create a default template.')
        return redirect('payroll:payroll_detail', payroll_id=payroll_id)

    context = {
        'payroll': payroll,
        'employee': payroll.employee,
        'period': payroll.payroll_period,
        'template': template
    }

    return render(request, 'payroll/payslip/payslip.html', context)


@login_required
def payslip_view(request, salary_slip_id):
    """View/print payslip using SalarySlip model - ERPNext style"""
    from .models import SalarySlip, SalarySlipDetail
    from company.models import Company

    salary_slip = get_object_or_404(
        SalarySlip.objects.select_related(
            'employee', 'payroll_period', 'salary_structure'
        ).prefetch_related('details__salary_component'),
        id=salary_slip_id
    )

    # Get company information
    company = None
    if hasattr(request, 'tenant'):
        company = request.tenant
    else:
        try:
            company = Company.objects.first()
        except:
            pass

    # Separate earnings and deductions
    earnings = salary_slip.details.filter(
        salary_component__component_type='EARNING',
        salary_component__is_statistical_component=False
    ).select_related('salary_component').order_by('salary_component__display_order')

    deductions = salary_slip.details.filter(
        salary_component__component_type='DEDUCTION',
        salary_component__is_statistical_component=False
    ).select_related('salary_component').order_by('salary_component__display_order')

    context = {
        'salary_slip': salary_slip,
        'employee': salary_slip.employee,
        'company': company,
        'earnings': earnings,
        'deductions': deductions,
    }

    # Add timesheet and project data for timesheet-based payslips
    if salary_slip.salary_structure and salary_slip.salary_structure.salary_slip_based_on_timesheet:
        # Get timesheet data for this period
        from project.models import Timesheet
        timesheets = Timesheet.objects.filter(
            employee=salary_slip.employee,
            start_date__lte=salary_slip.end_date,
            end_date__gte=salary_slip.start_date,
            status='approved'
        ).prefetch_related('details__project')

        # Get unique projects from timesheet details
        projects_summary = {}
        total_billable = 0

        for timesheet in timesheets:
            for detail in timesheet.details.all():
                if detail.project:
                    project_name = detail.project.project_name
                    if project_name not in projects_summary:
                        projects_summary[project_name] = {
                            'hours': 0,
                            'amount': 0,
                            'project': detail.project
                        }
                    projects_summary[project_name]['hours'] += float(detail.hours)
                    projects_summary[project_name]['amount'] += float(detail.billing_amount or 0)
                    if detail.is_billable:
                        total_billable += float(detail.hours)

        context['timesheets'] = timesheets
        context['projects_summary'] = projects_summary
        context['total_billable_hours'] = total_billable

    # Get overtime data from attendance records
    try:
        from attendance.models import AttendanceRecord
        overtime_records = AttendanceRecord.objects.filter(
            employee=salary_slip.employee,
            date__range=[salary_slip.start_date, salary_slip.end_date],
            overtime_hours__gt=0
        )

        total_overtime_hours = sum(float(record.overtime_hours) for record in overtime_records)

        # Calculate overtime amount if there's an overtime component
        overtime_amount = Decimal('0')
        if total_overtime_hours > 0 and salary_slip.hour_rate:
            # Calculate based on hourly rate and overtime multiplier
            overtime_amount = Decimal(str(total_overtime_hours)) * salary_slip.hour_rate * salary_slip.overtime_rate
        elif total_overtime_hours > 0 and salary_slip.base_salary and salary_slip.total_working_days:
            # Calculate hourly rate from monthly salary
            hours_per_day = Decimal('8')  # Standard 8 hours per day
            total_standard_hours = Decimal(str(salary_slip.total_working_days)) * hours_per_day
            hourly_rate = salary_slip.base_salary / total_standard_hours if total_standard_hours > 0 else Decimal('0')
            overtime_amount = Decimal(str(total_overtime_hours)) * hourly_rate * salary_slip.overtime_rate

        context['overtime_hours'] = total_overtime_hours
        context['overtime_amount'] = overtime_amount
        context['overtime_records'] = overtime_records
    except:
        context['overtime_hours'] = 0
        context['overtime_amount'] = Decimal('0')

    # Use unified compact receipt template for all payslips
    return render(request, 'payroll/payslip/salary_slip.html', context)


@login_required
def ajax_calculate_payroll(request):
    """AJAX endpoint to calculate payroll"""
    if request.method == 'POST':
        try:
            payroll_id = request.POST.get('payroll_id')
            payroll = get_object_or_404(Payroll, id=payroll_id)

            # Update fields from POST data
            for field in ['basic_salary', 'housing_allowance', 'transport_allowance',
                         'meal_allowance', 'phone_allowance', 'seniority_allowance',
                         'overtime_amount', 'bonus', 'other_earnings',
                         'advance_salary', 'loan_deduction', 'other_deductions']:
                if field in request.POST:
                    setattr(payroll, field, Decimal(request.POST[field] or '0'))

            # Calculate payroll
            payroll.calculate()

            return JsonResponse({
                'success': True,
                'gross_salary': float(payroll.gross_pay),
                'total_deductions': float(payroll.total_deduction),
                'net_salary': float(payroll.net_pay),
                'salary_tax': float(payroll.salary_tax),
                'nssf_employee': float(payroll.nssf_employee),
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


# Salary Structure Management Views
@login_required
def salary_structure_list(request):
    """List all salary structures"""
    from .models import SalaryStructure, SalaryStructureAssignment
    from django.db.models import Count

    all_structures = SalaryStructure.objects.annotate(
        salary_slips_count=Count('salaryslip', distinct=True)
    )

    # Calculate statistics
    stats = {
        'total': all_structures.count(),
        'active': all_structures.filter(is_active=True).count(),
        'inactive': all_structures.filter(is_active=False).count(),
        'total_assignments': SalaryStructureAssignment.objects.filter(is_active=True).count(),
    }

    structures = all_structures

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        structures = structures.filter(
            Q(name__icontains=search_query) |
            Q(company__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'active':
            structures = structures.filter(is_active=True)
        elif status_filter == 'inactive':
            structures = structures.filter(is_active=False)

    # Pagination
    paginator = Paginator(structures, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/salary_structure/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'stats': stats,
    })


@login_required
def salary_structure_detail(request, structure_id):
    """View salary structure details"""
    from .models import SalaryStructure, SalaryStructureAssignment

    structure = get_object_or_404(SalaryStructure, id=structure_id)

    # Get all salary details (components) for this structure
    salary_details = structure.salary_details.select_related('salary_component').all()

    # Get employees assigned to this structure
    assignments = SalaryStructureAssignment.objects.filter(
        salary_structure=structure,
        is_active=True
    ).select_related('employee')

    # Separate earnings and deductions
    earnings = salary_details.filter(salary_component__component_type='EARNING')
    deductions = salary_details.filter(salary_component__component_type='DEDUCTION')

    return render(request, 'payroll/salary_structure/detail.html', {
        'structure': structure,
        'earnings': earnings,
        'deductions': deductions,
        'assignments': assignments
    })


@login_required
def salary_structure_create(request):
    """Create a new salary structure"""
    from .models import SalaryStructure, SalaryDetail, SalaryComponent

    if request.method == 'POST':
        try:
            name = request.POST['name']
            company = request.POST.get('company', '')
            is_active = request.POST.get('is_active') == 'on'
            salary_slip_based_on_timesheet = request.POST.get('salary_slip_based_on_timesheet') == 'on'
            hour_rate = request.POST.get('hour_rate')
            leave_encashment = request.POST.get('leave_encashment') == 'on'
            max_benefits = request.POST.get('max_benefits')

            # Create salary structure
            structure = SalaryStructure.objects.create(
                name=name,
                company=company,
                is_active=is_active,
                salary_slip_based_on_timesheet=salary_slip_based_on_timesheet,
                hour_rate=Decimal(hour_rate) if hour_rate else None,
                leave_encashment=leave_encashment,
                max_benefits=Decimal(max_benefits) if max_benefits else None,
                docstatus=0
            )

            # Handle salary components
            component_ids = request.POST.getlist('component_id[]')
            component_amounts = request.POST.getlist('component_amount[]')
            component_formulas = request.POST.getlist('component_formula[]')

            for i, component_id in enumerate(component_ids):
                if component_id:
                    component = SalaryComponent.objects.get(id=component_id)
                    amount = Decimal(component_amounts[i]) if component_amounts[i] else Decimal('0')
                    formula = component_formulas[i] if i < len(component_formulas) else ''

                    SalaryDetail.objects.create(
                        salary_structure=structure,
                        salary_component=component,
                        amount=amount,
                        formula=formula
                    )

            messages.success(request, f'Salary structure "{name}" created successfully.')
            return redirect('payroll:salary_structure_detail', structure_id=structure.id)

        except Exception as e:
            messages.error(request, f'Error creating salary structure: {str(e)}')

    # Get all active salary components
    components = SalaryComponent.objects.filter(is_active=True).order_by('component_type', 'display_order')
    earnings = components.filter(component_type='EARNING')
    deductions = components.filter(component_type='DEDUCTION')

    return render(request, 'payroll/salary_structure/create.html', {
        'earnings': earnings,
        'deductions': deductions
    })


@login_required
def salary_structure_edit(request, structure_id):
    """Edit an existing salary structure"""
    from .models import SalaryStructure, SalaryDetail, SalaryComponent

    structure = get_object_or_404(SalaryStructure, id=structure_id)

    if request.method == 'POST':
        try:
            structure.name = request.POST['name']
            structure.company = request.POST.get('company', '')
            structure.is_active = request.POST.get('is_active') == 'on'
            structure.salary_slip_based_on_timesheet = request.POST.get('salary_slip_based_on_timesheet') == 'on'
            hour_rate = request.POST.get('hour_rate')
            structure.hour_rate = Decimal(hour_rate) if hour_rate else None
            structure.leave_encashment = request.POST.get('leave_encashment') == 'on'
            max_benefits = request.POST.get('max_benefits')
            structure.max_benefits = Decimal(max_benefits) if max_benefits else None
            structure.save()

            # Update salary details
            structure.salary_details.all().delete()

            component_ids = request.POST.getlist('component_id[]')
            component_amounts = request.POST.getlist('component_amount[]')
            component_formulas = request.POST.getlist('component_formula[]')

            for i, component_id in enumerate(component_ids):
                if component_id:
                    component = SalaryComponent.objects.get(id=component_id)
                    amount = Decimal(component_amounts[i]) if component_amounts[i] else Decimal('0')
                    formula = component_formulas[i] if i < len(component_formulas) else ''

                    SalaryDetail.objects.create(
                        salary_structure=structure,
                        salary_component=component,
                        amount=amount,
                        formula=formula
                    )

            messages.success(request, f'Salary structure "{structure.name}" updated successfully.')
            return redirect('payroll:salary_structure_detail', structure_id=structure.id)

        except Exception as e:
            messages.error(request, f'Error updating salary structure: {str(e)}')

    # Get all active salary components
    components = SalaryComponent.objects.filter(is_active=True).order_by('component_type', 'display_order')
    earnings = components.filter(component_type='EARNING')
    deductions = components.filter(component_type='DEDUCTION')

    # Get existing salary details
    existing_details = structure.salary_details.all()

    return render(request, 'payroll/salary_structure/edit.html', {
        'structure': structure,
        'earnings': earnings,
        'deductions': deductions,
        'existing_details': existing_details
    })


@login_required
def salary_structure_delete(request, structure_id):
    """Delete a salary structure with cascade deletion"""
    from .models import SalaryStructure, SalaryStructureAssignment, SalaryDetail, SalarySlip

    structure = get_object_or_404(SalaryStructure, id=structure_id)

    if request.method == 'POST':
        # Get counts of related records that will be cascade deleted
        details_count = structure.salary_details.count()
        assignments_count = SalaryStructureAssignment.objects.filter(salary_structure=structure).count()
        salary_slips_count = SalarySlip.objects.filter(salary_structure=structure).count()

        structure_name = structure.name

        # Perform cascade delete
        structure.delete()

        # Show detailed success message
        deleted_items = []
        if details_count > 0:
            deleted_items.append(f'{details_count} salary component(s)')
        if assignments_count > 0:
            deleted_items.append(f'{assignments_count} employee assignment(s)')
        if salary_slips_count > 0:
            deleted_items.append(f'{salary_slips_count} salary slip(s)')

        if deleted_items:
            details = ' and '.join(deleted_items)
            messages.success(request, f'Salary structure "{structure_name}" and {details} have been deleted successfully.')
        else:
            messages.success(request, f'Salary structure "{structure_name}" has been deleted successfully.')

        return redirect('payroll:salary_structure_list')

    # GET request - redirect to list
    return redirect('payroll:salary_structure_list')


# Salary Structure Assignment Views
@login_required
def salary_structure_assignment_list(request):
    """List all salary structure assignments"""
    from .models import SalaryStructureAssignment, SalaryStructure

    all_assignments = SalaryStructureAssignment.objects.select_related(
        'employee', 'salary_structure'
    ).all()

    # Calculate statistics
    stats = {
        'total': all_assignments.count(),
        'active': all_assignments.filter(is_active=True).count(),
        'inactive': all_assignments.filter(is_active=False).count(),
        'total_structures': SalaryStructure.objects.filter(is_active=True).count(),
    }

    # Calculate average base salary for active assignments
    avg_base_salary = all_assignments.filter(is_active=True).aggregate(
        avg=Sum('base_salary')
    )['avg'] or 0

    assignments = all_assignments

    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        assignments = assignments.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query) |
            Q(salary_structure__name__icontains=search_query)
        )

    # Filter by status
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        if status_filter == 'active':
            assignments = assignments.filter(is_active=True)
        elif status_filter == 'inactive':
            assignments = assignments.filter(is_active=False)

    # Pagination with per_page support
    per_page = request.GET.get('per_page', '20')
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 25, 50, 100, 200]:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20

    paginator = Paginator(assignments, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/salary_structure_assignment/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'stats': stats,
        'avg_base_salary': avg_base_salary,
        'per_page': per_page,
    })


@login_required
def salary_structure_assignment_create(request):
    """Create a new salary structure assignment"""
    from .models import SalaryStructure, SalaryStructureAssignment

    if request.method == 'POST':
        try:
            employee_id = request.POST['employee']
            salary_structure_id = request.POST['salary_structure']
            from_date = datetime.strptime(request.POST['from_date'], '%Y-%m-%d').date()
            to_date = request.POST.get('to_date')
            base_salary = Decimal(request.POST['base_salary'])
            is_active = request.POST.get('is_active') == 'on'

            employee = Employee.objects.get(id=employee_id)
            salary_structure = SalaryStructure.objects.get(id=salary_structure_id)

            # Deactivate previous assignments if this is active
            if is_active:
                SalaryStructureAssignment.objects.filter(
                    employee=employee,
                    is_active=True
                ).update(is_active=False)

            assignment = SalaryStructureAssignment.objects.create(
                employee=employee,
                salary_structure=salary_structure,
                from_date=from_date,
                to_date=datetime.strptime(to_date, '%Y-%m-%d').date() if to_date else None,
                base_salary=base_salary,
                is_active=is_active,
                docstatus=0
            )

            messages.success(
                request,
                f'Salary structure "{salary_structure.name}" assigned to {employee.get_full_name()} successfully.'
            )
            return redirect('payroll:salary_structure_assignment_list')

        except Exception as e:
            messages.error(request, f'Error creating assignment: {str(e)}')

    # Get active employees and salary structures
    employees = Employee.objects.filter(employment_status='active').order_by('first_name', 'last_name')
    structures = SalaryStructure.objects.filter(is_active=True).order_by('name')

    return render(request, 'payroll/salary_structure_assignment/create.html', {
        'employees': employees,
        'structures': structures
    })


@login_required
def salary_structure_assignment_edit(request, assignment_id):
    """Edit a salary structure assignment"""
    from .models import SalaryStructure, SalaryStructureAssignment

    assignment = get_object_or_404(SalaryStructureAssignment, id=assignment_id)

    if request.method == 'POST':
        try:
            salary_structure_id = request.POST['salary_structure']
            from_date = datetime.strptime(request.POST['from_date'], '%Y-%m-%d').date()
            to_date = request.POST.get('to_date')
            base_salary = Decimal(request.POST['base_salary'])
            is_active = request.POST.get('is_active') == 'on'

            salary_structure = SalaryStructure.objects.get(id=salary_structure_id)

            # Deactivate other assignments if this becomes active
            if is_active and not assignment.is_active:
                SalaryStructureAssignment.objects.filter(
                    employee=assignment.employee,
                    is_active=True
                ).exclude(id=assignment_id).update(is_active=False)

            assignment.salary_structure = salary_structure
            assignment.from_date = from_date
            assignment.to_date = datetime.strptime(to_date, '%Y-%m-%d').date() if to_date else None
            assignment.base_salary = base_salary
            assignment.is_active = is_active
            assignment.save()

            messages.success(request, 'Salary structure assignment updated successfully.')
            return redirect('payroll:salary_structure_assignment_list')

        except Exception as e:
            messages.error(request, f'Error updating assignment: {str(e)}')

    # Get active salary structures
    structures = SalaryStructure.objects.filter(is_active=True).order_by('name')

    return render(request, 'payroll/salary_structure_assignment/edit.html', {
        'assignment': assignment,
        'structures': structures
    })


@login_required
def salary_structure_assignment_delete(request, assignment_id):
    """Delete a salary structure assignment"""
    from .models import SalaryStructureAssignment

    assignment = get_object_or_404(SalaryStructureAssignment, id=assignment_id)

    if request.method == 'POST':
        employee_name = assignment.employee.get_full_name()
        structure_name = assignment.salary_structure.name
        assignment.delete()
        messages.success(
            request,
            f'Salary structure assignment for {employee_name} - {structure_name} deleted successfully.'
        )
        return redirect('payroll:salary_structure_assignment_list')

    return render(request, 'payroll/salary_structure_assignment/delete_confirm.html', {
        'assignment': assignment
    })


# Salary Component Management Views
@login_required
def salary_component_list(request):
    """List all salary components"""
    all_components = SalaryComponent.objects.all()

    # Calculate statistics
    stats = {
        'total': all_components.count(),
        'earnings': all_components.filter(component_type='EARNING').count(),
        'deductions': all_components.filter(component_type='DEDUCTION').count(),
        'active': all_components.filter(is_active=True).count(),
    }

    components = all_components

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        components = components.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query) |
            Q(abbreviation__icontains=search_query)
        )

    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        components = components.filter(component_type=type_filter)

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'active':
            components = components.filter(is_active=True)
        elif status_filter == 'inactive':
            components = components.filter(is_active=False)

    # Pagination
    paginator = Paginator(components, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/salary_components/list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'type_filter': type_filter,
        'status_filter': status_filter,
        'stats': stats,
    })


@login_required
def salary_component_create(request):
    """Create a new salary component"""
    if request.method == 'POST':
        try:
            code = request.POST['code'].upper()
            name = request.POST['name']
            abbreviation = request.POST.get('abbreviation', '')
            component_type = request.POST['component_type']
            calculation_type = request.POST['calculation_type']

            # Boolean fields
            is_payable = request.POST.get('is_payable') == 'on'
            depends_on_payment_days = request.POST.get('depends_on_payment_days') == 'on'
            depends_on_timesheet = request.POST.get('depends_on_timesheet') == 'on'
            is_tax_applicable = request.POST.get('is_tax_applicable') == 'on'
            is_additional_component = request.POST.get('is_additional_component') == 'on'
            is_statistical_component = request.POST.get('is_statistical_component') == 'on'
            variable_based_on_taxable_salary = request.POST.get('variable_based_on_taxable_salary') == 'on'
            pay_against_benefit_claim = request.POST.get('pay_against_benefit_claim') == 'on'

            # Text fields
            formula = request.POST.get('formula', '')
            condition = request.POST.get('condition', '')
            description = request.POST.get('description', '')

            # Numeric fields
            round_to_nearest = int(request.POST.get('round_to_nearest', 0))
            display_order = int(request.POST.get('display_order', 0))
            max_benefit_amount = request.POST.get('max_benefit_amount')
            percentage_value = request.POST.get('percentage_value')
            percentage_of_id = request.POST.get('percentage_of')

            # Create salary component
            component = SalaryComponent.objects.create(
                code=code,
                name=name,
                abbreviation=abbreviation,
                component_type=component_type,
                calculation_type=calculation_type,
                is_payable=is_payable,
                depends_on_payment_days=depends_on_payment_days,
                depends_on_timesheet=depends_on_timesheet,
                is_tax_applicable=is_tax_applicable,
                is_additional_component=is_additional_component,
                is_statistical_component=is_statistical_component,
                variable_based_on_taxable_salary=variable_based_on_taxable_salary,
                pay_against_benefit_claim=pay_against_benefit_claim,
                formula=formula,
                condition=condition,
                description=description,
                round_to_nearest=round_to_nearest,
                display_order=display_order,
                max_benefit_amount=Decimal(max_benefit_amount) if max_benefit_amount else None,
                percentage_value=Decimal(percentage_value) if percentage_value else None,
                percentage_of_id=percentage_of_id if percentage_of_id else None,
                is_active=True
            )

            messages.success(request, f'Salary component "{name}" created successfully.')
            return redirect('payroll:salary_component_detail', component_id=component.id)

        except Exception as e:
            messages.error(request, f'Error creating salary component: {str(e)}')

    # Get all components for percentage_of dropdown
    components = SalaryComponent.objects.filter(is_active=True).order_by('name')

    return render(request, 'payroll/salary_components/create.html', {
        'components': components
    })


@login_required
def salary_component_detail(request, component_id):
    """View salary component details"""
    component = get_object_or_404(SalaryComponent, id=component_id)

    # Get structures using this component
    from .models import SalaryDetail
    structures_using = SalaryDetail.objects.filter(
        salary_component=component
    ).select_related('salary_structure')

    return render(request, 'payroll/salary_components/detail.html', {
        'component': component,
        'structures_using': structures_using
    })


@login_required
def salary_component_edit(request, component_id):
    """Edit an existing salary component"""
    component = get_object_or_404(SalaryComponent, id=component_id)

    if request.method == 'POST':
        try:
            component.code = request.POST['code'].upper()
            component.name = request.POST['name']
            component.abbreviation = request.POST.get('abbreviation', '')
            component.component_type = request.POST['component_type']
            component.calculation_type = request.POST['calculation_type']

            # Boolean fields
            component.is_payable = request.POST.get('is_payable') == 'on'
            component.depends_on_payment_days = request.POST.get('depends_on_payment_days') == 'on'
            component.depends_on_timesheet = request.POST.get('depends_on_timesheet') == 'on'
            component.is_tax_applicable = request.POST.get('is_tax_applicable') == 'on'
            component.is_additional_component = request.POST.get('is_additional_component') == 'on'
            component.is_statistical_component = request.POST.get('is_statistical_component') == 'on'
            component.variable_based_on_taxable_salary = request.POST.get('variable_based_on_taxable_salary') == 'on'
            component.pay_against_benefit_claim = request.POST.get('pay_against_benefit_claim') == 'on'
            component.is_active = request.POST.get('is_active') == 'on'

            # Text fields
            component.formula = request.POST.get('formula', '')
            component.condition = request.POST.get('condition', '')
            component.description = request.POST.get('description', '')

            # Numeric fields
            component.round_to_nearest = int(request.POST.get('round_to_nearest', 0))
            component.display_order = int(request.POST.get('display_order', 0))

            max_benefit_amount = request.POST.get('max_benefit_amount')
            component.max_benefit_amount = Decimal(max_benefit_amount) if max_benefit_amount else None

            percentage_value = request.POST.get('percentage_value')
            component.percentage_value = Decimal(percentage_value) if percentage_value else None

            percentage_of_id = request.POST.get('percentage_of')
            component.percentage_of_id = percentage_of_id if percentage_of_id else None

            component.save()

            messages.success(request, f'Salary component "{component.name}" updated successfully.')
            return redirect('payroll:salary_component_detail', component_id=component.id)

        except Exception as e:
            messages.error(request, f'Error updating salary component: {str(e)}')

    # Get all components for percentage_of dropdown (excluding current component)
    components = SalaryComponent.objects.filter(is_active=True).exclude(id=component_id).order_by('name')

    return render(request, 'payroll/salary_components/edit.html', {
        'component': component,
        'components': components
    })


@login_required
def salary_component_delete(request, component_id):
    """Delete a salary component"""
    from .models import SalaryDetail

    component = get_object_or_404(SalaryComponent, id=component_id)

    # Check if component is used in any salary structure
    if SalaryDetail.objects.filter(salary_component=component).exists():
        messages.error(request, 'Cannot delete salary component that is used in salary structures.')
        return redirect('payroll:salary_component_detail', component_id=component_id)

    if request.method == 'POST':
        component_name = component.name
        component.delete()
        messages.success(request, f'Salary component "{component_name}" deleted successfully.')
        return redirect('payroll:salary_component_list')

    return render(request, 'payroll/salary_components/delete_confirm.html', {
        'component': component
    })


# Tax Slab Management Views
@login_required
def tax_slab_list(request):
    """List all tax slabs"""
    all_slabs = TaxSlab.objects.all()

    # Calculate statistics
    stats = {
        'total': all_slabs.count(),
        'active': all_slabs.filter(is_active=True).count(),
        'inactive': all_slabs.filter(is_active=False).count(),
    }

    slabs = all_slabs

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'active':
            slabs = slabs.filter(is_active=True)
        elif status_filter == 'inactive':
            slabs = slabs.filter(is_active=False)

    # Pagination
    paginator = Paginator(slabs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/tax_slabs/list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'stats': stats,
    })


@login_required
def tax_slab_create(request):
    """Create a new tax slab"""
    if request.method == 'POST':
        try:
            min_amount = Decimal(request.POST['min_amount'])
            max_amount = request.POST.get('max_amount')
            tax_rate = Decimal(request.POST['tax_rate'])
            fixed_tax = Decimal(request.POST.get('fixed_tax', 0))
            effective_from = request.POST['effective_from']
            effective_to = request.POST.get('effective_to')

            slab = TaxSlab.objects.create(
                min_amount=min_amount,
                max_amount=Decimal(max_amount) if max_amount else None,
                tax_rate=tax_rate,
                fixed_tax=fixed_tax,
                effective_from=effective_from,
                effective_to=effective_to if effective_to else None,
                is_active=True
            )

            messages.success(request, 'Tax slab created successfully.')
            return redirect('payroll:tax_slab_list')

        except Exception as e:
            messages.error(request, f'Error creating tax slab: {str(e)}')

    return render(request, 'payroll/tax_slabs/create.html')


@login_required
def tax_slab_edit(request, slab_id):
    """Edit an existing tax slab"""
    slab = get_object_or_404(TaxSlab, id=slab_id)

    if request.method == 'POST':
        try:
            slab.min_amount = Decimal(request.POST['min_amount'])
            max_amount = request.POST.get('max_amount')
            slab.max_amount = Decimal(max_amount) if max_amount else None
            slab.tax_rate = Decimal(request.POST['tax_rate'])
            slab.fixed_tax = Decimal(request.POST.get('fixed_tax', 0))
            slab.effective_from = request.POST['effective_from']
            effective_to = request.POST.get('effective_to')
            slab.effective_to = effective_to if effective_to else None
            slab.is_active = request.POST.get('is_active') == 'on'

            slab.save()

            messages.success(request, 'Tax slab updated successfully.')
            return redirect('payroll:tax_slab_list')

        except Exception as e:
            messages.error(request, f'Error updating tax slab: {str(e)}')

    return render(request, 'payroll/tax_slabs/edit.html', {
        'slab': slab
    })


@login_required
def tax_slab_delete(request, slab_id):
    """Delete a tax slab"""
    slab = get_object_or_404(TaxSlab, id=slab_id)

    if request.method == 'POST':
        slab.delete()
        messages.success(request, 'Tax slab deleted successfully.')
        return redirect('payroll:tax_slab_list')

    return render(request, 'payroll/tax_slabs/delete_confirm.html', {
        'slab': slab
    })


# NSSF Configuration Management Views
@login_required
def nssf_config_list(request):
    """List all NSSF configurations"""
    all_configs = NSSFConfiguration.objects.all()

    # Calculate statistics
    stats = {
        'total': all_configs.count(),
        'active': all_configs.filter(is_active=True).count(),
        'inactive': all_configs.filter(is_active=False).count(),
    }

    configs = all_configs

    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        if status_filter == 'active':
            configs = configs.filter(is_active=True)
        elif status_filter == 'inactive':
            configs = configs.filter(is_active=False)

    # Pagination
    paginator = Paginator(configs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'payroll/nssf_config/list.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'stats': stats,
    })


@login_required
def nssf_config_create(request):
    """Create a new NSSF configuration"""
    if request.method == 'POST':
        try:
            contribution_type = request.POST['contribution_type']
            employee_rate = Decimal(request.POST['employee_rate'])
            employer_rate = Decimal(request.POST['employer_rate'])
            max_salary_cap = Decimal(request.POST['max_salary_cap'])
            effective_from = request.POST['effective_from']
            effective_to = request.POST.get('effective_to')

            config = NSSFConfiguration.objects.create(
                contribution_type=contribution_type,
                employee_rate=employee_rate,
                employer_rate=employer_rate,
                max_salary_cap=max_salary_cap,
                effective_from=effective_from,
                effective_to=effective_to if effective_to else None,
                is_active=True
            )

            messages.success(request, 'NSSF configuration created successfully.')
            return redirect('payroll:nssf_config_list')

        except Exception as e:
            messages.error(request, f'Error creating NSSF configuration: {str(e)}')

    return render(request, 'payroll/nssf_config/create.html')


@login_required
def nssf_config_edit(request, config_id):
    """Edit an existing NSSF configuration"""
    config = get_object_or_404(NSSFConfiguration, id=config_id)

    if request.method == 'POST':
        try:
            config.contribution_type = request.POST['contribution_type']
            config.employee_rate = Decimal(request.POST['employee_rate'])
            config.employer_rate = Decimal(request.POST['employer_rate'])
            config.max_salary_cap = Decimal(request.POST['max_salary_cap'])
            config.effective_from = request.POST['effective_from']
            effective_to = request.POST.get('effective_to')
            config.effective_to = effective_to if effective_to else None
            config.is_active = request.POST.get('is_active') == 'on'

            config.save()

            messages.success(request, 'NSSF configuration updated successfully.')
            return redirect('payroll:nssf_config_list')

        except Exception as e:
            messages.error(request, f'Error updating NSSF configuration: {str(e)}')

    return render(request, 'payroll/nssf_config/edit.html', {
        'config': config
    })


@login_required
def nssf_config_delete(request, config_id):
    """Delete an NSSF configuration"""
    config = get_object_or_404(NSSFConfiguration, id=config_id)

    if request.method == 'POST':
        config.delete()
        messages.success(request, 'NSSF configuration deleted successfully.')
        return redirect('payroll:nssf_config_list')

    return render(request, 'payroll/nssf_config/delete_confirm.html', {
        'config': config
    })
