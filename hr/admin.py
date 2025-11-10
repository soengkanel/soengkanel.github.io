# admin config for employees
from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    Department, Position, Employee, EmployeeDocument, EmployeeHistory,
    ProbationPeriod, ProbationExtension,
    # Employee Lifecycle models
    OnboardingTemplate, OnboardingTask, EmployeeOnboarding, OnboardingTaskInstance,
    PromotionTransfer, ExitInterview, ExitChecklist
)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent', 'created_at')
    list_filter = ('parent',)
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('parent',)

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'department', 'level')
    list_filter = ('department', 'level')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('department',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_name', 'last_name', 'employment_status')
    list_filter = ('employment_status', 'gender')
    search_fields = ('employee_id', 'first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('employee_id', 'created_at', 'updated_at')
    raw_id_fields = ()
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee_id',)
        }),
        ('Basic Information', {
            'fields': ('first_name', 'last_name', 'photo', 'gender', 'date_of_birth', 'nationality')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'email', 'address', 'emergency_contact_name', 
                      'emergency_contact_phone')
        }),
        ('Employment Information', {
            'fields': ('employment_status', 'hire_date', 'end_date')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'document_type', 'document_number', 'issue_date', 'expiry_date')
    list_filter = ('document_type', 'issue_date', 'expiry_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'document_number')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('employee',)
    date_hierarchy = 'issue_date'

@admin.register(EmployeeHistory)
class EmployeeHistoryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'event_type', 'date')
    list_filter = ('event_type', 'date')
    search_fields = ('employee__first_name', 'employee__last_name', 'description')
    readonly_fields = ('created_at',)
    raw_id_fields = ('employee',)
    date_hierarchy = 'date'

@admin.register(ProbationPeriod)
class ProbationPeriodAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_date', 'original_end_date', 'actual_end_date', 'status')
    list_filter = ('status', 'start_date')
    search_fields = ('employee__first_name', 'employee__last_name', 'evaluation_notes')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('employee',)
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Probation Period', {
            'fields': ('start_date', 'original_end_date', 'actual_end_date', 'status')
        }),
        ('Evaluation', {
            'fields': ('evaluation_notes',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ProbationExtension)
class ProbationExtensionAdmin(admin.ModelAdmin):
    list_display = ('probation_period', 'extension_duration_days', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('probation_period__employee__first_name', 
                    'probation_period__employee__last_name', 
                    'reason')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('probation_period',)

    fieldsets = (
        ('Probation Information', {
            'fields': ('probation_period',)
        }),
        ('Extension Details', {
            'fields': ('extension_duration_days', 'reason')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# IDCard admin removed - use Cards app for ID card management

# IDCardRequest admin removed - use Cards app for ID card management


# ============ EMPLOYEE LIFECYCLE ADMINS ============

class OnboardingTaskInline(admin.TabularInline):
    model = OnboardingTask
    extra = 1
    fields = ['title', 'task_type', 'priority', 'due_after_days', 'estimated_hours', 'is_mandatory', 'order']
    ordering = ['order']


@admin.register(OnboardingTemplate)
class OnboardingTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'position', 'total_duration_days', 'is_active']
    list_filter = ['is_active', 'department', 'position']
    search_fields = ['name', 'description']
    inlines = [OnboardingTaskInline]

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Scope'), {
            'fields': ('department', 'position')
        }),
        (_('Duration Settings'), {
            'fields': ('total_duration_days', 'probation_period_days')
        }),
        (_('Auto-assign Settings'), {
            'fields': ('assign_buddy', 'create_user_account', 'send_welcome_email')
        }),
    )


@admin.register(OnboardingTask)
class OnboardingTaskAdmin(admin.ModelAdmin):
    list_display = ['template', 'title', 'task_type', 'priority', 'due_after_days', 'estimated_hours', 'is_mandatory', 'order']
    list_filter = ['template', 'task_type', 'priority', 'is_mandatory', 'is_active']
    search_fields = ['title', 'description']
    ordering = ['template', 'order']

    fieldsets = (
        (_('Task Information'), {
            'fields': ('template', 'title', 'description', 'task_type', 'priority')
        }),
        (_('Timing'), {
            'fields': ('due_after_days', 'estimated_hours')
        }),
        (_('Assignment'), {
            'fields': ('assigned_to_role', 'requires_buddy')
        }),
        (_('Requirements'), {
            'fields': ('requires_approval', 'requires_attachment')
        }),
        (_('Settings'), {
            'fields': ('order', 'is_mandatory', 'is_active')
        }),
    )


class OnboardingTaskInstanceInline(admin.TabularInline):
    model = OnboardingTaskInstance
    extra = 0
    readonly_fields = ['task', 'title', 'due_date', 'status']
    fields = ['task', 'title', 'due_date', 'status', 'assigned_to', 'completion_date']


@admin.register(EmployeeOnboarding)
class EmployeeOnboardingAdmin(admin.ModelAdmin):
    list_display = ['employee', 'template', 'start_date', 'status', 'progress_percentage', 'days_remaining_display', 'is_overdue']
    list_filter = ['status', 'template', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['progress_percentage', 'total_tasks', 'completed_tasks', 'expected_completion_date']
    inlines = [OnboardingTaskInstanceInline]

    fieldsets = (
        (_('Employee & Template'), {
            'fields': ('employee', 'template', 'status')
        }),
        (_('Timeline'), {
            'fields': ('start_date', 'expected_completion_date', 'actual_completion_date')
        }),
        (_('Progress'), {
            'fields': ('progress_percentage', 'total_tasks', 'completed_tasks')
        }),
        (_('Assignments'), {
            'fields': ('hr_representative', 'buddy', 'manager')
        }),
        (_('Feedback'), {
            'fields': ('notes', 'employee_feedback', 'hr_feedback'),
            'classes': ('collapse',)
        }),
    )

    def days_remaining_display(self, obj):
        days = obj.days_remaining
        if obj.is_overdue:
            return format_html('<span style="color: red;">Overdue by {} days</span>', abs(days))
        elif days <= 3:
            return format_html('<span style="color: orange;">{} days</span>', days)
        return f"{days} days"
    days_remaining_display.short_description = _('Days Remaining')


@admin.register(OnboardingTaskInstance)
class OnboardingTaskInstanceAdmin(admin.ModelAdmin):
    list_display = ['onboarding', 'title', 'task_type', 'priority', 'due_date', 'status', 'assigned_to']
    list_filter = ['status', 'task_type', 'priority', 'due_date']
    search_fields = ['title', 'onboarding__employee__first_name', 'onboarding__employee__last_name']
    readonly_fields = ['onboarding', 'task', 'title', 'task_type', 'priority', 'due_date']

    fieldsets = (
        (_('Task Details'), {
            'fields': ('onboarding', 'task', 'title', 'description', 'task_type', 'priority')
        }),
        (_('Schedule'), {
            'fields': ('due_date', 'start_date', 'completion_date', 'estimated_hours')
        }),
        (_('Assignment'), {
            'fields': ('assigned_to', 'status')
        }),
        (_('Completion'), {
            'fields': ('actual_hours', 'completion_notes', 'attachments'),
            'classes': ('collapse',)
        }),
        (_('Approval'), {
            'fields': ('requires_approval', 'approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PromotionTransfer)
class PromotionTransferAdmin(admin.ModelAdmin):
    list_display = ['employee', 'change_type', 'current_position', 'new_position', 'effective_date', 'status']
    list_filter = ['change_type', 'status', 'effective_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['approved_at', 'implemented_at']

    fieldsets = (
        (_('Employee & Change Type'), {
            'fields': ('employee', 'change_type', 'status')
        }),
        (_('Current Details'), {
            'fields': ('current_position', 'current_department')
        }),
        (_('New Details'), {
            'fields': ('new_position', 'new_department')
        }),
        (_('Timing'), {
            'fields': ('effective_date', 'announcement_date')
        }),
        (_('Details'), {
            'fields': ('reason', 'salary_change', 'salary_change_percentage')
        }),
        (_('Approval'), {
            'fields': ('requested_by', 'approved_by', 'approved_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        (_('Implementation'), {
            'fields': ('implemented_by', 'implemented_at', 'notes'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExitInterview)
class ExitInterviewAdmin(admin.ModelAdmin):
    list_display = ['employee', 'exit_reason', 'last_working_day', 'status', 'interviewer', 'overall_satisfaction_display']
    list_filter = ['exit_reason', 'status', 'interview_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']

    fieldsets = (
        (_('Employee & Exit Details'), {
            'fields': ('employee', 'exit_reason', 'last_working_day')
        }),
        (_('Interview Details'), {
            'fields': ('interview_date', 'interviewer', 'status')
        }),
        (_('Ratings (1-5 Scale)'), {
            'fields': ('job_satisfaction', 'work_environment', 'management_quality',
                      'career_development', 'work_life_balance', 'compensation_benefits')
        }),
        (_('Feedback Questions'), {
            'fields': ('liked_most', 'liked_least', 'improvements', 'recommend_company')
        }),
        (_('Additional Feedback'), {
            'fields': ('additional_comments', 'confidential_feedback'),
            'classes': ('collapse',)
        }),
        (_('Follow-up'), {
            'fields': ('follow_up_required', 'follow_up_notes'),
            'classes': ('collapse',)
        }),
    )

    def overall_satisfaction_display(self, obj):
        rating = obj.overall_satisfaction
        if rating is None:
            return '-'

        if rating >= 4:
            color = 'green'
        elif rating >= 3:
            color = 'orange'
        else:
            color = 'red'

        return format_html('<span style="color: {};">{:.1f}/5</span>', color, rating)
    overall_satisfaction_display.short_description = _('Overall Satisfaction')


@admin.register(ExitChecklist)
class ExitChecklistAdmin(admin.ModelAdmin):
    list_display = ['employee', 'completion_percentage_display', 'all_cleared_by', 'all_cleared_date']
    list_filter = ['all_cleared_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['completion_percentage']

    fieldsets = (
        (_('Employee'), {
            'fields': ('employee',)
        }),
        (_('HR Tasks'), {
            'fields': ('final_interview_completed', 'benefits_explained', 'cobra_forms', 'final_paycheck')
        }),
        (_('IT Tasks'), {
            'fields': ('laptop_returned', 'phone_returned', 'id_card_returned', 'access_revoked', 'email_deactivated')
        }),
        (_('Finance Tasks'), {
            'fields': ('expense_reports', 'company_credit_card', 'outstanding_advances')
        }),
        (_('Manager Tasks'), {
            'fields': ('knowledge_transfer', 'project_handover', 'keys_returned')
        }),
        (_('General Tasks'), {
            'fields': ('locker_cleared', 'uniform_returned')
        }),
        (_('Completion'), {
            'fields': ('completion_percentage', 'all_cleared_by', 'all_cleared_date', 'notes')
        }),
    )

    def completion_percentage_display(self, obj):
        percentage = obj.completion_percentage
        if percentage >= 100:
            color = 'green'
        elif percentage >= 75:
            color = 'orange'
        else:
            color = 'red'

        return format_html('<span style="color: {};">{:.0f}%</span>', color, percentage)
    completion_percentage_display.short_description = _('Completion %')

