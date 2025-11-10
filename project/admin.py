from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    ProjectType, ProjectTemplate, Project, ProjectTeamMember,
    ProjectTask, TaskDependency, ProjectMilestone, ActivityTypeMaster,
    Timesheet, TimesheetDetail, ProjectExpense, ProjectDocument,
    ProjectUpdate, ProjectBudget, ProjectInvoice
)


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('type_name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ProjectTemplate)
class ProjectTemplateAdmin(admin.ModelAdmin):
    list_display = ('template_name', 'project_type', 'estimated_duration_days', 'is_active', 'created_by')
    list_filter = ('project_type', 'is_active', 'created_at')
    search_fields = ('template_name', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    raw_id_fields = ('created_by',)


class ProjectTeamMemberInline(admin.TabularInline):
    model = ProjectTeamMember
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('employee',)


class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 0
    fields = ('task_name', 'assigned_to', 'status', 'priority', 'expected_end_date', 'progress')
    readonly_fields = ('task_code',)
    raw_id_fields = ('assigned_to',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_code', 'project_name', 'status', 'priority', 'project_manager', 'expected_start_date', 'percent_complete')
    list_filter = ('status', 'priority')
    search_fields = ('project_code', 'project_name', 'description')
    readonly_fields = ('id', 'project_code', 'created_at', 'updated_at')
    raw_id_fields = ('project_manager', 'created_by')
    inlines = [ProjectTeamMemberInline, ProjectTaskInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('project_code', 'project_name', 'description')
        }),
        ('Construction Details', {
            'fields': ('location', 'site_address', 'client_name', 'client_contact', 'client_phone')
        }),
        ('Organization', {
            'fields': ('project_manager',)
        }),
        ('Dates & Schedule', {
            'fields': ('expected_start_date', 'expected_end_date', 'actual_end_date')
        }),
        ('Status & Progress', {
            'fields': ('status', 'priority', 'percent_complete')
        }),
        ('Budget & Resources', {
            'fields': ('estimated_cost', 'actual_cost', 'estimated_duration_days')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ProjectTeamMember)
class ProjectTeamMemberAdmin(admin.ModelAdmin):
    list_display = ('project', 'employee', 'role', 'hourly_rate', 'is_active')
    list_filter = ('role', 'is_active', 'start_date', 'end_date')
    search_fields = ('project__project_name', 'employee__user__first_name', 'employee__user__last_name')
    raw_id_fields = ('project', 'employee')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('task_code', 'task_name', 'project', 'assigned_to', 'status', 'priority', 'progress', 'expected_end_date')
    list_filter = ('status', 'priority', 'project')
    search_fields = ('task_code', 'task_name', 'description', 'project__project_name')
    readonly_fields = ('id', 'task_code', 'created_at', 'updated_at')
    raw_id_fields = ('project', 'assigned_to')

    fieldsets = (
        ('Basic Information', {
            'fields': ('task_code', 'task_name', 'description', 'project')
        }),
        ('Assignment', {
            'fields': ('assigned_to',)
        }),
        ('Schedule', {
            'fields': ('expected_start_date', 'expected_end_date', 'actual_end_date')
        }),
        ('Status & Progress', {
            'fields': ('status', 'priority', 'progress')
        }),
        ('Time Tracking', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Additional Info', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TaskDependency)
class TaskDependencyAdmin(admin.ModelAdmin):
    list_display = ('task', 'depends_on_task', 'lag_days', 'created_at')
    raw_id_fields = ('task', 'depends_on_task')
    readonly_fields = ('id', 'created_at')


@admin.register(ProjectMilestone)
class ProjectMilestoneAdmin(admin.ModelAdmin):
    list_display = ('milestone_name', 'project', 'milestone_date', 'status', 'amount', 'completed_date')
    list_filter = ('status', 'milestone_date', 'completed_date')
    search_fields = ('milestone_name', 'project__project_name', 'description')
    raw_id_fields = ('project', 'task', 'created_by')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ActivityTypeMaster)
class ActivityTypeMasterAdmin(admin.ModelAdmin):
    list_display = ('activity_name', 'activity_type', 'is_billable', 'billing_rate', 'costing_rate', 'is_active')
    list_filter = ('activity_type', 'is_billable', 'is_active')
    search_fields = ('activity_name',)
    readonly_fields = ('id', 'created_at', 'updated_at')


class TimesheetDetailInline(admin.TabularInline):
    model = TimesheetDetail
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('project', 'task', 'activity_type')


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ('timesheet_code', 'employee', 'start_date', 'end_date', 'status', 'total_hours', 'total_billable_amount')
    list_filter = ('status', 'start_date', 'end_date', 'submitted_date', 'approved_date')
    search_fields = ('timesheet_code', 'employee__user__first_name', 'employee__user__last_name')
    readonly_fields = ('id', 'timesheet_code', 'created_at', 'updated_at')
    raw_id_fields = ('employee', 'company', 'approved_by', 'created_by')
    inlines = [TimesheetDetailInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('timesheet_code', 'employee', 'company', 'start_date', 'end_date')
        }),
        ('Status & Approval', {
            'fields': ('status', 'submitted_date', 'approved_date', 'approved_by')
        }),
        ('Totals', {
            'fields': ('total_hours', 'total_billable_hours', 'total_billed_hours', 'total_billable_amount', 'total_costing_amount', 'per_hour_rate')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TimesheetDetail)
class TimesheetDetailAdmin(admin.ModelAdmin):
    list_display = ('timesheet', 'activity_date', 'project', 'task', 'hours', 'is_billable', 'billing_amount')
    list_filter = ('activity_date', 'is_billable', 'project', 'activity_type')
    search_fields = ('timesheet__timesheet_code', 'project__project_name', 'task__task_name', 'description')
    raw_id_fields = ('timesheet', 'project', 'task', 'activity_type')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ProjectExpense)
class ProjectExpenseAdmin(admin.ModelAdmin):
    list_display = ('expense_code', 'project', 'employee', 'expense_date', 'expense_type', 'amount', 'status', 'is_billable')
    list_filter = ('status', 'is_billable', 'is_reimbursable', 'expense_date', 'approved_date')
    search_fields = ('expense_code', 'project__project_name', 'employee__user__first_name', 'description')
    readonly_fields = ('id', 'expense_code', 'created_at', 'updated_at')
    raw_id_fields = ('project', 'task', 'employee', 'approved_by', 'created_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('expense_code', 'project', 'task', 'employee', 'expense_date')
        }),
        ('Expense Details', {
            'fields': ('expense_type', 'description', 'amount', 'attachment_url')
        }),
        ('Status & Approval', {
            'fields': ('status', 'is_billable', 'is_reimbursable', 'approved_by', 'approved_date')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_name', 'project', 'document_type', 'file_size', 'uploaded_by', 'created_at')
    list_filter = ('document_type', 'created_at')
    search_fields = ('document_name', 'project__project_name', 'description')
    raw_id_fields = ('project', 'task', 'uploaded_by')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ProjectUpdate)
class ProjectUpdateAdmin(admin.ModelAdmin):
    list_display = ('project', 'task', 'is_internal', 'created_by', 'created_at')
    list_filter = ('is_internal', 'created_at')
    search_fields = ('project__project_name', 'task__task_name', 'comment')
    raw_id_fields = ('project', 'task', 'created_by')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ProjectBudget)
class ProjectBudgetAdmin(admin.ModelAdmin):
    list_display = ('project', 'budget_type', 'budgeted_amount', 'actual_amount', 'variance_amount', 'fiscal_year')
    list_filter = ('budget_type', 'fiscal_year')
    search_fields = ('project__project_name', 'budget_type')
    raw_id_fields = ('project', 'created_by')
    readonly_fields = ('id', 'variance_amount', 'created_at', 'updated_at')


@admin.register(ProjectInvoice)
class ProjectInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'project', 'invoice_date', 'amount', 'status', 'created_by')
    list_filter = ('status', 'invoice_date')
    search_fields = ('invoice_number', 'project__project_name')
    # TEMPORARILY REMOVED 'timesheet' from raw_id_fields - re-add after tenant setup
    raw_id_fields = ('project', 'created_by')
    readonly_fields = ('id', 'created_at', 'updated_at')
