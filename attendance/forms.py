from django import forms
from django.utils.translation import gettext_lazy as _
from .models import (
    AttendanceRecord, WorkSchedule, EmployeeSchedule,
    OvertimeRequest, AttendanceCorrection, BiometricDevice,
    BreakRecord
)
from hr.models import Employee


class AttendanceRecordForm(forms.ModelForm):
    """Form for manual attendance entry"""

    class Meta:
        model = AttendanceRecord
        fields = [
            'employee', 'date', 'current_project', 'clock_in', 'clock_out',
            'status', 'manual_entry_reason', 'notes'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'clock_in': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'clock_out': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'employee': forms.Select(attrs={'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'current_project': forms.Select(attrs={'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'status': forms.Select(attrs={'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'manual_entry_reason': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['manual_entry_reason'].required = True
        self.fields['manual_entry_reason'].help_text = _('Required for manual entries')

        # Make project field optional with searchable dropdown
        self.fields['current_project'].required = False
        self.fields['current_project'].label = _('Project')
        self.fields['current_project'].help_text = _('Optional - assign to a project')

        # Filter projects to show only active ones
        try:
            from project.models import Project
            self.fields['current_project'].queryset = Project.objects.exclude(
                status__in=['completed', 'cancelled']
            ).order_by('project_name')
        except Exception:
            pass


class WorkScheduleForm(forms.ModelForm):
    """Form for creating/editing work schedules"""

    class Meta:
        model = WorkSchedule
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),

            # Day schedules
            'monday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'monday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'tuesday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'tuesday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'wednesday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'wednesday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'thursday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'thursday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'friday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'friday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'saturday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'saturday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'sunday_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'sunday_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),

            # Break settings
            'break_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'break_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),

            # Flexibility settings
            'flexible_hours': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'core_hours_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'core_hours_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'required_hours_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),

            # Grace periods
            'late_grace_period': forms.NumberInput(attrs={'class': 'form-control'}),
            'early_leave_grace_period': forms.NumberInput(attrs={'class': 'form-control'}),

            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class EmployeeScheduleForm(forms.ModelForm):
    """Form for assigning schedules to employees"""

    class Meta:
        model = EmployeeSchedule
        fields = ['employee', 'schedule', 'effective_from', 'effective_to', 'is_active', 'notes']
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'schedule': forms.Select(attrs={'class': 'form-control'}),
            'effective_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'effective_to': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class OvertimeRequestForm(forms.ModelForm):
    """Form for overtime requests"""

    class Meta:
        model = OvertimeRequest
        fields = ['employee', 'project', 'date', 'start_time', 'end_time', 'hours', 'reason', 'overtime_rate']
        widgets = {
            'employee': forms.Select(attrs={'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'project': forms.Select(attrs={'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500'}),
            'hours': forms.NumberInput(attrs={'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'step': '0.5'}),
            'reason': forms.Textarea(attrs={'class': 'w-full px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'rows': 3}),
            'overtime_rate': forms.NumberInput(attrs={'class': 'w-full h-[38px] px-3 py-2 text-sm border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500', 'step': '0.25'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter projects to show only active ones
        from project.models import Project
        self.fields['project'].queryset = Project.objects.filter(
            status__in=['open', 'in_progress']
        ).order_by('project_name')
        self.fields['project'].required = False

        # Set default date to today if creating a new overtime request
        if not self.instance.pk:
            from datetime import date
            self.fields['date'].initial = date.today()

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if end_time <= start_time:
                raise forms.ValidationError(_('End time must be after start time'))

        return cleaned_data


class AttendanceCorrectionForm(forms.ModelForm):
    """Form for attendance correction requests"""

    class Meta:
        model = AttendanceCorrection
        fields = [
            'attendance', 'correction_type', 'new_clock_in', 'new_clock_out',
            'new_status', 'reason', 'supporting_document'
        ]
        widgets = {
            'attendance': forms.Select(attrs={'class': 'form-control'}),
            'correction_type': forms.Select(attrs={'class': 'form-control'}),
            'new_clock_in': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'new_clock_out': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'new_status': forms.Select(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'supporting_document': forms.FileInput(attrs={'class': 'form-control'}),
        }


class BiometricDeviceForm(forms.ModelForm):
    """Form for biometric device management"""

    class Meta:
        model = BiometricDevice
        fields = [
            'device_id', 'name', 'device_type', 'location',
            'ip_address', 'port', 'serial_number', 'firmware_version', 'status'
        ]
        widgets = {
            'device_id': forms.TextInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'device_type': forms.Select(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'ip_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '192.168.1.100'}),
            'port': forms.NumberInput(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
            'firmware_version': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class BreakRecordForm(forms.ModelForm):
    """Form for recording breaks"""

    class Meta:
        model = BreakRecord
        fields = ['attendance', 'break_type', 'start_time', 'end_time', 'notes']
        widgets = {
            'attendance': forms.Select(attrs={'class': 'form-control'}),
            'break_type': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class AttendanceReportForm(forms.Form):
    """Form for generating attendance reports"""

    REPORT_TYPES = [
        ('daily', _('Daily Report')),
        ('weekly', _('Weekly Report')),
        ('monthly', _('Monthly Report')),
        ('custom', _('Custom Range')),
    ]

    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Leave empty for all employees')
    )

    department = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Filter by department')
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    include_overtime = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('Include Overtime Details')
    )

    include_breaks = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label=_('Include Break Details')
    )

    export_format = forms.ChoiceField(
        choices=[
            ('pdf', 'PDF'),
            ('excel', 'Excel'),
            ('csv', 'CSV'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )