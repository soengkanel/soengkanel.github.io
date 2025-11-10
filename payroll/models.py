from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone
from datetime import date, timedelta
from hr.models import Employee, Department
from django.core.cache import cache


class PayrollSettings(models.Model):
    """Global payroll settings including currency configuration"""
    CURRENCY_CHOICES = [
        ('USD', 'US Dollar ($)'),
        ('KHR', 'Cambodian Riel (៛)'),
        ('EUR', 'Euro (€)'),
        ('GBP', 'British Pound (£)'),
        ('JPY', 'Japanese Yen (¥)'),
        ('CNY', 'Chinese Yuan (¥)'),
        ('THB', 'Thai Baht (฿)'),
        ('VND', 'Vietnamese Dong (₫)'),
    ]

    DECIMAL_PLACES_CHOICES = [
        (0, 'No decimals (e.g., 1000)'),
        (2, 'Two decimals (e.g., 1000.00)'),
    ]

    # Currency settings
    base_currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        help_text="Primary currency for payroll calculations"
    )
    currency_symbol = models.CharField(
        max_length=10,
        default='$',
        help_text="Symbol to display (e.g., $, ៛, €)"
    )
    currency_position = models.CharField(
        max_length=10,
        choices=[
            ('before', 'Before amount ($100)'),
            ('after', 'After amount (100$)'),
        ],
        default='before',
        help_text="Where to display currency symbol"
    )
    decimal_places = models.IntegerField(
        choices=DECIMAL_PLACES_CHOICES,
        default=2,
        help_text="Number of decimal places to display"
    )

    # Display settings
    use_thousand_separator = models.BooleanField(
        default=True,
        help_text="Use comma separator for thousands (e.g., 1,000,000)"
    )

    # Company info
    company_name = models.CharField(max_length=200, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payroll Settings"
        verbose_name_plural = "Payroll Settings"

    def __str__(self):
        return f"Payroll Settings - {self.base_currency}"

    def save(self, *args, **kwargs):
        # Clear cache when settings are updated
        cache.delete('payroll_settings')
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create payroll settings with caching"""
        settings = cache.get('payroll_settings')
        if not settings:
            settings, created = cls.objects.get_or_create(pk=1)
            cache.set('payroll_settings', settings, 3600)  # Cache for 1 hour
        return settings

    def format_currency(self, amount):
        """Format amount according to currency settings"""
        if amount is None:
            amount = 0

        # Convert to Decimal if needed
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount))

        # Format with decimal places
        if self.decimal_places == 0:
            formatted = f"{amount:,.0f}" if self.use_thousand_separator else f"{amount:.0f}"
        else:
            formatted = f"{amount:,.2f}" if self.use_thousand_separator else f"{amount:.2f}"

        # Add currency symbol
        if self.currency_position == 'before':
            return f"{self.currency_symbol} {formatted}"
        else:
            return f"{formatted} {self.currency_symbol}"

    def get_currency_display_name(self):
        """Get full currency name with code"""
        return f"{self.get_base_currency_display()}"


class PayrollPeriod(models.Model):
    """
    Payroll processing periods with status tracking and summary calculations.
    Enhanced with automatic working days calculation and period metrics.
    """
    PERIOD_TYPE_CHOICES = [
        ('MONTHLY', 'Monthly'),
        ('SEMI_MONTHLY', 'Semi-Monthly'),
        ('WEEKLY', 'Weekly'),
        ('BI_WEEKLY', 'Bi-Weekly'),
    ]

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PROCESSING', 'Processing'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]

    # Basic information
    name = models.CharField(max_length=100)
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPE_CHOICES, default='MONTHLY')
    start_date = models.DateField()
    end_date = models.DateField()
    payment_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    # Period summary metrics (auto-calculated from salary slips)
    total_employees = models.IntegerField(default=0, help_text='Total number of employees in this period')
    processed_employees = models.IntegerField(default=0, help_text='Number of processed salary slips')
    total_gross_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Sum of all gross pay')
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Sum of all deductions')
    total_net_pay = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Sum of all net pay')

    # Tracking fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_periods')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_periods')
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_periods', help_text='User who processed the payroll')
    processed_at = models.DateTimeField(null=True, blank=True, help_text='When the payroll was processed')

    # Additional fields
    notes = models.TextField(blank=True, help_text='Internal notes about this period')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']
        unique_together = ['start_date', 'end_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    @property
    def is_current(self):
        """Check if this period is currently active"""
        today = date.today()
        return self.start_date <= today <= self.end_date

    @property
    def is_semi_monthly(self):
        """Check if this is a semi-monthly period"""
        return self.period_type == 'SEMI_MONTHLY'

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

    def get_period_multiplier(self):
        """
        Get the multiplier for salary calculations based on period type.
        - MONTHLY: 1.0 (full monthly salary)
        - SEMI_MONTHLY: 0.5 (half of monthly salary)
        - WEEKLY/BI_WEEKLY: Based on working days
        """
        if self.period_type == 'SEMI_MONTHLY':
            return Decimal('0.5')
        elif self.period_type == 'MONTHLY':
            return Decimal('1.0')
        else:
            # For weekly/bi-weekly, calculate based on standard month (22 working days)
            return Decimal(str(self.working_days / 22)) if self.working_days > 0 else Decimal('1.0')

    def update_summary(self):
        """Update summary metrics from associated salary slips"""
        from django.db.models import Sum, Count

        summary = self.salary_slips.aggregate(
            total=Count('id'),
            processed=Count('id', filter=models.Q(status__in=['SUBMITTED', 'PAID'])),
            gross=Sum('gross_pay'),
            deductions=Sum('total_deduction'),
            net=Sum('net_pay')
        )

        self.total_employees = summary['total'] or 0
        self.processed_employees = summary['processed'] or 0
        self.total_gross_pay = summary['gross'] or Decimal('0.00')
        self.total_deductions = summary['deductions'] or Decimal('0.00')
        self.total_net_pay = summary['net'] or Decimal('0.00')
        self.save(update_fields=['total_employees', 'processed_employees', 'total_gross_pay',
                                'total_deductions', 'total_net_pay', 'updated_at'])


class SalaryComponent(models.Model):
    """ERPNext-style Salary Component with enhanced features"""
    COMPONENT_TYPE_CHOICES = [
        ('EARNING', 'Earning'),
        ('DEDUCTION', 'Deduction'),
    ]

    CALCULATION_TYPE_CHOICES = [
        ('FIXED', 'Fixed Amount'),
        ('PERCENTAGE', 'Percentage'),
        ('FORMULA', 'Formula Based'),
    ]

    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=50, blank=True)
    component_type = models.CharField(max_length=20, choices=COMPONENT_TYPE_CHOICES)
    calculation_type = models.CharField(max_length=20, choices=CALCULATION_TYPE_CHOICES)

    # ERPNext-style attributes
    is_payable = models.BooleanField(default=True, help_text="Whether this component should be paid")
    depends_on_payment_days = models.BooleanField(default=False, help_text="Calculate based on working days")
    depends_on_timesheet = models.BooleanField(default=False, help_text="Calculate based on timesheet data")
    is_tax_applicable = models.BooleanField(default=True, help_text="Include in tax calculations")
    is_additional_component = models.BooleanField(default=False, help_text="Can only be paid as additional salary")
    is_statistical_component = models.BooleanField(default=False, help_text="For information only, not included in totals")
    variable_based_on_taxable_salary = models.BooleanField(default=False, help_text="Standard tax deduction component")

    # Formula and condition support
    formula = models.TextField(blank=True, help_text="Python expression for calculation (e.g., base * 0.1)")
    condition = models.TextField(blank=True, help_text="Python expression for when to apply (e.g., grade == 'Manager')")
    round_to_nearest = models.IntegerField(default=0, help_text="Round amount to nearest value (0 = no rounding)")

    # Flexible benefits
    max_benefit_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Maximum yearly benefit amount")
    pay_against_benefit_claim = models.BooleanField(default=False)

    # Legacy fields for backward compatibility
    percentage_of = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    percentage_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def calculate_amount(self, employee, base_salary, gross_salary=None, context=None):
        """Calculate component amount based on formula or fixed value"""
        if not context:
            context = {}

        # Add common variables to context
        context.update({
            'employee': employee,
            'base': base_salary,
            'basic': base_salary,
            'gross': gross_salary or base_salary,
            'round': round,
            'max': max,
            'min': min,
            'Decimal': Decimal,  # Allow Decimal in formulas
        })

        # Check condition first
        if self.condition:
            try:
                if not eval(self.condition, {'__builtins__': {}}, context):
                    return Decimal('0')
            except Exception:
                return Decimal('0')

        # Calculate amount
        amount = Decimal('0')

        if self.calculation_type == 'FORMULA' and self.formula:
            try:
                amount = Decimal(str(eval(self.formula, {'__builtins__': {}}, context)))
            except Exception:
                amount = Decimal('0')
        elif self.calculation_type == 'PERCENTAGE' and self.percentage_value:
            if self.percentage_of:
                base_amount = context.get(self.percentage_of.code.lower(), base_salary)
                amount = Decimal(str(base_amount)) * self.percentage_value / 100
            else:
                amount = base_salary * self.percentage_value / 100

        # Round if specified
        if self.round_to_nearest > 0:
            amount = round(amount / self.round_to_nearest) * self.round_to_nearest

        return amount


class SalaryStructure(models.Model):
    """ERPNext-style Salary Structure - defines how salary is calculated"""
    name = models.CharField(max_length=100, unique=True)
    company = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    docstatus = models.IntegerField(default=0, choices=[(0, 'Draft'), (1, 'Submitted'), (2, 'Cancelled')])

    # Payroll settings
    salary_slip_based_on_timesheet = models.BooleanField(default=False)
    hour_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Leave settings
    leave_encashment = models.BooleanField(default=False)
    max_benefits = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SalaryDetail(models.Model):
    """Components within a Salary Structure"""
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.CASCADE, related_name='salary_details')
    salary_component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)

    # Amount can be fixed or formula-based
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    formula = models.TextField(blank=True, help_text="Override component formula")
    condition = models.TextField(blank=True, help_text="Override component condition")

    # Statistical components don't affect total
    statistical_component = models.BooleanField(default=False)

    class Meta:
        unique_together = ['salary_structure', 'salary_component']
        ordering = ['salary_component__display_order']

    def __str__(self):
        return f"{self.salary_structure.name} - {self.salary_component.name}"


class SalaryStructureAssignment(models.Model):
    """Assign salary structure to employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_assignments')
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.CASCADE)

    from_date = models.DateField()
    to_date = models.DateField(null=True, blank=True)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, help_text="Base amount for percentage calculations")

    is_active = models.BooleanField(default=True)
    docstatus = models.IntegerField(default=0, choices=[(0, 'Draft'), (1, 'Submitted'), (2, 'Cancelled')])

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-from_date']
        unique_together = ['employee', 'from_date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.salary_structure.name}"


class AdditionalSalary(models.Model):
    """ERPNext-style Additional Salary for one-time payments/deductions"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='additional_salaries')
    salary_component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payroll_date = models.DateField(help_text="Date when this should be included in payroll")

    # Recurring settings
    is_recurring = models.BooleanField(default=False)
    to_date = models.DateField(null=True, blank=True, help_text="End date for recurring additional salary")

    # Reference
    ref_doctype = models.CharField(max_length=50, blank=True)
    ref_docname = models.CharField(max_length=100, blank=True)

    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    reason = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-payroll_date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.salary_component.name}: {self.amount}"


class EmployeeBenefit(models.Model):
    """Employee benefit claims and applications"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='benefits')
    earning_component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE, limit_choices_to={'component_type': 'EARNING'})

    max_benefit_amount = models.DecimalField(max_digits=12, decimal_places=2)
    claimed_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    remaining_benefit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['employee', 'earning_component', 'payroll_period']

    def save(self, *args, **kwargs):
        self.remaining_benefit = self.max_benefit_amount - self.claimed_amount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.earning_component.name}"


