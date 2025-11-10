from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Service, Invoice, InvoiceLineItem, VisaServiceRecord
from payments.models import Payment


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'default_price', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'category', 'description', 'default_price', 'is_active')
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class InvoiceLineItemInline(admin.TabularInline):
    model = InvoiceLineItem
    extra = 3  # Show 3 empty rows by default
    fields = ('service', 'description', 'quantity', 'unit_price', 'total_amount', 'notes')
    readonly_fields = ('total_amount',)
    verbose_name = "Invoice Line Item"
    verbose_name_plural = "Invoice Line Items"


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ('payment_number', 'amount', 'payment_date', 'payment_method', 'status', 'reference_number')
    readonly_fields = ('payment_number',)


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number', 'client_name_display', 'subtotal', 'tax_amount', 'total_amount', 
        'status_badge', 'issue_date', 'due_date', 'is_overdue_display', 'balance_due'
    )
    list_filter = ('status', 'issue_date', 'due_date', 'created_at')
    search_fields = (
        'invoice_number', 'client_name', 
        'worker__first_name', 'worker__last_name', 'worker__worker_id',
        'vip__first_name', 'vip__last_name', 'vip__email'
    )
    readonly_fields = ('invoice_number', 'total_paid', 'balance_due', 'is_overdue', 'days_overdue', 'created_at', 'updated_at')
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date', '-created_at']
    inlines = [InvoiceLineItemInline, PaymentInline]
    
    fieldsets = (
        ('Client Information', {
            'fields': ('worker', 'vip', 'client_name')
        }),
        ('Invoice Details', {
            'fields': ('invoice_number', 'status')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date')
        }),
        ('Totals (will auto-calculate from line items below)', {
            'fields': ('subtotal', 'tax_amount', 'total_amount'),
            'description': 'Add line items below, then save to auto-calculate totals'
        }),
        ('Payment Summary', {
            'fields': ('total_paid', 'balance_due', 'is_overdue', 'days_overdue'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def client_name_display(self, obj):
        return obj.get_client_name()
    client_name_display.short_description = 'Client'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',  # Yellow
            'paid': '#28a745',     # Green
            'overdue': '#dc3545',  # Red
            'cancelled': '#6c757d', # Gray
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def is_overdue_display(self, obj):
        return obj.is_overdue
    is_overdue_display.boolean = True
    is_overdue_display.short_description = 'Overdue'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('worker', 'created_by')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        """Save the formset and recalculate invoice totals"""
        super().save_formset(request, form, formset, change)
        # Recalculate totals after saving line items
        if formset.model == InvoiceLineItem:
            invoice = form.instance
            invoice.calculate_totals()
            invoice.save()


@admin.register(InvoiceLineItem)
class InvoiceLineItemAdmin(admin.ModelAdmin):
    list_display = ('invoice_link', 'service', 'description', 'quantity', 'unit_price', 'total_amount', 'created_at')
    list_filter = ('service', 'created_at')
    search_fields = ('invoice__invoice_number', 'service__name', 'description')
    readonly_fields = ('total_amount', 'created_at')
    
    fieldsets = (
        ('Service Information', {
            'fields': ('service', 'description')
        }),
        ('Pricing', {
            'fields': ('quantity', 'unit_price', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def invoice_link(self, obj):
        url = reverse('admin:billing_invoice_change', args=[obj.invoice.id])
        return format_html('<a href="{}">{}</a>', url, obj.invoice.invoice_number)
    invoice_link.short_description = 'Invoice'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('invoice', 'service')


# Custom admin actions
@admin.action(description='Mark selected invoices as paid')
def mark_invoices_as_paid(modeladmin, request, queryset):
    updated = queryset.filter(status='pending').update(status='paid')
    modeladmin.message_user(request, f'{updated} invoices marked as paid.')

@admin.action(description='Mark selected invoices as overdue')
def mark_invoices_as_overdue(modeladmin, request, queryset):
    updated = queryset.filter(status='pending', due_date__lt=timezone.now().date()).update(status='overdue')
    modeladmin.message_user(request, f'{updated} invoices marked as overdue.')

# Add actions to InvoiceAdmin
InvoiceAdmin.actions = [mark_invoices_as_paid, mark_invoices_as_overdue]


@admin.register(VisaServiceRecord)
class VisaServiceRecordAdmin(admin.ModelAdmin):
    list_display = ['get_client_name', 'service', 'duration_months', 'amount', 'status', 'start_date', 'end_date', 'created_at']
    list_filter = ['status', 'duration_months', 'service', 'created_at', 'start_date', 'end_date']
    search_fields = ['worker__first_name', 'worker__last_name', 'vip__first_name', 'vip__last_name', 'client_name', 'service__name']
    readonly_fields = ['created_at', 'updated_at', 'created_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('worker', 'vip', 'client_name')
        }),
        ('Service Details', {
            'fields': ('service', 'duration_months', 'amount', 'start_date', 'end_date')
        }),
        ('Payment & Status', {
            'fields': ('status', 'invoice', 'payment_date')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set created_by on creation
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'worker', 'vip', 'service', 'invoice', 'created_by'
        )
    
    # Custom methods for better display
    def get_client_name(self, obj):
        return obj.get_client_name()
    get_client_name.short_description = 'Client'
    get_client_name.admin_order_field = 'worker__first_name'
