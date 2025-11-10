
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

User = get_user_model()


class ProjectType(models.Model):
    id = models.BigAutoField(primary_key=True)
    type_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_types'
        ordering = ['type_name']

    def __str__(self):
        return self.type_name


class ProjectTemplate(models.Model):
    id = models.BigAutoField(primary_key=True)
    template_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    project_type = models.ForeignKey(ProjectType, on_delete=models.SET_NULL, null=True, blank=True)
    default_tasks = models.JSONField(default=dict, blank=True)
    estimated_duration_days = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_templates'
        ordering = ['template_name']

    def __str__(self):
        return self.template_name


class Project(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('overdue', 'Overdue'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    BILLING_METHOD_CHOICES = [
        ('fixed_cost', 'Fixed Cost'),
        ('time_and_material', 'Time and Material'),
        ('milestone_based', 'Milestone Based'),
    ]

    id = models.BigAutoField(primary_key=True)
    project_code = models.CharField(max_length=50, unique=True)
    project_name = models.CharField(max_length=200, db_column='name')  # DB column is 'name'
    description = models.TextField(blank=True, null=True)

    # Construction-specific fields
    location = models.CharField(max_length=300, blank=True, null=True)
    site_address = models.TextField(blank=True, null=True)
    client_name = models.CharField(max_length=200, blank=True, null=True)
    client_contact = models.CharField(max_length=100, blank=True, null=True)
    client_phone = models.CharField(max_length=20, blank=True, null=True)

    # Project Manager
    project_manager = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='managed_projects', db_column='project_manager_id')

    # Dates
    expected_start_date = models.DateField(null=True, blank=True, db_column='start_date')
    expected_end_date = models.DateField(null=True, blank=True, db_column='end_date')
    actual_end_date = models.DateField(null=True, blank=True, db_column='actual_completion_date')

    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    percent_complete = models.IntegerField(default=0, db_column='progress_percentage',
                                          validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Budget and Billing
    estimated_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0, db_column='budget')
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    estimated_duration_days = models.IntegerField(null=True, blank=True)

    # Additional Info
    notes = models.TextField(blank=True, null=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_project'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.project_code} - {self.project_name}"

    def save(self, *args, **kwargs):
        if not self.project_code:
            self.project_code = self.generate_project_code()
        super().save(*args, **kwargs)

    def generate_project_code(self):
        from datetime import datetime
        year = datetime.now().year
        count = Project.objects.filter(created_at__year=year).count() + 1
        return f"PRJ-{year}-{count:04d}"

    # ========== TIMESHEET INTEGRATION METHODS ==========

    def get_total_timesheet_hours(self):
        """Get total hours from all timesheets for this project"""
        from decimal import Decimal
        from django.db import connection
        from django.db.utils import ProgrammingError, OperationalError

        # Get hours from timesheet details
        try:
            # Import here to avoid circular imports and table existence issues
            timesheet_hours = TimesheetDetail.objects.filter(
                project=self
            ).aggregate(total=models.Sum('hours'))['total'] or Decimal('0')
        except (ProgrammingError, OperationalError):
            # Table doesn't exist yet (during migrations)
            timesheet_hours = Decimal('0')

        # Get hours from timecard entries
        try:
            timecard_hours = self.timecard_entries.aggregate(
                total=models.Sum('hours')
            )['total'] or Decimal('0')
        except (ProgrammingError, OperationalError):
            timecard_hours = Decimal('0')

        return timesheet_hours + timecard_hours

    def get_total_billable_hours(self):
        """Get total billable hours from all timesheets for this project"""
        from decimal import Decimal
        from django.db.utils import ProgrammingError, OperationalError

        # Get billable hours from timesheet details
        try:
            timesheet_billable = TimesheetDetail.objects.filter(
                project=self,
                is_billable=True
            ).aggregate(total=models.Sum('hours'))['total'] or Decimal('0')
        except (ProgrammingError, OperationalError):
            timesheet_billable = Decimal('0')

        # Get billable hours from timecard entries
        try:
            timecard_billable = self.timecard_entries.filter(
                is_billable=True
            ).aggregate(total=models.Sum('hours'))['total'] or Decimal('0')
        except (ProgrammingError, OperationalError):
            timecard_billable = Decimal('0')

        return timesheet_billable + timecard_billable

    def get_total_billable_amount(self):
        """Get total billable amount from all timesheets for this project"""
        from decimal import Decimal
        from django.db.utils import ProgrammingError, OperationalError

        try:
            return TimesheetDetail.objects.filter(
                project=self
            ).aggregate(total=models.Sum('billing_amount'))['total'] or Decimal('0')
        except (ProgrammingError, OperationalError):
            return Decimal('0')

    def get_project_timesheets(self):
        """Get all timesheets associated with this project"""
        from django.db.utils import ProgrammingError, OperationalError

        try:
            return Timesheet.objects.filter(
                details__project=self
            ).distinct()
        except (ProgrammingError, OperationalError):
            return Timesheet.objects.none()

    def get_project_employees_with_time(self):
        """Get all employees who have logged time on this project"""
        from hr.models import Employee
        from django.db.utils import ProgrammingError, OperationalError

        try:
            # Get employees from timesheets
            timesheet_employees = Employee.objects.filter(
                timesheets__details__project=self
            ).distinct()
        except (ProgrammingError, OperationalError):
            timesheet_employees = Employee.objects.none()

        try:
            # Get employees from timecard entries
            timecard_employees = Employee.objects.filter(
                timecards__entries__project=self
            ).distinct()
        except (ProgrammingError, OperationalError):
            timecard_employees = Employee.objects.none()

        # Combine both querysets
        all_employees = (timesheet_employees | timecard_employees).distinct()
        return all_employees

    def get_time_tracking_summary(self):
        """Get comprehensive time tracking summary for this project"""
        from decimal import Decimal
        from django.db.utils import ProgrammingError, OperationalError

        try:
            # Get or create time tracking record
            time_tracking, created = ProjectTimeTracking.objects.get_or_create(
                project=self,
                defaults={'total_estimated_hours': self.estimated_hours or 0}
            )

            if created or not time_tracking.last_calculated_at:
                time_tracking.recalculate_totals()
                time_tracking.refresh_from_db()

            return {
                'estimated_hours': time_tracking.total_estimated_hours,
                'actual_hours': time_tracking.total_actual_hours,
                'billable_hours': time_tracking.total_billable_hours,
                'billed_hours': time_tracking.total_billed_hours,
                'billable_amount': time_tracking.total_billable_amount,
                'billed_amount': time_tracking.total_billed_amount,
                'costing_amount': time_tracking.total_costing_amount,
                'efficiency_rate': time_tracking.efficiency_rate,
                'utilization_rate': time_tracking.utilization_rate,
                'hours_variance': time_tracking.hours_variance,
                'is_over_budget': time_tracking.is_over_budget_hours,
                'first_timesheet_date': time_tracking.first_timesheet_date,
                'last_timesheet_date': time_tracking.last_timesheet_date,
                'last_calculated_at': time_tracking.last_calculated_at,
            }
        except (ProgrammingError, OperationalError):
            # Return empty summary if tables don't exist
            return {
                'estimated_hours': Decimal('0'),
                'actual_hours': Decimal('0'),
                'billable_hours': Decimal('0'),
                'billed_hours': Decimal('0'),
                'billable_amount': Decimal('0'),
                'billed_amount': Decimal('0'),
                'costing_amount': Decimal('0'),
                'efficiency_rate': Decimal('0'),
                'utilization_rate': Decimal('0'),
                'hours_variance': Decimal('0'),
                'is_over_budget': False,
                'first_timesheet_date': None,
                'last_timesheet_date': None,
                'last_calculated_at': None,
            }

    def get_monthly_time_breakdown(self, year=None, month=None):
        """Get time breakdown for a specific month"""
        from django.utils import timezone
        from django.db.models import Sum
        from django.db.utils import ProgrammingError, OperationalError
        import calendar

        if not year:
            year = timezone.now().year
        if not month:
            month = timezone.now().month

        # Get start and end dates for the month
        start_date = timezone.datetime(year, month, 1).date()
        _, last_day = calendar.monthrange(year, month)
        end_date = timezone.datetime(year, month, last_day).date()

        # Get timesheet details for the month
        try:
            timesheet_data = TimesheetDetail.objects.filter(
                project=self,
                activity_date__gte=start_date,
                activity_date__lte=end_date
            ).aggregate(
                total_hours=Sum('hours'),
                billable_hours=Sum('hours', filter=models.Q(is_billable=True)),
                billable_amount=Sum('billing_amount')
            )
        except (ProgrammingError, OperationalError):
            timesheet_data = {'total_hours': 0, 'billable_hours': 0, 'billable_amount': 0}

        # Get timecard entries for the month
        try:
            timecard_data = self.timecard_entries.filter(
                date__gte=start_date,
                date__lte=end_date
            ).aggregate(
                total_hours=Sum('hours'),
                billable_hours=Sum('hours', filter=models.Q(is_billable=True))
            )
        except (ProgrammingError, OperationalError):
            timecard_data = {'total_hours': 0, 'billable_hours': 0}

        return {
            'year': year,
            'month': month,
            'total_hours': (timesheet_data['total_hours'] or 0) + (timecard_data['total_hours'] or 0),
            'billable_hours': (timesheet_data['billable_hours'] or 0) + (timecard_data['billable_hours'] or 0),
            'billable_amount': timesheet_data['billable_amount'] or 0
        }

    def update_project_time_tracking(self):
        """Update project time tracking totals"""
        from django.db.utils import ProgrammingError, OperationalError

        try:
            time_tracking, created = ProjectTimeTracking.objects.get_or_create(
                project=self,
                defaults={'total_estimated_hours': self.estimated_hours or 0}
            )
            time_tracking.recalculate_totals()
            return time_tracking
        except (ProgrammingError, OperationalError):
            return None

    # ========== ATTENDANCE INTEGRATION METHODS ==========

    def get_daily_attendance(self, date=None):
        """Get attendance records for this project on a specific date"""
        from django.utils import timezone
        if not date:
            date = timezone.now().date()

        return self.attendance_records.filter(attendance__date=date)

    def get_present_employees_today(self):
        """Get employees present and working on this project today"""
        from django.utils import timezone
        from attendance.models import AttendanceRecord

        today = timezone.now().date()

        # Get attendance records for today where current_project is this project
        attendance_records = AttendanceRecord.objects.filter(
            current_project=self,
            date=today,
            status__in=['present', 'late', 'early_leave']
        ).select_related('employee')

        # Also get employees with timecard entries for this project today
        from hr.timecard_models import TimecardEntry
        timecard_employees = TimecardEntry.objects.filter(
            project=self,
            date=today,
            timecard__employee__attendance_records__date=today,
            timecard__employee__attendance_records__status__in=['present', 'late', 'early_leave']
        ).values_list('timecard__employee', flat=True).distinct()

        # Combine both sets
        present_employee_ids = set(attendance_records.values_list('employee_id', flat=True))
        present_employee_ids.update(timecard_employees)

        from hr.models import Employee
        return Employee.objects.filter(id__in=present_employee_ids)

    def get_project_attendance_summary(self, date=None):
        """Get comprehensive attendance summary for this project"""
        from django.utils import timezone
        if not date:
            date = timezone.now().date()

        # Get project team members
        team_members = self.team_members.filter(is_active=True)

        # Get attendance data for team members
        attendance_data = []
        for member in team_members:
            from attendance.models import AttendanceRecord
            attendance = AttendanceRecord.objects.filter(
                employee=member.employee,
                date=date
            ).first()

            if attendance:
                project_assignment = attendance.project_assignments.filter(project=self).first()
                attendance_data.append({
                    'employee': member.employee,
                    'attendance': attendance,
                    'project_assignment': project_assignment,
                    'timecard_hours': sum(
                        float(entry.hours) for entry in attendance.get_timecard_entries().filter(project=self)
                    ),
                    'is_working_on_project': attendance.current_project == self or
                                          attendance.get_timecard_entries().filter(project=self).exists()
                })

        return attendance_data

    def get_remote_workers_today(self):
        """Get employees working remotely on this project today"""
        from django.utils import timezone
        from attendance.models import AttendanceRecord

        today = timezone.now().date()
        return AttendanceRecord.objects.filter(
            current_project=self,
            date=today,
            is_remote_work=True,
            status__in=['present', 'late', 'early_leave']
        ).select_related('employee')

    def get_project_location_breakdown(self, date=None):
        """Get breakdown of workers by location for this project"""
        from django.utils import timezone
        from django.db.models import Count

        if not date:
            date = timezone.now().date()

        return self.attendance_records.filter(
            attendance__date=date
        ).values('work_location').annotate(
            worker_count=Count('attendance__employee')
        ).order_by('-worker_count')

    def get_project_productivity_metrics(self, date=None):
        """Get productivity metrics for the project on a specific date"""
        from django.utils import timezone

        if not date:
            date = timezone.now().date()

        project_assignments = self.attendance_records.filter(attendance__date=date)

        total_allocated = sum(float(pa.allocated_hours) for pa in project_assignments)
        total_actual = sum(float(pa.actual_hours) for pa in project_assignments)

        return {
            'date': date,
            'total_allocated_hours': total_allocated,
            'total_actual_hours': total_actual,
            'utilization_rate': (total_actual / total_allocated * 100) if total_allocated > 0 else 0,
            'hours_variance': total_actual - total_allocated,
            'worker_count': project_assignments.count(),
            'productivity_score': (total_actual / total_allocated * 100) if total_allocated > 0 else 100
        }

    @property
    def time_tracking_available(self):
        """Check if time tracking is available for this project"""
        return hasattr(self, 'time_tracking')

    @property
    def total_logged_hours(self):
        """Quick access to total logged hours"""
        return self.get_total_timesheet_hours()

    @property
    def total_billable_logged_hours(self):
        """Quick access to total billable hours"""
        return self.get_total_billable_hours()

    @property
    def current_active_workers(self):
        """Get count of workers currently active on this project"""
        return self.get_present_employees_today().count()


class ProjectTeamMember(models.Model):
    PAY_TYPE_CHOICES = [
        ('Normal', 'Normal'),
        ('PH', 'Public Holiday'),
        ('OT', 'Overtime'),
        ('Weekend', 'Weekend'),
    ]

    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='team_members')
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='project_memberships', db_column='worker_id')
    pay_type = models.CharField(max_length=50, choices=PAY_TYPE_CHOICES, default='Normal', blank=True, null=True)
    daily_rate_usd = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Daily rate in USD")
    multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.0, null=True, blank=True, help_text="Pay multiplier (e.g., 1.0, 1.5, 2.0)")

    # Legacy fields (keeping for backward compatibility)
    role = models.CharField(max_length=100, blank=True, null=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, db_column='daily_rate')
    ot_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Overtime rate per day")

    start_date = models.DateField(null=True, blank=True, db_column='assigned_date')
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_projectteam'
        unique_together = ['project', 'employee']

    def __str__(self):
        return f"{self.employee} - {self.project.project_name}"


