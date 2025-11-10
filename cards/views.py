from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Sum
from django.http import JsonResponse, HttpResponse
from django.utils.translation import gettext as _
from django.utils import timezone
from django.conf import settings
from datetime import datetime, timedelta
from decimal import Decimal
import csv
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from django.db import transaction, IntegrityError

from billing.forms import InvoiceForm, InvoiceLineItemForm, InvoiceLineItemFormSet, ServiceForm
from billing.models import Invoice
from user_management.models import UserRoleAssignment

from .models import WorkerIDCard, EmployeeIDCard, CardReplacement, CardPrintingHistory, CardCharge
from .forms import WorkerIDCardForm, CardReplacementForm, WorkerIDCardSearchForm, CardReplacementSearchForm, BatchWorkerIDCardForm, WorkerSelectionForm, PrintingPreviewForm, CardReplacementApprovalForm, CardReplacementCompletionForm
from zone.models import Worker, Zone, Building
from zone.models import WorkerProbationPeriod
from hr.models import Employee


# ============================================================================
# WORKER ID CARD VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def worker_id_card_list(request,option):
    """List worker ID cards for workers who have passed probation with search, filter, and pagination."""
    # Get all cards first, then filter by workers who have passed probation
    isVip = False

    if option =='vip':
        isVip = True
    else:
        isVip=False

    cards = WorkerIDCard.objects.filter(
        worker__is_vip=isVip
    ).select_related(
        'worker', 'worker__zone__created_by', 'worker__building', 'worker__position'
    ).prefetch_related(
        'printing_history__print_batch',
        'worker__probation_periods'
    )
    
    # Filter based on worker type: VIPs bypass probation checks
    if isVip:
        # VIP workers are always eligible for ID cards regardless of probation status
        eligible_worker_ids = [card.worker.id for card in cards]
    else:
        # Regular workers must pass probation checks
        # Workers are eligible if they either:
        # 1. Never had probation, OR
        # 2. Have completed probation (status='passed' or 'completed')
        eligible_worker_ids = []
        for card in cards:
            worker = card.worker
            current_probation = worker.current_probation_period
            if current_probation is None:
                # Worker never had probation - eligible
                eligible_worker_ids.append(worker.id)
            elif worker.status == 'passed':
                # Worker completed probation - eligible
                eligible_worker_ids.append(worker.id)
            # Workers with status 'probation', 'extended', 'failed', 'terminated' are NOT eligible
    
    cards = cards.filter(worker_id__in=eligible_worker_ids)
    
    # Initialize search form
    search_form = WorkerIDCardSearchForm(request.GET)
    
    # Apply search filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        status = search_form.cleaned_data.get('status')
        date_range = search_form.cleaned_data.get('date_range')
        building = search_form.cleaned_data.get('building')
        zone = search_form.cleaned_data.get('zone')
        batch = search_form.cleaned_data.get('batch')
        
        if search_query:
            cards = cards.filter(
                Q(worker__first_name__icontains=search_query) |
                Q(worker__last_name__icontains=search_query) |
                Q(worker__worker_id__icontains=search_query) |
                Q(card_number__icontains=search_query)
            )
        
        if status:
            cards = cards.filter(status=status)
            
        if building:
            cards = cards.filter(worker__building=building)
            
        if zone:
            cards = cards.filter(worker__zone=zone)
            
        if batch:
            cards = cards.filter(worker__probation_periods__evaluation_notes__icontains=f'Batch: {batch}').distinct()
            
        if date_range:
            today = timezone.now().date()
            if date_range == 'today':
                cards = cards.filter(request_date__date=today)
            elif date_range == 'week':
                cards = cards.filter(request_date__date__gte=today - timedelta(days=7))
            elif date_range == 'month':
                cards = cards.filter(request_date__date__gte=today - timedelta(days=30))
            elif date_range == 'year':
                cards = cards.filter(request_date__date__gte=today - timedelta(days=365))
    
    # Sorting
    sort_by = request.GET.get('sort', '-request_date')
    order = request.GET.get('order', 'desc')
    
    # Apply sort direction
    if order == 'asc':
        sort_by = sort_by.lstrip('-')
    else:
        if not sort_by.startswith('-'):
            sort_by = f'-{sort_by}'
    
    cards = cards.order_by(sort_by)
    
    # Get statistics including charge data with VIP considerations
    all_cards = WorkerIDCard.objects.select_related('worker').filter(worker__is_vip=isVip)
    eligible_card_ids = []
    for card in all_cards:
        worker = card.worker
        if isVip:
            # VIP workers are always eligible
            eligible_card_ids.append(card.id)
        else:
            # Regular workers need probation checks
            current_probation = worker.current_probation_period
            if current_probation is None or worker.status == 'passed':
                eligible_card_ids.append(card.id)
    
    eligible_cards = WorkerIDCard.objects.filter(id__in=eligible_card_ids)
    
    stats = {
        'total_cards': eligible_cards.count(),
        'active_cards': eligible_cards.filter(
            status='approved',
            expiry_date__gte=timezone.now().date()
        ).count(),
        'expired_cards': eligible_cards.filter(
            expiry_date__lt=timezone.now().date()
        ).count(),
        'pending_cards': eligible_cards.filter(status='requested').count(),
        'approved_cards': eligible_cards.filter(status='approved').count(),
        'rejected_cards': eligible_cards.filter(status='rejected').count(),
        'recent_requests': eligible_cards.filter(
            request_date__date__gte=timezone.now().date() - timedelta(days=7)
        ).count(),
        # Add charge-related statistics
        'total_charges': CardCharge.objects.count(),
        'pending_charges': CardCharge.objects.filter(status='pending').count(),
        'outstanding_amount': CardCharge.objects.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00'),
        'total_prints': CardPrintingHistory.objects.count(),
        'charged_prints': CardPrintingHistory.objects.filter(print_number__gt=1).count(),
    }
    
    # Pagination
    per_page = request.GET.get('per_page', '25')
    try:
        per_page = int(per_page)
        if per_page not in [25, 50, 100, 200]:
            per_page = 25
    except (ValueError, TypeError):
        per_page = 25
    
    paginator = Paginator(cards, per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Add charge information for each card in the current page
    for card in page_obj:
        card.total_charges = card.charges.count()
        card.outstanding_charges = card.charges.filter(status='pending').count()
        card.outstanding_amount = card.charges.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00')
        card.total_prints = card.printing_history.count()
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'stats': stats,
        'per_page': per_page,
        'current_sort': sort_by,
        'current_order': order,
        'option':option,
        'is_vip_view': isVip,
        'page_title': 'VIP Worker ID Cards' if isVip else 'Worker ID Cards'
    }
    
    return render(request, 'cards/worker_id_card_list.html', context)


@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def worker_id_card_detail(request, pk):
    """Display detailed information about a worker ID card."""
    card = get_object_or_404(WorkerIDCard, pk=pk)
    
    # Check if worker is eligible (has passed probation)
    worker = card.worker
    current_probation = worker.current_probation_period
    is_eligible = current_probation is None or worker.status == 'passed'
    
    replacements = card.replacements.all().order_by('-created_at')
    
    # Get charge and printing information
    charges = card.charges.all().order_by('-created_at')
    printing_history = card.printing_history.all().order_by('-print_date')
    
    # Calculate charge statistics
    charge_stats = {
        'total_charges': charges.count(),
        'pending_charges': charges.filter(status='pending').count(),
        'paid_charges': charges.filter(status='paid').count(),
        'waived_charges': charges.filter(status='waived').count(),
        'total_amount': charges.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'outstanding_amount': charges.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00'),
        'paid_amount': charges.filter(status='paid').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00'),
    }
    
    # Calculate printing statistics
    print_stats = {
        'total_prints': printing_history.count(),
        'free_prints': printing_history.filter(print_number=1).count(),
        'charged_prints': printing_history.filter(print_number__gt=1).count(),
        'last_print_date': printing_history.first().print_date if printing_history.exists() else None,
        'next_print_charge': card.next_print_charge,
    }
    
    context = {
        'card': card,
        'worker': worker,
        'is_eligible': is_eligible,
        'current_probation': current_probation,
        'replacements': replacements,
        'charges': charges,
        'printing_history': printing_history,
        'charge_stats': charge_stats,
        'print_stats': print_stats,
    }
    
    return render(request, 'cards/worker_id_card_detail.html', context)



