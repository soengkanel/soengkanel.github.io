from django import forms
from django.utils.translation import gettext_lazy as _
from .models import PerformanceReview, Goal


class PerformanceReviewForm(forms.ModelForm):
    """Form for creating and editing performance reviews"""

    class Meta:
        model = PerformanceReview
        fields = [
            'employee', 'review_period', 'review_date',
            'period_start', 'period_end', 'overall_rating',
            'strengths', 'areas_for_improvement', 'goals_achieved',
            'comments', 'status'
        ]
        widgets = {
            'review_date': forms.DateInput(attrs={'type': 'date'}),
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
            'strengths': forms.Textarea(attrs={'rows': 4}),
            'areas_for_improvement': forms.Textarea(attrs={'rows': 4}),
            'goals_achieved': forms.Textarea(attrs={'rows': 4}),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }


class GoalForm(forms.ModelForm):
    """Form for creating and editing goals"""

    class Meta:
        model = Goal
        fields = [
            'employee', 'title', 'description', 'priority',
            'status', 'start_date', 'target_date',
            'completion_date', 'progress'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'completion_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