class ProjectTask(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('working', 'Working'),
        ('pending_review', 'Pending Review'),
        ('overdue', 'Overdue'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.BigAutoField(primary_key=True)
    task_code = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    task_name = models.CharField(max_length=200, db_column='title')  # DB column is 'title'
    description = models.TextField(blank=True, null=True)

    # Assignment
    assigned_to = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='assigned_tasks')

    # Dates
    expected_start_date = models.DateField(null=True, blank=True, db_column='start_date')
    expected_end_date = models.DateField(null=True, blank=True, db_column='due_date')
    actual_end_date = models.DateField(null=True, blank=True, db_column='completion_date')

    # Status and Priority
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    progress = models.IntegerField(default=0, db_column='progress_percentage',
                                  validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Time Tracking
    estimated_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    actual_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Additional Info
    notes = models.TextField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_projecttask'
        ordering = ['expected_start_date', 'task_name']

    def __str__(self):
        return f"{self.task_code} - {self.task_name}"

    def save(self, *args, **kwargs):
        if not self.task_code:
            self.task_code = self.generate_task_code()
        super().save(*args, **kwargs)

    def generate_task_code(self):
        count = ProjectTask.objects.filter(project=self.project).count() + 1
        return f"{self.project.project_code}-T{count:03d}"


class TaskDependency(models.Model):
    id = models.BigAutoField(primary_key=True)
    task = models.ForeignKey(ProjectTask, on_delete=models.CASCADE, related_name='dependencies')
    depends_on_task = models.ForeignKey(ProjectTask, on_delete=models.CASCADE, related_name='dependent_tasks')
    lag_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'task_dependencies'
        unique_together = ['task', 'depends_on_task']

    def __str__(self):
        return f"{self.task.task_name} depends on {self.depends_on_task.task_name}"


class ProjectMilestone(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
    ]

    MILESTONE_TYPE_CHOICES = [
        ('deliverable', 'Deliverable'),
        ('payment', 'Payment'),
        ('review', 'Review'),
        ('approval', 'Approval'),
        ('launch', 'Launch'),
        ('testing', 'Testing'),
        ('other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='milestones')
    milestone_name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    milestone_type = models.CharField(max_length=20, choices=MILESTONE_TYPE_CHOICES, default='deliverable')
    milestone_date = models.DateField()
    task = models.ForeignKey(ProjectTask, on_delete=models.SET_NULL, null=True, blank=True,
                            help_text="Optional: Link milestone to a specific task")

    # Financial tracking
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                help_text="Payment amount or budget allocation")
    is_billable = models.BooleanField(default=False, help_text="Is this milestone billable to client?")

    # Status and completion
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    completion_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              validators=[MinValueValidator(0), MaxValueValidator(100)])
    completed_date = models.DateField(null=True, blank=True)
    completed_by = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='completed_milestones')

    # Dependencies
    depends_on_milestones = models.ManyToManyField('self', blank=True, symmetrical=False,
                                                  related_name='dependent_milestones')

    # Approval workflow
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_milestones')
    approved_date = models.DateTimeField(null=True, blank=True)

    # Additional tracking
    deliverables = models.TextField(blank=True, null=True, help_text="List of deliverables for this milestone")
    acceptance_criteria = models.TextField(blank=True, null=True, help_text="Criteria for milestone completion")

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_milestones')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_milestones'
        ordering = ['milestone_date']
        verbose_name = 'Project Milestone'
        verbose_name_plural = 'Project Milestones'

    def __str__(self):
        return f"{self.project.project_name} - {self.milestone_name}"

    def save(self, *args, **kwargs):
        # Auto-update status based on completion and dates
        if self.completion_percentage == 100 and self.status != 'completed':
            self.status = 'completed'
            if not self.completed_date:
                self.completed_date = timezone.now().date()
        elif self.milestone_date < timezone.now().date() and self.status == 'pending':
            self.status = 'overdue'

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        """Check if milestone is overdue"""
        return (self.milestone_date < timezone.now().date() and
                self.status not in ['completed', 'cancelled'])

    @property
    def days_until_due(self):
        """Calculate days until milestone is due"""
        today = timezone.now().date()
        return (self.milestone_date - today).days

    @property
    def is_critical(self):
        """Check if milestone is critical (due within 7 days or overdue)"""
        return self.days_until_due <= 7

    @property
    def progress_color(self):
        """Get color for progress display"""
        if self.status == 'completed':
            return 'success'
        elif self.status == 'overdue':
            return 'danger'
        elif self.is_critical:
            return 'warning'
        else:
            return 'primary'

    def can_be_completed(self):
        """Check if milestone can be marked as completed based on dependencies"""
        incomplete_dependencies = self.depends_on_milestones.exclude(status='completed')
        return not incomplete_dependencies.exists()

    def get_blocking_dependencies(self):
        """Get list of incomplete dependencies"""
        return self.depends_on_milestones.exclude(status='completed')


class ProjectTimeTracking(models.Model):
    """
    Aggregate time tracking per project (ERPNext-style)
    Maintains running totals for project time and billing
    """
    id = models.BigAutoField(primary_key=True)
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='time_tracking',
        verbose_name='Project'
    )

    # Time tracking totals
    total_estimated_hours = models.DecimalField(
        'Total Estimated Hours',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Total estimated hours for the project'
    )
    total_actual_hours = models.DecimalField(
        'Total Actual Hours',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Total hours logged across all timesheets'
    )
    total_billable_hours = models.DecimalField(
        'Total Billable Hours',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Total billable hours across all timesheets'
    )
    total_billed_hours = models.DecimalField(
        'Total Billed Hours',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Total hours that have been billed to client'
    )

    # Financial tracking
    total_billable_amount = models.DecimalField(
        'Total Billable Amount',
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Total billable amount across all timesheets'
    )
    total_billed_amount = models.DecimalField(
        'Total Billed Amount',
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Total amount that has been billed to client'
    )
    total_costing_amount = models.DecimalField(
        'Total Costing Amount',
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Total internal costing amount'
    )

    # Performance metrics
    efficiency_rate = models.DecimalField(
        'Efficiency Rate (%)',
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Billable hours / Total hours * 100'
    )
    utilization_rate = models.DecimalField(
        'Utilization Rate (%)',
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Actual hours / Estimated hours * 100'
    )

    # Date tracking
    first_timesheet_date = models.DateField(
        'First Timesheet Date',
        null=True,
        blank=True,
        help_text='Date of first time entry'
    )
    last_timesheet_date = models.DateField(
        'Last Timesheet Date',
        null=True,
        blank=True,
        help_text='Date of most recent time entry'
    )

    # Metadata
    last_calculated_at = models.DateTimeField(
        'Last Calculated At',
        null=True,
        blank=True,
        help_text='When totals were last recalculated'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_time_tracking'
        verbose_name = 'Project Time Tracking'
        verbose_name_plural = 'Project Time Tracking'

    def __str__(self):
        return f"{self.project.project_name} - Time Tracking"

    def recalculate_totals(self):
        """Recalculate all time tracking totals from timesheets and timecard entries"""
        from decimal import Decimal
        from django.utils import timezone
        from django.db.utils import ProgrammingError, OperationalError

        # Calculate from timesheet details
        try:
            timesheet_totals = TimesheetDetail.objects.filter(
                project=self.project
            ).aggregate(
                total_hours=models.Sum('hours'),
                billable_hours=models.Sum('hours', filter=models.Q(is_billable=True)),
                billable_amount=models.Sum('billing_amount'),
                costing_amount=models.Sum('costing_amount')
            )
        except (ProgrammingError, OperationalError):
            timesheet_totals = {'total_hours': None, 'billable_hours': None, 'billable_amount': None, 'costing_amount': None}

        # Calculate from timecard entries
        try:
            timecard_totals = self.project.timecard_entries.aggregate(
                total_hours=models.Sum('hours'),
                billable_hours=models.Sum('hours', filter=models.Q(is_billable=True))
            )
        except (ProgrammingError, OperationalError):
            timecard_totals = {'total_hours': None, 'billable_hours': None}

        # Combine totals
        self.total_actual_hours = (
            (timesheet_totals['total_hours'] or Decimal('0')) +
            (timecard_totals['total_hours'] or Decimal('0'))
        )
        self.total_billable_hours = (
            (timesheet_totals['billable_hours'] or Decimal('0')) +
            (timecard_totals['billable_hours'] or Decimal('0'))
        )
        self.total_billable_amount = timesheet_totals['billable_amount'] or Decimal('0')
        self.total_costing_amount = timesheet_totals['costing_amount'] or Decimal('0')

        # Calculate performance metrics
        if self.total_actual_hours > 0:
            self.efficiency_rate = (self.total_billable_hours / self.total_actual_hours) * 100
        else:
            self.efficiency_rate = 0

        if self.total_estimated_hours > 0:
            self.utilization_rate = (self.total_actual_hours / self.total_estimated_hours) * 100
        else:
            self.utilization_rate = 0

        # Update date ranges
        try:
            if self.project.timecard_entries.exists():
                timecard_dates = self.project.timecard_entries.aggregate(
                    first_date=models.Min('date'),
                    last_date=models.Max('date')
                )
                self.first_timesheet_date = timecard_dates['first_date']
                self.last_timesheet_date = timecard_dates['last_date']
        except (ProgrammingError, OperationalError):
            pass

        # Update timesheet detail dates if available
        try:
            if TimesheetDetail.objects.filter(project=self.project).exists():
                detail_dates = TimesheetDetail.objects.filter(project=self.project).aggregate(
                    first_date=models.Min('activity_date'),
                    last_date=models.Max('activity_date')
                )
                if not self.first_timesheet_date or detail_dates['first_date'] < self.first_timesheet_date:
                    self.first_timesheet_date = detail_dates['first_date']
                if not self.last_timesheet_date or detail_dates['last_date'] > self.last_timesheet_date:
                    self.last_timesheet_date = detail_dates['last_date']
        except (ProgrammingError, OperationalError):
            pass

        self.last_calculated_at = timezone.now()
        self.save()

    @property
    def hours_variance(self):
        """Calculate variance between estimated and actual hours"""
        return self.total_actual_hours - self.total_estimated_hours

    @property
    def unbilled_hours(self):
        """Calculate unbilled billable hours"""
        return self.total_billable_hours - self.total_billed_hours

    @property
    def unbilled_amount(self):
        """Calculate unbilled amount"""
        return self.total_billable_amount - self.total_billed_amount

    @property
    def is_over_budget_hours(self):
        """Check if project is over estimated hours"""
        return self.total_actual_hours > self.total_estimated_hours

    @property
    def budget_variance_percentage(self):
        """Calculate budget variance as percentage"""
        if self.total_estimated_hours > 0:
            return ((self.total_actual_hours - self.total_estimated_hours) / self.total_estimated_hours) * 100
        return 0


class ActivityTypeMaster(models.Model):
    ACTIVITY_TYPE_CHOICES = [
        ('planning', 'Planning'),
        ('execution', 'Execution'),
        ('testing', 'Testing'),
        ('documentation', 'Documentation'),
        ('meeting', 'Meeting'),
        ('communication', 'Communication'),
        ('research', 'Research'),
        ('review', 'Review'),
        ('other', 'Other'),
    ]

    id = models.BigAutoField(primary_key=True)
    activity_name = models.CharField(max_length=100, unique=True)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES, null=True, blank=True)
    billing_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costing_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_billable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'activity_types_master'
        ordering = ['activity_name']

    def __str__(self):
        return self.activity_name