@login_required
# @permission_required('cards.add_workeridcard', raise_exception=True) Previus Version
@permission_required('hr.add_idcard', raise_exception=True)
def worker_id_card_create(request, filter):
    """Create a new worker ID card."""
    is_editable = False
    worker_id = request.GET.get('worker')
    selected_worker = None
    role = None
    role = UserRoleAssignment.objects.filter(user=request.user).first()
    if worker_id:
        try:
            selected_worker = Worker.objects.get(id=worker_id)
            
            # Check if the selected worker is eligible for card creation
            # VIP workers bypass probation requirements
            if not selected_worker.is_vip:
                current_probation = selected_worker.current_probation_period
                if current_probation and selected_worker.status in ['probation', 'extended', 'failed', 'terminated']:
                    messages.error(
                        request, 
                        f'Worker {selected_worker.get_full_name()} is not eligible for ID card creation. '
                        f'Current probation status: {selected_worker.get_status_display()}. '
                        f'ID cards can only be created for workers who have completed their probation period.'
                    )
                    return redirect('cards:worker_id_card_list', 'all')
            else:
                # VIP worker - show special message
                messages.info(request, f'Creating ID card for VIP worker {selected_worker.get_full_name()} - probation checks bypassed.')
                
        except Worker.DoesNotExist:
            messages.error(request, _('Selected worker not found.'))
            return redirect('cards:worker_id_card_list', 'all')
    
    # Get count of workers on probation for context
    workers_with_active_probation = Worker.objects.filter(
        status__in=['probation', 'extended']
    ).values_list('id', flat=True)
    
    total_workers_on_probation = len(workers_with_active_probation)
    
    # Get count of workers who have ACTUALLY completed probation (status='passed')
    # Only workers who went through probation and completed it should be eligible
    workers_with_completed_probation = Worker.objects.filter(
        status='passed'
    ).values_list('id', flat=True)
    
    total_workers_completed_probation = len(workers_with_completed_probation)
    
    # Get count of workers who already have active ID cards
    workers_with_active_cards = WorkerIDCard.objects.filter(
        status__in=['pending', 'approved', 'printed', 'delivered', 'active']
    ).values_list('worker_id', flat=True)
    
    # Only count workers who completed probation AND have active cards
    workers_completed_probation_with_active_cards = Worker.objects.filter(
        id__in=workers_with_completed_probation
    ).filter(
        id__in=workers_with_active_cards
    ).count()
    
    # Calculate eligible workers (completed probation but no active cards)
    eligible_workers_count = total_workers_completed_probation - workers_completed_probation_with_active_cards
    
    if request.method == 'POST':
        form = WorkerIDCardForm(request.POST, request.FILES, card_type=filter, user=request.user)

        if form.is_valid():
            card = form.save(commit=False)
            
            # Check if user has manager roles (m1, m2) for automatic approval
            user_roles = []
            try:
                # Get user roles from UserRoleAssignment
               
                user_assignment = UserRoleAssignment.objects.filter(user=request.user, is_active=True).first()
                if user_assignment and user_assignment.role:
                    user_roles.append(user_assignment.role.name.lower())
                
                # Also check Django groups for roles like m1, m2
                user_groups = request.user.groups.values_list('name', flat=True)
                user_roles.extend([group.lower() for group in user_groups])
                
                # Check username for manager roles (m1, m2)
                username = request.user.username.lower()
                if username in ['m1', 'm2']:
                    user_roles.append(username)
                    
            except Exception:
                pass  # Continue if role checking fails
            
            # Auto-approve for manager roles
            if any(role in ['m1', 'm2', 'manager'] for role in user_roles):
                card.status = 'approved'
                messages.info(request, _('Card automatically approved due to manager privileges.'))
            
            # Wrap card saving and number generation in a transaction for safety
            try:
                with transaction.atomic():
                    card.save()

                    # Generate card number immediately if not already set using safe method
                    if not card.card_number:
                        card.card_number = card.generate_unique_card_number()
                        card.save(update_fields=['card_number'])
            except (IntegrityError, ValueError) as e:
                messages.error(request, f'Failed to create card: Could not generate unique card number. Please try again.')
                return redirect('cards:worker_id_card_create', filter=filter)
            
            messages.success(request, _('Worker ID card created successfully.'))
            return redirect('cards:worker_id_card_detail', pk=card.pk)
    else:
        initial_data = {}
        if selected_worker:
            initial_data['worker'] = selected_worker
            initial_data['worker_search'] = selected_worker.get_full_name()
        
        # Check if user has manager roles for auto-approval
        user_roles = []
        try:
            # Get user roles from UserRoleAssignment
            
            user_assignment = UserRoleAssignment.objects.filter(user=request.user, is_active=True).first()
            if user_assignment and user_assignment.role:
                user_roles.append(user_assignment.role.name.lower())
            
            # Also check Django groups for roles like m1, m2
            user_groups = request.user.groups.values_list('name', flat=True)
            user_roles.extend([group.lower() for group in user_groups])
            
            # Check username for manager roles (m1, m2)
            username = request.user.username.lower()
            if username in ['m1', 'm2']:
                user_roles.append(username)
        except Exception:
            pass  # Continue if role checking fails
        
        # Pre-select approved status for manager roles
        if any(role in ['m1', 'm2', 'manager'] for role in user_roles):
            initial_data['status'] = 'approved'
            
        form = WorkerIDCardForm(initial=initial_data, card_type=filter, user=request.user)
    

    

    context = {
        'form': form,
        'title': 'Create Worker ID Card',
        'submit_text': 'Create Card',
        'selected_worker': selected_worker,
        'workers_on_probation_count': total_workers_on_probation,
        'workers_completed_probation_count': total_workers_completed_probation,
        'workers_with_active_cards_count': workers_completed_probation_with_active_cards,
        'eligible_workers_count': eligible_workers_count,
        'business_rule_message': 'Only workers who have completed their probation period are eligible for ID cards. VIP workers are exempt from probation requirements.',
        'filter':filter,
        'role':role,
        'status_choices':WorkerIDCard.STATUS_CHOICES,
        'is_editable':is_editable
    }
    
    return render(request, 'cards/worker_id_card_form.html', context)


@login_required
# @permission_required('cards.change_workeridcard', raise_exception=True)
@permission_required('hr.change_idcard', raise_exception=True)
def worker_id_card_update(request, pk):
    """Update an existing worker ID card."""
    is_editable = True
    card = get_object_or_404(WorkerIDCard, pk=pk)
    role = None
    role = UserRoleAssignment.objects.filter(user=request.user).first()
    if request.method == 'POST':
        # Determine card type based on the worker's VIP status
        card_type = 'vip' if card.worker.is_vip else 'regular'
        form = WorkerIDCardForm(request.POST, request.FILES, instance=card, user=request.user, card_type=card_type)
        if not form.is_valid():
            # Debug: Print form errors to help identify the issue
            print(f"Form validation failed for card {pk}")
            print(f"Form data: {request.POST}")
            print(f"Form errors: {form.errors}")
            print(f"Worker field queryset count: {form.fields['worker'].queryset.count()}")
            print(f"Submitted worker ID: {request.POST.get('worker')}")
            print(f"Card's current worker ID: {card.worker.id}")
            print(f"Card's worker is VIP: {card.worker.is_vip}")
            if 'worker' in form.errors:
                print(f"Worker error: {form.errors['worker']}")
                # Check if the current worker is in the queryset
                worker_in_queryset = form.fields['worker'].queryset.filter(id=card.worker.id).exists()
                print(f"Current worker in queryset: {worker_in_queryset}")
        if form.is_valid():
            card = form.save()
            messages.success(request, _('Worker ID card updated successfully.'))
            return redirect('cards:worker_id_card_update', pk=card.pk)
    else:
        # Determine card type based on the worker's VIP status
        card_type = 'vip' if card.worker.is_vip else 'regular'
        form = WorkerIDCardForm(instance=card, user=request.user, card_type=card_type)
        # Debug: Print form field choices for status
        print(f"Form status choices for card {pk}: {form.fields['status'].choices}")
        print(f"Current card status: {card.status}")
        print(f"Worker is VIP: {card.worker.is_vip}")
    
    context = {
        'form': form,
        'card': card,
        'title': f'Update Worker ID Card - {card.worker.get_full_name()}',
        'submit_text': 'Update Card',
        'status_choices':WorkerIDCard.STATUS_CHOICES,
        'role':role,
        'is_editable':is_editable
    }
    
    return render(request, 'cards/worker_id_card_form.html', context)


@login_required
# @permission_required('cards.delete_workeridcard', raise_exception=True)
@permission_required('hr.delete_idcard', raise_exception=True)
def worker_id_card_delete(request, pk):
    """Delete a worker ID card."""
    card = get_object_or_404(WorkerIDCard, pk=pk)
    
    if request.method == 'POST':
        # Determine which list to redirect to based on worker type
        redirect_option = 'vip' if card.worker.is_vip else 'worker'
        card.delete()
        messages.success(request, _('Worker ID card deleted successfully.'))
        return redirect('cards:worker_id_card_list', redirect_option)
    
    context = {'card': card}
    return render(request, 'cards/worker_id_card_confirm_delete.html', context)




# ============================================================================
# CARD REPLACEMENT VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def card_replacement_list(request):
    """List all card replacements with search, filter, and pagination."""
    
    user = request.user
    role = UserRoleAssignment.objects.filter(user=user).first()
    replacements = CardReplacement.objects.select_related(
        'worker_card__worker'
    )
    
    # Initialize search form
    search_form = CardReplacementSearchForm(request.GET)
    
    # Apply search filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        status = search_form.cleaned_data.get('status')
        reason = search_form.cleaned_data.get('reason')
        date_range = search_form.cleaned_data.get('date_range')
        
        if search_query:
            replacements = replacements.filter(
                Q(worker_card__worker__first_name__icontains=search_query) |
                Q(worker_card__worker__last_name__icontains=search_query) |
                Q(worker_card__worker__worker_id__icontains=search_query) |
                Q(worker_card__card_number__icontains=search_query)
            )
        
        if status:
            replacements = replacements.filter(status=status)
            
        if reason:
            replacements = replacements.filter(reason=reason)
            
        if date_range:
            today = timezone.now().date()
            if date_range == 'today':
                replacements = replacements.filter(created_at__date=today)
            elif date_range == 'week':
                replacements = replacements.filter(created_at__date__gte=today - timedelta(days=7))
            elif date_range == 'month':
                replacements = replacements.filter(created_at__date__gte=today - timedelta(days=30))
            elif date_range == 'year':
                replacements = replacements.filter(created_at__date__gte=today - timedelta(days=365))
    
    # Sorting
    sort_by = request.GET.get('sort', '-created_at')
    order = request.GET.get('order', 'desc')
    
    # Apply sort direction
    if order == 'asc':
        sort_by = sort_by.lstrip('-')
    else:
        if not sort_by.startswith('-'):
            sort_by = f'-{sort_by}'
    
    replacements = replacements.order_by(sort_by)
    
    # Get statistics
    stats = {
        'total_replacements': CardReplacement.objects.count(),
        'pending_replacements': CardReplacement.objects.filter(status='pending').count(),
        'completed_replacements': CardReplacement.objects.filter(status='completed').count(),
        'lost_cards': CardReplacement.objects.filter(reason='lost').count(),
        'damaged_cards': CardReplacement.objects.filter(reason='damaged').count(),
        'worker_replacements': CardReplacement.objects.filter(worker_card__isnull=False).count(),
        'vip_replacements': 0,
    }
    
    # Pagination
    per_page = request.GET.get('per_page', '25')
    try:
        per_page = int(per_page)
        if per_page not in [25, 50, 100, 200]:
            per_page = 25
    except (ValueError, TypeError):
        per_page = 25
    
    paginator = Paginator(replacements, per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'stats': stats,
        'per_page': per_page,
        'current_sort': sort_by,
        'current_order': order,
        'role':role
    }
    
    return render(request, 'cards/card_replacement_list.html', context)


@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def card_replacement_detail(request, pk):
    """Display detailed information about a card replacement."""
    replacement = get_object_or_404(CardReplacement, pk=pk)
    
    context = {
        'replacement': replacement,
    }
    
    return render(request, 'cards/card_replacement_detail.html', context)

