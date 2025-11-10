from django.contrib import admin
from django.utils.html import format_html
from .models import Announcement, AnnouncementRead, AnnouncementComment


class AnnouncementReadInline(admin.TabularInline):
    model = AnnouncementRead
    extra = 0
    fields = ['employee', 'read_at', 'acknowledged', 'acknowledged_at']
    readonly_fields = ['read_at', 'acknowledged_at']
    can_delete = False


class AnnouncementCommentInline(admin.TabularInline):
    model = AnnouncementComment
    extra = 0
    fields = ['employee', 'comment', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'priority_badge', 'target_audience', 'publish_date',
        'expiry_date', 'is_active', 'is_pinned', 'view_count',
        'read_count', 'created_by'
    ]
    list_filter = [
        'priority', 'is_active', 'is_pinned', 'target_audience',
        'require_acknowledgment', 'publish_date'
    ]
    search_fields = ['title', 'content', 'summary']
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'read_count', 'acknowledgment_rate']
    filter_horizontal = ['target_departments']
    date_hierarchy = 'publish_date'

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'summary')
        }),
        ('Priority & Visibility', {
            'fields': ('priority', 'is_active', 'is_pinned')
        }),
        ('Targeting', {
            'fields': ('target_audience', 'target_departments')
        }),
        ('Scheduling', {
            'fields': ('publish_date', 'expiry_date')
        }),
        ('Options', {
            'fields': ('attachment', 'require_acknowledgment')
        }),
        ('Metadata', {
            'fields': ('created_by', 'view_count', 'read_count', 'acknowledgment_rate', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [AnnouncementCommentInline]

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def priority_badge(self, obj):
        colors = {
            'low': 'secondary',
            'normal': 'info',
            'high': 'warning',
            'urgent': 'danger'
        }
        color = colors.get(obj.priority, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def read_count(self, obj):
        return obj.reads.count()
    read_count.short_description = 'Reads'

    def acknowledgment_rate(self, obj):
        total_reads = obj.reads.count()
        if total_reads == 0:
            return 'N/A'
        acknowledged = obj.reads.filter(acknowledged=True).count()
        rate = (acknowledged / total_reads) * 100
        return f"{rate:.1f}% ({acknowledged}/{total_reads})"
    acknowledgment_rate.short_description = 'Acknowledgment Rate'


@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'employee', 'read_at', 'acknowledged', 'acknowledged_at']
    list_filter = ['acknowledged', 'read_at']
    search_fields = ['announcement__title', 'employee__first_name', 'employee__last_name']
    readonly_fields = ['read_at', 'acknowledged_at']
    date_hierarchy = 'read_at'


@admin.register(AnnouncementComment)
class AnnouncementCommentAdmin(admin.ModelAdmin):
    list_display = ['announcement', 'employee', 'comment_preview', 'created_at']
    list_filter = ['created_at']
    search_fields = ['announcement__title', 'employee__first_name', 'employee__last_name', 'comment']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'
