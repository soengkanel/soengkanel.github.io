from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
from django.utils import timezone
from django.apps import apps
import csv

from .models import SimpleAuditLog
from .simple_logger import SimpleAuditLogger


@login_required
def simple_audit_logs(request):
    """Simple audit logs view - focus on what/when/who"""
    
    # Get all audit logs
    logs = SimpleAuditLog.objects.select_related('user').all()
    
    # Apply filters
    if request.GET.get('user'):
        logs = logs.filter(user__id=request.GET['user'])
    
    if request.GET.get('action'):
        logs = logs.filter(action=request.GET['action'])
    
    if request.GET.get('model'):
        logs = logs.filter(model_name__icontains=request.GET['model'])
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d')
        logs = logs.filter(timestamp__date__gte=start_date.date())
    
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d')
        logs = logs.filter(timestamp__date__lte=end_date.date())
    
    # Search functionality
    if request.GET.get('search'):
        search_term = request.GET['search']
        logs = logs.filter(
            Q(description__icontains=search_term) |
            Q(object_name__icontains=search_term) |
            Q(user__username__icontains=search_term) |
            Q(user__first_name__icontains=search_term) |
            Q(user__last_name__icontains=search_term)
        )
    
    # Order by timestamp (newest first)
    logs = logs.order_by('-timestamp')
    
    # Pagination
    paginator = Paginator(logs, 50)  # Show 50 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options
    users = User.objects.filter(
        id__in=SimpleAuditLog.objects.values_list('user_id', flat=True).distinct()
    ).order_by('username')
    
    actions = SimpleAuditLog.ACTION_CHOICES
    
    models = SimpleAuditLog.objects.values_list('model_name', flat=True).distinct().order_by('model_name')
    
    # Basic statistics
    today = timezone.now().date()
    stats = {
        'total_logs': SimpleAuditLog.objects.count(),
        'today_logs': SimpleAuditLog.objects.filter(timestamp__date=today).count(),
        'this_week_logs': SimpleAuditLog.objects.filter(
            timestamp__date__gte=today - timedelta(days=7)
        ).count(),
        'active_users': SimpleAuditLog.objects.filter(
            timestamp__date__gte=today - timedelta(days=7)
        ).values('user').distinct().count(),
    }
    
    context = {
        'page_obj': page_obj,
        'users': users,
        'actions': actions,
        'models': models,
        'current_filters': request.GET,
        'stats': stats,
    }
    
    return render(request, 'audit_management/simple_logs.html', context)


@login_required
def export_simple_logs(request):
    """Export simple audit logs to CSV"""
    
    # Get filtered logs (same filters as main view)
    logs = SimpleAuditLog.objects.select_related('user').all()
    
    # Apply same filters
    if request.GET.get('user'):
        logs = logs.filter(user__id=request.GET['user'])
    
    if request.GET.get('action'):
        logs = logs.filter(action=request.GET['action'])
    
    if request.GET.get('model'):
        logs = logs.filter(model_name__icontains=request.GET['model'])
    
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET['start_date'], '%Y-%m-%d')
        logs = logs.filter(timestamp__date__gte=start_date.date())
    
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET['end_date'], '%Y-%m-%d')
        logs = logs.filter(timestamp__date__lte=end_date.date())
    
    if request.GET.get('search'):
        search_term = request.GET['search']
        logs = logs.filter(
            Q(description__icontains=search_term) |
            Q(object_name__icontains=search_term) |
            Q(user__username__icontains=search_term)
        )
    
    # Order by timestamp and limit
    logs = logs.order_by('-timestamp')[:5000]  # Limit to 5,000 records
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="audit_logs_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'When (Date & Time)',
        'Who (User)',
        'What Action',
        'What Model',
        'Object Name',
        'Description',
        'Old Values',
        'New Values',
        'IP Address'
    ])
    
    # Write data
    for log in logs:
        writer.writerow([
            log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            log.user_display,
            log.get_action_display(),
            log.model_name,
            log.object_name or '',
            log.description,
            log.old_values or '',
            log.new_values or '',
            log.ip_address or '',
        ])
    
    return response


