from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    Project, ProjectTask, ProjectTeamMember, ProjectType,
    ProjectTemplate, Timesheet, TimesheetDetail, ProjectMilestone,
    ProjectExpense, ProjectDocument, ProjectUpdate, ActivityTypeMaster,
    ProjectBudget, ProjectInvoice, TaskDependency, ProjectTimeTracking
)

User = get_user_model()


class ProjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectType
        fields = ['id', 'type_name', 'description', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectTemplateSerializer(serializers.ModelSerializer):
    project_type_name = serializers.CharField(source='project_type.type_name', read_only=True)
    
    class Meta:
        model = ProjectTemplate
        fields = [
            'id', 'template_name', 'description', 'project_type', 'project_type_name',
            'default_tasks', 'estimated_duration_days', 'is_active', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_email = serializers.CharField(source='employee.user.email', read_only=True)
    
    class Meta:
        model = ProjectTeamMember
        fields = [
            'id', 'project', 'employee', 'employee_name', 'employee_email',
            'role', 'allocation_percentage', 'hourly_rate', 'start_date',
            'end_date', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'employee_name', 'employee_email']


class ProjectTaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.user.get_full_name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    parent_task_name = serializers.CharField(source='parent_task.task_name', read_only=True)
    
    class Meta:
        model = ProjectTask
        fields = [
            'id', 'task_code', 'project', 'project_name', 'parent_task', 'parent_task_name',
            'task_name', 'description', 'assigned_to', 'assigned_to_name', 'assigned_by',
            'expected_start_date', 'expected_end_date', 'actual_start_date', 'actual_end_date',
            'status', 'priority', 'progress', 'estimated_hours', 'actual_hours',
            'depends_on_tasks', 'review_date', 'reviewed_by', 'is_milestone', 'is_group',
            'closing_date', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'task_code', 'created_at', 'updated_at', 'created_by']


class ProjectSerializer(serializers.ModelSerializer):
    project_type_name = serializers.CharField(source='project_type.type_name', read_only=True)
    project_manager_name = serializers.CharField(source='project_manager.user.get_full_name', read_only=True)
    team_lead_name = serializers.CharField(source='team_lead.user.get_full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    # Time tracking fields
    total_logged_hours = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_billable_logged_hours = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    # Nested serializers for related data
    team_members = ProjectTeamMemberSerializer(many=True, read_only=True)
    tasks = ProjectTaskSerializer(many=True, read_only=True)

    # Computed fields
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    timesheet_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'project_code', 'project_name', 'description', 'project_type',
            'project_type_name', 'template', 'company', 'company_name',
            'department', 'department_name', 'project_manager', 'project_manager_name',
            'team_lead', 'team_lead_name', 'expected_start_date', 'expected_end_date',
            'actual_start_date', 'actual_end_date', 'status', 'priority',
            'percent_complete', 'estimated_cost', 'actual_cost', 'total_sales_amount',
            'billing_method', 'estimated_hours', 'actual_hours', 'notes',
            'is_active', 'is_milestone_tracking', 'collect_progress',
            'total_logged_hours', 'total_billable_logged_hours',
            'team_members', 'tasks', 'task_count', 'completed_task_count', 'timesheet_count',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'project_code', 'created_at', 'updated_at', 'created_by', 'actual_hours']

    def get_task_count(self, obj):
        return obj.tasks.count()

    def get_completed_task_count(self, obj):
        return obj.tasks.filter(status='completed').count()

    def get_timesheet_count(self, obj):
        return obj.get_project_timesheets().count()


    def to_representation(self, instance):
        """Add computed fields to the representation"""
        representation = super().to_representation(instance)

        # Add time tracking summary
        representation['total_logged_hours'] = str(instance.get_total_timesheet_hours())
        representation['total_billable_logged_hours'] = str(instance.get_total_billable_hours())

        return representation


class TaskDependencySerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    depends_on_task_name = serializers.CharField(source='depends_on_task.task_name', read_only=True)
    
    class Meta:
        model = TaskDependency
        fields = [
            'id', 'task', 'task_name', 'depends_on_task', 'depends_on_task_name',
            'lag_days', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    
    class Meta:
        model = ProjectMilestone
        fields = [
            'id', 'project', 'project_name', 'milestone_name', 'description',
            'milestone_date', 'task', 'task_name', 'amount', 'status',
            'completed_date', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ActivityTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTypeMaster
        fields = [
            'id', 'activity_name', 'activity_type', 'billing_rate',
            'costing_rate', 'is_billable', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimesheetDetailSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    activity_type_name = serializers.CharField(source='activity_type.activity_name', read_only=True)
    
    class Meta:
        model = TimesheetDetail
        fields = [
            'id', 'timesheet', 'activity_date', 'project', 'project_name',
            'task', 'task_name', 'activity_type', 'activity_type_name',
            'from_time', 'to_time', 'hours', 'description', 'is_billable',
            'billing_rate', 'billing_amount', 'costing_rate', 'costing_amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimesheetSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.user.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    # Nested timesheet details
    details = TimesheetDetailSerializer(many=True, read_only=True)

    # Calculated fields
    efficiency_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Timesheet
        fields = [
            'id', 'timesheet_code', 'employee', 'employee_name', 'employee_id',
            'company', 'company_name', 'start_date', 'end_date',
            'status', 'status_display', 'total_hours', 'total_billable_hours',
            'total_billed_hours', 'total_billable_amount', 'total_costing_amount',
            'per_hour_rate', 'notes', 'submitted_date', 'approved_date',
            'approved_by', 'approved_by_name', 'efficiency_rate',
            'details', 'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'timesheet_code', 'total_hours', 'total_billable_hours',
            'total_billable_amount', 'total_costing_amount', 'created_at', 'updated_at', 'created_by'
        ]

    def create(self, validated_data):
        """Create timesheet with automatic code generation"""
        timesheet = super().create(validated_data)
        timesheet.calculate_totals()
        return timesheet

    def update(self, instance, validated_data):
        """Update timesheet and recalculate totals"""
        timesheet = super().update(instance, validated_data)
        timesheet.calculate_totals()
        return timesheet


class ProjectExpenseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    employee_name = serializers.CharField(source='employee.user.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.user.get_full_name', read_only=True)
    
    class Meta:
        model = ProjectExpense
        fields = [
            'id', 'expense_code', 'project', 'project_name', 'task', 'task_name',
            'employee', 'employee_name', 'expense_date', 'expense_type',
            'description', 'amount', 'is_billable', 'is_reimbursable', 'status',
            'approved_by', 'approved_by_name', 'approved_date', 'attachment_url',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'expense_code', 'created_at', 'updated_at', 'created_by']


class ProjectDocumentSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.user.get_full_name', read_only=True)
    
    class Meta:
        model = ProjectDocument
        fields = [
            'id', 'project', 'project_name', 'task', 'task_name',
            'document_name', 'document_type', 'file_url', 'file_size',
            'mime_type', 'description', 'uploaded_by', 'uploaded_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectUpdateSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    
    class Meta:
        model = ProjectUpdate
        fields = [
            'id', 'project', 'project_name', 'task', 'task_name',
            'comment', 'is_internal', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class ProjectBudgetSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    variance_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = ProjectBudget
        fields = [
            'id', 'project', 'project_name', 'budget_type', 'budgeted_amount',
            'actual_amount', 'variance_amount', 'fiscal_year', 'created_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'variance_amount', 'created_at', 'updated_at', 'created_by']


class ProjectInvoiceSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    timesheet_code = serializers.CharField(source='timesheet.timesheet_code', read_only=True)
    
    class Meta:
        model = ProjectInvoice
        fields = [
            'id', 'project', 'project_name', 'invoice_id', 'invoice_number',
            'invoice_date', 'amount', 'status', 'timesheet', 'timesheet_code',
            'created_by', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


# Summary serializers for lighter API responses
class ProjectSummarySerializer(serializers.ModelSerializer):
    project_type_name = serializers.CharField(source='project_type.type_name', read_only=True)
    project_manager_name = serializers.CharField(source='project_manager.user.get_full_name', read_only=True)
    task_count = serializers.SerializerMethodField()
    completed_task_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'project_code', 'project_name', 'project_type_name',
            'project_manager_name', 'status', 'priority', 'percent_complete',
            'expected_start_date', 'expected_end_date', 'task_count',
            'completed_task_count'
        ]
    
    def get_task_count(self, obj):
        return obj.tasks.count()
    
    def get_completed_task_count(self, obj):
        return obj.tasks.filter(status='completed').count()


class TaskSummarySerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.user.get_full_name', read_only=True)

    class Meta:
        model = ProjectTask
        fields = [
            'id', 'task_code', 'task_name', 'project_name', 'assigned_to_name',
            'status', 'priority', 'progress', 'expected_end_date'
        ]


class ProjectTimeTrackingSerializer(serializers.ModelSerializer):
    """Serializer for ProjectTimeTracking model (ERPNext-style time tracking)"""
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    project_status = serializers.CharField(source='project.status', read_only=True)

    # Calculated properties
    hours_variance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    unbilled_hours = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    unbilled_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    is_over_budget_hours = serializers.BooleanField(read_only=True)
    budget_variance_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = ProjectTimeTracking
        fields = [
            'id', 'project', 'project_name', 'project_code', 'project_status',
            'total_estimated_hours', 'total_actual_hours', 'total_billable_hours',
            'total_billed_hours', 'total_billable_amount', 'total_billed_amount',
            'total_costing_amount', 'efficiency_rate', 'utilization_rate',
            'first_timesheet_date', 'last_timesheet_date', 'last_calculated_at',
            'hours_variance', 'unbilled_hours', 'unbilled_amount',
            'is_over_budget_hours', 'budget_variance_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_actual_hours', 'total_billable_hours', 'total_billed_hours',
            'total_billable_amount', 'total_billed_amount', 'total_costing_amount',
            'efficiency_rate', 'utilization_rate', 'first_timesheet_date',
            'last_timesheet_date', 'last_calculated_at'
        ]


class ProjectTimeReportSerializer(serializers.Serializer):
    """Serializer for project time reports"""
    project_id = serializers.UUIDField()
    project_name = serializers.CharField()
    project_code = serializers.CharField()

    # Time summary
    estimated_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    actual_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    billable_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    billed_hours = serializers.DecimalField(max_digits=10, decimal_places=2)

    # Financial summary
    billable_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    billed_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    costing_amount = serializers.DecimalField(max_digits=15, decimal_places=2)

    # Performance metrics
    efficiency_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    utilization_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    hours_variance = serializers.DecimalField(max_digits=10, decimal_places=2)

    # Date ranges
    first_timesheet_date = serializers.DateField()
    last_timesheet_date = serializers.DateField()
    last_calculated_at = serializers.DateTimeField()


class TimesheetSubmissionSerializer(serializers.Serializer):
    """Serializer for timesheet submission"""
    timesheet_id = serializers.UUIDField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_timesheet_id(self, value):
        """Validate that timesheet exists and can be submitted"""
        from django.utils.translation import gettext_lazy as _
        try:
            timesheet = Timesheet.objects.get(id=value)
            if timesheet.status != 'draft':
                raise serializers.ValidationError(_("Only draft timesheets can be submitted"))
            return value
        except Timesheet.DoesNotExist:
            raise serializers.ValidationError(_("Timesheet not found"))


class TimesheetApprovalSerializer(serializers.Serializer):
    """Serializer for timesheet approval"""
    timesheet_id = serializers.UUIDField()
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_timesheet_id(self, value):
        """Validate that timesheet exists and can be approved"""
        from django.utils.translation import gettext_lazy as _
        try:
            timesheet = Timesheet.objects.get(id=value)
            if timesheet.status != 'submitted':
                raise serializers.ValidationError(_("Only submitted timesheets can be approved"))
            return value
        except Timesheet.DoesNotExist:
            raise serializers.ValidationError(_("Timesheet not found"))