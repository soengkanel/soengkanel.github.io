# API ViewSets for Overtime module
from rest_framework import viewsets, status, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Q, Sum, Count, Avg, Max
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from datetime import datetime, timedelta
from decimal import Decimal

from .models import (
    OvertimePolicy, OvertimeClaim, OvertimeApproval, OvertimeReport,
    Employee, Department
)
from .serializers import (
    OvertimePolicySerializer,
    OvertimeClaimListSerializer,
    OvertimeClaimDetailSerializer,
    OvertimeClaimCreateUpdateSerializer,
    OvertimeApprovalSerializer,
    OvertimeApprovalCreateSerializer,
    OvertimeReportSerializer,
    OvertimeSummarySerializer,
    EmployeeOvertimeSummarySerializer
)


@extend_schema_view(
    list=extend_schema(
        summary="List overtime policies",
        description="Get a list of all overtime policies with filtering capabilities",
        parameters=[
            OpenApiParameter(
                name='is_active',
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                description='Filter by active status',
                required=False
            ),
            OpenApiParameter(
                name='department',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Filter by department ID',
                required=False
            ),
            OpenApiParameter(
                name='rate_type',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by rate type (fixed, multiplier, tiered)',
                required=False
            ),
        ],
        tags=['Overtime Policies']
    ),
    create=extend_schema(
        summary="Create overtime policy",
        description="Create a new overtime policy",
        tags=['Overtime Policies']
    ),
    retrieve=extend_schema(
        summary="Get overtime policy details",
        description="Get detailed information about a specific overtime policy",
        tags=['Overtime Policies']
    ),
    update=extend_schema(
        summary="Update overtime policy",
        description="Update all fields of an overtime policy",
        tags=['Overtime Policies']
    ),
    partial_update=extend_schema(
        summary="Partially update overtime policy",
        description="Update specific fields of an overtime policy",
        tags=['Overtime Policies']
    ),
    destroy=extend_schema(
        summary="Delete overtime policy",
        description="Delete an overtime policy",
        tags=['Overtime Policies']
    ),
)
class OvertimePolicyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for OvertimePolicy CRUD operations
    """
    queryset = OvertimePolicy.objects.all()
    serializer_class = OvertimePolicySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'rate_type', 'approval_level', 'departments', 'positions']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'effective_date', 'created_at']
    ordering = ['-created_at']

    @extend_schema(
        summary="Get applicable employees",
        description="Get employees that this policy applies to",
        tags=['Overtime Policies']
    )
    @action(detail=True, methods=['get'])
    def applicable_employees(self, request, pk=None):
        """Get employees that this overtime policy applies to"""
        policy = self.get_object()
        employees = []

        # Direct employee assignments
        for employee in policy.employees.all():
            employees.append(employee)

        # Department-based assignments
        for department in policy.departments.all():
            for employee in department.employees.all():
                if employee not in employees:
                    employees.append(employee)

        # Position-based assignments
        for position in policy.positions.all():
            for employee in position.employees.all():
                if employee not in employees:
                    employees.append(employee)

        from .serializers import EmployeeMinimalSerializer
        serializer = EmployeeMinimalSerializer(employees, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Test policy calculation",
        description="Test overtime calculation for given parameters",
        parameters=[
            OpenApiParameter('employee_id', OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter('hours', OpenApiTypes.NUMBER, OpenApiParameter.QUERY),
            OpenApiParameter('is_weekend', OpenApiTypes.BOOL, OpenApiParameter.QUERY),
            OpenApiParameter('is_holiday', OpenApiTypes.BOOL, OpenApiParameter.QUERY),
        ],
        tags=['Overtime Policies']
    )
    @action(detail=True, methods=['get'])
    def test_calculation(self, request, pk=None):
        """Test overtime rate calculation"""
        policy = self.get_object()
        employee_id = request.query_params.get('employee_id')
        hours = request.query_params.get('hours', 1)
        is_weekend = request.query_params.get('is_weekend', 'false').lower() == 'true'
        is_holiday = request.query_params.get('is_holiday', 'false').lower() == 'true'

        try:
            hours = float(hours)
            if employee_id:
                employee = Employee.objects.get(id=employee_id)
                overtime_rate = policy.calculate_overtime_rate(employee, hours, is_weekend, is_holiday)

                return Response({
                    'employee': employee.full_name,
                    'hours': hours,
                    'is_weekend': is_weekend,
                    'is_holiday': is_holiday,
                    'overtime_rate': overtime_rate,
                    'total_amount': hours * overtime_rate,
                    'base_hourly_rate': employee.salary / 160 if employee.salary else 0,
                })
            else:
                return Response({'error': 'Employee ID is required'}, status=400)
        except (Employee.DoesNotExist, ValueError) as e:
            return Response({'error': str(e)}, status=400)


@extend_schema_view(
    list=extend_schema(
        summary="List overtime claims",
        description="Get a list of overtime claims with filtering and search capabilities",
        parameters=[
            OpenApiParameter('employee', OpenApiTypes.INT, OpenApiParameter.QUERY, description='Filter by employee ID'),
            OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY,
                           description='Filter by status (draft, submitted, approved, rejected, paid, cancelled)'),
            OpenApiParameter('work_date_from', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                           description='Filter by work date from'),
            OpenApiParameter('work_date_to', OpenApiTypes.DATE, OpenApiParameter.QUERY,
                           description='Filter by work date to'),
            OpenApiParameter('payroll_period', OpenApiTypes.STR, OpenApiParameter.QUERY,
                           description='Filter by payroll period (e.g., 2024-01)'),
            OpenApiParameter('department', OpenApiTypes.INT, OpenApiParameter.QUERY,
                           description='Filter by department ID'),
            OpenApiParameter('is_weekend', OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                           description='Filter by weekend work'),
            OpenApiParameter('is_holiday', OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                           description='Filter by holiday work'),
            OpenApiParameter('is_emergency', OpenApiTypes.BOOL, OpenApiParameter.QUERY,
                           description='Filter by emergency work'),
        ],
        tags=['Overtime Claims']
    ),
    create=extend_schema(
        summary="Create overtime claim",
        description="Create a new overtime claim",
        tags=['Overtime Claims']
    ),
    retrieve=extend_schema(
        summary="Get overtime claim details",
        description="Get detailed information about a specific overtime claim",
        tags=['Overtime Claims']
    ),
    update=extend_schema(
        summary="Update overtime claim",
        description="Update all fields of an overtime claim",
        tags=['Overtime Claims']
    ),
    partial_update=extend_schema(
        summary="Partially update overtime claim",
        description="Update specific fields of an overtime claim",
        tags=['Overtime Claims']
    ),
    destroy=extend_schema(
        summary="Delete overtime claim",
        description="Delete an overtime claim",
        tags=['Overtime Claims']
    ),
)
class OvertimeClaimViewSet(viewsets.ModelViewSet):
    """
    ViewSet for OvertimeClaim CRUD operations
    """
    queryset = OvertimeClaim.objects.select_related(
        'employee', 'overtime_policy', 'approved_by',
        'employee__department', 'employee__position'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'employee', 'status', 'payroll_period', 'is_weekend',
        'is_holiday', 'is_emergency', 'overtime_policy'
    ]
    search_fields = ['employee__first_name', 'employee__last_name', 'project_name', 'reason']
    ordering_fields = ['work_date', 'created_at', 'total_amount', 'overtime_hours']
    ordering = ['-work_date', '-created_at']

    def get_queryset(self):
        """Filter queryset based on query parameters"""
        queryset = super().get_queryset()

        # Date range filtering
        work_date_from = self.request.query_params.get('work_date_from')
        work_date_to = self.request.query_params.get('work_date_to')

        if work_date_from:
            queryset = queryset.filter(work_date__gte=work_date_from)
        if work_date_to:
            queryset = queryset.filter(work_date__lte=work_date_to)

        # Department filtering
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(employee__department_id=department)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return OvertimeClaimListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return OvertimeClaimCreateUpdateSerializer
        return OvertimeClaimDetailSerializer

    @extend_schema(
        summary="Submit overtime claim",
        description="Submit an overtime claim for approval",
        tags=['Overtime Claims']
    )
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit overtime claim for approval"""
        claim = self.get_object()

        if claim.status != 'draft':
            return Response(
                {'error': 'Only draft claims can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        claim.status = 'submitted'
        claim.submitted_at = timezone.now()
        claim.save()

        return Response({
            'message': 'Overtime claim submitted successfully',
            'status': claim.status,
            'submitted_at': claim.submitted_at
        })

    @extend_schema(
        summary="Cancel overtime claim",
        description="Cancel an overtime claim",
        tags=['Overtime Claims']
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel overtime claim"""
        claim = self.get_object()

        if claim.status in ['approved', 'paid']:
            return Response(
                {'error': 'Cannot cancel approved or paid claims'},
                status=status.HTTP_400_BAD_REQUEST
            )

        claim.status = 'cancelled'
        claim.save()

        return Response({
            'message': 'Overtime claim cancelled successfully',
            'status': claim.status
        })

    @extend_schema(
        summary="Get claim approvals",
        description="Get approval history for an overtime claim",
        tags=['Overtime Claims']
    )
    @action(detail=True, methods=['get'])
    def approvals(self, request, pk=None):
        """Get approval history for this claim"""
        claim = self.get_object()
        approvals = claim.approvals.all()
        serializer = OvertimeApprovalSerializer(approvals, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get my claims",
        description="Get overtime claims for the current user",
        parameters=[
            OpenApiParameter('status', OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter('month', OpenApiTypes.STR, OpenApiParameter.QUERY,
                           description='Filter by month (YYYY-MM format)'),
        ],
        tags=['Overtime Claims']
    )
    @action(detail=False, methods=['get'])
    def my_claims(self, request):
        """Get overtime claims for the current user"""
        try:
            employee = Employee.objects.get(user=request.user)
            queryset = self.get_queryset().filter(employee=employee)

            # Additional filtering
            claim_status = request.query_params.get('status')
            if claim_status:
                queryset = queryset.filter(status=claim_status)

            month = request.query_params.get('month')
            if month:
                try:
                    year, month_num = month.split('-')
                    queryset = queryset.filter(
                        work_date__year=int(year),
                        work_date__month=int(month_num)
                    )
                except ValueError:
                    pass

            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = OvertimeClaimListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = OvertimeClaimListSerializer(queryset, many=True)
            return Response(serializer.data)

        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @extend_schema(
        summary="Get pending approvals",
        description="Get overtime claims pending approval for the current user",
        tags=['Overtime Claims']
    )
    @action(detail=False, methods=['get'])
    def pending_approvals(self, request):
        """Get claims pending approval for the current user"""
        try:
            employee = Employee.objects.get(user=request.user)

            # Find claims where current user should approve
            # This would need to be enhanced based on approval workflow logic
            queryset = self.get_queryset().filter(
                status='submitted',
                employee__manager=employee  # Simple manager approval
            )

            queryset = self.filter_queryset(queryset)
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = OvertimeClaimListSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = OvertimeClaimListSerializer(queryset, many=True)
            return Response(serializer.data)

        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="List overtime approvals",
        description="Get a list of overtime approvals",
        tags=['Overtime Approvals']
    ),
    create=extend_schema(
        summary="Create overtime approval",
        description="Create a new overtime approval (approve/reject claim)",
        tags=['Overtime Approvals']
    ),
    retrieve=extend_schema(
        summary="Get overtime approval details",
        description="Get detailed information about a specific overtime approval",
        tags=['Overtime Approvals']
    ),
)
class OvertimeApprovalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for OvertimeApproval operations
    """
    queryset = OvertimeApproval.objects.select_related(
        'overtime_claim', 'approver', 'overtime_claim__employee'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'approver', 'approval_level', 'is_final_approval']
    search_fields = ['overtime_claim__employee__first_name', 'overtime_claim__employee__last_name', 'comments']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    http_method_names = ['get', 'post', 'head', 'options']  # No updates/deletes for approvals

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return OvertimeApprovalCreateSerializer
        return OvertimeApprovalSerializer

    def perform_create(self, serializer):
        """Set the approver to current user when creating"""
        try:
            approver = Employee.objects.get(user=self.request.user)
            serializer.save(approver=approver)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee profile not found for current user")

    @extend_schema(
        summary="Quick approve claim",
        description="Quickly approve an overtime claim",
        tags=['Overtime Approvals']
    )
    @action(detail=False, methods=['post'])
    def quick_approve(self, request):
        """Quick approve an overtime claim"""
        claim_id = request.data.get('claim_id')
        comments = request.data.get('comments', '')

        if not claim_id:
            return Response({'error': 'claim_id is required'}, status=400)

        try:
            claim = OvertimeClaim.objects.get(id=claim_id)
            approver = Employee.objects.get(user=request.user)

            # Create approval
            approval = OvertimeApproval.objects.create(
                overtime_claim=claim,
                action='approved',
                approver=approver,
                comments=comments,
                is_final_approval=True
            )

            serializer = OvertimeApprovalSerializer(approval)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except (OvertimeClaim.DoesNotExist, Employee.DoesNotExist) as e:
            return Response({'error': str(e)}, status=400)

    @extend_schema(
        summary="Quick reject claim",
        description="Quickly reject an overtime claim",
        tags=['Overtime Approvals']
    )
    @action(detail=False, methods=['post'])
    def quick_reject(self, request):
        """Quick reject an overtime claim"""
        claim_id = request.data.get('claim_id')
        comments = request.data.get('comments', '')

        if not claim_id:
            return Response({'error': 'claim_id is required'}, status=400)

        if not comments:
            return Response({'error': 'Rejection reason is required'}, status=400)

        try:
            claim = OvertimeClaim.objects.get(id=claim_id)
            approver = Employee.objects.get(user=request.user)

            # Create approval
            approval = OvertimeApproval.objects.create(
                overtime_claim=claim,
                action='rejected',
                approver=approver,
                comments=comments,
                is_final_approval=True
            )

            serializer = OvertimeApprovalSerializer(approval)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except (OvertimeClaim.DoesNotExist, Employee.DoesNotExist) as e:
            return Response({'error': str(e)}, status=400)


@extend_schema_view(
    list=extend_schema(
        summary="List overtime reports",
        description="Get a list of overtime reports",
        tags=['Overtime Reports']
    ),
    create=extend_schema(
        summary="Create overtime report",
        description="Create a new overtime report",
        tags=['Overtime Reports']
    ),
    retrieve=extend_schema(
        summary="Get overtime report details",
        description="Get detailed information about a specific overtime report",
        tags=['Overtime Reports']
    ),
)
class OvertimeReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for OvertimeReport operations
    """
    queryset = OvertimeReport.objects.select_related(
        'generated_by', 'department', 'employee'
    ).all()
    serializer_class = OvertimeReportSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'department', 'employee']
    search_fields = ['title']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Set the generator to current user when creating"""
        try:
            generator = Employee.objects.get(user=self.request.user)
            serializer.save(generated_by=generator)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Employee profile not found for current user")

    @extend_schema(
        summary="Generate summary report",
        description="Generate a summary report for given parameters",
        parameters=[
            OpenApiParameter('start_date', OpenApiTypes.DATE, OpenApiParameter.QUERY),
            OpenApiParameter('end_date', OpenApiTypes.DATE, OpenApiParameter.QUERY),
            OpenApiParameter('department', OpenApiTypes.INT, OpenApiParameter.QUERY),
            OpenApiParameter('employee', OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        tags=['Overtime Reports']
    )
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Generate overtime summary statistics"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department_id = request.query_params.get('department')
        employee_id = request.query_params.get('employee')

        queryset = OvertimeClaim.objects.all()

        if start_date:
            queryset = queryset.filter(work_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(work_date__lte=end_date)
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        # Calculate summary statistics
        summary_stats = queryset.aggregate(
            total_claims=Count('id'),
            total_overtime_hours=Sum('overtime_hours') or Decimal('0'),
            total_amount=Sum('total_amount') or Decimal('0'),
            weekend_hours=Sum('overtime_hours', filter=Q(is_weekend=True)) or Decimal('0'),
            holiday_hours=Sum('overtime_hours', filter=Q(is_holiday=True)) or Decimal('0'),
            emergency_hours=Sum('overtime_hours', filter=Q(is_emergency=True)) or Decimal('0'),
        )

        # Status breakdown
        status_counts = queryset.values('status').annotate(count=Count('id'))
        status_dict = {item['status']: item['count'] for item in status_counts}

        summary_stats.update({
            'pending_claims': status_dict.get('submitted', 0),
            'approved_claims': status_dict.get('approved', 0),
            'rejected_claims': status_dict.get('rejected', 0),
            'average_daily_overtime': (
                summary_stats['total_overtime_hours'] / summary_stats['total_claims']
                if summary_stats['total_claims'] > 0 else Decimal('0')
            ),
        })

        serializer = OvertimeSummarySerializer(summary_stats)
        return Response(serializer.data)

    @extend_schema(
        summary="Employee summary report",
        description="Generate per-employee overtime summary",
        parameters=[
            OpenApiParameter('start_date', OpenApiTypes.DATE, OpenApiParameter.QUERY),
            OpenApiParameter('end_date', OpenApiTypes.DATE, OpenApiParameter.QUERY),
            OpenApiParameter('department', OpenApiTypes.INT, OpenApiParameter.QUERY),
        ],
        tags=['Overtime Reports']
    )
    @action(detail=False, methods=['get'])
    def employee_summary(self, request):
        """Generate per-employee overtime summary"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        department_id = request.query_params.get('department')

        queryset = OvertimeClaim.objects.select_related('employee', 'employee__department')

        if start_date:
            queryset = queryset.filter(work_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(work_date__lte=end_date)
        if department_id:
            queryset = queryset.filter(employee__department_id=department_id)

        # Group by employee and calculate stats
        employee_stats = queryset.values(
            'employee__employee_id',
            'employee__first_name',
            'employee__last_name',
            'employee__department__name'
        ).annotate(
            total_claims=Count('id'),
            total_overtime_hours=Sum('overtime_hours'),
            total_amount=Sum('total_amount'),
            last_claim_date=models.Max('work_date'),
            pending_approvals=Count('id', filter=Q(status='submitted'))
        ).order_by('-total_overtime_hours')

        # Format the response data
        response_data = []
        for stat in employee_stats:
            response_data.append({
                'employee_id': stat['employee__employee_id'],
                'employee_name': f"{stat['employee__first_name']} {stat['employee__last_name']}",
                'department': stat['employee__department__name'] or '',
                'total_claims': stat['total_claims'],
                'total_overtime_hours': stat['total_overtime_hours'] or Decimal('0'),
                'total_amount': stat['total_amount'] or Decimal('0'),
                'avg_weekly_overtime': (
                    stat['total_overtime_hours'] / Decimal('4')
                    if stat['total_overtime_hours'] else Decimal('0')
                ),  # Rough weekly average
                'last_claim_date': stat['last_claim_date'],
                'pending_approvals': stat['pending_approvals'],
            })

        serializer = EmployeeOvertimeSummarySerializer(response_data, many=True)
        return Response(serializer.data)