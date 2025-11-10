from django.shortcuts import render
import json
import csv
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Q, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.contrib.contenttypes.models import ContentType
from auditlog.models import LogEntry

from .models import AuditTrail, AuditSession, AuditException, AuditReport
from .utils import AuditLogger


@login_required
def audit_dashboard(request):
    """Main audit dashboard with statistics and charts"""
    
    # Date range for dashboard (default: last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Get date range from request if provided
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d')
        start_date = timezone.make_aware(start_date)
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d')
        end_date = timezone.make_aware(end_date)
    
    # Basic statistics
    total_logs = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date]
    ).count()
    
    unique_users = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date]
    ).values('user').distinct().count()
    
    high_risk_events = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date],
        risk_score__gte=50
    ).count()
    
    failed_logins = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date],
        action_type='login',
        severity__in=['warning', 'error']
    ).count()
    
    # Activity by action type
    action_stats = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date]
    ).values('action_type').annotate(count=Count('id')).order_by('-count')
    
    # Top users by activity
    user_stats = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date],
        user__isnull=False  # Exclude records without a user
    ).values('user__id', 'user__username', 'user__first_name', 'user__last_name').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Risk distribution
    risk_stats = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date]
    ).extra(
        select={
            'risk_level': """
                CASE 
                    WHEN risk_score >= 80 THEN 'Critical'
                    WHEN risk_score >= 60 THEN 'High'
                    WHEN risk_score >= 40 THEN 'Medium'
                    WHEN risk_score >= 20 THEN 'Low'
                    ELSE 'Minimal'
                END
            """
        }
    ).values('risk_level').annotate(count=Count('id'))
    
    # Recent high-risk events
    recent_high_risk = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date],
        risk_score__gte=50
    ).order_by('-timestamp')[:10]
    
    # Active sessions
    active_sessions = AuditSession.objects.filter(
        is_active=True,
        last_activity__gte=timezone.now() - timedelta(hours=24)
    ).count()
    
    # Unresolved exceptions
    unresolved_exceptions = AuditException.objects.filter(
        resolved=False
    ).count()
    
    context = {
        'total_logs': total_logs,
        'unique_users': unique_users,
        'high_risk_events': high_risk_events,
        'failed_logins': failed_logins,
        'active_sessions': active_sessions,
        'unresolved_exceptions': unresolved_exceptions,
        'action_stats': action_stats,
        'user_stats': user_stats,
        'risk_stats': risk_stats,
        'recent_high_risk': recent_high_risk,
        'start_date': start_date.date(),
        'end_date': end_date.date(),
    }
    
    return render(request, 'audit_management/dashboard.html', context)


