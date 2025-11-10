from rest_framework import serializers
from project.models import (
    Project, ProjectType, ProjectTemplate, ProjectTeamMember,
    ProjectTask, TaskDependency, ProjectMilestone, ActivityTypeMaster,
    Timesheet, TimesheetDetail, ProjectExpense, ProjectDocument,
    ProjectUpdate, ProjectBudget, ProjectInvoice, Team, TeamMember
)
from hr.models import Employee, Department
from company.models import Company
from django.contrib.auth import get_user_model

User = get_user_model()


class ProjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectType
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectTemplateSerializer(serializers.ModelSerializer):
    project_type_name = serializers.CharField(source='project_type.type_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ProjectTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectTeamMemberSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_code = serializers.CharField(source='employee.employee_id', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)

    class Meta:
        model = ProjectTeamMember
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectTaskSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.CharField(source='assigned_to.full_name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.full_name', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.full_name', read_only=True)
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    subtasks = serializers.SerializerMethodField()

    class Meta:
        model = ProjectTask
        fields = '__all__'
        read_only_fields = ['id', 'task_code', 'created_at', 'updated_at']

    def get_subtasks(self, obj):
        subtasks = obj.subtasks.all()
        return ProjectTaskSerializer(subtasks, many=True).data


class TaskDependencySerializer(serializers.ModelSerializer):
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    depends_on_task_name = serializers.CharField(source='depends_on_task.task_name', read_only=True)

    class Meta:
        model = TaskDependency
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ProjectMilestoneSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    completed_by_name = serializers.CharField(source='completed_by.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    is_overdue = serializers.ReadOnlyField()
    days_until_due = serializers.ReadOnlyField()
    is_critical = serializers.ReadOnlyField()
    progress_color = serializers.ReadOnlyField()

    class Meta:
        model = ProjectMilestone
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectListSerializer(serializers.ModelSerializer):
    project_type_name = serializers.CharField(source='project_type.type_name', read_only=True)
    project_manager_name = serializers.CharField(source='project_manager.full_name', read_only=True)
    team_lead_name = serializers.CharField(source='team_lead.full_name', read_only=True)
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'project_code', 'project_name', 'description', 'status', 'priority',
            'project_type_name', 'project_manager_name', 'team_lead_name',
            'department_name', 'company_name', 'expected_start_date', 'expected_end_date',
            'percent_complete', 'estimated_cost', 'actual_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'project_code', 'created_at', 'updated_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    project_type = ProjectTypeSerializer(read_only=True)
    template = ProjectTemplateSerializer(read_only=True)
    project_manager_name = serializers.CharField(source='project_manager.full_name', read_only=True)
    team_lead_name = serializers.CharField(source='team_lead.full_name', read_only=True)
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    team_members = ProjectTeamMemberSerializer(many=True, read_only=True)
    tasks = ProjectTaskSerializer(many=True, read_only=True)
    milestones = ProjectMilestoneSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'project_code', 'created_at', 'updated_at']


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'project_code', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ActivityTypeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActivityTypeMaster
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimesheetDetailSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    activity_type_name = serializers.CharField(source='activity_type.activity_name', read_only=True)

    class Meta:
        model = TimesheetDetail
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TimesheetSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)
    details = TimesheetDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Timesheet
        fields = '__all__'
        read_only_fields = ['id', 'timesheet_code', 'created_at', 'updated_at']


class ProjectExpenseSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)

    class Meta:
        model = ProjectExpense
        fields = '__all__'
        read_only_fields = ['id', 'expense_code', 'created_at', 'updated_at']


class ProjectDocumentSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)

    class Meta:
        model = ProjectDocument
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectUpdateSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    task_name = serializers.CharField(source='task.task_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)

    class Meta:
        model = ProjectUpdate
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectBudgetSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    variance_amount = serializers.ReadOnlyField()

    class Meta:
        model = ProjectBudget
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectInvoiceSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.project_name', read_only=True)
    timesheet_code = serializers.CharField(source='timesheet.timesheet_code', read_only=True)

    class Meta:
        model = ProjectInvoice
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TeamSerializer(serializers.ModelSerializer):
    team_lead_name = serializers.CharField(source='team_lead.full_name', read_only=True)
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    department_name = serializers.CharField(source='department.department_name', read_only=True)
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    member_count = serializers.ReadOnlyField()
    is_full = serializers.ReadOnlyField()
    available_slots = serializers.ReadOnlyField()

    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['id', 'team_code', 'created_at', 'updated_at', 'created_by']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TeamMemberSerializer(serializers.ModelSerializer):
    team_name = serializers.CharField(source='team.team_name', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_code = serializers.CharField(source='employee.employee_id', read_only=True)
    role_display = serializers.ReadOnlyField()
    is_team_lead = serializers.ReadOnlyField()
    is_current_member = serializers.ReadOnlyField()

    class Meta:
        model = TeamMember
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'added_by']

    def create(self, validated_data):
        validated_data['added_by'] = self.context['request'].user
        return super().create(validated_data)


class ProjectStatsSerializer(serializers.Serializer):
    total_projects = serializers.IntegerField()
    active_projects = serializers.IntegerField()
    completed_projects = serializers.IntegerField()
    overdue_projects = serializers.IntegerField()
    total_budget = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_spent = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_completion = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_tasks = serializers.IntegerField()
    completed_tasks = serializers.IntegerField()
    overdue_tasks = serializers.IntegerField()