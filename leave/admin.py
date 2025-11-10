from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import (
    LeaveType, LeavePolicy, LeavePolicyLeaveType, EmployeeLeavePolicy,
    LeaveAllocation, Holiday, LeaveApplication, CompensatoryLeaveRequest,
    LeaveEncashment, LeaveBlockedDate
)


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'max_days_per_year', 'is_paid', 'carry_forward_allowed',
                   'encashment_allowed', 'is_active']
    list_filter = ['is_paid', 'carry_forward_allowed', 'encashment_allowed', 'is_active',
                  'medical_certificate_required']
    search_fields = ['name', 'code']
    ordering = ['name']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'color', 'is_active')
        }),
        (_('Allocation Settings'), {
            'fields': ('max_days_per_year', 'is_paid', 'include_holiday')
        }),
        (_('Carry Forward'), {
            'fields': ('carry_forward_allowed', 'max_carry_forward_days'),
            'classes': ('collapse',)
        }),
        (_('Encashment'), {
            'fields': ('encashment_allowed',),
            'classes': ('collapse',)
        }),
        (_('Application Rules'), {
            'fields': ('apply_in_advance_days', 'minimum_continuous_days', 'maximum_continuous_days')
        }),
        (_('Medical Certificate'), {
            'fields': ('medical_certificate_required', 'medical_certificate_min_days'),
            'classes': ('collapse',)
        }),
    )


class LeavePolicyLeaveTypeInline(admin.TabularInline):
    model = LeavePolicyLeaveType
    extra = 1
    fields = ['leave_type', 'annual_allocation']


@admin.register(LeavePolicy)
class LeavePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_employment_months', 'requires_approval', 'is_active']
    list_filter = ['requires_approval', 'is_active', 'applicable_to_probation']
    search_fields = ['name', 'description']
    inlines = [LeavePolicyLeaveTypeInline]

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Eligibility'), {
            'fields': ('min_employment_months', 'applicable_to_probation')
        }),
        (_('Approval Workflow'), {
            'fields': ('requires_approval', 'auto_approve_half_day', 'max_days_auto_approve')
        }),
        (_('Regional Holidays'), {
            'fields': ('include_regional_holidays', 'regional_holiday_list'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmployeeLeavePolicy)
class EmployeeLeftPolicyAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_policy', 'effective_from', 'effective_to', 'is_active']
    list_filter = ['leave_policy', 'is_active', 'effective_from']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'effective_from'


@admin.register(LeaveAllocation)
class LeaveAllocationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'year', 'allocated_days', 'used_days', 'remaining_days_display', 'utilization_display']
    list_filter = ['year', 'leave_type', 'from_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'from_date'
    readonly_fields = ['remaining_days', 'utilization_percentage']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('employee', 'leave_type', 'year')
        }),
        (_('Allocation Period'), {
            'fields': ('from_date', 'to_date')
        }),
        (_('Days Allocation'), {
            'fields': ('allocated_days', 'carried_forward', 'used_days')
        }),
        (_('Calculated Fields'), {
            'fields': ('remaining_days', 'utilization_percentage'),
            'classes': ('collapse',)
        }),
    )

    def remaining_days_display(self, obj):
        remaining = obj.remaining_days
        if remaining < 0:
            return format_html('<span style="color: red;">{:.1f}</span>', remaining)
        elif remaining < 2:
            return format_html('<span style="color: orange;">{:.1f}</span>', remaining)
        return f"{remaining:.1f}"
    remaining_days_display.short_description = _('Remaining Days')

    def utilization_display(self, obj):
        utilization = obj.utilization_percentage
        if utilization > 80:
            return format_html('<span style="color: green;">{:.1f}%</span>', utilization)
        elif utilization > 50:
            return format_html('<span style="color: orange;">{:.1f}%</span>', utilization)
        return format_html('<span style="color: red;">{:.1f}%</span>', utilization)
    utilization_display.short_description = _('Utilization %')


