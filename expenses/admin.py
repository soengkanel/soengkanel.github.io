from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import (
    ExpenseCategory, ExpensePolicy, ExpenseClaim, ExpenseClaimLineItem,
    EmployeeAdvance, AdvanceRecovery, ExpenseApprovalWorkflow
)


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'requires_receipt', 'max_amount_per_claim', 'is_active']
    list_filter = ['requires_receipt', 'requires_approval', 'is_active']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        (_('Policy Settings'), {
            'fields': ('requires_receipt', 'max_amount_per_claim', 'requires_approval')
        }),
        (_('ERPNext Integration'), {
            'fields': ('gl_account',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ExpensePolicy)
class ExpensePolicyAdmin(admin.ModelAdmin):
    list_display = ['name', 'applies_to_all_employees', 'max_amount_per_claim', 'requires_manager_approval', 'is_active']
    list_filter = ['applies_to_all_employees', 'requires_manager_approval', 'requires_finance_approval', 'is_active']
    search_fields = ['name', 'description']
    filter_horizontal = ['applicable_positions', 'applicable_departments']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'description', 'is_active')
        }),
        (_('Eligibility'), {
            'fields': ('applies_to_all_employees', 'applicable_positions', 'applicable_departments')
        }),
        (_('Limits'), {
            'fields': ('max_amount_per_claim', 'max_amount_per_month', 'max_amount_per_year')
        }),
        (_('Approval Workflow'), {
            'fields': ('auto_approve_limit', 'requires_manager_approval', 'requires_finance_approval', 'finance_approval_limit')
        }),
        (_('Document Requirements'), {
            'fields': ('receipt_required', 'receipt_required_above')
        }),
        (_('Timing'), {
            'fields': ('claim_deadline_days',)
        }),
    )


class ExpenseClaimLineItemInline(admin.TabularInline):
    model = ExpenseClaimLineItem
    extra = 1
    fields = ['category', 'description', 'expense_date', 'amount', 'receipt']
    readonly_fields = []


