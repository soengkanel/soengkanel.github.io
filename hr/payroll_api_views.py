# Payroll API views for NextHR Django application
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from django.db import transaction, models
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from django.contrib.auth.models import User
from django_tenants.utils import schema_context
from decimal import Decimal
from datetime import date, datetime, timedelta
import json
import logging

from .payroll_models import (
    PayrollPolicy, PayrollPeriod, PayrollComponent, TaxSlab,
    EmployeeSalary, EmployeeSalaryComponent, PayrollRun, PayrollEntry,
    PaySlip, SalaryAdvance, SalaryAdvanceRecovery, YearEndStatement
)
from .payroll_serializers import (
    PayrollPolicySerializer, PayrollPolicyDetailSerializer,
    PayrollPeriodSerializer, PayrollComponentSerializer,
    TaxSlabSerializer, EmployeeSalarySerializer, EmployeeSalaryDetailSerializer,
    EmployeeSalaryComponentSerializer, PayrollRunSerializer,
    PayrollEntrySerializer, PayrollEntryDetailSerializer,
    PaySlipSerializer, PaySlipDetailSerializer,
    SalaryAdvanceSerializer, SalaryAdvanceDetailSerializer,
    SalaryAdvanceRecoverySerializer, YearEndStatementSerializer,
    YearEndStatementDetailSerializer, PayrollCalculationSerializer,
    PayrollApprovalSerializer, PayslipGenerationSerializer,
    PayrollReportSerializer, BulkSalaryUpdateSerializer
)
from .models import Employee, Department

logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination class for payroll APIs"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class PayrollPolicyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll policies
    """
    queryset = PayrollPolicy.objects.all()
    serializer_class = PayrollPolicySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['calculation_method', 'tax_calculation_method', 'is_active']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return detailed serializer for retrieve actions"""
        if self.action == 'retrieve':
            return PayrollPolicyDetailSerializer
        return PayrollPolicySerializer

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = PayrollPolicy.objects.all()

        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        # Filter by effective date
        effective_date = self.request.query_params.get('effective_date')
        if effective_date:
            queryset = queryset.filter(effective_date__lte=effective_date)

        return queryset.order_by('-effective_date')

    @action(detail=True, methods=['post'])
    def add_tax_slab(self, request, pk=None):
        """Add tax slab to a payroll policy"""
        policy = self.get_object()
        serializer = TaxSlabSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(payroll_policy=policy)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def tax_slabs(self, request, pk=None):
        """Get tax slabs for a payroll policy"""
        policy = self.get_object()
        tax_slabs = policy.tax_slabs.all().order_by('slab_order', 'min_amount')
        serializer = TaxSlabSerializer(tax_slabs, many=True)
        return Response(serializer.data)


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll periods
    """
    queryset = PayrollPeriod.objects.all()
    serializer_class = PayrollPeriodSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payroll_policy']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = PayrollPeriod.objects.select_related('payroll_policy', 'processed_by')

        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(start_date__year=year)

        # Filter by current period
        is_current = self.request.query_params.get('current')
        if is_current == 'true':
            today = date.today()
            queryset = queryset.filter(start_date__lte=today, end_date__gte=today)

        return queryset.order_by('-start_date')

    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current active payroll period"""
        today = date.today()
        try:
            period = PayrollPeriod.objects.filter(
                start_date__lte=today,
                end_date__gte=today,
                status='active'
            ).first()

            if period:
                serializer = self.get_serializer(period)
                return Response(serializer.data)
            else:
                return Response(
                    {'detail': 'No active payroll period found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def lock_period(self, request, pk=None):
        """Lock a payroll period to prevent changes"""
        period = self.get_object()

        if period.status != 'active':
            return Response(
                {'error': 'Only active periods can be locked'},
                status=status.HTTP_400_BAD_REQUEST
            )

        period.status = 'locked'
        period.save()

        return Response({'message': 'Payroll period locked successfully'})

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get payroll period summary"""
        period = self.get_object()

        # Get payroll runs for this period
        payroll_runs = period.payroll_runs.all()

        summary = {
            'period_info': PayrollPeriodSerializer(period).data,
            'total_runs': payroll_runs.count(),
            'total_employees_processed': period.processed_employees,
            'total_gross_pay': float(period.total_gross_pay),
            'total_deductions': float(period.total_deductions),
            'total_net_pay': float(period.total_net_pay),
            'runs': PayrollRunSerializer(payroll_runs, many=True).data
        }

        return Response(summary)


class PayrollComponentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll components
    """
    queryset = PayrollComponent.objects.all()
    serializer_class = PayrollComponentSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['component_type', 'calculation_type', 'is_active', 'is_mandatory']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = PayrollComponent.objects.prefetch_related('departments', 'positions')

        # Filter by component type
        component_type = self.request.query_params.get('component_type')
        if component_type:
            queryset = queryset.filter(component_type=component_type)

        # Filter by applicable to employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            try:
                employee = Employee.objects.get(id=employee_id)
                queryset = queryset.filter(
                    Q(applicable_to_all=True) |
                    Q(departments=employee.department) |
                    Q(positions=employee.position)
                ).distinct()
            except Employee.DoesNotExist:
                pass

        return queryset.order_by('component_type', 'display_order', 'name')

    @action(detail=True, methods=['post'])
    def calculate(self, request, pk=None):
        """Calculate component amount for given parameters"""
        component = self.get_object()

        basic_salary = request.data.get('basic_salary', 0)
        gross_salary = request.data.get('gross_salary', 0)
        custom_values = request.data.get('custom_values', {})

        try:
            basic_salary = Decimal(str(basic_salary))
            gross_salary = Decimal(str(gross_salary))

            calculated_amount = component.calculate_amount(
                basic_salary, gross_salary, custom_values=custom_values
            )

            return Response({
                'component': component.name,
                'calculated_amount': float(calculated_amount),
                'basic_salary': float(basic_salary),
                'gross_salary': float(gross_salary),
                'custom_values': custom_values
            })
        except (ValueError, TypeError) as e:
            return Response(
                {'error': f'Invalid input: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing employee salaries
    """
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'payroll_policy', 'is_active']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return detailed serializer for retrieve actions"""
        if self.action == 'retrieve':
            return EmployeeSalaryDetailSerializer
        return EmployeeSalarySerializer

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = EmployeeSalary.objects.select_related(
            'employee', 'payroll_policy', 'approved_by', 'created_by'
        ).prefetch_related('components__payroll_component')

        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Filter by current salaries
        current_only = self.request.query_params.get('current_only')
        if current_only == 'true':
            today = date.today()
            queryset = queryset.filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today),
                effective_date__lte=today,
                is_active=True
            )

        return queryset.order_by('-effective_date')

    def perform_create(self, serializer):
        """Set created_by when creating salary"""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_component(self, request, pk=None):
        """Add salary component to employee salary"""
        employee_salary = self.get_object()
        serializer = EmployeeSalaryComponentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(employee_salary=employee_salary)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def components(self, request, pk=None):
        """Get salary components for employee salary"""
        employee_salary = self.get_object()
        components = employee_salary.components.filter(is_active=True)
        serializer = EmployeeSalaryComponentSerializer(components, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve employee salary structure"""
        employee_salary = self.get_object()

        if employee_salary.approved_by:
            return Response(
                {'error': 'Salary structure is already approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee_salary.approved_by = request.user
        employee_salary.approved_at = timezone.now()
        employee_salary.save()

        return Response({'message': 'Salary structure approved successfully'})


class PayrollRunViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll runs
    """
    queryset = PayrollRun.objects.all()
    serializer_class = PayrollRunSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['payroll_period', 'status']
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = PayrollRun.objects.select_related(
            'payroll_period', 'processed_by', 'approved_by'
        ).prefetch_related('departments', 'employees')

        return queryset.order_by('-run_date')

    def perform_create(self, serializer):
        """Set processed_by when creating payroll run"""
        # Auto-increment run number for the same period
        period = serializer.validated_data['payroll_period']
        last_run = PayrollRun.objects.filter(payroll_period=period).order_by('-run_number').first()
        run_number = (last_run.run_number + 1) if last_run else 1

        serializer.save(processed_by=self.request.user, run_number=run_number)

    @action(detail=False, methods=['post'])
    def calculate(self, request):
        """Calculate payroll for a period"""
        serializer = PayrollCalculationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            with transaction.atomic():
                # Get payroll period
                period = PayrollPeriod.objects.get(id=data['payroll_period_id'])

                # Create payroll run
                payroll_run = PayrollRun.objects.create(
                    payroll_period=period,
                    processed_by=request.user,
                    status='calculating'
                )

                # Add filter criteria
                if data.get('employee_ids'):
                    payroll_run.employees.set(data['employee_ids'])
                if data.get('department_ids'):
                    payroll_run.departments.set(data['department_ids'])

                # Start calculation process
                calculation_result = self._calculate_payroll(payroll_run, data)

                return Response({
                    'payroll_run_id': payroll_run.id,
                    'status': 'calculated',
                    'calculation_result': calculation_result
                })

        except Exception as e:
            return Response(
                {'error': f'Payroll calculation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _calculate_payroll(self, payroll_run, data):
        """Perform actual payroll calculation"""
        # Get employees to process
        if data.get('employee_ids'):
            employees = Employee.objects.filter(id__in=data['employee_ids'])
        elif data.get('department_ids'):
            employees = Employee.objects.filter(department_id__in=data['department_ids'])
        else:
            employees = Employee.objects.filter(employment_status='active')

        results = {
            'processed_employees': 0,
            'successful_calculations': 0,
            'failed_calculations': 0,
            'total_gross_pay': 0,
            'total_deductions': 0,
            'total_net_pay': 0,
            'errors': []
        }

        payroll_run.processing_started_at = timezone.now()
        payroll_run.save()

        for employee in employees:
            try:
                # Get current salary structure
                salary_structure = EmployeeSalary.objects.filter(
                    employee=employee,
                    is_active=True,
                    effective_date__lte=payroll_run.payroll_period.end_date
                ).order_by('-effective_date').first()

                if not salary_structure:
                    results['errors'].append(f"No salary structure found for {employee.full_name}")
                    results['failed_calculations'] += 1
                    continue

                # Create or update payroll entry
                payroll_entry, created = PayrollEntry.objects.get_or_create(
                    payroll_run=payroll_run,
                    employee=employee,
                    defaults={'employee_salary': salary_structure}
                )

                # Calculate payroll
                payroll_entry.calculate_payroll()

                # Update totals
                results['total_gross_pay'] += float(payroll_entry.gross_salary)
                results['total_deductions'] += float(payroll_entry.total_deductions)
                results['total_net_pay'] += float(payroll_entry.net_salary)
                results['successful_calculations'] += 1

            except Exception as e:
                results['errors'].append(f"Error calculating for {employee.full_name}: {str(e)}")
                results['failed_calculations'] += 1

            results['processed_employees'] += 1

        # Update payroll run
        payroll_run.status = 'calculated'
        payroll_run.processing_completed_at = timezone.now()
        payroll_run.total_employees_processed = results['processed_employees']
        payroll_run.total_gross_pay = Decimal(str(results['total_gross_pay']))
        payroll_run.total_deductions = Decimal(str(results['total_deductions']))
        payroll_run.total_net_pay = Decimal(str(results['total_net_pay']))
        payroll_run.save()

        return results

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve payroll run"""
        serializer = PayrollApprovalSerializer(data={**request.data, 'payroll_run_id': pk})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        payroll_run = self.get_object()

        try:
            with transaction.atomic():
                # Update payroll run status
                payroll_run.status = 'approved'
                payroll_run.approved_by = request.user
                payroll_run.approved_at = timezone.now()
                payroll_run.save()

                # Update payroll entries
                entries_to_approve = payroll_run.entries.all()
                if data.get('entry_ids'):
                    entries_to_approve = entries_to_approve.filter(id__in=data['entry_ids'])

                entries_to_approve.update(
                    status='approved',
                    approved_by=request.user,
                    approved_at=timezone.now()
                )

                return Response({
                    'message': 'Payroll run approved successfully',
                    'approved_entries': entries_to_approve.count()
                })

        except Exception as e:
            return Response(
                {'error': f'Approval failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def entries(self, request, pk=None):
        """Get payroll entries for a run"""
        payroll_run = self.get_object()
        entries = payroll_run.entries.select_related('employee', 'employee_salary')

        # Apply filters
        status_filter = request.query_params.get('status')
        if status_filter:
            entries = entries.filter(status=status_filter)

        department_id = request.query_params.get('department_id')
        if department_id:
            entries = entries.filter(employee__department_id=department_id)

        serializer = PayrollEntrySerializer(entries, many=True)
        return Response(serializer.data)


class PayrollEntryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payroll entries
    """
    queryset = PayrollEntry.objects.all()
    serializer_class = PayrollEntrySerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'status', 'payroll_run__payroll_period']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return detailed serializer for retrieve actions"""
        if self.action == 'retrieve':
            return PayrollEntryDetailSerializer
        return PayrollEntrySerializer

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = PayrollEntry.objects.select_related(
            'employee', 'employee_salary', 'payroll_run', 'approved_by'
        )

        # Filter by payroll period
        period_id = self.request.query_params.get('period_id')
        if period_id:
            queryset = queryset.filter(payroll_run__payroll_period_id=period_id)

        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        return queryset.order_by('-payroll_run__run_date', 'employee__employee_id')

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Recalculate payroll entry"""
        entry = self.get_object()

        if entry.status not in ['draft', 'calculated']:
            return Response(
                {'error': 'Only draft or calculated entries can be recalculated'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            entry.calculate_payroll()
            return Response({
                'message': 'Payroll entry recalculated successfully',
                'entry': PayrollEntryDetailSerializer(entry).data
            })
        except Exception as e:
            return Response(
                {'error': f'Recalculation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark payroll entry as paid"""
        entry = self.get_object()

        if entry.status != 'approved':
            return Response(
                {'error': 'Only approved entries can be marked as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_reference = request.data.get('payment_reference', '')

        entry.status = 'paid'
        entry.paid_at = timezone.now()
        entry.payment_reference = payment_reference
        entry.save()

        return Response({'message': 'Payroll entry marked as paid'})


class PaySlipViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payslips
    """
    queryset = PaySlip.objects.all()
    serializer_class = PaySlipSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'payroll_entry__employee']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return detailed serializer for retrieve actions"""
        if self.action == 'retrieve':
            return PaySlipDetailSerializer
        return PaySlipSerializer

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = PaySlip.objects.select_related(
            'payroll_entry__employee',
            'payroll_entry__payroll_run__payroll_period'
        )

        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(payroll_entry__employee_id=employee_id)

        # Filter by period
        period_id = self.request.query_params.get('period_id')
        if period_id:
            queryset = queryset.filter(payroll_entry__payroll_run__payroll_period_id=period_id)

        return queryset.order_by('-generation_date')

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate payslips for payroll run"""
        serializer = PayslipGenerationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            payroll_run = PayrollRun.objects.get(id=data['payroll_run_id'])

            # Get payroll entries to generate payslips for
            entries = payroll_run.entries.filter(status='approved')
            if data.get('employee_ids'):
                entries = entries.filter(employee_id__in=data['employee_ids'])

            generated_payslips = []

            for entry in entries:
                # Create or get existing payslip
                payslip, created = PaySlip.objects.get_or_create(
                    payroll_entry=entry,
                    defaults={'status': 'generated'}
                )

                if created:
                    generated_payslips.append(payslip)

                    # TODO: Generate PDF if needed
                    # if data.get('generate_pdf', True):
                    #     pass
                    #     payslip.generate_pdf()

                    # TODO: Send email if requested
                    # if data.get('send_email', False):
                    #     pass
                    #     payslip.send_email()

            return Response({
                'message': f'Generated {len(generated_payslips)} payslips',
                'generated_count': len(generated_payslips),
                'payslips': PaySlipSerializer(generated_payslips, many=True).data
            })

        except Exception as e:
            return Response(
                {'error': f'Payslip generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """Download payslip PDF"""
        payslip = self.get_object()

        # TODO: Implement PDF generation and download
        # For now, return a placeholder response
        return Response({
            'message': 'PDF download will be implemented',
            'payslip_number': payslip.payslip_number,
            'employee': payslip.payroll_entry.employee.full_name
        })

    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark payslip as viewed"""
        payslip = self.get_object()

        if not payslip.viewed_at:
            payslip.viewed_at = timezone.now()
            payslip.status = 'viewed'
            payslip.save()

        return Response({'message': 'Payslip marked as viewed'})


class SalaryAdvanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing salary advances
    """
    queryset = SalaryAdvance.objects.all()
    serializer_class = SalaryAdvanceSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'status']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return detailed serializer for retrieve actions"""
        if self.action == 'retrieve':
            return SalaryAdvanceDetailSerializer
        return SalaryAdvanceSerializer

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = SalaryAdvance.objects.select_related('employee', 'approved_by')

        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Filter by pending status
        pending_only = self.request.query_params.get('pending_only')
        if pending_only == 'true':
            queryset = queryset.filter(status='requested')

        return queryset.order_by('-request_date')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve salary advance request"""
        advance = self.get_object()

        if advance.status != 'requested':
            return Response(
                {'error': 'Only requested advances can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        approval_comments = request.data.get('approval_comments', '')

        advance.status = 'approved'
        advance.approved_by = request.user
        advance.approved_at = timezone.now()
        advance.approval_comments = approval_comments
        advance.save()

        return Response({'message': 'Salary advance approved successfully'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject salary advance request"""
        advance = self.get_object()

        if advance.status != 'requested':
            return Response(
                {'error': 'Only requested advances can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        approval_comments = request.data.get('approval_comments', '')

        advance.status = 'rejected'
        advance.approval_comments = approval_comments
        advance.save()

        return Response({'message': 'Salary advance rejected'})

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark salary advance as paid"""
        advance = self.get_object()

        if advance.status != 'approved':
            return Response(
                {'error': 'Only approved advances can be marked as paid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment_reference = request.data.get('payment_reference', '')

        advance.status = 'paid'
        advance.paid_at = timezone.now()
        advance.payment_reference = payment_reference
        advance.save()

        return Response({'message': 'Salary advance marked as paid'})

    @action(detail=True, methods=['get'])
    def recoveries(self, request, pk=None):
        """Get recovery history for salary advance"""
        advance = self.get_object()
        recoveries = advance.recoveries.all().order_by('-recovery_date')
        serializer = SalaryAdvanceRecoverySerializer(recoveries, many=True)
        return Response(serializer.data)


class YearEndStatementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing year-end statements
    """
    queryset = YearEndStatement.objects.all()
    serializer_class = YearEndStatementSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['employee', 'financial_year', 'is_final']
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Return detailed serializer for retrieve actions"""
        if self.action == 'retrieve':
            return YearEndStatementDetailSerializer
        return YearEndStatementSerializer

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = YearEndStatement.objects.select_related('employee', 'generated_by')

        # Filter by employee
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        return queryset.order_by('-financial_year', 'employee__employee_id')

    def perform_create(self, serializer):
        """Set generated_by when creating statement"""
        serializer.save(generated_by=self.request.user)

    @action(detail=True, methods=['post'])
    def generate_data(self, request, pk=None):
        """Generate year-end statement data from payroll entries"""
        statement = self.get_object()

        try:
            statement.generate_statement()
            return Response({
                'message': 'Year-end statement data generated successfully',
                'statement': YearEndStatementDetailSerializer(statement).data
            })
        except Exception as e:
            return Response(
                {'error': f'Statement generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def finalize(self, request, pk=None):
        """Finalize year-end statement"""
        statement = self.get_object()

        statement.is_final = True
        statement.save()

        return Response({'message': 'Year-end statement finalized'})


# Additional ViewSet for bulk operations and reports

class PayrollUtilityViewSet(viewsets.ViewSet):
    """
    ViewSet for payroll utility operations like bulk updates and reports
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def bulk_salary_update(self, request):
        """Bulk update employee salaries"""
        serializer = BulkSalaryUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            with transaction.atomic():
                employees = Employee.objects.filter(id__in=data['employee_ids'])
                updated_salaries = []

                for employee in employees:
                    # Get current salary
                    current_salary = EmployeeSalary.objects.filter(
                        employee=employee,
                        is_active=True
                    ).order_by('-effective_date').first()

                    if not current_salary:
                        continue

                    # Calculate new salary
                    if data.get('salary_increase_percentage'):
                        new_basic_salary = current_salary.basic_salary * (
                            1 + data['salary_increase_percentage'] / 100
                        )
                    else:
                        new_basic_salary = current_salary.basic_salary + data['salary_increase_amount']

                    # Create new salary structure
                    new_salary = EmployeeSalary.objects.create(
                        employee=employee,
                        payroll_policy=current_salary.payroll_policy,
                        basic_salary=new_basic_salary,
                        effective_date=data['effective_date'],
                        previous_salary=current_salary.basic_salary,
                        revision_reason=data['revision_reason'],
                        created_by=request.user
                    )

                    # Deactivate old salary
                    current_salary.end_date = data['effective_date'] - timedelta(days=1)
                    current_salary.save()

                    updated_salaries.append(new_salary)

                return Response({
                    'message': f'Updated salaries for {len(updated_salaries)} employees',
                    'updated_count': len(updated_salaries),
                    'salaries': EmployeeSalarySerializer(updated_salaries, many=True).data
                })

        except Exception as e:
            return Response(
                {'error': f'Bulk salary update failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def generate_reports(self, request):
        """Generate payroll reports"""
        serializer = PayrollReportSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        try:
            # Get payroll entries for the period
            entries_query = PayrollEntry.objects.filter(
                payroll_run__payroll_period__start_date__gte=data['start_date'],
                payroll_run__payroll_period__end_date__lte=data['end_date']
            )

            if not data.get('include_drafts'):
                entries_query = entries_query.exclude(status='draft')

            if data.get('department_ids'):
                entries_query = entries_query.filter(
                    employee__department_id__in=data['department_ids']
                )

            if data.get('employee_ids'):
                entries_query = entries_query.filter(
                    employee_id__in=data['employee_ids']
                )

            entries = entries_query.select_related(
                'employee', 'employee__department', 'payroll_run__payroll_period'
            )

            # Generate report based on type
            report_data = self._generate_payroll_report(data['report_type'], entries)

            return Response({
                'report_type': data['report_type'],
                'period': f"{data['start_date']} to {data['end_date']}",
                'generated_at': timezone.now().isoformat(),
                'data': report_data
            })

        except Exception as e:
            return Response(
                {'error': f'Report generation failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _generate_payroll_report(self, report_type, entries):
        """Generate specific type of payroll report"""
        if report_type == 'summary':
            return {
                'total_employees': entries.values('employee').distinct().count(),
                'total_gross_pay': float(entries.aggregate(Sum('gross_salary'))['gross_salary__sum'] or 0),
                'total_deductions': float(entries.aggregate(Sum('total_deductions'))['total_deductions__sum'] or 0),
                'total_net_pay': float(entries.aggregate(Sum('net_salary'))['net_salary__sum'] or 0),
                'average_gross_salary': float(entries.aggregate(Avg('gross_salary'))['gross_salary__avg'] or 0),
            }

        elif report_type == 'department_wise':
            dept_summary = entries.values(
                'employee__department__name'
            ).annotate(
                employee_count=Count('employee', distinct=True),
                total_gross=Sum('gross_salary'),
                total_deductions=Sum('total_deductions'),
                total_net=Sum('net_salary'),
                avg_gross=Avg('gross_salary')
            ).order_by('employee__department__name')

            return list(dept_summary)

        elif report_type == 'detailed':
            return PayrollEntrySerializer(entries, many=True).data

        # Add more report types as needed
        return {'message': f'Report type {report_type} not yet implemented'}

