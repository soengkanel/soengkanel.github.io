from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
from django.db import connection
import json

from user_management.models import UserRoleAssignment

from .models import DocumentSubmission, DocumentUpdate, DocumentType
from zone.models import Worker, Building
from company.models import Company
from billing.models import Service


def _parse_date_field(date_string):
    """Helper function to parse date strings from form input"""
    if not date_string or not date_string.strip():
        return None
    
    date_string = date_string.strip()
    try:
        from datetime import datetime
        # Parse the date string in YYYY-MM-DD format
        return datetime.strptime(date_string, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return None


# Dashboard view removed - redirects to submission_list via URL configuration


@login_required
@permission_required('zone.view_document', raise_exception=True)
def submission_list(request):
    """List all document submissions with search and filtering"""
    submissions = DocumentSubmission.objects.prefetch_related(
        'workers'
    ).order_by('-submission_date', '-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        submissions = submissions.filter(
            Q(submission_id__icontains=search) |
            Q(reference_number__icontains=search) |
            Q(document_title__icontains=search) |
            Q(government_office__icontains=search) |
            Q(workers__first_name__icontains=search) |
            Q(workers__last_name__icontains=search)
        ).distinct()
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        submissions = submissions.filter(status=status)
    
    # Filter by document type
    doc_type = request.GET.get('document_type')
    if doc_type:
        submissions = submissions.filter(document_type=doc_type)
    
    # Filter by processing entity
    entity = request.GET.get('entity')
    if entity:
        submissions = submissions.filter(processing_entity=entity)
    
    # Filter by date range
    date_from = request.GET.get('date_from')
    if date_from:
        submissions = submissions.filter(submission_date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        submissions = submissions.filter(submission_date__lte=date_to)
    
    # Filter overdue only
    if request.GET.get('overdue') == 'true':
        today = timezone.now().date()
        submissions = submissions.filter(
            expected_completion_date__lt=today,
            status__in=['submitted', 'under_review']
        )
    
    # Calculate statistics for counter cards
    all_submissions = DocumentSubmission.objects.all()
    today = timezone.now().date()
    
    stats = {
        'total': all_submissions.count(),
        'pending': all_submissions.filter(status='pending').count(),
        'submitted': all_submissions.filter(status='submitted').count(),
        'completed': all_submissions.filter(status='completed').count(),
        'overdue': all_submissions.filter(
            expected_completion_date__lt=today,
            status__in=['submitted', 'under_review', 'pending']
        ).count(),
    }
    
    # Pagination
    paginator = Paginator(submissions, 25)
    page = request.GET.get('page')
    submissions = paginator.get_page(page)
    
    context = {
        'title': 'All Document Submissions',
        'submissions': submissions,
        'stats': stats,
        'search': search,
        'selected_status': status,
        'selected_document_type': doc_type,
        'selected_entity': entity,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': DocumentSubmission.STATUS_CHOICES,
        'document_type_choices': DocumentSubmission.DOCUMENT_TYPE_CHOICES,
        'entity_choices': DocumentSubmission.PROCESSING_ENTITY_CHOICES,
    }
    return render(request, 'document_tracking/submission_list_table.html', context)


@login_required
@permission_required('zone.view_document', raise_exception=True)
def submission_detail(request, submission_id):
    """View document submission details"""
    submission = get_object_or_404(
        DocumentSubmission.objects.prefetch_related(
            'workers__documents',
            'updates',
            'submissionworker_set__worker__documents',
            'submissionworker_set__visa_service_charge'
        ),
        id=submission_id
    )
    
    updates = submission.updates.order_by('-created_at')
    
    # Calculate dates for alerts
    today = timezone.now().date()
    expiry_warning_date = today + timedelta(days=30)
    
    # Calculate gender statistics
    worker_male_count = submission.workers.filter(sex='M').count()
    worker_female_count = submission.workers.filter(sex='F').count()
    
    # Check if VIPs exist and calculate their gender counts (Note: VIPs don't exist in current model)
    vip_male_count = 0
    vip_female_count = 0
    # vip_male_count = submission.vips.filter(sex='M').count() if hasattr(submission, 'vips') else 0
    # vip_female_count = submission.vips.filter(sex='F').count() if hasattr(submission, 'vips') else 0
    
    total_male = worker_male_count + vip_male_count
    total_female = worker_female_count + vip_female_count
    
    # Add passport numbers and visa expiry dates to workers for template display
    for submission_worker in submission.submissionworker_set.all():
        worker = submission_worker.worker
        passport_doc = worker.documents.filter(document_type='passport').first()
        worker.passport_number = passport_doc.document_number if passport_doc else ''
        
        visa_doc = worker.documents.filter(document_type='visa').first()
        worker.visa_expiry = visa_doc.expiry_date if visa_doc else ''
    
    # Add passport numbers and visa expiry dates to VIPs for template display (if VIPs exist)
    if hasattr(submission, 'vips'):
        for vip in submission.vips.all():
            passport_doc = vip.documents.filter(document_type='passport').first()
            vip.passport_number = passport_doc.document_number if passport_doc else ''
            
            visa_doc = vip.documents.filter(document_type='visa').first()
            vip.visa_expiry = visa_doc.expiry_date if visa_doc else ''
    
    # Get current tenant (company) information for letterhead
    company = None
    if connection.tenant:
        company = connection.tenant
    
    context = {
        'title': f'Document Submission {submission.submission_id or "Details"}',
        'submission': submission,
        'updates': updates,
        'today': today,
        'expiry_warning_date': expiry_warning_date,
        'worker_male_count': worker_male_count,
        'worker_female_count': worker_female_count,
        'vip_male_count': vip_male_count,
        'vip_female_count': vip_female_count,
        'total_male': total_male,
        'total_female': total_female,
        'company': company,
    }
    return render(request, 'document_tracking/submission_detail.html', context)


@login_required
@permission_required('zone.add_document', raise_exception=True)
def submission_create(request):
    """Create a new document submission"""
    if request.method == 'POST':
        try:
            # Validate required fields
            document_type = request.POST.get('document_type')
            processing_entity = request.POST.get('processing_entity')
            government_office = request.POST.get('government_office')
            
            if not document_type:
                messages.error(request, 'Document type is required.')
            elif not processing_entity:
                messages.error(request, 'Processing entity is required.')
            elif not government_office or government_office.strip() == '':
                messages.error(request, 'Government office is required.')
            else:
                # Continue with submission creation only if validation passes
                # Global service charge removed - now handled per worker
                
                # Create the submission
                submission = DocumentSubmission.objects.create(
                    document_type=document_type,
                    processing_entity=processing_entity,
                    government_office=government_office.strip(),
                    document_title=request.POST.get('document_title') or '',
                    purpose=request.POST.get('purpose') or '',
                    submission_date=_parse_date_field(request.POST.get('submission_date')),
                    expected_completion_date=_parse_date_field(request.POST.get('expected_completion_date')),
                    actual_completion_date=_parse_date_field(request.POST.get('actual_completion_date')),
                    expiry_date=_parse_date_field(request.POST.get('expiry_date')),
                    reference_number=request.POST.get('reference_number') or None,
                    notes=request.POST.get('notes') or '',
                    status=request.POST.get('status', 'submitted')
                )
                
                # Handle file uploads
                if request.FILES.get('submitted_documents'):
                    submission.submitted_documents = request.FILES['submitted_documents']
                if request.FILES.get('received_documents'):
                    submission.received_documents = request.FILES['received_documents']
                
                submission.save()
                
                # Add workers using through model with individual visa service charges
                worker_ids = request.POST.getlist('workers')
                if worker_ids:
                    from .models import SubmissionWorker


                    # Create worker relationships
                    for worker_id in worker_ids:
                        # Get individual visa service charge for this worker if document type is visa
                        visa_service_charge_id = None
                        if document_type == 'visa':
                            visa_service_charge_id = request.POST.get(f'visa_service_charge_{worker_id}') or None

                        SubmissionWorker.objects.create(
                            submission=submission,
                            worker_id=worker_id,
                            mark='New',  # Default to 'New' since we removed the field from UI
                            visa_service_charge_id=visa_service_charge_id
                        )
                
                
                # Create initial update log
                DocumentUpdate.objects.create(
                    submission=submission,
                    update_type='status_change',
                    old_value='',
                    new_value=f'Submission created with {submission.get_document_type_display()} status: {submission.get_status_display()}',
                    notes=f'Document submission created by {request.user.username}',
                    updated_by=request.user.username
                )
                
                messages.success(request, f'Document submission created successfully. ID: {submission.submission_id or "Pending"}')
                return redirect('document_tracking:submission_detail', submission_id=submission.id)
            
        except Exception as e:

            
            pass
            import traceback
            error_details = traceback.format_exc()
            messages.error(request, f'Error creating submission: {str(e)}')
            # Log the full error for debugging
    
    # Get workers and buildings for selection
    workers = Worker.objects.filter(status__in=['active', 'passed']).select_related('building').prefetch_related('documents').order_by('first_name', 'last_name')
    buildings = Building.objects.all().order_by('name')
    role = UserRoleAssignment.objects.filter(user=request.user).first()
    # Add passport numbers and visa expiry dates to workers for template display
    today = timezone.now().date()
    for worker in workers:
        passport_doc = worker.documents.filter(document_type='passport').first()
        worker.passport_number = passport_doc.document_number if passport_doc else ''
        
        visa_doc = worker.documents.filter(document_type='visa').first()
        worker.visa_number = visa_doc.document_number if visa_doc else ''
        worker.visa_expiry = visa_doc.expiry_date if visa_doc else ''
        
        # Check visa expiry status
        if visa_doc and visa_doc.expiry_date:
            days_until_expiry = (visa_doc.expiry_date - today).days
            worker.visa_expiry_warning = days_until_expiry < 0  # Expired
            worker.visa_expiry_soon = 0 <= days_until_expiry <= 30  # Expiring within 30 days
        else:
            worker.visa_expiry_warning = False
            worker.visa_expiry_soon = False
        
        work_permit_doc = worker.documents.filter(document_type='work_permit').first()
        worker.work_permit_number = work_permit_doc.document_number if work_permit_doc else ''
        # Note: worker.work_permit_expiry is a read-only property, so we use different names for warning flags
        
        # Check work permit expiry status
        if work_permit_doc and work_permit_doc.expiry_date:
            days_until_expiry = (work_permit_doc.expiry_date - today).days
            worker.wp_expiry_warning = days_until_expiry < 0  # Expired
            worker.wp_expiry_soon = 0 <= days_until_expiry <= 30  # Expiring within 30 days
        else:
            worker.wp_expiry_warning = False
            worker.wp_expiry_soon = False
        
        # Add debug info for missing documents
        if not passport_doc and not visa_doc:
            worker.missing_docs = True
    
    # Get visa services for dropdown
    from billing.models import Service
    try:
        visa_services = Service.objects.filter(category='visas', is_active=True).order_by('name')
    except Exception:
        # Handle case where billing tables don't exist yet
        visa_services = []
    
    context = {
        'title': 'Create Document Submission',
        'workers': workers,
        'buildings': buildings,
        'visa_services': visa_services,
        'document_type_choices': DocumentSubmission.DOCUMENT_TYPE_CHOICES,
        'entity_choices': DocumentSubmission.PROCESSING_ENTITY_CHOICES,
        'status_choices': DocumentSubmission.STATUS_CHOICES,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'submission': None,  # Explicitly set to None for create view
        'role':role
    }
    return render(request, 'document_tracking/submission_form.html', context)


@login_required
@permission_required('zone.change_document', raise_exception=True)
def submission_edit(request, submission_id):
    """Edit an existing document submission"""
    submission = get_object_or_404(
        DocumentSubmission.objects.prefetch_related(
            'submissionworker_set__worker__documents'
        ), 
        id=submission_id
    )
    
    if request.method == 'POST':
        try:
            # Track changes for update log
            changes = []
            old_status = submission.status
            
            # Update fields
            submission.document_type = request.POST.get('document_type')
            submission.processing_entity = request.POST.get('processing_entity')
            submission.government_office = request.POST.get('government_office')
            submission.document_title = request.POST.get('document_title')
            submission.purpose = request.POST.get('purpose')
            
            # Global service charge removed - now handled per worker
            # Handle date fields properly (convert strings to date objects or None)
            submission.submission_date = _parse_date_field(request.POST.get('submission_date'))
            submission.expected_completion_date = _parse_date_field(request.POST.get('expected_completion_date'))
            submission.actual_completion_date = _parse_date_field(request.POST.get('actual_completion_date'))
            submission.expiry_date = _parse_date_field(request.POST.get('expiry_date'))
            submission.reference_number = request.POST.get('reference_number') or None
            submission.notes = request.POST.get('notes') or ''
            new_status = request.POST.get('status')
            if new_status:  # Only update status if a value is provided
                submission.status = new_status
            
            # Handle file uploads
            if request.FILES.get('submitted_documents'):
                submission.submitted_documents = request.FILES['submitted_documents']
                changes.append('Submitted documents updated')
            if request.FILES.get('received_documents'):
                submission.received_documents = request.FILES['received_documents']
                changes.append('Received documents updated')
            
            submission.save()
            
            # Update workers using through model with individual visa service charges
            worker_ids = request.POST.getlist('workers')
            from .models import SubmissionWorker


            # Clear existing relationships
            SubmissionWorker.objects.filter(submission=submission).delete()

            # Add new relationships
            for worker_id in worker_ids:
                # Get individual visa service charge for this worker if document type is visa
                visa_service_charge_id = None
                if submission.document_type == 'visa':
                    visa_service_charge_id = request.POST.get(f'visa_service_charge_{worker_id}') or None

                SubmissionWorker.objects.create(
                    submission=submission,
                    worker_id=worker_id,
                    mark='New',  # Default to 'New' since we removed the field from UI
                    visa_service_charge_id=visa_service_charge_id
                )
            
            
            # Log status change if it occurred
            if new_status and old_status != new_status:
                DocumentUpdate.objects.create(
                    submission=submission,
                    update_type='status_change',
                    old_value=old_status,
                    new_value=new_status,
                    notes=f'Status changed from {dict(DocumentSubmission.STATUS_CHOICES).get(old_status, str(old_status))} to {submission.get_status_display()}',
                    updated_by=request.user.username
                )
            
            # Log other changes
            if changes:
                DocumentUpdate.objects.create(
                    submission=submission,
                    update_type='other',
                    new_value='; '.join(changes),
                    notes='Submission details updated',
                    updated_by=request.user.username
                )
            
            messages.success(request, 'Document submission updated successfully.')
            return redirect('document_tracking:submission_detail', submission_id=submission.id)
            
        except Exception as e:

            
            pass
            messages.error(request, f'Error updating submission: {str(e)}')
    
    role = UserRoleAssignment.objects.filter(user=request.user).first()
    # Add passport numbers and visa expiry dates to existing submission workers for template display
    for submission_worker in submission.submissionworker_set.all():
        worker = submission_worker.worker
        passport_doc = worker.documents.filter(document_type='passport').first()
        worker.passport_number = passport_doc.document_number if passport_doc else ''
        
        visa_doc = worker.documents.filter(document_type='visa').first()
        worker.visa_expiry = visa_doc.expiry_date if visa_doc else ''
        
        # Add debug info for missing documents
        if not passport_doc and not visa_doc:
            worker.missing_docs = True
    
    # Get workers and buildings for selection
    workers = Worker.objects.filter(status__in=['active', 'passed']).select_related('building').prefetch_related('documents').order_by('first_name', 'last_name')
    buildings = Building.objects.all().order_by('name')
    
    # Add passport numbers and visa expiry dates to workers for template display
    today = timezone.now().date()
    for worker in workers:
        passport_doc = worker.documents.filter(document_type='passport').first()
        worker.passport_number = passport_doc.document_number if passport_doc else ''
        
        visa_doc = worker.documents.filter(document_type='visa').first()
        worker.visa_number = visa_doc.document_number if visa_doc else ''
        worker.visa_expiry = visa_doc.expiry_date if visa_doc else ''
        
        # Check visa expiry status
        if visa_doc and visa_doc.expiry_date:
            days_until_expiry = (visa_doc.expiry_date - today).days
            worker.visa_expiry_warning = days_until_expiry < 0  # Expired
            worker.visa_expiry_soon = 0 <= days_until_expiry <= 30  # Expiring within 30 days
        else:
            worker.visa_expiry_warning = False
            worker.visa_expiry_soon = False
        
        work_permit_doc = worker.documents.filter(document_type='work_permit').first()
        worker.work_permit_number = work_permit_doc.document_number if work_permit_doc else ''
        # Note: worker.work_permit_expiry is a read-only property, so we use different names for warning flags
        
        # Check work permit expiry status
        if work_permit_doc and work_permit_doc.expiry_date:
            days_until_expiry = (work_permit_doc.expiry_date - today).days
            worker.wp_expiry_warning = days_until_expiry < 0  # Expired
            worker.wp_expiry_soon = 0 <= days_until_expiry <= 30  # Expiring within 30 days
        else:
            worker.wp_expiry_warning = False
            worker.wp_expiry_soon = False
        
        # Add debug info for missing documents
        if not passport_doc and not visa_doc:
            worker.missing_docs = True
    
    # Get visa services for dropdown
    from billing.models import Service
    try:
        visa_services = Service.objects.filter(category='visas', is_active=True).order_by('name')
    except Exception:
        # Handle case where billing tables don't exist yet
        visa_services = []
    
    context = {
        'title': f'Edit Document Submission {submission.submission_id or ""}',
        'submission': submission,
        'workers': workers,
        'buildings': buildings,
        'visa_services': visa_services,
        'document_type_choices': DocumentSubmission.DOCUMENT_TYPE_CHOICES,
        'entity_choices': DocumentSubmission.PROCESSING_ENTITY_CHOICES,
        'status_choices': DocumentSubmission.STATUS_CHOICES,
        'today': timezone.now().date().strftime('%Y-%m-%d'),
        'role':role
    }
    return render(request, 'document_tracking/submission_form.html', context)


@login_required
@permission_required('zone.delete_document', raise_exception=True)
def submission_delete(request, submission_id):
    """Delete a document submission with single-step confirmation"""
    submission = get_object_or_404(DocumentSubmission, id=submission_id)
    
    if request.method == 'POST':
        submission_info = str(submission)
        submission.delete()
        messages.success(request, f'Document submission "{submission_info}" deleted successfully.')
        return redirect('document_tracking:submission_list')
    
    # For GET requests, redirect back to detail page
    return redirect('document_tracking:submission_detail', submission_id=submission_id)





@login_required
@permission_required('zone.change_document', raise_exception=True)
def update_submission_status(request, submission_id):
    """AJAX endpoint to update submission status"""
    if request.method == 'POST':
        submission = get_object_or_404(DocumentSubmission, id=submission_id)
        old_status = submission.status
        new_status = request.POST.get('status')
        
        if new_status in dict(DocumentSubmission.STATUS_CHOICES):
            submission.status = new_status
            
            # Set completion date if marking as completed
            if new_status == 'completed' and not submission.actual_completion_date:
                submission.actual_completion_date = timezone.now().date()
            
            submission.save()
            
            # Log the change
            DocumentUpdate.objects.create(
                submission=submission,
                update_type='status_change',
                old_value=old_status,
                new_value=new_status,
                notes=f'Status updated via AJAX',
                updated_by=request.user.username
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Status updated to {submission.get_status_display()}'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid status'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def extension_stay_form(request):
    """Extension of Stay Application Interface with Smart Search"""
    context = {
        'page_title': 'Extension of Stay Application',
        'current_url_name': 'document_tracking:extension_stay_form',
    }
    return render(request, 'document_tracking/extension_stay_form.html', context)


@login_required
@permission_required('zone.view_document', raise_exception=True)
def document_submission(request):
    """Document Submission page with enhanced worker selection table"""
    from datetime import timedelta
    
    # Get workers with related data
    workers = Worker.objects.filter(
        status__in=['active', 'passed']
    ).select_related(
        'building', 
        'floor'
    ).prefetch_related(
        'documents'
    ).order_by('first_name', 'last_name')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        workers = workers.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(worker_id__icontains=search) |
            Q(documents__document_number__icontains=search)
        ).distinct()
    
    # Filter by building
    building_id = request.GET.get('building')
    if building_id:
        workers = workers.filter(building_id=building_id)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        workers = workers.filter(status=status)
    
    # Process workers to add document information
    today = timezone.now().date()
    for worker in workers:
        # Get passport document
        passport_doc = worker.documents.filter(document_type='passport').first()
        worker.passport_number = passport_doc.document_number if passport_doc else None
        
        # Get visa document and check expiry
        visa_doc = worker.documents.filter(document_type='visa').first()
        if visa_doc and visa_doc.expiry_date:
            worker.visa_expiry = visa_doc.expiry_date
            days_until_expiry = (visa_doc.expiry_date - today).days
            worker.visa_expiry_warning = days_until_expiry < 0
            worker.visa_expiry_soon = 0 <= days_until_expiry <= 30
        else:
            worker.visa_expiry = None
            worker.visa_expiry_warning = False
            worker.visa_expiry_soon = False
        
        # Get work permit document and check expiry
        work_permit_doc = worker.documents.filter(document_type='work_permit').first()
        if work_permit_doc and work_permit_doc.expiry_date:
            worker.work_permit_expiry = work_permit_doc.expiry_date
            days_until_expiry = (work_permit_doc.expiry_date - today).days
            worker.work_permit_expiry_warning = days_until_expiry < 0
            worker.work_permit_expiry_soon = 0 <= days_until_expiry <= 30
        else:
            worker.work_permit_expiry = None
            worker.work_permit_expiry_warning = False
            worker.work_permit_expiry_soon = False
    
    # Filter by expiry if requested
    expiry_filter = request.GET.get('expiry')
    if expiry_filter:
        filtered_workers = []
        for worker in workers:
            include = False
            
            if expiry_filter == 'expired':
                include = worker.visa_expiry_warning or worker.work_permit_expiry_warning
            elif expiry_filter == '30days':
                include = worker.visa_expiry_soon or worker.work_permit_expiry_soon
            elif expiry_filter == '60days':
                if worker.visa_expiry:
                    days = (worker.visa_expiry - today).days
                    include = include or (0 <= days <= 60)
                if worker.work_permit_expiry:
                    days = (worker.work_permit_expiry - today).days
                    include = include or (0 <= days <= 60)
            elif expiry_filter == '90days':
                if worker.visa_expiry:
                    days = (worker.visa_expiry - today).days
                    include = include or (0 <= days <= 90)
                if worker.work_permit_expiry:
                    days = (worker.work_permit_expiry - today).days
                    include = include or (0 <= days <= 90)
            
            if include:
                filtered_workers.append(worker)
        
        workers = filtered_workers
    
    # Pagination
    paginator = Paginator(workers, 50)  # Show 50 workers per page
    page = request.GET.get('page')
    workers = paginator.get_page(page)
    
    # Get buildings for filter dropdown
    buildings = Building.objects.all().order_by('name')
    
    context = {
        'title': 'Document Submission',
        'workers': workers,
        'buildings': buildings,
        'search': search,
        'selected_building': building_id,
        'selected_status': status,
        'selected_expiry': expiry_filter,
    }
    
    return render(request, 'document_tracking/document_submission.html', context)


@login_required
def api_get_batch_workers(request, batch_id):
    """API endpoint to get workers from a specific print batch"""
    from cards.models import PrintBatch
    
    try:
        batch = PrintBatch.objects.get(batch_id=batch_id)
        worker_ids = []
        
        # Get all worker cards from this batch
        for print_record in batch.worker_printing_records.select_related('card__worker'):
            if print_record.card and print_record.card.worker:
                worker_ids.append(print_record.card.worker.id)
        
        # Remove duplicates
        worker_ids = list(set(worker_ids))
        
        return JsonResponse({
            'success': True,
            'batch_id': batch.short_batch_id,
            'batch_name': batch.batch_name or batch.short_batch_id,
            'worker_ids': worker_ids,
            'worker_count': len(worker_ids)
        })
    except PrintBatch.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Batch not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_get_print_batches(request):
    """API endpoint to get list of print batches for ID cards"""
    from cards.models import PrintBatch
    
    # Get recent print batches
    batches = PrintBatch.objects.filter(
        batch_type__in=['worker', 'mixed']
    ).order_by('-print_date')[:20]  # Get last 20 batches
    
    batch_list = []
    for batch in batches:
        batch_list.append({
            'batch_id': str(batch.batch_id),
            'short_id': batch.short_batch_id,
            'name': batch.batch_name or batch.short_batch_id,
            'date': batch.print_date.strftime('%Y-%m-%d %H:%M'),
            'card_count': batch.card_count,
            'printed_by': batch.printed_by.username if batch.printed_by else 'Unknown'
        })
    
    return JsonResponse({
        'success': True,
        'batches': batch_list
    })


@login_required
def api_search_workers(request):
    """API endpoint to search workers for autocomplete"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'workers': []})
    
    # Search workers by name, worker_id, or passport number
    workers = Worker.objects.filter(
        status__in=['active', 'passed']
    ).filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(worker_id__icontains=query) |
        Q(documents__document_number__icontains=query)
    ).select_related('building', 'floor').prefetch_related('documents').distinct()[:10]
    
    worker_list = []
    for worker in workers:
        # Get passport document
        passport_doc = worker.documents.filter(document_type='passport').first()
        visa_doc = worker.documents.filter(document_type='visa').first()
        
        worker_name = f"{worker.first_name} {worker.last_name}"
        if worker.is_vip:
            worker_name += " [VIP]"
        
        worker_list.append({
            'id': worker.id,
            'name': worker_name,
            'worker_id': worker.worker_id or 'N/A',
            'gender': worker.sex or 'N/A',
            'dob': worker.dob.strftime('%d/%m/%Y') if worker.dob else 'N/A',
            'nationality': worker.nationality[:3].upper() if worker.nationality else 'N/A',
            'join_date': worker.date_joined.strftime('%d/%m/%Y') if worker.date_joined else 'N/A',
            'building': worker.building.name if worker.building else 'N/A',
            'passport': passport_doc.document_number if passport_doc else 'N/A',
            'visa_expiry': visa_doc.expiry_date.strftime('%d/%m/%Y') if visa_doc and visa_doc.expiry_date else 'N/A',
            'is_vip': worker.is_vip
        })
    
    return JsonResponse({'workers': worker_list})