@login_required
def card_replacement_invoice(request,pk):
    """Display detailed information about a card replacement."""
    replacement = get_object_or_404(CardReplacement, pk=pk)
    invoice = Invoice.objects.filter(invoice_number=replacement.invoice_number).first()
    line_items = invoice.line_items.all()

    context = {
        'replacement': replacement,
        'invoice':invoice,
        'line_items':line_items
    }
    
    return render(request, 'cards/card_replacement_invoice.html', context)

@login_required
def card_selection_for_replacement(request):
    """Show card selection interface for replacement requests - Workers only (VIP and Regular)"""
    search_query = request.GET.get('search', '')
    card_type_filter = request.GET.get('card_type', '')
    
    # Get worker cards only (no employee cards for replacement)
    worker_cards = WorkerIDCard.objects.select_related(
        'worker', 'worker__building', 'worker__position'
    )
    
    # Filter to only show cards for workers who have passed probation
    eligible_worker_ids = []
    for card in worker_cards:
        worker = card.worker
        current_probation = worker.current_probation_period
        if current_probation is None or worker.status == 'passed':
            eligible_worker_ids.append(worker.id)
    
    worker_cards = worker_cards.filter(worker_id__in=eligible_worker_ids)
    
    # Apply search filter
    if search_query:
        worker_cards = worker_cards.filter(
            Q(worker__first_name__icontains=search_query) |
            Q(worker__last_name__icontains=search_query) |
            Q(worker__worker_id__icontains=search_query) |
            Q(card_number__icontains=search_query)
        )
    
    # Apply card type filter (VIP or Regular workers)
    if card_type_filter == 'vip':
        worker_cards = worker_cards.filter(worker__is_vip=True)
    elif card_type_filter == 'regular':
        worker_cards = worker_cards.filter(worker__is_vip=False)
    
    # Order by creation date (newest first)
    worker_cards = worker_cards.order_by('-created_at')
    
    total_cards = worker_cards.count()
    
    context = {
        'worker_cards': worker_cards,
        'total_cards': total_cards,
        'search_query': search_query,
        'card_type_filter': card_type_filter,
    }
    
    return render(request, 'cards/card_selection_form.html', context)

@login_required
@permission_required('hr.add_idcard', raise_exception=True)
def card_replacement_create(request):
    """Create a new card replacement request"""
    # Get the card information from URL parameters
    # Support multiple parameter formats:
    # 1. ?type=worker&card_id=18
    # 2. ?worker_card=18
    # 3. ?employee_card=18
    
    card_type = request.GET.get('type')
    card_id = request.GET.get('card_id')
    worker_card_id = request.GET.get('worker_card')
    employee_card_id = request.GET.get('employee_card')
    
    # Initialize replacement instance
    replacement = CardReplacement()
    
    # Handle different parameter formats
    if worker_card_id:
        # Format: ?worker_card=18
        try:
            replacement.worker_card = WorkerIDCard.objects.get(id=worker_card_id)
            card_type = 'worker'
            card_id = worker_card_id
        except WorkerIDCard.DoesNotExist:
            messages.error(request, 'Worker card not found.')
            return redirect('cards:worker_id_card_list', 'all')
    elif employee_card_id:
        # Format: ?employee_card=18
        try:
            replacement.employee_card = EmployeeIDCard.objects.get(id=employee_card_id)
            card_type = 'employee'
            card_id = employee_card_id
        except EmployeeIDCard.DoesNotExist:
            messages.error(request, 'Employee card not found.')
            return redirect('cards:employee_id_card_list')
    elif card_type == 'worker' and card_id:
        # Format: ?type=worker&card_id=18
        try:
            replacement.worker_card = WorkerIDCard.objects.get(id=card_id)
        except WorkerIDCard.DoesNotExist:
            messages.error(request, 'Worker card not found.')
            return redirect('cards:worker_id_card_list', 'all')
    elif card_type == 'employee' and card_id:
        # Format: ?type=employee&card_id=18
        try:
            replacement.employee_card = EmployeeIDCard.objects.get(id=card_id)
        except EmployeeIDCard.DoesNotExist:
            messages.error(request, 'Employee card not found.')
            return redirect('cards:employee_id_card_list')
    else:
        # No card parameters provided - show card selection interface
        return card_selection_for_replacement(request)

    # Show information about existing replacements (but allow unlimited)
    if replacement.worker_card:
        existing_replacements = CardReplacement.objects.filter(worker_card=replacement.worker_card).count()
        card_holder_name = replacement.worker_card.worker.get_full_name()
    elif replacement.employee_card:
        existing_replacements = CardReplacement.objects.filter(employee_card=replacement.employee_card).count()
        card_holder_name = replacement.employee_card.employee.full_name
    else:
        existing_replacements = 0
        card_holder_name = "Unknown"

    # Show info message about previous replacements (but don't prevent creation)
    if existing_replacements > 0:
        messages.info(request, f'Note: This card already has {existing_replacements} replacement request(s). You can still create additional replacements.')

    if request.method == 'POST':
        form = CardReplacementForm(request.POST, instance=replacement)
        if form.is_valid():
            replacement = form.save(commit=False)
            replacement.status = 'pending'
            replacement.save()
            messages.success(request, f'Card replacement request submitted successfully for {card_holder_name}. Estimated charge: ${replacement.replacement_charge}')
            return redirect('cards:card_replacement_list')
    else:
        form = CardReplacementForm(instance=replacement)

    context = {
        'form': form,
        'replacement': replacement,
        'estimated_charge': replacement.replacement_charge,
        'card_type': card_type,
        'card_id': card_id,
        'card_holder_name': card_holder_name,
        'existing_replacements': existing_replacements,
        'title': f'Create Card Replacement - {card_holder_name}',
        'submit_text': 'Submit Request',
    }
    return render(request, 'cards/card_replacement_form.html', context)

@login_required
@permission_required('hr.change_idcard', raise_exception=True)
def card_replacement_update(request, pk):
    """Update an existing card replacement."""
    replacement = get_object_or_404(CardReplacement, pk=pk)
    
    # Only allow updating if status is pending
    if replacement.status != 'pending':
        messages.error(request, 'Only pending replacement requests can be updated.')
        return redirect('cards:card_replacement_detail', pk=pk)

    if request.method == 'POST':
        form = CardReplacementForm(request.POST, instance=replacement)
        if form.is_valid():
            replacement = form.save()
            messages.success(request, 'Card replacement updated successfully.')
            return redirect('cards:card_replacement_detail', pk=replacement.pk)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CardReplacementForm(instance=replacement)
    
    context = {
        'form': form,
        'replacement': replacement,
        'title': f'Update Card Replacement - {replacement.card_holder_name}',
        'submit_text': 'Update Request',
        'estimated_charge': replacement.replacement_charge,
    }
    
    return render(request, 'cards/card_replacement_form.html', context)


@login_required
# @permission_required('cards.delete_cardreplacement', raise_exception=True)
@permission_required('hr.delete_idcard', raise_exception=True)
def card_replacement_delete(request, pk):
    """Delete a card replacement."""
    replacement = get_object_or_404(CardReplacement, pk=pk)
    
    if request.method == 'POST':
        replacement.delete()
        messages.success(request, _('Card replacement deleted successfully.'))
        return redirect('cards:card_replacement_list')
    
    context = {'replacement': replacement}
    return render(request, 'cards/card_replacement_confirm_delete.html', context)


@login_required
def card_replacement_invoice_create(request):
    """Create invoice for card replacement"""
    from billing.forms import ServiceForm, InvoiceForm
    from billing.models import Service, Invoice
    from django.utils import timezone
    from datetime import timedelta
    
    worker_card_id = request.GET.get('worker_card')
    if not worker_card_id:
        messages.error(request, 'Worker card ID is required.')
        return redirect('cards:card_replacement_create')
    
    try:
        worker_card = WorkerIDCard.objects.get(id=worker_card_id)
    except WorkerIDCard.DoesNotExist:
        messages.error(request, 'Invalid worker card selected.')
        return redirect('cards:card_replacement_create')
    
    # Get the reason from the request
    reason = request.GET.get('reason', 'Card replacement')
    
    # Create or get the service
    service_name = f'Print ID Card for {worker_card.worker.get_full_name()}'
    service, created = Service.objects.get_or_create(
        name=service_name,
        category='id_cards',
        defaults={
            'description': reason,
            'default_price': 5.00,
            'is_active': True
        }
    )
    
    # Create the invoice
    invoice_data = {
        'client_type': 'worker',
        'worker_id': worker_card.worker.id,
        'worker_search': f'{worker_card.worker.get_full_name()} (ID: {worker_card.worker.worker_id})',
        'status': 'pending',
        'issue_date': timezone.now().date(),
        'due_date': timezone.now().date() + timedelta(days=30),
        'tax_amount': 0,
        'client_name': worker_card.worker.get_full_name(),
        'notes': f'Card replacement service for {worker_card.worker.get_full_name()}'
    }
    
    invoice_form = InvoiceForm(invoice_data)
    
    if invoice_form.is_valid():
        invoice = invoice_form.save(commit=False)
        invoice.worker = worker_card.worker
        invoice.created_by = request.user
        invoice.save()
        
        # Create the invoice line item
        from billing.models import InvoiceLineItem
        InvoiceLineItem.objects.create(
            invoice=invoice,
            service=service,
            description=service_name,
            quantity=1,
            unit_price=5.00,
            notes=f'Worker card ID: {worker_card.id}'
        )
        
        # Recalculate invoice totals
        invoice.calculate_totals()
        invoice.save()
        
        messages.success(request, f'Invoice {invoice.invoice_number} created successfully.')
        return redirect('billing:invoice_detail', pk=invoice.pk)
    else:
        # If form validation fails, show errors
        for field, errors in invoice_form.errors.items():
            for error in errors:
                messages.error(request, f'{field}: {error}')
        
        messages.error(request, 'Invoice could not be created because the data didn\'t validate.')
        return redirect('cards:card_replacement_create')


# ============================================================================
# DASHBOARD AND UTILITY VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def cards_dashboard(request):
    """Main dashboard for ID cards management."""
    # Worker ID Cards stats
    worker_stats = {
        'total': WorkerIDCard.objects.count(),
        'pending': WorkerIDCard.objects.filter(status='pending').count(),
        'active': WorkerIDCard.objects.filter(status='active').count(),
        'expired': WorkerIDCard.objects.filter(status='expired').count(),
    }
    
    
    # Replacement stats
    replacement_stats = {
        'total': CardReplacement.objects.count(),
        'pending': CardReplacement.objects.filter(status='pending').count(),
        'completed': CardReplacement.objects.filter(status='completed').count(),
    }
    
    # Recent activity
    recent_worker_cards = WorkerIDCard.objects.select_related('worker').order_by('-created_at')[:5]
    recent_replacements = CardReplacement.objects.select_related(
        'worker_card__worker'
    ).order_by('-created_at')[:5]
    
    context = {
        'worker_stats': worker_stats,
        'replacement_stats': replacement_stats,
        'recent_worker_cards': recent_worker_cards,
        'recent_replacements': recent_replacements,
    }
    
    return render(request, 'cards/dashboard.html', context)