@login_required
def audit_logs(request):
    """Display and filter audit logs"""
    
    # Get all audit trails, exclude routine view actions by default
    logs = AuditTrail.objects.select_related('user', 'session').all()
    
    # Hide routine view actions unless specifically requested
    if not request.GET.get('include_views'):
        logs = logs.exclude(action_type='view', resource_type='http_response')
    
    # Apply filters
    if request.GET.get('user'):
        logs = logs.filter(user__id=request.GET['user'])
    
    if request.GET.get('action_type'):
        logs = logs.filter(action_type=request.GET['action_type'])
    
    if request.GET.get('resource_type'):
        logs = logs.filter(resource_type__icontains=request.GET['resource_type'])
    
    if request.GET.get('severity'):
        logs = logs.filter(severity=request.GET['severity'])
    
    if request.GET.get('risk_level'):
        risk_level = request.GET['risk_level']
        if risk_level == 'critical':
            logs = logs.filter(risk_score__gte=80)
        elif risk_level == 'high':
            logs = logs.filter(risk_score__gte=60, risk_score__lt=80)
        elif risk_level == 'medium':
            logs = logs.filter(risk_score__gte=40, risk_score__lt=60)
        elif risk_level == 'low':
            logs = logs.filter(risk_score__gte=20, risk_score__lt=40)
        elif risk_level == 'minimal':
            logs = logs.filter(risk_score__lt=20)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d')
        logs = logs.filter(timestamp__date__gte=start_date.date())
    
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d')
        logs = logs.filter(timestamp__date__lte=end_date.date())
    
    if request.GET.get('correlation_id'):
        logs = logs.filter(correlation_id=request.GET['correlation_id'])
    
    # Search functionality
    if request.GET.get('search'):
        search_term = request.GET['search']
        logs = logs.filter(
            Q(description__icontains=search_term) |
            Q(resource_name__icontains=search_term) |
            Q(user__username__icontains=search_term) |
            Q(user__first_name__icontains=search_term) |
            Q(user__last_name__icontains=search_term)
        )
    
    # Order by timestamp (newest first)
    logs = logs.order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(logs, 25)  # Show 25 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get distinct values for filters
    # 1. Get action types from custom AuditTrail (exclude routine view actions)
    custom_action_types = AuditTrail.objects.exclude(
        action_type='view', resource_type='http_response'
    ).values_list('action_type', flat=True).distinct()
    
    # Get django-auditlog action types
    django_action_values = LogEntry.objects.values_list('action', flat=True).distinct()
    # Map numeric values to readable names
    action_map = {0: 'create', 1: 'update', 2: 'delete', 3: 'access'}
    django_action_types = [action_map.get(action, f'unknown_{action}') for action in django_action_values if action is not None]
    
    # Combine both sources
    all_action_types = list(custom_action_types) + django_action_types
    
    # 2. Get resource types from both custom AuditTrail AND django-auditlog
    custom_resource_types = AuditTrail.objects.exclude(
        action_type='view', resource_type='http_response'
    ).values_list('resource_type', flat=True).distinct()
    
    # Get django-auditlog model types
    django_log_types = LogEntry.objects.select_related('content_type').values_list(
        'content_type__app_label', 'content_type__model'
    ).distinct()
    
    # Format django-auditlog types as "app.model"
    django_resource_types = [f"{app}.{model}" for app, model in django_log_types if app and model]
    
    # Combine both sources
    all_resource_types = list(custom_resource_types) + django_resource_types
    
    # Remove duplicates and None values, sort alphabetically
    action_types = sorted(list(set([t for t in all_action_types if t])))
    resource_types = sorted(list(set([t for t in all_resource_types if t])))
    
    # 3. Get users who have audit logs (from both systems)
    from django.contrib.auth.models import User
    custom_user_ids = AuditTrail.objects.values_list('user_id', flat=True).distinct()
    django_user_ids = LogEntry.objects.values_list('actor_id', flat=True).distinct()
    all_user_ids = list(set(list(custom_user_ids) + [uid for uid in django_user_ids if uid is not None]))
    
    # Convert to integers and get user objects
    user_ids = [int(uid) for uid in all_user_ids if uid is not None]
    users = User.objects.filter(id__in=user_ids).order_by('username')
    
    context = {
        'page_obj': page_obj,
        'action_types': action_types,
        'resource_types': resource_types,
        'users': users,
        'current_filters': request.GET,
    }
    
    return render(request, 'audit_management/audit_logs.html', context)


@login_required
def log_detail(request, log_id):
    """Display detailed view of a single audit log"""
    
    log = get_object_or_404(AuditTrail, id=log_id)
    
    # Get related logs with same correlation ID
    related_logs = AuditTrail.objects.filter(
        correlation_id=log.correlation_id
    ).exclude(id=log.id).order_by('timestamp')
    
    # Get django-auditlog entry if available
    django_log = None
    if log.log_entry:
        django_log = log.log_entry
    
    context = {
        'log': log,
        'related_logs': related_logs,
        'django_log': django_log,
    }
    
    return render(request, 'audit_management/log_detail.html', context)


