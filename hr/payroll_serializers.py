# Payroll serializers for NextHR Django application
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime
import json

from .payroll_models import (
    PayrollPolicy, PayrollPeriod, PayrollComponent, TaxSlab,
    EmployeeSalary, EmployeeSalaryComponent, PayrollRun, PayrollEntry,
    PaySlip, SalaryAdvance, SalaryAdvanceRecovery, YearEndStatement
)
from .models import Employee, Department, Position
from .serializers import EmployeeMinimalSerializer, DepartmentSerializer, PositionSerializer


class PayrollPolicySerializer(serializers.ModelSerializer):
    """Serializer for PayrollPolicy model"""

    class Meta:
        model = PayrollPolicy
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        """Validate payroll policy data"""
        # Ensure end_date is after effective_date if provided
        if data.get('end_date') and data.get('effective_date'):
            if data['end_date'] <= data['effective_date']:
                raise serializers.ValidationError(
                    "End date must be after effective date"
                )

        # Validate percentage values
        percentage_fields = ['social_security_rate', 'health_insurance_rate']
        for field in percentage_fields:
            if field in data and (data[field] < 0 or data[field] > 100):
                raise serializers.ValidationError(
                    f"{field} must be between 0 and 100"
                )

        # Validate working hours
        if data.get('standard_working_hours_per_day', 0) <= 0:
            raise serializers.ValidationError(
                "Standard working hours per day must be greater than 0"
            )

        if data.get('standard_working_days_per_month', 0) <= 0:
            raise serializers.ValidationError(
                "Standard working days per month must be greater than 0"
            )

        return data


class TaxSlabSerializer(serializers.ModelSerializer):
    """Serializer for TaxSlab model"""

    class Meta:
        model = TaxSlab
        fields = '__all__'
        read_only_fields = ('created_at',)

    def validate(self, data):
        """Validate tax slab data"""
        # Ensure max_amount is greater than min_amount if provided
        if data.get('max_amount') and data.get('min_amount'):
            if data['max_amount'] <= data['min_amount']:
                raise serializers.ValidationError(
                    "Maximum amount must be greater than minimum amount"
                )

        # Validate tax rate
        if data.get('tax_rate', 0) < 0 or data.get('tax_rate', 0) > 100:
            raise serializers.ValidationError(
                "Tax rate must be between 0 and 100"
            )

        return data


class PayrollPolicyDetailSerializer(PayrollPolicySerializer):
    """Detailed serializer for PayrollPolicy with related data"""
    tax_slabs = TaxSlabSerializer(many=True, read_only=True)

    class Meta(PayrollPolicySerializer.Meta):
        pass


class PayrollPeriodSerializer(serializers.ModelSerializer):
    """Serializer for PayrollPeriod model"""
    payroll_policy_name = serializers.CharField(source='payroll_policy.name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    is_current = serializers.BooleanField(read_only=True)
    working_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = PayrollPeriod
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'processed_at')

    def validate(self, data):
        """Validate payroll period data"""
        # Ensure end_date is after start_date
        if data.get('end_date') and data.get('start_date'):
            if data['end_date'] <= data['start_date']:
                raise serializers.ValidationError(
                    "End date must be after start date"
                )

        # Ensure pay_date is not before end_date
        if data.get('pay_date') and data.get('end_date'):
            if data['pay_date'] < data['end_date']:
                raise serializers.ValidationError(
                    "Pay date should not be before period end date"
                )

        return data


class PayrollComponentSerializer(serializers.ModelSerializer):
    """Serializer for PayrollComponent model"""
    departments = DepartmentSerializer(many=True, read_only=True)
    positions = PositionSerializer(many=True, read_only=True)

    class Meta:
        model = PayrollComponent
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        """Validate payroll component data"""
        calculation_type = data.get('calculation_type')

        # Validate based on calculation type
        if calculation_type == 'fixed':
            if not data.get('default_amount'):
                raise serializers.ValidationError(
                    "Default amount is required for fixed calculation type"
                )

        elif calculation_type in ['percentage', 'percentage_gross']:
            if not data.get('percentage_value'):
                raise serializers.ValidationError(
                    f"Percentage value is required for {calculation_type} calculation type"
                )
            if data.get('percentage_value', 0) < 0 or data.get('percentage_value', 0) > 100:
                raise serializers.ValidationError(
                    "Percentage value must be between 0 and 100"
                )

        elif calculation_type == 'formula':
            if not data.get('calculation_formula'):
                raise serializers.ValidationError(
                    "Calculation formula is required for formula calculation type"
                )

        # Validate min/max amounts
        if data.get('max_amount') and data.get('min_amount'):
            if data['max_amount'] <= data['min_amount']:
                raise serializers.ValidationError(
                    "Maximum amount must be greater than minimum amount"
                )

        return data


