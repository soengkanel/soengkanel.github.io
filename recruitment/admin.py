from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    JobPosting, Candidate, Interview, Assessment,
    JobOffer, CandidateStatusHistory, Application
)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'position', 'status', 'vacancies', 'posted_date', 'closing_date']
    list_filter = ['status', 'department', 'employment_type', 'posted_date']
    search_fields = ['title', 'description', 'requirements']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    fieldsets = (
        (_('Job Information'), {
            'fields': ('title', 'department', 'position', 'employment_type', 'vacancies')
        }),
        (_('Job Details'), {
            'fields': ('description', 'requirements', 'responsibilities', 'qualifications')
        }),
        (_('Compensation'), {
            'fields': ('salary_range_min', 'salary_range_max')
        }),
        (_('Status & Dates'), {
            'fields': ('status', 'posted_date', 'closing_date')
        }),
        (_('System Information'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'job_posting', 'application_status', 'applied_date']
    list_filter = ['application_status', 'job_posting', 'applied_date']
    search_fields = ['first_name', 'last_name', 'email', 'phone']
    readonly_fields = ['applied_date', 'created_at', 'updated_at']

    fieldsets = (
        (_('Personal Information'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'address')
        }),
        (_('Application Details'), {
            'fields': ('job_posting', 'application_status', 'applied_date')
        }),
        (_('Documents'), {
            'fields': ('resume', 'cover_letter')
        }),
        (_('Additional Information'), {
            'fields': ('expected_salary', 'notice_period', 'availability_date')
        }),
        (_('Screening & Review'), {
            'fields': ('notes', 'reviewed_by', 'reviewed_at', 'reference_check_status', 'background_check_status')
        }),
        (_('Hiring Details'), {
            'fields': ('hired_as_employee', 'hired_date'),
            'classes': ('collapse',)
        }),
        (_('Rejection Details'), {
            'fields': ('rejection_reason', 'rejected_at'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'interview_type', 'scheduled_date', 'status', 'interviewer', 'rating']
    list_filter = ['interview_type', 'status', 'scheduled_date']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'candidate__email']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    filter_horizontal = ['panel_members']

    fieldsets = (
        (_('Interview Details'), {
            'fields': ('candidate', 'interview_type', 'status')
        }),
        (_('Scheduling'), {
            'fields': ('scheduled_date', 'duration_minutes', 'location', 'meeting_link')
        }),
        (_('Interviewers'), {
            'fields': ('interviewer', 'panel_members')
        }),
        (_('Feedback & Evaluation'), {
            'fields': ('feedback', 'rating', 'strengths', 'weaknesses', 'recommendation')
        }),
        (_('Timestamps'), {
            'fields': ('completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'title', 'assessment_type', 'status', 'score', 'percentage_score', 'assigned_date']
    list_filter = ['assessment_type', 'status', 'assigned_date']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'title']
    readonly_fields = ['assigned_date', 'submitted_date', 'evaluated_at', 'created_at', 'updated_at', 'percentage_score']

    fieldsets = (
        (_('Assessment Information'), {
            'fields': ('candidate', 'assessment_type', 'status', 'title')
        }),
        (_('Assessment Details'), {
            'fields': ('description', 'instructions')
        }),
        (_('Timing'), {
            'fields': ('assigned_date', 'due_date', 'submitted_date')
        }),
        (_('Results & Evaluation'), {
            'fields': ('file_submission', 'score', 'max_score', 'percentage_score', 'evaluator_notes', 'evaluated_by', 'evaluated_at')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobOffer)
class JobOfferAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'position_offered', 'salary', 'status', 'start_date', 'offer_sent_date']
    list_filter = ['status', 'employment_type', 'start_date']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'candidate__email']
    readonly_fields = ['offer_sent_date', 'response_date', 'approved_at', 'created_at', 'updated_at']

    fieldsets = (
        (_('Candidate & Position'), {
            'fields': ('candidate', 'position_offered', 'department', 'status')
        }),
        (_('Compensation'), {
            'fields': ('salary', 'currency', 'bonus', 'benefits')
        }),
        (_('Employment Details'), {
            'fields': ('employment_type', 'start_date', 'probation_period_months')
        }),
        (_('Offer Management'), {
            'fields': ('offer_letter', 'offer_sent_date', 'offer_expiry_date')
        }),
        (_('Candidate Response'), {
            'fields': ('candidate_response', 'response_date')
        }),
        (_('Approval'), {
            'fields': ('approved_by', 'approved_at')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('System Information'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CandidateStatusHistory)
class CandidateStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'old_status', 'new_status', 'changed_by', 'timestamp']
    list_filter = ['new_status', 'timestamp']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'reason']
    readonly_fields = ['timestamp']

    def has_add_permission(self, request):
        return False  # Status history is auto-created

    def has_change_permission(self, request, obj=None):
        return False  # Don't allow editing history

    def has_delete_permission(self, request, obj=None):
        return False  # Don't allow deleting history


# Register legacy Application model
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job_posting', 'status', 'applied_date']
    list_filter = ['status', 'applied_date']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'job_posting__title']
    readonly_fields = ['applied_date', 'reviewed_at']
