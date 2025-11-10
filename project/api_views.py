from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
import json

from .models import (
    Project, ProjectTask, ProjectTeamMember, ProjectType,
    ProjectTemplate, Timesheet, TimesheetDetail, ProjectMilestone,
    ProjectExpense, ProjectDocument, ProjectUpdate, ActivityTypeMaster,
    ProjectBudget, ProjectInvoice, TaskDependency, ProjectTimeTracking
)
from .serializers import (
    ProjectSerializer, ProjectTaskSerializer, ProjectTeamMemberSerializer,
    ProjectTypeSerializer, ProjectTemplateSerializer, TimesheetSerializer,
    TimesheetDetailSerializer, ProjectMilestoneSerializer,
    ProjectExpenseSerializer, ProjectDocumentSerializer,
    ProjectUpdateSerializer, ActivityTypeMasterSerializer,
    ProjectBudgetSerializer, ProjectInvoiceSerializer,
    ProjectTimeTrackingSerializer, ProjectTimeReportSerializer,
    TimesheetSubmissionSerializer, TimesheetApprovalSerializer
)


class ProjectTypeViewSet(viewsets.ModelViewSet):
    queryset = ProjectType.objects.all()
    serializer_class = ProjectTypeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = self.queryset.filter(is_active=True)
        return queryset.order_by('type_name')