@login_required
def export_worker_id_cards(request):
    """Export worker ID cards to CSV."""
    cards = WorkerIDCard.objects.select_related(
        'worker', 'worker__building', 'worker__zone__created_by'
    ).order_by('-request_date')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="worker_id_cards.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Card Number', 'Worker Name', 'Worker ID', 'Building', 'Zone', 
        'Position', 'Status', 'Request Date', 'Issue Date', 'Expiry Date'
    ])
    
    for card in cards:
        writer.writerow([
            card.card_number,
            card.worker.get_full_name(),
            card.worker.worker_id,
            card.worker.building.name if card.worker.building else '',
            card.worker.zone.name if card.worker.zone else '',
            card.worker.position.name if card.worker.position else '',
            card.get_status_display(),
            card.request_date.strftime('%Y-%m-%d'),
            card.issue_date.strftime('%Y-%m-%d') if card.issue_date else '',
            card.expiry_date.strftime('%Y-%m-%d') if card.expiry_date else '',
        ])
    
    return response




# ============================================================================
# BATCH WORKER ID CARD VIEWS
# ============================================================================

@login_required
# @permission_required('cards.add_workeridcard', raise_exception=True)
@permission_required('hr.add_idcard', raise_exception=True)
@transaction.atomic
def worker_id_card_batch_create(request):
    """Create multiple worker ID cards at once with transaction safety."""

    # Get count of workers on probation for context
    total_workers_on_probation = Worker.objects.filter(
        status__in=['probation', 'extended', 'failed', 'terminated']
    ).count()

    if request.method == 'POST':
        form = BatchWorkerIDCardForm(request.POST)
        if form.is_valid():
            workers = form.cleaned_data['workers']
            status = form.cleaned_data['status']
            issue_date = form.cleaned_data['issue_date']
            expiry_date = form.cleaned_data['expiry_date']
            copy_worker_photo = form.cleaned_data['copy_worker_photo']
            notes = form.cleaned_data['notes']

            created_cards = []
            skipped_workers = []
            failed_workers = []
            auto_approved_count = 0

            for worker in workers:
                # Skip VIP workers - they should not be processed in batch
                if worker.is_vip:
                    skipped_workers.append(f"{worker.get_full_name()} (VIP worker - use individual creation)")
                    continue
                
                # Double-check probation status for regular workers
                current_probation = worker.current_probation_period
                if current_probation and worker.status in ['probation', 'extended', 'failed', 'terminated']:
                    skipped_workers.append(f"{worker.get_full_name()} (probation status: {worker.get_status_display()})")
                    continue
                
                # Check if worker already has an active card
                existing_card = WorkerIDCard.objects.filter(
                    worker=worker, 
                    status__in=['pending', 'approved', 'printed', 'delivered', 'active']
                ).first()
                
                if existing_card:
                    skipped_workers.append(f"{worker.get_full_name()} (has active card)")
                    continue
                
                # Check if user has manager roles for auto-approval
                final_status = status
                try:
                    # Get user roles from UserRoleAssignment
                   
                    user_roles = []
                    user_assignment = UserRoleAssignment.objects.filter(user=request.user, is_active=True).first()
                    if user_assignment and user_assignment.role:
                        user_roles.append(user_assignment.role.name.lower())
                    
                    # Also check Django groups for roles like m1, m2
                    user_groups = request.user.groups.values_list('name', flat=True)
                    user_roles.extend([group.lower() for group in user_groups])
                    
                    # Check username for manager roles (m1, m2)
                    username = request.user.username.lower()
                    if username in ['m1', 'm2']:
                        user_roles.append(username)
                    
                    # Auto-approve for manager roles if status is pending
                    if final_status == 'pending' and any(role in ['m1', 'm2', 'manager'] for role in user_roles):
                        final_status = 'approved'
                        auto_approved_count += 1
                        
                except Exception:
                    pass  # Continue if role checking fails

                # Create the card
                card_data = {
                    'worker': worker,
                    'status': final_status,
                    'expiry_date': expiry_date,
                    'request_date': timezone.now(),
                }
                
                if issue_date:
                    card_data['issue_date'] = issue_date
                
                if notes:
                    card_data['notes'] = notes
                
                card = WorkerIDCard.objects.create(**card_data)

                # Generate card number immediately for batch created cards with retry logic
                try:
                    if not card.card_number:
                        card.card_number = card.generate_unique_card_number()
                        card.save(update_fields=['card_number'])
                except (IntegrityError, ValueError) as e:
                    # If card number generation fails, delete the card and track the failure
                    card.delete()
                    failed_workers.append(f"{worker.get_full_name()} (could not generate unique card number)")
                    continue
                
                # Copy worker photo if requested and available
                if copy_worker_photo and worker.photo:
                    try:
                        card.photo = worker.photo
                        card.save()
                    except Exception as e:
                        # Log the error but don't fail the entire operation
                        pass
                
                created_cards.append(card)
            
            # Provide feedback to user
            if created_cards:
                success_msg = f'Successfully created {len(created_cards)} worker ID cards.'
                if auto_approved_count > 0:
                    success_msg += f' {auto_approved_count} cards were automatically approved due to manager privileges.'
                messages.success(request, success_msg)
            
            if skipped_workers:
                messages.warning(
                    request,
                    f'Skipped {len(skipped_workers)} workers: {", ".join(skipped_workers[:5])}'
                    + (f' and {len(skipped_workers) - 5} others' if len(skipped_workers) > 5 else '')
                )

            if failed_workers:
                messages.error(
                    request,
                    f'Failed to create cards for {len(failed_workers)} workers: {", ".join(failed_workers[:3])}'
                    + (f' and {len(failed_workers) - 3} others' if len(failed_workers) > 3 else '')
                )

            if not created_cards and not skipped_workers and not failed_workers:
                messages.info(request, 'No cards were created.')
            
            return redirect('cards:worker_id_card_list', 'all')
    else:
        form = BatchWorkerIDCardForm()
    
    # Get statistics for the overview
    from django.db.models import Count, Q
    from datetime import datetime, timedelta
    
    # Calculate stats for regular workers only (exclude VIP)
    total_workers = Worker.objects.filter(
        status='passed',
        is_vip=False
    ).count()
    
    workers_without_cards = form.fields['workers'].queryset.count()
    
    workers_with_photos = Worker.objects.filter(
        status='passed',
        is_vip=False
    ).exclude(
        photo__in=['', None]
    ).count()
    
    # Cards created this week
    one_week_ago = timezone.now() - timedelta(days=7)
    recent_cards = WorkerIDCard.objects.filter(
        created_at__gte=one_week_ago
    ).count()
    
    stats = {
        'total_workers': total_workers,
        'workers_without_cards': workers_without_cards,
        'workers_with_photos': workers_with_photos,
        'recent_cards': recent_cards,
    }
    
    context = {
        'form': form,
        'title': 'Batch Create Worker ID Cards',
        'submit_text': 'Create Cards',
        'workers_on_probation_count': total_workers_on_probation,
        'business_rule_message': 'Only workers who have completed their probation period are eligible for ID cards. VIP workers are exempt from probation requirements.'
    }
    
    return render(request, 'cards/worker_id_card_batch_create.html', context)


@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def worker_id_card_print_preview(request):
    """Preview worker ID cards before printing."""
    # Handle both comma-separated values and multiple parameters
    card_ids_raw = request.GET.getlist('cards')
    card_ids = []
    
    for card_id_group in card_ids_raw:
        if ',' in card_id_group:
            # Split comma-separated values
            card_ids.extend(card_id_group.split(','))
        else:
            card_ids.append(card_id_group)
    
    # Remove empty strings and convert to integers
    card_ids = [int(card_id.strip()) for card_id in card_ids if card_id.strip().isdigit()]
    
    if not card_ids:
        messages.error(request, 'No cards selected for preview.')
        return redirect('cards:worker_id_card_list', 'all')
    
    cards = WorkerIDCard.objects.filter(
        id__in=card_ids
    ).select_related(
        'worker'
    )
    
    
    # Additional safety check: filter out cards for workers still on probation (VIPs bypass this)
    eligible_cards = []
    for card in cards:
        worker = card.worker
        if worker.is_vip:
            # VIP workers are always eligible for printing
            eligible_cards.append(card)
        else:
            # Regular workers need probation checks
            current_probation = worker.current_probation_period
            if current_probation is None or worker.status == 'passed':
                eligible_cards.append(card)
            else:
                messages.warning(request, f'Skipping {worker.get_full_name()} - probation status: {worker.get_status_display()}')
    
    if not eligible_cards:
        messages.error(request, 'No valid cards found for printing.')
        return redirect('cards:worker_id_card_list', 'all')
    
    cards = eligible_cards
    
    context = {
        'cards': cards,
        'total_cards': len(cards),
        'print_date': timezone.now().date(),
    }
    
    return render(request, 'cards/worker_id_card_print_preview.html', context)


