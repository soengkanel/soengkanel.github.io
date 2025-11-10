from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json
from .models import AuditSession, AuditTrail, AuditException, AuditReport, SimpleAuditLog


@admin.register(AuditSession)
class AuditSessionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'ip_address', 'started_at', 'last_activity', 
        'is_active', 'session_duration'
    ]
    list_filter = ['is_active', 'started_at', 'last_activity']
    search_fields = ['user__username', 'user__email', 'ip_address', 'session_key']
    readonly_fields = ['session_key', 'started_at']
    date_hierarchy = 'started_at'
    
    def session_duration(self, obj):
        """Calculate session duration"""
        if obj.is_active:
            return "Active"
        else:
            duration = obj.last_activity - obj.started_at
            hours, remainder = divmod(duration.total_seconds(), 3600)
            minutes, _ = divmod(remainder, 60)
            return f"{int(hours)}h {int(minutes)}m"
    session_duration.short_description = "Duration"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'user', 'action_type', 'resource_type', 
        'severity', 'risk_level_badge', 'ip_address'
    ]
    list_filter = [
        'action_type', 'severity', 'timestamp', 'resource_type',
        'risk_score',
    ]
    search_fields = [
        'user__username', 'user__email', 'description', 
        'resource_name', 'correlation_id', 'ip_address'
    ]
    readonly_fields = [
        'timestamp', 'correlation_id', 'session', 'log_entry',
        'formatted_old_values', 'formatted_new_values', 'changes_summary'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'session', 'action_type', 'severity', 'timestamp')
        }),
        ('Resource Information', {
            'fields': ('resource_type', 'resource_id', 'resource_name', 'description')
        }),
        ('Changes', {
            'fields': ('formatted_old_values', 'formatted_new_values', 'changes_summary'),
            'classes': ('collapse',)
        }),
        ('Context', {
            'fields': ('ip_address', 'user_agent', 'request_path', 'request_method'),
            'classes': ('collapse',)
        }),
        ('Business Context', {
            'fields': ('department', 'location', 'business_unit'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('correlation_id', 'tags', 'risk_score', 'log_entry'),
            'classes': ('collapse',)
        }),
    )
    
    def risk_level_badge(self, obj):
        """Display risk level as colored badge"""
        level = obj.get_risk_level()
        colors = {
            'Critical': 'red',
            'High': 'orange', 
            'Medium': 'yellow',
            'Low': 'blue',
            'Minimal': 'green'
        }
        color = colors.get(level, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 12px;">{}</span>',
            color, level
        )
    risk_level_badge.short_description = "Risk Level"
    risk_level_badge.admin_order_field = 'risk_score'
    
    def formatted_old_values(self, obj):
        """Format old values as readable JSON"""
        if obj.old_values:
            return format_html('<pre>{}</pre>', json.dumps(obj.old_values, indent=2))
        return "No data"
    formatted_old_values.short_description = "Old Values"
    
    def formatted_new_values(self, obj):
        """Format new values as readable JSON"""
        if obj.new_values:
            return format_html('<pre>{}</pre>', json.dumps(obj.new_values, indent=2))
        return "No data"
    formatted_new_values.short_description = "New Values"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'session')
    
    def has_add_permission(self, request):
        # Don't allow manual creation of audit trails
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow viewing but not editing
        return False


@admin.register(AuditException)
class AuditExceptionAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'exception_type', 'user', 'resolved', 
        'resolved_by', 'resolved_at'
    ]
    list_filter = [
        'exception_type', 'resolved', 'timestamp', 'resolved_at'
    ]
    search_fields = [
        'user__username', 'description', 'error_message', 
        'request_path', 'ip_address'
    ]
    readonly_fields = [
        'timestamp', 'exception_type', 'user', 'description',
        'error_message', 'stack_trace', 'request_path', 
        'ip_address', 'user_agent'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Exception Information', {
            'fields': ('exception_type', 'user', 'timestamp', 'description')
        }),
        ('Error Details', {
            'fields': ('error_message', 'stack_trace'),
            'classes': ('collapse',)
        }),
        ('Context', {
            'fields': ('request_path', 'ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_by', 'resolved_at', 'resolution_notes')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'resolved_by')
    
    actions = ['mark_resolved']
    
    def mark_resolved(self, request, queryset):
        """Mark selected exceptions as resolved"""
        from django.utils import timezone
        
        updated = queryset.filter(resolved=False).update(
            resolved=True,
            resolved_by=request.user,
            resolved_at=timezone.now(),
            resolution_notes=f"Marked as resolved by {request.user.username} via admin interface"
        )
        
        self.message_user(
            request, 
            f"{updated} exception(s) marked as resolved."
        )
    mark_resolved.short_description = "Mark selected exceptions as resolved"


@admin.register(AuditReport)
class AuditReportAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'report_type', 'frequency', 'is_active', 
        'last_generated', 'next_generation', 'record_count'
    ]
    list_filter = [
        'report_type', 'frequency', 'is_active', 
        'created_at', 'last_generated'
    ]
    search_fields = ['name', 'description']
    readonly_fields = [
        'created_at', 'updated_at', 'last_generated', 
        'record_count', 'file_path'
    ]
    filter_horizontal = ['users']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('name', 'report_type', 'description')
        }),
        ('Parameters', {
            'fields': ('date_from', 'date_to', 'users', 'resource_types', 'action_types')
        }),
        ('Scheduling', {
            'fields': ('frequency', 'is_active', 'next_generation')
        }),
        ('Results', {
            'fields': ('last_generated', 'record_count', 'file_path', 'generated_by'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('generated_by')


@admin.register(SimpleAuditLog)
class SimpleAuditLogAdmin(admin.ModelAdmin):
    """Simple audit log admin - focus on what/when/who"""
    list_display = [
        'timestamp', 'user_display_name', 'action', 'model_name', 
        'object_name', 'description_preview'
    ]
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = [
        'user__username', 'user__first_name', 'user__last_name',
        'description', 'object_name', 'model_name'
    ]
    readonly_fields = [
        'timestamp', 'user', 'action', 'model_name', 
        'object_id', 'object_name', 'description',
        'old_values', 'new_values', 'ip_address'
    ]
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    def user_display_name(self, obj):
        """Display user name or System"""
        return obj.user_display
    user_display_name.short_description = "Who"
    user_display_name.admin_order_field = 'user__username'
    
    def description_preview(self, obj):
        """Show shortened description"""
        return obj.description[:100] + "..." if len(obj.description) > 100 else obj.description
    description_preview.short_description = "What Changed"
    
    fieldsets = (
        ('Core Information', {
            'fields': ('timestamp', 'user', 'action', 'model_name', 'object_id', 'object_name')
        }),
        ('Details', {
            'fields': ('description', 'old_values', 'new_values')
        }),
        ('Context', {
            'fields': ('ip_address',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def has_add_permission(self, request):
        # Don't allow manual creation of simple audit logs
        return False
    
    def has_change_permission(self, request, obj=None):
        # Allow viewing but not editing
        return False


# Custom admin site configuration
admin.site.site_header = "GuanYu Audit Management"
admin.site.site_title = "Audit Admin"
admin.site.index_title = "Audit Management Administration"
