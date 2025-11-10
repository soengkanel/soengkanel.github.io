"""
Timesheet Models for hourly-based payroll
"""
from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
from hr.models import Employee


class Timesheet(models.Model):
    """Employee timesheet for hourly-based payroll"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='payroll_timesheets')
    start_date = models.DateField()
    end_date = models.DateField()

    # Time tracking
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))
    billable_hours = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0.00'))

    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')

    # ERPNext-style docstatus
    DOCSTATUS_CHOICES = [
        (0, 'Draft'),
        (1, 'Submitted'),
        (2, 'Cancelled'),
    ]
    docstatus = models.IntegerField(choices=DOCSTATUS_CHOICES, default=0)

    # Notes
    note = models.TextField(blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_timesheets')

    class Meta:
        ordering = ['-start_date']
        db_table = 'payroll_timesheet'
        verbose_name = 'Timesheet'
        verbose_name_plural = 'Timesheets'

    def __str__(self):
        return f"{self.employee.get_full_name()} - {self.start_date} to {self.end_date}"

    def calculate_total_hours(self):
        """Calculate total hours from detail entries"""
        total = self.details.aggregate(total=models.Sum('hours'))['total'] or Decimal('0.00')
        self.total_hours = total

        billable = self.details.filter(billable=True).aggregate(total=models.Sum('hours'))['total'] or Decimal('0.00')
        self.billable_hours = billable

        self.save(update_fields=['total_hours', 'billable_hours'])
        return total


class TimesheetDetail(models.Model):
    """Timesheet detail entries"""
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='details')

    # Activity details
    activity = models.CharField(max_length=200)
    from_time = models.DateTimeField()
    to_time = models.DateTimeField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)

    # Project/Task tracking
    project = models.CharField(max_length=100, blank=True)
    task = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    # Billing
    billable = models.BooleanField(default=True)
    billing_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['from_time']
        db_table = 'payroll_timesheet_detail'
        verbose_name = 'Timesheet Detail'
        verbose_name_plural = 'Timesheet Details'

    def __str__(self):
        return f"{self.activity} - {self.hours}h"

    def save(self, *args, **kwargs):
        """Auto-calculate hours if not provided"""
        if not self.hours and self.from_time and self.to_time:
            duration = self.to_time - self.from_time
            self.hours = Decimal(duration.total_seconds() / 3600)
        super().save(*args, **kwargs)

        # Update parent timesheet totals
        if self.timesheet:
            self.timesheet.calculate_total_hours()