@login_required
def audit_sessions(request):
    """Display audit sessions"""
    
    sessions = AuditSession.objects.select_related('user').all()
    
    # Apply filters
    if request.GET.get('user'):
        sessions = sessions.filter(user__username__icontains=request.GET['user'])
    
    if request.GET.get('active') == 'true':
        sessions = sessions.filter(is_active=True)
    elif request.GET.get('active') == 'false':
        sessions = sessions.filter(is_active=False)
    
    # Order by start time (newest first)
    sessions = sessions.order_by('-started_at')
    
    # Pagination
    paginator = Paginator(sessions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_filters': request.GET,
    }
    
    return render(request, 'audit_management/sessions.html', context)


@login_required
def user_activity(request, user_id):
    """Display activity for a specific user"""
    
    user = get_object_or_404(User, id=user_id)
    
    # Get date range (default: last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d')
        start_date = timezone.make_aware(start_date)
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d')
        end_date = timezone.make_aware(end_date)
    
    # Get user activity summary
    activity_summary = AuditLogger.get_user_activity_summary(user, 30)
    
    # Get user's audit logs
    logs = AuditTrail.objects.filter(
        user=user,
        timestamp__range=[start_date, end_date]
    ).order_by('-timestamp')
    
    # Get user's sessions
    sessions = AuditSession.objects.filter(
        user=user,
        started_at__range=[start_date, end_date]
    ).order_by('-started_at')
    
    # Activity by day
    daily_activity = logs.extra(
        select={'day': "DATE(timestamp)"}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    context = {
        'target_user': user,
        'activity_summary': activity_summary,
        'logs': logs[:50],  # Show last 50 logs
        'sessions': sessions[:10],  # Show last 10 sessions
        'daily_activity': daily_activity,
        'start_date': start_date.date(),
        'end_date': end_date.date(),
    }
    
    return render(request, 'audit_management/user_activity.html', context)


@login_required
def audit_exceptions(request):
    """Display and manage audit exceptions"""
    
    exceptions = AuditException.objects.select_related(
        'user', 'resolved_by'
    ).all()
    
    # Apply filters
    if request.GET.get('exception_type'):
        exceptions = exceptions.filter(exception_type=request.GET['exception_type'])
    
    if request.GET.get('resolved') == 'true':
        exceptions = exceptions.filter(resolved=True)
    elif request.GET.get('resolved') == 'false':
        exceptions = exceptions.filter(resolved=False)
    
    # Order by timestamp (newest first)
    exceptions = exceptions.order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(exceptions, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'current_filters': request.GET,
    }
    
    return render(request, 'audit_management/exceptions.html', context)


@login_required
@require_http_methods(["POST"])
def resolve_exception(request, exception_id):
    """Resolve an audit exception"""
    
    exception = get_object_or_404(AuditException, id=exception_id)
    
    resolution_notes = request.POST.get('resolution_notes', '')
    
    exception.resolved = True
    exception.resolved_by = request.user
    exception.resolved_at = timezone.now()
    exception.resolution_notes = resolution_notes
    exception.save()
    
    # Log the resolution
    AuditLogger.log_action(
        user=request.user,
        action_type='update',
        resource_type='audit_exception',
        resource_id=exception.id,
        description=f"Resolved audit exception: {exception.exception_type}",
        request=request
    )
    
    messages.success(request, "Exception resolved successfully.")
    return redirect('audit_management:exceptions')


@login_required
def export_logs(request):
    """Export audit logs to CSV"""
    
    # Get filtered logs (same as audit_logs view)
    logs = AuditTrail.objects.select_related('user', 'session').all()
    
    # Apply same filters as audit_logs view
    if request.GET.get('user'):
        logs = logs.filter(user__username__icontains=request.GET['user'])
    
    if request.GET.get('action_type'):
        logs = logs.filter(action_type=request.GET['action_type'])
    
    if request.GET.get('resource_type'):
        logs = logs.filter(resource_type__icontains=request.GET['resource_type'])
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d')
        logs = logs.filter(timestamp__date__gte=start_date.date())
    
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d')
        logs = logs.filter(timestamp__date__lte=end_date.date())
    
    # Order by timestamp
    logs = logs.order_by('-timestamp')
    
    # Limit to prevent performance issues
    logs = logs[:10000]  # Limit to 10,000 records
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Timestamp',
        'User',
        'Action Type',
        'Resource Type',
        'Resource ID',
        'Resource Name',
        'Description',
        'Severity',
        'Risk Score',
        'IP Address',
        'Request Path',
        'Correlation ID',
        'Department',
        'Location',
    ])
    
    # Write data
    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.user.username if log.user else '',
            log.action_type,
            log.resource_type,
            log.resource_id,
            log.resource_name,
            log.description,
            log.severity,
            log.risk_score,
            log.ip_address,
            log.request_path,
            log.correlation_id,
            log.department,
            log.location,
        ])
    
    # Log the export
    AuditLogger.log_data_export(
        user=request.user,
        resource_type='audit_logs',
        count=logs.count(),
        request=request
    )
    
    return response