@admin.register(ExpenseClaim)
class ExpenseClaimAdmin(admin.ModelAdmin):
    list_display = ['claim_id', 'employee', 'title', 'expense_date', 'total_amount_display', 'status_display', 'payment_status']
    list_filter = ['status', 'payment_status', 'policy', 'expense_date', 'created_at']
    search_fields = ['claim_id', 'employee__first_name', 'employee__last_name', 'employee__employee_id', 'title']
    readonly_fields = ['claim_id', 'total_amount', 'submitted_at', 'manager_approved_at', 'finance_approved_at', 'rejected_at', 'paid_at']
    inlines = [ExpenseClaimLineItemInline]
    date_hierarchy = 'expense_date'

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('claim_id', 'employee', 'policy', 'status', 'payment_status')
        }),
        (_('Claim Details'), {
            'fields': ('title', 'purpose', 'expense_date', 'total_amount')
        }),
        (_('Manager Approval'), {
            'fields': ('manager_approved_by', 'manager_approved_at'),
            'classes': ('collapse',)
        }),
        (_('Finance Approval'), {
            'fields': ('finance_approved_by', 'finance_approved_at'),
            'classes': ('collapse',)
        }),
        (_('Rejection'), {
            'fields': ('rejected_by', 'rejected_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        (_('Payment'), {
            'fields': ('payment_method', 'payment_reference', 'paid_by', 'paid_at'),
            'classes': ('collapse',)
        }),
        (_('ERPNext Integration'), {
            'fields': ('erp_expense_claim_id', 'erp_journal_entry_id'),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_claims', 'reject_claims', 'mark_as_paid']

    def total_amount_display(self, obj):
        return f"KHR {obj.total_amount:,.2f}"
    total_amount_display.short_description = _('Total Amount')

    def status_display(self, obj):
        status_colors = {
            'draft': 'gray',
            'submitted': 'orange',
            'manager_approved': 'blue',
            'finance_approved': 'purple',
            'approved': 'green',
            'paid': 'darkgreen',
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

    def approve_claims(self, request, queryset):
        updated = queryset.filter(status='submitted').update(
            status='approved',
            manager_approved_by=request.user,
            manager_approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} expense claims approved.')
    approve_claims.short_description = _('Approve selected claims')

    def reject_claims(self, request, queryset):
        updated = queryset.filter(status__in=['submitted', 'manager_approved']).update(
            status='rejected',
            rejected_by=request.user,
            rejected_at=timezone.now()
        )
        self.message_user(request, f'{updated} expense claims rejected.')
    reject_claims.short_description = _('Reject selected claims')

    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status='approved').update(
            status='paid',
            payment_status='paid',
            paid_by=request.user,
            paid_at=timezone.now()
        )
        self.message_user(request, f'{updated} expense claims marked as paid.')
    mark_as_paid.short_description = _('Mark selected claims as paid')


@admin.register(EmployeeAdvance)
class EmployeeAdvanceAdmin(admin.ModelAdmin):
    list_display = ['advance_id', 'employee', 'requested_amount_display', 'approved_amount_display',
                   'outstanding_amount_display', 'status_display', 'recovery_percentage_display']
    list_filter = ['status', 'recovery_method', 'created_at', 'payment_date']
    search_fields = ['advance_id', 'employee__first_name', 'employee__last_name', 'employee__employee_id', 'purpose']
    readonly_fields = ['advance_id', 'outstanding_amount', 'recovered_amount', 'installment_amount',
                      'submitted_at', 'approved_at', 'rejected_at']

    fieldsets = (
        (_('Basic Information'), {
            'fields': ('advance_id', 'employee', 'status')
        }),
        (_('Advance Details'), {
            'fields': ('purpose', 'requested_amount', 'approved_amount', 'paid_amount')
        }),
        (_('Recovery Settings'), {
            'fields': ('recovery_method', 'recovery_start_date', 'number_of_installments', 'installment_amount')
        }),
        (_('Recovery Tracking'), {
            'fields': ('outstanding_amount', 'recovered_amount'),
            'classes': ('collapse',)
        }),
        (_('Approval'), {
            'fields': ('approved_by', 'approved_at', 'submitted_at'),
            'classes': ('collapse',)
        }),
        (_('Rejection'), {
            'fields': ('rejected_by', 'rejected_at', 'rejection_reason'),
            'classes': ('collapse',)
        }),
        (_('Payment'), {
            'fields': ('payment_date', 'payment_method', 'payment_reference', 'paid_by'),
            'classes': ('collapse',)
        }),
        (_('ERPNext Integration'), {
            'fields': ('erp_employee_advance_id',),
            'classes': ('collapse',)
        }),
    )

    actions = ['approve_advances', 'reject_advances', 'mark_as_paid']

    def requested_amount_display(self, obj):
        return f"KHR {obj.requested_amount:,.2f}"
    requested_amount_display.short_description = _('Requested Amount')

    def approved_amount_display(self, obj):
        return f"KHR {obj.approved_amount:,.2f}"
    approved_amount_display.short_description = _('Approved Amount')

    def outstanding_amount_display(self, obj):
        amount = obj.outstanding_amount
        if amount > 0:
            return format_html('<span style="color: red;">KHR {:.2f}</span>', amount)
        return f"KHR {amount:,.2f}"
    outstanding_amount_display.short_description = _('Outstanding')

    def status_display(self, obj):
        status_colors = {
            'draft': 'gray',
            'submitted': 'orange',
            'approved': 'blue',
            'paid': 'green',
            'rejected': 'red',
            'cancelled': 'darkred',
            'fully_recovered': 'darkgreen',
        }
        color = status_colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = _('Status')

    def recovery_percentage_display(self, obj):
        percentage = obj.recovery_percentage
        if percentage >= 100:
            color = 'green'
        elif percentage >= 50:
            color = 'orange'
        else:
            color = 'red'
        return format_html('<span style="color: {};">{:.1f}%</span>', color, percentage)
    recovery_percentage_display.short_description = _('Recovery %')

    def approve_advances(self, request, queryset):
        updated = queryset.filter(status='submitted').update(
            status='approved',
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{updated} advances approved.')
    approve_advances.short_description = _('Approve selected advances')

    def reject_advances(self, request, queryset):
        updated = queryset.filter(status='submitted').update(
            status='rejected',
            rejected_by=request.user,
            rejected_at=timezone.now()
        )
        self.message_user(request, f'{updated} advances rejected.')
    reject_advances.short_description = _('Reject selected advances')

    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status='approved').update(
            status='paid',
            paid_by=request.user,
            payment_date=timezone.now().date()
        )
        self.message_user(request, f'{updated} advances marked as paid.')
    mark_as_paid.short_description = _('Mark selected advances as paid')
