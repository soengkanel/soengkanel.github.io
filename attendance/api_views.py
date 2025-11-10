from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from datetime import datetime, time, timedelta, date

from .models import (
    BiometricDevice, WorkSchedule, EmployeeSchedule, AttendanceRecord,
    BreakRecord, OvertimeRequest, AttendanceCorrection, AttendancePolicy,
    ProjectAttendance
)


class BiometricDeviceViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['device_type', 'status', 'location']
    search_fields = ['name', 'device_id', 'location']
    ordering_fields = ['name', 'location', 'created_at']
    ordering = ['location', 'name']

    def get_queryset(self):
        try:
            return BiometricDevice.objects.filter(status='active')
        except:
            return BiometricDevice.objects.none()

    def list(self, request):
        # Return sample data for testing
        sample_data = [
            {
                "id": "1",
                "device_id": "FP001",
                "name": "Main Entrance Scanner",
                "device_type": "fingerprint",
                "location": "Main Building - Entrance",
                "ip_address": "192.168.1.100",
                "port": 4370,
                "serial_number": "FP2024001",
                "firmware_version": "v2.1.5",
                "status": "active",
                "last_sync": "2024-12-18T08:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-12-18T08:00:00Z"
            },
            {
                "id": "2",
                "device_id": "FP002",
                "name": "Side Entrance Scanner",
                "device_type": "fingerprint",
                "location": "Main Building - Side Entrance",
                "ip_address": "192.168.1.101",
                "port": 4370,
                "serial_number": "FP2024002",
                "firmware_version": "v2.1.5",
                "status": "active",
                "last_sync": "2024-12-18T08:00:00Z",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-12-18T08:00:00Z"
            }
        ]
        return Response(sample_data)


class WorkScheduleViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'flexible_hours']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        try:
            return WorkSchedule.objects.filter(is_active=True)
        except:
            return WorkSchedule.objects.none()

    def list(self, request):
        # Return sample data for testing
        sample_data = [
            {
                "id": "1",
                "name": "Standard 9-5",
                "code": "STD95",
                "description": "Standard Monday to Friday 9 AM to 5 PM schedule",
                "monday_start": "09:00:00",
                "monday_end": "17:00:00",
                "tuesday_start": "09:00:00",
                "tuesday_end": "17:00:00",
                "wednesday_start": "09:00:00",
                "wednesday_end": "17:00:00",
                "thursday_start": "09:00:00",
                "thursday_end": "17:00:00",
                "friday_start": "09:00:00",
                "friday_end": "17:00:00",
                "saturday_start": None,
                "saturday_end": None,
                "sunday_start": None,
                "sunday_end": None,
                "break_duration": 60,
                "break_start": "12:00:00",
                "flexible_hours": False,
                "core_hours_start": None,
                "core_hours_end": None,
                "required_hours_per_day": 8.0,
                "late_grace_period": 15,
                "early_leave_grace_period": 15,
                "is_active": True,
                "total_weekly_hours": 40.0,
                "working_days_count": 5,
                "avg_daily_hours": 8.0,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "2",
                "name": "Flexible Hours",
                "code": "FLEX",
                "description": "Flexible working hours with core hours 10 AM to 3 PM",
                "monday_start": "08:00:00",
                "monday_end": "18:00:00",
                "tuesday_start": "08:00:00",
                "tuesday_end": "18:00:00",
                "wednesday_start": "08:00:00",
                "wednesday_end": "18:00:00",
                "thursday_start": "08:00:00",
                "thursday_end": "18:00:00",
                "friday_start": "08:00:00",
                "friday_end": "18:00:00",
                "saturday_start": None,
                "saturday_end": None,
                "sunday_start": None,
                "sunday_end": None,
                "break_duration": 60,
                "break_start": "12:00:00",
                "flexible_hours": True,
                "core_hours_start": "10:00:00",
                "core_hours_end": "15:00:00",
                "required_hours_per_day": 8.0,
                "late_grace_period": 30,
                "early_leave_grace_period": 30,
                "is_active": True,
                "total_weekly_hours": 40.0,
                "working_days_count": 5,
                "avg_daily_hours": 8.0,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        return Response(sample_data)


class EmployeeScheduleViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'schedule', 'is_active']
    search_fields = ['employee__first_name', 'employee__last_name']
    ordering_fields = ['effective_from', 'created_at']
    ordering = ['-effective_from']

    def get_queryset(self):
        try:
            return EmployeeSchedule.objects.all()
        except:
            return EmployeeSchedule.objects.none()

    def list(self, request):
        # Return sample data for testing
        sample_data = [
            {
                "id": "1",
                "employee": "1",
                "employee_name": "John Doe",
                "schedule": "1",
                "schedule_name": "Standard 9-5",
                "effective_from": "2024-01-01",
                "effective_to": None,
                "is_active": True,
                "notes": "Standard working schedule",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        return Response(sample_data)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'status', 'date', 'is_manual_entry']
    search_fields = ['employee__first_name', 'employee__last_name', 'notes']
    ordering_fields = ['date', 'created_at', 'status']
    ordering = ['-date']

    def get_queryset(self):
        try:
            return AttendanceRecord.objects.all()
        except:
            return AttendanceRecord.objects.none()

    def list(self, request):
        # Return sample data for testing
        sample_data = [
            {
                "id": "1",
                "employee": "1",
                "employee_name": "John Doe",
                "date": "2024-12-18",
                "schedule": "1",
                "schedule_name": "Standard 9-5",
                "clock_in": "2024-12-18T08:45:00Z",
                "clock_out": "2024-12-18T17:15:00Z",
                "clock_in_device": "1",
                "clock_in_device_name": "Main Entrance Scanner",
                "clock_out_device": "1",
                "clock_out_device_name": "Main Entrance Scanner",
                "total_hours": 8.5,
                "overtime_hours": 0.5,
                "late_minutes": 0,
                "early_leave_minutes": 0,
                "status": "present",
                "is_manual_entry": False,
                "manual_entry_reason": "",
                "approved_by": None,
                "approved_by_name": None,
                "approved_at": None,
                "notes": "",
                "created_at": "2024-12-18T08:45:00Z",
                "updated_at": "2024-12-18T17:15:00Z"
            },
            {
                "id": "2",
                "employee": "1",
                "employee_name": "John Doe",
                "date": "2024-12-17",
                "schedule": "1",
                "schedule_name": "Standard 9-5",
                "clock_in": "2024-12-17T09:15:00Z",
                "clock_out": "2024-12-17T17:00:00Z",
                "clock_in_device": "2",
                "clock_in_device_name": "Side Entrance Scanner",
                "clock_out_device": "1",
                "clock_out_device_name": "Main Entrance Scanner",
                "total_hours": 7.75,
                "overtime_hours": 0,
                "late_minutes": 15,
                "early_leave_minutes": 0,
                "status": "late",
                "is_manual_entry": False,
                "manual_entry_reason": "",
                "approved_by": None,
                "approved_by_name": None,
                "approved_at": None,
                "notes": "Traffic delay",
                "created_at": "2024-12-17T09:15:00Z",
                "updated_at": "2024-12-17T17:00:00Z"
            }
        ]
        return Response(sample_data)

    @action(detail=False, methods=['post'])
    def clock_in(self, request):
        """Clock in an employee"""
        employee_id = request.data.get('employee')
        device_id = request.data.get('device')

        # Create sample response
        return Response({
            "id": "new_record_id",
            "employee": employee_id,
            "employee_name": "John Doe",
            "date": timezone.now().date().isoformat(),
            "clock_in": timezone.now().isoformat(),
            "clock_out": None,
            "status": "present",
            "total_hours": 0,
            "overtime_hours": 0,
            "late_minutes": 0,
            "early_leave_minutes": 0,
            "is_manual_entry": False,
            "created_at": timezone.now().isoformat(),
            "updated_at": timezone.now().isoformat()
        })

    @action(detail=True, methods=['post'])
    def clock_out(self, request, pk=None):
        """Clock out an employee"""
        device_id = request.data.get('device')

        # Create sample response
        return Response({
            "id": pk,
            "employee": "1",
            "employee_name": "John Doe",
            "date": timezone.now().date().isoformat(),
            "clock_in": "2024-12-18T09:00:00Z",
            "clock_out": timezone.now().isoformat(),
            "status": "present",
            "total_hours": 8.0,
            "overtime_hours": 0,
            "late_minutes": 0,
            "early_leave_minutes": 0,
            "is_manual_entry": False,
            "created_at": "2024-12-18T09:00:00Z",
            "updated_at": timezone.now().isoformat()
        })

    @action(detail=True, methods=['get'])
    def breaks(self, request, pk=None):
        """Get breaks for an attendance record"""
        return Response([
            {
                "id": "1",
                "attendance": pk,
                "break_type": "lunch",
                "start_time": "2024-12-18T12:00:00Z",
                "end_time": "2024-12-18T13:00:00Z",
                "duration_minutes": 60,
                "notes": "Lunch break",
                "created_at": "2024-12-18T12:00:00Z"
            }
        ])

    @action(detail=True, methods=['post'])
    def start_break(self, request, pk=None):
        """Start a break"""
        break_type = request.data.get('break_type', 'lunch')

        return Response({
            "id": "new_break_id",
            "attendance": pk,
            "break_type": break_type,
            "start_time": timezone.now().isoformat(),
            "end_time": None,
            "duration_minutes": 0,
            "notes": "",
            "created_at": timezone.now().isoformat()
        })

    @action(detail=False, methods=['post'])
    def bulk_mark_project_attendance(self, request):
        """Bulk mark attendance for multiple employees on a project"""
        project_id = request.data.get('project_id')
        date_str = request.data.get('date', timezone.now().date().isoformat())
        employee_attendance = request.data.get('employee_attendance', [])
        marked_by = request.data.get('marked_by')

        if not project_id or not employee_attendance:
            return Response({
                'error': 'project_id and employee_attendance are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Parse the date
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            results = []
            errors = []

            for item in employee_attendance:
                employee_id = item.get('employee_id')
                attendance_status = item.get('status', 'present')
                clock_in_time = item.get('clock_in')
                clock_out_time = item.get('clock_out')
                notes = item.get('notes', '')

                if not employee_id:
                    errors.append({'employee_id': 'missing', 'error': 'Employee ID is required'})
                    continue

                # For demo purposes, create a sample response
                # In production, you would:
                    pass
                # 1. Get or create AttendanceRecord for the employee and date
                # 2. Update attendance status, clock times, etc.
                # 3. Link to project if needed (through TimecardEntry)
                # 4. Validate permissions (ensure marked_by can mark attendance for this project)

                attendance_record = {
                    "id": f"bulk_{employee_id}_{attendance_date}",
                    "employee": employee_id,
                    "employee_name": f"Employee {employee_id}",  # Would fetch from Employee model
                    "date": date_str,
                    "project_id": project_id,
                    "schedule": "1",
                    "schedule_name": "Standard 9-5",
                    "clock_in": clock_in_time,
                    "clock_out": clock_out_time,
                    "clock_in_device": None,
                    "clock_out_device": None,
                    "total_hours": 8.0 if attendance_status == 'present' else 0,
                    "overtime_hours": 0,
                    "late_minutes": 0,
                    "early_leave_minutes": 0,
                    "status": attendance_status,
                    "is_manual_entry": True,
                    "manual_entry_reason": f"Bulk marked by manager for project {project_id}",
                    "approved_by": marked_by,
                    "approved_by_name": f"Manager {marked_by}",
                    "approved_at": timezone.now().isoformat(),
                    "notes": notes,
                    "created_at": timezone.now().isoformat(),
                    "updated_at": timezone.now().isoformat()
                }

                results.append(attendance_record)

            response_data = {
                "success": True,
                "message": f"Bulk attendance marked for {len(results)} employees",
                "project_id": project_id,
                "date": date_str,
                "marked_by": marked_by,
                "results": results,
                "errors": errors,
                "summary": {
                    "total_employees": len(employee_attendance),
                    "successful": len(results),
                    "failed": len(errors),
                    "present": len([r for r in results if r['status'] == 'present']),
                    "absent": len([r for r in results if r['status'] == 'absent']),
                    "late": len([r for r in results if r['status'] == 'late']),
                    "half_day": len([r for r in results if r['status'] == 'half_day'])
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({
                'error': f'Invalid date format: {e}'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def project_breakdown(self, request, pk=None):
        """Get project hours breakdown for an attendance record"""
        attendance = self.get_object()
        project_hours = attendance.get_project_hours_breakdown()

        return Response({
            'attendance_id': pk,
            'employee': {
                'id': attendance.employee.id,
                'name': attendance.employee.full_name
            },
            'date': attendance.date,
            'total_hours': float(attendance.total_hours),
            'project_breakdown': [
                {
                    'project_name': project_name,
                    'hours': breakdown['hours'],
                    'billable_hours': breakdown['billable_hours'],
                    'project_id': breakdown['project'].id if breakdown['project'] else None,
                    'entries_count': len(breakdown['entries'])
                }
                for project_name, breakdown in project_hours.items()
            ],
            'utilization_rate': attendance.project_utilization_rate,
            'has_project_time': attendance.has_project_time_logged
        })

    @action(detail=True, methods=['post'])
    def assign_project(self, request, pk=None):
        """Assign or update project for attendance record"""
        attendance = self.get_object()
        project_id = request.data.get('project_id')
        allocated_hours = request.data.get('allocated_hours', 8)
        work_location = request.data.get('work_location', '')
        is_primary = request.data.get('is_primary_project', False)

        try:
            from project.models import Project
            project = Project.objects.get(id=project_id) if project_id else None

            # Check if employee can work on this project
            if project and not attendance.can_work_on_project(project):
                return Response({
                    'error': 'Employee is not authorized to work on this project'
                }, status=status.HTTP_403_FORBIDDEN)

            # Update current project in attendance
            if is_primary:
                attendance.current_project = project
                attendance.location = work_location
                attendance.save(update_fields=['current_project', 'location'])

            # Create or update project attendance
            if project:
                project_attendance, created = ProjectAttendance.objects.get_or_create(
                    attendance=attendance,
                    project=project,
                    defaults={
                        'allocated_hours': allocated_hours,
                        'work_location': work_location,
                        'is_primary_project': is_primary,
                        'status': 'planned'
                    }
                )

                if not created:
                    project_attendance.allocated_hours = allocated_hours
                    project_attendance.work_location = work_location
                    project_attendance.is_primary_project = is_primary
                    project_attendance.save()

                # Sync with timecard data
                project_attendance.sync_actual_hours()

                return Response({
                    'success': True,
                    'project_attendance': {
                        'id': project_attendance.id,
                        'project_name': project.project_name,
                        'allocated_hours': float(project_attendance.allocated_hours),
                        'actual_hours': float(project_attendance.actual_hours),
                        'utilization_rate': float(project_attendance.utilization_rate),
                        'hours_variance': float(project_attendance.hours_variance),
                        'is_primary_project': project_attendance.is_primary_project,
                        'status': project_attendance.status
                    }
                })
            else:
                return Response({
                    'error': 'Project ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)

        except Project.DoesNotExist:
            return Response({
                'error': 'Project not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def sync_timecard(self, request, pk=None):
        """Sync attendance record with timecard data"""
        attendance = self.get_object()

        try:
            attendance.sync_with_timecard()

            return Response({
                'success': True,
                'updated_data': {
                    'current_project': {
                        'id': attendance.current_project.id if attendance.current_project else None,
                        'name': attendance.current_project.project_name if attendance.current_project else None
                    },
                    'total_hours': float(attendance.total_hours),
                    'project_utilization_rate': attendance.project_utilization_rate,
                    'has_project_time_logged': attendance.has_project_time_logged
                }
            })

        except Exception as e:
            return Response({
                'error': f'Sync failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def project_summary(self, request):
        """Get attendance summary by project for a specific date"""
        date_str = request.query_params.get('date', timezone.now().date().isoformat())

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Get all attendance records for the date with project assignments
            attendance_records = AttendanceRecord.objects.filter(
                date=target_date,
                status__in=['present', 'late', 'early_leave']
            ).select_related('employee', 'current_project').prefetch_related('project_assignments__project')

            project_summary = {}

            for attendance in attendance_records:
                # Group by current project
                if attendance.current_project:
                    project_id = attendance.current_project.id
                    project_name = attendance.current_project.project_name

                    if project_id not in project_summary:
                        project_summary[project_id] = {
                            'project': {
                                'id': project_id,
                                'name': project_name,
                                'code': attendance.current_project.project_code
                            },
                            'employees': [],
                            'total_employees': 0,
                            'total_hours': 0,
                            'total_billable_hours': 0,
                            'locations': set()
                        }

                    project_hours = attendance.get_project_hours_breakdown()
                    project_data = project_hours.get(project_name, {'hours': 0, 'billable_hours': 0})

                    project_summary[project_id]['employees'].append({
                        'id': attendance.employee.id,
                        'name': attendance.employee.full_name,
                        'status': attendance.status,
                        'clock_in': attendance.clock_in.isoformat() if attendance.clock_in else None,
                        'clock_out': attendance.clock_out.isoformat() if attendance.clock_out else None,
                        'total_hours': float(attendance.total_hours),
                        'project_hours': project_data['hours'],
                        'billable_hours': project_data['billable_hours'],
                        'location': attendance.location,
                        'is_remote': attendance.is_remote_work
                    })

                    project_summary[project_id]['total_employees'] += 1
                    project_summary[project_id]['total_hours'] += project_data['hours']
                    project_summary[project_id]['total_billable_hours'] += project_data['billable_hours']

                    if attendance.location:
                        project_summary[project_id]['locations'].add(attendance.location)

            # Convert to list and clean up
            result = []
            for project_data in project_summary.values():
                project_data['locations'] = list(project_data['locations'])
                result.append(project_data)

            return Response({
                'date': date_str,
                'total_projects': len(result),
                'projects': result
            })

        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProjectAttendanceViewSet(viewsets.ModelViewSet):
    """API endpoints for project attendance tracking"""
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'attendance__employee', 'attendance__date', 'status', 'is_primary_project']
    search_fields = ['project__project_name', 'attendance__employee__first_name', 'attendance__employee__last_name']
    ordering_fields = ['attendance__date', 'allocated_hours', 'actual_hours']
    ordering = ['-attendance__date']

    def get_queryset(self):
        try:
            return ProjectAttendance.objects.select_related(
                'attendance__employee', 'project'
            ).all()
        except:
            return ProjectAttendance.objects.none()

    @action(detail=False, methods=['get'])
    def daily_summary(self, request):
        """Get daily project attendance summary"""
        date_str = request.query_params.get('date', timezone.now().date().isoformat())
        project_id = request.query_params.get('project_id')

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            queryset = self.get_queryset().filter(attendance__date=target_date)
            if project_id:
                queryset = queryset.filter(project_id=project_id)

            summary_data = []
            for pa in queryset:
                summary_data.append({
                    'id': pa.id,
                    'employee': {
                        'id': pa.attendance.employee.id,
                        'name': pa.attendance.employee.full_name
                    },
                    'project': {
                        'id': pa.project.id,
                        'name': pa.project.project_name,
                        'code': pa.project.project_code
                    },
                    'attendance_status': pa.attendance.status,
                    'allocated_hours': float(pa.allocated_hours),
                    'actual_hours': float(pa.actual_hours),
                    'utilization_rate': float(pa.utilization_rate),
                    'hours_variance': float(pa.hours_variance),
                    'work_location': pa.work_location,
                    'is_primary_project': pa.is_primary_project,
                    'status': pa.status,
                    'approved_by': pa.approved_by.full_name if pa.approved_by else None
                })

            return Response({
                'date': date_str,
                'project_assignments': summary_data,
                'summary': {
                    'total_assignments': len(summary_data),
                    'total_allocated_hours': sum(pa['allocated_hours'] for pa in summary_data),
                    'total_actual_hours': sum(pa['actual_hours'] for pa in summary_data),
                    'avg_utilization_rate': sum(pa['utilization_rate'] for pa in summary_data) / len(summary_data) if summary_data else 0
                }
            })

        except ValueError:
            return Response({
                'error': 'Invalid date format. Use YYYY-MM-DD'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'error': f'An error occurred: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BreakRecordViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['break_type', 'attendance']
    ordering_fields = ['start_time', 'created_at']
    ordering = ['-start_time']

    def get_queryset(self):
        try:
            return BreakRecord.objects.all()
        except:
            return BreakRecord.objects.none()

    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a break"""
        return Response({
            "id": pk,
            "attendance": "1",
            "break_type": "lunch",
            "start_time": "2024-12-18T12:00:00Z",
            "end_time": timezone.now().isoformat(),
            "duration_minutes": 60,
            "notes": "",
            "created_at": "2024-12-18T12:00:00Z"
        })


class OvertimeRequestViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['employee', 'status', 'date']
    search_fields = ['reason', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['date', 'created_at', 'status']
    ordering = ['-date']

    def get_queryset(self):
        try:
            return OvertimeRequest.objects.all()
        except:
            return OvertimeRequest.objects.none()

    def list(self, request):
        # Return sample data for testing
        sample_data = [
            {
                "id": "1",
                "employee": "1",
                "employee_name": "John Doe",
                "date": "2024-12-20",
                "start_time": "18:00:00",
                "end_time": "20:00:00",
                "hours": 2.0,
                "reason": "Project deadline completion",
                "status": "pending",
                "requested_by": "1",
                "requested_by_name": "John Doe",
                "approved_by": None,
                "approved_by_name": None,
                "approved_at": None,
                "rejection_reason": "",
                "overtime_rate": 1.5,
                "amount": None,
                "created_at": "2024-12-18T10:00:00Z",
                "updated_at": "2024-12-18T10:00:00Z"
            }
        ]
        return Response(sample_data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve overtime request"""
        return Response({
            "id": pk,
            "status": "approved",
            "approved_by": "2",
            "approved_by_name": "Jane Smith",
            "approved_at": timezone.now().isoformat(),
            "message": "Overtime request approved successfully"
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject overtime request"""
        rejection_reason = request.data.get('rejection_reason', '')

        return Response({
            "id": pk,
            "status": "rejected",
            "rejection_reason": rejection_reason,
            "message": "Overtime request rejected"
        })


class AttendanceCorrectionViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['requested_by', 'status', 'correction_type']
    search_fields = ['reason', 'requested_by__first_name', 'requested_by__last_name']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        try:
            return AttendanceCorrection.objects.all()
        except:
            return AttendanceCorrection.objects.none()

    def list(self, request):
        # Return sample data for testing
        sample_data = [
            {
                "id": "1",
                "attendance": "1",
                "attendance_date": "2024-12-17",
                "requested_by": "1",
                "requested_by_name": "John Doe",
                "correction_type": "clock_in",
                "new_clock_in": "2024-12-17T08:55:00Z",
                "new_clock_out": None,
                "new_status": None,
                "reason": "Forgot to clock in on time due to fingerprint scanner issue",
                "supporting_document": None,
                "status": "pending",
                "approved_by": None,
                "approved_by_name": None,
                "approved_at": None,
                "rejection_reason": "",
                "created_at": "2024-12-17T18:00:00Z",
                "updated_at": "2024-12-17T18:00:00Z"
            }
        ]
        return Response(sample_data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve attendance correction"""
        return Response({
            "id": pk,
            "status": "approved",
            "approved_by": "2",
            "approved_by_name": "Jane Smith",
            "approved_at": timezone.now().isoformat(),
            "message": "Attendance correction approved successfully"
        })

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject attendance correction"""
        rejection_reason = request.data.get('rejection_reason', '')

        return Response({
            "id": pk,
            "status": "rejected",
            "rejection_reason": rejection_reason,
            "message": "Attendance correction rejected"
        })


class ActivityTypeViewSet(viewsets.ModelViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['activity_type', 'is_billable', 'is_active']
    search_fields = ['activity_name']
    ordering_fields = ['activity_name', 'created_at']
    ordering = ['activity_name']

    def get_queryset(self):
        try:
            from project.models import ActivityTypeMaster
            return ActivityTypeMaster.objects.filter(is_active=True)
        except:
            from project.models import ActivityTypeMaster
            return ActivityTypeMaster.objects.none()

    def list(self, request):
        # Return sample data for testing
        sample_data = [
            {
                "id": "1",
                "activity_name": "Development",
                "activity_type": "execution",
                "billing_rate": 100.00,
                "costing_rate": 50.00,
                "is_billable": True,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "2",
                "activity_name": "Testing",
                "activity_type": "testing",
                "billing_rate": 80.00,
                "costing_rate": 40.00,
                "is_billable": True,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": "3",
                "activity_name": "Meeting",
                "activity_type": "meeting",
                "billing_rate": 120.00,
                "costing_rate": 60.00,
                "is_billable": True,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        return Response(sample_data)


class AttendanceStatsViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        """Get attendance statistics"""
        sample_stats = {
            "total_employees": 25,
            "present_today": 22,
            "absent_today": 3,
            "late_today": 5,
            "on_break": 3,
            "early_leaves": 1,
            "attendance_rate": 88,
            "avg_hours_today": 7.8,
            "overtime_hours_today": 12.5,
            "pending_corrections": 2,
            "pending_overtime_requests": 3
        }
        return Response(sample_stats)


class TimesheetStatsViewSet(viewsets.ViewSet):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        """Get timesheet statistics"""
        sample_stats = {
            "total_timesheets": 12,
            "draft_timesheets": 2,
            "submitted_timesheets": 3,
            "approved_timesheets": 7,
            "rejected_timesheets": 0,
            "total_hours_logged": 450.5,
            "total_billable_hours": 398.0,
            "total_billable_amount": 39800.00,
            "avg_hours_per_employee": 37.5
        }
        return Response(sample_stats)