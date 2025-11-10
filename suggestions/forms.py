from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Suggestion, SuggestionComment, SuggestionCategory
from hr.models import Department


class SuggestionForm(forms.ModelForm):
    """Form for employees to submit suggestions"""

    class Meta:
        model = Suggestion
        fields = [
            'title', 'category', 'suggestion_type', 'description',
            'expected_outcome', 'affected_department', 'attachment',
            'is_anonymous'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Brief title for your suggestion'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'suggestion_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Provide detailed description of your suggestion...'
            }),
            'expected_outcome': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What benefits or improvements do you expect from this suggestion?'
            }),
            'affected_department': forms.Select(attrs={
                'class': 'form-select'
            }),
            'attachment': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'is_anonymous': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        help_texts = {
            'is_anonymous': _('Your name will be hidden from other employees, but visible to management.')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter only active categories
        self.fields['category'].queryset = SuggestionCategory.objects.filter(is_active=True)
        # Make category optional
        self.fields['category'].required = False
        self.fields['affected_department'].required = False
        self.fields['expected_outcome'].required = False


class SuggestionResponseForm(forms.ModelForm):
    """Form for management to respond to suggestions"""

    class Meta:
        model = Suggestion
        fields = ['status', 'priority', 'assigned_to', 'response']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select'
            }),
            'assigned_to': forms.Select(attrs={
                'class': 'form-select'
            }),
            'response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Provide your response to this suggestion...'
            })
        }


class SuggestionImplementationForm(forms.ModelForm):
    """Form for tracking implementation details"""

    class Meta:
        model = Suggestion
        fields = [
            'implementation_notes', 'implementation_date',
            'estimated_cost', 'actual_cost'
        ]
        widgets = {
            'implementation_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'implementation_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'estimated_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            }),
            'actual_cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01'
            })
        }


class SuggestionCommentForm(forms.ModelForm):
    """Form for adding comments to suggestions"""

    class Meta:
        model = SuggestionComment
        fields = ['comment', 'is_internal']
        widgets = {
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add your comment...'
            }),
            'is_internal': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class SuggestionFilterForm(forms.Form):
    """Form for filtering suggestions"""
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + list(Suggestion.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    suggestion_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Suggestion.TYPE_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.ModelChoiceField(
        queryset=SuggestionCategory.objects.filter(is_active=True),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search suggestions...'
        })
    )
