from django import forms
from django.utils.translation import gettext_lazy as _
from .models import JobPosting, Application


class JobPostingForm(forms.ModelForm):
    """Form for creating and editing job postings"""
    class Meta:
        model = JobPosting
        fields = ['title', 'department', 'position', 'description', 'requirements',
                  'vacancies', 'status', 'posted_date', 'closing_date']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Job Title')}),
            'department': forms.Select(attrs={'class': 'form-control'}),
            'position': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Job Description')}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Job Requirements')}),
            'vacancies': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'posted_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'closing_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class ApplicationForm(forms.Form):
    """Form for job application"""
    first_name = forms.CharField(
        label=_('First Name'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('First Name')})
    )
    last_name = forms.CharField(
        label=_('Last Name'),
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Last Name')})
    )
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Email')})
    )
    phone = forms.CharField(
        label=_('Phone'),
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Phone')})
    )
    resume = forms.FileField(
        label=_('Resume'),
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'})
    )
    cover_letter = forms.CharField(
        label=_('Cover Letter'),
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': _('Cover Letter')})
    )
