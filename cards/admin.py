from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import WorkerIDCard, EmployeeIDCard, CardReplacement, PrintBatch, CardPrintingHistory, EmployeeCardPrintingHistory


@admin.register(WorkerIDCard)
class WorkerIDCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'worker', 'status', 'issue_date', 'expiry_date', 'created_at')
    list_filter = ('status', 'issue_date', 'expiry_date', 'created_at')
    search_fields = ('card_number', 'worker__first_name', 'worker__last_name', 'worker__worker_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Worker Information', {
            'fields': ('worker',)
        }),
        ('Card Details', {
            'fields': ('card_number', 'status')
        }),
        ('Important Dates', {
            'fields': ('issue_date', 'expiry_date')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('worker')


@admin.register(EmployeeIDCard)
class EmployeeIDCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'employee', 'status', 'issue_date', 'expiry_date', 'created_at')
    list_filter = ('status', 'issue_date', 'expiry_date', 'created_at')
    search_fields = ('card_number', 'employee__first_name', 'employee__last_name', 'employee__employee_id')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee',)
        }),
        ('Card Details', {
            'fields': ('card_number', 'status', 'card_type')
        }),
        ('Important Dates', {
            'fields': ('issue_date', 'expiry_date')
        }),
        ('Photo', {
            'fields': ('photo',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee')


@admin.register(CardReplacement)
class CardReplacementAdmin(admin.ModelAdmin):
    list_display = ('get_card_holder', 'get_card_type', 'reason', 'status', 'created_at', 'replacement_charge')
    list_filter = ('reason', 'status', 'created_at')
    search_fields = (
        'worker_card__worker__first_name', 'worker_card__worker__last_name',
        'employee_card__employee__first_name', 'employee_card__employee__last_name')
    readonly_fields = ('created_at', 'updated_at', 'replacement_charge')
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

    fieldsets = (
        ('Card Information', {
            'fields': ('worker_card', 'employee_card')
        }),
        ('Replacement Details', {
            'fields': ('reason', 'notes')
        }),
        ('Processing', {
            'fields': ('status',)
        }),
        ('Cost Information', {
            'fields': ('replacement_charge',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_card_holder(self, obj):
        if obj.worker_card:
            return str(obj.worker_card.worker)
        elif obj.employee_card:
            return str(obj.employee_card.employee)
        return '-'
    get_card_holder.short_description = 'Card Holder'

    def get_card_type(self, obj):
        if obj.worker_card:
            return "Worker ID"
        elif obj.employee_card:
            return "Employee ID"
        return '-'
    get_card_type.short_description = 'Card Type'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'worker_card__worker', 'employee_card__employee'
        )


@admin.register(PrintBatch)
class PrintBatchAdmin(admin.ModelAdmin):
    list_display = ('short_batch_id', 'batch_type', 'card_count', 'printed_by', 'print_date')
    list_filter = ('batch_type', 'print_date', 'printed_by')
    search_fields = ('batch_id', 'batch_name', 'notes')
    readonly_fields = ('batch_id', 'print_date', 'created_at')
    date_hierarchy = 'print_date'
    ordering = ['-print_date']

    fieldsets = (
        ('Batch Information', {
            'fields': ('batch_id', 'batch_name', 'batch_type')
        }),
        ('Print Details', {
            'fields': ('printed_by', 'card_count', 'print_date')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('printed_by')


@admin.register(CardPrintingHistory)
class CardPrintingHistoryAdmin(admin.ModelAdmin):
    list_display = ('card', 'print_number', 'print_batch_id', 'printed_by', 'print_date', 'charge_amount')
    list_filter = ('print_date', 'printed_by', 'print_batch')
    search_fields = ('card__card_number', 'card__worker__first_name', 'card__worker__last_name')
    readonly_fields = ('print_date', 'created_at')
    date_hierarchy = 'print_date'
    ordering = ['-print_date']

    def print_batch_id(self, obj):
        if obj.print_batch:
            return obj.print_batch.short_batch_id
        return '-'
    print_batch_id.short_description = 'Batch ID'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('card__worker', 'printed_by', 'print_batch')


@admin.register(EmployeeCardPrintingHistory)
class EmployeeCardPrintingHistoryAdmin(admin.ModelAdmin):
    list_display = ('card', 'print_number', 'print_batch_id', 'printed_by', 'print_date', 'charge_amount')
    list_filter = ('print_date', 'printed_by', 'print_batch')
    search_fields = ('card__card_number', 'card__employee__first_name', 'card__employee__last_name')
    readonly_fields = ('print_date', 'created_at')
    date_hierarchy = 'print_date'
    ordering = ['-print_date']

    def print_batch_id(self, obj):
        if obj.print_batch:
            return obj.print_batch.short_batch_id
        return '-'
    print_batch_id.short_description = 'Batch ID'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('card__employee', 'printed_by', 'print_batch') 