class Timesheet(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    id = models.BigAutoField(primary_key=True)
    timesheet_code = models.CharField(max_length=50, unique=True)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='timesheets')
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    total_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_billable_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_billed_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_billable_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_costing_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    per_hour_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    submitted_date = models.DateTimeField(null=True, blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_timesheets')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_timesheets')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timesheets'
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.timesheet_code} - {self.employee}"

    def save(self, *args, **kwargs):
        if not self.timesheet_code:
            self.timesheet_code = self.generate_timesheet_code()
        super().save(*args, **kwargs)

    def generate_timesheet_code(self):
        from datetime import datetime
        month_year = self.start_date.strftime('%Y%m')
        count = Timesheet.objects.filter(
            created_at__year=self.start_date.year,
            created_at__month=self.start_date.month
        ).count() + 1
        return f"TS-{month_year}-{count:04d}"

    def calculate_totals(self):
        """Calculate and update timesheet totals from details and timecard entries"""
        from decimal import Decimal

        # Calculate from timesheet details
        details_total = self.details.aggregate(
            total_hours=models.Sum('hours'),
            billable_hours=models.Sum('hours', filter=models.Q(is_billable=True)),
            billable_amount=models.Sum('billing_amount'),
            costing_amount=models.Sum('costing_amount')
        )

        # Calculate from linked timecard entries
        timecard_total = self.timecard_entries.aggregate(
            total_hours=models.Sum('hours'),
            billable_hours=models.Sum('hours', filter=models.Q(is_billable=True))
        )

        # Combine totals
        self.total_hours = (details_total['total_hours'] or Decimal('0')) + (timecard_total['total_hours'] or Decimal('0'))
        self.total_billable_hours = (details_total['billable_hours'] or Decimal('0')) + (timecard_total['billable_hours'] or Decimal('0'))
        self.total_billable_amount = details_total['billable_amount'] or Decimal('0')
        self.total_costing_amount = details_total['costing_amount'] or Decimal('0')

        # Update project time tracking
        self._update_project_time_tracking()

        self.save(update_fields=['total_hours', 'total_billable_hours', 'total_billable_amount', 'total_costing_amount'])

    def _update_project_time_tracking(self):
        """Update project time tracking aggregates"""
        # Get all projects involved in this timesheet
        projects_in_timesheet = self.details.values_list('project', flat=True).distinct()

        for project_id in projects_in_timesheet:
            if project_id:
                try:
                    project = Project.objects.get(id=project_id)
                    time_tracking, created = ProjectTimeTracking.objects.get_or_create(
                        project=project,
                        defaults={'total_estimated_hours': project.estimated_hours or 0}
                    )
                    time_tracking.recalculate_totals()
                except Project.DoesNotExist:
                    continue

    @property
    def project(self):
        """Get the main project associated with this timesheet"""
        # Since timesheet can have multiple projects through details,
        # we'll get the most frequently used project
        project_hours = self.details.values('project').annotate(
            total_hours=models.Sum('hours')
        ).order_by('-total_hours').first()

        if project_hours and project_hours['project']:
            from .models import Project
            return Project.objects.filter(id=project_hours['project']).first()
        return None

    @property
    def efficiency_rate(self):
        """Calculate efficiency rate (billable hours / total hours)"""
        if self.total_hours > 0:
            return (self.total_billable_hours / self.total_hours) * 100
        return 0


