from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    PayrollSettings, PayrollPeriod, SalaryComponent, EmployeeSalary, TaxSlab,
    NSSFConfiguration, SalarySlip, SalarySlipDetail, SalaryAdvance,
    EmployeeLoan, PayslipTemplate, SalaryStructure, SalaryDetail,
    SalaryStructureAssignment, AdditionalSalary, PayrollEntry, PayrollDetail
)

# Import Timesheet models
from .models_timesheet import Timesheet, TimesheetDetail


@admin.register(PayrollSettings)
class PayrollSettingsAdmin(admin.ModelAdmin):
    """Admin for Payroll Settings - Currency and Display Configuration"""
    list_display = ['base_currency', 'currency_symbol', 'currency_position', 'decimal_places', 'use_thousand_separator']

    fieldsets = (
        ('Currency Settings', {
            'fields': ('base_currency', 'currency_symbol', 'currency_position', 'decimal_places'),
            'description': 'Configure the primary currency for all payroll calculations and displays.'
        }),
        ('Display Settings', {
            'fields': ('use_thousand_separator',),
            'description': 'Customize how amounts are displayed in the system.'
        }),
        ('Company Information', {
            'fields': ('company_name',),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        # Only allow one settings instance
        return not PayrollSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of settings
        return False

    class Meta:
        verbose_name = "Payroll Settings"
        verbose_name_plural = "Payroll Settings"


class TimesheetDetailInline(admin.TabularInline):
    model = TimesheetDetail
    extra = 1
    fields = ['activity', 'from_time', 'to_time', 'hours', 'billable', 'description']
    readonly_fields = ['hours']


@admin.register(Timesheet)
class TimesheetAdmin(admin.ModelAdmin):
    list_display = ['employee', 'start_date', 'end_date', 'total_hours_display', 'billable_hours_display', 'status', 'docstatus']
    list_filter = ['status', 'docstatus', 'start_date', 'employee__department']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    date_hierarchy = 'start_date'
    readonly_fields = ['total_hours', 'billable_hours']
    inlines = [TimesheetDetailInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'start_date', 'end_date', 'status', 'docstatus')
        }),
        ('Hours Summary', {
            'fields': ('total_hours', 'billable_hours')
        }),
        ('Notes', {
            'fields': ('note',),
            'classes': ('collapse',)
        })
    )

    def total_hours_display(self, obj):
        return f"{obj.total_hours} hrs"
    total_hours_display.short_description = 'Total Hours'

    def billable_hours_display(self, obj):
        return f"{obj.billable_hours} hrs"
    billable_hours_display.short_description = 'Billable Hours'


