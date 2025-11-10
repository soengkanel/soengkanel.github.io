from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch, OuterRef, Subquery
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import random
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

from .models import CertificateRequest, Form, FormField, FormSubmission, FormTemplate, ExtensionRequest, CertificateRequestWorkerService
from zone.models import Document, Worker
from django.core.files.storage import default_storage


@login_required
def form_list(request):
    """Display list of forms created by user"""
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    forms = Form.objects.filter(created_by=request.user)
    
    if search_query:
        forms = forms.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    if status_filter:
        forms = forms.filter(status=status_filter)
    
    paginator = Paginator(forms, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Form.STATUS_CHOICES,
    }
    return render(request, 'eform/form_list.html', context)


@login_required
@permission_required('eform.add_form', raise_exception=True)
def create_form(request):
    """Create a new form"""
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        template_id = request.POST.get('template_id')

        if title:
            new_form = Form.objects.create(
                title=title,
                description=description,
                created_by=request.user
            )

            # If using a template, create fields from template
            if template_id:
                try:
                    template = FormTemplate.objects.get(id=template_id)
                    fields_data = template.template_data.get('fields', [])

                    for field_data in fields_data:
                        FormField.objects.create(
                            form=new_form,
                            label=field_data.get('label', ''),
                            field_type=field_data.get('field_type', 'text'),
                            help_text=field_data.get('help_text', ''),
                            is_required=field_data.get('is_required', False),
                            order=field_data.get('order', 0),
                            options=field_data.get('options', []),
                            min_length=field_data.get('min_length'),
                            max_length=field_data.get('max_length'),
                            min_value=field_data.get('min_value'),
                            max_value=field_data.get('max_value'),
                            pattern=field_data.get('pattern', ''),
                            default_value=field_data.get('default_value', ''),
                            placeholder=field_data.get('placeholder', ''),
                        )
                    messages.success(request, f'Form "{new_form.title}" created from template successfully!')
                except FormTemplate.DoesNotExist:
                    messages.warning(request, f'Form created, but template not found.')
            else:
                messages.success(request, f'Form "{new_form.title}" created successfully!')

            return redirect('eform:form_builder', form_id=new_form.id)
        else:
            messages.error(request, 'Title is required.')

    # Check if template is selected via GET parameter
    template_id = request.GET.get('template')
    selected_template = None
    if template_id:
        try:
            selected_template = FormTemplate.objects.get(id=template_id)
        except FormTemplate.DoesNotExist:
            pass

    # Get available templates
    templates = FormTemplate.objects.filter(
        Q(is_public=True) | Q(created_by=request.user)
    ).order_by('category', 'name')

    context = {
        'templates': templates,
        'selected_template': selected_template,
    }
    return render(request, 'eform/create_form.html', context)


@login_required
def form_builder(request, form_id):
    """Form builder interface"""
    form = get_object_or_404(Form, id=form_id, created_by=request.user)
    
    if request.method == 'POST':
        # Handle form field updates via AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            action = request.POST.get('action')
            
            if action == 'add_field':
                field_data = json.loads(request.POST.get('field_data'))
                field = FormField.objects.create(
                    form=form,
                    label=field_data['label'],
                    field_type=field_data['field_type'],
                    help_text=field_data.get('help_text', ''),
                    is_required=field_data.get('is_required', False),
                    order=field_data.get('order', 0),
                    options=field_data.get('options', []),
                    placeholder=field_data.get('placeholder', ''),
                )
                return JsonResponse({'success': True, 'field_id': field.id})
            
            elif action == 'update_field':
                field_id = request.POST.get('field_id')
                field = get_object_or_404(FormField, id=field_id, form=form)
                field_data = json.loads(request.POST.get('field_data'))
                
                field.label = field_data['label']
                field.field_type = field_data['field_type']
                field.help_text = field_data.get('help_text', '')
                field.is_required = field_data.get('is_required', False)
                field.order = field_data.get('order', field.order)
                field.options = field_data.get('options', [])
                field.placeholder = field_data.get('placeholder', '')
                field.save()
                
                return JsonResponse({'success': True})
            
            elif action == 'delete_field':
                field_id = request.POST.get('field_id')
                field = get_object_or_404(FormField, id=field_id, form=form)
                field.delete()
                return JsonResponse({'success': True})
            
            elif action == 'reorder_fields':
                field_orders = json.loads(request.POST.get('field_orders'))
                for field_id, order in field_orders.items():
                    FormField.objects.filter(id=field_id, form=form).update(order=order)
                return JsonResponse({'success': True})
    
    context = {
        'form': form,
        'fields': form.fields.all(),
        'field_types': FormField.FIELD_TYPES,
    }
    return render(request, 'eform/form_builder.html', context)


def view_form(request, form_id):
    """View a published form (public access)"""
    form = get_object_or_404(Form, id=form_id)
    
    # Check if form is accessible
    if form.status != 'published':
        if not request.user.is_authenticated or form.created_by != request.user:
            messages.error(request, 'This form is not available.')
            return redirect('eform:form_list')
    
    if form.require_login and not request.user.is_authenticated:
        messages.info(request, 'You need to log in to access this form.')
        return redirect('login')
    
    if form.submission_deadline and timezone.now() > form.submission_deadline:
        messages.warning(request, 'The submission deadline for this form has passed.')
        return render(request, 'eform/form_expired.html', {'form': form})
    
    context = {
        'form': form,
        'fields': form.fields.all(),
    }
    return render(request, 'eform/view_form.html', context)


def fill_form(request, form_id):
    """Fill and submit a form"""
    form = get_object_or_404(Form, id=form_id)
    
    # Check form accessibility
    if form.status != 'published':
        messages.error(request, 'This form is not available.')
        return redirect('eform:form_list')
    
    if form.require_login and not request.user.is_authenticated:
        messages.info(request, 'You need to log in to submit this form.')
        return redirect('login')
    
    if form.submission_deadline and timezone.now() > form.submission_deadline:
        messages.warning(request, 'The submission deadline for this form has passed.')
        return render(request, 'eform/form_expired.html', {'form': form})
    
    # Check for existing submissions if multiple submissions not allowed
    if not form.allow_multiple_submissions and request.user.is_authenticated:
        existing_submission = FormSubmission.objects.filter(
            form=form, submitted_by=request.user
        ).first()
        if existing_submission:
            messages.info(request, 'You have already submitted this form.')
            return render(request, 'eform/submission_exists.html', {
                'form': form,
                'submission': existing_submission
            })
    
    if request.method == 'POST':
        # Process form submission
        submission_data = {}
        email = ''
        
        for field in form.fields.all():
            field_name = f'field_{field.id}'
            value = request.POST.get(field_name, '')
            
            if field.field_type == 'checkbox':
                value = request.POST.getlist(field_name)
            
            submission_data[field.label] = value
            
            # Basic validation
            if field.is_required and not value:
                messages.error(request, f'Field "{field.label}" is required.')
                return render(request, 'eform/fill_form.html', {
                    'form': form,
                    'fields': form.fields.all(),
                    'submitted_data': request.POST
                })
        
        if form.collect_email:
            email = request.POST.get('email', '')
            if not email and not request.user.is_authenticated:
                messages.error(request, 'Email is required.')
                return render(request, 'eform/fill_form.html', {
                    'form': form,
                    'fields': form.fields.all(),
                    'submitted_data': request.POST
                })
        
        # Create submission
        submission = FormSubmission.objects.create(
            form=form,
            submitted_by=request.user if request.user.is_authenticated else None,
            data=submission_data,
            email=email,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, 'Your form has been submitted successfully!')
        return render(request, 'eform/submission_success.html', {
            'form': form,
            'submission': submission
        })
    
    context = {
        'form': form,
        'fields': form.fields.all(),
    }
    return render(request, 'eform/fill_form.html', context)


@login_required
def form_submissions(request, form_id):
    """View submissions for a form"""
    form = get_object_or_404(Form, id=form_id, created_by=request.user)
    
    search_query = request.GET.get('search', '')
    submissions = form.submissions.all()
    
    if search_query:
        submissions = submissions.filter(
            Q(submitted_by__username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(data__icontains=search_query)
        )
    
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'search_query': search_query,
    }
    return render(request, 'eform/form_submissions.html', context)


@login_required
def view_submission(request, submission_id):
    """View a specific form submission"""
    submission = get_object_or_404(FormSubmission, id=submission_id)

    # Check if user can view this submission
    if submission.form.created_by != request.user and submission.submitted_by != request.user:
        messages.error(request, 'You do not have permission to view this submission.')
        return redirect('eform:form_list')

    # Get employees for employee name lookup
    from hr.models import Employee
    employees = Employee.objects.all()  # Get all employees including inactive

    # Process submission data to convert employee IDs to names
    processed_data = {}
    if submission.data:
        for key, value in submission.data.items():
            if key == 'Employee Name' and value:
                # Check if value is a numeric ID (old format)
                if str(value).isdigit():
                    try:
                        employee = Employee.objects.get(id=int(value))
                        processed_data[key] = employee.full_name
                        processed_data['Employee ID'] = employee.employee_id or 'Not set'
                    except Employee.DoesNotExist:
                        processed_data[key] = f"Employee #{value} (not found)"
                else:
                    processed_data[key] = value
            else:
                processed_data[key] = value

    context = {
        'submission': submission,
        'form': submission.form,
        'employees': employees,
        'processed_data': processed_data or submission.data,
    }
    return render(request, 'eform/view_submission.html', context)


