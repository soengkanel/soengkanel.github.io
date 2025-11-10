from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Announcement, AnnouncementComment


class AnnouncementForm(forms.ModelForm):
    """Form for creating and editing announcements"""

    class Meta:
        model = Announcement
        fields = [
            'title', 'content', 'summary', 'priority', 'is_active', 'is_pinned',
            'target_audience', 'target_departments', 'publish_date', 'expiry_date',
            'attachment', 'require_acknowledgment'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter announcement title'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 8,
                'placeholder': 'Enter announcement content...'
            }),
            'summary': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief summary (optional - auto-generated if empty)'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_pinned': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'target_audience': forms.Select(attrs={
                'class': 'form-select'
            }),
            'target_departments': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '5'
            }),
            'publish_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'expiry_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }, format='%Y-%m-%dT%H:%M'),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'require_acknowledgment': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set input formats for datetime fields
        self.fields['publish_date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['expiry_date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['expiry_date'].required = False


class AnnouncementCommentForm(forms.ModelForm):
    """Form for adding comments to announcements"""

    class Meta:
        model = AnnouncementComment
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add your comment...'
            })
        }


class AnnouncementFilterForm(forms.Form):
    """Form for filtering announcements"""

    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + list(Announcement.PRIORITY_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Search announcements...'
        })
    )
