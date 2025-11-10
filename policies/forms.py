from django import forms
from leave.models import LeavePolicy
from attendance.models import AttendancePolicy
from hr.models import OvertimePolicy
from hr.payroll_models import PayrollPolicy
from expenses.models import ExpensePolicy


class LeavePolicyForm(forms.ModelForm):
    """Form for Leave Policy"""
    class Meta:
        model = LeavePolicy
        fields = [
            'name', 'description', 'min_employment_months',
            'applicable_to_probation', 'requires_approval',
            'auto_approve_half_day', 'max_days_auto_approve',
            'include_regional_holidays', 'regional_holiday_list',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter policy name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'min_employment_months': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_days_auto_approve': forms.NumberInput(attrs={'class': 'form-control'}),
            'regional_holiday_list': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'JSON format'}),
            'applicable_to_probation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_approve_half_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'include_regional_holidays': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AttendancePolicyForm(forms.ModelForm):
    """Form for Attendance Policy"""
    class Meta:
        model = AttendancePolicy
        fields = [
            'name', 'code', 'description',
            'late_deduction_per_minute', 'max_late_minutes_per_month', 'late_penalty_amount',
            'absence_deduction_per_day', 'max_absences_per_month',
            'overtime_rate_regular', 'overtime_rate_holiday', 'min_overtime_minutes',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'late_deduction_per_minute': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_late_minutes_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'late_penalty_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'absence_deduction_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_absences_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'overtime_rate_regular': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'overtime_rate_holiday': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'min_overtime_minutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class OvertimePolicyForm(forms.ModelForm):
    """Form for Overtime Policy"""
    class Meta:
        model = OvertimePolicy
        fields = [
            'name', 'description',
            'departments', 'positions', 'employees',
            'daily_threshold_hours', 'weekly_threshold_hours',
            'requires_pre_approval', 'auto_calculate',
            'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'departments': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'positions': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'employees': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'daily_threshold_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'weekly_threshold_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'requires_pre_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'auto_calculate': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PayrollPolicyForm(forms.ModelForm):
    """Form for Payroll Policy"""
    class Meta:
        model = PayrollPolicy
        fields = [
            'name', 'description', 'calculation_method', 'currency',
            'standard_working_hours_per_day', 'standard_working_days_per_month',
            'tax_calculation_method', 'social_security_rate', 'health_insurance_rate',
            'integrate_overtime', 'integrate_timecards',
            'deduct_unpaid_leave', 'deduct_half_day_leave',
            'allow_performance_bonus', 'allow_project_bonus',
            'is_active', 'effective_date', 'end_date'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'calculation_method': forms.Select(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'standard_working_hours_per_day': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'standard_working_days_per_month': forms.NumberInput(attrs={'class': 'form-control'}),
            'tax_calculation_method': forms.Select(attrs={'class': 'form-control'}),
            'social_security_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'health_insurance_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'integrate_overtime': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'integrate_timecards': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'deduct_unpaid_leave': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'deduct_half_day_leave': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_performance_bonus': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_project_bonus': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ExpensePolicyForm(forms.ModelForm):
    """Form for Expense Policy"""
    class Meta:
        model = ExpensePolicy
        fields = [
            'name', 'description',
            'applies_to_all_employees', 'applicable_positions', 'applicable_departments',
            'max_amount_per_claim', 'max_amount_per_month', 'max_amount_per_year',
            'auto_approve_limit', 'requires_manager_approval', 'requires_finance_approval',
            'finance_approval_limit', 'receipt_required', 'receipt_required_above',
            'claim_deadline_days', 'is_active'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'applicable_positions': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'applicable_departments': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'max_amount_per_claim': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_amount_per_month': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_amount_per_year': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'auto_approve_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'finance_approval_limit': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'receipt_required_above': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'claim_deadline_days': forms.NumberInput(attrs={'class': 'form-control'}),
            'applies_to_all_employees': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_manager_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'requires_finance_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'receipt_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
