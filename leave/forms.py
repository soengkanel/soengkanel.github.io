from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    LeaveType, LeavePolicy, LeaveAllocation,
    LeaveApplication, Holiday, CompensatoryLeaveRequest
)


class LeaveTypeForm(forms.ModelForm):
    """Form for creating/editing leave types"""
    class Meta:
        model = LeaveType
        fields = [
            'name', 'code', 'max_days_per_year', 'carry_forward_allowed',
            'max_carry_forward_days', 'encashment_allowed', 'include_holiday',
            'is_paid', 'apply_in_advance_days', 'maximum_continuous_days',
            'minimum_continuous_days', 'medical_certificate_required',
            'medical_certificate_min_days', 'color', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Annual Leave'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., AL'}),
            'max_days_per_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_carry_forward_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'apply_in_advance_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'maximum_continuous_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'minimum_continuous_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'medical_certificate_min_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class LeaveApplicationForm(forms.ModelForm):
    """Form for submitting leave applications"""

    def __init__(self, *args, **kwargs):
        # Accept user parameter to determine if employee field should be excluded
        self.user = kwargs.pop('user', None)
        self.is_basic_user = False

        super().__init__(*args, **kwargs)

        # If user is provided and has User role, remove employee field completely
        if self.user:
            try:
                from user_management.models import UserRoleAssignment
                role_assignment = UserRoleAssignment.objects.get(
                    user=self.user,
                    is_active=True
                )
                if role_assignment.role.name == "User":
                    self.is_basic_user = True
                    # Remove employee field for basic users - it will be auto-assigned
                    if 'employee' in self.fields:
                        del self.fields['employee']
            except:
                pass

    def clean(self):
        cleaned_data = super().clean()

        # For basic users, add employee to cleaned_data
        if self.is_basic_user and self.user:
            try:
                from hr.models import Employee
                employee = Employee.objects.get(user=self.user)
                cleaned_data['employee'] = employee
            except Employee.DoesNotExist:
                raise forms.ValidationError('Employee profile not found. Please contact HR.')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # If basic user and employee not set, get from cleaned_data or user
        if self.is_basic_user and not instance.employee_id:
            if 'employee' in self.cleaned_data:
                instance.employee = self.cleaned_data['employee']
            elif self.user and hasattr(self.user, 'employee'):
                instance.employee = self.user.employee

        if commit:
            instance.save()
        return instance

    class Meta:
        model = LeaveApplication
        fields = [
            'employee', 'leave_type', 'from_date', 'to_date',
            'half_day', 'half_day_date', 'leave_session',
            'reason', 'supporting_document', 'medical_certificate'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'half_day_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'leave_session': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for leave...'}),
            'supporting_document': forms.FileInput(attrs={'class': 'form-control'}),
            'medical_certificate': forms.FileInput(attrs={'class': 'form-control'}),
        }


class LeaveAllocationForm(forms.ModelForm):
    """Form for allocating leave to employees"""
    class Meta:
        model = LeaveAllocation
        fields = [
            'employee', 'leave_type', 'year', 'allocated_days',
            'carried_forward', 'from_date', 'to_date'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'leave_type': forms.Select(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'allocated_days': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'carried_forward': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'from_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'to_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class HolidayForm(forms.ModelForm):
    """Form for managing holidays"""
    # Additional fields for date range
    use_date_range = forms.BooleanField(
        required=False,
        initial=False,
        label='Use Date Range',
        help_text='Create multiple holidays for a date range'
    )
    from_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='From Date'
    )
    to_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='To Date'
    )

    class Meta:
        model = Holiday
        fields = ['name', 'date', 'year', 'is_optional', 'description', 'applies_to_all', 'regions']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Holiday name'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'regions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., North, South, East'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        use_date_range = cleaned_data.get('use_date_range')
        date = cleaned_data.get('date')
        from_date = cleaned_data.get('from_date')
        to_date = cleaned_data.get('to_date')

        if use_date_range:
            if not from_date or not to_date:
                raise forms.ValidationError('Both From Date and To Date are required when using date range.')
            if from_date > to_date:
                raise forms.ValidationError('From Date must be before or equal to To Date.')
        else:
            if not date:
                raise forms.ValidationError('Date is required when not using date range.')

        return cleaned_data


class LeaveApprovalForm(forms.ModelForm):
    """Form for approving/rejecting leave applications"""
    class Meta:
        model = LeaveApplication
        fields = ['status', 'rejection_reason']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'rejection_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
