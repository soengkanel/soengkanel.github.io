from django.contrib import admin
from .models import (
    Zone, Worker, Document,
    Building, Floor, WorkerProbationPeriod, WorkerProbationExtension
)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('worker', 'document_type', 'document_number', 'issue_date', 'expiry_date', 'issuing_authority', 'created_by')
    list_filter = ('document_type', 'issue_date', 'expiry_date', 'worker__zone')
    search_fields = ('worker__first_name', 'worker__last_name', 'worker__worker_id', 'document_number', 'issuing_authority', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'issue_date'
    raw_id_fields = ('worker', 'created_by')
    
    fieldsets = (
        ('Worker Information', {
            'fields': ('worker',)
        }),
        ('Document Details', {
            'fields': ('document_type', 'document_number', 'issue_date', 'expiry_date', 'issuing_authority', 'document_file')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'is_active', 'created_by', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'phone_number', 'address')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('created_by',)
    
    fieldsets = (
        ('Zone Information', {
            'fields': ('name', 'is_active')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address')
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1
    fields = ('document_type', 'document_number', 'issue_date', 'expiry_date', 'issuing_authority', 'document_file', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('worker')


class WorkerProbationPeriodInline(admin.TabularInline):
    model = WorkerProbationPeriod
    extra = 0
    fields = ('start_date', 'original_end_date', 'actual_end_date', 'status', 'terminated_date', 'evaluation_notes')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('worker')

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['worker_id', 'get_full_name', 'nickname', 'is_vip', 'zone', 'building', 'status', 'date_joined']
    list_filter = ['status', 'is_vip', 'zone', 'building', 'date_joined']
    search_fields = ['worker_id', 'first_name', 'last_name', 'nickname', 'phone_number']
    ordering = ['-date_joined']
    readonly_fields = ('worker_id', 'created_at', 'updated_at', 'date_joined')
    raw_id_fields = ('zone', 'building', 'floor', 'position', 'created_by')
    inlines = [DocumentInline, WorkerProbationPeriodInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('worker_id', 'first_name', 'last_name', 'nickname', 'sex', 'dob', 'nationality', 'is_vip')
        }),
        ('Photo', {
            'fields': ('photo',)
        }),
        ('Position', {
            'fields': ('position',)
        }),
        ('Contact Information', {
            'fields': ('phone_number',)
        }),
        ('Work Assignment', {
            'fields': ('zone', 'building', 'floor', 'status')
        }),
        ('System Information', {
            'fields': ('date_joined', 'created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def document_count(self, obj):
        return obj.documents.count()
    document_count.short_description = 'Documents'

@admin.register(Building)
class BuildingAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone', 'address', 'total_floors', 'is_active', 'created_at')
    list_filter = ('zone', 'is_active', 'created_at')
    search_fields = ('name', 'address', 'description', 'zone__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('zone', 'created_by')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'zone', 'is_active')
        }),
        ('Location Details', {
            'fields': ('address', 'total_floors', 'description')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Floor)
class FloorAdmin(admin.ModelAdmin):
    list_display = ('building', 'floor_number', 'name', 'is_active', 'created_at')
    list_filter = ('is_active', 'building', 'created_at')
    search_fields = ('name', 'description', 'building__name')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('building', 'created_by')
    list_select_related = ('building',)


class WorkerProbationExtensionInline(admin.TabularInline):
    model = WorkerProbationExtension
    extra = 0
    fields = ('extension_duration_days', 'reason', 'approved_by', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('approved_by', 'created_by')


@admin.register(WorkerProbationPeriod)
class WorkerProbationPeriodAdmin(admin.ModelAdmin):
    list_display = ('worker', 'start_date', 'original_end_date', 'actual_end_date', 'worker_status', 'is_active_status', 'days_remaining', 'created_by')
    list_filter = ('worker__status', 'start_date', 'worker__zone')
    search_fields = ('worker__first_name', 'worker__last_name', 'worker__worker_id', 'evaluation_notes', 'termination_reason')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'start_date'
    raw_id_fields = ('worker', 'created_by', 'terminated_by')
    inlines = [WorkerProbationExtensionInline]
    
    fieldsets = (
        ('Worker Information', {
            'fields': ('worker',)
        }),
        ('Probation Period', {
            'fields': ('start_date', 'original_end_date', 'actual_end_date')
        }),
        ('Evaluation', {
            'fields': ('evaluation_notes',)
        }),
        ('Termination Details', {
            'fields': ('terminated_date', 'termination_reason', 'terminated_by'),
            'classes': ('collapse',),
            'description': 'Only applicable when status is "Terminated"'
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )

    def is_active_status(self, obj):
        return obj.is_active
    is_active_status.boolean = True
    is_active_status.short_description = 'Currently Active'

    def days_remaining(self, obj):
        return obj.days_remaining
    days_remaining.short_description = 'Days Remaining'
    
    def worker_status(self, obj):
        return obj.worker.get_status_display()
    worker_status.short_description = 'Worker Status'


@admin.register(WorkerProbationExtension)
class WorkerProbationExtensionAdmin(admin.ModelAdmin):
    list_display = ('probation_period', 'extension_duration_days', 'approved_by', 'created_at')
    list_filter = ('extension_duration_days', 'approved_by', 'created_at')
    search_fields = ('probation_period__worker__first_name', 
                    'probation_period__worker__last_name',
                    'probation_period__worker__worker_id', 
                    'reason')
    readonly_fields = ('created_at', 'updated_at')
    raw_id_fields = ('probation_period', 'approved_by', 'created_by')
    
    fieldsets = (
        ('Probation Information', {
            'fields': ('probation_period',)
        }),
        ('Extension Details', {
            'fields': ('extension_duration_days', 'reason', 'approved_by')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    ) 