@login_required
@require_http_methods(["GET", "POST"])
def clear_simple_logs(request):
    """Clear simple audit logs with simple options"""
    
    if request.method == 'GET':
        # Show confirmation page
        total_logs = SimpleAuditLog.objects.count()
        
        context = {
            'total_logs': total_logs,
        }
        return render(request, 'audit_management/clear_simple_logs.html', context)
    
    # POST request - perform the clearing
    clear_type = request.POST.get('clear_type', 'all')
    
    try:
        if clear_type == 'all':
            # Clear everything
            logs_deleted = SimpleAuditLog.objects.count()
            SimpleAuditLog.objects.all().delete()
            
            # Log this action
            SimpleAuditLogger.log_action(
                user=request.user,
                action='delete',
                model_name='SimpleAuditLog',
                description=f"Cleared all audit logs ({logs_deleted} logs)",
                request=request
            )
            
            messages.success(request, f'Successfully cleared {logs_deleted} audit logs.')
            
        elif clear_type == 'older_than':
            # Clear logs older than specified days
            days = request.POST.get('days', '')
            if not days:
                messages.error(request, 'Please specify number of days.')
                return redirect('audit_management:clear_simple_logs')
                
            try:
                days_int = int(days)
                cutoff_date = timezone.now() - timedelta(days=days_int)
                
                logs_deleted = SimpleAuditLog.objects.filter(timestamp__lt=cutoff_date).count()
                SimpleAuditLog.objects.filter(timestamp__lt=cutoff_date).delete()
                
                # Log this action
                SimpleAuditLogger.log_action(
                    user=request.user,
                    action='delete',
                    model_name='SimpleAuditLog',
                    description=f"Cleared audit logs older than {days} days ({logs_deleted} logs)",
                    request=request
                )
                
                messages.success(request, f'Successfully cleared {logs_deleted} audit logs older than {days} days.')
                
            except ValueError:

                
                pass
                messages.error(request, 'Invalid number of days specified.')
                return redirect('audit_management:clear_simple_logs')
        
        else:
            messages.error(request, 'Invalid clear type specified.')
            return redirect('audit_management:clear_simple_logs')
        
    except Exception as e:

        
        pass
        messages.error(request, f'Error clearing logs: {str(e)}')
    
    return redirect('audit_management:simple_logs')