class EmployeeSalary(models.Model):
    """
    Employee Salary Information
    NOTE: basic_salary is now a computed property from SalaryStructureAssignment.
    To update an employee's salary, create a new SalaryStructureAssignment.
    """
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='salary_info')

    # DEPRECATED: basic_salary database field removed - now computed from SalaryStructureAssignment
    # Migration: Run 'python manage.py migrate' to remove the database column
    # basic_salary = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])

    # Allowances specific to Cambodia
    housing_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    transport_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    meal_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    phone_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    seniority_allowance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Banking Information
    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)
    bank_account_name = models.CharField(max_length=100, blank=True)

    # Payment Method
    PAYMENT_METHOD_CHOICES = [
        ('BANK', 'Bank Transfer'),
        ('CASH', 'Cash'),
        ('CHEQUE', 'Cheque'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='BANK')

    effective_date = models.DateField(default=date.today)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.first_name} {self.employee.last_name} - Salary Info"

    def get_active_salary_assignment(self):
        """Get the active salary structure assignment for this employee"""
        try:
            return SalaryStructureAssignment.objects.filter(
                employee=self.employee,
                is_active=True,
                docstatus=1
            ).order_by('-from_date').first()
        except:
            return None

    @property
    def basic_salary(self):
        """
        Get basic salary from active SalaryStructureAssignment.
        This is now the SINGLE SOURCE OF TRUTH for employee salary.

        To update salary: Create a new SalaryStructureAssignment with the new base_salary.
        """
        assignment = self.get_active_salary_assignment()
        if assignment:
            return assignment.base_salary
        return Decimal('0.00')

    @property
    def gross_salary(self):
        """Calculate gross salary: basic + all allowances"""
        return (self.basic_salary +
                self.housing_allowance +
                self.transport_allowance +
                self.meal_allowance +
                self.phone_allowance +
                self.seniority_allowance)