@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def worker_id_card_print_confirm(request):
    """Record the printing event when user actually prints the cards."""
    if request.method == 'POST':
        # Handle both comma-separated values and multiple parameters
        card_ids_raw = request.POST.getlist('cards')
        if not card_ids_raw:
            card_ids_raw = [request.POST.get('cards', '')]
        
        card_ids = []
        for card_id_group in card_ids_raw:
            if ',' in card_id_group:
                # Split comma-separated values
                card_ids.extend(card_id_group.split(','))
            else:
                card_ids.append(card_id_group)
        
        # Remove empty strings and convert to integers
        card_ids = [int(card_id.strip()) for card_id in card_ids if card_id.strip().isdigit()]
        
        if not card_ids:
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'message': 'No cards selected for printing.'
            }, status=400)
        
        cards = WorkerIDCard.objects.filter(id__in=card_ids)
        printed_cards = 0
        
        # Get custom batch name from request
        batch_name = request.POST.get('batch_name', '').strip()
        
        # Create a print batch for this print operation
        from .models import PrintBatch
        print_batch = PrintBatch.objects.create(
            printed_by=request.user,
            batch_name=batch_name if batch_name else f'Worker Cards - {timezone.now().strftime("%Y-%m-%d %H:%M")}',
            card_count=len(card_ids),
            batch_type='worker',
            notes=f'Worker cards printed via web interface'
        )
        
        for card in cards:
            # Record the printing event with batch reference
            card.record_print(
                user=request.user,
                notes=f'Printed via web interface on {timezone.now().strftime("%Y-%m-%d %H:%M")}',
                print_batch=print_batch
            )
            printed_cards += 1
        
        # Return JSON response with batch information
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'message': f'Successfully recorded printing of {printed_cards} card{"s" if printed_cards > 1 else ""}',
            'batch_id': print_batch.short_batch_id,
            'batch_name': print_batch.batch_name,
            'full_batch_id': str(print_batch.batch_id),
            'cards_printed': printed_cards,
            'print_date': print_batch.print_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # If GET request, redirect to preview
    return redirect('cards:worker_id_card_print_preview')


@login_required
def card_printing_history(request):
    """View printing history for all cards."""
    printing_history = CardPrintingHistory.objects.select_related(
        'card__worker', 'printed_by'
    ).all()
    
    # Apply filters
    search_query = request.GET.get('search', '').strip()
    date_range = request.GET.get('date_range', '')
    printed_by = request.GET.get('printed_by', '')
    charge_status = request.GET.get('charge_status', '')
    
    if search_query:
        printing_history = printing_history.filter(
            Q(card__worker__first_name__icontains=search_query) |
            Q(card__worker__last_name__icontains=search_query) |
            Q(card__card_number__icontains=search_query)
        )
    
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            printing_history = printing_history.filter(print_date__date=today)
        elif date_range == 'week':
            printing_history = printing_history.filter(print_date__date__gte=today - timedelta(days=7))
        elif date_range == 'month':
            printing_history = printing_history.filter(print_date__date__gte=today - timedelta(days=30))
    
    if printed_by:
        printing_history = printing_history.filter(printed_by_id=printed_by)
    
    if charge_status == 'free':
        printing_history = printing_history.filter(print_number=1)
    elif charge_status == 'charged':
        printing_history = printing_history.filter(print_number__gt=1)
    
    # Pagination
    per_page = request.GET.get('per_page', '25')
    try:
        per_page = int(per_page)
        if per_page not in [25, 50, 100]:
            per_page = 25
    except (ValueError, TypeError):
        per_page = 25
    
    paginator = Paginator(printing_history, per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Statistics
    stats = {
        'total_prints': printing_history.count(),
        'free_prints': printing_history.filter(print_number=1).count(),
        'charged_prints': printing_history.filter(print_number__gt=1).count(),
        'total_charges': printing_history.filter(print_number__gt=1).aggregate(
            total=Sum('charge_amount'))['total'] or Decimal('0.00'),
    }
    
    # Get users who have printed cards for filter
    printing_users = printing_history.values_list('printed_by__id', 'printed_by__username').distinct()
    
    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'stats': stats,
        'printing_users': printing_users,
        'search_query': search_query,
        'date_range': date_range,
        'printed_by': printed_by,
        'charge_status': charge_status,
        'title': 'Card Printing History'
    }
    
    return render(request, 'cards/card_printing_history.html', context)


@login_required
def card_charges_list(request):
    """View and manage card charges."""
    charges = CardCharge.objects.select_related(
        'worker', 'card', 'print_history', 'created_by', 'invoice'
    ).all()
    
    # Apply filters
    search_query = request.GET.get('search', '').strip()
    status = request.GET.get('status', '')
    charge_type = request.GET.get('charge_type', '')
    date_range = request.GET.get('date_range', '')
    
    if search_query:
        charges = charges.filter(
            Q(worker__first_name__icontains=search_query) |
            Q(worker__last_name__icontains=search_query) |
            Q(card__card_number__icontains=search_query) |
            Q(reason__icontains=search_query) |
            Q(invoice__invoice_number__icontains=search_query)
        )
    
    if status:
        charges = charges.filter(status=status)
    
    if charge_type:
        charges = charges.filter(charge_type=charge_type)
    
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            charges = charges.filter(created_at__date=today)
        elif date_range == 'week':
            charges = charges.filter(created_at__date__gte=today - timedelta(days=7))
        elif date_range == 'month':
            charges = charges.filter(created_at__date__gte=today - timedelta(days=30))
    
    # Handle bulk actions
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_charges = request.POST.getlist('selected_charges')
        
        if selected_charges:
            selected_charges_qs = charges.filter(id__in=selected_charges)
            
            if action == 'mark_paid':
                updated = selected_charges_qs.filter(status='pending').update(
                    status='paid',
                    payment_date=timezone.now()
                )
                messages.success(request, f'{updated} charges marked as paid.')
            
            elif action == 'waive':
                updated_count = 0
                for charge in selected_charges_qs.filter(status='pending'):
                    charge.waive_charge(request.user, 'Waived via bulk action')
                    updated_count += 1
                messages.success(request, f'{updated_count} charges waived.')
            
            elif action == 'create_invoices':
                created_count = 0
                error_count = 0
                for charge in selected_charges_qs.filter(invoice__isnull=True, amount__gt=0):
                    try:
                        charge.create_invoice()
                        created_count += 1
                    except Exception as e:
                        error_count += 1
                        messages.error(request, f'Error creating invoice for {charge.worker}: {str(e)}')
                
                if created_count > 0:
                    messages.success(request, f'{created_count} invoices created successfully.')
                if error_count > 0:
                    messages.warning(request, f'{error_count} invoices failed to create.')
        
        return redirect('cards:card_charges_list')
    
    # Pagination
    per_page = request.GET.get('per_page', '25')
    try:
        per_page = int(per_page)
        if per_page not in [25, 50, 100]:
            per_page = 25
    except (ValueError, TypeError):
        per_page = 25
    
    paginator = Paginator(charges, per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Statistics
    stats = {
        'total_charges': charges.count(),
        'pending_charges': charges.filter(status='pending').count(),
        'paid_charges': charges.filter(status='paid').count(),
        'waived_charges': charges.filter(status='waived').count(),
        'total_amount': charges.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'outstanding_amount': charges.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00'),
    }
    
    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'stats': stats,
        'search_query': search_query,
        'status': status,
        'charge_type': charge_type,
        'date_range': date_range,
        'title': 'Card Charges & Invoices'
    }
    
    return render(request, 'cards/card_charges_list.html', context)


