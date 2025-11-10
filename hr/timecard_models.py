from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from .models import Employee
from datetime import date, timedelta
import calendar

class Timecard(models.Model):
    """
    Represents a timecard for an employee for a specific pay period
    """
    APPROVAL_STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='timecards',
        verbose_name=_('Employee')
    )

    year = models.IntegerField(
        _('Year'),
        validators=[
            MinValueValidator(2020),
            MaxValueValidator(2100)
        ]
    )

    month = models.IntegerField(
        _('Month'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(12)
        ]
    )

    department = models.CharField(
        _('Department'),
        max_length=200,
        blank=True
    )

    position = models.CharField(
        _('Position'),
        max_length=200,
        blank=True
    )

    total_hours = models.DecimalField(
        _('Total Hours'),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )

    approval_status = models.CharField(
        _('Approval Status'),
        max_length=20,
        choices=APPROVAL_STATUS_CHOICES,
        default='draft'
    )

    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_timecards',
        verbose_name=_('Approved By')
    )

    approval_date = models.DateTimeField(
        _('Approval Date'),
        null=True,
        blank=True
    )

    notes = models.TextField(
        _('Notes'),
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Timecard')
        verbose_name_plural = _('Timecards')
        unique_together = [['employee', 'year', 'month']]
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.employee.full_name} - {self.year}/{self.month:02d}"

    def save(self, *args, **kwargs):
        if self.employee and not self.department:
            self.department = self.employee.department.name if self.employee.department else ''
        if self.employee and not self.position:
            self.position = self.employee.position.name if self.employee.position else ''
        super().save(*args, **kwargs)

    def calculate_total_hours(self):
        """Calculate total hours from all timecard entries"""
        total = sum(entry.hours for entry in self.entries.all())
        self.total_hours = total
        self.save(update_fields=['total_hours'])
        return total

    def get_payroll_period_start(self):
        """Get the start date of the payroll period (21st of previous month)"""
        if self.month == 1:
            return date(self.year - 1, 12, 21)
        return date(self.year, self.month - 1, 21)

    def get_payroll_period_end(self):
        """Get the end date of the payroll period (20th of current month)"""
        return date(self.year, self.month, 20)

    def get_submission_deadline(self):
        """Get the submission deadline (21st of current month)"""
        return date(self.year, self.month, 21)

    def is_submission_overdue(self):
        """Check if the submission deadline has passed"""
        return date.today() > self.get_submission_deadline()

    def days_until_deadline(self):
        """Calculate days remaining until submission deadline"""
        deadline = self.get_submission_deadline()
        today = date.today()
        return (deadline - today).days


class TimecardEntry(models.Model):
    """
    Represents daily hours entry for a timecard
    Enhanced with project and timesheet relationships following ERPNext pattern
    """
    timecard = models.ForeignKey(
        Timecard,
        on_delete=models.CASCADE,
        related_name='entries',
        verbose_name=_('Timecard')
    )

    date = models.DateField(
        _('Date')
    )

    # Legacy field for backward compatibility
    project_name = models.CharField(
        _('Project Name'),
        max_length=200,
        blank=True,
        help_text=_('Legacy field - use project field for new entries')
    )

    # New project relationship
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timecard_entries',
        verbose_name=_('Project')
    )

    # Link to timesheet for ERPNext-style integration
    timesheet = models.ForeignKey(
        'project.Timesheet',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='timecard_entries',
        verbose_name=_('Timesheet')
    )

    hours = models.DecimalField(
        _('Hours'),
        max_digits=4,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(24)
        ]
    )

    is_weekend = models.BooleanField(
        _('Is Weekend'),
        default=False
    )

    is_holiday = models.BooleanField(
        _('Is Holiday'),
        default=False
    )

    # Additional fields for better time tracking
    is_billable = models.BooleanField(
        _('Is Billable'),
        default=True,
        help_text=_('Whether this time is billable to client')
    )

    activity_description = models.CharField(
        _('Activity Description'),
        max_length=500,
        blank=True,
        help_text=_('Brief description of work performed')
    )

    notes = models.TextField(
        _('Notes'),
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Timecard Entry')
        verbose_name_plural = _('Timecard Entries')
        # Allow multiple entries per day for different projects
        # Remove problematic unique_together constraint for now
        # unique_together = [['timecard', 'date', 'project_name']]
        ordering = ['date', 'project_name']

    def __str__(self):
        project_display = self.get_project_display()
        return f"{self.timecard.employee.full_name} - {self.date} - {project_display} - {self.hours}h"

    def get_project_display(self):
        """Get display name for project (project or legacy project_name)"""
        if self.project:
            return self.project.project_name
        return self.project_name or 'No Project'

    def get_project_code(self):
        """Get project code if available"""
        if self.project:
            return self.project.project_code
        return None

    def save(self, *args, **kwargs):
        from django.db.utils import ProgrammingError, OperationalError

        try:
            # Mark weekends automatically
            if self.date:
                weekday = self.date.weekday()
                self.is_weekend = weekday in [5, 6]  # Saturday = 5, Sunday = 6

            # Auto-create or link to timesheet if project is specified
            if self.project and not self.timesheet:
                self._create_or_link_timesheet()

            # Ensure project_name is populated for backward compatibility
            if self.project and not self.project_name:
                self.project_name = self.project.project_name

            super().save(*args, **kwargs)

            # Update timecard total hours
            if self.timecard:
                self.timecard.calculate_total_hours()

            # Update timesheet totals if linked
            if self.timesheet:
                self.timesheet.calculate_totals()
        except (ProgrammingError, OperationalError):
            # During migrations, just save without extra operations
            super().save(*args, **kwargs)

    def _create_or_link_timesheet(self):
        """Create or link to appropriate timesheet"""
        if not self.project or not self.timecard:
            return

        try:
            from project.models import Timesheet
            from datetime import datetime
            from django.db.utils import ProgrammingError, OperationalError

            # Get start and end of month for timesheet period
            start_date = self.date.replace(day=1)
            if start_date.month == 12:
                end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)

            # Find or create timesheet for this employee, project, and period
            timesheet, created = Timesheet.objects.get_or_create(
                employee=self.timecard.employee,
                company=self.project.company,
                start_date=start_date,
                end_date=end_date,
                defaults={
                    'status': 'draft',
                    'total_hours': 0,
                    'total_billable_hours': 0,
                    'per_hour_rate': self._get_employee_hourly_rate()
                }
            )

            self.timesheet = timesheet
        except (ProgrammingError, OperationalError):
            # Table doesn't exist yet (during migrations)
            pass

    def _get_employee_hourly_rate(self):
        """Calculate employee hourly rate from salary"""
        if self.timecard and self.timecard.employee and self.timecard.employee.salary:
            # Assuming monthly salary, convert to hourly (160 hours/month)
            return self.timecard.employee.salary / 160
        return None