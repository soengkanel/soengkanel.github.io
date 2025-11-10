from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from hr.models import Employee
import uuid
from datetime import datetime, time, timedelta
import hashlib
import json


class BiometricDevice(models.Model):
    """Model for fingerprint/biometric devices"""
    DEVICE_TYPES = [
        ('fingerprint', _('Fingerprint Scanner')),
        ('face', _('Face Recognition')),
        ('iris', _('Iris Scanner')),
        ('card', _('Card Reader')),
        ('multi', _('Multi-Modal')),
    ]

    DEVICE_STATUS = [
        ('active', _('Active')),
        ('inactive', _('Inactive')),
        ('maintenance', _('Under Maintenance')),
        ('offline', _('Offline')),
    ]

    device_id = models.CharField(_('Device ID'), max_length=100, unique=True)
    name = models.CharField(_('Device Name'), max_length=200)
    device_type = models.CharField(_('Device Type'), max_length=20, choices=DEVICE_TYPES, default='fingerprint')
    location = models.CharField(_('Location'), max_length=200)
    ip_address = models.GenericIPAddressField(_('IP Address'), blank=True, null=True)
    port = models.IntegerField(_('Port'), default=4370)
    serial_number = models.CharField(_('Serial Number'), max_length=100, blank=True)
    firmware_version = models.CharField(_('Firmware Version'), max_length=50, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=DEVICE_STATUS, default='active')
    last_sync = models.DateTimeField(_('Last Sync'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Biometric Device')
        verbose_name_plural = _('Biometric Devices')
        ordering = ['location', 'name']

    def __str__(self):
        return f"{self.name} - {self.location}"


class BiometricTemplate(models.Model):
    """Store biometric templates for employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='biometric_templates')
    device = models.ForeignKey(BiometricDevice, on_delete=models.CASCADE, related_name='templates')
    template_type = models.CharField(_('Template Type'), max_length=20, choices=[
        ('fingerprint', _('Fingerprint')),
        ('face', _('Face')),
        ('iris', _('Iris')),
        ('card', _('Card')),
    ])
    template_data = models.TextField(_('Template Data'))  # Encrypted biometric template
    finger_index = models.IntegerField(_('Finger Index'), blank=True, null=True, validators=[
        MinValueValidator(0), MaxValueValidator(9)
    ])  # 0-9 for different fingers
    quality_score = models.IntegerField(_('Quality Score'), blank=True, null=True, validators=[
        MinValueValidator(0), MaxValueValidator(100)
    ])
    is_primary = models.BooleanField(_('Is Primary'), default=False)
    enrolled_at = models.DateTimeField(_('Enrolled At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Biometric Template')
        verbose_name_plural = _('Biometric Templates')
        unique_together = [['employee', 'device', 'template_type', 'finger_index']]

    def __str__(self):
        return f"{self.employee.full_name} - {self.template_type}"


class WorkSchedule(models.Model):
    """Define work schedules for employees"""
    name = models.CharField(_('Schedule Name'), max_length=100)
    code = models.CharField(_('Schedule Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)

    # Regular schedule
    monday_start = models.TimeField(_('Monday Start'), blank=True, null=True)
    monday_end = models.TimeField(_('Monday End'), blank=True, null=True)
    tuesday_start = models.TimeField(_('Tuesday Start'), blank=True, null=True)
    tuesday_end = models.TimeField(_('Tuesday End'), blank=True, null=True)
    wednesday_start = models.TimeField(_('Wednesday Start'), blank=True, null=True)
    wednesday_end = models.TimeField(_('Wednesday End'), blank=True, null=True)
    thursday_start = models.TimeField(_('Thursday Start'), blank=True, null=True)
    thursday_end = models.TimeField(_('Thursday End'), blank=True, null=True)
    friday_start = models.TimeField(_('Friday Start'), blank=True, null=True)
    friday_end = models.TimeField(_('Friday End'), blank=True, null=True)
    saturday_start = models.TimeField(_('Saturday Start'), blank=True, null=True)
    saturday_end = models.TimeField(_('Saturday End'), blank=True, null=True)
    sunday_start = models.TimeField(_('Sunday Start'), blank=True, null=True)
    sunday_end = models.TimeField(_('Sunday End'), blank=True, null=True)

    # Break times
    break_duration = models.IntegerField(_('Break Duration (minutes)'), default=60)
    break_start = models.TimeField(_('Break Start'), blank=True, null=True)

    # Flexibility settings
    flexible_hours = models.BooleanField(_('Flexible Hours'), default=False)
    core_hours_start = models.TimeField(_('Core Hours Start'), blank=True, null=True)
    core_hours_end = models.TimeField(_('Core Hours End'), blank=True, null=True)
    required_hours_per_day = models.DecimalField(_('Required Hours Per Day'), max_digits=4, decimal_places=2, default=8.0)

    # Grace periods
    late_grace_period = models.IntegerField(_('Late Grace Period (minutes)'), default=15)
    early_leave_grace_period = models.IntegerField(_('Early Leave Grace Period (minutes)'), default=15)

    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Work Schedule')
        verbose_name_plural = _('Work Schedules')
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_day_schedule(self, day_of_week):
        """Get schedule for a specific day (0=Monday, 6=Sunday)"""
        day_map = {
            0: (self.monday_start, self.monday_end),
            1: (self.tuesday_start, self.tuesday_end),
            2: (self.wednesday_start, self.wednesday_end),
            3: (self.thursday_start, self.thursday_end),
            4: (self.friday_start, self.friday_end),
            5: (self.saturday_start, self.saturday_end),
            6: (self.sunday_start, self.sunday_end),
        }
        return day_map.get(day_of_week, (None, None))

    def _calculate_hours(self, start_time, end_time):
        """Calculate hours between two times"""
        if not start_time or not end_time:
            return 0
        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), start_time)
        end = datetime.combine(datetime.today(), end_time)
        if end < start:  # Handle overnight shifts
            end += timedelta(days=1)
        return (end - start).total_seconds() / 3600

    def get_monday_hours(self):
        return self._calculate_hours(self.monday_start, self.monday_end)

    def get_tuesday_hours(self):
        return self._calculate_hours(self.tuesday_start, self.tuesday_end)

    def get_wednesday_hours(self):
        return self._calculate_hours(self.wednesday_start, self.wednesday_end)

    def get_thursday_hours(self):
        return self._calculate_hours(self.thursday_start, self.thursday_end)

    def get_friday_hours(self):
        return self._calculate_hours(self.friday_start, self.friday_end)

    def get_saturday_hours(self):
        return self._calculate_hours(self.saturday_start, self.saturday_end)

    def get_sunday_hours(self):
        return self._calculate_hours(self.sunday_start, self.sunday_end)

    def get_total_weekly_hours(self):
        """Calculate total weekly hours"""
        return (
            self.get_monday_hours() +
            self.get_tuesday_hours() +
            self.get_wednesday_hours() +
            self.get_thursday_hours() +
            self.get_friday_hours() +
            self.get_saturday_hours() +
            self.get_sunday_hours()
        )

    def get_working_days_count(self):
        """Count working days in the week"""
        days = [
            self.monday_start, self.tuesday_start, self.wednesday_start,
            self.thursday_start, self.friday_start, self.saturday_start, self.sunday_start
        ]
        return sum(1 for day in days if day)

    def get_avg_daily_hours(self):
        """Calculate average daily hours for working days"""
        working_days = self.get_working_days_count()
        if working_days == 0:
            return 0
        return self.get_total_weekly_hours() / working_days

    # Day enabled properties for template usage
    @property
    def monday_enabled(self):
        return bool(self.monday_start)

    @property
    def tuesday_enabled(self):
        return bool(self.tuesday_start)

    @property
    def wednesday_enabled(self):
        return bool(self.wednesday_start)

    @property
    def thursday_enabled(self):
        return bool(self.thursday_start)

    @property
    def friday_enabled(self):
        return bool(self.friday_start)

    @property
    def saturday_enabled(self):
        return bool(self.saturday_start)

    @property
    def sunday_enabled(self):
        return bool(self.sunday_start)


class EmployeeSchedule(models.Model):
    """Assign schedules to employees"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='schedules')
    schedule = models.ForeignKey(WorkSchedule, on_delete=models.CASCADE, related_name='employee_schedules')
    effective_from = models.DateField(_('Effective From'))
    effective_to = models.DateField(_('Effective To'), blank=True, null=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Employee Schedule')
        verbose_name_plural = _('Employee Schedules')
        ordering = ['-effective_from']

    def __str__(self):
        return f"{self.employee.full_name} - {self.schedule.name}"

    def clean(self):
        if self.effective_to and self.effective_from > self.effective_to:
            raise ValidationError(_('Effective from date must be before effective to date'))


class AttendanceRecord(models.Model):
    """Main attendance tracking model"""
    ATTENDANCE_STATUS = [
        ('present', _('Present')),
        ('absent', _('Absent')),
        ('late', _('Late')),
        ('early_leave', _('Early Leave')),
        ('half_day', _('Half Day')),
        ('holiday', _('Holiday')),
        ('weekend', _('Weekend')),
        ('leave', _('On Leave')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(_('Date'))
    schedule = models.ForeignKey(WorkSchedule, on_delete=models.SET_NULL, null=True, blank=True)

    # Clock times
    clock_in = models.DateTimeField(_('Clock In'), blank=True, null=True)
    clock_out = models.DateTimeField(_('Clock Out'), blank=True, null=True)

    # Device information
    clock_in_device = models.ForeignKey(BiometricDevice, on_delete=models.SET_NULL, null=True, blank=True, related_name='clock_in_records')
    clock_out_device = models.ForeignKey(BiometricDevice, on_delete=models.SET_NULL, null=True, blank=True, related_name='clock_out_records')

    # Project Integration - NEW FIELDS
    current_project = models.ForeignKey(
        'project.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='daily_attendance',
        verbose_name=_('Current Project'),
        help_text=_('Project the employee is primarily working on today')
    )
    location = models.CharField(
        _('Work Location'),
        max_length=200,
        blank=True,
        help_text=_('Physical location or project site')
    )
    is_remote_work = models.BooleanField(
        _('Remote Work'),
        default=False,
        help_text=_('Employee working remotely today')
    )

    # GPS Coordinates
    clock_in_latitude = models.DecimalField(
        _('Clock In Latitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text=_('GPS latitude for clock in location')
    )
    clock_in_longitude = models.DecimalField(
        _('Clock In Longitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text=_('GPS longitude for clock in location')
    )
    clock_out_latitude = models.DecimalField(
        _('Clock Out Latitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text=_('GPS latitude for clock out location')
    )
    clock_out_longitude = models.DecimalField(
        _('Clock Out Longitude'),
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text=_('GPS longitude for clock out location')
    )

    # Calculated fields
    total_hours = models.DecimalField(_('Total Hours'), max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(_('Overtime Hours'), max_digits=5, decimal_places=2, default=0)
    late_minutes = models.IntegerField(_('Late Minutes'), default=0)
    early_leave_minutes = models.IntegerField(_('Early Leave Minutes'), default=0)

    # Status
    status = models.CharField(_('Status'), max_length=20, choices=ATTENDANCE_STATUS, default='absent')
    is_manual_entry = models.BooleanField(_('Manual Entry'), default=False)
    manual_entry_reason = models.TextField(_('Manual Entry Reason'), blank=True)

    # Approval
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_attendance')
    approved_at = models.DateTimeField(_('Approved At'), blank=True, null=True)

    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Attendance Record')
        verbose_name_plural = _('Attendance Records')
        ordering = ['-date', '-clock_in', 'employee']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    def calculate_hours(self):
        """Calculate total hours, overtime, and late/early minutes"""
        if self.clock_in and self.clock_out:
            # Calculate total hours
            duration = self.clock_out - self.clock_in
            self.total_hours = duration.total_seconds() / 3600

            # Calculate late minutes
            if self.schedule:
                day_schedule = self.schedule.get_day_schedule(self.date.weekday())
                if day_schedule[0]:  # Has start time
                    scheduled_start = datetime.combine(self.date, day_schedule[0])
                    # Make scheduled_start timezone-aware if clock_in is timezone-aware
                    if timezone.is_aware(self.clock_in) and timezone.is_naive(scheduled_start):
                        scheduled_start = timezone.make_aware(scheduled_start)

                    if self.clock_in > scheduled_start + timedelta(minutes=self.schedule.late_grace_period):
                        self.late_minutes = int((self.clock_in - scheduled_start).total_seconds() / 60)
                        self.status = 'late'

                # Calculate early leave
                if day_schedule[1]:  # Has end time
                    scheduled_end = datetime.combine(self.date, day_schedule[1])
                    # Make scheduled_end timezone-aware if clock_out is timezone-aware
                    if timezone.is_aware(self.clock_out) and timezone.is_naive(scheduled_end):
                        scheduled_end = timezone.make_aware(scheduled_end)

                    if self.clock_out < scheduled_end - timedelta(minutes=self.schedule.early_leave_grace_period):
                        self.early_leave_minutes = int((scheduled_end - self.clock_out).total_seconds() / 60)
                        if self.status != 'late':
                            self.status = 'early_leave'

                # Calculate overtime
                if self.total_hours > float(self.schedule.required_hours_per_day):
                    self.overtime_hours = self.total_hours - float(self.schedule.required_hours_per_day)

            # Set status as present if not already set
            if self.status == 'absent':
                self.status = 'present'

    def save(self, *args, **kwargs):
        self.calculate_hours()
        super().save(*args, **kwargs)

    # ========== PROJECT INTEGRATION METHODS ==========

    def get_timecard_entries(self):
        """Get all timecard entries for this attendance date"""
        from hr.timecard_models import TimecardEntry
        return TimecardEntry.objects.filter(
            timecard__employee=self.employee,
            date=self.date
        )

    def get_project_hours_breakdown(self):
        """Get breakdown of hours by project for this attendance day"""
        timecard_entries = self.get_timecard_entries()
        project_hours = {}

        for entry in timecard_entries:
            project_name = entry.get_project_display()
            if project_name not in project_hours:
                project_hours[project_name] = {
                    'hours': 0,
                    'billable_hours': 0,
                    'project': entry.project,
                    'entries': []
                }
            project_hours[project_name]['hours'] += float(entry.hours)
            if entry.is_billable:
                project_hours[project_name]['billable_hours'] += float(entry.hours)
            project_hours[project_name]['entries'].append(entry)

        return project_hours

    def get_primary_project(self):
        """Get the project with most hours logged for this day"""
        project_hours = self.get_project_hours_breakdown()
        if not project_hours:
            return self.current_project

        primary_project = max(project_hours.items(), key=lambda x: x[1]['hours'])
        return primary_project[1]['project'] if primary_project[1]['project'] else self.current_project

    def sync_with_timecard(self):
        """Sync attendance record with timecard data"""
        timecard_entries = self.get_timecard_entries()
        if timecard_entries.exists():
            # Update current project if not set
            if not self.current_project:
                self.current_project = self.get_primary_project()

            # Update total hours if timecard has more accurate data
            timecard_total = sum(float(entry.hours) for entry in timecard_entries)
            if timecard_total > 0 and abs(float(self.total_hours) - timecard_total) > 0.5:
                self.total_hours = timecard_total
                self.save(update_fields=['current_project', 'total_hours'])

    def get_attendance_summary(self):
        """Get comprehensive attendance summary including project data"""
        project_hours = self.get_project_hours_breakdown()

        return {
            'employee': self.employee,
            'date': self.date,
            'status': self.status,
            'clock_in': self.clock_in,
            'clock_out': self.clock_out,
            'total_hours': self.total_hours,
            'current_project': self.current_project,
            'location': self.location,
            'is_remote_work': self.is_remote_work,
            'project_breakdown': project_hours,
            'overtime_hours': self.overtime_hours,
            'late_minutes': self.late_minutes,
            'early_leave_minutes': self.early_leave_minutes,
        }

    def can_work_on_project(self, project):
        """Check if employee can work on the specified project"""
        if not project:
            return True

        # Check if employee is a team member of the project
        from project.models import ProjectTeamMember
        is_team_member = ProjectTeamMember.objects.filter(
            project=project,
            employee=self.employee,
            is_active=True
        ).exists()

        return is_team_member or project.project_manager == self.employee or project.team_lead == self.employee

    @property
    def has_project_time_logged(self):
        """Check if any time has been logged for projects today"""
        return self.get_timecard_entries().exists()

    @property
    def project_utilization_rate(self):
        """Calculate utilization rate (project hours / total attendance hours)"""
        if self.total_hours == 0:
            return 0

        project_hours = sum(
            breakdown['hours'] for breakdown in self.get_project_hours_breakdown().values()
        )
        return (project_hours / float(self.total_hours)) * 100


class BreakRecord(models.Model):
    """Track employee breaks"""
    BREAK_TYPES = [
        ('lunch', _('Lunch Break')),
        ('tea', _('Tea Break')),
        ('personal', _('Personal Break')),
        ('prayer', _('Prayer Break')),
        ('other', _('Other')),
    ]

    attendance = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE, related_name='breaks')
    break_type = models.CharField(_('Break Type'), max_length=20, choices=BREAK_TYPES, default='lunch')
    start_time = models.DateTimeField(_('Start Time'))
    end_time = models.DateTimeField(_('End Time'), blank=True, null=True)
    duration_minutes = models.IntegerField(_('Duration (minutes)'), default=0)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Break Record')
        verbose_name_plural = _('Break Records')
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.attendance.employee.full_name} - {self.break_type} - {self.start_time}"

    def calculate_duration(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            self.duration_minutes = int(duration.total_seconds() / 60)

    def save(self, *args, **kwargs):
        self.calculate_duration()
        super().save(*args, **kwargs)


class OvertimeRequest(models.Model):
    """Manage overtime requests"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtime_requests')
    project = models.ForeignKey('project.Project', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='overtime_requests', verbose_name=_('Project'))
    date = models.DateField(_('Date'))
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'))
    hours = models.DecimalField(_('Hours'), max_digits=4, decimal_places=2)
    reason = models.TextField(_('Reason'))

    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    requested_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, related_name='overtime_requested_by')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='overtime_approved_by')
    approved_at = models.DateTimeField(_('Approved At'), blank=True, null=True)
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)

    # Rate calculation
    overtime_rate = models.DecimalField(_('Overtime Rate'), max_digits=5, decimal_places=2, default=1.5)
    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2, blank=True, null=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Overtime Request')
        verbose_name_plural = _('Overtime Requests')
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.hours}hrs"


class AttendanceCorrection(models.Model):
    """Handle attendance correction requests"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
    ]

    attendance = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE, related_name='corrections')
    requested_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='correction_requests')

    # Correction details
    correction_type = models.CharField(_('Correction Type'), max_length=50, choices=[
        ('clock_in', _('Clock In Time')),
        ('clock_out', _('Clock Out Time')),
        ('both', _('Both Clock In and Out')),
        ('status', _('Attendance Status')),
    ])

    new_clock_in = models.DateTimeField(_('New Clock In'), blank=True, null=True)
    new_clock_out = models.DateTimeField(_('New Clock Out'), blank=True, null=True)
    new_status = models.CharField(_('New Status'), max_length=20, blank=True, choices=AttendanceRecord.ATTENDANCE_STATUS)

    reason = models.TextField(_('Reason for Correction'))
    supporting_document = models.FileField(_('Supporting Document'), upload_to='attendance/corrections/', blank=True, null=True)

    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_corrections')
    approved_at = models.DateTimeField(_('Approved At'), blank=True, null=True)
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Attendance Correction')
        verbose_name_plural = _('Attendance Corrections')
        ordering = ['-created_at']

    def __str__(self):
        return f"Correction for {self.attendance} by {self.requested_by}"


class ProjectAttendance(models.Model):
    """
    Track employee attendance for specific projects
    Links attendance records with project assignments
    """
    attendance = models.ForeignKey(
        AttendanceRecord,
        on_delete=models.CASCADE,
        related_name='project_assignments'
    )
    project = models.ForeignKey(
        'project.Project',
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )

    # Time allocation for this project on this day
    allocated_hours = models.DecimalField(
        _('Allocated Hours'),
        max_digits=4,
        decimal_places=2,
        default=0,
        help_text=_('Planned hours to work on this project')
    )
    actual_hours = models.DecimalField(
        _('Actual Hours'),
        max_digits=4,
        decimal_places=2,
        default=0,
        help_text=_('Actual hours worked on this project (from timecard)')
    )

    # Work location and setup
    work_location = models.CharField(
        _('Work Location'),
        max_length=200,
        blank=True,
        help_text=_('Specific location for this project work')
    )
    is_primary_project = models.BooleanField(
        _('Primary Project'),
        default=False,
        help_text=_('Main project for this attendance day')
    )

    # Status and notes
    status = models.CharField(
        _('Project Work Status'),
        max_length=20,
        choices=[
            ('planned', _('Planned')),
            ('in_progress', _('In Progress')),
            ('completed', _('Completed')),
            ('on_hold', _('On Hold')),
            ('cancelled', _('Cancelled')),
        ],
        default='planned'
    )
    notes = models.TextField(_('Notes'), blank=True)

    # Approval for project work
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_project_attendance',
        verbose_name=_('Approved By')
    )
    approved_at = models.DateTimeField(_('Approved At'), blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Project Attendance')
        verbose_name_plural = _('Project Attendance')
        unique_together = [['attendance', 'project']]
        ordering = ['-attendance__date', 'project__project_name']

    def __str__(self):
        return f"{self.attendance.employee.full_name} - {self.project.project_name} - {self.attendance.date}"

    def save(self, *args, **kwargs):
        # Update actual hours from timecard entries
        self.sync_actual_hours()
        super().save(*args, **kwargs)

    def sync_actual_hours(self):
        """Sync actual hours from timecard entries"""
        timecard_entries = self.attendance.get_timecard_entries().filter(project=self.project)
        self.actual_hours = sum(float(entry.hours) for entry in timecard_entries)

    @property
    def hours_variance(self):
        """Calculate variance between allocated and actual hours"""
        return self.actual_hours - self.allocated_hours

    @property
    def utilization_rate(self):
        """Calculate utilization rate for this project assignment"""
        if self.allocated_hours == 0:
            return 0
        return (self.actual_hours / self.allocated_hours) * 100

    def get_timecard_entries(self):
        """Get timecard entries for this project on this attendance day"""
        return self.attendance.get_timecard_entries().filter(project=self.project)


class AttendancePolicy(models.Model):
    """Define attendance policies"""
    name = models.CharField(_('Policy Name'), max_length=100)
    code = models.CharField(_('Policy Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)

    # Late policy
    late_deduction_per_minute = models.DecimalField(_('Late Deduction Per Minute'), max_digits=6, decimal_places=2, default=0)
    max_late_minutes_per_month = models.IntegerField(_('Max Late Minutes Per Month'), default=120)
    late_penalty_amount = models.DecimalField(_('Late Penalty Amount'), max_digits=8, decimal_places=2, default=0)

    # Absence policy
    absence_deduction_per_day = models.DecimalField(_('Absence Deduction Per Day'), max_digits=8, decimal_places=2, default=0)
    max_absences_per_month = models.IntegerField(_('Max Absences Per Month'), default=3)

    # Overtime policy
    overtime_rate_regular = models.DecimalField(_('Regular Overtime Rate'), max_digits=3, decimal_places=2, default=1.5)
    overtime_rate_holiday = models.DecimalField(_('Holiday Overtime Rate'), max_digits=3, decimal_places=2, default=2.0)
    min_overtime_minutes = models.IntegerField(_('Minimum Overtime Minutes'), default=30)

    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Attendance Policy')
        verbose_name_plural = _('Attendance Policies')
        ordering = ['name']

    def __str__(self):
        return self.name