@login_required
def api_logs_data(request):
    """API endpoint for audit logs data (for AJAX/charts)"""
    
    # Get date range
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Activity by day
    daily_activity = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date]
    ).extra(
        select={'day': "DATE(timestamp)"}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Activity by action type
    action_activity = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date]
    ).values('action_type').annotate(count=Count('id')).order_by('-count')
    
    # Risk distribution
    risk_distribution = AuditTrail.objects.filter(
        timestamp__range=[start_date, end_date]
    ).extra(
        select={
            'risk_level': """
                CASE 
                    WHEN risk_score >= 80 THEN 'Critical'
                    WHEN risk_score >= 60 THEN 'High'
                    WHEN risk_score >= 40 THEN 'Medium'
                    WHEN risk_score >= 20 THEN 'Low'
                    ELSE 'Minimal'
                END
            """
        }
    ).values('risk_level').annotate(count=Count('id'))
    
    data = {
        'daily_activity': list(daily_activity),
        'action_activity': list(action_activity),
        'risk_distribution': list(risk_distribution),
    }
    
    return JsonResponse(data)


@login_required
def search_logs(request):
    """Search audit logs via AJAX"""
    
    query = request.GET.get('q', '')
    if len(query) < 3:
        return JsonResponse({'results': []})
    
    logs = AuditTrail.objects.filter(
        Q(description__icontains=query) |
        Q(resource_name__icontains=query) |
        Q(user__username__icontains=query) |
        Q(correlation_id__icontains=query)
    ).select_related('user')[:20]
    
    results = []
    for log in logs:
        results.append({
            'id': log.id,
            'description': log.description,
            'user': log.user.username if log.user else 'System',
            'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'action_type': log.action_type,
            'resource_type': log.resource_type,
            'severity': log.severity,
            'risk_score': log.risk_score,
        })
    
    return JsonResponse({'results': results})