@login_required
def edit_submission(request, submission_id):
    """Edit a form submission"""
    submission = get_object_or_404(FormSubmission, id=submission_id)

    # Check if user can edit this submission
    if submission.submitted_by != request.user:
        messages.error(request, 'You do not have permission to edit this submission.')
        return redirect('eform:form_list')

    # Get the form template for this submission
    form_title = submission.form.title
    form_slug = None

    # Map form titles back to slugs
    form_mapping = {
        'Dental Claim Form': 'dental-claim',
        'Medical Claim Form': 'medical-claim',
        'Payment Request Form 001': 'payment-request',
        'Resignation Form': 'resignation',
        'Probation Evaluation Form': 'probation-evaluation',
        'Travel Request Form 001': 'travel-request',
    }

    form_slug = form_mapping.get(form_title)

    if not form_slug:
        messages.error(request, 'Form type not recognized.')
        return redirect('eform:form_list')

    # Get form template
    try:
        form_template = FormTemplate.objects.get(name=form_title)
    except FormTemplate.DoesNotExist:
        messages.error(request, 'Form template not found.')
        return redirect('eform:form_list')

    # Handle form submission
    if request.method == 'POST':
        from hr.models import Employee, Department

        form_data = {}
        files = {}

        # Collect form data
        for field_data in form_template.template_data.get('fields', []):
            field_label = field_data['label']
            field_type = field_data['field_type']

            if field_type == 'file':
                if field_label in request.FILES:
                    uploaded_file = request.FILES[field_label]
                    # Save file
                    file_path = default_storage.save(
                        f'form_submissions/{form_slug}/{uploaded_file.name}',
                        uploaded_file
                    )
                    files[field_label] = file_path
                else:
                    # Keep existing file if no new file uploaded
                    if field_label in submission.data:
                        files[field_label] = submission.data[field_label]
            else:
                # Handle special autocomplete fields
                if field_label == 'Employee Name':
                    # Get employee ID from autocomplete and convert to name
                    employee_id = request.POST.get('employee', '')
                    if employee_id:
                        try:
                            employee = Employee.objects.get(id=employee_id)
                            form_data[field_label] = employee.full_name
                            # Also store the employee ID in a separate field
                            form_data['Employee ID'] = employee.employee_id or ''
                        except Employee.DoesNotExist:
                            form_data[field_label] = ''
                    else:
                        form_data[field_label] = ''
                elif field_label == 'Employee ID':
                    # Skip - handled by employee name autocomplete
                    continue
                elif field_label == 'Department':
                    # Get department ID from autocomplete and convert to name
                    department_id = request.POST.get('department', '')
                    if department_id:
                        try:
                            department = Department.objects.get(id=department_id)
                            form_data[field_label] = department.name
                        except Department.DoesNotExist:
                            form_data[field_label] = ''
                    else:
                        form_data[field_label] = ''
                else:
                    form_data[field_label] = request.POST.get(field_label, '')

        # Combine form data and file paths
        submission_data = {**form_data, **files}

        # Update submission
        submission.data = submission_data
        submission.save()

        messages.success(request, f'{form_title} updated successfully!')
        return redirect('eform:quick_form_list', form_slug=form_slug)

    # Get employees and departments for form
    from hr.models import Employee, Department
    employees = Employee.objects.filter(employment_status='active').order_by('first_name', 'last_name')
    departments = Department.objects.all().order_by('name')

    # Process submission data to convert old numeric IDs to names for display
    processed_data = {}
    if submission.data:
        for key, value in submission.data.items():
            if key == 'Employee Name' and value:
                # Check if value is a numeric ID (old format)
                if str(value).isdigit():
                    try:
                        employee = Employee.objects.get(id=int(value))
                        processed_data[key] = employee.full_name
                        processed_data['Employee ID'] = employee.employee_id or ''
                    except Employee.DoesNotExist:
                        processed_data[key] = value
                else:
                    processed_data[key] = value
            else:
                processed_data[key] = value

    # Update submission.data with processed data for template display
    submission.data = processed_data or submission.data

    context = {
        'submission': submission,
        'form_template': form_template,
        'fields': form_template.template_data.get('fields', []),
        'form_slug': form_slug,
        'employees': employees,
        'departments': departments,
        'is_edit': True,
    }
    return render(request, 'eform/edit_submission.html', context)


@login_required
def delete_form(request, form_id):
    """Delete a form"""
    form = get_object_or_404(Form, id=form_id, created_by=request.user)
    
    if request.method == 'POST':
        form_title = form.title
        form.delete()
        messages.success(request, f'Form "{form_title}" has been deleted.')
        return redirect('eform:form_list')
    
    context = {
        'form': form,
    }
    return render(request, 'eform/delete_form.html', context)


# Operations Dashboard Views
@login_required
@permission_required('eform.view_form', raise_exception=True)
def operations_dashboard(request):
    """Operations dashboard with E-Forms menu"""
    context = {
        'total_workers': Worker.objects.count(),
        'active_workers': Worker.objects.filter(status='active').count(),
    }
    return render(request, 'eform/operations_dashboard.html', context)


@login_required
def unified_dashboard(request):
    """Ultra-streamlined E-Forms dashboard with one-page workflow"""
    # Get comprehensive statistics for better UX
    total_workers = Worker.objects.count()
    active_workers = Worker.objects.filter(status='active').count()
    
    # Workers with permits expiring soon (next 30 days)
    today = timezone.now().date()
    expiring_soon = Worker.objects.filter(
        documents__document_type='work_permit',
        documents__expiry_date__isnull=False,
        documents__expiry_date__lte=today + timedelta(days=30),
        documents__expiry_date__gte=today,
        status='active'
    ).distinct().count()
    
    # Recent extension and certificate requests for quick access
    from .models import ExtensionRequest, CertificateRequest
    recent_extensions = ExtensionRequest.objects.select_related('worker').order_by('-created_at')[:3]
    recent_certificates = CertificateRequest.objects.prefetch_related('workers').order_by('-created_at')[:3]
    
    context = {
        'total_workers': total_workers,
        'active_workers': active_workers,
        'expiring_soon': expiring_soon,
        'recent_extensions': recent_extensions,
        'recent_certificates': recent_certificates,
        'today': today,
    }
    return render(request, 'eform/eforms_unified_dashboard.html', context)


@login_required
def ajax_load_workers(request):
    """AJAX endpoint to load workers for unified dashboard"""
    search_query = request.GET.get('search', '')
    worker_type = request.GET.get('type', 'all')  # 'extension' or 'certificate'
    filter_type = request.GET.get('filter', 'all')  # 'all', 'expiring', 'expired', 'active', 'recent'
    
    workers = Worker.objects.filter(status='active').select_related(
        'zone', 'building', 'position'
    ).order_by('first_name', 'last_name')
    
    # Apply search filter
    if search_query:
        workers = workers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(worker_id__icontains=search_query) |
            Q(position__name__icontains=search_query) |
            Q(building__name__icontains=search_query) |
            Q(nationality__icontains=search_query)
        ).distinct()
    
    # Apply type-specific filters
    today = timezone.now().date()
    if filter_type == 'expiring':
        workers = workers.filter(
            documents__document_type='work_permit',
            documents__expiry_date__lte=today + timedelta(days=30),
            documents__expiry_date__gte=today
        ).distinct()
    elif filter_type == 'expired':
        workers = workers.filter(
            documents__document_type='work_permit',
            documents__expiry_date__lt=today
        ).distinct()
    elif filter_type == 'recent':
        workers = workers.filter(created_at__gte=today - timedelta(days=7))
    
    # Limit results for performance
    workers = workers[:50]
    
    worker_data = []
    for worker in workers:
        # Calculate expiry status for extensions
        expiry_status = ""
        if worker_type == 'extension':
            # Check work permit expiry
            work_permit = worker.documents.filter(document_type='work_permit', expiry_date__isnull=False).first()
            if work_permit and work_permit.expiry_date:
                days_until_expiry = (work_permit.expiry_date - today).days
                if days_until_expiry < 0:
                    expiry_status = f"Expired {abs(days_until_expiry)} days ago"
                elif days_until_expiry <= 30:
                    expiry_status = f"Expires in {days_until_expiry} days"
                else:
                    expiry_status = f"Expires {work_permit.expiry_date.strftime('%b %d, %Y')}"
            else:
                expiry_status = "No permit found"
        
        worker_data.append({
            'id': worker.id,
            'name': worker.get_full_name(),
            'initials': f"{worker.first_name[0] if worker.first_name else ''}{worker.last_name[0] if worker.last_name else ''}",
            'position': worker.position.name if worker.position else 'No Position',
            'building': worker.building.name if worker.building else 'No Building',
            'status': worker.get_status_display(),
            'expiry_status': expiry_status,
            'details': f"{worker.position.name if worker.position else 'No Position'} • {worker.building.name if worker.building else 'No Building'} • {expiry_status if expiry_status else worker.get_status_display()}"
        })
    
    return JsonResponse({
        'workers': worker_data,
        'total': len(worker_data),
        'search_query': search_query,
        'filter_type': filter_type
    })


