from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count, Sum, Avg
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils import timezone
from django.urls import reverse
from datetime import datetime, timedelta
import json

from .models import (
    Project, ProjectTask, ProjectTeamMember, ProjectType,
    ProjectTemplate, Timesheet, TimesheetDetail, ProjectMilestone,
    ProjectExpense, ProjectDocument, ProjectUpdate, Team, TeamMember, ProjectSettings
)
from .forms import (
    ProjectForm, ProjectTaskForm, TeamMemberForm,
    TimesheetEntryForm, ProjectFilterForm, QuickTaskForm, ProjectSettingsForm
)


@login_required
def project_list(request):
    """Main project list view with filtering and search"""
    projects = Project.objects.select_related(
        'project_manager', 'created_by'
    ).prefetch_related('team_members')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        projects = projects.filter(
            Q(project_name__icontains=search) |
            Q(project_code__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Status filter
    status = request.GET.get('status')
    if status:
        projects = projects.filter(status=status)
    
    # Priority filter
    priority = request.GET.get('priority')
    if priority:
        projects = projects.filter(priority=priority)

    # Team filter
    team_id = request.GET.get('team')
    if team_id:
        try:
            team = Team.objects.get(id=team_id)
            # Filter projects that have team members from this team
            team_member_employees = team.team_members.filter(is_active=True).values_list('employee_id', flat=True)
            projects = projects.filter(team_members__employee_id__in=team_member_employees).distinct()
        except (Team.DoesNotExist, ValueError):
            pass

    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        projects = projects.filter(expected_start_date__gte=date_from)
    if date_to:
        projects = projects.filter(expected_end_date__lte=date_to)
    
    # Sorting
    sort = request.GET.get('sort', '-created_at')
    projects = projects.order_by(sort)
    
    # Pagination
    paginator = Paginator(projects, 20)
    page = request.GET.get('page', 1)
    projects_page = paginator.get_page(page)
    
    # Stats for dashboard
    stats = {
        'total': projects.count(),
        'open': projects.filter(status='open').count(),
        'in_progress': projects.filter(status='in_progress').count(),
        'completed': projects.filter(status='completed').count(),
        'overdue': projects.filter(status='overdue').count(),
    }
    
    if request.headers.get('HX-Request'):
        # Return only the project cards for HTMX requests
        return render(request, 'project/partials/project_cards.html', {
            'projects': projects_page,
        })
    
    # Get teams for filter dropdown
    teams = Team.objects.filter(status='active').order_by('team_name')

    return render(request, 'project/project_list.html', {
        'projects': projects_page,
        'stats': stats,
        'filter_form': ProjectFilterForm(request.GET),
        'teams': teams,
    })


@login_required
def project_detail(request, project_id):
    """Project detail view with tabs for different sections"""
    project = get_object_or_404(
        Project.objects.select_related(
            'project_manager', 'created_by'
        ).prefetch_related(
            'team_members__employee',
            'tasks'
            # TODO: Fix schema - these tables use UUID foreign keys while project uses bigint
            # 'milestones',
            # 'documents',
            # 'expenses'
        ),
        id=project_id
    )
    
    # Get active tab from request
    tab = request.GET.get('tab', 'overview')
    
    # Calculate project statistics
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
    
    # Budget summary
    # TODO: Fix expenses table - currently uses UUID foreign key while project uses bigint
    total_expenses = 0

    budget_stats = {
        'estimated': project.estimated_cost or 0,
        'actual': project.actual_cost or 0,
        'expenses': total_expenses,
        'remaining': (project.estimated_cost or 0) - (project.actual_cost or 0) - total_expenses
    }
    
    # Time tracking summary
    # TODO: Fix timesheet_details table - currently uses UUID foreign key while project uses bigint
    time_stats = {
        'estimated': 0,
        'logged': 0,
        'billable': 0,
    }

    # Milestone statistics
    # TODO: Fix milestone table - currently uses UUID foreign key while project uses bigint
    # milestones = project.milestones.all()
    today = timezone.now().date()
    milestone_stats = {
        'total': 0,
        'completed': 0,
        'pending': 0,
        'overdue': 0,
        'critical': 0,
    }

    # Expense statistics
    # TODO: Fix expenses table - currently uses UUID foreign key while project uses bigint
    expense_stats = {
        'total': 0,
        'billable': 0,
        'approved': 0,
        'submitted_count': 0,
    }

    # Get available employees for team member addition
    from hr.models import Employee
    current_member_ids = project.team_members.values_list('employee_id', flat=True)
    available_employees = Employee.objects.exclude(id__in=current_member_ids).select_related('user').order_by('user__first_name', 'user__last_name')

    # Get all active employees for task assignment (not just team members)
    all_employees = Employee.objects.filter(employment_status='active').select_related('user').order_by('user__first_name', 'user__last_name')

    # Format employees data with email for autocomplete
    all_employees_data = []
    for emp in all_employees:
        all_employees_data.append({
            'id': emp.id,
            'name': emp.get_full_name(),
            'email': emp.email if emp.email else (emp.user.email if emp.user else ''),
            'initials': emp.get_full_name()[:2].upper() if emp.get_full_name() else ''
        })

    # Get or create project settings for settings tab
    settings_form = None
    if tab == 'settings':
        settings, created = ProjectSettings.objects.get_or_create(
            project=project,
            defaults={'created_by': request.user}
        )
        settings_form = ProjectSettingsForm(instance=settings)

    context = {
        'project': project,
        'tab': tab,
        'task_stats': task_stats,
        'budget_stats': budget_stats,
        'time_stats': time_stats,
        'milestone_stats': milestone_stats,
        'expense_stats': expense_stats,
        'milestones': [],  # TODO: Fix milestone table schema (UUID vs bigint)
        'expenses': [],  # TODO: Fix expenses table schema (UUID vs bigint)
        'documents': [],  # TODO: Fix documents table schema (UUID vs bigint)
        'today': timezone.now().date(),
        'available_employees': available_employees,
        'all_employees': all_employees,  # All active employees for task assignment
        'all_employees_data': all_employees_data,  # Formatted employee data with email
        'settings_form': settings_form,
    }

    # Return appropriate template based on tab
    if request.headers.get('HX-Request'):
        template_map = {
            'overview': 'project/partials/project_overview.html',
            'tasks': 'project/partials/project_tasks.html',
            'team': 'project/partials/project_team.html',
            'milestones': 'project/partials/project_milestones.html',
            'timeline': 'project/partials/project_timeline.html',
            'documents': 'project/partials/project_documents.html',
            'expenses': 'project/partials/project_expenses.html',
            'settings': 'project/partials/project_settings.html',
        }
        return render(request, template_map.get(tab, template_map['overview']), context)
    
    return render(request, 'project/project_detail.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def project_create(request):
    """Create new project"""
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.created_by = request.user
            project.save()

            # Add team members if provided
            team_members = request.POST.getlist('team_members')
            for member_id in team_members:
                ProjectTeamMember.objects.create(
                    project=project,
                    employee_id=member_id,
                    role=request.POST.get(f'role_{member_id}', ''),
                    allocation_percentage=request.POST.get(f'allocation_{member_id}', 100)
                )

            if request.headers.get('HX-Request'):
                response = HttpResponse()
                response['HX-Redirect'] = f'/project/{project.id}/'
                return response

            return redirect('project:project_detail', project_id=project.id)
        # If form is not valid, it will fall through to render with errors
    else:
        form = ProjectForm()

    # Get active tab from request (check both GET and POST for form errors)
    tab = request.POST.get('tab') or request.GET.get('tab', 'overview')

    if request.headers.get('HX-Request'):
        return render(request, 'project/partials/project_edit_form.html', {
            'form': form,
            'project': None,
        })

    # Initialize empty statistics for new project
    task_stats = {
        'total': 0,
        'completed': 0,
        'in_progress': 0,
        'overdue': 0,
    }

    # Budget summary (empty for new project)
    budget_stats = {
        'estimated': 0,
        'actual': 0,
        'expenses': 0,
        'remaining': 0
    }

    # Time tracking summary (empty for new project)
    time_stats = {
        'estimated': 0,
        'logged': 0,
        'billable': 0,
    }

    # Milestone statistics (empty for new project)
    milestone_stats = {
        'total': 0,
        'completed': 0,
        'pending': 0,
        'overdue': 0,
        'critical': 0,
    }

    # Expense statistics (empty for new project)
    expense_stats = {
        'total': 0,
        'billable': 0,
        'approved': 0,
        'submitted_count': 0,
    }

    # Get all available employees for team member addition
    from hr.models import Employee
    available_employees = Employee.objects.filter(employment_status='active').select_related('user').order_by('user__first_name', 'user__last_name')

    # Get all active employees for task assignment
    all_employees = Employee.objects.filter(employment_status='active').select_related('user').order_by('user__first_name', 'user__last_name')

    # Format employees data with email for autocomplete
    all_employees_data = []
    for emp in all_employees:
        all_employees_data.append({
            'id': emp.id,
            'name': emp.get_full_name(),
            'email': emp.email if emp.email else (emp.user.email if emp.user else ''),
            'initials': emp.get_full_name()[:2].upper() if emp.get_full_name() else ''
        })

    # Create an empty settings form for new project
    settings_form = ProjectSettingsForm()

    return render(request, 'project/project_form.html', {
        'form': form,
        'project': None,
        'title': 'Create New Project',
        'tab': tab,
        'task_stats': task_stats,
        'budget_stats': budget_stats,
        'time_stats': time_stats,
        'milestone_stats': milestone_stats,
        'expense_stats': expense_stats,
        'milestones': [],
        'expenses': [],
        'documents': [],
        'today': timezone.now().date(),
        'available_employees': available_employees,
        'all_employees': all_employees,
        'all_employees_data': all_employees_data,
        'settings_form': settings_form,
    })


@login_required
@require_http_methods(["GET", "POST"])
def project_edit(request, project_id):
    """Edit existing project"""
    project = get_object_or_404(
        Project.objects.select_related(
            'project_manager', 'created_by'
        ).prefetch_related(
            'team_members__employee',
            'tasks'
        ),
        id=project_id
    )

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()

            if request.headers.get('HX-Request'):
                return render(request, 'project/partials/project_header.html', {
                    'project': project,
                    'message': 'Project updated successfully'
                })

            return redirect('project:project_detail', project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    # Get active tab from request
    tab = request.GET.get('tab', 'overview')

    if request.headers.get('HX-Request'):
        return render(request, 'project/partials/project_edit_form.html', {
            'form': form,
            'project': project,
        })

    # Calculate project statistics (same as project_detail view)
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

    # Budget summary
    total_expenses = 0
    budget_stats = {
        'estimated': project.estimated_cost or 0,
        'actual': project.actual_cost or 0,
        'expenses': total_expenses,
        'remaining': (project.estimated_cost or 0) - (project.actual_cost or 0) - total_expenses
    }

    # Time tracking summary
    time_stats = {
        'estimated': 0,
        'logged': 0,
        'billable': 0,
    }

    # Milestone statistics
    milestone_stats = {
        'total': 0,
        'completed': 0,
        'pending': 0,
        'overdue': 0,
        'critical': 0,
    }

    # Expense statistics
    expense_stats = {
        'total': 0,
        'billable': 0,
        'approved': 0,
        'submitted_count': 0,
    }

    # Get available employees for team member addition
    from hr.models import Employee
    current_member_ids = project.team_members.values_list('employee_id', flat=True)
    available_employees = Employee.objects.exclude(id__in=current_member_ids).select_related('user').order_by('user__first_name', 'user__last_name')

    # Get all active employees for task assignment
    all_employees = Employee.objects.filter(employment_status='active').select_related('user').order_by('user__first_name', 'user__last_name')

    # Format employees data with email for autocomplete
    all_employees_data = []
    for emp in all_employees:
        all_employees_data.append({
            'id': emp.id,
            'name': emp.get_full_name(),
            'email': emp.email if emp.email else (emp.user.email if emp.user else ''),
            'initials': emp.get_full_name()[:2].upper() if emp.get_full_name() else ''
        })

    # Get or create project settings
    settings, created = ProjectSettings.objects.get_or_create(
        project=project,
        defaults={'created_by': request.user}
    )
    settings_form = ProjectSettingsForm(instance=settings)

    return render(request, 'project/project_form.html', {
        'form': form,
        'project': project,
        'title': 'Edit Project',
        'tab': tab,
        'task_stats': task_stats,
        'budget_stats': budget_stats,
        'time_stats': time_stats,
        'milestone_stats': milestone_stats,
        'expense_stats': expense_stats,
        'milestones': [],
        'expenses': [],
        'documents': [],
        'today': timezone.now().date(),
        'available_employees': available_employees,
        'all_employees': all_employees,
        'all_employees_data': all_employees_data,
        'settings_form': settings_form,
    })


@login_required
@require_http_methods(["POST"])
def project_settings_save(request, project_id):
    """Save project-specific settings (AJAX endpoint)"""
    project = get_object_or_404(Project, id=project_id)

    # Get or create settings instance
    settings, created = ProjectSettings.objects.get_or_create(
        project=project,
        defaults={'created_by': request.user}
    )

    form = ProjectSettingsForm(request.POST, instance=settings)
    if form.is_valid():
        settings_instance = form.save(commit=False)
        if created:
            settings_instance.created_by = request.user
        settings_instance.save()

        # Re-render the settings form with success message
        form = ProjectSettingsForm(instance=settings)
        return render(request, 'project/partials/project_settings.html', {
            'project': project,
            'settings_form': form,
            'tab': 'settings',
            'success_message': 'Project settings updated successfully'
        })
    else:
        # Re-render with errors
        return render(request, 'project/partials/project_settings.html', {
            'project': project,
            'settings_form': form,
            'tab': 'settings',
        })


@login_required
@require_http_methods(["GET", "POST"])
def task_create(request, project_id):
    """Task creation for a project"""
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = ProjectTaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            task.project = project
            task.created_by = request.user
            task.save()

            return redirect(f"{reverse('project:project_detail', args=[project.id])}?tab=tasks")
    else:
        form = ProjectTaskForm(project=project)

    # Get available employees for assignment
    try:
        from hr.models import Employee
        employees = Employee.objects.filter(is_active=True).select_related('user')
    except:
        employees = []

    return render(request, 'project/task_create.html', {
        'form': form,
        'project': project,
        'employees': employees,
    })


@login_required
@require_http_methods(["GET", "POST"])
def task_edit(request, task_id):
    """Edit task inline"""
    task = get_object_or_404(ProjectTask, id=task_id)
    
    if request.method == "POST":
        form = ProjectTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return render(request, 'project/partials/task_row.html', {
                'task': task,
            })
    else:
        form = ProjectTaskForm(instance=task)
    
    return render(request, 'project/partials/task_edit_row.html', {
        'form': form,
        'task': task,
    })


@login_required
@require_http_methods(["POST"])
def task_update_status(request, task_id):
    """Quick status update for task"""
    task = get_object_or_404(ProjectTask, id=task_id)
    
    status = request.POST.get('status')
    if status in dict(ProjectTask.STATUS_CHOICES):
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
    
    return render(request, 'project/partials/task_row.html', {
        'task': task,
    })


@login_required
@require_http_methods(["DELETE"])
def task_delete(request, task_id):
    """Delete task"""
    task = get_object_or_404(ProjectTask, id=task_id)
    task.delete()

    return HttpResponse('')


@login_required
@require_http_methods(["POST"])
def task_create_inline(request, project_id):
    """Create task inline from table (Excel-like)"""
    import logging
    logger = logging.getLogger(__name__)

    project = get_object_or_404(Project, id=project_id)

    try:
        # Get data from POST
        task_name = request.POST.get('task_name', '').strip()
        if not task_name:
            return JsonResponse({'error': 'Task name is required'}, status=400)

        # Create the task with minimal required fields
        task = ProjectTask.objects.create(
            project=project,
            task_name=task_name,
            description=request.POST.get('description', ''),
            assigned_to_id=request.POST.get('assigned_to') if request.POST.get('assigned_to') else None,
            priority=request.POST.get('priority', 'medium'),
            status=request.POST.get('status', 'open'),
            expected_start_date=request.POST.get('expected_start_date') if request.POST.get('expected_start_date') else None,
            expected_end_date=request.POST.get('expected_end_date') if request.POST.get('expected_end_date') else None,
            estimated_hours=request.POST.get('estimated_hours') if request.POST.get('estimated_hours') else None,
            progress=request.POST.get('progress', 0)
        )


        if request.headers.get('HX-Request'):
            # Return the new task row
            from hr.models import Employee
            all_employees = Employee.objects.filter(employment_status='active').select_related('user').order_by('user__first_name', 'user__last_name')

            # Format employees data with email for autocomplete
            all_employees_data = []
            for emp in all_employees:
                all_employees_data.append({
                    'id': emp.id,
                    'name': emp.get_full_name(),
                    'email': emp.email if emp.email else (emp.user.email if emp.user else ''),
                    'initials': emp.get_full_name()[:2].upper() if emp.get_full_name() else ''
                })

            return render(request, 'project/partials/task_row_inline.html', {
                'task': task,
                'project': project,
                'today': timezone.now().date(),
                'all_employees': all_employees,
                'all_employees_data': all_employees_data,
            })

        return JsonResponse({'success': True, 'task_id': str(task.id)})

    except Exception as e:
        logger.exception(f"Error creating task: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def task_update_inline(request, task_id):
    """Update task inline from table (Excel-like)"""
    task = get_object_or_404(ProjectTask, id=task_id)

    try:
        # Update fields that are provided
        if 'task_name' in request.POST:
            task.task_name = request.POST['task_name']

        if 'description' in request.POST:
            task.description = request.POST['description']

        if 'assigned_to' in request.POST:
            task.assigned_to_id = request.POST['assigned_to'] if request.POST['assigned_to'] else None

        if 'priority' in request.POST:
            task.priority = request.POST['priority']

        if 'status' in request.POST:
            task.status = request.POST['status']
            # Auto-update completion date when completed
            if task.status == 'completed':
                task.actual_end_date = timezone.now().date()
                task.progress = 100

        if 'expected_start_date' in request.POST:
            task.expected_start_date = request.POST['expected_start_date'] if request.POST['expected_start_date'] else None

        if 'expected_end_date' in request.POST:
            task.expected_end_date = request.POST['expected_end_date'] if request.POST['expected_end_date'] else None

        if 'estimated_hours' in request.POST:
            task.estimated_hours = request.POST['estimated_hours'] if request.POST['estimated_hours'] else None

        if 'progress' in request.POST:
            task.progress = request.POST['progress']

        task.save()

        if request.headers.get('HX-Request'):
            # Return updated task row
            from hr.models import Employee
            all_employees = Employee.objects.filter(employment_status='active').select_related('user').order_by('user__first_name', 'user__last_name')

            # Format employees data with email for autocomplete
            all_employees_data = []
            for emp in all_employees:
                all_employees_data.append({
                    'id': emp.id,
                    'name': emp.get_full_name(),
                    'email': emp.email if emp.email else (emp.user.email if emp.user else ''),
                    'initials': emp.get_full_name()[:2].upper() if emp.get_full_name() else ''
                })

            return render(request, 'project/partials/task_row_inline.html', {
                'task': task,
                'project': task.project,
                'today': timezone.now().date(),
                'all_employees': all_employees,
                'all_employees_data': all_employees_data,
            })

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ========== ENHANCED TASK MANAGEMENT VIEWS ==========

@login_required
def task_list(request):
    """List all tasks with filtering and search"""
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
    except:
        employee = None

    # Base queryset
    tasks = ProjectTask.objects.select_related(
        'project', 'assigned_to'
    ).prefetch_related('project__team_members')

    # Filter based on user role
    if not request.user.is_superuser:
        if employee:
            # Show tasks where user is assigned or is project team member
            tasks = tasks.filter(
                Q(assigned_to=employee) |
                Q(project__team_members__employee=employee)
            ).distinct()
        else:
            tasks = tasks.none()

    # Search functionality
    search = request.GET.get('search')
    if search:
        tasks = tasks.filter(
            Q(task_name__icontains=search) |
            Q(task_code__icontains=search) |
            Q(description__icontains=search) |
            Q(project__project_name__icontains=search)
        )

    # Status filter
    status = request.GET.get('status')
    if status:
        tasks = tasks.filter(status=status)

    # Priority filter
    priority = request.GET.get('priority')
    if priority:
        tasks = tasks.filter(priority=priority)

    # Project filter
    project_id = request.GET.get('project')
    if project_id:
        tasks = tasks.filter(project_id=project_id)

    # Assignment filter
    assigned = request.GET.get('assigned')
    if assigned == 'me' and employee:
        tasks = tasks.filter(assigned_to=employee)
    elif assigned == 'unassigned':
        tasks = tasks.filter(assigned_to__isnull=True)

    # Team filter
    team_id = request.GET.get('team')
    if team_id:
        try:
            team = Team.objects.get(id=team_id)
            # Filter tasks assigned to team members
            team_member_employees = team.team_members.filter(is_active=True).values_list('employee_id', flat=True)
            tasks = tasks.filter(assigned_to_id__in=team_member_employees)
        except (Team.DoesNotExist, ValueError):
            pass

    # Due date filter
    due_filter = request.GET.get('due')
    if due_filter:
        today = timezone.now().date()
        if due_filter == 'overdue':
            tasks = tasks.filter(expected_end_date__lt=today, status__in=['open', 'working'])
        elif due_filter == 'today':
            tasks = tasks.filter(expected_end_date=today)
        elif due_filter == 'week':
            week_end = today + timedelta(days=7)
            tasks = tasks.filter(expected_end_date__lte=week_end, expected_end_date__gte=today)

    # Sorting
    sort = request.GET.get('sort', '-created_at')
    tasks = tasks.order_by(sort)

    # Pagination
    paginator = Paginator(tasks, 25)
    page = request.GET.get('page', 1)
    tasks_page = paginator.get_page(page)

    # Get projects for filter dropdown
    if employee and not request.user.is_superuser:
        projects = Project.objects.filter(
            team_members__employee=employee,
            is_active=True
        ).distinct()
    else:
        projects = Project.objects.all()

    # Statistics
    stats = {
        'total': tasks.count(),
        'assigned_to_me': tasks.filter(assigned_to=employee).count() if employee else 0,
        'overdue': tasks.filter(
            expected_end_date__lt=timezone.now().date(),
            status__in=['open', 'working']
        ).count(),
        'due_today': tasks.filter(expected_end_date=timezone.now().date()).count(),
    }

    # Get teams for filter dropdown
    teams = Team.objects.filter(status='active').order_by('team_name')

    return render(request, 'project/task_list.html', {
        'tasks': tasks_page,
        'projects': projects,
        'teams': teams,
        'stats': stats,
        'current_employee': employee,
    })


@login_required
def task_detail(request, task_id):
    """Task detail view with comments and time tracking"""
    task = get_object_or_404(
        ProjectTask.objects.select_related(
            'project', 'assigned_to'
        ).prefetch_related('updates'),
        id=task_id
    )

    # Permission check
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
        if not request.user.is_superuser:
            # Check if user has access to this task
            has_access = (
                task.assigned_to == employee or
                task.project.team_members.filter(employee=employee).exists() or
                task.project.project_manager == employee
            )
            if not has_access:
                return redirect('project:task_list')
    except:
        if not request.user.is_superuser:
            return redirect('project:task_list')

    # Get time entries for this task
    time_entries = TimesheetDetail.objects.filter(task=task).select_related(
        'timesheet__employee'
    ).order_by('-activity_date')

    # Calculate time statistics
    time_stats = {
        'total_logged': time_entries.aggregate(Sum('hours'))['hours__sum'] or 0,
        'billable_logged': time_entries.filter(is_billable=True).aggregate(Sum('hours'))['hours__sum'] or 0,
        'estimated': task.estimated_hours or 0,
    }

    # Get recent comments/updates
    updates = task.updates.order_by('-created_at')[:10]

    return render(request, 'project/task_detail.html', {
        'task': task,
        'time_entries': time_entries,
        'time_stats': time_stats,
        'dependencies': dependencies,
        'dependent_tasks': dependent_tasks,
        'subtasks': subtasks,
        'updates': updates,
    })


@login_required
@require_http_methods(["GET", "POST"])
def task_create_full(request, project_id=None):
    """Full task creation form"""
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = ProjectTaskForm(request.POST, project=project)
        if form.is_valid():
            task = form.save(commit=False)
            if project:
                task.project = project
            task.created_by = request.user
            task.save()

            return redirect('project:task_detail', task_id=task.id)
    else:
        form = ProjectTaskForm(project=project)

    # Get available projects for assignment
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
        if not request.user.is_superuser:
            projects = Project.objects.filter(
                team_members__employee=employee,
                is_active=True
            ).distinct()
        else:
            projects = Project.objects.all()
    except:
        projects = Project.objects.all()

    return render(request, 'project/task_create.html', {
        'form': form,
        'project': project,
        'projects': projects,
    })


@login_required
@require_http_methods(["POST"])
def task_assign(request, task_id):
    """Assign task to employee"""
    task = get_object_or_404(ProjectTask, id=task_id)

    employee_id = request.POST.get('assigned_to')
    if employee_id:
        try:
            from hr.models import Employee
            employee = Employee.objects.get(id=employee_id)

            # Check if employee is part of the project team
            if task.project.team_members.filter(employee=employee).exists():
                task.assigned_to = employee
                # task.assigned_by = Employee.objects.get(user=request.user)  # Field doesn't exist
                task.save()

                # Create update log - table doesn't exist in database
                # ProjectUpdate.objects.create(
                #     project=task.project,
                #     task=task,
                #     comment=f'Task assigned to {employee.full_name}',
                #     created_by=request.user
                # )
        except:
            pass

    if request.headers.get('HX-Request'):
        return render(request, 'project/partials/task_row.html', {
            'task': task,
        })

    return redirect('project:task_detail', task_id=task.id)


@login_required
@require_http_methods(["POST"])
def task_bulk_assign(request):
    """Bulk assign tasks to an employee"""
    try:
        data = json.loads(request.body)
        task_ids = data.get('task_ids', [])
        assigned_to_id = data.get('assigned_to')

        if not task_ids or not assigned_to_id:
            return JsonResponse({'error': 'Missing task_ids or assigned_to'}, status=400)

        from hr.models import Employee
        employee = get_object_or_404(Employee, id=assigned_to_id)
        # assigned_by = Employee.objects.get(user=request.user)  # Field doesn't exist

        updated_count = 0
        for task_id in task_ids:
            try:
                task = ProjectTask.objects.get(id=task_id)

                # Check if employee is part of the project team
                if task.project.team_members.filter(employee=employee).exists():
                    task.assigned_to = employee
                    # task.assigned_by = assigned_by  # Field doesn't exist
                    task.save()

                    # Create update log - table doesn't exist in database
                    # ProjectUpdate.objects.create(
                    #     project=task.project,
                    #     task=task,
                    #     comment=f'Task assigned to {employee.full_name}',
                    #     created_by=request.user
                    # )
                    updated_count += 1
            except ProjectTask.DoesNotExist:
                continue

        return JsonResponse({
            'success': True,
            'updated_count': updated_count,
            'message': f'{updated_count} task(s) assigned successfully'
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def task_update_progress(request, task_id):
    """Update task progress"""
    task = get_object_or_404(ProjectTask, id=task_id)

    progress = request.POST.get('progress')
    if progress:
        try:
            progress_value = float(progress)
            if 0 <= progress_value <= 100:
                task.progress = progress_value

                # Auto-update status based on progress
                if progress_value == 0:
                    task.status = 'open'
                elif progress_value == 100:
                    task.status = 'completed'
                    task.actual_end_date = timezone.now().date()
                elif task.status == 'open':
                    task.status = 'working'
                    if not task.actual_start_date:
                        task.actual_start_date = timezone.now().date()

                task.save()

                # Update project progress
                project = task.project
                total_tasks = project.tasks.count()
                if total_tasks > 0:
                    avg_progress = project.tasks.aggregate(Avg('progress'))['progress__avg'] or 0
                    project.percent_complete = avg_progress
                    project.save()
        except ValueError:
            pass

    if request.headers.get('HX-Request'):
        return render(request, 'project/partials/task_row.html', {
            'task': task,
        })

    return redirect('project:task_detail', task_id=task.id)


@login_required
def my_tasks(request):
    """Personal task dashboard for current user"""
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
    except:
        return redirect('project:task_list')

    # Get user's assigned tasks
    assigned_tasks = ProjectTask.objects.filter(
        assigned_to=employee
    ).select_related('project').order_by('expected_end_date')

    # Filter by status
    status_filter = request.GET.get('status', 'active')
    if status_filter == 'active':
        assigned_tasks = assigned_tasks.filter(status__in=['open', 'working', 'pending_review'])
    elif status_filter == 'completed':
        assigned_tasks = assigned_tasks.filter(status='completed')
    elif status_filter != 'all':
        assigned_tasks = assigned_tasks.filter(status=status_filter)

    # Categorize tasks
    today = timezone.now().date()
    task_categories = {
        'overdue': assigned_tasks.filter(
            expected_end_date__lt=today,
            status__in=['open', 'working', 'pending_review']
        ),
        'due_today': assigned_tasks.filter(expected_end_date=today),
        'due_this_week': assigned_tasks.filter(
            expected_end_date__gte=today,
            expected_end_date__lte=today + timedelta(days=7)
        ).exclude(expected_end_date=today),
        'upcoming': assigned_tasks.filter(
            expected_end_date__gt=today + timedelta(days=7)
        ),
    }

    # Task statistics
    stats = {
        'total_assigned': assigned_tasks.count(),
        'completed_this_week': ProjectTask.objects.filter(
            assigned_to=employee,
            status='completed',
            actual_end_date__gte=today - timedelta(days=7)
        ).count(),
        'overdue': task_categories['overdue'].count(),
        'due_today': task_categories['due_today'].count(),
    }

    # Recent activity
    recent_tasks = ProjectTask.objects.filter(
        assigned_to=employee
    ).order_by('-updated_at')[:5]

    return render(request, 'project/my_tasks.html', {
        'task_categories': task_categories,
        'stats': stats,
        'recent_tasks': recent_tasks,
        'employee': employee,
        'status_filter': status_filter,
    })


@login_required
@require_http_methods(["GET", "POST"])
def project_team_member_add(request, project_id):
    """Add team member to project"""
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        form = TeamMemberForm(request.POST)
        if form.is_valid():
            member = form.save(commit=False)
            member.project = project
            member.save()

            return redirect(f"{reverse('project:project_detail', args=[project.id])}?tab=team")
    else:
        form = TeamMemberForm()

    # Get available employees
    try:
        from hr.models import Employee
        # Exclude employees already in this project
        existing_members = project.team_members.values_list('employee_id', flat=True)
        employees = Employee.objects.filter(is_active=True).exclude(
            id__in=existing_members
        ).select_related('user')
    except:
        employees = []

    return render(request, 'project/team_member_add.html', {
        'form': form,
        'project': project,
        'employees': employees,
    })


@login_required
@require_http_methods(["GET", "POST"])
def project_team_member_edit(request, member_id):
    """Edit project team member"""
    member = get_object_or_404(ProjectTeamMember, id=member_id)
    project = member.project

    if request.method == "POST":
        form = TeamMemberForm(request.POST, instance=member)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('project:project_detail', args=[project.id])}?tab=team")
    else:
        form = TeamMemberForm(instance=member)

    return render(request, 'project/team_member_edit.html', {
        'form': form,
        'member': member,
        'project': project,
    })


@login_required
@require_http_methods(["DELETE", "GET"])
def project_team_member_remove(request, member_id):
    """Remove team member from project"""
    member = get_object_or_404(ProjectTeamMember, id=member_id)

    if request.method == "GET":
        # Handle GET request for non-HTMX navigation
        project_id = member.project.id
        member.delete()
        return redirect(f"{reverse('project:project_detail', args=[project_id])}?tab=team")

    # Handle DELETE request
    member.delete()
    return HttpResponse('')


@login_required
@require_http_methods(["POST"])
def team_member_add_inline(request, project_id):
    """Add team member inline (for Excel-like table editing)"""
    import logging
    import traceback
    logger = logging.getLogger(__name__)

    # Log incoming request data

    project = get_object_or_404(Project, id=project_id)

    try:
        from hr.models import Employee

        employee_id = request.POST.get('employee_id')

        if not employee_id:
            return JsonResponse({'error': 'Employee is required'}, status=400)

        employee = Employee.objects.get(id=employee_id)

        # Check if employee is already in the project
        if ProjectTeamMember.objects.filter(project=project, employee=employee).exists():
            return JsonResponse({'error': 'Employee is already a member of this project'}, status=400)

        # Parse dates - handle empty strings
        start_date = request.POST.get('start_date', '').strip()
        end_date = request.POST.get('end_date', '').strip()

        # Convert empty strings to None
        start_date = start_date if start_date else None
        end_date = end_date if end_date else None

        # Parse numeric fields
        daily_rate = request.POST.get('daily_rate_usd', '').strip()
        multiplier = request.POST.get('multiplier', '1.0').strip()

        # Convert empty strings to None for daily_rate
        daily_rate = daily_rate if daily_rate else None
        # Ensure multiplier has a default value
        multiplier = multiplier if multiplier else '1.0'

        # Get role with default value
        role = request.POST.get('role', 'Team Member').strip()
        role = role if role else 'Team Member'

        # Create team member

        member = ProjectTeamMember.objects.create(
            project=project,
            employee=employee,
            role=role,
            pay_type=request.POST.get('pay_type', 'Normal'),
            daily_rate_usd=daily_rate,
            multiplier=multiplier,
            start_date=start_date,
            end_date=end_date,
            notes='',  # Default empty string to satisfy NOT NULL constraint
        )


        return JsonResponse({
            'success': True,
            'member_id': member.id,
            'message': 'Team member added successfully'
        })
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()
        return JsonResponse({'error': error_msg}, status=500)


@login_required
@require_http_methods(["POST"])
def team_member_update_inline(request, member_id):
    """Update team member field inline"""
    member = get_object_or_404(ProjectTeamMember, id=member_id)

    try:
        # Get the field to update from POST data
        for field in ['role', 'pay_type', 'daily_rate_usd', 'multiplier', 'start_date', 'end_date']:
            if field in request.POST:
                value = request.POST.get(field)

                # Handle empty values
                if value == '':
                    if field in ['daily_rate_usd', 'start_date', 'end_date']:
                        value = None
                    elif field == 'multiplier':
                        value = 1.0
                    elif field == 'pay_type':
                        value = 'Normal'
                    elif field == 'role':
                        value = 'Team Member'

                # Convert to appropriate type
                if field in ['daily_rate_usd', 'multiplier'] and value is not None:
                    value = float(value)

                setattr(member, field, value)

        member.save()
        return HttpResponse('')
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def dashboard(request):
    """Project dashboard with key metrics"""
    # Get current user's employee record
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
    except:
        employee = None
    
    # Projects where user is involved
    if employee:
        my_projects = Project.objects.filter(
            Q(project_manager=employee) |
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
        'total_projects': Project.objects.count(),
        'active_projects': Project.objects.filter(
            status__in=['open', 'in_progress']
        ).count(),
        'overdue_tasks': ProjectTask.objects.filter(
            expected_end_date__lt=timezone.now().date(),
            status__in=['open', 'working']
        ).count(),
        'pending_approvals': Timesheet.objects.filter(status='submitted').count(),
    }

    # Recent updates - table doesn't exist in database
    # recent_updates = ProjectUpdate.objects.select_related(
    #     'project', 'created_by'
    # ).order_by('-created_at')[:10]
    recent_updates = []

    # Upcoming milestones
    upcoming_milestones = ProjectMilestone.objects.filter(
        milestone_date__gte=timezone.now().date(),
        status='pending'
    ).order_by('milestone_date')[:5]
    
    return render(request, 'project/dashboard.html', {
        'my_projects': my_projects,
        'my_tasks': my_tasks,
        'stats': stats,
        'recent_updates': recent_updates,
        'upcoming_milestones': upcoming_milestones,
    })


# ========== TIMESHEET MANAGEMENT VIEWS ==========

@login_required
def timesheet_list(request):
    """List all timesheets for the current user or all if manager"""
    from datetime import datetime, timedelta
    from django.db.models import Sum
    from decimal import Decimal

    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
    except:
        employee = None

    # Determine if user is manager
    is_manager = request.user.is_superuser or (employee and hasattr(employee, 'user_role_assignments'))

    # Filter timesheets based on user role
    if is_manager:
        # Managers can see all timesheets
        timesheets = Timesheet.objects.select_related(
            'employee', 'company', 'approved_by', 'created_by'
        ).prefetch_related('details')
        # Get all employees for filter dropdown
        all_employees = Employee.objects.filter(employment_status='active').order_by('first_name', 'last_name')
    else:
        # Regular users can only see their own timesheets
        timesheets = Timesheet.objects.filter(
            employee=employee
        ).select_related('employee', 'company', 'approved_by', 'created_by').prefetch_related('details')
        all_employees = None

    # Search functionality
    search = request.GET.get('search', '').strip()
    if search:
        timesheets = timesheets.filter(
            Q(timesheet_code__icontains=search) |
            Q(employee__first_name__icontains=search) |
            Q(employee__last_name__icontains=search) |
            Q(employee__employee_id__icontains=search)
        )

    # Status filter
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        timesheets = timesheets.filter(status=status_filter)

    # Employee filter (for managers only)
    employee_filter = request.GET.get('employee', '').strip()
    if is_manager and employee_filter:
        timesheets = timesheets.filter(employee_id=employee_filter)

    # Date range filters
    start_date_from = request.GET.get('start_date_from', '').strip()
    if start_date_from:
        try:
            start_date_from_obj = datetime.strptime(start_date_from, '%Y-%m-%d').date()
            timesheets = timesheets.filter(start_date__gte=start_date_from_obj)
        except ValueError:
            start_date_from = ''

    start_date_to = request.GET.get('start_date_to', '').strip()
    if start_date_to:
        try:
            start_date_to_obj = datetime.strptime(start_date_to, '%Y-%m-%d').date()
            timesheets = timesheets.filter(start_date__lte=start_date_to_obj)
        except ValueError:
            start_date_to = ''

    # Calculate statistics (before sorting/pagination)
    stats = {
        'total': timesheets.count(),
        'submitted': timesheets.filter(status='submitted').count(),
        'approved': timesheets.filter(status='approved').count(),
        'draft': timesheets.filter(status='draft').count(),
        'rejected': timesheets.filter(status='rejected').count(),
    }

    # Calculate this week's hours
    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    this_week_timesheets = timesheets.filter(
        start_date__lte=week_end,
        end_date__gte=week_start
    )

    total_hours = this_week_timesheets.aggregate(
        total=Sum('total_hours')
    )['total'] or Decimal('0')

    total_billable_hours = this_week_timesheets.aggregate(
        total=Sum('total_billable_hours')
    )['total'] or Decimal('0')

    # Calculate last week for comparison
    last_week_start = week_start - timedelta(days=7)
    last_week_end = week_start - timedelta(days=1)

    last_week_hours = timesheets.filter(
        start_date__lte=last_week_end,
        end_date__gte=last_week_start
    ).aggregate(total=Sum('total_hours'))['total'] or Decimal('0')

    # Calculate percentage change
    week_comparison = 0
    if last_week_hours > 0:
        week_comparison = ((total_hours - last_week_hours) / last_week_hours) * 100

    # Calculate billable percentage
    billable_percentage = 0
    if total_hours > 0:
        billable_percentage = (total_billable_hours / total_hours) * 100

    # Sorting
    sort_by = request.GET.get('sort', 'start_date')
    sort_order = request.GET.get('order', 'desc')

    # Validate sort field
    valid_sort_fields = ['start_date', 'timesheet_code', 'employee__first_name', 'status',
                        'total_hours', 'total_billable_hours', 'submitted_date']
    if sort_by not in valid_sort_fields:
        sort_by = 'start_date'

    # Apply sorting
    if sort_order == 'asc':
        timesheets = timesheets.order_by(sort_by)
    else:
        timesheets = timesheets.order_by(f'-{sort_by}')

    # Pagination with per_page handling
    per_page = request.GET.get('per_page', '20')
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 25, 50, 100, 200]:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20

    paginator = Paginator(timesheets, per_page)
    page_number = request.GET.get('page')

    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'project/timesheet_list.html', {
        'page_obj': page_obj,
        'timesheets': page_obj,  # For backward compatibility
        'current_employee': employee,
        'is_manager': is_manager,
        'all_employees': all_employees,
        'stats': stats,
        'total_hours': total_hours,
        'total_billable_hours': total_billable_hours,
        'week_comparison': week_comparison,
        'billable_percentage': billable_percentage,
        'per_page': per_page,
        'search_query': search,
        'status_filter': status_filter,
        'employee_filter': employee_filter,
        'start_date_from': start_date_from,
        'start_date_to': start_date_to,
        'current_sort': sort_by,
        'current_order': sort_order,
    })


@login_required
def timesheet_detail(request, timesheet_id):
    """View timesheet details with entries"""
    timesheet = get_object_or_404(
        Timesheet.objects.select_related(
            'employee', 'company', 'approved_by', 'created_by'
        ).prefetch_related('details__project', 'details__task', 'details__activity_type'),
        id=timesheet_id
    )

    # Permission check
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
        if not request.user.is_superuser and timesheet.employee != employee:
            return redirect('project:timesheet_list')
    except:
        if not request.user.is_superuser:
            return redirect('project:timesheet_list')

    # Calculate totals
    entries = timesheet.details.all()
    totals = {
        'total_hours': entries.aggregate(Sum('hours'))['hours__sum'] or 0,
        'billable_hours': entries.filter(is_billable=True).aggregate(Sum('hours'))['hours__sum'] or 0,
        'total_amount': entries.aggregate(Sum('billing_amount'))['billing_amount__sum'] or 0,
    }

    # Get projects where employee is assigned
    assigned_projects = Project.objects.filter(
        team_members__employee=timesheet.employee
    ).exclude(
        status__in=['cancelled', 'completed']
    ).distinct()

    return render(request, 'project/timesheet_detail.html', {
        'timesheet': timesheet,
        'entries': entries,
        'totals': totals,
        'assigned_projects': assigned_projects,
    })


@login_required
@require_http_methods(["GET", "POST"])
def timesheet_edit(request, timesheet_id):
    """Edit timesheet details"""
    from django.contrib import messages
    from .forms import TimesheetForm
    import json

    timesheet = get_object_or_404(Timesheet, id=timesheet_id)

    # Permission check
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
        if timesheet.employee != employee and not request.user.is_superuser:
            messages.error(request, 'You do not have permission to edit this timesheet.')
            return redirect('project:timesheet_detail', timesheet_id=timesheet_id)
    except:
        messages.error(request, 'You do not have permission to edit this timesheet.')
        return redirect('project:timesheet_detail', timesheet_id=timesheet_id)

    # Only allow editing draft timesheets
    if timesheet.status != 'draft':
        messages.error(request, 'Only draft timesheets can be edited.')
        return redirect('project:timesheet_detail', timesheet_id=timesheet_id)

    # Get company from request or default
    company = None
    if hasattr(request, 'tenant'):
        company = request.tenant
    else:
        try:
            from company.models import Company
            company = Company.objects.first()
        except:
            pass

    if not company:
        messages.error(request, 'No company/tenant found. Please contact your administrator.')
        return redirect('project:timesheet_list')

    if request.method == "POST":
        form = TimesheetForm(request.POST, instance=timesheet, company=company, user=request.user)
        if form.is_valid():
            try:
                timesheet = form.save(commit=False)
                timesheet.company = company
                timesheet.save()

                # Handle time entries if provided
                time_entries_json = request.POST.get('time_entries', '[]')
                try:
                    time_entries = json.loads(time_entries_json)
                    # Get existing entry IDs to track what to keep
                    existing_entry_ids = set()

                    for entry_data in time_entries:
                        entry_id = entry_data.get('id')
                        if entry_id:
                            # Update existing entry
                            try:
                                entry = TimesheetDetail.objects.get(id=entry_id, timesheet=timesheet)
                                entry.activity_date = entry_data.get('activity_date')
                                entry.project_id = entry_data.get('project')
                                entry.hours = entry_data.get('hours')
                                entry.is_billable = entry_data.get('is_billable', True)
                                entry.description = entry_data.get('description', '')
                                entry.save()
                                existing_entry_ids.add(entry_id)
                            except TimesheetDetail.DoesNotExist:
                                pass
                        else:
                            # Create new entry
                            new_entry = TimesheetDetail.objects.create(
                                timesheet=timesheet,
                                activity_date=entry_data.get('activity_date'),
                                project_id=entry_data.get('project'),
                                hours=entry_data.get('hours'),
                                is_billable=entry_data.get('is_billable', True),
                                description=entry_data.get('description', '')
                            )
                            existing_entry_ids.add(new_entry.id)

                    # Update timesheet totals
                    _update_timesheet_totals(timesheet)
                except json.JSONDecodeError:
                    pass  # If no entries or invalid JSON, just skip

                messages.success(request, f'Timesheet updated successfully.')
                return redirect('project:timesheet_detail', timesheet_id=timesheet.id)

            except Exception as e:
                messages.error(request, f'Error updating timesheet: {str(e)}')
    else:
        form = TimesheetForm(instance=timesheet, company=company, user=request.user)

    # Get existing entries
    entries = timesheet.details.all()

    # Get projects where employee is assigned
    assigned_projects = Project.objects.filter(
        team_members__employee=timesheet.employee
    ).exclude(
        status__in=['cancelled', 'completed']
    ).distinct()

    return render(request, 'project/timesheet_edit.html', {
        'form': form,
        'timesheet': timesheet,
        'entries': entries,
        'assigned_projects': assigned_projects,
    })


@login_required
@require_http_methods(["GET", "POST"])
def timesheet_create(request):
    """Create new timesheet"""
    from django.contrib import messages
    from .forms import TimesheetForm
    import json

    # Get company from request or default
    company = None
    if hasattr(request, 'tenant'):
        company = request.tenant
    else:
        try:
            from company.models import Company
            company = Company.objects.first()
        except:
            pass

    if not company:
        messages.error(request, 'No company/tenant found. Please contact your administrator.')
        return redirect('project:timesheet_list')

    # Get date range for new timesheet (current week)
    from datetime import date, timedelta
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    if request.method == "POST":
        form = TimesheetForm(request.POST, company=company, user=request.user)
        if form.is_valid():
            try:
                timesheet = form.save(commit=False)
                timesheet.company = company
                timesheet.created_by = request.user
                timesheet.save()

                # Handle time entries if provided
                time_entries_json = request.POST.get('time_entries', '[]')
                try:
                    time_entries = json.loads(time_entries_json)
                    for entry_data in time_entries:
                        TimesheetDetail.objects.create(
                            timesheet=timesheet,
                            activity_date=entry_data.get('activity_date'),
                            project_id=entry_data.get('project'),
                            hours=entry_data.get('hours'),
                            is_billable=entry_data.get('is_billable', True),
                            description=entry_data.get('description', '')
                        )

                    # Update timesheet totals
                    _update_timesheet_totals(timesheet)
                except json.JSONDecodeError:
                    pass  # If no entries or invalid JSON, just skip

                messages.success(request, f'Timesheet created successfully for {timesheet.start_date} to {timesheet.end_date}.')
                return redirect('project:timesheet_detail', timesheet_id=timesheet.id)

            except Exception as e:
                messages.error(request, f'Error creating timesheet: {str(e)}')
    else:
        # Pre-populate form with suggested dates
        initial_data = {
            'start_date': start_of_week,
            'end_date': end_of_week,
        }
        form = TimesheetForm(initial=initial_data, company=company, user=request.user)

    return render(request, 'project/timesheet_create.html', {
        'form': form,
    })


@login_required
@require_http_methods(["GET", "POST"])
def timesheet_entry_create(request, timesheet_id):
    """Add new timesheet entry"""
    timesheet = get_object_or_404(Timesheet, id=timesheet_id)

    # Permission check
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
        if timesheet.employee != employee and not request.user.is_superuser:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == "POST":
        form = TimesheetEntryForm(request.POST, employee=employee)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.timesheet = timesheet
            entry.save()

            # Update timesheet totals
            _update_timesheet_totals(timesheet)

            if request.headers.get('HX-Request'):
                return render(request, 'project/partials/timesheet_entry_row.html', {
                    'entry': entry,
                    'timesheet': timesheet,
                })

            return redirect('project:timesheet_detail', timesheet_id=timesheet.id)
    else:
        form = TimesheetEntryForm(employee=employee)

    # Get projects where employee is assigned
    assigned_projects = Project.objects.filter(
        team_members__employee=timesheet.employee
    ).exclude(
        status__in=['cancelled', 'completed']
    ).distinct()

    if request.headers.get('HX-Request'):
        return render(request, 'project/partials/timesheet_entry_form.html', {
            'form': form,
            'timesheet': timesheet,
            'assigned_projects': assigned_projects,
        })

    return render(request, 'project/timesheet_entry_form.html', {
        'form': form,
        'timesheet': timesheet,
        'assigned_projects': assigned_projects,
    })


@login_required
@require_http_methods(["POST"])
def timesheet_entry_edit(request, entry_id):
    """Edit timesheet entry inline"""
    entry = get_object_or_404(TimesheetDetail, id=entry_id)
    timesheet = entry.timesheet

    # Permission check
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
        if timesheet.employee != employee and not request.user.is_superuser:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Update entry fields
    fields = ['hours', 'description', 'is_billable']
    for field in fields:
        if field in request.POST:
            setattr(entry, field, request.POST[field])

    entry.save()

    # Update timesheet totals
    _update_timesheet_totals(timesheet)

    return render(request, 'project/partials/timesheet_entry_row.html', {
        'entry': entry,
        'timesheet': timesheet,
    })


@login_required
@require_http_methods(["DELETE"])
def timesheet_entry_delete(request, entry_id):
    """Delete timesheet entry"""
    entry = get_object_or_404(TimesheetDetail, id=entry_id)
    timesheet = entry.timesheet

    # Permission check
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
        if timesheet.employee != employee and not request.user.is_superuser:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    entry.delete()

    # Update timesheet totals
    _update_timesheet_totals(timesheet)

    return HttpResponse('')


@login_required
@require_http_methods(["POST"])
def timesheet_submit(request, timesheet_id):
    """Submit timesheet for approval"""
    timesheet = get_object_or_404(Timesheet, id=timesheet_id)

    # Permission check
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
        if timesheet.employee != employee:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if timesheet.status == 'draft':
        timesheet.status = 'submitted'
        timesheet.submitted_date = timezone.now()
        timesheet.save()

        # Update totals before submitting
        _update_timesheet_totals(timesheet)

    return redirect('project:timesheet_detail', timesheet_id=timesheet.id)


@login_required
@require_http_methods(["POST"])
def timesheet_approve(request, timesheet_id):
    """Approve timesheet (managers only)"""
    timesheet = get_object_or_404(Timesheet, id=timesheet_id)

    # Check if user can approve timesheets
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
        # Add your role checking logic here
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Permission denied'}, status=403)
    except:
        if not request.user.is_superuser:
            return JsonResponse({'error': 'Permission denied'}, status=403)

    if timesheet.status == 'submitted':
        timesheet.status = 'approved'
        timesheet.approved_date = timezone.now()
        try:
            from hr.models import Employee
            timesheet.approved_by = Employee.objects.get(user=request.user)
        except:
            pass
        timesheet.save()

    return redirect('project:timesheet_detail', timesheet_id=timesheet.id)


def _update_timesheet_totals(timesheet):
    """Helper function to update timesheet totals"""
    entries = timesheet.details.all()

    timesheet.total_hours = entries.aggregate(Sum('hours'))['hours__sum'] or 0
    timesheet.total_billable_hours = entries.filter(is_billable=True).aggregate(Sum('hours'))['hours__sum'] or 0
    timesheet.total_billable_amount = entries.filter(is_billable=True).aggregate(Sum('billing_amount'))['billing_amount__sum'] or 0
    timesheet.total_costing_amount = entries.aggregate(Sum('costing_amount'))['costing_amount__sum'] or 0

    timesheet.save()


@login_required
def my_timesheet(request):
    """Current user's timesheet dashboard"""
    try:
        from hr.models import Employee
        employee = Employee.objects.get(user=request.user)
    except:
        return redirect('project:timesheet_list')

    # Get current week's timesheet or create one
    from datetime import date, timedelta
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    # Get company for timesheet
    company = None
    if hasattr(request, 'tenant'):
        company = request.tenant
    else:
        try:
            from company.models import Company
            company = Company.objects.first()  # Get any company for now
        except:
            pass

    current_timesheet, created = Timesheet.objects.get_or_create(
        employee=employee,
        start_date=start_of_week,
        end_date=end_of_week,
        defaults={
            'company': company,
            'created_by': request.user,
        }
    )

    # Get recent timesheets
    recent_timesheets = Timesheet.objects.filter(
        employee=employee
    ).order_by('-start_date')[:5]

    # Get projects user is assigned to
    assigned_projects = Project.objects.filter(
        team_members__employee=employee
    ).exclude(
        status__in=['cancelled', 'completed']
    ).distinct()

    return render(request, 'project/timesheet_quick_entry.html', {
        'current_timesheet': current_timesheet,
        'recent_timesheets': recent_timesheets,
        'assigned_projects': assigned_projects,
        'employee': employee,
    })


# Team Management Views

@login_required
def team_list(request):
    """List all teams with filtering"""
    teams = Team.objects.select_related(
        'manager', 'department', 'company', 'created_by'
    ).prefetch_related('team_members__employee')

    # Search functionality
    search = request.GET.get('search')
    if search:
        teams = teams.filter(
            Q(team_name__icontains=search) |
            Q(team_code__icontains=search) |
            Q(description__icontains=search)
        )

    # Status filter
    status = request.GET.get('status')
    if status:
        teams = teams.filter(status=status)

    # Team type filter
    team_type = request.GET.get('team_type')
    if team_type:
        teams = teams.filter(team_type=team_type)

    # Department filter
    department = request.GET.get('department')
    if department:
        teams = teams.filter(department_id=department)

    # Annotate with member counts
    teams = teams.annotate(
        active_members=Count('team_members', filter=Q(team_members__is_active=True))
    )

    # Pagination
    paginator = Paginator(teams.order_by('team_name'), 20)
    page = request.GET.get('page', 1)
    teams_page = paginator.get_page(page)

    # Get filter options
    from hr.models import Department
    departments = Department.objects.all() if hasattr(request, 'hr') else []

    return render(request, 'project/team_list.html', {
        'teams': teams_page,
        'departments': departments,
        'team_types': Team.TEAM_TYPE_CHOICES,
        'status_choices': Team.STATUS_CHOICES,
    })


@login_required
def team_detail(request, team_id):
    """View team details with members"""
    team = get_object_or_404(
        Team.objects.select_related(
            'manager', 'department', 'company', 'created_by'
        ).prefetch_related(
            'team_members__employee',
            'team_members__added_by'
        ),
        id=team_id
    )

    # Get team members
    members = team.team_members.filter(is_active=True).select_related('employee')

    # Get team statistics
    stats = {
        'total_members': members.count(),
        'available_slots': team.available_slots,
        'full_time_members': members.filter(availability='full_time').count(),
        'part_time_members': members.filter(availability='part_time').count(),
        'avg_allocation': members.aggregate(Avg('allocation_percentage'))['allocation_percentage__avg'] or 0,
    }

    # Get potential team members (employees not in this team)
    from hr.models import Employee
    potential_members = Employee.objects.exclude(
        id__in=members.values_list('employee_id', flat=True)
    ).filter(employment_status='active')

    return render(request, 'project/team_detail.html', {
        'team': team,
        'members': members,
        'stats': stats,
        'potential_members': potential_members,
        'role_choices': TeamMember.ROLE_CHOICES,
        'availability_choices': TeamMember.AVAILABILITY_CHOICES,
    })


@login_required
@require_http_methods(["GET", "POST"])
def team_create(request):
    """Create new team with optional member assignments"""
    if request.method == "POST":
        team_name = request.POST.get('team_name')
        description = request.POST.get('description')
        team_type = request.POST.get('team_type')
        max_members = request.POST.get('max_members', 10)
        department_id = request.POST.get('department')

        # Get company
        company = None
        if hasattr(request, 'tenant'):
            company = request.tenant
        else:
            try:
                from company.models import Company
                company = Company.objects.first()
            except:
                pass

        # Create team
        team = Team.objects.create(
            team_name=team_name,
            description=description,
            team_type=team_type,
            max_members=int(max_members),
            company=company,
            created_by=request.user
        )

        # Set department
        if department_id:
            try:
                from hr.models import Department
                team.department_id = department_id
            except:
                pass

        team.save()

        # Handle member assignments
        member_employees = request.POST.getlist('member_employee[]')
        member_roles = request.POST.getlist('member_role[]')
        member_allocations = request.POST.getlist('member_allocation[]')
        member_rates = request.POST.getlist('member_rate[]')

        # Add team members
        from django.contrib import messages
        added_count = 0
        for i, employee_id in enumerate(member_employees):
            if employee_id:  # Skip empty selections
                try:
                    from hr.models import Employee
                    employee = Employee.objects.get(id=employee_id)

                    # Get values for this member
                    role = member_roles[i] if i < len(member_roles) else 'member'
                    allocation = int(member_allocations[i]) if i < len(member_allocations) and member_allocations[i] else 100
                    rate = float(member_rates[i]) if i < len(member_rates) and member_rates[i] else None

                    # Create team member
                    TeamMember.objects.create(
                        team=team,
                        employee=employee,
                        role=role,
                        allocation_percentage=allocation,
                        hourly_rate=rate,
                        added_by=request.user,
                        is_active=True
                    )
                    added_count += 1

                except Exception as e:
                    messages.warning(request, f'Could not add employee {employee_id}: {str(e)}')

        if added_count > 0:
            messages.success(request, f'Team created successfully with {added_count} member(s).')
        else:
            messages.success(request, 'Team created successfully.')

        return redirect('project:team_detail', team_id=team.id)

    # Get filter options
    from hr.models import Department, Employee
    departments = Department.objects.all() if Department else []
    employees = Employee.objects.filter(employment_status='active') if Employee else []

    # Get team statistics for sidebar
    total_teams = Team.objects.filter(status='active').count()
    total_members = TeamMember.objects.filter(is_active=True).count()

    return render(request, 'project/team_create.html', {
        'departments': departments,
        'employees': employees,
        'team_types': Team.TEAM_TYPE_CHOICES,
        'total_teams': total_teams,
        'total_members': total_members,
    })


@login_required
@require_http_methods(["GET", "POST"])
def team_edit(request, team_id):
    """Edit team details"""
    team = get_object_or_404(Team, id=team_id)

    if request.method == "POST":
        team.team_name = request.POST.get('team_name', team.team_name)
        team.description = request.POST.get('description', team.description)
        team.team_type = request.POST.get('team_type', team.team_type)
        team.max_members = int(request.POST.get('max_members', team.max_members))
        team.status = request.POST.get('status', team.status)

        # Update department
        department_id = request.POST.get('department')
        if department_id:
            try:
                from hr.models import Department
                team.department_id = department_id
            except:
                pass

        team.save()
        return redirect('project:team_detail', team_id=team.id)

    # Get filter options
    from hr.models import Department, Employee
    departments = Department.objects.all() if hasattr(request, 'hr') else []
    employees = Employee.objects.filter(employment_status='active') if hasattr(request, 'hr') else []

    return render(request, 'project/team_edit.html', {
        'team': team,
        'departments': departments,
        'employees': employees,
        'team_types': Team.TEAM_TYPE_CHOICES,
        'status_choices': Team.STATUS_CHOICES,
    })


@login_required
@require_http_methods(["POST"])
def team_member_add(request, team_id):
    """Add member to team"""
    team = get_object_or_404(Team, id=team_id)

    if team.is_full:
        return JsonResponse({'error': 'Team is at maximum capacity'}, status=400)

    employee_id = request.POST.get('employee_id')
    role = request.POST.get('role', 'developer')
    availability = request.POST.get('availability', 'full_time')
    allocation_percentage = int(request.POST.get('allocation_percentage', 100))
    hourly_rate = request.POST.get('hourly_rate')

    try:
        from hr.models import Employee
        employee = Employee.objects.get(id=employee_id)

        # Check if employee is already in this team
        if TeamMember.objects.filter(team=team, employee=employee, is_active=True).exists():
            return JsonResponse({'error': 'Employee is already a member of this team'}, status=400)

        # Create team member
        member = TeamMember.objects.create(
            team=team,
            employee=employee,
            role=role,
            availability=availability,
            allocation_percentage=allocation_percentage,
            hourly_rate=hourly_rate if hourly_rate else None,
            added_by=request.user
        )

        if request.headers.get('HX-Request'):
            return render(request, 'project/partials/team_member_row.html', {
                'member': member,
                'team': team,
            })

        return redirect('project:team_detail', team_id=team.id)

    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def team_member_edit(request, member_id):
    """Edit team member details"""
    member = get_object_or_404(TeamMember, id=member_id)

    # Update member fields
    member.role = request.POST.get('role', member.role)
    member.availability = request.POST.get('availability', member.availability)
    member.allocation_percentage = int(request.POST.get('allocation_percentage', member.allocation_percentage))

    hourly_rate = request.POST.get('hourly_rate')
    if hourly_rate:
        member.hourly_rate = hourly_rate

    # Update permissions
    member.can_manage_team = request.POST.get('can_manage_team') == 'on'
    member.can_assign_tasks = request.POST.get('can_assign_tasks') == 'on'
    member.can_view_reports = request.POST.get('can_view_reports') == 'on'

    member.save()

    if request.headers.get('HX-Request'):
        return render(request, 'project/partials/team_member_row.html', {
            'member': member,
            'team': member.team,
        })

    return redirect('project:team_detail', team_id=member.team.id)


@login_required
@require_http_methods(["DELETE"])
def team_member_remove(request, member_id):
    """Remove member from team"""
    member = get_object_or_404(TeamMember, id=member_id)
    team_id = member.team.id

    member.is_active = False
    member.end_date = timezone.now().date()
    member.save()

    if request.headers.get('HX-Request'):
        return HttpResponse('')

    return redirect('project:team_detail', team_id=team_id)


@login_required
@require_http_methods(["DELETE"])
def team_delete(request, team_id):
    """Delete team (soft delete)"""
    team = get_object_or_404(Team, id=team_id)

    # Archive the team instead of deleting
    team.status = 'archived'
    team.save()

    # Deactivate all team members
    TeamMember.objects.filter(team=team).update(
        is_active=False,
        end_date=timezone.now().date()
    )

    return redirect('project:team_list')


@login_required
def team_projects(request, team_id):
    """View projects assigned to team"""
    team = get_object_or_404(Team, id=team_id)

    # Get projects where team members are assigned
    projects = Project.objects.filter(
        team_members__employee__in=team.team_members.values_list('employee', flat=True)
    ).distinct().select_related(
        'project_manager'
    ).prefetch_related('team_members__employee')

    return render(request, 'project/team_projects.html', {
        'team': team,
        'projects': projects,
    })


# Milestone Management Views

@login_required
def milestone_list(request):
    """List all milestones with filtering"""
    milestones = ProjectMilestone.objects.select_related(
        'project', 'task', 'completed_by', 'approved_by', 'created_by'
    )

    # Filter by project if specified
    project_id = request.GET.get('project')
    if project_id:
        milestones = milestones.filter(project_id=project_id)

    # Status filter
    status = request.GET.get('status')
    if status:
        milestones = milestones.filter(status=status)

    # Milestone type filter
    milestone_type = request.GET.get('type')
    if milestone_type:
        milestones = milestones.filter(milestone_type=milestone_type)

    # Date range filter
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        milestones = milestones.filter(milestone_date__gte=date_from)
    if date_to:
        milestones = milestones.filter(milestone_date__lte=date_to)

    # Search functionality
    search = request.GET.get('search')
    if search:
        milestones = milestones.filter(
            Q(milestone_name__icontains=search) |
            Q(description__icontains=search) |
            Q(project__project_name__icontains=search)
        )

    # Sorting
    sort = request.GET.get('sort', 'milestone_date')
    milestones = milestones.order_by(sort)

    # Pagination
    paginator = Paginator(milestones, 25)
    page = request.GET.get('page', 1)
    milestones_page = paginator.get_page(page)

    # Get projects for filter dropdown
    projects = Project.objects.exclude(status__in=['cancelled']).order_by('project_name')

    # Statistics
    today = timezone.now().date()
    stats = {
        'total': milestones.count(),
        'pending': milestones.filter(status='pending').count(),
        'completed': milestones.filter(status='completed').count(),
        'overdue': milestones.filter(milestone_date__lt=today, status__in=['pending', 'in_progress']).count(),
        'due_this_week': milestones.filter(
            milestone_date__gte=today,
            milestone_date__lte=today + timedelta(days=7)
        ).count(),
    }

    return render(request, 'project/milestone_list.html', {
        'milestones': milestones_page,
        'projects': projects,
        'stats': stats,
        'milestone_types': ProjectMilestone.MILESTONE_TYPE_CHOICES,
        'status_choices': ProjectMilestone.STATUS_CHOICES,
    })


@login_required
def milestone_detail(request, milestone_id):
    """View milestone details"""
    milestone = get_object_or_404(
        ProjectMilestone.objects.select_related(
            'project', 'task', 'completed_by', 'approved_by', 'created_by'
        ).prefetch_related('depends_on_milestones', 'dependent_milestones'),
        id=milestone_id
    )

    # Get related tasks and dependencies
    dependent_milestones = milestone.dependent_milestones.all()
    blocking_dependencies = milestone.get_blocking_dependencies()

    return render(request, 'project/milestone_detail.html', {
        'milestone': milestone,
        'dependent_milestones': dependent_milestones,
        'blocking_dependencies': blocking_dependencies,
    })


@login_required
@require_http_methods(["GET", "POST"])
def milestone_create(request, project_id=None):
    """Create new milestone"""
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        milestone_name = request.POST.get('milestone_name')
        description = request.POST.get('description')
        milestone_type = request.POST.get('milestone_type')
        milestone_date = request.POST.get('milestone_date')
        task_id = request.POST.get('task')
        amount = request.POST.get('amount')
        is_billable = request.POST.get('is_billable') == 'on'
        requires_approval = request.POST.get('requires_approval') == 'on'
        deliverables = request.POST.get('deliverables')
        acceptance_criteria = request.POST.get('acceptance_criteria')

        # Get project if not already set
        if not project:
            project_id = request.POST.get('project')
            project = get_object_or_404(Project, id=project_id)

        milestone = ProjectMilestone.objects.create(
            project=project,
            milestone_name=milestone_name,
            description=description,
            milestone_type=milestone_type,
            milestone_date=milestone_date,
            task_id=task_id if task_id else None,
            amount=amount if amount else None,
            is_billable=is_billable,
            requires_approval=requires_approval,
            deliverables=deliverables,
            acceptance_criteria=acceptance_criteria,
            created_by=request.user
        )

        # Handle dependencies
        dependencies = request.POST.getlist('depends_on_milestones')
        if dependencies:
            milestone.depends_on_milestones.set(dependencies)

        if request.headers.get('HX-Request'):
            return render(request, 'project/partials/milestone_row.html', {
                'milestone': milestone,
            })

        return redirect('project:milestone_detail', milestone_id=milestone.id)

    # Get available projects and tasks
    if project:
        projects = [project]
        tasks = project.tasks.exclude(status='cancelled')
        # TODO: Fix milestone table schema (UUID vs bigint incompatibility)
        available_milestones = ProjectMilestone.objects.none()
    else:
        projects = Project.objects.all().order_by('project_name')
        tasks = ProjectTask.objects.none()
        available_milestones = ProjectMilestone.objects.none()

    return render(request, 'project/milestone_create.html', {
        'project': project,
        'projects': projects,
        'tasks': tasks,
        'available_milestones': available_milestones,
        'milestone_types': ProjectMilestone.MILESTONE_TYPE_CHOICES,
    })


@login_required
@require_http_methods(["GET", "POST"])
def milestone_edit(request, milestone_id):
    """Edit milestone"""
    milestone = get_object_or_404(ProjectMilestone, id=milestone_id)

    if request.method == "POST":
        milestone.milestone_name = request.POST.get('milestone_name', milestone.milestone_name)
        milestone.description = request.POST.get('description', milestone.description)
        milestone.milestone_type = request.POST.get('milestone_type', milestone.milestone_type)
        milestone.milestone_date = request.POST.get('milestone_date', milestone.milestone_date)

        task_id = request.POST.get('task')
        milestone.task_id = task_id if task_id else None

        amount = request.POST.get('amount')
        milestone.amount = amount if amount else None

        milestone.is_billable = request.POST.get('is_billable') == 'on'
        milestone.requires_approval = request.POST.get('requires_approval') == 'on'
        milestone.deliverables = request.POST.get('deliverables', milestone.deliverables)
        milestone.acceptance_criteria = request.POST.get('acceptance_criteria', milestone.acceptance_criteria)

        milestone.save()

        # Handle dependencies
        dependencies = request.POST.getlist('depends_on_milestones')
        milestone.depends_on_milestones.set(dependencies)

        return redirect('project:milestone_detail', milestone_id=milestone.id)

    # Get available tasks and milestones for this project
    tasks = milestone.project.tasks.exclude(status='cancelled')
    # TODO: Fix milestone table schema (UUID vs bigint incompatibility)
    available_milestones = ProjectMilestone.objects.none()

    return render(request, 'project/milestone_edit.html', {
        'milestone': milestone,
        'tasks': tasks,
        'available_milestones': available_milestones,
        'milestone_types': ProjectMilestone.MILESTONE_TYPE_CHOICES,
    })


@login_required
@require_http_methods(["POST"])
def milestone_update_status(request, milestone_id):
    """Update milestone status and completion"""
    milestone = get_object_or_404(ProjectMilestone, id=milestone_id)

    new_status = request.POST.get('status')
    completion_percentage = request.POST.get('completion_percentage')

    if new_status:
        milestone.status = new_status

    if completion_percentage:
        milestone.completion_percentage = float(completion_percentage)

    # Mark as completed if status is completed
    if new_status == 'completed':
        milestone.completion_percentage = 100
        milestone.completed_date = timezone.now().date()

        # Set completed_by if employee exists
        try:
            from hr.models import Employee
            employee = Employee.objects.get(user=request.user)
            milestone.completed_by = employee
        except:
            pass

    milestone.save()

    if request.headers.get('HX-Request'):
        return render(request, 'project/partials/milestone_row.html', {
            'milestone': milestone,
        })

    return redirect('project:milestone_detail', milestone_id=milestone.id)


@login_required
@require_http_methods(["POST"])
def milestone_approve(request, milestone_id):
    """Approve milestone"""
    milestone = get_object_or_404(ProjectMilestone, id=milestone_id)

    if milestone.requires_approval:
        try:
            from hr.models import Employee
            employee = Employee.objects.get(user=request.user)
            milestone.approved_by = employee
            milestone.approved_date = timezone.now()
            milestone.save()
        except:
            pass

    return redirect('project:milestone_detail', milestone_id=milestone.id)


@login_required
@require_http_methods(["DELETE"])
def milestone_delete(request, milestone_id):
    """Delete milestone"""
    milestone = get_object_or_404(ProjectMilestone, id=milestone_id)
    project_id = milestone.project.id

    milestone.delete()

    if request.headers.get('HX-Request'):
        return HttpResponse('')

    return redirect('project:project_detail', project_id=project_id)


@login_required
@require_http_methods(["POST"])
def milestone_create_inline(request, project_id):
    """Create milestone inline from table (Excel-like)"""
    import logging
    logger = logging.getLogger(__name__)

    project = get_object_or_404(Project, id=project_id)

    try:
        # Get data from POST
        milestone_name = request.POST.get('milestone_name', '').strip()
        if not milestone_name:
            return JsonResponse({'error': 'Milestone name is required'}, status=400)

        # Create the milestone with minimal required fields
        milestone = ProjectMilestone.objects.create(
            project=project,
            milestone_name=milestone_name,
            description=request.POST.get('description', ''),
            milestone_type=request.POST.get('milestone_type', 'deliverable'),
            status=request.POST.get('status', 'pending'),
            milestone_date=request.POST.get('milestone_date') if request.POST.get('milestone_date') else None,
            completion_percentage=request.POST.get('completion_percentage', 0),
            amount=request.POST.get('amount') if request.POST.get('amount') else None,
            created_by=request.user
        )


        if request.headers.get('HX-Request'):
            # Return the new milestone row
            return render(request, 'project/partials/milestone_row_inline.html', {
                'milestone': milestone,
                'project': project,
                'today': timezone.now().date(),
            })

        return JsonResponse({'success': True, 'milestone_id': str(milestone.id)})

    except Exception as e:
        logger.exception(f"Error creating milestone: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["POST"])
def milestone_update_inline(request, milestone_id):
    """Update milestone inline from table (Excel-like)"""
    milestone = get_object_or_404(ProjectMilestone, id=milestone_id)

    try:
        # Update fields that are provided
        if 'milestone_name' in request.POST:
            milestone.milestone_name = request.POST['milestone_name']

        if 'description' in request.POST:
            milestone.description = request.POST['description']

        if 'milestone_type' in request.POST:
            milestone.milestone_type = request.POST['milestone_type']

        if 'status' in request.POST:
            milestone.status = request.POST['status']
            # Auto-update completion date when completed
            if milestone.status == 'completed':
                milestone.completed_date = timezone.now().date()
                milestone.completion_percentage = 100

                # Set completed_by if employee exists
                try:
                    from hr.models import Employee
                    employee = Employee.objects.get(user=request.user)
                    milestone.completed_by = employee
                except:
                    pass

        if 'milestone_date' in request.POST:
            milestone.milestone_date = request.POST['milestone_date'] if request.POST['milestone_date'] else None

        if 'completion_percentage' in request.POST:
            milestone.completion_percentage = request.POST['completion_percentage']

        if 'amount' in request.POST:
            milestone.amount = request.POST['amount'] if request.POST['amount'] else None

        milestone.save()

        if request.headers.get('HX-Request'):
            # Return updated milestone row
            return render(request, 'project/partials/milestone_row_inline.html', {
                'milestone': milestone,
                'project': milestone.project,
                'today': timezone.now().date(),
            })

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET", "POST"])
def document_create(request, project_id):
    """Create project document"""
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        document_name = request.POST.get('document_name')
        document_type = request.POST.get('document_type')
        file_url = request.POST.get('file_url')
        description = request.POST.get('description')

        from .models import ProjectDocument
        document = ProjectDocument.objects.create(
            project=project,
            document_name=document_name,
            document_type=document_type,
            file_url=file_url,
            description=description,
            uploaded_by=request.user.employee
        )

        return redirect(f"{reverse('project:project_detail', args=[project.id])}?tab=documents")

    return render(request, 'project/document_create.html', {
        'project': project,
    })


@login_required
@require_http_methods(["GET", "POST"])
def expense_create(request, project_id):
    """Create project expense"""
    project = get_object_or_404(Project, id=project_id)

    if request.method == "POST":
        expense_type = request.POST.get('expense_type')
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        expense_date = request.POST.get('expense_date')
        is_billable = request.POST.get('is_billable') == 'on'
        is_reimbursable = request.POST.get('is_reimbursable') == 'on'

        from .models import ProjectExpense
        import datetime

        # Generate expense code
        expense_code = f"EXP-{project.project_code}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        expense = ProjectExpense.objects.create(
            project=project,
            expense_code=expense_code,
            employee=request.user.employee,
            expense_type=expense_type,
            description=description,
            amount=amount,
            expense_date=expense_date,
            is_billable=is_billable,
            is_reimbursable=is_reimbursable,
            status='draft'
        )

        return redirect(f"{reverse('project:project_detail', args=[project.id])}?tab=expenses")

    return render(request, 'project/expense_create.html', {
        'project': project,
    })
