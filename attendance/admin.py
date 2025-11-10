from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    BiometricDevice, BiometricTemplate, WorkSchedule, EmployeeSchedule,
    AttendanceRecord, BreakRecord, OvertimeRequest, AttendanceCorrection,
    AttendancePolicy
)


@admin.register(BiometricDevice)
class BiometricDeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'device_type', 'location', 'ip_address', 'status', 'last_sync']
    list_filter = ['device_type', 'status', 'location']
    search_fields = ['name', 'device_id', 'location', 'ip_address']
    readonly_fields = ['last_sync']
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('device_id', 'name', 'device_type', 'location')
        }),
        (_('Network Configuration'), {
            'fields': ('ip_address', 'port')
        }),
        (_('Device Details'), {
            'fields': ('serial_number', 'firmware_version', 'status')
        }),
        (_('Sync Information'), {
            'fields': ('last_sync',)
        }),
    )



@admin.register(BiometricTemplate)
class BiometricTemplateAdmin(admin.ModelAdmin):
    list_display = ['employee', 'device', 'template_type', 'finger_index', 'quality_score', 'is_primary']
    list_filter = ['template_type', 'is_primary', 'device', 'finger_index']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['enrolled_at', 'updated_at']



@admin.register(WorkSchedule)
class WorkScheduleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'flexible_hours', 'required_hours_per_day', 'is_active']
    list_filter = ['flexible_hours', 'is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        (_('Monday'), {
            'fields': ('monday_start', 'monday_end'),
            'classes': ('collapse',)
        }),
        (_('Tuesday'), {
            'fields': ('tuesday_start', 'tuesday_end'),
            'classes': ('collapse',)
        }),
        (_('Wednesday'), {
            'fields': ('wednesday_start', 'wednesday_end'),
            'classes': ('collapse',)
        }),
        (_('Thursday'), {
            'fields': ('thursday_start', 'thursday_end'),
            'classes': ('collapse',)
        }),
        (_('Friday'), {
            'fields': ('friday_start', 'friday_end'),
            'classes': ('collapse',)
        }),
        (_('Saturday'), {
            'fields': ('saturday_start', 'saturday_end'),
            'classes': ('collapse',)
        }),
        (_('Sunday'), {
            'fields': ('sunday_start', 'sunday_end'),
            'classes': ('collapse',)
        }),
        (_('Break Configuration'), {
            'fields': ('break_duration', 'break_start')
        }),
        (_('Flexibility Settings'), {
            'fields': ('flexible_hours', 'core_hours_start', 'core_hours_end', 'required_hours_per_day')
        }),
        (_('Grace Periods'), {
            'fields': ('late_grace_period', 'early_leave_grace_period')
        }),
    )



@admin.register(EmployeeSchedule)
class EmployeeScheduleAdmin(admin.ModelAdmin):
    list_display = ['employee', 'schedule', 'effective_from', 'effective_to', 'is_active']
    list_filter = ['is_active', 'schedule', 'effective_from']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'effective_from'
    readonly_fields = ['created_at', 'updated_at']



class BreakRecordInline(admin.TabularInline):
    model = BreakRecord
    extra = 0
    readonly_fields = ['duration_minutes', 'created_at']


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'clock_in_time', 'clock_out_time', 'total_hours', 'status', 'is_manual_entry']
    list_filter = ['status', 'is_manual_entry', 'date', 'schedule']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'date'
    readonly_fields = ['total_hours', 'overtime_hours', 'late_minutes', 'early_leave_minutes', 'created_at', 'updated_at']
    inlines = [BreakRecordInline]

    fieldsets = (
        (_('Employee & Date'), {
            'fields': ('employee', 'date', 'schedule')
        }),
        (_('Clock Times'), {
            'fields': ('clock_in', 'clock_out', 'clock_in_device', 'clock_out_device')
        }),
        (_('Calculated Fields'), {
            'fields': ('total_hours', 'overtime_hours', 'late_minutes', 'early_leave_minutes'),
            'classes': ('collapse',)
        }),
        (_('Status & Notes'), {
            'fields': ('status', 'notes')
        }),
        (_('Manual Entry'), {
            'fields': ('is_manual_entry', 'manual_entry_reason'),
            'classes': ('collapse',)
        }),
        (_('Approval'), {
            'fields': ('approved_by', 'approved_at'),
            'classes': ('collapse',)
        }),
    )

    def clock_in_time(self, obj):
        return obj.clock_in.strftime('%H:%M:%S') if obj.clock_in else '-'
    clock_in_time.short_description = _('Clock In')

    def clock_out_time(self, obj):
        return obj.clock_out.strftime('%H:%M:%S') if obj.clock_out else '-'
    clock_out_time.short_description = _('Clock Out')



@admin.register(BreakRecord)
class BreakRecordAdmin(admin.ModelAdmin):
    list_display = ['attendance', 'break_type', 'start_time', 'end_time', 'duration_minutes']
    list_filter = ['break_type', 'start_time']
    search_fields = ['attendance__employee__first_name', 'attendance__employee__last_name']
    readonly_fields = ['duration_minutes', 'created_at']



@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'hours', 'status', 'requested_by', 'approved_by']
    list_filter = ['status', 'date', 'overtime_rate']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('Request Details'), {
            'fields': ('employee', 'date', 'start_time', 'end_time', 'hours', 'reason')
        }),
        (_('Rate & Amount'), {
            'fields': ('overtime_rate', 'amount')
        }),
        (_('Status & Approval'), {
            'fields': ('status', 'requested_by', 'approved_by', 'approved_at', 'rejection_reason')
        }),
    )



@admin.register(AttendanceCorrection)
class AttendanceCorrectionAdmin(admin.ModelAdmin):
    list_display = ['attendance', 'correction_type', 'requested_by', 'status', 'created_at']
    list_filter = ['correction_type', 'status', 'created_at']
    search_fields = ['attendance__employee__first_name', 'attendance__employee__last_name']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('Correction Request'), {
            'fields': ('attendance', 'requested_by', 'correction_type', 'reason')
        }),
        (_('New Values'), {
            'fields': ('new_clock_in', 'new_clock_out', 'new_status')
        }),
        (_('Supporting Documents'), {
            'fields': ('supporting_document',)
        }),
        (_('Approval'), {
            'fields': ('status', 'approved_by', 'approved_at', 'rejection_reason')
        }),
    )



@admin.register(AttendancePolicy)
class AttendancePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        (_('Late Policy'), {
            'fields': ('late_deduction_per_minute', 'max_late_minutes_per_month', 'late_penalty_amount')
        }),
        (_('Absence Policy'), {
            'fields': ('absence_deduction_per_day', 'max_absences_per_month')
        }),
        (_('Overtime Policy'), {
            'fields': ('overtime_rate_regular', 'overtime_rate_holiday', 'min_overtime_minutes')
        }),
    )

