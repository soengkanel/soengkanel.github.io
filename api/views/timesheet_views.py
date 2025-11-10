"""
Timesheet-related API views for NextHR.

This module contains all ViewSets and views related to timesheet management,
including timesheets and timesheet details.
"""
from rest_framework import viewsets, status, filters, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from project.models import Timesheet
from ..serializers import TimesheetSerializer
from ..mixins import TenantFilterMixin


class TimesheetViewSet(TenantFilterMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing timesheets.

    Provides CRUD operations for timesheets with tenant filtering,
    search, ordering, and approval workflows.
    """
    queryset = Timesheet.objects.none()  # Use .none() to prevent query during import
    serializer_class = TimesheetSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status']
    search_fields = ['timesheet_code']
    ordering_fields = ['start_date', 'created_at', 'status']
    ordering = ['-start_date']

    def get_queryset(self):
        """Get timesheet queryset at runtime"""
        return Timesheet.objects.all()

    def perform_create(self, serializer):
        super().perform_create(serializer)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit timesheet for approval"""
        timesheet = self.get_object()

        if timesheet.status != 'draft':
            return Response({'error': f'Cannot submit timesheet with status {timesheet.status}'},
                          status=status.HTTP_400_BAD_REQUEST)

        timesheet.status = 'submitted'
        timesheet.submitted_date = timezone.now()
        timesheet.save()

        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve timesheet"""
        timesheet = self.get_object()

        if timesheet.status != 'submitted':
            return Response({'error': f'Cannot approve timesheet with status {timesheet.status}'},
                          status=status.HTTP_400_BAD_REQUEST)

        timesheet.status = 'approved'
        timesheet.approved_date = timezone.now()
        timesheet.approved_by = request.user.employee if hasattr(request.user, 'employee') else None
        timesheet.save()

        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject timesheet"""
        timesheet = self.get_object()

        if timesheet.status != 'submitted':
            return Response({'error': f'Cannot reject timesheet with status {timesheet.status}'},
                          status=status.HTTP_400_BAD_REQUEST)

        timesheet.status = 'rejected'
        timesheet.save()

        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)