class ProjectTemplateViewSet(viewsets.ModelViewSet):
    queryset = ProjectTemplate.objects.all()
    serializer_class = ProjectTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = self.queryset.filter(is_active=True)
        project_type = self.request.query_params.get('project_type')
        if project_type:
            queryset = queryset.filter(project_type_id=project_type)
        return queryset.order_by('template_name')
    
    @action(detail=True, methods=['post'])
    def apply_to_project(self, request, pk=None):
        template = self.get_object()
        project_id = request.data.get('project_id')
        
        if not project_id:
            return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            project = Project.objects.get(id=project_id)
            project.template = template
            project.project_type = template.project_type
            
            # Apply default tasks from template
            if template.default_tasks:
                for task_data in template.default_tasks:
                    ProjectTask.objects.create(
                        project=project,
                        task_name=task_data.get('name'),
                        description=task_data.get('description', ''),
                        estimated_hours=task_data.get('estimated_hours'),
                        priority=task_data.get('priority', 'medium'),
                        created_by=request.user
                    )
            
            project.save()
            return Response({'message': 'Template applied successfully'})
        
        except Project.DoesNotExist:

        
            pass
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = self.queryset.select_related(
            'project_type', 'project_manager', 'team_lead'
        ).prefetch_related('team_members', 'tasks')
        
        # Filtering
        status_filter = self.request.query_params.get('status')
        if status_filter:
            statuses = status_filter.split(',')
            queryset = queryset.filter(status__in=statuses)
        
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            priorities = priority_filter.split(',')
            queryset = queryset.filter(priority__in=priorities)
        
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(
                Q(project_manager_id=assigned_to) |
                Q(team_lead_id=assigned_to) |
                Q(team_members__employee_id=assigned_to)
            ).distinct()
        
        project_manager = self.request.query_params.get('project_manager')
        if project_manager:
            queryset = queryset.filter(project_manager_id=project_manager)
        
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(expected_start_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(expected_end_date__lte=date_to)
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(project_name__icontains=search) |
                Q(project_code__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        project = self.get_object()
        
        # Task statistics
        tasks = project.tasks.all()
        task_stats = {
            'total': tasks.count(),
            'completed': tasks.filter(status='completed').count(),
            'in_progress': tasks.filter(status='working').count(),
            'overdue': tasks.filter(
                expected_end_date__lt=timezone.now().date(),
                status__in=['open', 'working']
            ).count(),
        }
        
        # Budget statistics
        total_expenses = project.expenses.aggregate(total=Sum('amount'))['total'] or 0
        budget_stats = {
            'estimated': project.estimated_cost or 0,
            'actual': project.actual_cost or 0,
            'expenses': total_expenses,
            'remaining': (project.estimated_cost or 0) - (project.actual_cost or 0) - total_expenses
        }
        
        # Time statistics
        timesheet_entries = TimesheetDetail.objects.filter(project=project)
        time_stats = {
            'estimated': project.estimated_hours or 0,
            'logged': timesheet_entries.aggregate(total=Sum('hours'))['total'] or 0,
            'billable': timesheet_entries.filter(is_billable=True).aggregate(
                total=Sum('hours')
            )['total'] or 0,
        }
        
        return Response({
            'project_id': project.id,
            'task_stats': task_stats,
            'budget_stats': budget_stats,
            'time_stats': time_stats,
        })
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        original_project = self.get_object()
        
        # Create duplicate project
        duplicate_project = Project.objects.create(
            project_name=f"{original_project.project_name} (Copy)",
            description=original_project.description,
            project_type=original_project.project_type,
            template=original_project.template,
            company=original_project.company,
            department=original_project.department,
            priority=original_project.priority,
            estimated_cost=original_project.estimated_cost,
            estimated_hours=original_project.estimated_hours,
            billing_method=original_project.billing_method,
            is_milestone_tracking=original_project.is_milestone_tracking,
            collect_progress=original_project.collect_progress,
            created_by=request.user
        )
        
        # Copy team members
        for member in original_project.team_members.all():
            ProjectTeamMember.objects.create(
                project=duplicate_project,
                employee=member.employee,
                role=member.role,
                allocation_percentage=member.allocation_percentage,
                hourly_rate=member.hourly_rate
            )
        
        # Copy tasks
        task_mapping = {}
        for task in original_project.tasks.filter(parent_task__isnull=True):
            new_task = self._copy_task_recursive(task, duplicate_project, request.user, task_mapping)
        
        return Response({
            'message': 'Project duplicated successfully',
            'new_project_id': duplicate_project.id
        })
    
    def _copy_task_recursive(self, original_task, new_project, user, task_mapping, parent_task=None):
        new_task = ProjectTask.objects.create(
            project=new_project,
            parent_task=parent_task,
            task_name=original_task.task_name,
            description=original_task.description,
            priority=original_task.priority,
            estimated_hours=original_task.estimated_hours,
            is_milestone=original_task.is_milestone,
            is_group=original_task.is_group,
            created_by=user
        )
        
        task_mapping[original_task.id] = new_task
        
        # Copy subtasks
        for subtask in original_task.subtasks.all():
            self._copy_task_recursive(subtask, new_project, user, task_mapping, new_task)
        
        return new_task
    
    @action(detail=True, methods=['get'])
    def gantt_data(self, request, pk=None):
        project = self.get_object()
        tasks = project.tasks.select_related('assigned_to', 'parent_task').all()

        gantt_data = []
        for task in tasks:
            gantt_data.append({
                'id': str(task.id),
                'text': task.task_name,
                'start_date': task.expected_start_date.strftime('%Y-%m-%d') if task.expected_start_date else None,
                'end_date': task.expected_end_date.strftime('%Y-%m-%d') if task.expected_end_date else None,
                'duration': task.estimated_hours or 0,
                'progress': float(task.progress) / 100 if task.progress else 0,
                'parent': str(task.parent_task.id) if task.parent_task else None,
                'assigned_to': task.assigned_to.user.get_full_name() if task.assigned_to else None,
                'status': task.status,
                'priority': task.priority,
            })

        return Response({'data': gantt_data})

    @action(detail=True, methods=['get'])
    def time_tracking(self, request, pk=None):
        """Get detailed time tracking information for a project"""
        project = self.get_object()
        time_tracking_summary = project.get_time_tracking_summary()

        return Response({
            'project_id': project.id,
            'project_name': project.project_name,
            'project_code': project.project_code,
            **time_tracking_summary
        })

    @action(detail=True, methods=['get'])
    def timesheets(self, request, pk=None):
        """Get all timesheets for a project"""
        project = self.get_object()
        timesheets = project.get_project_timesheets()

        serializer = TimesheetSerializer(timesheets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def time_breakdown(self, request, pk=None):
        """Get monthly time breakdown for a project"""
        project = self.get_object()

        # Get year and month from query parameters
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        if year:
            year = int(year)
        if month:
            month = int(month)

        breakdown = project.get_monthly_time_breakdown(year=year, month=month)
        return Response(breakdown)

    @action(detail=True, methods=['post'])
    def update_time_tracking(self, request, pk=None):
        """Manually trigger time tracking update for a project"""
        project = self.get_object()
        time_tracking = project.update_project_time_tracking()

        serializer = ProjectTimeTrackingSerializer(time_tracking)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def employees_with_time(self, request, pk=None):
        """Get employees who have logged time on this project"""
        project = self.get_object()
        employees = project.get_project_employees_with_time()

        employee_data = []
        for employee in employees:
            # Get time summary for each employee
            timesheet_hours = TimesheetDetail.objects.filter(
                project=project,
                timesheet__employee=employee
            ).aggregate(
                total_hours=Sum('hours'),
                billable_hours=Sum('hours', filter=Q(is_billable=True))
            )

            timecard_hours = project.timecard_entries.aggregate(
                total_hours=Sum('hours'),
                billable_hours=Sum('hours', filter=Q(is_billable=True))
            )

            total_hours = (timesheet_hours['total_hours'] or 0) + (timecard_hours['total_hours'] or 0)
            billable_hours = (timesheet_hours['billable_hours'] or 0) + (timecard_hours['billable_hours'] or 0)

            employee_data.append({
                'employee_id': employee.id,
                'employee_name': employee.full_name,
                'employee_code': employee.employee_id,
                'total_hours': total_hours,
                'billable_hours': billable_hours,
                'department': employee.department.name if employee.department else None,
                'position': employee.position.name if employee.position else None
            })

        return Response(employee_data)


class ProjectTaskViewSet(viewsets.ModelViewSet):
    queryset = ProjectTask.objects.all()
    serializer_class = ProjectTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = self.queryset.select_related('project', 'assigned_to', 'parent_task')
        
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            statuses = status_filter.split(',')
            queryset = queryset.filter(status__in=statuses)
        
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)
        
        return queryset.order_by('expected_start_date', 'task_name')
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['put'])
    def update_status(self, request, pk=None):
        task = self.get_object()
        status = request.data.get('status')
        
        if status not in dict(ProjectTask.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.status = status
        
        # Update dates based on status
        if status == 'working' and not task.actual_start_date:
            task.actual_start_date = timezone.now().date()
        elif status == 'completed':
            task.actual_end_date = timezone.now().date()
            task.progress = 100
        
        task.save()
        
        # Update project progress
        project = task.project
        total_tasks = project.tasks.count()
        if total_tasks > 0:
            completed_tasks = project.tasks.filter(status='completed').count()
            project.percent_complete = (completed_tasks / total_tasks) * 100
            project.save()
        
        return Response({'message': 'Task status updated successfully'})
    
    @action(detail=False, methods=['post'])
    def bulk_assign(self, request):
        task_ids = request.data.get('task_ids', [])
        assigned_to_id = request.data.get('assigned_to')
        
        if not task_ids or not assigned_to_id:
            return Response({'error': 'task_ids and assigned_to are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        tasks = ProjectTask.objects.filter(id__in=task_ids)
        updated_count = tasks.update(assigned_to_id=assigned_to_id)
        
        return Response({'message': f'{updated_count} tasks assigned successfully'})


class ProjectTeamMemberViewSet(viewsets.ModelViewSet):
    queryset = ProjectTeamMember.objects.all()
    serializer_class = ProjectTeamMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = self.queryset.select_related('project', 'employee')
        
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.filter(is_active=True)
    
    @action(detail=False, methods=['get'])
    def availability(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({'error': 'project_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        project = get_object_or_404(Project, id=project_id)
        team_members = project.team_members.filter(is_active=True)
        
        availability_data = []
        for member in team_members:
            # Calculate current allocation across all active projects
            total_allocation = ProjectTeamMember.objects.filter(
                employee=member.employee,
                is_active=True,
                project__status__in=['open', 'in_progress']
            ).aggregate(total=Sum('allocation_percentage'))['total'] or 0
            
            availability_data.append({
                'employee_id': member.employee.id,
                'employee_name': member.employee.user.get_full_name(),
                'current_allocation': total_allocation,
                'available_capacity': 100 - total_allocation,
                'role': member.role,
            })
        
        return Response({'availability': availability_data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
    except:
        employee = None
    
    # Projects where user is involved
    if employee:
        my_projects = Project.objects.filter(
            Q(project_manager=employee) |
            Q(team_lead=employee) |
            Q(team_members__employee=employee)
        ).distinct()
        
        my_tasks = ProjectTask.objects.filter(
            assigned_to=employee,
            status__in=['open', 'working', 'pending_review']
        ).order_by('expected_end_date')[:10]
    else:
        my_projects = Project.objects.none()
        my_tasks = ProjectTask.objects.none()
    
    # Overall statistics
    stats = {
        'total_projects': Project.objects.filter(is_active=True).count(),
        'active_projects': Project.objects.filter(
            status__in=['open', 'in_progress']
        ).count(),
        'my_projects_count': my_projects.count(),
        'overdue_tasks': ProjectTask.objects.filter(
            expected_end_date__lt=timezone.now().date(),
            status__in=['open', 'working']
        ).count(),
        'pending_approvals': Timesheet.objects.filter(status='submitted').count(),
        'my_pending_tasks': my_tasks.count(),
    }
    
    # Recent updates
    recent_updates = ProjectUpdate.objects.select_related(
        'project', 'created_by'
    ).order_by('-created_at')[:5]
    
    updates_data = []
    for update in recent_updates:
        updates_data.append({
            'id': update.id,
            'project_name': update.project.project_name,
            'comment': update.comment,
            'created_by': update.created_by.get_full_name() if update.created_by else 'System',
            'created_at': update.created_at.isoformat(),
            'is_internal': update.is_internal
        })
    
    # Upcoming milestones
    upcoming_milestones = ProjectMilestone.objects.filter(
        milestone_date__gte=timezone.now().date(),
        status='pending'
    ).order_by('milestone_date')[:5]
    
    milestones_data = []
    for milestone in upcoming_milestones:
        milestones_data.append({
            'id': milestone.id,
            'project_name': milestone.project.project_name,
            'milestone_name': milestone.milestone_name,
            'milestone_date': milestone.milestone_date.isoformat(),
            'amount': milestone.amount
        })
    
    return Response({
        'stats': stats,
        'recent_updates': updates_data,
        'upcoming_milestones': milestones_data,
        'my_tasks': [
            {
                'id': task.id,
                'task_name': task.task_name,
                'project_name': task.project.project_name,
                'expected_end_date': task.expected_end_date.isoformat() if task.expected_end_date else None,
                'status': task.status,
                'priority': task.priority
            }
            for task in my_tasks
        ]
    })


# Enhanced Timesheet ViewSet with ERPNext-style functionality
class TimesheetViewSet(viewsets.ModelViewSet):
    queryset = Timesheet.objects.none()  # Use .none() to prevent query during import
    serializer_class = TimesheetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter timesheets based on permissions and query parameters"""
        queryset = Timesheet.objects.all()  # Get all timesheets at runtime

        # Filter by employee
        employee_param = self.request.query_params.get('employee')
        if employee_param:
            queryset = queryset.filter(employee_id=employee_param)

        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)

        # Filter by project (through details)
        project_param = self.request.query_params.get('project')
        if project_param:
            queryset = queryset.filter(details__project_id=project_param).distinct()

        return queryset.select_related(
            'employee', 'company', 'approved_by'
        ).prefetch_related('details__project', 'details__task', 'details__activity_type')

    def perform_create(self, serializer):
        """Set created_by when creating timesheet"""
        from hr.models import Employee

        if hasattr(self.request.user, 'employee'):
            employee = self.request.user.employee
        else:
            # Fallback to get employee by user
            employee = get_object_or_404(Employee, user=self.request.user)

        serializer.save(
            created_by=self.request.user,
            employee=employee if not serializer.validated_data.get('employee') else serializer.validated_data['employee']
        )

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """Submit timesheet for approval"""
        timesheet = self.get_object()

        if timesheet.status != 'draft':
            return Response(
                {'error': 'Only draft timesheets can be submitted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update timesheet status and timestamp
        timesheet.status = 'submitted'
        timesheet.submitted_date = timezone.now()
        if request.data.get('notes'):
            timesheet.notes = request.data['notes']
        timesheet.save()

        # Recalculate totals
        timesheet.calculate_totals()

        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve or reject timesheet"""
        timesheet = self.get_object()

        if timesheet.status != 'submitted':
            return Response(
                {'error': 'Only submitted timesheets can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        action_type = request.data.get('action', 'approve')
        notes = request.data.get('notes', '')

        if action_type == 'approve':
            timesheet.status = 'approved'
            timesheet.approved_date = timezone.now()
            if hasattr(request.user, 'employee'):
                timesheet.approved_by = request.user.employee
        elif action_type == 'reject':
            timesheet.status = 'rejected'

        if notes:
            timesheet.notes = notes

        timesheet.save()

        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel timesheet"""
        timesheet = self.get_object()

        if timesheet.status in ['approved', 'paid']:
            return Response(
                {'error': 'Cannot cancel approved or paid timesheets'},
                status=status.HTTP_400_BAD_REQUEST
            )

        timesheet.status = 'cancelled'
        timesheet.save()

        serializer = self.get_serializer(timesheet)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get timesheet summary"""
        timesheet = self.get_object()

        # Get project breakdown
        project_breakdown = timesheet.details.values(
            'project__project_name', 'project__project_code'
        ).annotate(
            total_hours=Sum('hours'),
            billable_hours=Sum('hours', filter=Q(is_billable=True)),
            total_amount=Sum('billing_amount')
        )

        return Response({
            'timesheet_code': timesheet.timesheet_code,
            'total_hours': timesheet.total_hours,
            'billable_hours': timesheet.total_billable_hours,
            'billable_amount': timesheet.total_billable_amount,
            'efficiency_rate': timesheet.efficiency_rate,
            'project_breakdown': list(project_breakdown)
        })


class ActivityTypeMasterViewSet(viewsets.ModelViewSet):
    queryset = ActivityTypeMaster.objects.all()
    serializer_class = ActivityTypeMasterSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(is_active=True).order_by('activity_name')


class ProjectMilestoneViewSet(viewsets.ModelViewSet):
    queryset = ProjectMilestone.objects.all()
    serializer_class = ProjectMilestoneSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = self.queryset.select_related('project', 'task')
        
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset.order_by('milestone_date')
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        milestone = self.get_object()
        milestone.status = 'completed'
        milestone.completed_date = timezone.now().date()
        milestone.save()

        return Response({'message': 'Milestone marked as completed'})


class TimesheetDetailViewSet(viewsets.ModelViewSet):
    """
    TimesheetDetail ViewSet for individual time entries
    """
    queryset = TimesheetDetail.objects.none()  # Use .none() to prevent query during import
    serializer_class = TimesheetDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter timesheet details based on query parameters"""
        queryset = TimesheetDetail.objects.all()  # Get all details at runtime

        # Filter by timesheet
        timesheet_param = self.request.query_params.get('timesheet')
        if timesheet_param:
            queryset = queryset.filter(timesheet_id=timesheet_param)

        # Filter by project
        project_param = self.request.query_params.get('project')
        if project_param:
            queryset = queryset.filter(project_id=project_param)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(activity_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(activity_date__lte=end_date)

        return queryset.select_related('timesheet', 'project', 'task', 'activity_type')

    def perform_create(self, serializer):
        """Update timesheet totals when creating detail"""
        detail = serializer.save()
        detail.timesheet.calculate_totals()

    def perform_update(self, serializer):
        """Update timesheet totals when updating detail"""
        detail = serializer.save()
        detail.timesheet.calculate_totals()

    def perform_destroy(self, instance):
        """Update timesheet totals when deleting detail"""
        timesheet = instance.timesheet
        super().perform_destroy(instance)
        timesheet.calculate_totals()


class ProjectTimeTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ProjectTimeTracking ViewSet for time tracking aggregates
    """
    queryset = ProjectTimeTracking.objects.all()
    serializer_class = ProjectTimeTrackingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter time tracking based on query parameters"""
        queryset = super().get_queryset()

        # Filter by project
        project_param = self.request.query_params.get('project')
        if project_param:
            queryset = queryset.filter(project_id=project_param)

        return queryset.select_related('project')

    @action(detail=True, methods=['post'])
    def recalculate(self, request, pk=None):
        """Manually trigger recalculation of time tracking totals"""
        time_tracking = self.get_object()
        time_tracking.recalculate_totals()

        serializer = self.get_serializer(time_tracking)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def project_time_report(request):
    """
    Generate time tracking reports for projects
    """
    # Get query parameters
    project_ids = request.query_params.getlist('project_ids[]')
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')

    # Base queryset
    projects = Project.objects.all()

    # Filter by project IDs if provided
    if project_ids:
        projects = projects.filter(id__in=project_ids)

    # Get time tracking data
    report_data = []
    for project in projects:
        time_tracking_summary = project.get_time_tracking_summary()

        # Apply date filtering if needed
        if start_date and end_date:
            # Filter timesheet details by date range
            filtered_totals = TimesheetDetail.objects.filter(
                project=project,
                activity_date__gte=start_date,
                activity_date__lte=end_date
            ).aggregate(
                total_hours=Sum('hours'),
                billable_hours=Sum('hours', filter=Q(is_billable=True)),
                billable_amount=Sum('billing_amount')
            )

            time_tracking_summary.update({
                'actual_hours': filtered_totals['total_hours'] or 0,
                'billable_hours': filtered_totals['billable_hours'] or 0,
                'billable_amount': filtered_totals['billable_amount'] or 0
            })

        report_data.append({
            'project_id': project.id,
            'project_name': project.project_name,
            'project_code': project.project_code,
            **time_tracking_summary
        })

    serializer = ProjectTimeReportSerializer(report_data, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def timesheet_bulk_operations(request):
    """
    Bulk operations on timesheets
    """
    operation = request.data.get('operation')
    timesheet_ids = request.data.get('timesheet_ids', [])

    if not operation or not timesheet_ids:
        return Response(
            {'error': 'Operation and timesheet_ids are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    timesheets = Timesheet.objects.filter(id__in=timesheet_ids)

    if operation == 'submit':
        # Submit multiple timesheets
        draft_timesheets = timesheets.filter(status='draft')
        draft_timesheets.update(
            status='submitted',
            submitted_date=timezone.now()
        )
        return Response({
            'message': f'{draft_timesheets.count()} timesheets submitted'
        })

    elif operation == 'approve':
        # Approve multiple timesheets
        submitted_timesheets = timesheets.filter(status='submitted')
        approved_by = getattr(request.user, 'employee', None)

        submitted_timesheets.update(
            status='approved',
            approved_date=timezone.now(),
            approved_by=approved_by
        )
        return Response({
            'message': f'{submitted_timesheets.count()} timesheets approved'
        })

    elif operation == 'reject':
        # Reject multiple timesheets
        submitted_timesheets = timesheets.filter(status='submitted')
        submitted_timesheets.update(status='rejected')
        return Response({
            'message': f'{submitted_timesheets.count()} timesheets rejected'
        })

    else:
        return Response(
            {'error': 'Invalid operation'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def timesheet_stats(request):
    """
    Get timesheet statistics and analytics
    """
    # Get query parameters
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    employee_id = request.query_params.get('employee')

    # Base queryset
    timesheets = Timesheet.objects.all()

    # Apply filters
    if start_date:
        timesheets = timesheets.filter(start_date__gte=start_date)
    if end_date:
        timesheets = timesheets.filter(end_date__lte=end_date)
    if employee_id:
        timesheets = timesheets.filter(employee_id=employee_id)

    # Calculate statistics
    stats = timesheets.aggregate(
        total_timesheets=Count('id'),
        draft_count=Count('id', filter=Q(status='draft')),
        submitted_count=Count('id', filter=Q(status='submitted')),
        approved_count=Count('id', filter=Q(status='approved')),
        rejected_count=Count('id', filter=Q(status='rejected')),
        total_hours=Sum('total_hours'),
        total_billable_hours=Sum('total_billable_hours'),
        total_billable_amount=Sum('total_billable_amount')
    )

    # Calculate average efficiency rate
    if stats['total_hours'] and stats['total_hours'] > 0:
        stats['avg_efficiency_rate'] = (stats['total_billable_hours'] / stats['total_hours']) * 100
    else:
        stats['avg_efficiency_rate'] = 0

    return Response(stats)