from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import DocumentSubmission, DocumentUpdate, DocumentType, SubmissionWorker


class SubmissionWorkerInline(admin.TabularInline):
    model = SubmissionWorker
    extra = 0
    fields = ('worker', 'mark')
    autocomplete_fields = ('worker',)


@admin.register(DocumentSubmission)
class DocumentSubmissionAdmin(admin.ModelAdmin):
    inlines = [SubmissionWorkerInline]
    list_display = (
        'submission_id', 'document_type_display', 'applicant_names_display', 'total_applicants_display', 'status_badge', 
        'submission_date', 'expected_completion_date', 'days_remaining_display', 
        'processing_entity', 'is_overdue_display'
    )
    list_filter = (
        'status', 'document_type', 'processing_entity', 'submission_date', 
        'expected_completion_date', 'created_at'
    )
    search_fields = (
        'submission_id', 'reference_number', 
        'workers__first_name', 'workers__last_name', 'workers__worker_id',
        'processing_office', 'notes'
    )
    readonly_fields = (
        'submission_id', 'expected_completion_date', 'days_remaining', 'is_overdue', 
        'is_expiring_soon', 'total_applicants', 'created_at', 'updated_at'
    )
    date_hierarchy = 'submission_date'
    ordering = ['-submission_date', '-created_at']
    # filter_horizontal removed due to through model 
    
    fieldsets = (
        ('Applicant Information', {
            'fields': ('total_applicants',),
            'description': 'Workers are managed through the Submission Workers section below.'
        }),
        ('Document Details', {
            'fields': ('document_type', 'document_title', 'purpose', 'status')
        }),
        ('Government Office Information', {
            'fields': ('processing_entity', 'government_office', 'reference_number')
        }),
        ('Important Dates', {
            'fields': ('submission_date', 'expected_completion_date', 'actual_completion_date', 'expiry_date')
        }),
        ('Tracking Information', {
            'fields': ('submission_id', 'days_remaining', 'is_overdue', 'is_expiring_soon')
        }),
        ('File Attachments', {
            'fields': ('submitted_documents', 'received_documents'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def document_type_display(self, obj):
        return obj.get_document_type_display()
    document_type_display.short_description = 'Document Type'
    
    def applicant_names_display(self, obj):
        """Display applicant names with count if many"""
        if not obj.pk:
            return format_html('<span style="color: #999;">New submission</span>')
        names = obj.applicant_names
        if not names:
            return format_html('<span style="color: #999;">No applicants</span>')
        elif len(names) <= 2:
            return ", ".join(names)
        else:
            return f"{names[0]}, {names[1]} (+{len(names) - 2} more)"
    applicant_names_display.short_description = 'Applicants'
    
    def total_applicants_display(self, obj):
        """Display total count of applicants"""
        if not obj.pk:
            return format_html('<span style="color: #999;">-</span>')
        total = obj.total_applicants
        if total == 0:
            return format_html('<span style="color: #999;">0</span>')
        else:
            workers_count = obj.workers.count()
            vips_count = obj.vips.count()
            details = []
            if workers_count > 0:
                details.append(f"{workers_count} worker{'s' if workers_count != 1 else ''}")
            if vips_count > 0:
                details.append(f"{vips_count} VIP{'s' if vips_count != 1 else ''}")
            return format_html('<span title="{}">{}</span>', ", ".join(details), total)
    total_applicants_display.short_description = 'Total'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',  # Yellow
            'submitted': '#17a2b8',  # Blue
            'under_review': '#6f42c1',  # Purple
            'approved': '#28a745',  # Green
            'rejected': '#dc3545',  # Red
            'completed': '#20c997',  # Teal
            'expired': '#6c757d',  # Gray
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def days_remaining_display(self, obj):
        days = obj.days_remaining
        if days is None:
            return '-'
        if days < 0:
            return format_html('<span style="color: red; font-weight: bold;">Overdue by {} days</span>', abs(days))
        elif days <= 3:
            return format_html('<span style="color: orange; font-weight: bold;">{} days</span>', days)
        else:
            return f"{days} days"
    days_remaining_display.short_description = 'Days Remaining'
    
    def is_overdue_display(self, obj):
        return obj.is_overdue
    is_overdue_display.boolean = True
    is_overdue_display.short_description = 'Overdue'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('workers', 'vips')

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Create update record for status changes
        if change and 'status' in form.changed_data:
            DocumentUpdate.objects.create(
                submission=obj,
                update_type='status_change',
                old_value=form.initial.get('status', ''),
                new_value=obj.status,
                updated_by=request.user.username,
                notes=f"Status changed by {request.user.get_full_name() or request.user.username}"
            )


@admin.register(SubmissionWorker)
class SubmissionWorkerAdmin(admin.ModelAdmin):
    list_display = ('submission', 'worker', 'mark', 'created_at')
    list_filter = ('mark', 'created_at')
    search_fields = ('submission__submission_id', 'worker__first_name', 'worker__last_name', 'worker__worker_id')
    ordering = ['-created_at']
    autocomplete_fields = ('submission', 'worker')


@admin.register(DocumentUpdate)
class DocumentUpdateAdmin(admin.ModelAdmin):
    list_display = ('submission_link', 'update_type', 'created_at', 'updated_by')
    list_filter = ('update_type', 'created_at')
    search_fields = ('submission__submission_id', 'notes', 'updated_by')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Update Information', {
            'fields': ('submission', 'update_type', 'updated_by')
        }),
        ('Changes', {
            'fields': ('old_value', 'new_value', 'notes')
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def submission_link(self, obj):
        url = reverse('admin:document_tracking_documentsubmission_change', args=[obj.submission.id])
        return format_html('<a href="{}">{}</a>', url, obj.submission.submission_id or f"#{obj.submission.id}")
    submission_link.short_description = 'Submission'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('submission')


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'processing_days', 'processing_entity', 'is_express', 'is_active', 'fees')
    list_filter = ('processing_entity', 'is_express', 'is_active', 'processing_days')
    search_fields = ('name', 'description', 'required_documents')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Processing Details', {
            'fields': ('processing_days', 'processing_entity', 'is_express', 'fees')
        }),
        ('Requirements', {
            'fields': ('required_documents',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Custom admin actions
@admin.action(description='Mark selected submissions as submitted')
def mark_as_submitted(modeladmin, request, queryset):
    updated = queryset.filter(status='pending').update(
        status='submitted',
        submission_date=timezone.now().date()
    )
    modeladmin.message_user(request, f'{updated} submissions marked as submitted.')

@admin.action(description='Mark selected submissions as completed')
def mark_as_completed(modeladmin, request, queryset):
    updated = queryset.filter(status__in=['submitted', 'under_review', 'approved']).update(
        status='completed',
        actual_completion_date=timezone.now().date()
    )
    modeladmin.message_user(request, f'{updated} submissions marked as completed.')

# Add actions to DocumentSubmissionAdmin
DocumentSubmissionAdmin.actions = [mark_as_submitted, mark_as_completed]
