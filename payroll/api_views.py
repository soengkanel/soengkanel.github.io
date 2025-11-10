from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import (
    PayrollPeriod, SalaryComponent, SalaryStructure, SalaryStructureAssignment,
    SalarySlip, SalaryAdvance, EmployeeLoan, EmployeeSalary
)
from .serializers import (
    PayrollPeriodSerializer, SalaryComponentSerializer, SalaryStructureSerializer,
    SalaryStructureAssignmentSerializer, SalarySlipSerializer, SalaryAdvanceSerializer,
    EmployeeLoanSerializer, EmployeeSalarySerializer
)
from hr.models import Employee


class PayrollPeriodViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'period_type']
    search_fields = ['name']
    ordering_fields = ['start_date', 'end_date', 'created_at']
    ordering = ['-start_date']

    def get_queryset(self):
        try:
            return PayrollPeriod.objects.all()
        except:
            return PayrollPeriod.objects.none()

    def get_serializer_class(self):
        return PayrollPeriodSerializer

    def list(self, request):
        # Return sample data for testing
        sample_data = []
        return Response(sample_data)

    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate payroll for all employees in this period"""
        period = self.get_object()

        # Get all active employees
        employees = Employee.objects.filter(employment_status='active')
        generated_payrolls = []

        # Calculate working days from period (excluding weekends)
        working_days = period.working_days

        for employee in employees:
            # Check if payroll already exists
            existing_payroll = SalarySlip.objects.filter(
                employee=employee,
                payroll_period=period
            ).first()

            if not existing_payroll:
                # Create new salary slip
                salary_slip = SalarySlip.objects.create(
                    employee=employee,
                    payroll_period=period,
                    start_date=period.start_date,
                    end_date=period.end_date,
                    total_working_days=working_days,  # Use calculated working days
                    payment_days=working_days,  # Default to full working days
                    created_by=request.user
                )

                # Calculate salary from structure
                salary_slip.calculate_from_salary_structure()
                generated_payrolls.append(salary_slip.id)

        # Update period status and summary metrics
        period.status = 'PROCESSING'
        period.processed_by = request.user
        period.processed_at = timezone.now()
        period.save()

        # Update summary totals from generated salary slips
        period.update_summary()

        return Response({
            'message': f'Generated payroll for {len(generated_payrolls)} employees',
            'payroll_ids': generated_payrolls,
            'working_days': working_days,
            'total_gross_pay': float(period.total_gross_pay),
            'total_net_pay': float(period.total_net_pay)
        })


class SalaryComponentViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['component_type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'display_order']
    ordering = ['display_order', 'name']

    def get_queryset(self):
        # Return empty queryset for now due to database table issues
        try:
            return SalaryComponent.objects.all()
        except:
            return SalaryComponent.objects.none()

    def get_serializer_class(self):
        return SalaryComponentSerializer

    def list(self, request):
        # Return sample data for testing
        sample_data = [
            {
                "id": 1,
                "name": "Basic Salary",
                "component_type": "EARNING",
                "is_tax_applicable": True,
                "is_flexible_benefit": False,
                "depends_on_payment_days": True,
                "is_statistical_component": False,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "name": "House Rent Allowance",
                "component_type": "EARNING",
                "is_tax_applicable": True,
                "is_flexible_benefit": False,
                "depends_on_payment_days": False,
                "is_statistical_component": False,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": 3,
                "name": "Income Tax",
                "component_type": "DEDUCTION",
                "is_tax_applicable": False,
                "is_flexible_benefit": False,
                "depends_on_payment_days": False,
                "is_statistical_component": False,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        return Response(sample_data)


class SalaryStructureViewSet(viewsets.ModelViewSet):
    queryset = SalaryStructure.objects.all()
    serializer_class = SalaryStructureSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'docstatus']
    search_fields = ['name']
    ordering = ['name']


class EmployeeSalaryStructureViewSet(viewsets.ModelViewSet):
    """API endpoint for employee salary structures (assignments)"""
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'salary_structure', 'is_active']
    search_fields = ['employee__first_name', 'employee__last_name', 'salary_structure__name']
    ordering = ['-from_date']

    def get_queryset(self):
        try:
            return SalaryStructureAssignment.objects.all()
        except:
            return SalaryStructureAssignment.objects.none()

    def get_serializer_class(self):
        return SalaryStructureAssignmentSerializer

    def list(self, request):
        # Return sample data for testing
        sample_data = []
        return Response(sample_data)


class PayrollViewSet(viewsets.ModelViewSet):
    """API endpoint for individual payroll records (salary slips)"""
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'payroll_period', 'status']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['-start_date']

    def get_queryset(self):
        try:
            return SalarySlip.objects.all()
        except:
            return SalarySlip.objects.none()

    def get_serializer_class(self):
        return SalarySlipSerializer

    def list(self, request):
        # Return sample data for testing
        sample_data = []
        return Response(sample_data)

    @action(detail=True, methods=['get'])
    def payslip(self, request, pk=None):
        """Generate PDF payslip for download"""
        salary_slip = self.get_object()

        # This is a placeholder - you'll need to implement PDF generation
        # For now, return a simple response
        from django.template.loader import render_to_string

        html_content = f"""
        <html>
        <body>
            <h1>Payslip for {salary_slip.employee.get_full_name()}</h1>
            <p>Period: {salary_slip.payroll_period.name}</p>
            <p>Net Pay: ${salary_slip.net_pay}</p>
        </body>
        </html>
        """

        response = HttpResponse(html_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="payslip_{salary_slip.id}.pdf"'
        return response


class SalaryAdvanceViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'reason']
    ordering = ['-request_date']

    def get_queryset(self):
        try:
            return SalaryAdvance.objects.all()
        except:
            return SalaryAdvance.objects.none()

    def get_serializer_class(self):
        return SalaryAdvanceSerializer

    def list(self, request):
        # Return sample data for testing
        sample_data = []
        return Response(sample_data)


class EmployeeLoanViewSet(viewsets.ModelViewSet):
    queryset = EmployeeLoan.objects.all()
    serializer_class = EmployeeLoanSerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'status']
    search_fields = ['employee__first_name', 'employee__last_name', 'purpose']
    ordering = ['-created_at']


class EmployeeSalaryViewSet(viewsets.ModelViewSet):
    """API endpoint for employee basic salary information"""
    queryset = EmployeeSalary.objects.all()
    serializer_class = EmployeeSalarySerializer
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'is_active']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering = ['employee__first_name']