class TimesheetDetail(models.Model):
    id = models.BigAutoField(primary_key=True)
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE, related_name='details')
    activity_date = models.DateField()
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True)
    task = models.ForeignKey(ProjectTask, on_delete=models.SET_NULL, null=True, blank=True)
    activity_type = models.ForeignKey(ActivityTypeMaster, on_delete=models.SET_NULL, null=True, blank=True)
    from_time = models.TimeField(null=True, blank=True)
    to_time = models.TimeField(null=True, blank=True)
    hours = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_billable = models.BooleanField(default=True)
    billing_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    billing_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    costing_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    costing_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'timesheet_details'
        ordering = ['activity_date', 'from_time']

    def __str__(self):
        return f"{self.timesheet.timesheet_code} - {self.activity_date}"


class ProjectExpense(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
    ]

    id = models.BigAutoField(primary_key=True)
    expense_code = models.CharField(max_length=50, unique=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='expenses')
    task = models.ForeignKey(ProjectTask, on_delete=models.SET_NULL, null=True, blank=True)
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='project_expenses')
    expense_date = models.DateField()
    expense_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    is_billable = models.BooleanField(default=False)
    is_reimbursable = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    approved_by = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_expenses')
    approved_date = models.DateTimeField(null=True, blank=True)
    attachment_url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_expenses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_expenses'
        ordering = ['-expense_date']

    def __str__(self):
        return f"{self.expense_code} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.expense_code:
            self.expense_code = self.generate_expense_code()
        super().save(*args, **kwargs)

    def generate_expense_code(self):
        from datetime import datetime
        year = datetime.now().year
        count = ProjectExpense.objects.filter(created_at__year=year).count() + 1
        return f"EXP-{year}-{count:05d}"