@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'year', 'is_optional', 'applies_to_all']
    list_filter = ['year', 'is_optional', 'applies_to_all']
    search_fields = ['name', 'description']
    date_hierarchy = 'date'
    ordering = ['date']

    fieldsets = (
        (_('Holiday Details'), {
            'fields': ('name', 'date', 'year', 'description')
        }),
        (_('Configuration'), {
            'fields': ('is_optional', 'applies_to_all', 'regions')
        }),
    )


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'from_date', 'to_date', 'total_leave_days',
                   'status_display', 'half_day', 'approved_by']
    list_filter = ['status', 'leave_type', 'half_day', 'from_date', 'approved_by']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id', 'reason']
    date_hierarchy = 'from_date'
    readonly_fields = ['total_leave_days', 'created_at', 'updated_at']

    fieldsets = (
        (_('Employee & Leave Details'), {
            'fields': ('employee', 'leave_type', 'status')
        }),
        (_('Leave Period'), {
            'fields': ('from_date', 'to_date', 'total_leave_days')
        }),
        (_('Half Day Leave'), {
            'fields': ('half_day', 'half_day_date', 'leave_session'),
            'classes': ('collapse',)
        }),
        (_('Application Details'), {
            'fields': ('reason', 'posting_date')
        }),
        (_('Supporting Documents'), {
            'fields': ('supporting_document', 'medical_certificate'),
            'classes': ('collapse',)
        }),
        (_('Approval'), {
            'fields': ('approved_by', 'approved_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        (_('System Information'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def status_display(self, obj):
        status_colors = {
            'draft': 'gray',
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
            'cancelled': 'darkred',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = _('Status')

    actions = ['approve_applications', 'reject_applications']

    def approve_applications(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} leave applications approved.')
    approve_applications.short_description = _('Approve selected applications')

    def reject_applications(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='rejected',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} leave applications rejected.')
    reject_applications.short_description = _('Reject selected applications')


@admin.register(CompensatoryLeaveRequest)
class CompensatoryLeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'work_from_date', 'work_to_date', 'leave_date', 'half_day', 'status', 'approved_by']
    list_filter = ['status', 'half_day', 'work_from_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    date_hierarchy = 'work_from_date'

    fieldsets = (
        (_('Employee'), {
            'fields': ('employee',)
        }),
        (_('Overtime Work Details'), {
            'fields': ('work_from_date', 'work_to_date', 'work_end_date', 'reason')
        }),
        (_('Compensatory Leave'), {
            'fields': ('leave_date', 'half_day')
        }),
        (_('Approval'), {
            'fields': ('status', 'approved_by', 'approved_at')
        }),
    )


@admin.register(LeaveEncashment)
class LeaveEncashmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'encashable_days', 'encashment_amount_display',
                   'encashment_date', 'status', 'approved_by']
    list_filter = ['status', 'leave_type', 'encashment_date']
    search_fields = ['employee__first_name', 'employee__last_name']
    date_hierarchy = 'encashment_date'

    fieldsets = (
        (_('Employee & Leave Type'), {
            'fields': ('employee', 'leave_type')
        }),
        (_('Leave Period'), {
            'fields': ('leave_period_from', 'leave_period_to')
        }),
        (_('Encashment Details'), {
            'fields': ('encashable_days', 'encashment_amount', 'encashment_date')
        }),
        (_('Approval'), {
            'fields': ('status', 'approved_by', 'approved_at')
        }),
    )

    def encashment_amount_display(self, obj):
        return f"KHR {obj.encashment_amount:,.2f}"
    encashment_amount_display.short_description = _('Encashment Amount')


@admin.register(LeaveBlockedDate)
class LeaveBlockedDateAdmin(admin.ModelAdmin):
    list_display = ['from_date', 'to_date', 'reason', 'applies_to_company', 'block_days']
    list_filter = ['applies_to_company', 'from_date']
    search_fields = ['reason']
    date_hierarchy = 'from_date'
    ordering = ['from_date']

    fieldsets = (
        (_('Blocked Period'), {
            'fields': ('from_date', 'to_date', 'block_days')
        }),
        (_('Details'), {
            'fields': ('reason', 'applies_to_company')
        }),
    )
