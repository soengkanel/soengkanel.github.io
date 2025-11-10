# Payroll models for NextHR Django application
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, datetime, timedelta
from decimal import Decimal
from calendar import monthrange
import uuid

from .models import Employee, Department, Position
from .timecard_models import TimecardEntry


class PayrollPolicy(models.Model):
    """
    Company-wide payroll rules and policies
    """
    CALCULATION_METHOD_CHOICES = [
        ('monthly', _('Monthly')),
        ('bi_weekly', _('Bi-Weekly')),
        ('weekly', _('Weekly')),
        ('daily', _('Daily')),
    ]

    TAX_CALCULATION_CHOICES = [
        ('progressive', _('Progressive Tax Slabs')),
        ('flat_rate', _('Flat Rate')),
        ('no_tax', _('No Tax')),
    ]

    name = models.CharField(_('Policy Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)

    # Basic settings
    calculation_method = models.CharField(_('Calculation Method'), max_length=20,
                                        choices=CALCULATION_METHOD_CHOICES, default='monthly')
    currency = models.CharField(_('Currency'), max_length=3, default='USD')

    # Working time settings
    standard_working_hours_per_day = models.DecimalField(_('Standard Working Hours/Day'),
                                                       max_digits=4, decimal_places=2, default=8.00)
    standard_working_days_per_month = models.IntegerField(_('Standard Working Days/Month'), default=22)

    # Tax settings
    tax_calculation_method = models.CharField(_('Tax Calculation'), max_length=20,
                                            choices=TAX_CALCULATION_CHOICES, default='progressive')

    # Deduction settings
    social_security_rate = models.DecimalField(_('Social Security Rate %'), max_digits=5,
                                             decimal_places=2, default=3.00)
    health_insurance_rate = models.DecimalField(_('Health Insurance Rate %'), max_digits=5,
                                              decimal_places=2, default=2.00)

    # Overtime integration
    integrate_overtime = models.BooleanField(_('Integrate Overtime Claims'), default=True)
    integrate_timecards = models.BooleanField(_('Integrate Timecard Data'), default=True)

    # Leave deductions
    deduct_unpaid_leave = models.BooleanField(_('Deduct Unpaid Leave'), default=True)
    deduct_half_day_leave = models.BooleanField(_('Deduct Half Day Leave'), default=True)

    # Bonus settings
    allow_performance_bonus = models.BooleanField(_('Allow Performance Bonus'), default=True)
    allow_project_bonus = models.BooleanField(_('Allow Project Bonus'), default=True)

    is_active = models.BooleanField(_('Active'), default=True)
    effective_date = models.DateField(_('Effective Date'), default=date.today)
    end_date = models.DateField(_('End Date'), null=True, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Payroll Policy')
        verbose_name_plural = _('Payroll Policies')
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.name} ({self.get_calculation_method_display()})"


class PayrollPeriod(models.Model):
    """
    Payroll processing periods (monthly, bi-weekly, etc.)
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('locked', _('Locked')),
        ('processed', _('Processed')),
        ('closed', _('Closed')),
    ]

    name = models.CharField(_('Period Name'), max_length=50)
    payroll_policy = models.ForeignKey(PayrollPolicy, on_delete=models.CASCADE,
                                     related_name='periods', verbose_name=_('Payroll Policy'))

    # Period dates
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    pay_date = models.DateField(_('Pay Date'))

    # Status and processing
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Period metadata
    total_employees = models.IntegerField(_('Total Employees'), default=0)
    processed_employees = models.IntegerField(_('Processed Employees'), default=0)
    total_gross_pay = models.DecimalField(_('Total Gross Pay'), max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(_('Total Deductions'), max_digits=15, decimal_places=2, default=0)
    total_net_pay = models.DecimalField(_('Total Net Pay'), max_digits=15, decimal_places=2, default=0)

    # Processing info
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='processed_payroll_periods')
    processed_at = models.DateTimeField(_('Processed At'), null=True, blank=True)

    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Payroll Period')
        verbose_name_plural = _('Payroll Periods')
        ordering = ['-start_date']
        unique_together = ['payroll_policy', 'start_date', 'end_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

    @property
    def is_current(self):
        """Check if this period is currently active"""
        today = date.today()
        return self.start_date <= today <= self.end_date

    @property
    def working_days(self):
        """Calculate working days in this period (excluding weekends)"""
        current_date = self.start_date
        working_days = 0
        while current_date <= self.end_date:
            if current_date.weekday() < 5:  # Monday=0, Friday=4
                working_days += 1
            current_date += timedelta(days=1)
        return working_days


class PayrollComponent(models.Model):
    """
    Salary components like basic salary, allowances, deductions, taxes
    """
    COMPONENT_TYPE_CHOICES = [
        ('earning', _('Earning')),
        ('deduction', _('Deduction')),
        ('employer_contribution', _('Employer Contribution')),
    ]

    CALCULATION_TYPE_CHOICES = [
        ('fixed', _('Fixed Amount')),
        ('percentage', _('Percentage of Basic')),
        ('percentage_gross', _('Percentage of Gross')),
        ('formula', _('Custom Formula')),
    ]

    name = models.CharField(_('Component Name'), max_length=100)
    code = models.CharField(_('Component Code'), max_length=20, unique=True)
    component_type = models.CharField(_('Type'), max_length=30, choices=COMPONENT_TYPE_CHOICES)
    calculation_type = models.CharField(_('Calculation Type'), max_length=20,
                                      choices=CALCULATION_TYPE_CHOICES, default='fixed')

    # Component settings
    is_taxable = models.BooleanField(_('Taxable'), default=True)
    is_mandatory = models.BooleanField(_('Mandatory'), default=False)
    is_variable = models.BooleanField(_('Variable'), default=False)

    # Calculation settings
    default_amount = models.DecimalField(_('Default Amount'), max_digits=10, decimal_places=2,
                                       null=True, blank=True)
    percentage_value = models.DecimalField(_('Percentage Value'), max_digits=5, decimal_places=2,
                                         null=True, blank=True)
    min_amount = models.DecimalField(_('Minimum Amount'), max_digits=10, decimal_places=2,
                                   null=True, blank=True)
    max_amount = models.DecimalField(_('Maximum Amount'), max_digits=10, decimal_places=2,
                                   null=True, blank=True)

    # Formula for complex calculations
    calculation_formula = models.TextField(_('Calculation Formula'), blank=True,
                                         help_text=_('Python expression for complex calculations'))

    # Display settings
    display_order = models.IntegerField(_('Display Order'), default=1)
    show_in_payslip = models.BooleanField(_('Show in Payslip'), default=True)

    # Applicability
    applicable_to_all = models.BooleanField(_('Applicable to All Employees'), default=True)
    departments = models.ManyToManyField(Department, blank=True,
                                       related_name='payroll_components')
    positions = models.ManyToManyField(Position, blank=True,
                                     related_name='payroll_components')

    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Payroll Component')
        verbose_name_plural = _('Payroll Components')
        ordering = ['component_type', 'display_order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"

    def calculate_amount(self, basic_salary, gross_salary, employee=None, custom_values=None):
        """
        Calculate component amount based on calculation type
        """
        custom_values = custom_values or {}

        if self.calculation_type == 'fixed':
            amount = custom_values.get('amount', self.default_amount or 0)

        elif self.calculation_type == 'percentage':
            percentage = custom_values.get('percentage', self.percentage_value or 0)
            amount = (basic_salary * percentage) / 100

        elif self.calculation_type == 'percentage_gross':
            percentage = custom_values.get('percentage', self.percentage_value or 0)
            amount = (gross_salary * percentage) / 100

        elif self.calculation_type == 'formula' and self.calculation_formula:
            # Safe evaluation of formula
            try:
                # Create safe context for formula evaluation
                context = {
                    'basic_salary': float(basic_salary),
                    'gross_salary': float(gross_salary),
                    'min': min,
                    'max': max,
                    'round': round,
                    **custom_values
                }
                amount = eval(self.calculation_formula, {"__builtins__": {}}, context)
            except:
                amount = 0
        else:
            amount = 0

        # Apply min/max limits
        if self.min_amount is not None:
            amount = max(amount, float(self.min_amount))
        if self.max_amount is not None:
            amount = min(amount, float(self.max_amount))

        return Decimal(str(amount))


class TaxSlab(models.Model):
    """
    Tax slabs for progressive tax calculation
    """
    payroll_policy = models.ForeignKey(PayrollPolicy, on_delete=models.CASCADE,
                                     related_name='tax_slabs')

    min_amount = models.DecimalField(_('Minimum Amount'), max_digits=12, decimal_places=2, default=0)
    max_amount = models.DecimalField(_('Maximum Amount'), max_digits=12, decimal_places=2,
                                   null=True, blank=True)
    tax_rate = models.DecimalField(_('Tax Rate %'), max_digits=5, decimal_places=2)

    slab_order = models.IntegerField(_('Slab Order'), default=1)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Tax Slab')
        verbose_name_plural = _('Tax Slabs')
        ordering = ['payroll_policy', 'slab_order', 'min_amount']

    def __str__(self):
        max_display = f" to {self.max_amount}" if self.max_amount else " and above"
        return f"{self.min_amount}{max_display} @ {self.tax_rate}%"


class EmployeeSalary(models.Model):
    """
    Employee salary structure and components
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                               related_name='hr_salary_structures', verbose_name=_('Employee'))
    payroll_policy = models.ForeignKey(PayrollPolicy, on_delete=models.CASCADE,
                                     related_name='employee_salaries')

    # Basic salary information
    basic_salary = models.DecimalField(_('Basic Salary'), max_digits=12, decimal_places=2)
    effective_date = models.DateField(_('Effective Date'))
    end_date = models.DateField(_('End Date'), null=True, blank=True)

    # Salary revision info
    previous_salary = models.DecimalField(_('Previous Salary'), max_digits=12, decimal_places=2,
                                        null=True, blank=True)
    revision_reason = models.CharField(_('Revision Reason'), max_length=200, blank=True)

    # Status
    is_active = models.BooleanField(_('Active'), default=True)

    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_salaries')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)

    notes = models.TextField(_('Notes'), blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_salaries')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Employee Salary')
        verbose_name_plural = _('Employee Salaries')
        ordering = ['-effective_date']
        unique_together = ['employee', 'effective_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.basic_salary} (from {self.effective_date})"

    @property
    def is_current(self):
        """Check if this salary structure is currently effective"""
        today = date.today()
        if self.end_date:
            return self.effective_date <= today <= self.end_date
        return self.effective_date <= today and self.is_active


class EmployeeSalaryComponent(models.Model):
    """
    Individual salary components for each employee
    """
    employee_salary = models.ForeignKey(EmployeeSalary, on_delete=models.CASCADE,
                                      related_name='components')
    payroll_component = models.ForeignKey(PayrollComponent, on_delete=models.CASCADE,
                                        related_name='employee_components')

    # Component value overrides
    custom_amount = models.DecimalField(_('Custom Amount'), max_digits=10, decimal_places=2,
                                      null=True, blank=True)
    custom_percentage = models.DecimalField(_('Custom Percentage'), max_digits=5, decimal_places=2,
                                          null=True, blank=True)

    # Status
    is_active = models.BooleanField(_('Active'), default=True)
    effective_date = models.DateField(_('Effective Date'), default=date.today)
    end_date = models.DateField(_('End Date'), null=True, blank=True)

    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Employee Salary Component')
        verbose_name_plural = _('Employee Salary Components')
        unique_together = ['employee_salary', 'payroll_component']

    def __str__(self):
        return f"{self.employee_salary.employee.full_name} - {self.payroll_component.name}"

    def get_calculated_amount(self, basic_salary, gross_salary):
        """Get the calculated amount for this component"""
        custom_values = {}
        if self.custom_amount:
            custom_values['amount'] = float(self.custom_amount)
        if self.custom_percentage:
            custom_values['percentage'] = float(self.custom_percentage)

        return self.payroll_component.calculate_amount(
            basic_salary, gross_salary, self.employee_salary.employee, custom_values
        )


class PayrollRun(models.Model):
    """
    Actual payroll processing instance
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('calculating', _('Calculating')),
        ('calculated', _('Calculated')),
        ('approved', _('Approved')),
        ('processed', _('Processed')),
        ('failed', _('Failed')),
    ]

    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE,
                                     related_name='payroll_runs')

    run_number = models.IntegerField(_('Run Number'), default=1)
    run_date = models.DateTimeField(_('Run Date'), auto_now_add=True)

    # Processing status
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Filters for selective processing
    departments = models.ManyToManyField(Department, blank=True,
                                       related_name='payroll_runs')
    employees = models.ManyToManyField(Employee, blank=True,
                                     related_name='payroll_runs')

    # Summary data
    total_employees_processed = models.IntegerField(_('Total Employees Processed'), default=0)
    total_gross_pay = models.DecimalField(_('Total Gross Pay'), max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(_('Total Deductions'), max_digits=15, decimal_places=2, default=0)
    total_net_pay = models.DecimalField(_('Total Net Pay'), max_digits=15, decimal_places=2, default=0)

    # Processing details
    processed_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='processed_payrolls')
    processing_started_at = models.DateTimeField(_('Processing Started'), null=True, blank=True)
    processing_completed_at = models.DateTimeField(_('Processing Completed'), null=True, blank=True)

    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_payroll_runs')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)

    # Error handling
    error_message = models.TextField(_('Error Message'), blank=True)
    processing_log = models.TextField(_('Processing Log'), blank=True)

    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Payroll Run')
        verbose_name_plural = _('Payroll Runs')
        ordering = ['-run_date']
        unique_together = ['payroll_period', 'run_number']

    def __str__(self):
        return f"{self.payroll_period.name} - Run #{self.run_number} ({self.get_status_display()})"


class PayrollEntry(models.Model):
    """
    Individual employee payroll calculation for a specific period
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('calculated', _('Calculated')),
        ('approved', _('Approved')),
        ('paid', _('Paid')),
        ('hold', _('On Hold')),
        ('cancelled', _('Cancelled')),
    ]

    payroll_run = models.ForeignKey(PayrollRun, on_delete=models.CASCADE,
                                  related_name='entries')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                               related_name='payroll_entries')
    employee_salary = models.ForeignKey(EmployeeSalary, on_delete=models.CASCADE,
                                      related_name='payroll_entries')

    # Attendance and working data
    working_days = models.IntegerField(_('Working Days'), default=0)
    actual_working_days = models.IntegerField(_('Actual Working Days'), default=0)
    overtime_hours = models.DecimalField(_('Overtime Hours'), max_digits=6, decimal_places=2, default=0)
    leave_days = models.IntegerField(_('Leave Days'), default=0)
    unpaid_leave_days = models.IntegerField(_('Unpaid Leave Days'), default=0)

    # Salary calculations
    basic_salary = models.DecimalField(_('Basic Salary'), max_digits=12, decimal_places=2, default=0)
    gross_salary = models.DecimalField(_('Gross Salary'), max_digits=12, decimal_places=2, default=0)
    total_earnings = models.DecimalField(_('Total Earnings'), max_digits=12, decimal_places=2, default=0)
    total_deductions = models.DecimalField(_('Total Deductions'), max_digits=12, decimal_places=2, default=0)
    net_salary = models.DecimalField(_('Net Salary'), max_digits=12, decimal_places=2, default=0)

    # Tax calculations
    taxable_income = models.DecimalField(_('Taxable Income'), max_digits=12, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('Tax Amount'), max_digits=10, decimal_places=2, default=0)

    # Bonus and incentives
    performance_bonus = models.DecimalField(_('Performance Bonus'), max_digits=10, decimal_places=2, default=0)
    project_bonus = models.DecimalField(_('Project Bonus'), max_digits=10, decimal_places=2, default=0)
    other_earnings = models.DecimalField(_('Other Earnings'), max_digits=10, decimal_places=2, default=0)

    # Deductions
    advance_deduction = models.DecimalField(_('Advance Deduction'), max_digits=10, decimal_places=2, default=0)
    loan_deduction = models.DecimalField(_('Loan Deduction'), max_digits=10, decimal_places=2, default=0)
    other_deductions = models.DecimalField(_('Other Deductions'), max_digits=10, decimal_places=2, default=0)

    # Status and processing
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    calculation_date = models.DateTimeField(_('Calculation Date'), null=True, blank=True)

    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_payroll_entries')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)

    # Payment
    paid_at = models.DateTimeField(_('Paid At'), null=True, blank=True)
    payment_reference = models.CharField(_('Payment Reference'), max_length=100, blank=True)

    # Calculation details (JSON for component breakdown)
    calculation_details = models.JSONField(_('Calculation Details'), default=dict)

    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Payroll Entry')
        verbose_name_plural = _('Payroll Entries')
        ordering = ['-payroll_run__run_date', 'employee__employee_id']
        unique_together = ['payroll_run', 'employee']

    def __str__(self):
        return f"{self.employee.full_name} - {self.payroll_run.payroll_period.name}"

    def calculate_payroll(self):
        """
        Calculate payroll for this employee
        """
        period = self.payroll_run.payroll_period
        policy = period.payroll_policy

        # Get employee's current salary structure
        salary_structure = self.employee_salary
        self.basic_salary = salary_structure.basic_salary

        # Calculate working days and attendance
        self.working_days = period.working_days
        self._calculate_attendance_data(period)

        # Calculate salary components
        earnings = self._calculate_earnings()
        deductions = self._calculate_deductions()

        # Calculate totals
        self.total_earnings = sum(earnings.values())
        self.total_deductions = sum(deductions.values())
        self.gross_salary = self.basic_salary + self.total_earnings
        self.net_salary = self.gross_salary - self.total_deductions

        # Calculate tax
        if policy.tax_calculation_method != 'no_tax':
            self.tax_amount = self._calculate_tax()
            self.net_salary -= self.tax_amount

        # Store calculation details
        self.calculation_details = {
            'earnings': earnings,
            'deductions': deductions,
            'tax_calculation': {
                'taxable_income': float(self.taxable_income),
                'tax_amount': float(self.tax_amount),
            },
            'calculation_date': timezone.now().isoformat(),
        }

        self.status = 'calculated'
        self.calculation_date = timezone.now()
        self.save()

    def _calculate_attendance_data(self, period):
        """Calculate attendance-related data"""
        # This would integrate with attendance/timecard systems
        # For now, assume full attendance
        self.actual_working_days = self.working_days
        self.leave_days = 0
        self.unpaid_leave_days = 0

        # Calculate overtime from timecard entries or overtime claims
        if period.payroll_policy.integrate_overtime:
            from .models import OvertimeClaim
            overtime_claims = OvertimeClaim.objects.filter(
                employee=self.employee,
                work_date__range=[period.start_date, period.end_date],
                status='approved'
            )
            self.overtime_hours = sum(claim.overtime_hours for claim in overtime_claims)

    def _calculate_earnings(self):
        """Calculate all earnings components"""
        earnings = {}

        # Get all earning components for this employee
        components = self.employee_salary.components.filter(
            payroll_component__component_type='earning',
            is_active=True
        )

        current_gross = self.basic_salary

        for component in components:
            amount = component.get_calculated_amount(self.basic_salary, current_gross)
            earnings[component.payroll_component.code] = float(amount)
            current_gross += amount

        # Add overtime earnings
        if self.overtime_hours > 0:
            # Calculate overtime rate (simplified)
            hourly_rate = self.basic_salary / 160  # Monthly to hourly
            overtime_amount = self.overtime_hours * hourly_rate * Decimal('1.5')
            earnings['overtime'] = float(overtime_amount)

        return earnings

    def _calculate_deductions(self):
        """Calculate all deduction components"""
        deductions = {}

        # Get all deduction components for this employee
        components = self.employee_salary.components.filter(
            payroll_component__component_type='deduction',
            is_active=True
        )

        for component in components:
            amount = component.get_calculated_amount(self.basic_salary, self.gross_salary)
            deductions[component.payroll_component.code] = float(amount)

        # Add leave deductions
        if self.unpaid_leave_days > 0:
            daily_rate = self.basic_salary / self.working_days
            leave_deduction = daily_rate * self.unpaid_leave_days
            deductions['unpaid_leave'] = float(leave_deduction)

        return deductions

    def _calculate_tax(self):
        """Calculate income tax based on policy"""
        policy = self.payroll_run.payroll_period.payroll_policy

        # Calculate taxable income
        taxable_components = self.employee_salary.components.filter(
            payroll_component__is_taxable=True,
            is_active=True
        )

        self.taxable_income = self.basic_salary
        for component in taxable_components:
            if component.payroll_component.component_type == 'earning':
                amount = component.get_calculated_amount(self.basic_salary, self.gross_salary)
                self.taxable_income += amount

        if policy.tax_calculation_method == 'progressive':
            return self._calculate_progressive_tax()
        elif policy.tax_calculation_method == 'flat_rate':
            # Simple flat rate (would need to be configured)
            return self.taxable_income * Decimal('0.15')  # 15% flat rate

        return Decimal('0')

    def _calculate_progressive_tax(self):
        """Calculate progressive tax based on tax slabs"""
        policy = self.payroll_run.payroll_period.payroll_policy
        tax_slabs = policy.tax_slabs.order_by('min_amount')

        total_tax = Decimal('0')
        remaining_income = self.taxable_income

        for slab in tax_slabs:
            if remaining_income <= 0:
                break

            # Determine taxable amount for this slab
            if slab.max_amount:
                slab_range = slab.max_amount - slab.min_amount
                taxable_in_slab = min(remaining_income, slab_range)
            else:
                taxable_in_slab = remaining_income

            # Calculate tax for this slab
            slab_tax = taxable_in_slab * (slab.tax_rate / 100)
            total_tax += slab_tax
            remaining_income -= taxable_in_slab

        return total_tax