@login_required
def audit_models_settings(request):
    """Manage which models are tracked by the audit system"""
    try:
        from auditlog.registry import auditlog
    except ImportError:
        messages.error(request, 'Auditlog is not available.')
        return redirect('audit_management:simple_logs')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'register':
            app_label = request.POST.get('app_label')
            model_name = request.POST.get('model_name')
            exclude_fields = request.POST.get('exclude_fields', '').split(',')
            exclude_fields = [f.strip() for f in exclude_fields if f.strip()]
            
            try:
                model_class = apps.get_model(app_label, model_name)
                
                # Check if already registered
                if auditlog.contains(model_class):
                    messages.warning(request, f'{app_label}.{model_name} is already registered for audit logging.')
                else:
                    # Register with exclusions if provided
                    if exclude_fields:
                        auditlog.register(model_class, exclude_fields=exclude_fields)
                        messages.success(request, f'{app_label}.{model_name} registered with excluded fields: {", ".join(exclude_fields)}')
                    else:
                        auditlog.register(model_class)
                        messages.success(request, f'{app_label}.{model_name} registered for audit logging.')
                        
            except LookupError:

                        
                pass
                messages.error(request, f'Model {app_label}.{model_name} not found.')
            except Exception as e:
                messages.error(request, f'Error registering model: {str(e)}')
        
        elif action == 'unregister':
            app_label = request.POST.get('app_label')
            model_name = request.POST.get('model_name')
            
            try:
                model_class = apps.get_model(app_label, model_name)
                
                if auditlog.contains(model_class):
                    auditlog.unregister(model_class)
                    messages.success(request, f'{app_label}.{model_name} unregistered from audit logging.')
                else:
                    messages.warning(request, f'{app_label}.{model_name} was not registered.')
                    
            except LookupError:

                    
                pass
                messages.error(request, f'Model {app_label}.{model_name} not found.')
            except Exception as e:
                messages.error(request, f'Error unregistering model: {str(e)}')
        
        return redirect('audit_management:audit_models_settings')
    
    # GET request - show the settings page
    
    # Get all registered models
    registered_models = auditlog.get_models()
    registered_models_info = []
    
    for model in registered_models:
        model_info = {
            'app_label': model._meta.app_label,
            'model_name': model._meta.model_name,
            'verbose_name': str(model._meta.verbose_name),
            'full_name': f'{model._meta.app_label}.{model._meta.model_name}',
        }
        
        # Try to get field configuration (this might not work with all auditlog versions)
        try:
            # Get exclude fields if available
            if hasattr(auditlog, '_registry') and model in auditlog._registry:
                config = auditlog._registry[model]
                if hasattr(config, 'exclude_fields'):
                    model_info['exclude_fields'] = list(config.exclude_fields) if config.exclude_fields else []
                else:
                    model_info['exclude_fields'] = []
            else:
                model_info['exclude_fields'] = []
        except:
            model_info['exclude_fields'] = []
        
        registered_models_info.append(model_info)
    
    # Group by app
    models_by_app = {}
    for model_info in registered_models_info:
        app_label = model_info['app_label']
        if app_label not in models_by_app:
            models_by_app[app_label] = []
        models_by_app[app_label].append(model_info)
    
    # Get all available models for registration
    available_models = []
    registered_lookup = {f"{m._meta.app_label}.{m._meta.model_name}": True for m in registered_models}
    
    for app_config in apps.get_app_configs():
        app_label = app_config.label
        
        # Skip certain apps we don't want to audit
        skip_apps = ['admin', 'auth', 'contenttypes', 'sessions', 'messages', 
                     'staticfiles', 'django_tenants', 'auditlog', 'audit_management']
        if app_label in skip_apps:
            continue
            
        for model in app_config.get_models():
            full_name = f'{app_label}.{model._meta.model_name}'
            is_registered = full_name in registered_lookup
            
            # Add exclude fields info if registered
            exclude_fields = []
            if is_registered:
                for reg_model in registered_models_info:
                    if reg_model['full_name'] == full_name:
                        exclude_fields = reg_model.get('exclude_fields', [])
                        break
            
            model_info = {
                'app_label': app_label,
                'model_name': model._meta.model_name,
                'verbose_name': str(model._meta.verbose_name),
                'full_name': full_name,
                'is_registered': is_registered,
                'exclude_fields': exclude_fields,
                'fields': [f.name for f in model._meta.fields if not f.name.endswith('_ptr')]
            }
            available_models.append(model_info)
    
    # Apply filters based on GET parameters
    filtered_models = available_models.copy()
    
    # Filter by tracking status
    status_filter = request.GET.get('status', '')
    if status_filter == 'tracked':
        filtered_models = [m for m in filtered_models if m['is_registered']]
    elif status_filter == 'untracked':
        filtered_models = [m for m in filtered_models if not m['is_registered']]
    
    # Filter by app
    app_filter = request.GET.get('app', '')
    if app_filter:
        filtered_models = [m for m in filtered_models if m['app_label'] == app_filter]
    
    # Filter by search term
    search_term = request.GET.get('search', '').strip()
    if search_term:
        search_lower = search_term.lower()
        filtered_models = [
            m for m in filtered_models 
            if search_lower in m['model_name'].lower() or search_lower in m['verbose_name'].lower()
        ]
    
    # Group filtered models by app
    filtered_by_app = {}
    for model_info in filtered_models:
        app_label = model_info['app_label']
        if app_label not in filtered_by_app:
            filtered_by_app[app_label] = []
        filtered_by_app[app_label].append(model_info)
    
    # Get unique app labels for filter dropdown
    app_labels = sorted(set(m['app_label'] for m in available_models))
    
    # Calculate totals
    total_untracked = len([m for m in available_models if not m['is_registered']])
    
    context = {
        'registered_models_by_app': dict(sorted(models_by_app.items())),
        'available_models_by_app': dict(sorted(filtered_by_app.items())),
        'total_registered': len(registered_models_info),
        'total_available': len(available_models),
        'total_untracked': total_untracked,
        'filtered_count': len(filtered_models),
        'app_labels': app_labels,
    }
    
    return render(request, 'audit_management/audit_models_settings.html', context)