class TaxSlab(models.Model):
    """Cambodia Tax Slabs for Salary Tax on Resident"""
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0), MaxValueValidator(100)])
    fixed_tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['min_amount']

    def __str__(self):
        if self.max_amount:
            return f"KHR {self.min_amount:,.0f} - {self.max_amount:,.0f} ({self.tax_rate}%)"
        return f"Above KHR {self.min_amount:,.0f} ({self.tax_rate}%)"


class NSSFConfiguration(models.Model):
    """National Social Security Fund (NSSF) Configuration for Cambodia"""
    CONTRIBUTION_TYPE_CHOICES = [
        ('OCCUPATIONAL_RISK', 'Occupational Risk'),
        ('HEALTH_CARE', 'Health Care'),
    ]

    contribution_type = models.CharField(max_length=30, choices=CONTRIBUTION_TYPE_CHOICES)
    employee_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Employee contribution rate (%)")
    employer_rate = models.DecimalField(max_digits=5, decimal_places=2, help_text="Employer contribution rate (%)")
    max_salary_cap = models.DecimalField(max_digits=12, decimal_places=2, help_text="Maximum salary for calculation")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.get_contribution_type_display()} - Employee: {self.employee_rate}%, Employer: {self.employer_rate}%"


class SalarySlip(models.Model):
    """ERPNext-style Salary Slip (renamed from Payroll for consistency)"""
    # Basic info
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_slips')
    payroll_period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='salary_slips')
    salary_structure = models.ForeignKey(SalaryStructure, on_delete=models.CASCADE, null=True, blank=True)

    # Dates
    start_date = models.DateField()
    end_date = models.DateField()
    posting_date = models.DateField(default=date.today)

    # Working days calculation
    total_working_days = models.IntegerField(default=0)
    payment_days = models.IntegerField(default=0)
    leave_without_pay = models.IntegerField(default=0)

    # Basic salary info
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    # Totals (calculated from salary slip details)
    gross_pay = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    total_deduction = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    net_pay = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    rounded_total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    # Additional info
    hour_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_working_hours = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0'))

    # Overtime tracking
    overtime_hours = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0'), help_text="Total overtime hours for this period")
    overtime_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.5'), help_text="Overtime multiplier (e.g., 1.5 for 1.5x pay)")

    # ERPNext-style document status
    docstatus = models.IntegerField(default=0, choices=[(0, 'Draft'), (1, 'Submitted'), (2, 'Cancelled')])

    # Legacy status for backward compatibility
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('CALCULATED', 'Calculated'),
        ('APPROVED', 'Approved'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    # Payment Info
    payment_method = models.CharField(max_length=20, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_payrolls')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_payrolls')

    class Meta:
        unique_together = ['payroll_period', 'employee']
        ordering = ['-start_date', 'employee__employee_id']

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.payroll_period.name}"

    def calculate_working_days(self):
        """Calculate working days based on attendance records"""
        if hasattr(self.employee, 'attendance_records'):
            from attendance.models import AttendanceRecord
            attendance_count = AttendanceRecord.objects.filter(
                employee=self.employee,
                date__range=[self.start_date, self.end_date],
                status='PRESENT'
            ).count()
            self.payment_days = attendance_count

        # Calculate LWP
        self.leave_without_pay = self.total_working_days - self.payment_days
        return self.payment_days

    def get_salary_structure_assignment(self):
        """Get active salary structure assignment for the employee"""
        try:
            return SalaryStructureAssignment.objects.filter(
                employee=self.employee,
                from_date__lte=self.end_date,
                is_active=True,
                docstatus=1
            ).order_by('-from_date').first()
        except SalaryStructureAssignment.DoesNotExist:
            return None

    def calculate_salary_tax(self):
        """Calculate Cambodia salary tax based on progressive tax slabs"""
        # Get total taxable earnings
        taxable_earnings = self.get_total_taxable_earnings()

        # Subtract employee NSSF contribution
        employee_nssf = self.get_total_component_amount('NSSF_EMPLOYEE') or Decimal('0')
        taxable_income = taxable_earnings - employee_nssf

        # Get spouse and children deductions (150,000 KHR per dependent)
        dependent_deduction = Decimal('150000') * (self.employee.number_of_dependents if hasattr(self.employee, 'number_of_dependents') else 0)
        taxable_income = max(taxable_income - dependent_deduction, Decimal('0'))

        tax = Decimal('0')
        tax_slabs = TaxSlab.objects.filter(
            is_active=True,
            effective_from__lte=self.end_date
        ).order_by('min_amount')

        for slab in tax_slabs:
            if taxable_income <= slab.min_amount:
                break

            if slab.max_amount:
                taxable_in_slab = min(taxable_income, slab.max_amount) - slab.min_amount
            else:
                taxable_in_slab = taxable_income - slab.min_amount

            tax += (taxable_in_slab * slab.tax_rate / 100) + slab.fixed_tax

            if slab.max_amount and taxable_income <= slab.max_amount:
                break

        return tax

    def calculate_nssf(self):
        """Calculate NSSF contributions for Cambodia"""
        nssf_configs = NSSFConfiguration.objects.filter(
            is_active=True,
            effective_from__lte=self.end_date
        )

        employee_total = Decimal('0')
        employer_total = Decimal('0')
        gross_pay = self.get_total_earnings()

        for config in nssf_configs:
            # Cap salary at maximum if specified
            salary_for_calc = min(gross_pay, config.max_salary_cap)

            employee_contribution = salary_for_calc * config.employee_rate / 100
            employer_contribution = salary_for_calc * config.employer_rate / 100

            employee_total += employee_contribution
            employer_total += employer_contribution

        return employee_total, employer_total

    def get_total_earnings(self):
        """Get total earnings from salary slip details"""
        return self.details.filter(
            salary_component__component_type='EARNING',
            salary_component__is_statistical_component=False
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    def get_total_deductions(self):
        """Get total deductions from salary slip details"""
        return self.details.filter(
            salary_component__component_type='DEDUCTION',
            salary_component__is_statistical_component=False
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    def get_total_taxable_earnings(self):
        """Get total taxable earnings"""
        return self.details.filter(
            salary_component__component_type='EARNING',
            salary_component__is_tax_applicable=True,
            salary_component__is_statistical_component=False
        ).aggregate(total=models.Sum('amount'))['total'] or Decimal('0')

    def get_total_component_amount(self, component_code):
        """Get amount for a specific component"""
        try:
            detail = self.details.get(salary_component__code=component_code)
            return detail.amount
        except:
            return Decimal('0')

    def get_total_allowances(self):
        """
        Get total allowances (excluding base/basic salary)
        Returns sum of all earning components except basic salary
        """
        # Common allowance component codes to include
        allowance_codes = [
            'HOUSING_ALLOWANCE', 'TRANSPORT_ALLOWANCE', 'MEAL_ALLOWANCE',
            'PHONE_ALLOWANCE', 'SENIORITY_ALLOWANCE', 'POSITION_ALLOWANCE'
        ]

        total = Decimal('0')
        for code in allowance_codes:
            total += self.get_total_component_amount(code)

        return total

    @property
    def housing_allowance(self):
        """Get housing allowance amount from salary slip details"""
        return self.get_total_component_amount('HOUSING_ALLOWANCE')

    @property
    def transport_allowance(self):
        """Get transport allowance amount from salary slip details"""
        return self.get_total_component_amount('TRANSPORT_ALLOWANCE')

    @property
    def meal_allowance(self):
        """Get meal allowance amount from salary slip details"""
        return self.get_total_component_amount('MEAL_ALLOWANCE')

    @property
    def phone_allowance(self):
        """Get phone allowance amount from salary slip details"""
        return self.get_total_component_amount('PHONE_ALLOWANCE')


    def calculate_from_salary_structure(self):
        """
        Calculate salary slip from assigned salary structure
        Following Cambodian Labor Law:
            pass
        - NSSF: 3.5% employee contribution (capped at KHR 1,300,000 for health care)
        - Progressive Tax: 0%, 5%, 10%, 15%, 20% based on taxable income
        - Dependent deduction: KHR 150,000 per dependent

        Supports multiple period types:
            pass
        - MONTHLY: Full monthly salary
        - SEMI_MONTHLY: 50% of monthly salary (automatic split)
        - WEEKLY: Prorated by working days
        - BI_WEEKLY: Prorated by working days
        """
        assignment = self.get_salary_structure_assignment()
        if not assignment:
            return

        self.salary_structure = assignment.salary_structure

        # Determine base salary based on period type
        monthly_base_salary = assignment.base_salary

        # Apply automatic proration for semi-monthly periods
        if self.payroll_period.period_type == 'SEMI_MONTHLY':
            # Semi-monthly: Split monthly salary 50/50
            self.base_salary = monthly_base_salary * Decimal('0.5')
            period_multiplier = Decimal('0.5')
        elif self.payroll_period.period_type == 'MONTHLY':
            # Monthly: Use full monthly salary
            self.base_salary = monthly_base_salary
            period_multiplier = Decimal('1.0')
        else:
            # Weekly/Bi-weekly: Use full base, will be prorated by working days
            self.base_salary = monthly_base_salary
            period_multiplier = Decimal('1.0')

        # Clear existing details
        self.details.all().delete()

        # Calculate working days if not set
        if self.payment_days == 0:
            self.calculate_working_days()

        # Create context for formula calculations
        context = {
            'base': self.base_salary,
            'basic': self.base_salary,
            'monthly_base': monthly_base_salary,  # Original monthly base
            'period_multiplier': period_multiplier,  # 0.5 for semi-monthly, 1.0 for others
            'working_days': self.total_working_days,
            'payment_days': self.payment_days,
            'lwp_days': self.leave_without_pay,
            'employee': self.employee,
            'hour_rate': self.hour_rate or Decimal('0'),  # For timesheet-based payroll
            'total_working_hours': self.total_working_hours or Decimal('0'),  # For timesheet-based payroll
            'Decimal': Decimal,  # Allow Decimal in formulas
            'min': min,
            'max': max,
            'round': round,
        }

        # ===== STEP 1: Process EARNINGS first =====
        earning_details = assignment.salary_structure.salary_details.filter(
            salary_component__component_type='EARNING'
        )

        for salary_detail in earning_details:
            component = salary_detail.salary_component

            # Skip if conditions not met
            if component.condition:
                try:
                    if not eval(component.condition, {'__builtins__': {}}, context):
                        continue
                except:
                    continue

            # Calculate amount
            if salary_detail.formula:
                # Use overridden formula
                try:
                    amount = Decimal(str(eval(salary_detail.formula, {'__builtins__': {}}, context)))
                except:
                    amount = salary_detail.amount
            elif component.formula:
                # Use component formula
                amount = component.calculate_amount(self.employee, self.base_salary, context=context)
            else:
                # Use fixed amount
                amount = salary_detail.amount

            # Apply payment days calculation if needed
            if component.depends_on_payment_days and self.total_working_days > 0:
                amount = amount * self.payment_days / self.total_working_days

            # Create salary slip detail
            if amount != 0 or not component.is_statistical_component:
                SalarySlipDetail.objects.create(
                    salary_slip=self,
                    salary_component=component,
                    amount=amount
                )
                context[component.code.lower()] = amount

        # ===== STEP 2: Calculate GROSS PAY and add to context =====
        gross_pay = self.get_total_earnings()
        context['gross'] = gross_pay
        context['gross_pay'] = gross_pay

        # ===== STEP 3: Process DEDUCTIONS (now gross is available) =====
        deduction_details = assignment.salary_structure.salary_details.filter(
            salary_component__component_type='DEDUCTION'
        )

        for salary_detail in deduction_details:
            component = salary_detail.salary_component

            # Skip if conditions not met
            if component.condition:
                try:
                    if not eval(component.condition, {'__builtins__': {}}, context):
                        continue
                except:
                    continue

            # Special handling for TAX component - use progressive tax calculation
            if component.code == 'TAX' or component.variable_based_on_taxable_salary:
                # Calculate Cambodia progressive tax
                amount = self.calculate_salary_tax()
            elif component.code == 'NSSF_EMPLOYEE':
                # Calculate NSSF following Cambodian law
                amount, _ = self.calculate_nssf()
            else:
                # Calculate amount for other deductions
                if salary_detail.formula:
                    # Use overridden formula
                    try:
                        amount = Decimal(str(eval(salary_detail.formula, {'__builtins__': {}}, context)))
                    except Exception as e:
                        amount = salary_detail.amount
                elif component.formula:
                    # Use component formula
                    amount = component.calculate_amount(self.employee, self.base_salary, gross_pay, context)
                else:
                    # Use fixed amount
                    amount = salary_detail.amount

                # Apply payment days calculation if needed
                if component.depends_on_payment_days and self.total_working_days > 0:
                    amount = amount * self.payment_days / self.total_working_days

            # Create salary slip detail
            if amount != 0 or not component.is_statistical_component:
                SalarySlipDetail.objects.create(
                    salary_slip=self,
                    salary_component=component,
                    amount=amount
                )
                context[component.code.lower()] = amount

        # ===== STEP 4: Process additional salaries =====
        additional_salaries = AdditionalSalary.objects.filter(
            employee=self.employee,
            payroll_date__range=[self.start_date, self.end_date],
            status='ACTIVE'
        )

        for additional in additional_salaries:
            # Check if component already exists
            existing_detail = self.details.filter(salary_component=additional.salary_component).first()
            if existing_detail:
                existing_detail.amount += additional.amount
                existing_detail.save()
            else:
                SalarySlipDetail.objects.create(
                    salary_slip=self,
                    salary_component=additional.salary_component,
                    amount=additional.amount
                )

        # ===== STEP 5: Calculate final totals =====
        self.calculate_totals()

    def calculate_totals(self):
        """Calculate final totals"""
        self.gross_pay = self.get_total_earnings()
        self.total_deduction = self.get_total_deductions()
        self.net_pay = self.gross_pay - self.total_deduction
        self.rounded_total = round(self.net_pay)

        self.status = 'CALCULATED'
        self.save()

    def calculate(self):
        """Calculate all payroll components"""
        # Calculate gross salary
        self.gross_salary = (
            self.basic_salary +
            self.housing_allowance +
            self.transport_allowance +
            self.meal_allowance +
            self.phone_allowance +
            self.seniority_allowance +
            self.overtime_amount +
            self.bonus +
            self.other_earnings
        )

        # Calculate NSSF
        self.nssf_employee, self.nssf_employer = self.calculate_nssf()

        # Calculate salary tax
        self.salary_tax = self.calculate_salary_tax()

        # Calculate total deductions
        self.total_deductions = (
            self.salary_tax +
            self.nssf_employee +
            self.advance_salary +
            self.loan_deduction +
            self.other_deductions
        )

        # Calculate net salary
        self.net_salary = self.gross_salary - self.total_deductions

        self.status = 'CALCULATED'
        self.save()


class SalarySlipDetail(models.Model):
    """ERPNext-style Salary Slip Detail - individual components"""
    salary_slip = models.ForeignKey(SalarySlip, on_delete=models.CASCADE, related_name='details')
    salary_component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    default_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))

    # For formula-based calculations
    depends_on_payment_days = models.BooleanField(default=False)

    class Meta:
        unique_together = ['salary_slip', 'salary_component']
        ordering = ['salary_component__display_order', 'salary_component__name']

    def __str__(self):
        return f"{self.salary_slip.employee.get_full_name()} - {self.salary_component.name}: {self.amount}"


