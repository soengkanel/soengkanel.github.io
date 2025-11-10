from rest_framework import serializers
from .models import (
    PayrollPeriod, SalaryComponent, SalaryStructure, SalaryStructureAssignment,
    SalarySlip, SalarySlipDetail, SalaryAdvance, EmployeeLoan, EmployeeSalary
)
from hr.models import Employee


class PayrollPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayrollPeriod
        fields = '__all__'
        read_only_fields = ('created_by', 'approved_by')

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class SalaryComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryComponent
        fields = '__all__'


class SalaryStructureSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalaryStructure
        fields = '__all__'


class EmployeeSalarySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)

    class Meta:
        model = EmployeeSalary
        fields = '__all__'


class SalaryStructureAssignmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    salary_structure_name = serializers.CharField(source='salary_structure.name', read_only=True)

    class Meta:
        model = SalaryStructureAssignment
        fields = '__all__'


class SalarySlipDetailSerializer(serializers.ModelSerializer):
    component_name = serializers.CharField(source='salary_component.name', read_only=True)
    component_type = serializers.CharField(source='salary_component.component_type', read_only=True)

    class Meta:
        model = SalarySlipDetail
        fields = '__all__'


class SalarySlipSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    period_name = serializers.CharField(source='payroll_period.name', read_only=True)
    earnings = SalarySlipDetailSerializer(source='details', many=True, read_only=True)
    deductions = SalarySlipDetailSerializer(source='details', many=True, read_only=True)

    class Meta:
        model = SalarySlip
        fields = '__all__'
        read_only_fields = ('created_by', 'approved_by')

    def get_earnings(self, obj):
        earnings = obj.details.filter(salary_component__component_type='EARNING')
        return SalarySlipDetailSerializer(earnings, many=True).data

    def get_deductions(self, obj):
        deductions = obj.details.filter(salary_component__component_type='DEDUCTION')
        return SalarySlipDetailSerializer(deductions, many=True).data


class SalaryAdvanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)
    advance_amount = serializers.DecimalField(source='amount', max_digits=10, decimal_places=2)
    posting_date = serializers.DateField(source='request_date')
    purpose = serializers.CharField(source='reason')

    class Meta:
        model = SalaryAdvance
        fields = [
            'id', 'employee', 'employee_name', 'advance_amount', 'posting_date',
            'approval_date', 'repayment_method', 'installment_months',
            'status', 'purpose', 'remarks', 'requested_by', 'approved_by',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('requested_by', 'approved_by')

    def create(self, validated_data):
        validated_data['requested_by'] = self.context['request'].user
        return super().create(validated_data)


class EmployeeLoanSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True)

    class Meta:
        model = EmployeeLoan
        fields = '__all__'
        read_only_fields = ('requested_by', 'approved_by')

    def create(self, validated_data):
        validated_data['requested_by'] = self.context['request'].user
        # Calculate monthly installment
        loan = EmployeeLoan(**validated_data)
        validated_data['monthly_installment'] = loan.calculate_monthly_installment()
        validated_data['remaining_balance'] = validated_data['loan_amount']
        return super().create(validated_data)