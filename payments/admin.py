from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'payment_number', 'invoice_link', 'amount', 'payment_date', 
        'payment_method', 'status_badge', 'reference_number'
    )
    list_filter = ('payment_method', 'status', 'payment_date', 'created_at')
    search_fields = (
        'payment_number', 'invoice_number', 'reference_number',
        'invoice__invoice_number', 'invoice__client_name'
    )
    readonly_fields = ('payment_number', 'created_at', 'updated_at')
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date', '-created_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_number', 'invoice', 'invoice_number', 'amount', 'status')
        }),
        ('Payment Details', {
            'fields': ('payment_date', 'payment_method', 'reference_number')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
        ('System Information', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def invoice_link(self, obj):
        if obj.invoice:
            url = reverse('admin:billing_invoice_change', args=[obj.invoice.id])
            return format_html('<a href="{}">{}</a>', url, obj.invoice.invoice_number)
        return obj.invoice_number or '-'
    invoice_link.short_description = 'Invoice'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',    # Yellow
            'completed': '#28a745',  # Green
            'failed': '#dc3545',     # Red
            'cancelled': '#6c757d',  # Gray
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


# Custom admin actions
@admin.action(description='Mark selected payments as completed')
def mark_payments_as_completed(modeladmin, request, queryset):
    updated = queryset.filter(status='pending').update(status='completed')
    modeladmin.message_user(request, f'{updated} payments marked as completed.')

@admin.action(description='Mark selected payments as failed')
def mark_payments_as_failed(modeladmin, request, queryset):
    updated = queryset.exclude(status='completed').update(status='failed')
    modeladmin.message_user(request, f'{updated} payments marked as failed.')

# Add actions to PaymentAdmin
PaymentAdmin.actions = [mark_payments_as_completed, mark_payments_as_failed]