class PaySlip(models.Model):
    """
    Generated payslip for each employee
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('generated', _('Generated')),
        ('sent', _('Sent')),
        ('viewed', _('Viewed')),
    ]

    payroll_entry = models.OneToOneField(PayrollEntry, on_delete=models.CASCADE,
                                       related_name='payslip')

    # Payslip details
    payslip_number = models.CharField(_('Payslip Number'), max_length=50, unique=True)
    generation_date = models.DateTimeField(_('Generation Date'), auto_now_add=True)

    # PDF generation
    pdf_file = models.FileField(_('PDF File'), upload_to='payslips/', null=True, blank=True)
    pdf_generated_at = models.DateTimeField(_('PDF Generated At'), null=True, blank=True)

    # Delivery
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    sent_at = models.DateTimeField(_('Sent At'), null=True, blank=True)
    viewed_at = models.DateTimeField(_('Viewed At'), null=True, blank=True)

    # Email details
    sent_to_email = models.EmailField(_('Sent to Email'), blank=True)
    email_delivery_status = models.CharField(_('Email Delivery Status'), max_length=50, blank=True)

    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Pay Slip')
        verbose_name_plural = _('Pay Slips')
        ordering = ['-generation_date']

    def __str__(self):
        return f"{self.payslip_number} - {self.payroll_entry.employee.full_name}"

    def save(self, *args, **kwargs):
        if not self.payslip_number:
            self.payslip_number = self.generate_payslip_number()
        super().save(*args, **kwargs)

    def generate_payslip_number(self):
        """Generate unique payslip number"""
        period = self.payroll_entry.payroll_run.payroll_period
        year_month = f"{period.start_date.year}{period.start_date.month:02d}"
        employee_id = self.payroll_entry.employee.employee_id

        # Format: PS-YYYYMM-EMP001-001
        base_number = f"PS-{year_month}-{employee_id}"

        # Check for existing payslips and increment
        existing = PaySlip.objects.filter(
            payslip_number__startswith=base_number
        ).count()

        return f"{base_number}-{existing + 1:03d}"


class SalaryAdvance(models.Model):
    """
    Salary advance requests and tracking
    """
    STATUS_CHOICES = [
        ('requested', _('Requested')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('paid', _('Paid')),
        ('fully_recovered', _('Fully Recovered')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                               related_name='hr_salary_advances')

    # Advance details
    request_date = models.DateField(_('Request Date'), auto_now_add=True)
    advance_amount = models.DecimalField(_('Advance Amount'), max_digits=10, decimal_places=2)
    reason = models.TextField(_('Reason'))

    # Repayment
    installments = models.IntegerField(_('Number of Installments'), default=1)
    installment_amount = models.DecimalField(_('Installment Amount'), max_digits=10,
                                           decimal_places=2, default=0)
    recovery_start_month = models.DateField(_('Recovery Start Month'))

    # Status tracking
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='requested')

    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='hr_approved_advances')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)
    approval_comments = models.TextField(_('Approval Comments'), blank=True)

    # Payment
    paid_at = models.DateTimeField(_('Paid At'), null=True, blank=True)
    payment_reference = models.CharField(_('Payment Reference'), max_length=100, blank=True)

    # Recovery tracking
    total_recovered = models.DecimalField(_('Total Recovered'), max_digits=10, decimal_places=2, default=0)
    balance_amount = models.DecimalField(_('Balance Amount'), max_digits=10, decimal_places=2, default=0)

    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Salary Advance')
        verbose_name_plural = _('Salary Advances')
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.advance_amount} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Calculate installment amount
        if self.installments > 0:
            self.installment_amount = self.advance_amount / self.installments

        # Calculate balance
        self.balance_amount = self.advance_amount - self.total_recovered

        # Update status based on recovery
        if self.balance_amount <= 0 and self.status == 'paid':
            self.status = 'fully_recovered'

        super().save(*args, **kwargs)


class SalaryAdvanceRecovery(models.Model):
    """
    Track salary advance recoveries from payroll
    """
    salary_advance = models.ForeignKey(SalaryAdvance, on_delete=models.CASCADE,
                                     related_name='recoveries')
    payroll_entry = models.ForeignKey(PayrollEntry, on_delete=models.CASCADE,
                                    related_name='advance_recoveries')

    recovery_amount = models.DecimalField(_('Recovery Amount'), max_digits=10, decimal_places=2)
    installment_number = models.IntegerField(_('Installment Number'))

    recovery_date = models.DateField(_('Recovery Date'), auto_now_add=True)
    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Salary Advance Recovery')
        verbose_name_plural = _('Salary Advance Recoveries')
        ordering = ['-recovery_date']

    def __str__(self):
        return f"{self.salary_advance.employee.full_name} - Installment #{self.installment_number}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Update total recovered in salary advance
        self.salary_advance.total_recovered = self.salary_advance.recoveries.aggregate(
            total=models.Sum('recovery_amount')
        )['total'] or 0
        self.salary_advance.save()


class YearEndStatement(models.Model):
    """
    Year-end tax statements for employees
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                               related_name='year_end_statements')

    # Statement details
    financial_year = models.CharField(_('Financial Year'), max_length=9)  # e.g., "2024-2025"
    statement_date = models.DateField(_('Statement Date'), auto_now_add=True)

    # Annual totals
    total_gross_salary = models.DecimalField(_('Total Gross Salary'), max_digits=15, decimal_places=2, default=0)
    total_deductions = models.DecimalField(_('Total Deductions'), max_digits=15, decimal_places=2, default=0)
    total_tax_paid = models.DecimalField(_('Total Tax Paid'), max_digits=12, decimal_places=2, default=0)
    total_net_salary = models.DecimalField(_('Total Net Salary'), max_digits=15, decimal_places=2, default=0)

    # Component-wise breakdown (JSON)
    annual_breakdown = models.JSONField(_('Annual Breakdown'), default=dict)

    # PDF generation
    pdf_file = models.FileField(_('PDF File'), upload_to='year_end_statements/', null=True, blank=True)
    pdf_generated_at = models.DateTimeField(_('PDF Generated At'), null=True, blank=True)

    # Status
    is_final = models.BooleanField(_('Final Statement'), default=False)

    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_statements')
    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Year End Statement')
        verbose_name_plural = _('Year End Statements')
        ordering = ['-financial_year', 'employee__employee_id']
        unique_together = ['employee', 'financial_year']

    def __str__(self):
        return f"{self.employee.full_name} - {self.financial_year}"

    def generate_statement(self):
        """
        Generate year-end statement data from payroll entries
        """
        # Get all payroll entries for this employee in the financial year
        year_start = date(int(self.financial_year.split('-')[0]), 4, 1)
        year_end = date(int(self.financial_year.split('-')[1]), 3, 31)

        payroll_entries = PayrollEntry.objects.filter(
            employee=self.employee,
            payroll_run__payroll_period__start_date__gte=year_start,
            payroll_run__payroll_period__end_date__lte=year_end,
            status__in=['approved', 'paid']
        )

        # Calculate totals
        self.total_gross_salary = sum(entry.gross_salary for entry in payroll_entries)
        self.total_deductions = sum(entry.total_deductions for entry in payroll_entries)
        self.total_tax_paid = sum(entry.tax_amount for entry in payroll_entries)
        self.total_net_salary = sum(entry.net_salary for entry in payroll_entries)

        # Generate component-wise breakdown
        breakdown = {
            'monthly_breakdown': [],
            'component_totals': {},
            'tax_breakdown': {},
        }

        for entry in payroll_entries:
            month_data = {
                'month': entry.payroll_run.payroll_period.name,
                'gross_salary': float(entry.gross_salary),
                'total_deductions': float(entry.total_deductions),
                'tax_amount': float(entry.tax_amount),
                'net_salary': float(entry.net_salary),
                'components': entry.calculation_details
            }
            breakdown['monthly_breakdown'].append(month_data)

        self.annual_breakdown = breakdown
        self.save()