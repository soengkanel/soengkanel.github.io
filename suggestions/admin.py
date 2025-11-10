from django.contrib import admin
from django.utils.html import format_html
from .models import (
    SuggestionCategory, Suggestion, SuggestionComment,
    SuggestionVote, SuggestionStatusHistory
)


@admin.register(SuggestionCategory)
class SuggestionCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'color', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']


class SuggestionCommentInline(admin.TabularInline):
    model = SuggestionComment
    extra = 0
    fields = ['user', 'comment', 'is_internal', 'created_at']
    readonly_fields = ['created_at']


class SuggestionStatusHistoryInline(admin.TabularInline):
    model = SuggestionStatusHistory
    extra = 0
    fields = ['old_status', 'new_status', 'changed_by', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'employee_name', 'suggestion_type', 'category',
        'status_badge', 'priority', 'submitted_date', 'days_open_display'
    ]
    list_filter = [
        'status', 'priority', 'suggestion_type', 'category',
        'is_anonymous', 'submitted_date'
    ]
    search_fields = [
        'title', 'description', 'employee__first_name',
        'employee__last_name', 'employee__employee_id'
    ]
    readonly_fields = [
        'submitted_date', 'created_at', 'updated_at',
        'days_open', 'views', 'upvotes'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'title', 'category', 'suggestion_type', 'is_anonymous')
        }),
        ('Content', {
            'fields': ('description', 'expected_outcome', 'affected_department', 'attachment')
        }),
        ('Status & Assignment', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Response', {
            'fields': ('response', 'response_by', 'response_date')
        }),
        ('Implementation', {
            'fields': (
                'implementation_notes', 'implementation_date',
                'estimated_cost', 'actual_cost'
            ),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('rating', 'upvotes', 'views', 'days_open'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'submitted_date', 'reviewed_date', 'closed_date',
                'created_at', 'updated_at'
            ),
            'classes': ('collapse',)
        }),
    )
    inlines = [SuggestionCommentInline, SuggestionStatusHistoryInline]
    date_hierarchy = 'submitted_date'

    def employee_name(self, obj):
        if obj.is_anonymous:
            return 'Anonymous'
        return obj.employee.get_full_name()
    employee_name.short_description = 'Employee'

    def status_badge(self, obj):
        colors = {
            'submitted': 'info',
            'under_review': 'primary',
            'approved': 'success',
            'implemented': 'success',
            'rejected': 'danger',
            'closed': 'secondary'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            f'var(--bs-{color})',
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    def days_open_display(self, obj):
        days = obj.days_open
        if days > 30:
            color = 'red'
        elif days > 14:
            color = 'orange'
        else:
            color = 'green'
        return format_html(
            '<span style="color: {};">{} days</span>',
            color,
            days
        )
    days_open_display.short_description = 'Days Open'


@admin.register(SuggestionComment)
class SuggestionCommentAdmin(admin.ModelAdmin):
    list_display = ['suggestion', 'user', 'comment_preview', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['comment', 'suggestion__title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']

    def comment_preview(self, obj):
        return obj.comment[:50] + '...' if len(obj.comment) > 50 else obj.comment
    comment_preview.short_description = 'Comment'


@admin.register(SuggestionVote)
class SuggestionVoteAdmin(admin.ModelAdmin):
    list_display = ['suggestion', 'employee', 'created_at']
    list_filter = ['created_at']
    search_fields = ['suggestion__title', 'employee__first_name', 'employee__last_name']
    readonly_fields = ['created_at']


@admin.register(SuggestionStatusHistory)
class SuggestionStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['suggestion', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['suggestion__title', 'changed_by__username']
    readonly_fields = ['created_at']