class PayrollEntry(models.Model):
    """ERPNext-style Payroll Entry for bulk payroll processing"""
    company = models.CharField(max_length=100, blank=True)
    payroll_frequency = models.CharField(max_length=20, default='Monthly')
    start_date = models.DateField()
    end_date = models.DateField()
    posting_date = models.DateField(default=date.today)

    # Department and employee filters
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    employees = models.ManyToManyField(Employee, blank=True)

    # Payment settings
    salary_slips_created = models.BooleanField(default=False)
    salary_slips_submitted = models.BooleanField(default=False)
    bank_entries_made = models.BooleanField(default=False)

    # Validation
    validate_attendance = models.BooleanField(default=True)

    # Status and workflow
    docstatus = models.IntegerField(default=0, choices=[(0, 'Draft'), (1, 'Submitted'), (2, 'Cancelled')])
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"Payroll Entry: {self.start_date} to {self.end_date}"

    def create_salary_slips(self):
        """Create salary slips for all employees in the payroll entry"""
        employees = self.employees.all() if self.employees.exists() else Employee.objects.filter(employment_status='active')

        if self.department:
            employees = employees.filter(department=self.department)

        created_slips = []
        for employee in employees:
            # Check if salary slip already exists
            existing_slip = SalarySlip.objects.filter(
                employee=employee,
                start_date=self.start_date,
                end_date=self.end_date
            ).first()

            if not existing_slip:
                salary_slip = SalarySlip.objects.create(
                    employee=employee,
                    payroll_period_id=1,  # You may need to adjust this
                    start_date=self.start_date,
                    end_date=self.end_date,
                    posting_date=self.posting_date,
                    total_working_days=22,  # Calculate based on your business logic
                )
                salary_slip.calculate_from_salary_structure()
                created_slips.append(salary_slip)

        self.salary_slips_created = True
        self.save()
        return created_slips


