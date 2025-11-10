from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    Employee, Department, Position, EmployeeDocument, EmployeeHistory,
    OvertimePolicy, OvertimeClaim, OvertimeApproval, OvertimeReport
)
from django.db import transaction
from decimal import Decimal


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'parent', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Position
        fields = ['id', 'name', 'code', 'department', 'department_name', 'description', 'level', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class EmployeeListSerializer(serializers.ModelSerializer):
    """Serializer for employee list view with minimal data"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    full_name = serializers.ReadOnlyField()
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'first_name', 'last_name', 'full_name',
            'email', 'phone_number', 'department', 'department_name',
            'position', 'position_name', 'employment_status', 'employee_type',
            'hire_date', 'manager', 'manager_name', 'work_location', 'branch', 'created_at'
        ]
        read_only_fields = ['employee_id', 'created_at', 'full_name']


class EmployeeDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single employee view"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    position_name = serializers.CharField(source='position.name', read_only=True)
    full_name = serializers.ReadOnlyField()
    manager_name = serializers.CharField(source='manager.full_name', read_only=True)
    photo_url = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'user', 'first_name', 'last_name', 'full_name',
            'photo', 'photo_url', 'gender', 'date_of_birth', 'nationality',
            'phone_number', 'email', 'address', 'emergency_contact_name',
            'emergency_contact_phone', 'department', 'department_name',
            'position', 'position_name', 'employment_status', 'employee_type',
            'hire_date', 'end_date', 'manager', 'manager_name', 'salary', 'work_location',
            'branch', 'notes', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['employee_id', 'created_at', 'updated_at', 'full_name', 'photo_url', 'is_active']


class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating employees"""

    class Meta:
        model = Employee
        fields = [
            'id', 'first_name', 'last_name', 'photo', 'gender', 'date_of_birth',
            'nationality', 'phone_number', 'email', 'address',
            'emergency_contact_name', 'emergency_contact_phone',
            'department', 'position', 'employment_status', 'employee_type',
            'hire_date', 'end_date', 'manager', 'salary', 'work_location', 'branch', 'notes'
        ]
        read_only_fields = ['id', 'employee_id']

    def validate_email(self, value):
        """Ensure email is unique among employees"""
        employee_id = self.instance.id if self.instance else None
        if value and Employee.objects.exclude(id=employee_id).filter(email=value).exists():
            raise serializers.ValidationError("Employee with this email already exists.")
        return value

    def validate_phone_number(self, value):
        """Validate phone number format"""
        if value and not value.startswith(('+855', '0')):
            raise serializers.ValidationError("Phone number must start with +855 or 0")
        return value

    def create(self, validated_data):
        """Create a new employee with auto-generated employee_id and user account"""
        with transaction.atomic():
            employee = Employee.objects.create(**validated_data)

            # Auto-create user account for the employee
            if not employee.has_user_account():
                try:
                    employee.create_user_account()
                except Exception as e:
                    # Log the error but don't fail the employee creation
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Failed to create user account for employee {employee.employee_id}: {str(e)}")

            return employee

    def update(self, instance, validated_data):
        """Update an existing employee"""
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance


class EmployeeDocumentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = EmployeeDocument
        fields = [
            'id', 'employee', 'employee_name', 'document_type', 'document_number',
            'issue_date', 'expiry_date', 'issuing_authority', 'document_file',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class EmployeeHistorySerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = EmployeeHistory
        fields = [
            'id', 'employee', 'employee_name', 'event_type', 'description',
            'date', 'created_at'
        ]
        read_only_fields = ['created_at']


class EmployeeMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer for dropdowns and references"""
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'first_name', 'last_name', 'full_name', 'department', 'position']
        read_only_fields = ['employee_id', 'full_name']


# ============ OVERTIME SERIALIZERS ============

class OvertimePolicySerializer(serializers.ModelSerializer):
    """Serializer for OvertimePolicy"""
    departments_list = DepartmentSerializer(source='departments', many=True, read_only=True)
    positions_list = PositionSerializer(source='positions', many=True, read_only=True)
    employees_list = EmployeeMinimalSerializer(source='employees', many=True, read_only=True)

    class Meta:
        model = OvertimePolicy
        fields = [
            'id', 'name', 'description', 'departments', 'departments_list',
            'positions', 'positions_list', 'employees', 'employees_list',
            'daily_threshold_hours', 'weekly_threshold_hours', 'rate_type',
            'standard_overtime_multiplier', 'extended_overtime_multiplier',
            'extended_hours_threshold', 'weekend_multiplier', 'holiday_multiplier',
            'fixed_hourly_rate', 'requires_pre_approval', 'approval_level',
            'max_daily_overtime', 'max_weekly_overtime', 'auto_calculate',
            'is_active', 'effective_date', 'end_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        """Custom validation for overtime policy"""
        if data.get('rate_type') == 'fixed' and not data.get('fixed_hourly_rate'):
            raise serializers.ValidationError(
                "Fixed hourly rate is required when rate type is 'fixed'"
            )

        if data.get('end_date') and data.get('effective_date'):
            if data['end_date'] <= data['effective_date']:
                raise serializers.ValidationError(
                    "End date must be after effective date"
                )

        return data


class OvertimeClaimListSerializer(serializers.ModelSerializer):
    """List serializer for overtime claims"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    department_name = serializers.CharField(source='employee.department.name', read_only=True)
    policy_name = serializers.CharField(source='overtime_policy.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)

    class Meta:
        model = OvertimeClaim
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'department_name',
            'overtime_policy', 'policy_name', 'claim_date', 'work_date',
            'overtime_hours', 'total_amount', 'status', 'approved_by_name',
            'payroll_period', 'is_weekend', 'is_holiday', 'is_emergency'
        ]


class OvertimeClaimDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for overtime claims"""
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_id = serializers.CharField(source='employee.employee_id', read_only=True)
    department_name = serializers.CharField(source='employee.department.name', read_only=True)
    policy_name = serializers.CharField(source='overtime_policy.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.full_name', read_only=True)

    # Read-only calculated fields
    is_pending_approval = serializers.ReadOnlyField()
    can_be_edited = serializers.ReadOnlyField()
    duration_hours = serializers.ReadOnlyField()

    class Meta:
        model = OvertimeClaim
        fields = [
            'id', 'employee', 'employee_name', 'employee_id', 'department_name',
            'overtime_policy', 'policy_name', 'claim_date', 'work_date',
            'start_time', 'end_time', 'regular_hours', 'overtime_hours',
            'total_hours', 'project_name', 'timecard_entry', 'reason',
            'is_weekend', 'is_holiday', 'is_emergency', 'hourly_rate',
            'overtime_rate', 'rate_multiplier', 'total_amount', 'status',
            'submitted_at', 'approved_at', 'approved_by', 'approved_by_name',
            'rejection_reason', 'payroll_period', 'paid_at', 'payroll_reference',
            'notes', 'attachments', 'created_at', 'updated_at',
            'is_pending_approval', 'can_be_edited', 'duration_hours'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'submitted_at', 'approved_at',
            'paid_at', 'is_pending_approval', 'can_be_edited', 'duration_hours',
            'regular_hours', 'overtime_hours', 'total_hours', 'hourly_rate',
            'overtime_rate', 'total_amount', 'payroll_period'
        ]


class OvertimeClaimCreateUpdateSerializer(serializers.ModelSerializer):
    """Create/Update serializer for overtime claims"""

    class Meta:
        model = OvertimeClaim
        fields = [
            'employee', 'overtime_policy', 'claim_date', 'work_date',
            'start_time', 'end_time', 'project_name', 'timecard_entry',
            'reason', 'is_holiday', 'is_emergency', 'notes', 'attachments'
        ]

    def validate(self, data):
        """Custom validation for overtime claims"""
        if data.get('start_time') and data.get('end_time'):
            # Basic time validation
            start_time = data['start_time']
            end_time = data['end_time']

            # For same-day work, end time should be after start time
            if end_time <= start_time:
                # Allow next-day scenarios (night shift)
                from datetime import datetime, timedelta
                work_date = data.get('work_date')
                if work_date:
                    start_datetime = datetime.combine(work_date, start_time)
                    end_datetime = datetime.combine(work_date, end_time) + timedelta(days=1)

                    # Check if total hours exceed 24 hours
                    total_hours = (end_datetime - start_datetime).total_seconds() / 3600
                    if total_hours > 24:
                        raise serializers.ValidationError(
                            "Work duration cannot exceed 24 hours"
                        )

        # Check if employee has applicable overtime policy
        employee = data.get('employee')
        policy = data.get('overtime_policy')
        if employee and policy:
            if not policy.is_applicable_to_employee(employee):
                raise serializers.ValidationError(
                    f"The selected overtime policy '{policy.name}' is not applicable to employee '{employee.full_name}'"
                )

        return data

    def create(self, validated_data):
        """Create overtime claim with auto-calculations"""
        validated_data['claim_date'] = validated_data.get('claim_date') or timezone.now().date()
        return super().create(validated_data)


class OvertimeApprovalSerializer(serializers.ModelSerializer):
    """Serializer for overtime approvals"""
    approver_name = serializers.CharField(source='approver.full_name', read_only=True)
    claim_details = OvertimeClaimListSerializer(source='overtime_claim', read_only=True)

    class Meta:
        model = OvertimeApproval
        fields = [
            'id', 'overtime_claim', 'claim_details', 'action', 'approver',
            'approver_name', 'approver_role', 'comments', 'suggestions',
            'approved_hours', 'approved_amount', 'conditions',
            'approval_level', 'is_final_approval', 'next_approver',
            'created_at'
        ]
        read_only_fields = ['created_at', 'approver_role']


class OvertimeApprovalCreateSerializer(serializers.ModelSerializer):
    """Create serializer for overtime approvals"""

    class Meta:
        model = OvertimeApproval
        fields = [
            'overtime_claim', 'action', 'approver', 'comments', 'suggestions',
            'approved_hours', 'approved_amount', 'conditions',
            'approval_level', 'is_final_approval', 'next_approver'
        ]

    def validate(self, data):
        """Custom validation for overtime approvals"""
        overtime_claim = data.get('overtime_claim')
        action = data.get('action')

        if overtime_claim and action == 'approved':
            # Validate approved hours don't exceed claimed hours
            approved_hours = data.get('approved_hours')
            if approved_hours and approved_hours > overtime_claim.overtime_hours:
                raise serializers.ValidationError(
                    f"Approved hours ({approved_hours}) cannot exceed claimed hours ({overtime_claim.overtime_hours})"
                )

        return data


class OvertimeReportSerializer(serializers.ModelSerializer):
    """Serializer for overtime reports"""
    generated_by_name = serializers.CharField(source='generated_by.full_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)

    class Meta:
        model = OvertimeReport
        fields = [
            'id', 'report_type', 'title', 'start_date', 'end_date',
            'department', 'department_name', 'employee', 'employee_name',
            'summary_data', 'generated_by', 'generated_by_name',
            'total_claims', 'total_hours', 'total_amount', 'created_at'
        ]
        read_only_fields = ['created_at', 'total_claims', 'total_hours', 'total_amount']


# Summary/Statistics Serializers

class OvertimeSummarySerializer(serializers.Serializer):
    """Serializer for overtime summary statistics"""
    total_claims = serializers.IntegerField()
    pending_claims = serializers.IntegerField()
    approved_claims = serializers.IntegerField()
    rejected_claims = serializers.IntegerField()
    total_overtime_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_daily_overtime = serializers.DecimalField(max_digits=6, decimal_places=2)
    weekend_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    holiday_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    emergency_hours = serializers.DecimalField(max_digits=8, decimal_places=2)


class EmployeeOvertimeSummarySerializer(serializers.Serializer):
    """Serializer for employee-specific overtime summary"""
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    department = serializers.CharField()
    total_claims = serializers.IntegerField()
    total_overtime_hours = serializers.DecimalField(max_digits=8, decimal_places=2)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    avg_weekly_overtime = serializers.DecimalField(max_digits=6, decimal_places=2)
    last_claim_date = serializers.DateField()
    pending_approvals = serializers.IntegerField()