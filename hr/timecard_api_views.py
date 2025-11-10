from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q, Sum
from django.core.exceptions import ValidationError
from datetime import datetime, date
import calendar

from .timecard_models import Timecard, TimecardEntry
from .timecard_serializers import (
    TimecardSerializer,
    TimecardDetailSerializer,
    TimecardEntrySerializer,
    TimecardSubmitSerializer,
    BulkTimecardEntrySerializer
)
from .models import Employee


class TimecardViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing timecards
    """
    queryset = Timecard.objects.all()
    serializer_class = TimecardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Tenant-aware filtering - only show timecards for employees in current tenant
        # This is automatically handled by django-tenants, but we make it explicit
        queryset = queryset.select_related('employee', 'approved_by').prefetch_related('entries')

        # User permission filtering - employees can only see their own timecards unless they're managers
        if hasattr(user, 'employee'):
            employee = user.employee
            # If user is not a manager/supervisor, only show their own timecards
            if not employee.is_manager and not user.is_superuser:
                queryset = queryset.filter(employee=employee)

        # Filter by employee if specified
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee__employee_id=employee_id)

        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            try:
                queryset = queryset.filter(year=int(year))
            except (ValueError, TypeError):
                pass  # Ignore invalid year values

        # Filter by month
        month = self.request.query_params.get('month')
        if month:
            try:
                month_val = int(month)
                if 1 <= month_val <= 12:
                    queryset = queryset.filter(month=month_val)
            except (ValueError, TypeError):
                pass  # Ignore invalid month values

        # Filter by status
        approval_status = self.request.query_params.get('status')
        if approval_status and approval_status in ['draft', 'submitted', 'approved', 'rejected']:
            queryset = queryset.filter(approval_status=approval_status)

        # Filter by department
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__icontains=department)

        return queryset

    def get_serializer_class(self):
        if self.action in ['retrieve', 'create', 'update', 'partial_update']:
            return TimecardDetailSerializer
        return TimecardSerializer

    @action(detail=False, methods=['get'])
    def current_month(self, request):
        """Get or create timecard for current month for a specific employee"""
        employee_id = request.query_params.get('employee_id')

        if not employee_id:
            return Response(
                {'error': 'employee_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            employee = Employee.objects.get(employee_id=employee_id)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get current year and month
        today = date.today()
        year = today.year
        month = today.month

        # Get or create timecard
        timecard, created = Timecard.objects.get_or_create(
            employee=employee,
            year=year,
            month=month,
            defaults={
                'department': employee.department.name if employee.department else '',
                'position': employee.position.name if employee.position else ''
            }
        )

        # If newly created, create entries for all days in the month
        if created:
            self.create_month_entries(timecard)

        serializer = TimecardDetailSerializer(timecard)
        return Response(serializer.data)

    def create_month_entries(self, timecard):
        """Create blank entries for all days in the month"""
        year = timecard.year
        month = timecard.month
        num_days = calendar.monthrange(year, month)[1]

        entries = []
        for day in range(1, num_days + 1):
            entry_date = date(year, month, day)
            entry = TimecardEntry(
                timecard=timecard,
                date=entry_date,
                hours=0,
                project_name=""
            )
            entries.append(entry)

        TimecardEntry.objects.bulk_create(entries)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit timecard for approval"""
        timecard = self.get_object()

        # Check permissions - only the employee who owns the timecard can submit it
        if hasattr(request.user, 'employee') and timecard.employee != request.user.employee and not request.user.is_superuser:
            return Response(
                {'error': 'You can only submit your own timecards'},
                status=status.HTTP_403_FORBIDDEN
            )

        if timecard.approval_status not in ['draft', 'rejected']:
            return Response(
                {'error': 'Timecard can only be submitted from draft or rejected status'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate that timecard has at least some hours
        if timecard.total_hours <= 0:
            return Response(
                {'error': 'Cannot submit timecard with zero hours'},
                status=status.HTTP_400_BAD_REQUEST
            )

        timecard.approval_status = 'submitted'
        timecard.save()

        serializer = TimecardSerializer(timecard)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a submitted timecard"""
        timecard = self.get_object()
        serializer = TimecardSubmitSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if timecard.approval_status != 'submitted':
            return Response(
                {'error': 'Only submitted timecards can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check approval permissions
        if not request.user.is_superuser:
            try:
                approver = request.user.employee
                # Only managers can approve timecards
                if not approver.is_manager:
                    return Response(
                        {'error': 'Only managers can approve timecards'},
                        status=status.HTTP_403_FORBIDDEN
                    )
                # Employees cannot approve their own timecards
                if timecard.employee == approver:
                    return Response(
                        {'error': 'You cannot approve your own timecard'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            except AttributeError:
                return Response(
                    {'error': 'User is not linked to an employee'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            approver = None  # Superuser approval

        timecard.approval_status = 'approved'
        timecard.approved_by = approver  # Can be None for superuser
        timecard.approval_date = timezone.now()
        notes = serializer.validated_data.get('notes', '')
        if notes:
            timecard.notes = notes
        timecard.save()

        result_serializer = TimecardSerializer(timecard)
        return Response(result_serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a submitted timecard"""
        timecard = self.get_object()
        serializer = TimecardSubmitSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if timecard.approval_status != 'submitted':
            return Response(
                {'error': 'Only submitted timecards can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        timecard.approval_status = 'rejected'
        timecard.notes = serializer.validated_data.get('notes', '')
        timecard.save()

        result_serializer = TimecardSerializer(timecard)
        return Response(result_serializer.data)

    @action(detail=True, methods=['post'])
    def bulk_update_entries(self, request, pk=None):
        """Bulk update timecard entries"""
        timecard = self.get_object()

        # Check permissions - only the employee who owns the timecard can edit it
        if hasattr(request.user, 'employee') and timecard.employee != request.user.employee and not request.user.is_superuser:
            return Response(
                {'error': 'You can only edit your own timecards'},
                status=status.HTTP_403_FORBIDDEN
            )

        if timecard.approval_status not in ['draft', 'rejected']:
            return Response(
                {'error': 'Cannot modify entries for submitted or approved timecards'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = BulkTimecardEntrySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.update(timecard, serializer.validated_data)
        except ValidationError as e:
            return Response(
                {'error': f'Validation error: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to update entries: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        result_serializer = TimecardDetailSerializer(timecard)
        return Response(result_serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get timecard summary statistics"""
        employee_id = request.query_params.get('employee_id')
        year = request.query_params.get('year', date.today().year)

        queryset = Timecard.objects.filter(year=year)

        if employee_id:
            queryset = queryset.filter(employee__employee_id=employee_id)

        summary = {
            'year': year,
            'total_timecards': queryset.count(),
            'total_hours': queryset.aggregate(Sum('total_hours'))['total_hours__sum'] or 0,
            'by_status': {
                'draft': queryset.filter(approval_status='draft').count(),
                'submitted': queryset.filter(approval_status='submitted').count(),
                'approved': queryset.filter(approval_status='approved').count(),
                'rejected': queryset.filter(approval_status='rejected').count(),
            },
            'monthly_hours': []
        }

        # Get monthly breakdown
        for month in range(1, 13):
            month_qs = queryset.filter(month=month)
            month_hours = month_qs.aggregate(Sum('total_hours'))['total_hours__sum'] or 0
            summary['monthly_hours'].append({
                'month': month,
                'hours': month_hours,
                'count': month_qs.count()
            })

        return Response(summary)

    @action(detail=False, methods=['get', 'post'])
    def my_timecard(self, request):
        """Get or create timecard for current user for specified month/year"""
        if not hasattr(request.user, 'employee'):
            return Response(
                {'error': 'User is not linked to an employee'},
                status=status.HTTP_400_BAD_REQUEST
            )

        employee = request.user.employee
        year = request.query_params.get('year', request.data.get('year', date.today().year))
        month = request.query_params.get('month', request.data.get('month', date.today().month))

        try:
            year = int(year)
            month = int(month)
            if not (1 <= month <= 12):
                raise ValueError("Month must be between 1 and 12")
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid year or month'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get or create timecard
        timecard, created = Timecard.objects.get_or_create(
            employee=employee,
            year=year,
            month=month,
            defaults={
                'department': employee.department.name if employee.department else '',
                'position': employee.position.name if employee.position else ''
            }
        )

        # If newly created, create entries for all days in the month
        if created:
            self.create_month_entries(timecard)

        serializer = TimecardDetailSerializer(timecard)
        return Response(serializer.data)


class TimecardEntryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing individual timecard entries
    """
    queryset = TimecardEntry.objects.all()
    serializer_class = TimecardEntrySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Tenant-aware filtering and permission control
        queryset = queryset.select_related('timecard', 'timecard__employee', 'project', 'timesheet')

        # User permission filtering - employees can only see their own timecard entries unless they're managers
        if hasattr(user, 'employee'):
            employee = user.employee
            if not employee.is_manager and not user.is_superuser:
                queryset = queryset.filter(timecard__employee=employee)

        # Filter by timecard
        timecard_id = self.request.query_params.get('timecard_id')
        if timecard_id:
            try:
                queryset = queryset.filter(timecard_id=int(timecard_id))
            except (ValueError, TypeError):
                pass

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            try:
                queryset = queryset.filter(date__range=[start_date, end_date])
            except (ValueError, TypeError):
                pass

        # Filter by project
        project_id = self.request.query_params.get('project_id')
        if project_id:
            try:
                queryset = queryset.filter(project_id=int(project_id))
            except (ValueError, TypeError):
                pass

        return queryset