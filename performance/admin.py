from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import PerformanceReview, Goal


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    """Admin interface for Performance Reviews"""
    list_display = [
        'employee', 'reviewer', 'review_period', 'review_date',
        'overall_rating', 'status', 'created_at'
    ]
    list_filter = ['status', 'review_period', 'review_date', 'overall_rating']
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'reviewer__username', 'reviewer__first_name', 'reviewer__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'review_date'

    fieldsets = (
        (_('Review Information'), {
            'fields': ('employee', 'reviewer', 'review_period', 'review_date',
                      'period_start', 'period_end', 'status')
        }),
        (_('Rating & Feedback'), {
            'fields': ('overall_rating', 'strengths', 'areas_for_improvement',
                      'goals_achieved', 'comments')
        }),
        (_('Metadata'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    """Admin interface for Goals"""
    list_display = [
        'employee', 'title', 'priority', 'status',
        'progress', 'target_date', 'created_at'
    ]
    list_filter = ['status', 'priority', 'target_date', 'created_at']
    search_fields = [
        'employee__first_name', 'employee__last_name',
        'title', 'description'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'target_date'

    fieldsets = (
        (_('Goal Information'), {
            'fields': ('employee', 'title', 'description', 'priority', 'status')
        }),
        (_('Timeline'), {
            'fields': ('start_date', 'target_date', 'completion_date', 'progress')
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
