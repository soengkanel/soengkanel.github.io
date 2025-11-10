from django.contrib import admin
from .models import Form, FormField, FormSubmission, FormTemplate, ExtensionRequest, CertificateRequest, CertificateRequestWorkerService


class FormFieldInline(admin.TabularInline):
    model = FormField
    extra = 0
    fields = ['label', 'field_type', 'is_required', 'order', 'help_text']
    ordering = ['order']


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'status', 'is_public', 'created_at', 'get_submission_count']
    list_filter = ['status', 'is_public', 'require_login', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [FormFieldInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'created_by', 'status')
        }),
        ('Access Settings', {
            'fields': ('is_public', 'require_login', 'allow_multiple_submissions')
        }),
        ('Data Collection', {
            'fields': ('collect_email', 'submission_deadline')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_submission_count(self, obj):
        return obj.get_submission_count()
    get_submission_count.short_description = 'Submissions'


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'form', 'field_type', 'is_required', 'order']
    list_filter = ['field_type', 'is_required', 'form']
    search_fields = ['label', 'form__title']
    ordering = ['form', 'order']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('form', 'label', 'field_type', 'help_text', 'order')
        }),
        ('Validation', {
            'fields': ('is_required', 'min_length', 'max_length', 'min_value', 'max_value', 'pattern')
        }),
        ('Options & Default', {
            'fields': ('options', 'default_value')
        }),
        ('Styling', {
            'fields': ('css_class', 'placeholder'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['form', 'submitted_by', 'email', 'submitted_at', 'ip_address']
    list_filter = ['form', 'submitted_at']
    search_fields = ['form__title', 'submitted_by__username', 'email']
    readonly_fields = ['submitted_at', 'ip_address', 'user_agent']
    ordering = ['-submitted_at']
    
    fieldsets = (
        ('Submission Info', {
            'fields': ('form', 'submitted_by', 'email', 'submitted_at')
        }),
        ('Data', {
            'fields': ('data',)
        }),
        ('Technical Info', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Prevent manual addition of submissions


@admin.register(FormTemplate)
class FormTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'created_by', 'is_public', 'created_at']
    list_filter = ['category', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Template Info', {
            'fields': ('name', 'description', 'category', 'created_by', 'is_public')
        }),
        ('Template Data', {
            'fields': ('template_data',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExtensionRequest)
class ExtensionRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'worker', 'status', 'extension_type', 'extension_duration', 'created_at', 'extension_end_date']
    list_filter = ['status', 'extension_type', 'extension_reason', 'current_visa_type', 'created_at']
    search_fields = ['request_number', 'worker__first_name', 'worker__last_name', 'passport_number']
    readonly_fields = ['request_number', 'created_at', 'updated_at', 'extension_end_date', 'is_expired', 'days_until_expiry']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'status', 'created_by', 'worker')
        }),
        ('Current Visa Details', {
            'fields': ('passport_number', 'current_visa_type', 'current_visa_expiry', 'entry_date')
        }),
        ('Extension Request', {
            'fields': ('extension_type', 'extension_duration', 'extension_reason', 'extension_start_date', 'additional_details')
        }),
        ('Supporting Documents', {
            'fields': ('passport_copy', 'visa_copy', 'employment_letter', 'other_documents'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes'),
            'classes': ('collapse',)
        }),
        ('Computed Fields', {
            'fields': ('extension_end_date', 'is_expired', 'days_until_expiry'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_delete_permission(self, request, obj=None):
        # Only allow deletion if status is draft
        if obj and obj.status != 'draft':
            return False
        return super().has_delete_permission(request, obj)


class CertificateRequestWorkerServiceInline(admin.TabularInline):
    model = CertificateRequestWorkerService
    extra = 0
    fields = ['worker', 'visa_service_charge', 'notes']
    readonly_fields = ['service_price']


@admin.register(CertificateRequest)
class CertificateRequestAdmin(admin.ModelAdmin):
    list_display = ['request_number', 'get_worker_names', 'certificate_type', 'status', 'urgency', 'created_at', 'expected_completion']
    list_filter = ['status', 'certificate_type', 'urgency', 'purpose', 'is_batch_request', 'created_at']
    search_fields = ['request_number', 'workers__first_name', 'workers__last_name', 'specific_details']
    readonly_fields = ['request_number', 'created_at', 'updated_at', 'is_overdue', 'days_until_deadline', 'processing_duration']
    ordering = ['-created_at']
    filter_horizontal = ['workers']
    inlines = [CertificateRequestWorkerServiceInline]

    fieldsets = (
        ('Request Information', {
            'fields': ('request_number', 'status', 'created_by', 'workers', 'is_batch_request', 'request_ref')
        }),
        ('Certificate Details', {
            'fields': ('certificate_type', 'purpose', 'urgency', 'specific_details', 'custom_text')
        }),
        ('Certificate Content Options', {
            'fields': ('include_salary', 'include_start_date', 'include_position', 'include_department')
        }),
        ('Delivery Information', {
            'fields': ('delivery_method', 'delivery_address', 'delivery_contact')
        }),
        ('Processing', {
            'fields': ('reviewed_by', 'reviewed_at', 'review_notes', 'expected_completion', 'actual_completion'),
            'classes': ('collapse',)
        }),
        ('Certificate File', {
            'fields': ('certificate_generated_at', 'certificate_file'),
            'classes': ('collapse',)
        }),
        ('Computed Fields', {
            'fields': ('is_overdue', 'days_until_deadline', 'processing_duration'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_worker_names(self, obj):
        return obj.worker_names[:50] + "..." if len(obj.worker_names) > 50 else obj.worker_names
    get_worker_names.short_description = 'Workers'


@admin.register(CertificateRequestWorkerService)
class CertificateRequestWorkerServiceAdmin(admin.ModelAdmin):
    list_display = ['certificate_request', 'worker', 'visa_service_charge', 'service_price', 'created_at']
    list_filter = ['visa_service_charge', 'certificate_request__status', 'created_at']
    search_fields = ['certificate_request__request_number', 'worker__first_name', 'worker__last_name', 'notes']
    readonly_fields = ['service_price', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Service Information', {
            'fields': ('certificate_request', 'worker', 'visa_service_charge', 'service_price')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