@login_required
@permission_required('eform.view_form', raise_exception=True)
def extension_form(request):
    """Enhanced Extension of stay application form with smart search and compact design"""
    # Check if this is for a specific worker (from worker selection)
    worker_id = request.GET.get('worker_id')
    if worker_id:
        # Redirect directly to print form for selected worker
        return redirect('eform:print_extension_form', worker_id=worker_id)
    
    # Otherwise show enhanced worker selection with smart search
    search_query = request.GET.get('search', '')
    position_filter = request.GET.get('position', '')
    building_filter = request.GET.get('building', '')
    nationality_filter = request.GET.get('nationality', '')
    zone_filter = request.GET.get('zone', '')
    
    # For extensions, only show workers who have passed probation or have extended status
    # These are workers who have successfully completed their probation period
    eligible_statuses = ['passed', 'extended']  # 'extended' = contract extended after passing probation
    status_filter = 'passed'  # Set for template compatibility, but we're filtering by eligible_statuses
    
    workers = Worker.objects.filter(
        status__in=eligible_statuses
    ).select_related(
        'zone', 'building', 'position'
    ).order_by('first_name', 'last_name')
    
    # Enhanced smart search with relevance scoring (excluding encrypted fields from direct search)
    if search_query:
        workers = workers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(worker_id__icontains=search_query) |
            Q(position__name__icontains=search_query) |
            Q(building__name__icontains=search_query) |
            Q(zone__name__icontains=search_query) |
            Q(nationality__icontains=search_query) |
            Q(documents__document_number__icontains=search_query)
        ).distinct()
    
    # Advanced filters
    if position_filter:
        workers = workers.filter(position_id=position_filter)
    
    if building_filter:
        workers = workers.filter(building_id=building_filter)
    
    if nationality_filter:
        workers = workers.filter(nationality=nationality_filter)
        
    if zone_filter:
        workers = workers.filter(zone_id=zone_filter)
    
    # Get filter options for dropdowns
    from zone.models import Position, Building, Zone
    positions = Position.objects.all().order_by('name')
    buildings = Building.objects.all().order_by('name')
    zones = Zone.objects.all().order_by('name')
    nationalities = Worker.objects.values_list('nationality', flat=True).distinct().order_by('nationality')
    nationality_choices = [choice for choice in Worker.NATIONALITY_CHOICES if choice[0] in nationalities]
    
    # Enhanced pagination with better performance
    paginator = Paginator(workers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add smart search suggestions for AJAX
    suggestions = []
    if search_query and len(search_query) >= 2:
        # Get top matching workers for suggestions
        suggestion_workers = workers[:10]
        for worker in suggestion_workers:
            suggestions.append({
                'text': f"{worker.get_full_name()}",
                'type': 'Worker',
                'details': f"{worker.position.name if worker.position else 'No Position'} - {worker.building.name if worker.building else 'No Building'}",
                'worker_id': worker.id
            })
    
    # Calculate extension statistics
    today = timezone.now().date()
    
    # Workers with permits expiring soon (through Document model)
    expiring_soon = Worker.objects.filter(
        documents__document_type='work_permit',
        documents__expiry_date__isnull=False,
        documents__expiry_date__lte=today + timedelta(days=30),
        documents__expiry_date__gte=today,
        status='active'
    ).distinct().count()
    
    # Workers with expired permits (through Document model)
    expired_permits = Worker.objects.filter(
        documents__document_type='work_permit',
        documents__expiry_date__isnull=False,
        documents__expiry_date__lt=today,
        status='active'
    ).distinct().count()
    

    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'position_filter': position_filter,
        'building_filter': building_filter,
        'nationality_filter': nationality_filter,
        'zone_filter': zone_filter,
        'status_filter': status_filter,
        'positions': positions,
        'buildings': buildings,
        'zones': zones,
        'nationality_choices': nationality_choices,
        'form_type': 'extension',
        'allow_multiple': False,  # Extension forms are for single workers
        'total_workers': workers.count(),
        'suggestions': suggestions,
        'expiring_soon': expiring_soon,
        'expired_permits': expired_permits,
        'active_workers': Worker.objects.filter(status='active').count(),
        'total_applications': Worker.objects.filter(status='active').count(),  # This would be actual extension applications in a real system
        'today': today,
        'expiry_warning_date': today + timedelta(days=30),
    }
    return render(request, 'eform/worker_selection.html', context)


@login_required
@permission_required('eform.view_form', raise_exception=True)
def certificate_form(request):
    """Building selection step for certificate requests"""
    # Check if building is already selected
    building_id = request.GET.get('building')
    if building_id:
        # Redirect to worker selection for the selected building
        return redirect(f"{reverse('eform:certificate_form_workers')}?building={building_id}")
    
    # Show building selection page
    from zone.models import Building
    buildings = Building.objects.annotate(
        worker_count=models.Count('workers', filter=models.Q(workers__status__in=['active', 'passed']))
    ).filter(worker_count__gt=0).order_by('name')
    
    context = {
        'buildings': buildings,
        'page_title': 'Select Building for Certificate Request',
        'page_subtitle': 'Choose a building to request certificates for workers'
    }
    return render(request, 'eform/certificate_building_selection.html', context)


@login_required
def certificate_form_workers(request):
    """Enhanced Employment Certificate form with smart search - workers from selected building"""
    # Get building ID from URL parameters
    building_id = request.GET.get('building')
    if not building_id:
        messages.error(request, 'Please select a building first.')
        return redirect('eform:certificate_form')
    
    try:
        from zone.models import Building
        building = Building.objects.get(id=building_id)
    except Building.DoesNotExist:
        messages.error(request, 'Selected building not found.')
        return redirect('eform:certificate_form')
    
    # Check if this is a POST request with selected workers
    if request.method == 'POST':
        selected_workers = request.POST.getlist('selected_workers')
        if selected_workers:
            # Redirect to certificate request form with selected workers
            worker_ids = ','.join(selected_workers)
            return redirect(f"{reverse('eform:certificate_request_form')}?workers={worker_ids}")
        else:
            messages.error(request, 'Please select at least one worker.')
    
    # Check if this is for a specific worker (from worker selection)
    worker_id = request.GET.get('worker_id')
    if worker_id:
        # Redirect directly to certificate request form for single worker
        return redirect(f"{reverse('eform:certificate_request_form')}?workers={worker_id}")
    
    # Otherwise show enhanced worker selection with smart search - filtered by building
    search_query = request.GET.get('search', '')
    position_filter = request.GET.get('position', '')
    nationality_filter = request.GET.get('nationality', '')
    zone_filter = request.GET.get('zone', '')
    status_filter = request.GET.get('status', 'active,passed')
    
    # Filter workers by building and status
    if status_filter == 'active,passed':
        workers = Worker.objects.filter(
            building=building,
            status__in=['active', 'passed']
        ).select_related(
            'zone', 'building', 'position'
        ).order_by('first_name', 'last_name')
    elif ',' in status_filter:
        status_list = status_filter.split(',')
        workers = Worker.objects.filter(
            building=building,
            status__in=status_list
        ).select_related(
            'zone', 'building', 'position'
        ).order_by('first_name', 'last_name')
    else:
        workers = Worker.objects.filter(
            building=building,
            status=status_filter
        ).select_related(
            'zone', 'building', 'position'
        ).order_by('first_name', 'last_name')
    
    # Enhanced smart search with document fields (excluding encrypted fields from direct search)
    if search_query:
        workers = workers.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(worker_id__icontains=search_query) |
            Q(position__name__icontains=search_query) |
            Q(zone__name__icontains=search_query) |
            Q(nationality__icontains=search_query) |
            Q(documents__document_number__icontains=search_query)
        ).distinct()
    
    # Advanced filters
    if position_filter:
        workers = workers.filter(position_id=position_filter)
    
    if nationality_filter:
        workers = workers.filter(nationality=nationality_filter)
        
    if zone_filter:
        workers = workers.filter(zone_id=zone_filter)
    
    # Get filter options for dropdowns (filtered by building)
    from zone.models import Position, Zone
    positions = Position.objects.filter(
        workers__building=building,
        workers__status__in=['active', 'passed']
    ).distinct().order_by('name')
    
    zones = Zone.objects.filter(
        workers__building=building,
        workers__status__in=['active', 'passed']
    ).distinct().order_by('name')
    
    nationalities = workers.values_list('nationality', flat=True).distinct().order_by('nationality')
    nationality_choices = [choice for choice in Worker.NATIONALITY_CHOICES if choice[0] in nationalities]
    
    # Enhanced pagination
    paginator = Paginator(workers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Add smart search suggestions for AJAX
    suggestions = []
    if search_query and len(search_query) >= 2:
        suggestion_workers = workers[:10]
        for worker in suggestion_workers:
            suggestions.append({
                'text': f"{worker.get_full_name()}",
                'type': 'Worker',
                'details': f"{worker.position.name if worker.position else 'No Position'} - {worker.building.name if worker.building else 'No Building'}",
                'worker_id': worker.id
            })
    
    # Calculate certificate statistics for this building
    building_workers_count = workers.count()
    active_workers_count = Worker.objects.filter(building=building, status='active').count()
    
    # Workers by position for quick stats (within building)
    top_positions = Worker.objects.filter(
        building=building, 
        status='active'
    ).values(
        'position__name'
    ).annotate(
        count=models.Count('id')
    ).order_by('-count')[:4]
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'position_filter': position_filter,
        'nationality_filter': nationality_filter,
        'zone_filter': zone_filter,
        'status_filter': status_filter,
        'positions': positions,
        'zones': zones,
        'nationality_choices': nationality_choices,
        'building': building,
        'building_id': building_id,
        'form_type': 'certificate',
        'allow_multiple': True,
        'total_workers': building_workers_count,
        'suggestions': suggestions,
        'active_workers_count': active_workers_count,
        'top_positions': top_positions,
    }
    return render(request, 'eform/certificate_smart_search.html', context)


@login_required
@permission_required('eform.add_form', raise_exception=True)
def certificate_request_form(request):
    """Certificate request form for selected workers"""
    from datetime import datetime, timedelta
    
    # Get selected worker IDs from URL parameters
    worker_ids = request.GET.get('workers', '').split(',')
    worker_ids = [id.strip() for id in worker_ids if id.strip()]
    
    if not worker_ids:
        messages.error(request, 'No workers selected.')
        return redirect('eform:certificate_form')
    
    # Get selected workers
    workers = Worker.objects.filter(id__in=worker_ids).select_related('position', 'building', 'zone')
    
    if not workers.exists():
        messages.error(request, 'Selected workers not found.')
        return redirect('eform:certificate_form')
    
    # Handle form submission
    if request.method == 'POST':
        # Calculate expected completion date based on urgency
        urgency = request.POST.get('urgency', 'normal')
        today = timezone.now().date()
        
        if urgency == 'emergency':
            expected_completion = today
        elif urgency == 'urgent':
            expected_completion = today + timedelta(days=2)
        else:
            expected_completion = today + timedelta(days=7)
        
        # Create a single certificate request for all selected workers (batch request)
        certificate_request = CertificateRequest.objects.create(
            created_by=request.user,
            certificate_type=request.POST.get('certificate_type', ''),
            purpose=request.POST.get('purpose', ''),
            urgency=urgency,
            specific_details=request.POST.get('specific_details', ''),
            include_salary=request.POST.get('include_salary') == 'on',
            include_start_date=request.POST.get('include_start_date') == 'on',
            include_position=request.POST.get('include_position') == 'on',
            include_department=request.POST.get('include_department') == 'on',
            custom_text=request.POST.get('custom_text', ''),
            delivery_method=request.POST.get('delivery_method', 'pickup'),
            delivery_address=request.POST.get('delivery_address', ''),
            delivery_contact=request.POST.get('delivery_contact', ''),
            expected_completion=expected_completion,
            status='submitted',
            is_batch_request=len(workers) > 1,
            request_ref=request.POST.get('request_ref')
        )
        
        # Add all workers to the certificate request
        certificate_request.workers.set(workers)
        
        # Show success message
        if len(workers) == 1:
            messages.success(request, f'Certificate request #{certificate_request.request_number} saved successfully!')
        else:
            messages.success(request, f'Batch certificate request #{certificate_request.request_number} saved successfully for {len(workers)} workers!')
        
        # Redirect to certificate requests list
        return redirect('eform:certificate_requests_list')
    
    # Pre-populate form with default data
    form_data = {
        'certificate_type': 'employment',  # Default type
        'purpose': 'personal_use',
        'urgency': 'normal',
        'include_salary': False,
        'include_start_date': True,
        'include_position': True,
        'include_department': True,
        'delivery_method': 'pickup',
        'specific_details': f"Employment certificate request for {len(workers)} worker{'s' if len(workers) > 1 else ''}",
    }
    
    context = {
        'workers': workers,
        'worker_count': len(workers),
        'form_date': timezone.now().date(),
        'form_data': form_data,
        'certificate_types': CertificateRequest.CERTIFICATE_TYPE_CHOICES,
        'purposes': CertificateRequest.PURPOSE_CHOICES,
        'urgency_choices': CertificateRequest.URGENCY_CHOICES,
    }
    return render(request, 'eform/certificate_request_form.html', context)