@login_required
# @permission_required('cards.change_cardcharge', raise_exception=True)
@permission_required('hr.change_idcard', raise_exception=True)
def card_charge_update(request, pk):
    """Update a card charge."""
    charge = get_object_or_404(CardCharge, pk=pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'mark_paid':
            payment_method = request.POST.get('payment_method', '')
            payment_reference = request.POST.get('payment_reference', '')
            notes = request.POST.get('notes', '')
            
            charge.mark_as_paid(payment_method, payment_reference, notes)
            messages.success(request, 'Charge marked as paid.')
            
        elif action == 'waive':
            reason = request.POST.get('waive_reason', '')
            charge.waive_charge(request.user, reason)
            messages.success(request, 'Charge waived.')
            
        elif action == 'update':
            charge.amount = Decimal(request.POST.get('amount', charge.amount))
            charge.reason = request.POST.get('reason', charge.reason)
            charge.notes = request.POST.get('notes', charge.notes)
            charge.save()
            messages.success(request, 'Charge updated.')
        
        return redirect('cards:card_charges_list')
    
    context = {
        'charge': charge,
        'title': f'Update Charge - {charge.worker}'
    }
    
    return render(request, 'cards/card_charge_update.html', context)


def worker_card_verify_api(request, pk):
    """API endpoint to verify worker card data (for QR code scanning)."""
    try:
        card = get_object_or_404(WorkerIDCard, pk=pk)
        
        data = {
            'success': True,
            'card': {
                'id': card.id,
                'card_number': card.card_number,
                'status': card.status,
                'worker': {
                    'id': card.worker.id,
                    'worker_id': card.worker.worker_id,
                    'name': card.worker.get_full_name(),
                    'building': card.worker.building.name if card.worker.building else None,
                    'position': card.worker.position.name if card.worker.position else None,
                },
                'dates': {
                    'issue_date': card.issue_date.isoformat() if card.issue_date else None,
                    'expiry_date': card.expiry_date.isoformat() if card.expiry_date else None,
                },
                'verified_at': timezone.now().isoformat(),
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Card not found or invalid'
        }, status=404)


@require_http_methods(["GET"])
def worker_search_api(request):
    """API endpoint for worker auto-suggestions in card replacement form"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:  # Require at least 2 characters
        return JsonResponse({'workers': []})
    
    # Search workers with active ID cards
    workers_with_cards = WorkerIDCard.objects.filter(
        status__in=['active', 'lost', 'damaged'],
        worker__isnull=False
    ).select_related('worker', 'worker__building', 'worker__position').filter(
        Q(worker__first_name__icontains=query) |
        Q(worker__last_name__icontains=query) |
        Q(worker__worker_id__icontains=query) |
        Q(worker__phone_number__icontains=query) |
        Q(card_number__icontains=query)
    ).distinct()[:10]  # Limit to 10 results
    
    # Format results for auto-suggestion
    suggestions = []
    for card in workers_with_cards:
        worker = card.worker
        suggestions.append({
            'card_id': card.id,
            'card_number': card.card_number or 'PENDING',
            'worker_name': worker.get_full_name(),
            'worker_id': worker.worker_id,
            'position': worker.position.name if worker.position else 'N/A',
            'building': worker.building.name if worker.building else 'N/A',
            'phone': worker.phone_number or '',
            'status': card.get_status_display(),
            'display_text': f"{worker.get_full_name()} ({worker.worker_id}) - {card.card_number or 'PENDING'}"
        })
    
    return JsonResponse({'workers': suggestions})


@require_http_methods(["GET"])
def worker_search_for_new_card_api(request):
    """API endpoint for worker auto-suggestions when creating new ID cards"""
    query = request.GET.get('q', '').strip()
    option = request.GET.get('option')
    isVip = False

    if option == 'vip':
        isVip = True
    else:
        isVip = False
    
    if len(query) < 2:  # Require at least 2 characters
        return JsonResponse({'workers': []})
    
    # Get workers who already have active ID cards (to exclude them)
    workers_with_active_cards = WorkerIDCard.objects.filter(
        status__in=['pending', 'approved', 'printed', 'delivered', 'active']
    ).values_list('worker_id', flat=True)
    
    
    # Filter workers based on the card type being created
    if isVip:
        # For VIP card creation, only show VIP workers
        eligible_workers = Worker.objects.filter(
            is_vip=True
        ).select_related('building', 'position', 'zone').filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(worker_id__icontains=query) |
            Q(nickname__icontains=query)
        )
    else:
        # For regular card creation, only show non-VIP workers with passed status
        eligible_workers = Worker.objects.filter(
            is_vip=False,  # Only non-VIP workers
            status='passed'  # Workers who have passed probation
        ).select_related('building', 'position', 'zone').filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(worker_id__icontains=query) |
            Q(nickname__icontains=query)
        )

    # Limit results and format for auto-suggestion
    suggestions = []
    for worker in eligible_workers[:10]:  # Limit to 10 results
        # Check existing cards for display purposes
        existing_cards = WorkerIDCard.objects.filter(worker=worker)
        existing_cards_info = []
        for card in existing_cards:
            existing_cards_info.append({
                'status': card.status,
                'card_number': card.card_number or 'PENDING',
                'request_date': card.request_date.strftime('%Y-%m-%d')
            })
        
        # Determine which field(s) matched the search query
        matched_fields = []
        query_lower = query.lower()
        
        if worker.first_name and query_lower in worker.first_name.lower():
            matched_fields.append(f"First Name: {worker.first_name}")
        if worker.last_name and query_lower in worker.last_name.lower():
            matched_fields.append(f"Last Name: {worker.last_name}")
        if worker.worker_id and query_lower in worker.worker_id.lower():
            matched_fields.append(f"Worker ID: {worker.worker_id}")
        if worker.nickname and query_lower in worker.nickname.lower():
            matched_fields.append(f"Nickname: {worker.nickname}")
        
        # Create match summary
        match_summary = " | ".join(matched_fields) if matched_fields else "No match detected"
        
        suggestions.append({
            'worker_id': worker.id,
            'worker_name': worker.get_full_name(),
            'worker_code': worker.worker_id,
            'position': worker.position.name if worker.position else 'N/A',
            'building': worker.building.name if worker.building else 'N/A',
            'building_code': getattr(worker.building, 'code', None) if worker.building else None,
            'floor_number': getattr(worker.floor, 'floor_number', None) if worker.floor else None,
            'zone': worker.zone.name if worker.zone else 'N/A',
            'phone': '',  # Phone number is encrypted, not displayed
            'existing_cards': existing_cards_info,
            'probation_status': 'completed',  # All results have completed probation
            'matched_fields': matched_fields,
            'match_summary': match_summary,
            'display_text': f"{worker.get_full_name()} ({worker.worker_id}) - {worker.position.name if worker.position else 'No Position'}"
        })
    
    # Get total counts for informational message
    # Count all eligible workers (VIP + passed status)
    total_eligible = Worker.objects.filter(
        Q(is_vip=True) | Q(status='passed')
    ).count()
    
    # Count eligible workers with active cards
    eligible_with_active_cards = Worker.objects.filter(
        Q(is_vip=True) | Q(status='passed')
    ).filter(id__in=workers_with_active_cards).count()
    
    return JsonResponse({
        'workers': suggestions,
        'message': f'Found {len(suggestions)} eligible workers (VIP workers and those with passed status)',
        'stats': {
            'total_eligible': total_eligible,
            'total_with_active_cards': eligible_with_active_cards,
            'eligible_for_new_cards': total_eligible - eligible_with_active_cards
        }
        })


@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def id_cards_dashboard(request):
    """ID Cards landing page with grid of card types."""
    
    # Get all worker ID cards and separate by worker type
    worker_cards = WorkerIDCard.objects.filter(worker__is_vip=False).select_related('worker')
    vip_cards = WorkerIDCard.objects.filter(worker__is_vip=True).select_related('worker')
    
    # Worker card statistics (regular workers, not VIPs)
    worker_card_stats = {
        'total': worker_cards.count(),
        'active': worker_cards.filter(status__in=['active', 'printed', 'delivered']).count(),
        'pending': worker_cards.filter(status__in=['requested', 'pending']).count(),
        'approved': worker_cards.filter(status='approved').count(),
    }

    # VIP card statistics
    vip_card_stats = {
        'total': vip_cards.count(),
        'active': vip_cards.filter(status__in=['active', 'printed', 'delivered']).count(),
        'pending': vip_cards.filter(status__in=['requested', 'pending']).count(),
        'approved': vip_cards.filter(status='approved').count(),
    }
    
    # Employee cards - using actual EmployeeIDCard statistics
    employee_card_stats = {
        'total': 0,
        'active': 0,
        'pending': 0,
        'approved': 0,
    }
    try:
        from .models import EmployeeIDCard
        employee_cards = EmployeeIDCard.objects.all()
        employee_card_stats = {
            'total': employee_cards.count(),
            'active': employee_cards.filter(status__in=['active', 'printed', 'delivered']).count(),
            'pending': employee_cards.filter(status__in=['pending']).count(),
            'approved': employee_cards.filter(status='approved').count(),
        }
    except ImportError:
        pass
    
    context = {
        'worker_card_stats': worker_card_stats,
        'vip_card_stats': vip_card_stats,
        'employee_card_stats': employee_card_stats,
    }
    
    return render(request, 'cards/id_cards_dashboard.html', context)


# ============================================================================
# EMPLOYEE ID CARD VIEWS
# ============================================================================

@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def employee_id_card_list(request):
    """List all employee ID cards with search, filter, and pagination."""
    from .models import EmployeeIDCard, EmployeeCardCharge, EmployeeCardPrintingHistory
    from hr.models import Employee
    
    cards = EmployeeIDCard.objects.select_related('employee').prefetch_related(
        'printing_history__print_batch'
    )
    
    # Apply search filters
    search_query = request.GET.get('search', '')
    status = request.GET.get('status', '')
    card_type = request.GET.get('card_type', '')
    date_range = request.GET.get('date_range', '')
    department = request.GET.get('department', '')
    
    if search_query:
        cards = cards.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(employee__employee_id__icontains=search_query) |
            Q(card_number__icontains=search_query)
        )
    
    if status:
        cards = cards.filter(status=status)
        
    if card_type:
        cards = cards.filter(card_type=card_type)
        
    # Department filter removed - Employee model doesn't have department field
        
    if date_range:
        today = timezone.now().date()
        if date_range == 'today':
            cards = cards.filter(request_date__date=today)
        elif date_range == 'week':
            cards = cards.filter(request_date__date__gte=today - timedelta(days=7))
        elif date_range == 'month':
            cards = cards.filter(request_date__date__gte=today - timedelta(days=30))
        elif date_range == 'year':
            cards = cards.filter(request_date__date__gte=today - timedelta(days=365))
    
    # Sorting
    sort_by = request.GET.get('sort', '-request_date')
    order = request.GET.get('order', 'desc')
    
    if order == 'asc':
        sort_by = sort_by.lstrip('-')
    else:
        if not sort_by.startswith('-'):
            sort_by = f'-{sort_by}'
    
    cards = cards.order_by(sort_by)
    
    # Get statistics
    stats = {
        'total_cards': EmployeeIDCard.objects.count(),
        'pending_cards': EmployeeIDCard.objects.filter(status='pending').count(),
        'approved_cards': EmployeeIDCard.objects.filter(status='approved').count(),
        'active_cards': EmployeeIDCard.objects.filter(status='active').count(),
        'expired_cards': EmployeeIDCard.objects.filter(status='expired').count(),
        'lost_damaged': EmployeeIDCard.objects.filter(status__in=['lost', 'damaged']).count(),
        'recent_requests': EmployeeIDCard.objects.filter(
            request_date__date__gte=timezone.now().date() - timedelta(days=7)
        ).count(),
        'total_charges': EmployeeCardCharge.objects.count(),
        'pending_charges': EmployeeCardCharge.objects.filter(status='pending').count(),
        'outstanding_amount': EmployeeCardCharge.objects.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00'),
        'total_prints': EmployeeCardPrintingHistory.objects.count(),
        'charged_prints': EmployeeCardPrintingHistory.objects.filter(print_number__gt=1).count(),
    }
    
    # Pagination
    per_page = request.GET.get('per_page', '25')
    try:
        per_page = int(per_page)
        if per_page not in [25, 50, 100, 200]:
            per_page = 25
    except (ValueError, TypeError):
        per_page = 25
    
    paginator = Paginator(cards, per_page)
    page = request.GET.get('page')
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # Add charge information for each card in the current page
    for card in page_obj:
        card.total_charges = card.charges.count()
        card.outstanding_charges = card.charges.filter(status='pending').count()
        card.outstanding_amount = card.charges.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00')
        card.total_prints = card.printing_history.count()
    
    # Department filter removed - Employee model doesn't have department field
    
    context = {
        'page_obj': page_obj,
        'stats': stats,
        'per_page': per_page,
        'current_sort': sort_by,
        'current_order': order,
        'search_query': search_query,
        'status': status,
        'card_type': card_type,
        'date_range': date_range,
        'status_choices': EmployeeIDCard.STATUS_CHOICES,
        'card_type_choices': EmployeeIDCard.CARD_TYPE_CHOICES,
    }
    
    return render(request, 'cards/employee_id_card_list.html', context)


@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def employee_id_card_detail(request, pk):
    """Display detailed information about an employee ID card."""
    from .models import EmployeeIDCard
    
    card = get_object_or_404(EmployeeIDCard, pk=pk)
    replacements = card.replacements.all().order_by('-created_at')
    
    # Get charge and printing information
    charges = card.charges.all().order_by('-created_at')
    printing_history = card.printing_history.all().order_by('-print_date')
    
    # Calculate charge statistics
    charge_stats = {
        'total_charges': charges.count(),
        'pending_charges': charges.filter(status='pending').count(),
        'paid_charges': charges.filter(status='paid').count(),
        'waived_charges': charges.filter(status='waived').count(),
        'total_amount': charges.aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
        'outstanding_amount': charges.filter(status='pending').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00'),
        'paid_amount': charges.filter(status='paid').aggregate(
            total=Sum('amount'))['total'] or Decimal('0.00'),
    }
    
    # Calculate printing statistics
    print_stats = {
        'total_prints': printing_history.count(),
        'free_prints': printing_history.filter(print_number=1).count(),
        'charged_prints': printing_history.filter(print_number__gt=1).count(),
        'last_print_date': printing_history.first().print_date if printing_history.exists() else None,
        'next_print_charge': card.next_print_charge,
    }
    
    context = {
        'card': card,
        'replacements': replacements,
        'charges': charges,
        'printing_history': printing_history,
        'charge_stats': charge_stats,
        'print_stats': print_stats,
    }
    
    return render(request, 'cards/employee_id_card_detail.html', context)


@login_required
# @permission_required('cards.add_employeeidcard', raise_exception=True)
@permission_required('hr.add_idcard', raise_exception=True)
def employee_id_card_create(request):
    """Create a new employee ID card."""
    from .forms import EmployeeIDCardForm
    
    if request.method == 'POST':
        form = EmployeeIDCardForm(request.POST)
        if form.is_valid():
            card = form.save(commit=False)
            
            # Check if user has manager roles (m1, m2) for automatic approval
            user_roles = []
            try:
                # Get user roles from UserRoleAssignment
               
                user_assignment = UserRoleAssignment.objects.filter(user=request.user, is_active=True).first()
                if user_assignment and user_assignment.role:
                    user_roles.append(user_assignment.role.name.lower())
                
                # Also check Django groups for roles like m1, m2
                user_groups = request.user.groups.values_list('name', flat=True)
                user_roles.extend([group.lower() for group in user_groups])
                
                # Check username for manager roles (m1, m2)
                username = request.user.username.lower()
                if username in ['m1', 'm2']:
                    user_roles.append(username)
                    
            except Exception:
                pass  # Continue if role checking fails
            
            # Auto-approve for manager roles
            if any(role in ['m1', 'm2', 'manager'] for role in user_roles):
                card.status = 'approved'
                messages.info(request, _('Card automatically approved due to manager privileges.'))
            
            card.save()
            messages.success(request, _('Employee ID card created successfully.'))
            return redirect('cards:employee_id_card_detail', pk=card.pk)
    else:
        initial_data = {}
        
        # Check if user has manager roles for auto-approval
        user_roles = []
        try:
            # Get user roles from UserRoleAssignment
           
            user_assignment = UserRoleAssignment.objects.filter(user=request.user, is_active=True).first()
            if user_assignment and user_assignment.role:
                user_roles.append(user_assignment.role.name.lower())
            
            # Also check Django groups for roles like m1, m2
            user_groups = request.user.groups.values_list('name', flat=True)
            user_roles.extend([group.lower() for group in user_groups])
            
            # Check username for manager roles (m1, m2)
            username = request.user.username.lower()
            if username in ['m1', 'm2']:
                user_roles.append(username)
        except Exception:
            pass  # Continue if role checking fails
        
        # Pre-select approved status for manager roles
        if any(role in ['m1', 'm2', 'manager'] for role in user_roles):
            initial_data['status'] = 'approved'
            
        form = EmployeeIDCardForm(initial=initial_data)
    role = UserRoleAssignment.objects.filter(user=request.user).first()
    context = {
        'form': form,
        'title': 'Create Employee ID Card',
        'submit_text': 'Create Card',
        'status_choices':EmployeeIDCard.STATUS_CHOICES,
        'role':role
    }
    
    return render(request, 'cards/employee_id_card_form.html', context)


@login_required
# @permission_required('cards.change_employeeidcard', raise_exception=True)
@permission_required('hr.change_idcard', raise_exception=True)
def employee_id_card_update(request, pk):
    """Update an employee ID card."""
    from .forms import EmployeeIDCardForm
    from .models import EmployeeIDCard
    
    card = get_object_or_404(EmployeeIDCard, pk=pk)
    
    # Get user role for template context
    role = UserRoleAssignment.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        form = EmployeeIDCardForm(request.POST, instance=card)
        if form.is_valid():
            form.save()
            messages.success(request, _('Employee ID card updated successfully.'))
            return redirect('cards:employee_id_card_detail', pk=card.pk)
    else:
        form = EmployeeIDCardForm(instance=card)
    
    context = {
        'form': form,
        'card': card,
        'title': f'Update Employee ID Card - {card.employee}',
        'submit_text': 'Update Card',
        'status_choices': EmployeeIDCard.STATUS_CHOICES,
        'role': role
    }
    
    return render(request, 'cards/employee_id_card_form.html', context)


@login_required
# @permission_required('cards.delete_employeeidcard', raise_exception=True)
@permission_required('hr.delete_idcard', raise_exception=True)
def employee_id_card_delete(request, pk):
    """Delete an employee ID card."""
    from .models import EmployeeIDCard
    
    card = get_object_or_404(EmployeeIDCard, pk=pk)
    
    if request.method == 'POST':
        card.delete()
        messages.success(request, _('Employee ID card deleted successfully.'))
        return redirect('cards:employee_id_card_list')
    
    context = {
        'card': card,
        'title': f'Delete Employee ID Card - {card.employee}'
    }
    
    return render(request, 'cards/employee_id_card_confirm_delete.html', context)


@login_required
# @permission_required('cards.add_employeeidcard', raise_exception=True)
@permission_required('hr.add_idcard', raise_exception=True)
def employee_id_card_batch_create(request):
    """Create multiple employee ID cards at once."""
    from .forms import BatchEmployeeIDCardForm, EmployeeSelectionForm
    from .models import EmployeeIDCard
    from hr.models import Employee
    
    if request.method == 'POST':
        form = BatchEmployeeIDCardForm(request.POST)
        if form.is_valid():
            employees = form.cleaned_data['employees']
            card_type = form.cleaned_data['card_type']
            issue_date = form.cleaned_data['issue_date']
            expiry_date = form.cleaned_data['expiry_date']
            notes = form.cleaned_data['notes']
            
            created_cards = []
            for employee in employees:
                # Check if employee already has an active card
                if not EmployeeIDCard.objects.filter(
                    employee=employee,
                    status__in=['active', 'pending', 'approved']
                ).exists():
                    card = EmployeeIDCard.objects.create(
                        employee=employee,
                        card_type=card_type,
                        issue_date=issue_date,
                        expiry_date=expiry_date,
                        notes=notes,
                        status='pending'
                    )
                    created_cards.append(card)
            
            messages.success(request, f'Created {len(created_cards)} employee ID cards.')
            return redirect('cards:employee_id_card_list')
    else:
        form = BatchEmployeeIDCardForm()
    
    # Get employees without active cards
    employees_without_cards = Employee.objects.exclude(
        id_cards__status__in=['active', 'pending', 'approved']
    ).distinct()
    
    context = {
        'form': form,
        'employees_without_cards': employees_without_cards,
        'title': 'Batch Create Employee ID Cards'
    }
    
    return render(request, 'cards/employee_id_card_batch_create.html', context)


@login_required
def employee_id_card_select_for_print(request):
    """Select employee ID cards for printing."""
    from .models import EmployeeIDCard
    
    if request.method == 'POST':
        card_ids = request.POST.getlist('selected_cards')
        if card_ids:
            return redirect(f"{reverse('cards:employee_id_card_print_preview')}?cards={','.join(card_ids)}")
        else:
            messages.warning(request, 'Please select at least one card to print.')
    
    # Get printable cards
    cards = EmployeeIDCard.objects.filter(
        status__in=['approved', 'active']
    ).select_related('employee')
    
    context = {
        'cards': cards,
        'title': 'Select Employee ID Cards for Printing'
    }
    
    return render(request, 'cards/employee_id_card_select_print.html', context)


@login_required
def employee_id_card_print_preview(request):
    """Preview employee ID cards before printing."""
    # Handle both comma-separated values and multiple parameters
    card_ids_raw = request.GET.getlist('cards')
    card_ids = []
    
    for card_id_group in card_ids_raw:
        if ',' in card_id_group:
            # Split comma-separated values
            card_ids.extend(card_id_group.split(','))
        else:
            card_ids.append(card_id_group)
    
    # Remove empty strings and convert to integers
    card_ids = [int(card_id.strip()) for card_id in card_ids if card_id.strip().isdigit()]
    
    if not card_ids:
        messages.error(request, 'No cards selected for preview.')
        return redirect('cards:employee_id_card_list')
    
    # Get the cards
    cards = EmployeeIDCard.objects.filter(id__in=card_ids).select_related('employee')
    
    if not cards.exists():
        messages.error(request, 'No valid cards found for printing.')
        return redirect('cards:employee_id_card_list')
    
    context = {
        'cards': cards,
        'total_cards': cards.count(),
        'print_date': timezone.now().date(),
    }
    
    return render(request, 'cards/employee_id_card_print_preview.html', context)


@login_required
def employee_id_card_print_confirm(request):
    """Record the printing event when user actually prints the employee cards."""
    if request.method == 'POST':
        # Handle both comma-separated values and multiple parameters
        card_ids_raw = request.POST.getlist('cards')
        if not card_ids_raw:
            card_ids_raw = [request.POST.get('cards', '')]
        
        card_ids = []
        for card_id_group in card_ids_raw:
            if ',' in card_id_group:
                # Split comma-separated values
                card_ids.extend(card_id_group.split(','))
            else:
                card_ids.append(card_id_group)
        
        # Remove empty strings and convert to integers
        card_ids = [int(card_id.strip()) for card_id in card_ids if card_id.strip().isdigit()]
        
        if not card_ids:
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'message': 'No cards selected for printing.'
            }, status=400)
        
        # Get custom batch name from request
        batch_name = request.POST.get('batch_name', '').strip()
        
        # Create a print batch for this print operation
        from .models import PrintBatch
        print_batch = PrintBatch.objects.create(
            printed_by=request.user,
            batch_name=batch_name if batch_name else f'Employee Cards - {timezone.now().strftime("%Y-%m-%d %H:%M")}',
            card_count=len(card_ids),
            batch_type='employee',
            notes=f'Employee cards printed via web interface'
        )
        
        cards = EmployeeIDCard.objects.filter(id__in=card_ids)
        printed_cards = 0
        
        for card in cards:
            # Record the printing event with batch reference
            card.record_print(
                user=request.user,
                notes=f'Printed via web interface on {timezone.now().strftime("%Y-%m-%d %H:%M")}',
                print_batch=print_batch
            )
            printed_cards += 1
        
        # Return JSON response with batch information
        from django.http import JsonResponse
        return JsonResponse({
            'success': True,
            'message': f'Successfully recorded printing of {printed_cards} card{"s" if printed_cards > 1 else ""}',
            'batch_id': print_batch.short_batch_id,
            'batch_name': print_batch.batch_name,
            'full_batch_id': str(print_batch.batch_id),
            'cards_printed': printed_cards,
            'print_date': print_batch.print_date.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    # If GET request, redirect to preview
    return redirect('cards:employee_id_card_print_preview')


@login_required
def export_employee_id_cards(request):
    """Export employee ID cards to CSV."""
    from .models import EmployeeIDCard
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="employee_id_cards.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Card Number', 'Employee ID', 'Employee Name', 'Card Type', 'Status',
        'Request Date', 'Issue Date', 'Expiry Date', 'Print Count', 'Notes'
    ])
    
    cards = EmployeeIDCard.objects.select_related(
        'employee'
    ).order_by('-request_date')
    
    for card in cards:
        writer.writerow([
            card.card_number or '',
            card.employee.employee_id,
            card.employee.full_name,
            card.get_card_type_display(),
            card.get_status_display(),
            card.request_date.strftime('%Y-%m-%d %H:%M'),
            card.issue_date.strftime('%Y-%m-%d') if card.issue_date else '',
            card.expiry_date.strftime('%Y-%m-%d') if card.expiry_date else '',
            card.print_count,
            card.notes or ''
        ])
    
    return response


@login_required
def employee_search_api(request):
    """API endpoint for searching employees."""
    from hr.models import Employee
    
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'employees': []})

    employees = Employee.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(employee_id__icontains=query)
    )[:20]

    employee_data = []
    for employee in employees:
        # Check if employee already has an active card
        from .models import EmployeeIDCard
        has_active_card = EmployeeIDCard.objects.filter(
            employee=employee,
            status__in=['active', 'pending', 'approved']
        ).exists()

        employee_info = {
            'id': employee.id,
            'name': employee.full_name,
            'employee_id': employee.employee_id,
            'department': 'Not assigned',  # No department field
            'position': 'Not assigned',  # No position field
            'has_active_card': has_active_card,
        }
        employee_data.append(employee_info)

    return JsonResponse({'employees': employee_data})


@require_http_methods(["GET"])
def employee_card_search_api(request):
    """API endpoint for employee card auto-suggestions in card replacement form"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:  # Require at least 2 characters
        return JsonResponse({'employee_cards': []})
    
    # Search employee cards with active status that can be replaced
    employee_cards = EmployeeIDCard.objects.filter(
        status__in=['active', 'lost', 'damaged'],
        employee__isnull=False
    ).select_related('employee').filter(
        Q(employee__first_name__icontains=query) |
        Q(employee__last_name__icontains=query) |
        Q(employee__employee_id__icontains=query) |
        Q(employee__email__icontains=query) |
        Q(employee__phone_number__icontains=query) |
        Q(card_number__icontains=query)
    ).distinct()[:10]  # Limit to 10 results
    
    # Format results for auto-suggestion
    suggestions = []
    for card in employee_cards:
        employee = card.employee
        suggestions.append({
            'card_id': card.id,
            'card_number': card.card_number or 'PENDING',
            'employee_name': employee.full_name,
            'employee_id': employee.employee_id,
            'department': 'N/A',  # No department field
            'position': 'N/A',  # No position field
            'email': employee.email or '',
            'phone': employee.phone_number or '',
            'status': card.get_status_display(),
            'card_type': card.get_card_type_display(),
            'display_text': f"{employee.full_name} ({employee.employee_id}) - {card.card_number or 'PENDING'}"
        })
    
    return JsonResponse({'employee_cards': suggestions})


@require_http_methods(["GET"])
def worker_card_search_api(request):
    """API endpoint for worker card auto-suggestions in card replacement form"""
    query = request.GET.get('q', '').strip()
    card_id = request.GET.get('card_id', '').strip()
    
    worker_cards = WorkerIDCard.objects.filter(
        worker__isnull=False
    ).select_related('worker', 'worker__building', 'worker__zone', 'worker__position')
    
    # If searching by specific card ID (for pre-selected cards)
    if card_id:
        try:
            card_id = int(card_id)
            worker_cards = worker_cards.filter(id=card_id)
        except (ValueError, TypeError):
            return JsonResponse({'worker_cards': []})
    else:
        # Regular search by query
        if len(query) < 2:  # Require at least 2 characters
            return JsonResponse({'worker_cards': []})
        
        # Search worker cards with active status that can be replaced
        worker_cards = worker_cards.filter(
            status__in=['active', 'lost', 'damaged']
        ).filter(
            Q(worker__first_name__icontains=query) |
            Q(worker__last_name__icontains=query) |
            Q(worker__worker_id__icontains=query) |
            Q(worker__email__icontains=query) |
            Q(worker__phone_number__icontains=query) |
            Q(card_number__icontains=query)
        ).distinct()[:10]  # Limit to 10 results
    
    # Format results for auto-suggestion
    suggestions = []
    for card in worker_cards:
        worker = card.worker
        suggestions.append({
            'card_id': card.id,
            'card_number': card.card_number or 'PENDING',
            'worker_name': worker.get_full_name(),
            'worker_id': worker.worker_id,
            'building': worker.building.name if worker.building else 'N/A',
            'zone': worker.zone.name if worker.zone else 'N/A',
            'position': worker.position.name if worker.position else 'N/A',
            'email': worker.email or '',
            'phone': worker.phone_number or '',
            'status': card.get_status_display(),
            'issue_date': card.issue_date.strftime('%Y-%m-%d') if card.issue_date else None,
            'expiry_date': card.expiry_date.strftime('%Y-%m-%d') if card.expiry_date else None,
            'print_count': card.print_count,
            'display_text': f"{worker.get_full_name()} ({worker.worker_id}) - {card.card_number or 'PENDING'}"
        })
    
    return JsonResponse({'worker_cards': suggestions})





def employee_card_verify_api(request, pk):
    """API endpoint to verify employee card data (for QR code scanning)."""
    from .models import EmployeeIDCard
    
    try:
        card = get_object_or_404(EmployeeIDCard, pk=pk)
        
        data = {
            'success': True,
            'card': {
                'id': card.id,
                'card_number': card.card_number,
                'status': card.status,
                'card_type': card.get_card_type_display(),
                'employee': {
                    'id': card.employee.id,
                    'employee_id': card.employee.employee_id,
                    'name': card.employee.full_name,
                    'department': None,  # No department field
                    'position': None,  # No position field
                },
                'dates': {
                    'issue_date': card.issue_date.isoformat() if card.issue_date else None,
                    'expiry_date': card.expiry_date.isoformat() if card.expiry_date else None,
                },
                'verified_at': timezone.now().isoformat(),
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': 'Card not found or invalid'
        }, status=404)


@login_required
@require_http_methods(["GET", "POST"])
def card_replacement_approve(request, pk):
    """Approve or reject a card replacement request"""
    replacement = get_object_or_404(CardReplacement, pk=pk)
    
    if replacement.status != 'pending':
        messages.error(request, 'This replacement request cannot be modified.')
        return redirect('cards:card_replacement_list')
    
    if request.method == 'POST':
        form = CardReplacementApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            notes = form.cleaned_data['notes']

            if action == 'approve':
                try:
                    replacement.approve_replacement(request.user, notes)

                    # Refresh from database to get updated status
                    replacement.refresh_from_db()

                    # Check if invoice was created
                    try:
                        # Try to get the invoice number for confirmation
                        invoice_info = ""
                        if replacement.auto_invoice:
                            invoice_info = " An invoice has been automatically generated."

                        messages.success(
                            request,
                            f'Card replacement request approved successfully.{invoice_info} '
                            f'Charge: ${replacement.replacement_charge} for {replacement.get_reason_display().lower()} '
                            f'{replacement.card_type.lower()} card replacement.'
                        )
                    except Exception as e:
                        messages.success(request, 'Card replacement request approved successfully.')

                except Exception as e:
                    messages.error(request, f'Error approving replacement: {str(e)}')

            else:
                try:
                    replacement.reject_replacement(request.user, notes)
                    replacement.refresh_from_db()
                    messages.success(request, 'Card replacement request rejected.')
                except Exception as e:
                    messages.error(request, f'Error rejecting replacement: {str(e)}')

            return redirect('cards:card_replacement_list')
        else:
            messages.error(request, 'Please correct the form errors below.')
    else:
        form = CardReplacementApprovalForm()
    
    context = {
        'form': form,
        'replacement': replacement,
    }
    return render(request, 'cards/card_replacement_approval_form.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def card_replacement_complete(request, pk):
    """Complete a card replacement request"""
    replacement = get_object_or_404(CardReplacement, pk=pk)
    
    if replacement.status != 'approved':
        messages.error(request, 'This replacement request is not approved and cannot be completed.')
        return redirect('cards:card_replacement_list')
    
    if request.method == 'POST':
        form = CardReplacementCompletionForm(request.POST)
        if form.is_valid():
            new_card_number = form.cleaned_data['new_card_number']
            notes = form.cleaned_data['notes']
            
            replacement.complete_replacement(request.user, new_card_number, notes)
            messages.success(request, 'Card replacement request completed successfully.')
            
            return redirect('cards:card_replacement_list')
    else:
        form = CardReplacementCompletionForm()
    
    context = {
        'form': form,
        'replacement': replacement,
    }
    return render(request, 'cards/card_replacement_completion_form.html', context)



@login_required
@permission_required('hr.view_idcard', raise_exception=True)
def next_card_sequence_api(request):
    """API endpoint to get the next sequence number for a card number prefix"""
    prefix = request.GET.get('prefix', '').strip()
    
    if not prefix:
        return JsonResponse({'error': 'Prefix is required'}, status=400)
    
    # Find existing cards with the same prefix
    existing_cards = WorkerIDCard.objects.filter(
        card_number__startswith=prefix
    )
    
    sequence_numbers = []
    for card in existing_cards:
        try:
            # Extract the sequence number from the end
            seq_part = card.card_number.split('-')[-1]
            if seq_part.isdigit():
                sequence_numbers.append(int(seq_part))
        except (IndexError, ValueError):
            continue
    
    # Get next sequence number
    next_sequence = max(sequence_numbers, default=0) + 1
    
    return JsonResponse({
        'next_sequence': next_sequence,
        'existing_count': len(sequence_numbers),
        'prefix': prefix
    })

 