@admin.register(PayrollPeriod)
class PayrollPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'period_type', 'start_date', 'end_date', 'payment_date', 'status',
                   'total_employees', 'total_net_pay_display', 'created_by']
    list_filter = ['period_type', 'status', 'start_date']
    search_fields = ['name', 'notes']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at', 'total_employees', 'processed_employees',
                      'total_gross_pay', 'total_deductions', 'total_net_pay', 'working_days_display',
                      'is_current_period']

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'period_type', 'start_date', 'end_date', 'payment_date', 'status')
        }),
        ('Period Metrics', {
            'fields': ('working_days_display', 'is_current_period'),
            'classes': ('collapse',)
        }),
        ('Summary Totals', {
            'fields': ('total_employees', 'processed_employees', 'total_gross_pay',
                      'total_deductions', 'total_net_pay'),
            'description': 'These values are automatically calculated from salary slips. Use the "Update Summary" action to refresh.',
        }),
        ('Tracking', {
            'fields': ('created_by', 'approved_by', 'processed_by', 'processed_at'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['update_period_summaries']

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def total_net_pay_display(self, obj):
        return f"KHR {obj.total_net_pay:,.0f}"
    total_net_pay_display.short_description = 'Total Net Pay'

    def working_days_display(self, obj):
        return f"{obj.working_days} days"
    working_days_display.short_description = 'Working Days'

    def is_current_period(self, obj):
        return '✓' if obj.is_current else ''
    is_current_period.short_description = 'Current Period'
    is_current_period.boolean = True

    def update_period_summaries(self, request, queryset):
        """Bulk action to update summary metrics for selected periods"""
        updated = 0
        for period in queryset:
            period.update_summary()
            updated += 1
        self.message_user(request, f'Successfully updated summaries for {updated} period(s).')
    update_period_summaries.short_description = 'Update summary metrics from salary slips'


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'component_type', 'calculation_type', 'is_tax_applicable', 'is_active', 'display_order']
    list_filter = ['component_type', 'calculation_type', 'is_tax_applicable', 'is_active', 'depends_on_payment_days']
    search_fields = ['code', 'name', 'abbreviation']
    ordering = ['display_order', 'name']

    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'abbreviation', 'component_type', 'description')
        }),
        ('Calculation Settings', {
            'fields': ('calculation_type', 'formula', 'condition', 'round_to_nearest')
        }),
        ('Properties', {
            'fields': ('is_payable', 'depends_on_payment_days', 'is_tax_applicable',
                      'is_additional_component', 'is_statistical_component',
                      'variable_based_on_taxable_salary')
        }),
        ('Legacy Fields', {
            'fields': ('percentage_of', 'percentage_value'),
            'classes': ('collapse',)
        }),
        ('Benefits', {
            'fields': ('max_benefit_amount', 'pay_against_benefit_claim'),
            'classes': ('collapse',)
        }),
        ('Display', {
            'fields': ('display_order', 'is_active')
        })
    )


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'basic_salary', 'gross_salary_display', 'payment_method', 'effective_date', 'is_active']
    list_filter = ['payment_method', 'is_active', 'effective_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'effective_date', 'is_active')
        }),
        ('Salary Components', {
            'fields': ('basic_salary', 'housing_allowance', 'transport_allowance',
                      'meal_allowance', 'phone_allowance', 'seniority_allowance')
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'bank_name', 'bank_account_number', 'bank_account_name')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def gross_salary_display(self, obj):
        return f"KHR {obj.gross_salary:,.0f}"
    gross_salary_display.short_description = 'Gross Salary'


@admin.register(TaxSlab)
class TaxSlabAdmin(admin.ModelAdmin):
    list_display = ['tax_range', 'tax_rate', 'fixed_tax', 'effective_from', 'is_active']
    list_filter = ['is_active', 'effective_from']
    ordering = ['min_amount']

    def tax_range(self, obj):
        if obj.max_amount:
            return f"KHR {obj.min_amount:,.0f} - {obj.max_amount:,.0f}"
        return f"Above KHR {obj.min_amount:,.0f}"
    tax_range.short_description = 'Tax Range'


@admin.register(NSSFConfiguration)
class NSSFConfigurationAdmin(admin.ModelAdmin):
    list_display = ['contribution_type', 'employee_rate', 'employer_rate', 'max_salary_cap', 'effective_from', 'is_active']
    list_filter = ['contribution_type', 'is_active', 'effective_from']


class SalarySlipDetailInline(admin.TabularInline):
    model = SalarySlipDetail
    extra = 0
    readonly_fields = ['salary_component', 'amount']


@admin.register(SalarySlip)
class SalarySlipAdmin(admin.ModelAdmin):
    list_display = ['employee', 'payroll_period', 'gross_pay_display', 'net_pay_display', 'status', 'posting_date']
    list_filter = ['status', 'payroll_period', 'posting_date', 'docstatus']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['gross_pay', 'total_deduction', 'net_pay', 'rounded_total']
    inlines = [SalarySlipDetailInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'payroll_period', 'salary_structure', 'status', 'docstatus')
        }),
        ('Period Details', {
            'fields': ('start_date', 'end_date', 'posting_date')
        }),
        ('Working Days', {
            'fields': ('total_working_days', 'payment_days', 'leave_without_pay')
        }),
        ('Salary Details', {
            'fields': ('base_salary', 'hour_rate', 'total_working_hours')
        }),
        ('Totals', {
            'fields': ('gross_pay', 'total_deduction', 'net_pay', 'rounded_total'),
            'classes': ('wide',)
        })
    )

    def gross_pay_display(self, obj):
        return f"KHR {obj.gross_pay:,.0f}"
    gross_pay_display.short_description = 'Gross Pay'

    def net_pay_display(self, obj):
        return f"KHR {obj.net_pay:,.0f}"
    net_pay_display.short_description = 'Net Pay'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(SalaryAdvance)
class SalaryAdvanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'amount_display', 'request_date', 'repayment_method', 'status', 'approved_by']
    list_filter = ['status', 'repayment_method', 'request_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['created_at', 'updated_at']

    def amount_display(self, obj):
        return f"KHR {obj.amount:,.0f}"
    amount_display.short_description = 'Amount'


@admin.register(EmployeeLoan)
class EmployeeLoanAdmin(admin.ModelAdmin):
    list_display = ['employee', 'loan_amount_display', 'monthly_installment_display',
                   'start_date', 'status', 'remaining_balance_display']
    list_filter = ['status', 'start_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    readonly_fields = ['created_at', 'updated_at', 'remaining_balance']

    def loan_amount_display(self, obj):
        return f"KHR {obj.loan_amount:,.0f}"
    loan_amount_display.short_description = 'Loan Amount'

    def monthly_installment_display(self, obj):
        return f"KHR {obj.monthly_installment:,.0f}"
    monthly_installment_display.short_description = 'Monthly Installment'

    def remaining_balance_display(self, obj):
        return f"KHR {obj.remaining_balance:,.0f}"
    remaining_balance_display.short_description = 'Remaining Balance'


# ERPNext-style admin classes

class SalaryDetailInline(admin.TabularInline):
    model = SalaryDetail
    extra = 1
    fields = ['salary_component', 'amount', 'formula', 'condition', 'statistical_component']


@admin.register(SalaryStructure)
class SalaryStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'is_active', 'docstatus', 'created_at']
    list_filter = ['is_active', 'docstatus', 'salary_slip_based_on_timesheet']
    search_fields = ['name', 'company']
    inlines = [SalaryDetailInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'company', 'is_active', 'docstatus')
        }),
        ('Payroll Settings', {
            'fields': ('salary_slip_based_on_timesheet', 'hour_rate')
        }),
        ('Leave Settings', {
            'fields': ('leave_encashment', 'max_benefits')
        })
    )


@admin.register(SalaryStructureAssignment)
class SalaryStructureAssignmentAdmin(admin.ModelAdmin):
    list_display = ['employee', 'salary_structure', 'from_date', 'to_date', 'base_salary', 'is_active', 'docstatus']
    list_filter = ['is_active', 'docstatus', 'from_date']
    search_fields = ['employee__first_name', 'employee__last_name', 'salary_structure__name']
    date_hierarchy = 'from_date'


@admin.register(AdditionalSalary)
class AdditionalSalaryAdmin(admin.ModelAdmin):
    list_display = ['employee', 'salary_component', 'amount_display', 'payroll_date', 'status', 'is_recurring']
    list_filter = ['status', 'is_recurring', 'payroll_date', 'salary_component__component_type']
    search_fields = ['employee__first_name', 'employee__last_name', 'salary_component__name']
    date_hierarchy = 'payroll_date'

    def amount_display(self, obj):
        return f"KHR {obj.amount:,.0f}"
    amount_display.short_description = 'Amount'


@admin.register(PayrollEntry)
class PayrollEntryAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'end_date', 'payroll_frequency', 'department', 'docstatus',
                   'salary_slips_created', 'salary_slips_submitted']
    list_filter = ['payroll_frequency', 'docstatus', 'salary_slips_created', 'validate_attendance']
    search_fields = ['company', 'department__name']
    date_hierarchy = 'start_date'
    filter_horizontal = ['employees']

    fieldsets = (
        ('Basic Information', {
            'fields': ('company', 'payroll_frequency', 'start_date', 'end_date', 'posting_date')
        }),
        ('Filters', {
            'fields': ('department', 'employees')
        }),
        ('Settings', {
            'fields': ('validate_attendance', 'docstatus')
        }),
        ('Status', {
            'fields': ('salary_slips_created', 'salary_slips_submitted', 'bank_entries_made'),
            'classes': ('collapse',)
        })
    )


@admin.register(PayslipTemplate)
class PayslipTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'is_active', 'created_at']
    list_filter = ['is_default', 'is_active']
    search_fields = ['name']