# Backward compatibility alias
Payroll = SalarySlip

# Legacy model for backward compatibility
class PayrollDetail(models.Model):
    """Detailed breakdown of payroll components"""
    payroll = models.ForeignKey('SalarySlip', on_delete=models.CASCADE, related_name='legacy_details')
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ['payroll', 'component']
        ordering = ['component__display_order']

    def __str__(self):
        return f"{self.payroll.employee.get_full_name()} - {self.component.name}: {self.amount}"


class SalaryAdvance(models.Model):
    """Track salary advances given to employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='salary_advances')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    request_date = models.DateField(default=date.today)
    approval_date = models.DateField(null=True, blank=True)

    REPAYMENT_METHOD_CHOICES = [
        ('ONE_TIME', 'One Time Deduction'),
        ('INSTALLMENTS', 'Monthly Installments'),
    ]
    repayment_method = models.CharField(max_length=20, choices=REPAYMENT_METHOD_CHOICES, default='ONE_TIME')
    installment_months = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(12)])

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('PARTIALLY_PAID', 'Partially Paid'),
        ('PAID', 'Paid'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    reason = models.TextField()
    remarks = models.TextField(blank=True)

    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_advances')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_advances')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-request_date']

    def __str__(self):
        return f"{self.employee.get_full_name()} - KHR {self.amount:,.0f} ({self.status})"


class EmployeeLoan(models.Model):
    """Track employee loans"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='loans')
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    loan_term_months = models.IntegerField(validators=[MinValueValidator(1)])
    monthly_installment = models.DecimalField(max_digits=10, decimal_places=2)

    start_date = models.DateField()
    end_date = models.DateField()

    total_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    remaining_balance = models.DecimalField(max_digits=12, decimal_places=2)

    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('DEFAULTED', 'Defaulted'),
        ('CANCELLED', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    purpose = models.TextField()
    remarks = models.TextField(blank=True)

    requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='requested_loans')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_loans')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} - Loan KHR {self.loan_amount:,.0f}"

    def calculate_monthly_installment(self):
        """Calculate monthly installment with interest"""
        if self.interest_rate > 0:
            monthly_rate = self.interest_rate / 100 / 12
            installment = (self.loan_amount * monthly_rate * (1 + monthly_rate) ** self.loan_term_months) / \
                         ((1 + monthly_rate) ** self.loan_term_months - 1)
        else:
            installment = self.loan_amount / self.loan_term_months

        return installment


class PayslipTemplate(models.Model):
    """Template for generating payslips"""
    name = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    header_content = models.TextField(help_text="HTML content for payslip header")
    footer_content = models.TextField(help_text="HTML content for payslip footer")
    css_styles = models.TextField(blank=True, help_text="Custom CSS for payslip")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_default:
            PayslipTemplate.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