class ProjectDocument(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    task = models.ForeignKey(ProjectTask, on_delete=models.SET_NULL, null=True, blank=True)
    document_name = models.CharField(max_length=200)
    document_type = models.CharField(max_length=100, blank=True, null=True)
    file_url = models.URLField()
    file_size = models.BigIntegerField(null=True, blank=True)
    mime_type = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_documents'
        ordering = ['-created_at']

    def __str__(self):
        return self.document_name


class ProjectUpdate(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='updates')
    task = models.ForeignKey(ProjectTask, on_delete=models.CASCADE, null=True, blank=True,
                            related_name='comments')
    comment = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_updates'
        ordering = ['-created_at']

    def __str__(self):
        return f"Update on {self.project.project_name}"


class ProjectBudget(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='budgets')
    budget_type = models.CharField(max_length=50, blank=True, null=True)
    budgeted_amount = models.DecimalField(max_digits=15, decimal_places=2)
    actual_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    fiscal_year = models.IntegerField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_budgets'

    def __str__(self):
        return f"{self.project.project_name} - {self.budget_type}"

    @property
    def variance_amount(self):
        return self.budgeted_amount - self.actual_amount


class ProjectInvoice(models.Model):
    id = models.BigAutoField(primary_key=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='invoices')
    invoice_id = models.UUIDField(null=True, blank=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    invoice_date = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=50, blank=True, null=True)
    # TEMPORARILY COMMENTED OUT to fix migration issues - will be re-added after migrations complete
    # timesheet = models.ForeignKey(Timesheet, on_delete=models.SET_NULL, null=True, blank=True)
    timesheet_id = models.BigIntegerField(null=True, blank=True, db_column='timesheet_id')  # Temporary workaround
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_invoices'
        ordering = ['-invoice_date']

    def __str__(self):
        return f"{self.invoice_number or 'Draft'} - {self.project.project_name}"


class Team(models.Model):
    """Team model for organizing employees into groups"""
    TEAM_TYPE_CHOICES = [
        ('development', 'Development Team'),
        ('design', 'Design Team'),
        ('qa', 'Quality Assurance'),
        ('devops', 'DevOps Team'),
        ('marketing', 'Marketing Team'),
        ('sales', 'Sales Team'),
        ('support', 'Support Team'),
        ('management', 'Management Team'),
        ('cross_functional', 'Cross-Functional Team'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('archived', 'Archived'),
    ]

    id = models.BigAutoField(primary_key=True)
    team_name = models.CharField(max_length=200)
    team_code = models.CharField(max_length=20, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    team_type = models.CharField(max_length=50, choices=TEAM_TYPE_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Team leadership
    team_lead = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='led_teams')
    manager = models.ForeignKey('hr.Employee', on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='managed_teams')

    # Organization
    department = models.ForeignKey('hr.Department', on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='teams')
    company = models.ForeignKey('company.Company', on_delete=models.CASCADE,
                               null=True, blank=True, related_name='teams')

    # Settings
    max_members = models.PositiveIntegerField(default=10,
                                            help_text="Maximum number of team members")
    is_project_based = models.BooleanField(default=False,
                                         help_text="Team created for specific projects")

    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project_teams'
        ordering = ['team_name']
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'

    def __str__(self):
        return f"{self.team_name} ({self.team_code})"

    def save(self, *args, **kwargs):
        if not self.team_code:
            self.team_code = self.generate_team_code()
        super().save(*args, **kwargs)

    def generate_team_code(self):
        """Generate unique team code"""
        base_code = ''.join([word[:3].upper() for word in self.team_name.split()[:2]])
        if len(base_code) < 3:
            base_code = self.team_name[:3].upper()

        count = Team.objects.filter(team_code__startswith=base_code).count()
        return f"{base_code}{count + 1:02d}"

    @property
    def member_count(self):
        """Get current number of team members"""
        return self.team_members.filter(is_active=True).count()

    @property
    def is_full(self):
        """Check if team has reached maximum capacity"""
        return self.member_count >= self.max_members

    @property
    def available_slots(self):
        """Get number of available slots"""
        return max(0, self.max_members - self.member_count)


class TeamMember(models.Model):
    """Team membership model for employees"""
    ROLE_CHOICES = [
        ('team_lead', 'Team Lead'),
        ('senior_developer', 'Senior Developer'),
        ('developer', 'Developer'),
        ('junior_developer', 'Junior Developer'),
        ('designer', 'Designer'),
        ('qa_engineer', 'QA Engineer'),
        ('devops_engineer', 'DevOps Engineer'),
        ('business_analyst', 'Business Analyst'),
        ('project_manager', 'Project Manager'),
        ('product_owner', 'Product Owner'),
        ('scrum_master', 'Scrum Master'),
        ('consultant', 'Consultant'),
        ('intern', 'Intern'),
        ('other', 'Other'),
    ]

    AVAILABILITY_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contractor', 'Contractor'),
        ('consultant', 'Consultant'),
        ('temporary', 'Temporary'),
    ]

    id = models.BigAutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='team_members')
    employee = models.ForeignKey('hr.Employee', on_delete=models.CASCADE, related_name='team_memberships')

    # Role and responsibilities
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='developer')
    custom_role = models.CharField(max_length=100, blank=True, null=True,
                                  help_text="Custom role name if 'other' is selected")
    responsibilities = models.TextField(blank=True, null=True,
                                      help_text="Specific responsibilities in this team")

    # Availability and capacity
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='full_time')
    allocation_percentage = models.PositiveIntegerField(default=100,
                                                       help_text="Percentage of time allocated to this team")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                    help_text="Hourly rate for this team role")

    # Timeline
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True,
                               help_text="Leave blank for permanent membership")
    is_active = models.BooleanField(default=True)

    # Permissions and access
    can_manage_team = models.BooleanField(default=False,
                                        help_text="Can add/remove team members")
    can_assign_tasks = models.BooleanField(default=False,
                                         help_text="Can assign tasks to team members")
    can_view_reports = models.BooleanField(default=False,
                                         help_text="Can view team performance reports")

    # Metadata
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='added_team_members')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'team_members'
        ordering = ['-created_at']
        unique_together = ['team', 'employee']
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'

    def __str__(self):
        return f"{self.employee.full_name} - {self.team.team_name} ({self.get_role_display()})"

    def clean(self):
        """Validate team member data"""
        from django.core.exceptions import ValidationError

        # Check team capacity
        if not self.pk and self.team.is_full:
            raise ValidationError(f'Team "{self.team.team_name}" is at maximum capacity')

        # Check allocation percentage
        if self.allocation_percentage > 100:
            raise ValidationError('Allocation percentage cannot exceed 100%')

        # Check date range
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date cannot be earlier than start date')

    @property
    def role_display(self):
        """Get display name for role"""
        if self.role == 'other' and self.custom_role:
            return self.custom_role
        return self.get_role_display()

    @property
    def is_team_lead(self):
        """Check if this member is the team lead"""
        return self.team.team_lead == self.employee

    @property
    def is_current_member(self):
        """Check if membership is currently active"""
        if not self.is_active:
            return False

        today = timezone.now().date()
        if self.start_date > today:
            return False

        if self.end_date and self.end_date < today:
            return False

        return True