@login_required
@require_http_methods(["GET", "POST"])
def clear_logs(request):
    """Clear audit logs with options"""
    
    if request.method == 'GET':
        # Show confirmation page
        total_logs = AuditTrail.objects.count()
        total_sessions = AuditSession.objects.count()
        total_exceptions = AuditException.objects.count()
        
        # Get action and resource types for selective clearing
        action_types = list(set([t for t in AuditTrail.objects.values_list('action_type', flat=True).distinct() if t]))
        resource_types = list(set([t for t in AuditTrail.objects.values_list('resource_type', flat=True).distinct() if t]))
        action_types.sort()
        resource_types.sort()
        
        context = {
            'total_logs': total_logs,
            'total_sessions': total_sessions,
            'total_exceptions': total_exceptions,
            'action_types': action_types,
            'resource_types': resource_types,
        }
        return render(request, 'audit_management/clear_logs.html', context)
    
    # POST request - perform the clearing
    clear_type = request.POST.get('clear_type', 'all')
    days = request.POST.get('days', '')
    
    try:
        if clear_type == 'all':
            # Clear everything
            logs_deleted = AuditTrail.objects.count()
            sessions_deleted = AuditSession.objects.filter(is_active=False).count()
            exceptions_deleted = AuditException.objects.count()
            
            AuditTrail.objects.all().delete()
            AuditSession.objects.filter(is_active=False).delete()
            AuditException.objects.all().delete()
            
            # Log this action
            AuditLogger.log_action(
                user=request.user,
                action_type='delete',
                resource_type='audit_logs',
                description=f"Cleared all audit logs ({logs_deleted} logs, {sessions_deleted} sessions, {exceptions_deleted} exceptions)",
                severity='warning',
                risk_score=80,
                request=request,
                tags=['maintenance', 'bulk_delete', 'admin_action']
            )
            
            messages.success(request, f'Successfully cleared {logs_deleted} audit logs, {sessions_deleted} sessions, and {exceptions_deleted} exceptions.')
            
        elif clear_type == 'older_than' and days:
            # Clear logs older than specified days
            try:
                days_int = int(days)
                cutoff_date = timezone.now() - timedelta(days=days_int)
                
                logs_deleted = AuditTrail.objects.filter(timestamp__lt=cutoff_date).count()
                sessions_deleted = AuditSession.objects.filter(
                    last_activity__lt=cutoff_date, 
                    is_active=False
                ).count()
                exceptions_deleted = AuditException.objects.filter(timestamp__lt=cutoff_date).count()
                
                AuditTrail.objects.filter(timestamp__lt=cutoff_date).delete()
                AuditSession.objects.filter(last_activity__lt=cutoff_date, is_active=False).delete()
                AuditException.objects.filter(timestamp__lt=cutoff_date).delete()
                
                # Log this action
                AuditLogger.log_action(
                    user=request.user,
                    action_type='delete',
                    resource_type='audit_logs',
                    description=f"Cleared audit logs older than {days} days ({logs_deleted} logs, {sessions_deleted} sessions, {exceptions_deleted} exceptions)",
                    severity='info',
                    risk_score=40,
                    request=request,
                    tags=['maintenance', 'cleanup', 'retention_policy']
                )
                
                messages.success(request, f'Successfully cleared {logs_deleted} audit logs, {sessions_deleted} sessions, and {exceptions_deleted} exceptions older than {days} days.')
                
            except ValueError:

                
                pass
                messages.error(request, 'Invalid number of days specified.')
                return redirect('audit_management:clear_logs')
        
        elif clear_type == 'by_type':
            # Clear specific types
            action_type = request.POST.get('action_type', '')
            resource_type = request.POST.get('resource_type', '')
            
            queryset = AuditTrail.objects.all()
            filter_desc = []
            
            if action_type:
                queryset = queryset.filter(action_type=action_type)
                filter_desc.append(f"action: {action_type}")
            if resource_type:
                queryset = queryset.filter(resource_type=resource_type)
                filter_desc.append(f"resource: {resource_type}")
            
            logs_deleted = queryset.count()
            queryset.delete()
            
            # Log this action
            AuditLogger.log_action(
                user=request.user,
                action_type='delete',
                resource_type='audit_logs',
                description=f"Cleared {logs_deleted} audit logs ({', '.join(filter_desc)})",
                severity='info',
                risk_score=30,
                request=request,
                tags=['maintenance', 'selective_cleanup']
            )
            
            messages.success(request, f'Successfully cleared {logs_deleted} audit logs matching the specified criteria.')
        
    except Exception as e:

        
        pass
        messages.error(request, f'Error clearing logs: {str(e)}')
    
    return redirect('audit_management:dashboard')