@login_required
def print_extension_form(request, worker_id):
    """Print extension of stay application form for selected worker"""

    doc_types=['passport,visa','work_permit']
    worker = get_object_or_404(Worker, id=worker_id)
    documents = Document.objects.filter(worker__id=worker_id)
    
    # Get the most recent extension request for this worker
    try:
        extension = ExtensionRequest.objects.filter(worker_id=worker_id).latest('created_at')
    except ExtensionRequest.DoesNotExist:
        # If no extension request exists, create a default one for printing
        extension = ExtensionRequest(
            worker=worker,
            extension_duration=365,  # Default 1 year
            extension_type='work',
            status='draft'
        )
    
    request_month = int(extension.extension_duration / 30) if extension.extension_duration else 12
    context = {
        'worker': worker,
        'extension': extension,
        'request_month': request_month,
        'form_date': timezone.now().date(),
        'documents':documents
    }
    return render(request, 'eform/print_extension_form.html', context)


@login_required
@permission_required('eform.change_form', raise_exception=True)
def extension_edit_form(request, worker_id=None, request_id=None):
    """Edit extension of stay application form before printing"""
    from .models import ExtensionRequest
    from datetime import datetime, timedelta
    import random
    
    worker = None
    existing_request = None
    
    # Determine if we're editing an existing request or creating new one
    if request_id:
        existing_request = get_object_or_404(ExtensionRequest, id=request_id)
        worker = existing_request.worker
    elif worker_id:
        worker = get_object_or_404(Worker, id=worker_id)
        # Check if there's an existing extension request for this worker
        existing_request = ExtensionRequest.objects.filter(worker=worker).first()
    else:
        messages.error(request, 'Worker ID or request ID is required.')
        return redirect('eform:unified_dashboard')
    
    # Generate realistic mock data for form pre-population (moved here to be available for POST handling)
    today = timezone.now().date()
    
    # Mock passport numbers (format: A1234567)
    mock_passport = f"A{random.randint(1000000, 9999999)}"
    
    # Mock visa expiry (current visa expires in 2-6 months)
    mock_visa_expiry = today + timedelta(days=random.randint(60, 180))
    
    # Mock entry date (6 months to 2 years ago)
    mock_entry_date = today - timedelta(days=random.randint(180, 730))
    
    # Mock extension start date (current visa expiry or a few days before)
    mock_start_date = mock_visa_expiry - timedelta(days=random.randint(0, 10))
    
    # Handle form submission
    if request.method == 'POST':
        # Get selected service
        from billing.models import Service
        service_id = request.POST.get('service')
        
        # Handle case where no service is selected or service doesn't exist
        service = None
        if service_id:
            try:
                service = Service.objects.get(id=service_id)
            except Service.DoesNotExist:
                messages.error(request, f'Selected service (ID: {service_id}) not found. Please select a valid service.')
                # Continue to show the form again
        
        if service and existing_request:
            # Update existing extension request
            existing_request.service = service
            existing_request.passport_number = request.POST.get('passport_number', '')
            passport_expiry_date = request.POST.get('passport_expiry_date')
            passport_issued_date = request.POST.get('passport_issued_date')
            existing_request.passport_expiry_date = passport_expiry_date if passport_expiry_date else None
            existing_request.passport_issued_date = passport_issued_date if passport_issued_date else None
            existing_request.current_visa_type = request.POST.get('current_visa_type', '')
            existing_request.current_visa_number = request.POST.get('current_visa_number', '')
            # Handle date fields properly - use defaults for required fields
            current_visa_expiry = request.POST.get('current_visa_expiry')
            existing_request.current_visa_expiry = current_visa_expiry if current_visa_expiry else mock_visa_expiry
            entry_date = request.POST.get('entry_date')
            existing_request.entry_date = entry_date if entry_date else mock_entry_date
            # Work permit fields
            existing_request.work_permit_number = request.POST.get('work_permit_number', '')
            work_permit_expiry = request.POST.get('work_permit_expiry')
            existing_request.work_permit_expiry = work_permit_expiry if work_permit_expiry else None
            # Address and Organization information
            existing_request.address_name = request.POST.get('address_name')
            existing_request.house_no = request.POST.get('house_no', '')
            existing_request.street_no = request.POST.get('street_no', '')
            existing_request.commune = request.POST.get('commune', '')
            existing_request.district = request.POST.get('district', '')
            existing_request.organization_name = request.POST.get('organization_name', 'KOH KONG RESORT')
            existing_request.position = request.POST.get('position', '')
            existing_request.extension_type = request.POST.get('extension_type', '')
            existing_request.extension_duration = int(request.POST.get('extension_duration', 0))
            existing_request.extension_reason = request.POST.get('extension_reason', '')
            extension_start_date = request.POST.get('extension_start_date')
            existing_request.extension_start_date = extension_start_date if extension_start_date else None
            existing_request.additional_details = request.POST.get('additional_details', '')
            existing_request.status = request.POST.get('status', 'requested')
            existing_request.save()
            
            messages.success(request, f'Extension request #{existing_request.request_number} updated successfully!')
            extension_request = existing_request
        elif service:
            # Create new extension request record
            # Handle date fields properly - convert empty strings to None
            passport_expiry_date = request.POST.get('passport_expiry_date')
            passport_issued_date = request.POST.get('passport_issued_date')
            current_visa_expiry = request.POST.get('current_visa_expiry')
            entry_date = request.POST.get('entry_date')
            work_permit_expiry = request.POST.get('work_permit_expiry')
            extension_start_date = request.POST.get('extension_start_date')

            # mask address 
            adrress = request.POST.get('address_name', '')
            house_no = request.POST.get('house_no', '')
            street_no = request.POST.get('street_no', '')
            commune = request.POST.get('commune', '')
            district = request.POST.get('district', '')

            adrress_name = adrress+":address:"+house_no+","+street_no+","+commune+","+district
            
            extension_request = ExtensionRequest.objects.create(
                created_by=request.user,
                worker=worker,
                service=service,
                passport_number=request.POST.get('passport_number', ''),
                passport_expiry_date=passport_expiry_date if passport_expiry_date else None,
                passport_issued_date=passport_issued_date if passport_issued_date else None,
                current_visa_type=request.POST.get('current_visa_type', ''),
                current_visa_number=request.POST.get('current_visa_number', ''),
                current_visa_expiry=current_visa_expiry if current_visa_expiry else mock_visa_expiry,
                entry_date=entry_date if entry_date else mock_entry_date,
                work_permit_number=request.POST.get('work_permit_number', ''),
                work_permit_expiry=work_permit_expiry if work_permit_expiry else None,
                address_name=request.POST.get('address_name'),
                house_no=request.POST.get('house_no', ''),
                street_no=request.POST.get('street_no', ''),
                commune=request.POST.get('commune', ''),
                district=request.POST.get('district', ''),
                organization_name=request.POST.get('organization_name', 'KOH KONG RESORT'),
                position=request.POST.get('position', worker.position.name if worker and worker.position else ''),
                extension_type=request.POST.get('extension_type', ''),
                extension_duration=int(request.POST.get('extension_duration', 0)),
                extension_reason=request.POST.get('extension_reason', ''),
                extension_start_date=extension_start_date if extension_start_date else None,
                additional_details=request.POST.get('additional_details', ''),
                status=request.POST.get('status', 'requested')
            )
            
            messages.success(request, f'Extension request #{extension_request.request_number} created successfully!')
        else:
            # No service selected
            if not service_id:
                messages.error(request, 'Please select a service before saving the extension request.')
            # Don't process the form, just redisplay it
            extension_request = existing_request
        
        # Handle different button actions only if we have a valid service
        if service:
            action = request.POST.get('action', 'save')
            
            if action == 'preview':
                # Redirect to print form for preview
                return redirect('eform:print_extension_form', worker_id=worker.id)
            else:
                # Stay on the form for continued editing
                if request_id:
                    return redirect('eform:extension_edit_form_request', request_id=request_id)
                else:
                    return redirect('eform:extension_edit_form', worker_id=worker.id)
    
    # Get available extension services from billing (duration-based services)
    from billing.models import Service
    extension_services = Service.objects.filter(
        Q(name__icontains='month') | Q(name__icontains='year') | Q(name__icontains='extension')
    ).order_by('name')
    
    # Get default service (first extension service if available)
    default_service = extension_services.first() if extension_services.exists() else Service.objects.first()
    
    doc_work_permit = None
    
    if worker:
        doc_work_permit = Document.objects.filter(worker = worker, document_type='work_permit').first()
    # Pre-populate form with existing request data or defaults
    if existing_request:
        # Use existing request data
        form_data = {
            'service': existing_request.service.id if existing_request.service else (default_service.id if default_service else None),
            'passport_number': existing_request.passport_number,
            'passport_expiry_date': existing_request.passport_expiry_date,
            'passport_issued_date':existing_request.passport_issued_date,
            'current_visa_type': existing_request.current_visa_type,
            'current_visa_number': existing_request.current_visa_number,
            'current_visa_expiry': existing_request.current_visa_expiry,
            'entry_date': existing_request.entry_date,
            'work_permit_number': existing_request.work_permit_number if existing_request.work_permit_number else (doc_work_permit.document_number if doc_work_permit else ''),
            'work_permit_expiry': existing_request.work_permit_expiry,
            'address_name': existing_request.address_name,
            'house_no': existing_request.house_no if hasattr(existing_request, 'house_no') else '',
            'street_no': existing_request.street_no if hasattr(existing_request, 'street_no') else '',
            'commune': existing_request.commune if hasattr(existing_request, 'commune') else '',
            'district': existing_request.district if hasattr(existing_request, 'district') else '',
            'organization_name': existing_request.organization_name if hasattr(existing_request, 'organization_name') else 'KOH KONG RESORT',
            'position': existing_request.position if hasattr(existing_request, 'position') else (worker.position.name if worker and worker.position else ''),
            'extension_type': existing_request.extension_type,
            'extension_duration': existing_request.extension_duration,
            'extension_reason': existing_request.extension_reason,
            'extension_start_date': existing_request.extension_start_date,
            'additional_details': existing_request.additional_details,
            'status': existing_request.status,
        }
    else:
        # Use mock data for new requests
        # Get documents safely
        passport_doc = worker.documents.filter(document_type='passport').first() if worker else None
        visa_doc = worker.documents.filter(document_type='visa').first() if worker else None
        
        form_data = {
            'service': default_service.id if default_service else extension_services.first().id if extension_services.exists() else None,
            'passport_number': passport_doc.document_number if passport_doc else mock_passport,
            'passport_expiry_date': passport_doc.expiry_date if passport_doc and passport_doc.expiry_date else today,
            'passport_issued_date': passport_doc.issue_date if passport_doc and passport_doc.issue_date else today,   # Will be filled by user
            'current_visa_expiry': visa_doc.expiry_date if visa_doc and visa_doc.expiry_date else mock_visa_expiry,
            'current_visa_number': visa_doc.document_number if visa_doc else None,  # Will be filled by user
            'entry_date': visa_doc.issue_date if visa_doc and visa_doc.issue_date else today,
            'work_permit_number': doc_work_permit.document_number if doc_work_permit else '',  # Will be filled by user
            'work_permit_expiry': worker.work_permit_expiry if worker else None,
            'address_name': '',  # Will be filled by user
            'house_no': '',  # Will be filled by user
            'street_no': '',  # Will be filled by user
            'commune': '',  # Will be filled by user
            'district': '',  # Will be filled by user
            'organization_name': 'KOH KONG RESORT',  # Default organization
            'position': worker.position.name if worker and worker.position else '',  # Default from worker's position
            'extension_type': 'work',  # Default to work extension
            'extension_duration': 365,  # Default to 1 year
            'extension_reason': 'employment',
            'extension_start_date': mock_start_date,
            'additional_details': f"Extension request for {worker.get_full_name() if worker else 'Worker'} working as {worker.position.name if worker and worker.position else 'Staff'} at {worker.building.name if worker and worker.building else 'company premises'}.",
            'status': 'requested',  # Default status for new requests
        }

    

    context = {
        'worker': worker,
        'form_date': timezone.now().date(),
        'form_data': form_data,
        'visa_services': extension_services,
        'status_choices': ExtensionRequest.STATUS_CHOICES,
        'existing_request': existing_request,
        'request_id': request_id,
    
    }
    return render(request, 'eform/extension_edit_form.html', context)



