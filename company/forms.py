from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import Branch


class BranchForm(forms.ModelForm):
    """Form for creating and updating branches."""

    class Meta:
        model = Branch
        fields = [
            'name', 'code', 'description', 'address', 'city',
            'state_province', 'postal_code', 'country',
            'phone_number', 'email', 'manager_name', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter branch name'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unique branch code'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter branch description (optional)'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter branch address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'}),
            'state_province': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter state/province'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter postal code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'value': 'Cambodia'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+85581123456'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'branch@example.com'}),
            'manager_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter branch manager name'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set default country to Cambodia for new branches
        if not self.instance.pk:
            self.fields['country'].initial = 'Cambodia'
            self.fields['is_active'].initial = True

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Check if code exists for other branches
            branch_qs = Branch.objects.filter(code=code)
            if self.instance and self.instance.pk:
                branch_qs = branch_qs.exclude(pk=self.instance.pk)
            if branch_qs.exists():
                raise ValidationError(_('Branch code already exists.'))
        return code