class EmployeeSalarySerializer(serializers.ModelSerializer):
    """Serializer for EmployeeSalary model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    payroll_policy_name = serializers.CharField(source='payroll_policy.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    is_current = serializers.BooleanField(read_only=True)

    class Meta:
        model = EmployeeSalary
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'approved_at')

    def validate(self, data):
        """Validate employee salary data"""
        # Ensure basic_salary is positive
        if data.get('basic_salary', 0) <= 0:
            raise serializers.ValidationError(
                "Basic salary must be greater than 0"
            )

        # Ensure end_date is after effective_date if provided
        if data.get('end_date') and data.get('effective_date'):
            if data['end_date'] <= data['effective_date']:
                raise serializers.ValidationError(
                    "End date must be after effective date"
                )

        # Check for overlapping salary structures for the same employee
        employee = data.get('employee')
        effective_date = data.get('effective_date')
        end_date = data.get('end_date')

        if employee and effective_date:
            from django.db import models as django_models
            overlapping = EmployeeSalary.objects.filter(
                employee=employee,
                effective_date__lte=effective_date,
                is_active=True
            )

            if end_date:
                overlapping = overlapping.filter(
                    django_models.Q(end_date__isnull=True) | django_models.Q(end_date__gte=effective_date)
                )
            else:
                overlapping = overlapping.filter(end_date__isnull=True)

            # Exclude current instance if updating
            if self.instance:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise serializers.ValidationError(
                    "Employee already has an active salary structure for this period"
                )

        return data


class EmployeeSalaryComponentSerializer(serializers.ModelSerializer):
    """Serializer for EmployeeSalaryComponent model"""
    component_name = serializers.CharField(source='payroll_component.name', read_only=True)
    component_type = serializers.CharField(source='payroll_component.component_type', read_only=True)
    component_code = serializers.CharField(source='payroll_component.code', read_only=True)
    calculated_amount = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalaryComponent
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def get_calculated_amount(self, obj):
        """Get calculated amount for this component"""
        if obj.employee_salary:
            basic_salary = obj.employee_salary.basic_salary
            # For gross salary calculation, we'd need to sum up all earning components
            # This is a simplified version
            gross_salary = basic_salary * Decimal('1.3')  # Assume 30% additional earnings
            return float(obj.get_calculated_amount(basic_salary, gross_salary))
        return 0


class EmployeeSalaryDetailSerializer(EmployeeSalarySerializer):
    """Detailed serializer for EmployeeSalary with components"""
    components = EmployeeSalaryComponentSerializer(many=True, read_only=True)
    employee = EmployeeMinimalSerializer(read_only=True)

    class Meta(EmployeeSalarySerializer.Meta):
        pass


class PayrollRunSerializer(serializers.ModelSerializer):
    """Serializer for PayrollRun model"""
    payroll_period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    processed_by_name = serializers.CharField(source='processed_by.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    departments = DepartmentSerializer(many=True, read_only=True)
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = PayrollRun
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'run_date', 'processing_started_at',
                          'processing_completed_at', 'approved_at')

    def get_employees_count(self, obj):
        """Get count of employees to be processed"""
        if obj.employees.exists():
            return obj.employees.count()
        elif obj.departments.exists():
            return Employee.objects.filter(department__in=obj.departments.all()).count()
        else:
            return Employee.objects.filter(employment_status='active').count()


class PayrollEntrySerializer(serializers.ModelSerializer):
    """Serializer for PayrollEntry model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    department_name = serializers.CharField(source='employee.department.name', read_only=True)
    position_name = serializers.CharField(source='employee.position.name', read_only=True)
    payroll_period_name = serializers.CharField(source='payroll_run.payroll_period.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

    class Meta:
        model = PayrollEntry
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'calculation_date', 'approved_at', 'paid_at')


class PayrollEntryDetailSerializer(PayrollEntrySerializer):
    """Detailed serializer for PayrollEntry with calculation breakdown"""
    employee = EmployeeMinimalSerializer(read_only=True)
    calculation_breakdown = serializers.SerializerMethodField()

    class Meta(PayrollEntrySerializer.Meta):
        pass

    def get_calculation_breakdown(self, obj):
        """Get detailed calculation breakdown"""
        return obj.calculation_details