@login_required
@permission_required('eform.view_form', raise_exception=True)
def extension_requests_list(request):
    """Display list of saved extension requests"""
    from .models import ExtensionRequest
    
    # Filter and search
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    requests = ExtensionRequest.objects.select_related('worker', 'worker__zone', 'created_by').order_by('-created_at')
    
    if search_query:
        requests = requests.filter(
            Q(request_number__icontains=search_query) |
            Q(worker__first_name__icontains=search_query) |
            Q(worker__last_name__icontains=search_query) |
            Q(passport_number__icontains=search_query) |
            Q(worker__zone__name__icontains=search_query)
        )
    
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    # Pagination
    paginator = Paginator(requests, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistics with status breakdown
    stats = {
        'total_requests': ExtensionRequest.objects.count(),
        'requested_requests': ExtensionRequest.objects.filter(status='requested').count(),
        'processing_requests': ExtensionRequest.objects.filter(status='processing').count(),
        'completed_requests': ExtensionRequest.objects.filter(status='completed').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': ExtensionRequest.STATUS_CHOICES,
        'stats': stats,
    }
    return render(request, 'eform/extension_requests_list.html', context)


@login_required
def extension_request_delete(request, request_id):
    """Delete an extension request"""
    from .models import ExtensionRequest
    from audit_management.models import AuditTrail
    
    # Check if user is manager or admin
    from user_management.models import UserRoleAssignment
    
    is_authorized = False
    
    # Check if superuser
    if request.user.is_superuser:
        is_authorized = True
    else:
        # Check for manager or admin role
        try:
            role_assignment = UserRoleAssignment.objects.select_related('role').filter(
                user=request.user,
                is_active=True
            ).first()
            
            if role_assignment and role_assignment.role:
                user_role = role_assignment.role.name.lower()
                if user_role in ['manager', 'admin']:
                    is_authorized = True
        except:
            pass
    
    if not is_authorized:
        messages.error(request, 'Only managers and administrators can delete extension requests.')
        return redirect('eform:extension_requests_list')
    
    extension_request = get_object_or_404(ExtensionRequest, id=request_id)
    
    if request.method == 'POST':
        # Store info for logging and messages
        worker_name = extension_request.worker.get_full_name()
        request_number = extension_request.request_number
        worker_id = extension_request.worker.worker_id
        
        try:
            # Log the deletion in audit trail before deleting
            try:
                AuditTrail.objects.create(
                    user=request.user,
                    action='delete',
                    resource_type='extension_request',
                    resource_id=str(request_id),
                    changes={
                        'request_number': request_number,
                        'worker': f'{worker_name} ({worker_id})',
                        'deleted_by': request.user.get_full_name() or request.user.username,
                        'status': extension_request.status,
                        'extension_type': extension_request.get_extension_type_display(),
                    },
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception as log_error:
                # Continue with deletion even if logging fails
                pass

            # Delete the extension request
            deleted_info = extension_request.delete()
            
            # Success message
            messages.success(
                request, 
                f'Extension request {request_number} for {worker_name} has been deleted successfully.'
            )
            
            
            return redirect('eform:extension_requests_list')
            
        except Exception as e:

            
            pass
            import traceback
            
            # User-friendly error messages
            if 'foreign key constraint' in str(e).lower():
                messages.error(
                    request, 
                    f'Cannot delete extension request {request_number}: It has related records that must be removed first.'
                )
            elif 'does not exist' in str(e).lower():
                messages.error(
                    request, 
                    f'Extension request {request_number} no longer exists.'
                )
            else:
                messages.error(
                    request, 
                    f'Error deleting extension request {request_number}: {str(e)}'
                )
            
            return redirect('eform:extension_requests_list')
    
    # If not POST, redirect back to list
    return redirect('eform:extension_requests_list')


@login_required
@permission_required('eform.view_form', raise_exception=True)
def extension_request_detail(request, request_id):
    """Display detailed view of an extension request"""
    extension_request = get_object_or_404(
        ExtensionRequest.objects.select_related('worker', 'created_by'),
        id=request_id
    )
    
    # Get audit logs for this extension request
    from audit_management.models import AuditTrail
    from auditlog.models import LogEntry
    from django.contrib.contenttypes.models import ContentType
    
    # Initialize empty lists for audit logs
    audit_logs = []
    change_logs = []
    
    try:
        # Get AuditTrail logs
        audit_logs = list(AuditTrail.objects.filter(
            resource_type='extension_request',
            resource_id=str(request_id)
        ).order_by('-timestamp')[:20])
    except Exception as e:
    
        pass
    try:
        # Get django-auditlog LogEntry logs
        extension_content_type = ContentType.objects.get_for_model(ExtensionRequest)
        change_logs = list(LogEntry.objects.filter(
            content_type=extension_content_type,
            object_pk=str(request_id)
        ).order_by('-timestamp')[:20])
    except Exception as e:
    
        pass
    # Combine all logs and sort by timestamp/date
    all_logs = []
    
    # Add AuditTrail logs with type marker
    for log in audit_logs:
        log.log_type = 'audit_trail'
        log.sort_timestamp = log.timestamp
        all_logs.append(log)
    
    # Add LogEntry logs with type marker  
    for log in change_logs:
        log.log_type = 'change_log'
        log.sort_timestamp = log.timestamp
        
        # Filter out unchanged fields from changes_display_dict
        if hasattr(log, 'changes_display_dict') and log.changes_display_dict:
            filtered_changes = {}
            for field, values in log.changes_display_dict.items():
                # Only include if values actually changed
                if len(values) == 2 and values[0] != values[1]:
                    filtered_changes[field] = values
                elif len(values) == 1:  # New field being set
                    filtered_changes[field] = values
            log.filtered_changes = filtered_changes
        
        all_logs.append(log)
    
    # Sort all logs by timestamp (newest first) and limit to 15
    all_logs.sort(key=lambda x: x.sort_timestamp, reverse=True)
    all_logs = all_logs[:15]
    
    context = {
        'extension_request': extension_request,
        'worker': extension_request.worker,
        'all_logs': all_logs,
        'has_audit_logs': len(all_logs) > 0,
    }
    return render(request, 'eform/extension_request_detail.html', context)


@login_required
def print_certificate_form(request):
    """Print certificate form for selected workers"""
    worker_ids = request.GET.get('workers', '').split(',')
    worker_ids = [id.strip() for id in worker_ids if id.strip()]
    request_id = request.GET.get('request_id', '')

    certificate_request = CertificateRequest.objects.select_related(
            'created_by', 'reviewed_by'
        ).prefetch_related(
            'workers', 'workers__position', 'workers__building', 'workers__zone',
            'workers__documents'
        ).get(id=request_id)

    doc_types = ["visa","passport"]
    
    if not worker_ids:
        messages.error(request, 'No workers selected.')
        return redirect('eform:certificate_form')
    
    # Enhanced query to get workers with all related data
    workers = Worker.objects.filter(id__in=worker_ids).select_related(
        'zone', 'building', 'position'
    ).prefetch_related('documents')
 
    # Get documents with better filtering
    documents = Document.objects.filter(
        worker__id__in=worker_ids, 
        document_type__in=doc_types
    ).select_related('worker').order_by('worker', 'document_type', '-created_at')
    
    extensions = ExtensionRequest.objects.filter(worker__id__in=worker_ids).select_related('worker')
    
    # Create a dictionary for easier template access
    worker_documents = {}
    for doc in documents:
        if doc.worker.id not in worker_documents:
            worker_documents[doc.worker.id] = {}
        if doc.document_type not in worker_documents[doc.worker.id]:
            worker_documents[doc.worker.id][doc.document_type] = doc
    
    # Enhanced context with better data organization
    context = {
        'workers': workers,
        'documents': documents,
        'worker_documents': worker_documents,  # New: organized document lookup
        'extensions': extensions,
        'form_date': timezone.now().date(),
        'doc_types': doc_types,  # New: for template debugging
        'certificate_request':certificate_request
    }
    return render(request, 'eform/print_certificate_form.html', context)


    


@login_required
@permission_required('eform.change_form', raise_exception=True)
def certificate_edit_form(request, worker_id=None, request_id=None):
    """Certificate request form - create new or edit existing"""
    from billing.models import Service
    from django.shortcuts import get_object_or_404
    
    worker = None
    certificate_request = None
    
    # Determine if we're editing an existing request or creating new one
    if request_id:
        certificate_request = get_object_or_404(CertificateRequest, id=request_id)
        worker = certificate_request.workers.first()  # Get the first worker from many-to-many
    elif worker_id:
        worker = get_object_or_404(Worker, id=worker_id)
    else:
        messages.error(request, 'Worker ID or request ID is required.')
        return redirect('eform:unified_dashboard')
    
    if request.method == 'POST':
        # Debug: Log all POST data to help troubleshoot

        # Get form data
        status = request.POST.get('status', 'requested')
        certificate_type = request.POST.get('certificate_type')
        purpose = request.POST.get('purpose')
        urgency = request.POST.get('urgency', 'normal')
        specific_details = request.POST.get('specific_details', '')
        include_salary = request.POST.get('include_salary') == 'on'
        include_start_date = request.POST.get('include_start_date') == 'on'
        include_position = request.POST.get('include_position') == 'on'
        include_department = request.POST.get('include_department') == 'on'
        custom_text = request.POST.get('custom_text', '')
        delivery_method = request.POST.get('delivery_method', 'pickup')
        delivery_address = request.POST.get('delivery_address', '')
        delivery_contact = request.POST.get('delivery_contact', '')
        review_notes = request.POST.get('review_notes', '')
        request_ref = request.POST.get('request_ref')
        
        # Calculate expected completion date based on urgency
        from datetime import timedelta
        if urgency == 'emergency':
            expected_completion = timezone.now().date()  # Same day
        elif urgency == 'urgent':
            expected_completion = timezone.now().date() + timedelta(days=3)  # 2-3 days
        else:
            expected_completion = timezone.now().date() + timedelta(days=7)  # 5-7 days
        
        if certificate_request:
            # Update existing request
            certificate_request.status = status
            certificate_request.certificate_type = certificate_type
            certificate_request.purpose = purpose
            certificate_request.urgency = urgency
            certificate_request.specific_details = specific_details
            certificate_request.include_salary = include_salary
            certificate_request.include_start_date = include_start_date
            certificate_request.include_position = include_position
            certificate_request.include_department = include_department
            certificate_request.custom_text = custom_text
            certificate_request.delivery_method = delivery_method
            certificate_request.delivery_address = delivery_address
            certificate_request.delivery_contact = delivery_contact
            certificate_request.review_notes = review_notes
            certificate_request.expected_completion = expected_completion
            certificate_request.updated_at = timezone.now()
            certificate_request.request_ref = request_ref
            
            if status == 'processing' and not certificate_request.reviewed_at:
                certificate_request.reviewed_by = request.user
                certificate_request.reviewed_at = timezone.now()
            elif status == 'completed':
                certificate_request.actual_completion = timezone.now().date()
            
            certificate_request.save()
            
            messages.success(request, f'Certificate request #{certificate_request.request_number} updated successfully!')
        else:
            # Create new request
            certificate_request = CertificateRequest.objects.create(
                status=status,
                created_by=request.user,
                certificate_type=certificate_type,
                purpose=purpose,
                urgency=urgency,
                specific_details=specific_details,
                include_salary=include_salary,
                include_start_date=include_start_date,
                include_position=include_position,
                include_department=include_department,
                custom_text=custom_text,
                delivery_method=delivery_method,
                delivery_address=delivery_address,
                delivery_contact=delivery_contact,
                review_notes=review_notes,
                expected_completion=expected_completion,
                request_ref=request_ref
            )
            
            # Add the worker to the request (many-to-many relationship)
            certificate_request.workers.add(worker)
            
            messages.success(request, f'Certificate request #{certificate_request.request_number} created successfully!')

        # Process visa service charges for each worker
        all_workers = certificate_request.workers.all() if certificate_request else [worker]

        for worker_item in all_workers:
            visa_service_key = f'visa_service_charge_{worker_item.id}'
            visa_service_id = request.POST.get(visa_service_key) or None


            # Always update or create the worker service record, even if visa_service_id is None
            # This handles both setting and clearing of service selections
            worker_service, created = CertificateRequestWorkerService.objects.update_or_create(
                certificate_request=certificate_request,
                worker=worker_item,
                defaults={
                    'visa_service_charge_id': visa_service_id,
                }
            )


            # If no service is selected, we could optionally delete the record
            # but keeping it with null visa_service_charge might be better for audit purposes

        # Add summary of visa services saved
        service_count = CertificateRequestWorkerService.objects.filter(
            certificate_request=certificate_request,
            visa_service_charge__isnull=False
        ).count()

        if service_count > 0:
            messages.info(request, f'Visa service charges saved for {service_count} worker(s).')

        # Redirect to certificate requests list
        return redirect('eform:certificate_requests_list')
    
    # Pre-populate form with existing data or defaults
    if certificate_request:
        form_data = {
            'status': certificate_request.status,
            'certificate_type': certificate_request.certificate_type,
            'purpose': certificate_request.purpose,
            'urgency': certificate_request.urgency,
            'specific_details': certificate_request.specific_details,
            'include_salary': certificate_request.include_salary,
            'include_start_date': certificate_request.include_start_date,
            'include_position': certificate_request.include_position,
            'include_department': certificate_request.include_department,
            'custom_text': certificate_request.custom_text,
            'delivery_method': certificate_request.delivery_method,
            'delivery_address': certificate_request.delivery_address,
            'delivery_contact': certificate_request.delivery_contact,
            'review_notes': certificate_request.review_notes,
            'request_ref': certificate_request.request_ref
        }
    else:
        form_data = {
            'status': 'requested',
            'certificate_type': 'employment',  # Default type
            'purpose': 'personal_use',
            'urgency': 'normal',
            'include_salary': False,
            'include_start_date': True,
            'include_position': True,
            'include_department': True,
            'delivery_method': 'pickup',
            'specific_details': f"Employment certificate request for {worker.get_full_name()}",
        }
    
    # Get all workers for the request (for table display)
    workers = []
    if certificate_request:
        workers = certificate_request.workers.all()
    elif worker:
        workers = [worker]

    # Get visa services from billing system (same pattern as document tracking)
    try:
        from billing.models import Service
        visa_services = Service.objects.filter(category='visas', is_active=True).order_by('name')
    except:
        # Handle case where billing app is not available or no services exist
        visa_services = []

    # Get existing worker service selections
    worker_services = {}
    worker_service_details = {}
    if certificate_request:
        existing_services = CertificateRequestWorkerService.objects.filter(
            certificate_request=certificate_request
        ).select_related('worker', 'visa_service_charge')
        worker_services = {
            service.worker.id: service.visa_service_charge.id if service.visa_service_charge else None
            for service in existing_services
        }
        worker_service_details = {
            service.worker.id: service.visa_service_charge if service.visa_service_charge else None
            for service in existing_services
        }

    context = {
        'worker': worker,
        'workers': workers,
        'worker_services': worker_services,
        'worker_service_details': worker_service_details,
        'visa_services': visa_services,
        'certificate_request': certificate_request,
        'form_date': timezone.now().date(),
        'form_data': form_data,
        'certificate_types': CertificateRequest.CERTIFICATE_TYPE_CHOICES,
        'purposes': CertificateRequest.PURPOSE_CHOICES,
        'urgency_choices': CertificateRequest.URGENCY_CHOICES,
        'status_choices': CertificateRequest.STATUS_CHOICES,
        'delivery_methods': [
            ('pickup', 'Pickup from Office'),
            ('mail', 'Mail to Address'),
            ('email', 'Email Copy'),
            ('courier', 'Courier Service'),
        ],
        'is_edit': bool(certificate_request),
        'is_batch': len(workers) > 1 if workers else False,
    }
    return render(request, 'eform/certificate_edit_form.html', context)


@login_required
@permission_required('eform.view_form', raise_exception=True)
def certificate_requests_list(request):
    """Certificate requests list with filtering and pagination"""
    # Check user role for delete permission
    from user_management.models import UserRoleAssignment
    
    can_delete = False
    if request.user.is_superuser:
        can_delete = True
    else:
        try:
            role_assignment = UserRoleAssignment.objects.select_related('role').filter(
                user=request.user,
                is_active=True
            ).first()
            if role_assignment and role_assignment.role:
                user_role = role_assignment.role.name.lower()
                if user_role in ['manager', 'admin']:
                    can_delete = True
        except:
            pass
    
    # Get filter parameters
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset with related objects
    requests = CertificateRequest.objects.prefetch_related(
        'workers', 'workers__position', 'workers__building', 'workers__zone'
    ).order_by('-created_at')
    
    # Apply search filter
    if search_query:
        requests = requests.filter(
            Q(request_number__icontains=search_query) |
            Q(workers__first_name__icontains=search_query) |
            Q(workers__last_name__icontains=search_query) |
            Q(workers__worker_id__icontains=search_query) |
            Q(workers__documents__document_number__icontains=search_query)
        ).distinct()
    
    # Apply status filter
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    # Calculate statistics
    total_requests = requests.count()
    requested_count = requests.filter(status='requested').count()
    processing_count = requests.filter(status='processing').count()
    completed_count = requests.filter(status='completed').count()
    urgent_requests = requests.filter(urgency__in=['urgent', 'emergency']).count()
    
    # Calculate overdue requests
    today = timezone.now().date()
    overdue_requests = requests.filter(
        expected_completion__lt=today,
        status__in=['requested', 'processing']
    ).count()
    
    # Pagination
    paginator = Paginator(requests, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Status choices for filter dropdown
    status_choices = CertificateRequest.STATUS_CHOICES
    
    # Calculate stats for template
    stats = {
        'total_requests': total_requests,
        'requested_count': requested_count,
        'processing_count': processing_count,
        'completed_count': completed_count,
        'urgent_requests': urgent_requests,
        'overdue_requests': overdue_requests,
    }
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
        'stats': stats,
        'can_delete': can_delete,
    }
    return render(request, 'eform/certificate_requests_list.html', context)


@login_required
@permission_required('eform.view_form', raise_exception=True)
def certificate_request_detail(request, request_id):
    """Display certificate request details with audit log"""
    try:
        # Use select_related to optimize database queries
        certificate_request = CertificateRequest.objects.select_related(
            'created_by', 'reviewed_by'
        ).prefetch_related(
            'workers', 'workers__position', 'workers__building', 'workers__zone',
            'workers__documents'
        ).get(id=request_id)
        
        # Get audit logs
        audit_logs = []
        
        try:
            # Get AuditTrail logs
            from audit_management.models import AuditTrail
            system_logs = AuditTrail.objects.filter(
                object_id=str(certificate_request.id),
                content_type__model='certificaterequest'
            ).select_related('user').order_by('-timestamp')
            
            for log in system_logs:
                audit_logs.append({
                    'type': 'system_audit',
                    'action': log.action,
                    'timestamp': log.timestamp,
                    'user': log.user,
                    'changes': log.changes if hasattr(log, 'changes') else {},
                    'details': getattr(log, 'details', '')
                })
        except Exception as e:
        
            pass
        try:
            # Get LogEntry logs from auditlog
            from auditlog.models import LogEntry
            from django.contrib.contenttypes.models import ContentType
            
            ct = ContentType.objects.get_for_model(CertificateRequest)
            business_logs = LogEntry.objects.filter(
                content_type=ct,
                object_pk=str(certificate_request.id)
            ).order_by('-timestamp')
            
            for log in business_logs:
                # Mask sensitive information
                changes_safe = {}
                if log.changes:
                    for field, values in log.changes.items():
                        if 'passport' in field.lower():
                            # Mask passport numbers for privacy
                            if isinstance(values, list) and len(values) >= 2:
                                values = [
                                    f"***{str(values[0])[-4:]}" if values[0] else values[0],
                                    f"***{str(values[1])[-4:]}" if values[1] else values[1]
                                ]
                        changes_safe[field] = values
                
                audit_logs.append({
                    'type': 'business_audit',
                    'action': log.action,
                    'timestamp': log.timestamp,
                    'user': log.actor,
                    'changes': changes_safe,
                    'actor_model': getattr(log, 'actor_model', ''),
                })
        except Exception as e:
        
            pass
        # Sort all logs by timestamp (newest first)
        audit_logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        context = {
            'certificate_request': certificate_request,
            'audit_logs': audit_logs,
        }
        return render(request, 'eform/certificate_request_detail.html', context)
        
    except CertificateRequest.DoesNotExist:

        
        pass
        messages.error(request, 'Certificate request not found.')
        return redirect('eform:certificate_requests_list')


@login_required
@require_http_methods(["POST"])
def certificate_request_delete(request, request_id):
    """Delete a certificate request - only for managers and administrators"""
    from audit_management.models import AuditTrail
    from user_management.models import UserRoleAssignment
    
    # Check if user is manager or admin
    is_authorized = False
    
    # Check if superuser
    if request.user.is_superuser:
        is_authorized = True
    else:
        # Check for manager or admin role
        try:
            role_assignment = UserRoleAssignment.objects.select_related('role').filter(
                user=request.user,
                is_active=True
            ).first()
            
            if role_assignment and role_assignment.role:
                user_role = role_assignment.role.name.lower()
                if user_role in ['manager', 'admin']:
                    is_authorized = True
        except:
            pass
    
    if not is_authorized:
        messages.error(request, 'Only managers and administrators can delete certificate requests.')
        return redirect('eform:certificate_requests_list')
    
    certificate_request = get_object_or_404(CertificateRequest, id=request_id)
    
    # Store info for logging and messages
    request_number = certificate_request.request_number
    worker_names = ', '.join([w.get_full_name() for w in certificate_request.workers.all()])
    
    try:
        # Log the deletion in audit trail before deleting
        try:
            AuditTrail.objects.create(
                user=request.user,
                action='delete',
                resource_type='certificate_request',
                resource_id=str(request_id),
                changes={
                    'request_number': request_number,
                    'workers': worker_names,
                    'deleted_by': request.user.get_full_name() or request.user.username,
                    'status': certificate_request.status,
                    'certificate_type': certificate_request.get_certificate_type_display(),
                },
                ip_address=request.META.get('REMOTE_ADDR', ''),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception as log_error:
            # Continue with deletion even if logging fails
            pass

        # Delete the certificate request
        deleted_info = certificate_request.delete()
        
        # Success message
        messages.success(
            request, 
            f'Certificate request {request_number} has been deleted successfully.'
        )
        
        
    except Exception as e:

        
        
        pass
        import traceback
        
        # User-friendly error messages
        if 'foreign key constraint' in str(e).lower():
            messages.error(
                request, 
                f'Cannot delete certificate request {request_number}: It has related records that must be removed first.'
            )
        elif 'does not exist' in str(e).lower():
            messages.error(
                request, 
                f'Certificate request {request_number} no longer exists.'
            )
        else:
            messages.error(
                request, 
                f'Error deleting certificate request: {str(e)}'
            )
    
    return redirect('eform:certificate_requests_list')


@login_required
def worker_reports(request):
    """Worker reports dashboard with filtering options and table results"""
    from zone.models import Building
    from datetime import datetime
    import calendar
    
    buildings = Building.objects.all().order_by('name')
    current_date = datetime.now()
    
    # Initialize default context
    context = {
        'buildings': buildings,
        'current_year': current_date.year,
        'current_month': current_date.month,
        'months': [
            (1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'),
            (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'),
            (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')
        ],
        'years': range(2020, current_date.year + 2),
    }
    
    # Handle POST request - generate report and show results
    if request.method == 'POST':
        year = int(request.POST.get('year', current_date.year))
        month = int(request.POST.get('month', current_date.month))
        building_id = request.POST.get('building', '')
        
        # Filter workers by building if specified
        if building_id:
            filter_buildings = Building.objects.filter(id=building_id)
        else:
            filter_buildings = Building.objects.all()
        
        # Get worker counts for each building
        building_data = []
        total_workers = 0
        
        for building in filter_buildings.order_by('name'):
            # Count workers in this building
            worker_count = Worker.objects.filter(
                building=building,
                status='active'
            ).count()
            
            building_data.append({
                'building': building,
                'worker_count': worker_count
            })
            total_workers += worker_count
        
        month_name = calendar.month_name[month]
        
        # Add report data to context
        context.update({
            'building_data': building_data,
            'total_workers': total_workers,
            'year': year,
            'month': month,
            'month_name': month_name,
            'report_date': f"{month_name.upper()}-{year}",
            'is_filtered_building': bool(building_id),
            'filtered_building': filter_buildings.first() if building_id else None,
        })
    
    return render(request, 'eform/worker_reports.html', context)


@login_required
def generate_worker_report(request):
    """Generate worker report based on filters"""
    from zone.models import Building
    from datetime import datetime
    import calendar
    
    if request.method != 'POST':
        return redirect('eform:worker_reports')
    
    year = int(request.POST.get('year', datetime.now().year))
    month = int(request.POST.get('month', datetime.now().month))
    building_id = request.POST.get('building', '')
    
    # Filter workers by building if specified
    if building_id:
        buildings = Building.objects.filter(id=building_id)
    else:
        buildings = Building.objects.all()
    
    # Get worker counts for each building
    building_data = []
    total_workers = 0
    
    for building in buildings.order_by('name'):
        # Count workers in this building (you can add date filtering if needed)
        worker_count = Worker.objects.filter(
            building=building,
            status='active'
        ).count()
        
        building_data.append({
            'building': building,
            'worker_count': worker_count
        })
        total_workers += worker_count
    
    month_name = calendar.month_name[month]
    
    context = {
        'building_data': building_data,
        'total_workers': total_workers,
        'year': year,
        'month': month,
        'month_name': month_name,
        'report_date': f"{month_name.upper()}-{year}",
        'is_filtered_building': bool(building_id),
        'filtered_building': buildings.first() if building_id else None,
    }
    
    return render(request, 'eform/worker_report_result.html', context)


@login_required
def print_worker_report(request):
    """Print the worker report"""
    from zone.models import Building
    from datetime import datetime
    import calendar
    
    year = int(request.GET.get('year', datetime.now().year))
    month = int(request.GET.get('month', datetime.now().month))
    building_id = request.GET.get('building', '')
    
    # Filter workers by building if specified
    if building_id:
        buildings = Building.objects.filter(id=building_id)
    else:
        buildings = Building.objects.all()
    
    # Get worker counts for each building
    building_data = []
    total_workers = 0
    
    for building in buildings.order_by('name'):
        # Count workers in this building
        worker_count = Worker.objects.filter(
            building=building,
            status='active'
        ).count()
        
        building_data.append({
            'building': building,
            'worker_count': worker_count
        })
        total_workers += worker_count
    
    month_name = calendar.month_name[month]
    
    context = {
        'building_data': building_data,
        'total_workers': total_workers,
        'year': year,
        'month': month,
        'month_name': month_name,
        'report_date': f"{month_name.upper()}-{year}",
        'is_filtered_building': bool(building_id),
        'filtered_building': buildings.first() if building_id else None,
        'print_mode': True,
    }
    
    return render(request, 'eform/print_worker_report.html', context)


@login_required
def recent_requests(request):
    """Display recent extension and certificate requests"""
    from datetime import timedelta
    
    # Get recent extension requests
    recent_extensions = ExtensionRequest.objects.select_related(
        'worker', 'created_by'
    ).order_by('-created_at')[:10]
    
    # Get recent certificate requests  
    recent_certificates = CertificateRequest.objects.select_related(
        'created_by'
    ).order_by('-created_at')[:10]
    
    # Calculate some statistics
    today = timezone.now().date()
    this_week = today - timedelta(days=7)
    
    weekly_extensions = ExtensionRequest.objects.filter(
        created_at__date__gte=this_week
    ).count()
    
    weekly_certificates = CertificateRequest.objects.filter(
        created_at__date__gte=this_week
    ).count()
    
    context = {
        'title': 'Recent Requests',
        'recent_extensions': recent_extensions,
        'recent_certificates': recent_certificates,
        'weekly_extensions': weekly_extensions,
        'weekly_certificates': weekly_certificates,
    }
    return render(request, 'eform/recent_requests.html', context)


@login_required
def quick_form(request, form_slug):
    """Display and handle submission for ready-to-use forms"""
    from hr.models import Employee, Department

    # Map slugs to template names
    form_mapping = {
        'dental-claim': 'Dental Claim Form',
        'medical-claim': 'Medical Claim Form',
        'payment-request': 'Payment Request Form 001',
        'resignation': 'Resignation Form',
        'probation-evaluation': 'Probation Evaluation Form',
        'travel-request': 'Travel Request Form 001',
    }

    template_name = form_mapping.get(form_slug)
    if not template_name:
        messages.error(request, 'Form not found.')
        return redirect('eform:operations_dashboard')

    # Get or create the form template
    try:
        form_template = FormTemplate.objects.get(name=template_name)
    except FormTemplate.DoesNotExist:
        # Auto-create missing form template from predefined templates
        from eform.management.commands.add_form_templates import Command as AddFormTemplatesCommand
        command = AddFormTemplatesCommand()
        command.handle()
        # Try again after creating templates
        try:
            form_template = FormTemplate.objects.get(name=template_name)
        except FormTemplate.DoesNotExist:
            messages.error(request, 'Form template not found. Please contact administrator.')
            return redirect('eform:operations_dashboard')

    # Fetch active employees for autocomplete (per guidelines)
    employees = Employee.objects.filter(
        employment_status='active'
    ).order_by('first_name', 'last_name')

    # Fetch departments for autocomplete
    departments = Department.objects.all().order_by('name')

    # Handle form submission
    if request.method == 'POST':
        form_data = {}
        files = {}

        # Collect form data
        for field_data in form_template.template_data.get('fields', []):
            field_label = field_data['label']
            field_type = field_data['field_type']

            if field_type == 'file':
                if field_label in request.FILES:
                    uploaded_file = request.FILES[field_label]
                    # Save file
                    file_path = default_storage.save(
                        f'form_submissions/{form_slug}/{uploaded_file.name}',
                        uploaded_file
                    )
                    files[field_label] = file_path
            else:
                # Handle special autocomplete fields
                if field_label == 'Employee Name':
                    # Get employee ID from autocomplete and convert to name
                    from hr.models import Employee, Department
                    employee_id = request.POST.get('employee', '')
                    if employee_id:
                        try:
                            employee = Employee.objects.get(id=employee_id)
                            form_data[field_label] = employee.full_name
                            # Also store the employee ID in a separate field
                            form_data['Employee ID'] = employee.employee_id or ''
                        except Employee.DoesNotExist:
                            form_data[field_label] = ''
                    else:
                        form_data[field_label] = ''
                elif field_label == 'Employee ID':
                    # Skip - handled by employee name autocomplete
                    continue
                elif field_label == 'Department':
                    # Get department ID from autocomplete and convert to name
                    from hr.models import Department
                    department_id = request.POST.get('department', '')
                    if department_id:
                        try:
                            department = Department.objects.get(id=department_id)
                            form_data[field_label] = department.name
                        except Department.DoesNotExist:
                            form_data[field_label] = ''
                    else:
                        form_data[field_label] = ''
                else:
                    form_data[field_label] = request.POST.get(field_label, '')

        # Combine form data and file paths
        submission_data = {**form_data, **files}

        # Get or create a Form object for this quick form template
        form_obj, created = Form.objects.get_or_create(
            title=template_name,
            created_by=request.user,
            defaults={
                'description': f'Quick form: {template_name}',
                'status': 'published'
            }
        )

        # Create form submission
        FormSubmission.objects.create(
            form=form_obj,
            submitted_by=request.user,
            data=submission_data,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        messages.success(request, f'{template_name} submitted successfully!')
        return redirect('eform:quick_form_list', form_slug=form_slug)

    # Display the form
    context = {
        'form_template': form_template,
        'fields': form_template.template_data.get('fields', []),
        'form_slug': form_slug,
        'employees': employees,
        'departments': departments,
    }
    return render(request, 'eform/quick_form.html', context)


@login_required
def quick_form_list(request, form_slug):
    """Display list of submissions for a specific quick form"""
    # Map slugs to template names
    form_mapping = {
        'dental-claim': 'Dental Claim Form',
        'medical-claim': 'Medical Claim Form',
        'payment-request': 'Payment Request Form 001',
        'resignation': 'Resignation Form',
        'probation-evaluation': 'Probation Evaluation Form',
        'travel-request': 'Travel Request Form 001',
    }

    template_name = form_mapping.get(form_slug)
    if not template_name:
        messages.error(request, 'Form not found.')
        return redirect('eform:operations_dashboard')

    # Get the form object for this quick form
    try:
        form_obj = Form.objects.get(title=template_name, created_by=request.user)
    except Form.DoesNotExist:
        # No submissions yet, show empty state
        form_obj = None

    # Get submissions
    submissions = []
    total_submissions = 0

    if form_obj:
        search_query = request.GET.get('search', '')
        submissions_qs = FormSubmission.objects.filter(form=form_obj).order_by('-submitted_at')

        if search_query:
            submissions_qs = submissions_qs.filter(
                Q(submitted_by__username__icontains=search_query) |
                Q(submitted_by__first_name__icontains=search_query) |
                Q(submitted_by__last_name__icontains=search_query) |
                Q(data__icontains=search_query)
            )

        total_submissions = submissions_qs.count()

        # Pagination
        paginator = Paginator(submissions_qs, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        submissions = page_obj
    else:
        page_obj = None
        search_query = ''

    # Map form slug to display info
    form_info = {
        'dental-claim': {'icon': 'bi-heart-pulse', 'color': '#3b82f6', 'title': 'Dental Claims'},
        'medical-claim': {'icon': 'bi-hospital', 'color': '#ef4444', 'title': 'Medical Claims'},
        'payment-request': {'icon': 'bi-cash-coin', 'color': '#10b981', 'title': 'Payment Requests'},
        'resignation': {'icon': 'bi-box-arrow-right', 'color': '#f59e0b', 'title': 'Resignations'},
        'probation-evaluation': {'icon': 'bi-clipboard-check', 'color': '#6366f1', 'title': 'Probation Evaluations'},
        'travel-request': {'icon': 'bi-airplane', 'color': '#06b6d4', 'title': 'Travel Requests'},
    }

    info = form_info.get(form_slug, {'icon': 'bi-file-text', 'color': '#6b7280', 'title': template_name})

    context = {
        'form_slug': form_slug,
        'template_name': template_name,
        'page_obj': page_obj,
        'submissions': submissions,
        'total_submissions': total_submissions,
        'search_query': search_query,
        'form_icon': info['icon'],
        'form_color': info['color'],
        'form_title': info['title'],
    }
    return render(request, 'eform/quick_form_list.html', context)


# Employee Form Submissions Management Views

@login_required
def employee_submissions_list(request):
    """List all employee form submissions with filtering"""
    from django.db.models import Q
    from django.core.paginator import Paginator

    # Get filter parameters
    status_filter = request.GET.get('status', '')
    form_filter = request.GET.get('form', '')
    search_query = request.GET.get('search', '')

    # Base queryset
    submissions = FormSubmission.objects.select_related(
        'form', 'submitted_by', 'reviewed_by'
    ).order_by('-submitted_at')

    # Apply filters
    if status_filter:
        submissions = submissions.filter(status=status_filter)

    if form_filter:
        submissions = submissions.filter(form_id=form_filter)

    if search_query:
        submissions = submissions.filter(
            Q(submitted_by__first_name__icontains=search_query) |
            Q(submitted_by__last_name__icontains=search_query) |
            Q(form__title__icontains=search_query)
        )

    # Get stats
    total_submissions = FormSubmission.objects.count()
    pending_count = FormSubmission.objects.filter(status='pending').count()
    in_review_count = FormSubmission.objects.filter(status='in_review').count()
    approved_count = FormSubmission.objects.filter(status__in=['approved', 'completed']).count()
    rejected_count = FormSubmission.objects.filter(status='rejected').count()

    # Get all forms for filter dropdown
    forms = Form.objects.filter(status='published').order_by('title')

    # Pagination
    paginator = Paginator(submissions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'submissions': page_obj.object_list,
        'forms': forms,
        'status_filter': status_filter,
        'form_filter': form_filter,
        'search_query': search_query,
        'total_submissions': total_submissions,
        'pending_count': pending_count,
        'in_review_count': in_review_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }

    return render(request, 'eform/employee_submissions_list.html', context)


@login_required
def employee_submission_detail(request, submission_id):
    """View and manage a specific employee form submission"""
    submission = get_object_or_404(
        FormSubmission.objects.select_related('form', 'submitted_by', 'reviewed_by'),
        id=submission_id
    )

    context = {
        'submission': submission,
    }

    return render(request, 'eform/employee_submission_detail.html', context)


@login_required
def update_submission_status(request, submission_id):
    """Update the status of a form submission"""
    from django.utils import timezone
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

    submission = get_object_or_404(FormSubmission, id=submission_id)

    new_status = request.POST.get('status')
    response_message = request.POST.get('response_message', '')
    admin_notes = request.POST.get('admin_notes', '')

    if new_status not in ['pending', 'in_review', 'approved', 'completed', 'rejected']:
        return JsonResponse({'success': False, 'error': 'Invalid status'})

    # Update submission
    submission.status = new_status
    submission.response_message = response_message
    submission.admin_notes = admin_notes
    submission.reviewed_by = request.user
    submission.reviewed_at = timezone.now()
    submission.save()

    messages.success(request, f'Submission status updated to {submission.get_status_display()}')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Status updated successfully'})

    return redirect('eform:employee_submission_detail', submission_id=submission_id)


@login_required
def form_builder_new(request):
    """Simple placeholder for form builder - redirect to create form"""
    messages.info(request, 'Use the form creation interface to build custom forms')
    return redirect('eform:create_form')
