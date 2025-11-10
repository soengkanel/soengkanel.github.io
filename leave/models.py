from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from hr.models import Employee
from datetime import date, timedelta
import calendar


class LeaveType(models.Model):
    """Leave type configuration (Annual, Sick, Personal, etc.)"""
    name = models.CharField(_('Leave Type'), max_length=100)
    code = models.CharField(_('Code'), max_length=10, unique=True)
    max_days_per_year = models.PositiveIntegerField(_('Max Days Per Year'), default=20)
    carry_forward_allowed = models.BooleanField(_('Carry Forward Allowed'), default=False)
    max_carry_forward_days = models.PositiveIntegerField(_('Max Carry Forward Days'), default=0)
    encashment_allowed = models.BooleanField(_('Encashment Allowed'), default=False)
    include_holiday = models.BooleanField(_('Include Holidays'), default=False)
    is_paid = models.BooleanField(_('Paid Leave'), default=True)

    # ERPNext-style fields
    apply_in_advance_days = models.PositiveIntegerField(_('Apply in Advance (Days)'), default=0)
    maximum_continuous_days = models.PositiveIntegerField(_('Max Continuous Days'), default=365)
    minimum_continuous_days = models.PositiveIntegerField(_('Min Continuous Days'), default=1)

    # Medical certificate requirements
    medical_certificate_required = models.BooleanField(_('Medical Certificate Required'), default=False)
    medical_certificate_min_days = models.PositiveIntegerField(_('Medical Certificate Min Days'), default=3)

    color = models.CharField(_('Color'), max_length=7, default='#007bff')
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Leave Type')
        verbose_name_plural = _('Leave Types')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class LeavePolicy(models.Model):
    """Leave policy configuration for different employee groups"""
    name = models.CharField(_('Policy Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)

    # Eligibility criteria
    min_employment_months = models.PositiveIntegerField(_('Minimum Employment (Months)'), default=0)
    applicable_to_probation = models.BooleanField(_('Applicable to Probation'), default=False)

    # Approval workflow
    requires_approval = models.BooleanField(_('Requires Approval'), default=True)
    auto_approve_half_day = models.BooleanField(_('Auto Approve Half Day'), default=False)
    max_days_auto_approve = models.PositiveIntegerField(_('Max Days Auto Approve'), default=0)

    # Regional holidays
    include_regional_holidays = models.BooleanField(_('Include Regional Holidays'), default=True)
    regional_holiday_list = models.TextField(_('Regional Holiday List'), blank=True,
                                           help_text=_('JSON format holiday configuration'))

    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Leave Policy')
        verbose_name_plural = _('Leave Policies')
        ordering = ['name']

    def __str__(self):
        return self.name


class LeavePolicyLeaveType(models.Model):
    """Many-to-many relationship between Leave Policy and Leave Types with allocation"""
    leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE, related_name='leave_allocations')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='policy_allocations')
    annual_allocation = models.FloatField(_('Annual Allocation'), default=0)

    class Meta:
        unique_together = ('leave_policy', 'leave_type')
        verbose_name = _('Leave Policy Allocation')
        verbose_name_plural = _('Leave Policy Allocations')

    def __str__(self):
        return f"{self.leave_policy.name} - {self.leave_type.name}: {self.annual_allocation} days"


class EmployeeLeavePolicy(models.Model):
    """Assign leave policy to employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_policies')
    leave_policy = models.ForeignKey(LeavePolicy, on_delete=models.CASCADE)
    effective_from = models.DateField(_('Effective From'))
    effective_to = models.DateField(_('Effective To'), null=True, blank=True)
    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Employee Leave Policy')
        verbose_name_plural = _('Employee Leave Policies')
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.employee} - {self.leave_policy.name}"


class LeaveAllocation(models.Model):
    """Annual leave allocation for employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_allocations')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(_('Year'), default=timezone.now().year)
    allocated_days = models.FloatField(_('Allocated Days'), default=0)
    used_days = models.FloatField(_('Used Days'), default=0)
    carried_forward = models.FloatField(_('Carried Forward'), default=0)

    # ERPNext-style fields
    from_date = models.DateField(_('From Date'))
    to_date = models.DateField(_('To Date'))

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        unique_together = ('employee', 'leave_type', 'year')
        verbose_name = _('Leave Allocation')
        verbose_name_plural = _('Leave Allocations')
        ordering = ['-year', 'employee', 'leave_type']

    def __str__(self):
        return f"{self.employee} - {self.leave_type.name} ({self.year})"

    @property
    def remaining_days(self):
        return self.allocated_days + self.carried_forward - self.used_days

    @property
    def utilization_percentage(self):
        if self.allocated_days > 0:
            return (self.used_days / self.allocated_days) * 100
        return 0