class PaySlipSerializer(serializers.ModelSerializer):
    """Serializer for PaySlip model"""
    employee_name = serializers.CharField(source='payroll_entry.employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='payroll_entry.employee.employee_id', read_only=True)
    payroll_period = serializers.CharField(source='payroll_entry.payroll_run.payroll_period.name', read_only=True)
    net_salary = serializers.CharField(source='payroll_entry.net_salary', read_only=True)

    class Meta:
        model = PaySlip
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'generation_date', 'payslip_number',
                          'pdf_generated_at', 'sent_at', 'viewed_at')


class PaySlipDetailSerializer(PaySlipSerializer):
    """Detailed serializer for PaySlip with payroll entry details"""
    payroll_entry = PayrollEntryDetailSerializer(read_only=True)

    class Meta(PaySlipSerializer.Meta):
        pass


class SalaryAdvanceSerializer(serializers.ModelSerializer):
    """Serializer for SalaryAdvance model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)
    recovery_progress = serializers.SerializerMethodField()

    class Meta:
        model = SalaryAdvance
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'request_date', 'approved_at',
                          'paid_at', 'total_recovered', 'balance_amount', 'installment_amount')

    def get_recovery_progress(self, obj):
        """Get recovery progress percentage"""
        if obj.advance_amount > 0:
            return round((obj.total_recovered / obj.advance_amount) * 100, 2)
        return 0

    def validate(self, data):
        """Validate salary advance data"""
        # Ensure advance_amount is positive
        if data.get('advance_amount', 0) <= 0:
            raise serializers.ValidationError(
                "Advance amount must be greater than 0"
            )

        # Ensure installments is positive
        if data.get('installments', 0) <= 0:
            raise serializers.ValidationError(
                "Number of installments must be greater than 0"
            )

        # Validate recovery start month is in the future
        if data.get('recovery_start_month'):
            if data['recovery_start_month'] <= date.today():
                raise serializers.ValidationError(
                    "Recovery start month should be in the future"
                )

        return data


class SalaryAdvanceRecoverySerializer(serializers.ModelSerializer):
    """Serializer for SalaryAdvanceRecovery model"""
    employee_name = serializers.CharField(source='salary_advance.employee.full_name', read_only=True)
    payroll_period = serializers.CharField(source='payroll_entry.payroll_run.payroll_period.name', read_only=True)

    class Meta:
        model = SalaryAdvanceRecovery
        fields = '__all__'
        read_only_fields = ('created_at', 'recovery_date')


class SalaryAdvanceDetailSerializer(SalaryAdvanceSerializer):
    """Detailed serializer for SalaryAdvance with recoveries"""
    recoveries = SalaryAdvanceRecoverySerializer(many=True, read_only=True)
    employee = EmployeeMinimalSerializer(read_only=True)

    class Meta(SalaryAdvanceSerializer.Meta):
        pass


class YearEndStatementSerializer(serializers.ModelSerializer):
    """Serializer for YearEndStatement model"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)

    class Meta:
        model = YearEndStatement
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at', 'statement_date', 'pdf_generated_at')

    def validate(self, data):
        """Validate year-end statement data"""
        # Validate financial year format
        financial_year = data.get('financial_year', '')
        if financial_year:
            try:
                years = financial_year.split('-')
                if len(years) != 2:
                    raise ValueError
                start_year = int(years[0])
                end_year = int(years[1])
                if end_year != start_year + 1:
                    raise ValueError
            except (ValueError, IndexError):
                raise serializers.ValidationError(
                    "Financial year must be in format 'YYYY-YYYY' (e.g., '2024-2025')"
                )

        return data


class YearEndStatementDetailSerializer(YearEndStatementSerializer):
    """Detailed serializer for YearEndStatement with breakdown"""
    employee = EmployeeMinimalSerializer(read_only=True)
    monthly_breakdown = serializers.SerializerMethodField()

    class Meta(YearEndStatementSerializer.Meta):
        pass

    def get_monthly_breakdown(self, obj):
        """Get monthly breakdown from annual_breakdown JSON"""
        return obj.annual_breakdown.get('monthly_breakdown', [])


# Calculation and Processing Serializers

class PayrollCalculationSerializer(serializers.Serializer):
    """Serializer for payroll calculation preview"""
    payroll_period_id = serializers.IntegerField()
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Optional list of employee IDs. If not provided, all active employees will be processed."
    )
    department_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Optional list of department IDs to filter employees."
    )

    def validate_payroll_period_id(self, value):
        """Validate payroll period exists"""
        try:
            PayrollPeriod.objects.get(id=value)
        except PayrollPeriod.DoesNotExist:
            raise serializers.ValidationError("Payroll period does not exist")
        return value

    def validate_employee_ids(self, value):
        """Validate employee IDs exist"""
        if value:
            existing_ids = set(Employee.objects.filter(id__in=value).values_list('id', flat=True))
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(f"Invalid employee IDs: {list(invalid_ids)}")
        return value

    def validate_department_ids(self, value):
        """Validate department IDs exist"""
        if value:
            existing_ids = set(Department.objects.filter(id__in=value).values_list('id', flat=True))
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(f"Invalid department IDs: {list(invalid_ids)}")
        return value