class ProjectSettings(models.Model):
    """
    Per-project settings for working time, overtime rules, and attendance
    Each project can override company/global settings
    """
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='settings',
        primary_key=True
    )

    # ========== WORKING TIME SETTINGS ==========
    use_custom_working_time = models.BooleanField(
        default=False,
        help_text="Use project-specific working time instead of global schedule"
    )

    # Weekly schedule
    monday_start = models.TimeField(null=True, blank=True)
    monday_end = models.TimeField(null=True, blank=True)
    tuesday_start = models.TimeField(null=True, blank=True)
    tuesday_end = models.TimeField(null=True, blank=True)
    wednesday_start = models.TimeField(null=True, blank=True)
    wednesday_end = models.TimeField(null=True, blank=True)
    thursday_start = models.TimeField(null=True, blank=True)
    thursday_end = models.TimeField(null=True, blank=True)
    friday_start = models.TimeField(null=True, blank=True)
    friday_end = models.TimeField(null=True, blank=True)
    saturday_start = models.TimeField(null=True, blank=True)
    saturday_end = models.TimeField(null=True, blank=True)
    sunday_start = models.TimeField(null=True, blank=True)
    sunday_end = models.TimeField(null=True, blank=True)

    # Break settings
    break_duration = models.IntegerField(
        'Break Duration (minutes)',
        default=60,
        help_text='Default lunch/break duration in minutes'
    )
    break_start = models.TimeField(null=True, blank=True, help_text='Standard break start time')

    # Flexibility
    flexible_hours = models.BooleanField(default=False, help_text='Allow flexible working hours')
    core_hours_start = models.TimeField(null=True, blank=True, help_text='Core hours start (for flexible schedule)')
    core_hours_end = models.TimeField(null=True, blank=True, help_text='Core hours end (for flexible schedule)')
    required_hours_per_day = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=8.0,
        help_text='Required working hours per day'
    )
    working_days_per_week = models.IntegerField(
        'Working Days Per Week',
        default=6,
        help_text='Number of working days per week (e.g., 5 or 6)',
        validators=[MinValueValidator(1), MaxValueValidator(7)]
    )

    # ========== OVERTIME RULES ==========
    use_custom_overtime_rules = models.BooleanField(
        default=False,
        help_text="Use project-specific overtime rules"
    )

    # Overtime rates
    overtime_rate_regular = models.DecimalField(
        'Regular Overtime Rate',
        max_digits=5,
        decimal_places=2,
        default=1.5,
        help_text='Multiplier for regular overtime (e.g., 1.5 = 150%)',
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    overtime_rate_weekend = models.DecimalField(
        'Weekend Overtime Rate',
        max_digits=5,
        decimal_places=2,
        default=2.0,
        help_text='Multiplier for weekend overtime',
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )
    overtime_rate_holiday = models.DecimalField(
        'Holiday Overtime Rate',
        max_digits=5,
        decimal_places=2,
        default=2.5,
        help_text='Multiplier for holiday overtime',
        validators=[MinValueValidator(1.0), MaxValueValidator(5.0)]
    )

    # Overtime limits
    min_overtime_minutes = models.IntegerField(
        'Minimum Overtime Minutes',
        default=30,
        help_text='Minimum minutes required to count as overtime',
        validators=[MinValueValidator(0)]
    )
    max_overtime_hours_per_day = models.DecimalField(
        'Max Overtime Hours Per Day',
        max_digits=4,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Maximum overtime hours allowed per day (leave empty for no limit)'
    )
    max_overtime_hours_per_week = models.DecimalField(
        'Max Overtime Hours Per Week',
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Maximum overtime hours allowed per week (leave empty for no limit)'
    )

    # Approval requirements
    overtime_requires_approval = models.BooleanField(
        default=True,
        help_text='Overtime must be pre-approved'
    )
    overtime_auto_approve_threshold = models.IntegerField(
        'Auto-approve Threshold (minutes)',
        default=0,
        help_text='Auto-approve overtime below this threshold (0 = always require approval)'
    )

    # ========== ATTENDANCE SETUP ==========
    use_custom_attendance_rules = models.BooleanField(
        default=False,
        help_text="Use project-specific attendance rules"
    )

    # Grace periods
    late_grace_period = models.IntegerField(
        'Late Grace Period (minutes)',
        default=15,
        help_text='Grace period before marking as late',
        validators=[MinValueValidator(0), MaxValueValidator(60)]
    )
    early_leave_grace_period = models.IntegerField(
        'Early Leave Grace Period (minutes)',
        default=15,
        help_text='Grace period before marking as early leave',
        validators=[MinValueValidator(0), MaxValueValidator(60)]
    )

    # Attendance requirements
    require_biometric_checkin = models.BooleanField(
        default=False,
        help_text='Require biometric device for check-in'
    )
    allow_remote_attendance = models.BooleanField(
        default=True,
        help_text='Allow remote/work-from-home attendance'
    )
    require_location_tracking = models.BooleanField(
        default=False,
        help_text='Require GPS location for attendance'
    )

    # Penalties and deductions
    late_deduction_per_minute = models.DecimalField(
        'Late Deduction Per Minute',
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text='Amount deducted per minute of lateness',
        validators=[MinValueValidator(0)]
    )
    absence_deduction_per_day = models.DecimalField(
        'Absence Deduction Per Day',
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Amount deducted for unexcused absence',
        validators=[MinValueValidator(0)]
    )

    # Limits
    max_late_minutes_per_month = models.IntegerField(
        'Max Late Minutes Per Month',
        default=120,
        help_text='Maximum allowed late minutes per month',
        validators=[MinValueValidator(0)]
    )
    max_absences_per_month = models.IntegerField(
        'Max Absences Per Month',
        default=3,
        help_text='Maximum allowed absences per month',
        validators=[MinValueValidator(0)]
    )

    # ========== METADATA ==========
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_project_settings'
    )

    class Meta:
        db_table = 'project_settings'
        verbose_name = 'Project Settings'
        verbose_name_plural = 'Project Settings'

    def __str__(self):
        return f"Settings for {self.project.project_name}"

    def get_working_hours(self, day_of_week):
        """Get working hours for a specific day (0=Monday, 6=Sunday)"""
        if not self.use_custom_working_time:
            return None, None

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

    def is_working_day(self, day_of_week):
        """Check if a specific day is a working day"""
        start_time, end_time = self.get_working_hours(day_of_week)
        return start_time is not None and end_time is not None

    def calculate_daily_hours(self, day_of_week):
        """Calculate working hours for a specific day"""
        start_time, end_time = self.get_working_hours(day_of_week)
        if not start_time or not end_time:
            return 0

        from datetime import datetime, timedelta
        start = datetime.combine(datetime.today(), start_time)
        end = datetime.combine(datetime.today(), end_time)
        if end < start:  # Handle overnight shifts
            end += timedelta(days=1)

        total_hours = (end - start).total_seconds() / 3600
        # Subtract break time
        total_hours -= (self.break_duration / 60)
        return max(0, total_hours)

    def get_total_weekly_hours(self):
        """Calculate total weekly working hours"""
        if not self.use_custom_working_time:
            return None

        total = 0
        for day in range(7):
            total += self.calculate_daily_hours(day)
        return total

    def get_overtime_rate(self, date, is_holiday=False):
        """Get applicable overtime rate for a specific date"""
        if not self.use_custom_overtime_rules:
            return None

        if is_holiday:
            return self.overtime_rate_holiday

        # Check if weekend (Saturday=5, Sunday=6)
        if date.weekday() in [5, 6]:
            return self.overtime_rate_weekend

        return self.overtime_rate_regular

    def validate_overtime_request(self, hours, date=None):
        """
        Validate if an overtime request is within limits
        Returns (is_valid, error_message)
        """
        if not self.use_custom_overtime_rules:
            return True, None

        # Check daily limit
        if self.max_overtime_hours_per_day and hours > float(self.max_overtime_hours_per_day):
            return False, f"Overtime exceeds daily limit of {self.max_overtime_hours_per_day} hours"

        # Check minimum
        if (hours * 60) < self.min_overtime_minutes:
            return False, f"Overtime must be at least {self.min_overtime_minutes} minutes"

        return True, None

    def needs_overtime_approval(self, minutes):
        """Check if overtime needs approval based on threshold"""
        if not self.use_custom_overtime_rules:
            return None

        if not self.overtime_requires_approval:
            return False

        if self.overtime_auto_approve_threshold > 0:
            return minutes > self.overtime_auto_approve_threshold

        return True