class Holiday(models.Model):
    """Public holidays configuration"""
    name = models.CharField(_('Holiday Name'), max_length=100)
    date = models.DateField(_('Date'))
    year = models.PositiveIntegerField(_('Year'), default=timezone.now().year)
    is_optional = models.BooleanField(_('Optional Holiday'), default=False)
    description = models.TextField(_('Description'), blank=True)

    # Regional application
    applies_to_all = models.BooleanField(_('Applies to All'), default=True)
    regions = models.TextField(_('Regions'), blank=True, help_text=_('Comma-separated list of regions'))

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        unique_together = ('name', 'date', 'year')
        verbose_name = _('Holiday')
        verbose_name_plural = _('Holidays')
        ordering = ['date']

    def __str__(self):
        return f"{self.name} - {self.date}"


class LeaveApplication(models.Model):
    """Leave application requests"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    ]

    LEAVE_SESSION_CHOICES = [
        ('full_day', _('Full Day')),
        ('first_half', _('First Half')),
        ('second_half', _('Second Half')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)

    # Leave period
    from_date = models.DateField(_('From Date'))
    to_date = models.DateField(_('To Date'))
    total_leave_days = models.FloatField(_('Total Leave Days'), default=0)

    # Session details for half-day leaves
    half_day = models.BooleanField(_('Half Day'), default=False)
    half_day_date = models.DateField(_('Half Day Date'), null=True, blank=True)
    leave_session = models.CharField(_('Leave Session'), max_length=20,
                                   choices=LEAVE_SESSION_CHOICES, default='full_day')

    # Application details
    reason = models.TextField(_('Reason'))
    posting_date = models.DateField(_('Posting Date'), default=timezone.now)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Approval workflow
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_leaves')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)

    # Supporting documents
    supporting_document = models.FileField(_('Supporting Document'), upload_to='leave_documents/',
                                         null=True, blank=True)
    medical_certificate = models.FileField(_('Medical Certificate'), upload_to='medical_certificates/',
                                         null=True, blank=True)

    # System fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_leaves')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Leave Application')
        verbose_name_plural = _('Leave Applications')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_type.name} ({self.from_date} to {self.to_date})"

    def clean(self):
        """Validate leave application"""
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise ValidationError(_('From date cannot be greater than to date'))

            # Check for overlapping leave applications
            overlapping = LeaveApplication.objects.filter(
                employee=self.employee,
                status__in=['approved', 'pending'],
                from_date__lte=self.to_date,
                to_date__gte=self.from_date
            ).exclude(pk=self.pk)

            if overlapping.exists():
                raise ValidationError(_('Leave application overlaps with existing application'))

    def save(self, *args, **kwargs):
        # Calculate total leave days
        if self.from_date and self.to_date:
            if self.half_day:
                self.total_leave_days = 0.5
            else:
                # Calculate working days excluding weekends and holidays
                self.total_leave_days = self.calculate_leave_days()

        super().save(*args, **kwargs)

    def calculate_leave_days(self):
        """Calculate total leave days excluding weekends and holidays"""
        if not self.from_date or not self.to_date:
            return 0

        total_days = 0
        current_date = self.from_date

        while current_date <= self.to_date:
            # Skip weekends (Saturday=5, Sunday=6)
            if current_date.weekday() < 5:  # Monday=0 to Friday=4
                # Check if it's not a holiday
                if not self.leave_type.include_holiday:
                    # Only count if it's not a holiday
                    if not Holiday.objects.filter(date=current_date).exists():
                        total_days += 1
                else:
                    total_days += 1

            current_date += timedelta(days=1)

        return total_days


class CompensatoryLeaveRequest(models.Model):
    """Compensatory leave requests for overtime work"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='compensatory_leaves')
    work_from_date = models.DateField(_('Work From Date'))
    work_to_date = models.DateField(_('Work To Date'))
    work_end_date = models.DateField(_('Work End Date'))
    reason = models.TextField(_('Reason for Overtime'))

    # Compensatory leave details
    leave_date = models.DateField(_('Leave Date'))
    half_day = models.BooleanField(_('Half Day'), default=False)

    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Compensatory Leave Request')
        verbose_name_plural = _('Compensatory Leave Requests')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - Comp Leave for {self.work_from_date}"


class LeaveEncashment(models.Model):
    """Leave encashment requests"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_encashments')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    leave_period_from = models.DateField(_('Leave Period From'))
    leave_period_to = models.DateField(_('Leave Period To'))

    encashable_days = models.FloatField(_('Encashable Days'))
    encashment_amount = models.DecimalField(_('Encashment Amount'), max_digits=12, decimal_places=2)
    encashment_date = models.DateField(_('Encashment Date'))

    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Leave Encashment')
        verbose_name_plural = _('Leave Encashments')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.leave_type.name} Encashment"


class LeaveBlockedDate(models.Model):
    """Blocked dates where leave cannot be applied"""
    from_date = models.DateField(_('From Date'))
    to_date = models.DateField(_('To Date'))
    reason = models.CharField(_('Reason'), max_length=200)
    applies_to_company = models.BooleanField(_('Applies to Company'), default=True)
    block_days = models.PositiveIntegerField(_('Block Days'), default=0)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Leave Blocked Date')
        verbose_name_plural = _('Leave Blocked Dates')
        ordering = ['from_date']

    def __str__(self):
        return f"Blocked: {self.from_date} to {self.to_date} - {self.reason}"