class PayrollApprovalSerializer(serializers.Serializer):
    """Serializer for payroll approval"""
    payroll_run_id = serializers.IntegerField()
    entry_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Optional list of payroll entry IDs to approve. If not provided, all entries will be approved."
    )
    approval_comments = serializers.CharField(max_length=500, required=False)

    def validate_payroll_run_id(self, value):
        """Validate payroll run exists and can be approved"""
        try:
            payroll_run = PayrollRun.objects.get(id=value)
            if payroll_run.status != 'calculated':
                raise serializers.ValidationError(
                    "Payroll run must be in 'calculated' status to be approved"
                )
        except PayrollRun.DoesNotExist:
            raise serializers.ValidationError("Payroll run does not exist")
        return value

    def validate_entry_ids(self, value):
        """Validate payroll entry IDs exist"""
        if value:
            existing_ids = set(PayrollEntry.objects.filter(id__in=value).values_list('id', flat=True))
            invalid_ids = set(value) - existing_ids
            if invalid_ids:
                raise serializers.ValidationError(f"Invalid payroll entry IDs: {list(invalid_ids)}")
        return value


class PayslipGenerationSerializer(serializers.Serializer):
    """Serializer for payslip generation"""
    payroll_run_id = serializers.IntegerField()
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Optional list of employee IDs. If not provided, payslips for all employees will be generated."
    )
    send_email = serializers.BooleanField(default=False)
    email_template = serializers.CharField(max_length=100, required=False)

    def validate_payroll_run_id(self, value):
        """Validate payroll run exists and is approved"""
        try:
            payroll_run = PayrollRun.objects.get(id=value)
            if payroll_run.status != 'approved':
                raise serializers.ValidationError(
                    "Payroll run must be approved before generating payslips"
                )
        except PayrollRun.DoesNotExist:
            raise serializers.ValidationError("Payroll run does not exist")
        return value


class PayrollReportSerializer(serializers.Serializer):
    """Serializer for payroll reports"""
    REPORT_TYPE_CHOICES = [
        ('summary', 'Payroll Summary'),
        ('detailed', 'Detailed Payroll Report'),
        ('tax_summary', 'Tax Summary Report'),
        ('department_wise', 'Department-wise Report'),
        ('employee_wise', 'Employee-wise Report'),
        ('component_wise', 'Component-wise Report'),
    ]

    report_type = serializers.ChoiceField(choices=REPORT_TYPE_CHOICES)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    department_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    employee_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    include_drafts = serializers.BooleanField(default=False)
    export_format = serializers.ChoiceField(
        choices=[('json', 'JSON'), ('excel', 'Excel'), ('pdf', 'PDF')],
        default='json'
    )

    def validate(self, data):
        """Validate report parameters"""
        if data['end_date'] <= data['start_date']:
            raise serializers.ValidationError(
                "End date must be after start date"
            )
        return data


# Bulk operation serializers

class BulkSalaryUpdateSerializer(serializers.Serializer):
    """Serializer for bulk salary updates"""
    employee_ids = serializers.ListField(child=serializers.IntegerField())
    salary_increase_percentage = serializers.DecimalField(
        max_digits=5, decimal_places=2, required=False
    )
    salary_increase_amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False
    )
    effective_date = serializers.DateField()
    revision_reason = serializers.CharField(max_length=200)

    def validate(self, data):
        """Validate bulk salary update data"""
        if not data.get('salary_increase_percentage') and not data.get('salary_increase_amount'):
            raise serializers.ValidationError(
                "Either salary_increase_percentage or salary_increase_amount must be provided"
            )

        if data.get('salary_increase_percentage') and data.get('salary_increase_amount'):
            raise serializers.ValidationError(
                "Provide either salary_increase_percentage or salary_increase_amount, not both"
            )

        # Validate employee IDs
        employee_ids = data['employee_ids']
        existing_ids = set(Employee.objects.filter(id__in=employee_ids).values_list('id', flat=True))
        invalid_ids = set(employee_ids) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(f"Invalid employee IDs: {list(invalid_ids)}")

        return data