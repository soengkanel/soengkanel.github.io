"""
Simplified Improved Probation Management Views
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.core.paginator import Paginator
from datetime import timedelta
from zone.models import Worker, WorkerProbationPeriod, Building, Floor
from zone.forms import ProbationSearchForm


def is_manager(user):
    """Check if user has manager privileges for probation approvals."""
    # First check superuser - they always have access
    if user.is_superuser:
        return True
    
    # Check for UserRoleAssignment with manager or admin role
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.select_related('role').filter(
            user=user, 
            is_active=True
        ).first()
        
        if role_assignment and role_assignment.role:
            user_role = role_assignment.role.name.lower()
            return user_role in ['manager', 'admin']
    except:
        pass
    
    # Fallback to group check
    return user.groups.filter(name='Managers').exists()

def can_add_probation(user):
    """Check if user can add probation periods (users, managers, and admins)."""
    # First check superuser - they always have access
    if user.is_superuser:
        return True
    
    # Check for UserRoleAssignment with user, manager or admin role
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.select_related('role').filter(
            user=user, 
            is_active=True
        ).first()
        
        if role_assignment and role_assignment.role:
            user_role = role_assignment.role.name.lower()
            return user_role in ['user', 'manager', 'admin']
    except:
        pass
    
    # Fallback to authenticated users
    return user.is_authenticated


@login_required
def probation_list_improved(request):
    """
    Enhanced probation management with comprehensive filtering, pagination, and sorting.
    Supports both table and board views with all filtering capabilities.
    """
    user_is_manager = is_manager(request.user)
    today = timezone.now().date()
    
    # Initialize search form
    search_form = ProbationSearchForm(request.GET or None)
    
    # First, ensure all workers with probation-related statuses have probation records (exclude VIP workers)
    probation_related_workers = Worker.objects.filter(
        status__in=['probation', 'extended', 'passed', 'failed', 'terminated'],
        is_vip=False  # VIP workers don't need probation management
    )
    
    for worker in probation_related_workers:
        if not worker.probation_periods.exists():
            # Create missing probation record
            start_date = worker.date_joined or (timezone.now().date() - timedelta(days=90))
            end_date = start_date + timedelta(days=90)
            
            # Get current user or None for auto-created records
            current_user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                current_user = request.user
            
            WorkerProbationPeriod.objects.create(
                worker=worker,
                start_date=start_date,
                original_end_date=end_date,
                evaluation_notes="Auto-created to sync with worker status",
                created_by=current_user
            )
    
    # Base queryset - START WITH WORKERS who have probation-related statuses (Worker-first approach)
    # This ensures worker names are NEVER empty and provides better performance
    # Include workers whose status might be 'probation', 'extended', 'passed', 'failed', etc.
    probation_workers = Worker.objects.filter(
        status__in=['probation', 'extended', 'passed', 'failed', 'terminated'],  # All probation-related statuses
        is_vip=False  # Exclude VIP workers from probation management
    ).select_related(
        'zone', 'building', 'position'
    ).prefetch_related(
        'probation_periods__extensions',
        'probation_periods__extension_requests__requested_by'
    )
    
    
    # Apply search filters to workers
    if search_form.is_valid():
        # Search by worker name or ID
        search_query = search_form.cleaned_data.get('search')
        if search_query:
            probation_workers = probation_workers.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(worker_id__icontains=search_query)
            )
        
        # Apply status filtering
        status_filter = search_form.cleaned_data.get('status')
        if status_filter:
            probation_workers = probation_workers.filter(status=status_filter)
        
        # Apply zone filtering
        zone_filter = search_form.cleaned_data.get('zone')
        if zone_filter:
            probation_workers = probation_workers.filter(zone=zone_filter)
            
        # Apply building filtering  
        building_filter = search_form.cleaned_data.get('building')
        if building_filter:
            probation_workers = probation_workers.filter(building=building_filter)
            
        # Apply position filtering
        position_filter = search_form.cleaned_data.get('position')
        if position_filter:
            probation_workers = probation_workers.filter(position=position_filter)
            
        # Apply days remaining filtering
        days_remaining_filter = search_form.cleaned_data.get('days_remaining')
        if days_remaining_filter:
            today = timezone.now().date()
            if days_remaining_filter == 'overdue':
                # Filter workers with overdue probations (negative days remaining)
                filtered_ids = []
                for worker in probation_workers:
                    if worker.probation_days_remaining < 0:
                        filtered_ids.append(worker.id)
                probation_workers = probation_workers.filter(id__in=filtered_ids)
            elif days_remaining_filter == 'ending_soon':
                # Filter workers with probations ending in 7 days or less
                filtered_ids = []
                for worker in probation_workers:
                    days_rem = worker.probation_days_remaining
                    if 0 <= days_rem <= 7:
                        filtered_ids.append(worker.id)
                probation_workers = probation_workers.filter(id__in=filtered_ids)
            elif days_remaining_filter == 'ending_month':
                # Filter workers with probations ending in 30 days or less
                filtered_ids = []
                for worker in probation_workers:
                    days_rem = worker.probation_days_remaining
                    if 0 <= days_rem <= 30:
                        filtered_ids.append(worker.id)
                probation_workers = probation_workers.filter(id__in=filtered_ids)
            elif days_remaining_filter == 'normal':
                # Filter workers with more than 30 days remaining
                filtered_ids = []
                for worker in probation_workers:
                    if worker.probation_days_remaining > 30:
                        filtered_ids.append(worker.id)
                probation_workers = probation_workers.filter(id__in=filtered_ids)
        
        # Apply batch name filtering
        batch_name_filter = search_form.cleaned_data.get('batch_name')
        if batch_name_filter:
            # Filter workers whose probation periods have batch names containing the search term
            filtered_ids = []
            for worker in probation_workers:
                current_probation = worker.current_probation_period
                if current_probation and current_probation.batch_name:
                    if batch_name_filter.lower() in current_probation.batch_name.lower():
                        filtered_ids.append(worker.id)
            probation_workers = probation_workers.filter(id__in=filtered_ids)
    else:
        # Fallback to GET parameters for backward compatibility
        search_query = request.GET.get('search')
        
        if search_query:
            probation_workers = probation_workers.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(worker_id__icontains=search_query)
            )
    
    # Convert to list for processing and add calculated fields
    workers_list = list(probation_workers)
    
    # Add pending extension request flags and additional calculated fields
    from .models import ProbationExtensionRequest
    for worker in workers_list:
        # Get current probation period for this worker
        current_probation = worker.current_probation_period
        
        if current_probation:
            worker.has_pending_extension_request = ProbationExtensionRequest.objects.filter(
                probation_period=current_probation,
                status='pending'
            ).exists()
            
            # Check for recent rejections (within last 7 days)
            recent_rejection_cutoff = timezone.now() - timedelta(days=7)
            worker.has_recent_rejection = ProbationExtensionRequest.objects.filter(
                probation_period=current_probation,
                status='rejected',
                reviewed_at__gte=recent_rejection_cutoff
            ).exists()
            
            # Add calculated days_remaining for filtering and sorting
            worker.calculated_days_remaining = worker.probation_days_remaining
        else:
            # Worker has no probation period (shouldn't happen with current filter)
            worker.has_pending_extension_request = False
            worker.has_recent_rejection = False
            worker.calculated_days_remaining = 999  # Fallback
    
    # No filtering applied - show all workers
    
    # Apply default sorting based on user role
    if user_is_manager:
        # Default manager priority sorting
        def sort_priority(worker):
            # Priority: 0 = highest, higher numbers = lower priority
            days_rem = worker.calculated_days_remaining
            if worker.status == 'probation' and days_rem <= 3:
                return (0, days_rem)  # Highest priority for urgent probations
            elif worker.status == 'probation':
                return (1, days_rem)  # Normal probations
            else:
                return (2, 999)
        
        workers_list.sort(key=sort_priority)
    else:
        # Default sorting: newest first
        workers_list.sort(key=lambda worker: worker.date_joined, reverse=True)
    
    # Get pagination parameters
    per_page = request.GET.get('per_page', 25)
    try:
        per_page = int(per_page)
        if per_page not in [10, 25, 50, 100]:
            per_page = 25
    except (ValueError, TypeError):
        per_page = 25
    
    # Setup pagination
    paginator = Paginator(workers_list, per_page)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Calculate statistics (exclude VIP workers)
    total_probations = WorkerProbationPeriod.objects.filter(worker__is_vip=False).count()
    active_count = Worker.objects.filter(status='probation', is_vip=False).count()
    
    # Calculate ending soon count (exclude VIP workers)
    ending_soon = 0
    for worker in Worker.objects.filter(status='probation', is_vip=False):
        if worker.probation_days_remaining <= 7 and worker.probation_days_remaining >= 0:
            ending_soon += 1
    
    extended_count = WorkerProbationPeriod.objects.filter(worker__status='extended', worker__is_vip=False).count()
    completed_count = WorkerProbationPeriod.objects.filter(worker__status='passed', worker__is_vip=False).count()
    
    # Get pending extension requests count (exclude VIP workers)
    from .models import ProbationExtensionRequest
    try:
        pending_extension_requests = ProbationExtensionRequest.objects.filter(
            status='pending',
            probation_period__worker__is_vip=False
        ).count()
    except Exception:
        pending_extension_requests = 0
    
    # Get workers needing attention (first 5)
    attention_needed = []
    for worker in workers_list[:5]:
        if (worker.status == 'probation' and 
            worker.calculated_days_remaining <= 3 and worker.calculated_days_remaining >= 0):
            attention_needed.append(worker)
    
    # Count workers by status for statistics
    active_probations_count = len([w for w in workers_list if w.status == 'probation'])
    completed_probations_count = completed_count
    failed_probations_count = len([w for w in workers_list if w.status in ['failed', 'terminated']])
    
    # Calculate stats for summary
    stats = {
        'total_active': len([w for w in workers_list if w.status == 'probation']),
        'ending_soon': ending_soon,
        'extended': extended_count,
        'passed': completed_count,
        'failed': failed_probations_count,
        'total_records': len(workers_list),  # Filtered count
        'all_records': total_probations,  # Total unfiltered count
    }
    
    context = {
        'probations': page_obj,  # Paginated workers for table view (keeping same name for template compatibility)
        'search_form': search_form,
        'stats': stats,  # Stats summary
        'user_is_manager': user_is_manager,
        'can_add_probation': can_add_probation(request.user),
        'total_probations': total_probations,
        'active_probations': active_count,  # Active probation workers count
        'extensions': extended_count,  # Extended probation workers count
        'active_count': active_count,
        'pending_requests': pending_extension_requests,
        'awaiting_approval': pending_extension_requests,
        'ending_soon': ending_soon,
        'extended_count': extended_count,
        'completed_count': completed_count,
        'attention_needed': attention_needed,
        'search_query': search_query,
        'per_page': per_page,
        'total_count': len(workers_list),
    }
    
    return render(request, 'zone/probation_list.html', context)


@login_required
def probation_workflow_action(request, probation_id, action):
    """
    Simple workflow actions for probation management.
    Handles both form POST and AJAX JSON requests.
    """
    import json
    from django.http import JsonResponse
    
    try:
        probation = get_object_or_404(WorkerProbationPeriod, id=probation_id)
        user_is_manager = is_manager(request.user)
    except Exception as e:
        messages.error(request, f'Error accessing probation period: {str(e)}')
        return redirect('zone:probation_list')
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or 'application/json' in request.headers.get('Accept', '')
    
    # Show confirmation page for GET requests
    
    if action == 'complete' and user_is_manager:
        # Manager action: Complete probation (pass)
        if request.method == 'POST':
            probation.worker.status = 'passed'
            probation.worker.save()
            
            # Keep worker status as 'probation' - no auto-syncing
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': f'Probation completed for {probation.worker.get_full_name()}'
                })
            
            messages.success(request, f'Probation completed for {probation.worker.get_full_name()} - Probation period marked as Passed')
            return redirect('zone:probation_list')
    
    elif action == 'extend':
        # Handle extension - proper maker-checker workflow
        if request.method == 'POST':
            try:
                # Get extension parameters from modal
                extension_days = int(request.POST.get('extension_days', 30))
                reason = request.POST.get('reason', '').strip()
                
                if not reason:
                    if is_ajax:
                        return JsonResponse({
                            'success': False,
                            'message': 'Extension reason is required'
                        })
                    messages.error(request, 'Extension reason is required')
                    return redirect('zone:probation_list')
            except (ValueError, TypeError) as e:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': f'Invalid extension days: {str(e)}'
                    })
                messages.error(request, f'Invalid extension days: {str(e)}')
                return redirect('zone:probation_list')
            
            if user_is_manager:
                # Manager action: Direct extension (bypass request system)
                try:
                    from .models import WorkerProbationExtension
                    
                    # Create extension record
                    extension = WorkerProbationExtension.objects.create(
                        probation_period=probation,
                        extension_duration_days=extension_days,
                        reason=reason or f"Direct manager extension - {extension_days} days",
                        approved_by=request.user,
                        created_by=request.user
                    )
                except Exception as e:
                    if is_ajax:
                        return JsonResponse({
                            'success': False,
                            'message': f'Error creating extension: {str(e)}'
                        })
                    messages.error(request, f'Error creating extension: {str(e)}')
                    return redirect('zone:probation_list')
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': f'Probation extended for {probation.worker.get_full_name()}'
                    })
                
                # Extension model automatically updates probation status and dates
                messages.success(request, f'Probation extended for {probation.worker.get_full_name()} - {extension_days} days added')
            else:
                # Regular user action: Create extension request for manager approval
                from .models import ProbationExtensionRequest
                
                # Check if there's already a pending request
                pending_request = ProbationExtensionRequest.objects.filter(
                    probation_period=probation,
                    status='pending'
                ).first()
                
                if pending_request:
                    if is_ajax:
                        return JsonResponse({
                            'success': False,
                            'message': f'Extension request already pending for {probation.worker.get_full_name()}'
                        })
                    messages.warning(request, f'Extension request already pending for {probation.worker.get_full_name()}')
                else:
                    # Create new extension request
                    extension_request = ProbationExtensionRequest.objects.create(
                        probation_period=probation,
                        extension_duration_days=extension_days,
                        reason=reason or f"User requested {extension_days}-day extension",
                        requested_by=request.user
                    )
                    
                    # Keep probation status as 'probation' - extension requests are tracked separately
                    # probation.status remains 'probation'
                    
                    # Keep worker status as 'probation' - no auto-syncing
                    
                    if is_ajax:
                        return JsonResponse({
                            'success': True,
                            'message': f'Extension request submitted for {probation.worker.get_full_name()}'
                        })
                    
                    messages.success(request, f'Extension request submitted for {probation.worker.get_full_name()} ({extension_days} days) - Waiting for manager approval')
            
            if not is_ajax:
                return redirect('zone:probation_list')
    
    elif action == 'edit' and user_is_manager:
        # Manager action: Edit probation details
        if request.method == 'POST':
            from datetime import datetime, timedelta
            
            # Get form data
            new_status = request.POST.get('status')
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            extension_days = int(request.POST.get('extension_days', 0))
            notes = request.POST.get('notes', '').strip()
            
            # Validate and update probation
            try:
                if start_date_str:
                    probation.start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                
                if end_date_str:
                    new_end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                    
                    # If we're setting a specific end date, clear existing extensions 
                    # and set the actual_end_date directly to override calculations
                    probation.actual_end_date = new_end_date
                    
                    # Add extension days if specified (on top of the set end date)
                    if extension_days > 0:
                        final_end_date = new_end_date + timedelta(days=extension_days)
                        probation.actual_end_date = final_end_date
                        
                        # Create an extension record for audit trail
                        from .models import WorkerProbationExtension
                        WorkerProbationExtension.objects.create(
                            probation_period=probation,
                            extension_duration_days=extension_days,
                            reason=f"Manager edit extension: {extension_days} days added to manually set end date",
                            approved_by=request.user,
                            created_by=request.user
                        )
                
                # Update worker status if changed  
                if new_status and new_status != probation.worker.status:
                    probation.worker.status = new_status
                    probation.worker.save()
                
                # Add notes if provided
                if notes:
                    if probation.evaluation_notes:
                        probation.evaluation_notes += f"\n\n[Manager Edit - {timezone.now().strftime('%Y-%m-%d %H:%M')}]: {notes}"
                    else:
                        probation.evaluation_notes = f"[Manager Edit - {timezone.now().strftime('%Y-%m-%d %H:%M')}]: {notes}"
                
                probation.save()
                
                # Force recalculation by refreshing the object
                probation.refresh_from_db()
                
                success_msg = f"Probation updated for {probation.worker.get_full_name()}"
                if extension_days > 0:
                    success_msg += f" (Extended {extension_days} days)"
                if end_date_str:
                    success_msg += f" (End date: {new_end_date.strftime('%b %d, %Y')})"
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': success_msg
                    })
                
                messages.success(request, success_msg)
                return redirect('zone:probation_list')
                
            except ValueError as e:
                error_msg = f"Invalid date format: {str(e)}"
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': error_msg
                    })
                messages.error(request, error_msg)
                return redirect('zone:probation_list')
            except Exception as e:
                error_msg = f"Error updating probation: {str(e)}"
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': error_msg
                    })
                messages.error(request, error_msg)
                return redirect('zone:probation_list')
    
    elif action == 'fail' and user_is_manager:
        # Manager action: Fail probation
        if request.method == 'POST':
            probation.worker.status = 'failed'
            probation.worker.save()
            
            # Keep worker status as 'probation' - no auto-syncing
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': f'Probation failed for {probation.worker.get_full_name()}'
                })
            
            messages.warning(request, f'Probation failed for {probation.worker.get_full_name()} - Probation period marked as Failed')
            return redirect('zone:probation_list')
    
    elif action == 'activate' and user_is_manager:
        # Manager action: Reactivate probation (move back to active status)
        if request.method == 'POST':
            probation.worker.status = 'probation'
            probation.worker.save()
            
            # Keep worker status as 'probation' - no auto-syncing
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': f'Probation reactivated for {probation.worker.get_full_name()}'
                })
            
            messages.success(request, f'Probation reactivated for {probation.worker.get_full_name()} - Probation period status updated to Active')
            return redirect('zone:probation_list')
    
    elif action == 'approve_extension' and user_is_manager:
        # Manager action: Approve extension request
        if request.method == 'POST':
            from .models import ProbationExtensionRequest, WorkerProbationExtension
            
            # Find the pending extension request
            extension_request = ProbationExtensionRequest.objects.filter(
                probation_period=probation,
                status='pending'
            ).first()
            
            if extension_request:
                # Create the actual extension
                extension = WorkerProbationExtension.objects.create(
                    probation_period=probation,
                    extension_duration_days=extension_request.extension_duration_days,
                    reason=f"Approved extension request: {extension_request.reason}",
                    approved_by=request.user,
                    created_by=extension_request.requested_by
                )
                
                # Update extension request status
                extension_request.status = 'approved'
                extension_request.reviewed_by = request.user
                extension_request.reviewed_at = timezone.now()
                extension_request.review_comments = request.POST.get('review_comments', 'Approved')
                extension_request.save()
                
                # Move worker to extended status
                probation.worker.status = 'extended'
                probation.worker.save()
                
                # Keep worker status as 'probation' - no auto-syncing
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': f'Extension request approved for {probation.worker.get_full_name()}'
                    })
                
                messages.success(request, f'Extension request approved for {probation.worker.get_full_name()} - {extension_request.extension_duration_days} days added')
            else:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': 'No pending extension request found'
                    })
                messages.error(request, 'No pending extension request found')
            
            if not is_ajax:
                return redirect('zone:probation_list')
    
    elif action == 'reject_extension' and user_is_manager:
        # Manager action: Reject extension request
        if request.method == 'POST':
            from .models import ProbationExtensionRequest
            
            # Find the pending extension request
            extension_request = ProbationExtensionRequest.objects.filter(
                probation_period=probation,
                status='pending'
            ).first()
            
            if extension_request:
                # Update extension request status
                extension_request.status = 'rejected'
                extension_request.reviewed_by = request.user
                extension_request.reviewed_at = timezone.now()
                extension_request.review_comments = request.POST.get('review_comments', 'Rejected')
                extension_request.save()
                
                # Move worker back to probation status
                probation.worker.status = 'probation'
                probation.worker.save()
                
                # Keep worker status as 'probation' - no auto-syncing
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': f'Extension request rejected for {probation.worker.get_full_name()}'
                    })
                
                messages.warning(request, f'Extension request rejected for {probation.worker.get_full_name()} - Moved back to active probation. Reason: {extension_request.review_comments}')
            else:
                if is_ajax:
                    return JsonResponse({
                        'success': False,
                        'message': 'No pending extension request found'
                    })
                messages.error(request, 'No pending extension request found')
            
            if not is_ajax:
                return redirect('zone:probation_list')
    
    elif action == 'request_extension':
        # Handle extension request (for drag-and-drop to pending column)
        if request.method == 'POST':
            if user_is_manager:
                # Manager can directly move worker to extended status
                probation.worker.status = 'extended'
                probation.worker.save()
                
                # Keep worker status as 'probation' - no auto-syncing
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': f'Probation status updated to extended for {probation.worker.get_full_name()}'
                    })
            else:
                # Regular user: create extension request
                from .models import ProbationExtensionRequest
                
                # Check if there's already a pending request
                pending_request = ProbationExtensionRequest.objects.filter(
                    probation_period=probation,
                    status='pending'
                ).first()
                
                if not pending_request:
                    # Create new extension request
                    ProbationExtensionRequest.objects.create(
                        probation_period=probation,
                        extension_duration_days=30,
                        reason="Extension request via drag-and-drop",
                        requested_by=request.user
                    )
                    
                    # Keep probation status as 'probation' - extension requests are tracked separately
                    # probation.status remains 'probation'
                    
                    # Keep worker status as 'probation' - no auto-syncing
                
                if is_ajax:
                    return JsonResponse({
                        'success': True,
                        'message': f'Extension request submitted for {probation.worker.get_full_name()}'
                    })
            
            if not is_ajax:
                return redirect('zone:probation_list')
    
    elif action == 'terminate' and user_is_manager:
        # Manager action: Terminate probation
        if request.method == 'POST':
            probation.worker.status = 'terminated'
            probation.worker.save()
            
            # Keep worker status as 'probation' - no auto-syncing
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'message': f'Probation terminated for {probation.worker.get_full_name()}'
                })
            
            messages.error(request, f'Probation terminated for {probation.worker.get_full_name()} - Probation period marked as Terminated')
            return redirect('zone:probation_list')
    
    # Handle permission denied for non-managers
    if not user_is_manager and action in ['complete', 'fail', 'activate', 'terminate']:
        if is_ajax:
            return JsonResponse({
                'success': False,
                'message': 'Permission denied: Only managers can perform this action'
            })
        messages.error(request, 'Permission denied: Only managers can perform this action')
        return redirect('zone:probation_list')
    
    # Handle unknown actions
    if is_ajax:
        return JsonResponse({
            'success': False,
            'message': f'Unknown action: {action}'
        })
    
    # If we get here, show confirmation page for non-AJAX requests
    context = {
        'probation': probation,
        'action': action,
        'user_is_manager': user_is_manager,
    }
    return render(request, 'zone/probation_workflow_action.html', context)


@login_required
def sync_worker_probation_status(request, probation_id):
    """
    Sync worker status with probation status for mismatched records.
    """
    probation = get_object_or_404(WorkerProbationPeriod, id=probation_id)
    user_is_manager = is_manager(request.user)
    
    if not user_is_manager:
        messages.error(request, 'Only managers can sync worker statuses.')
        return redirect('zone:probation_list')
    
    if request.method == 'POST':
        sync_direction = request.POST.get('sync_direction')
        
        # Since we now only use Worker.status as single source of truth, 
        # no syncing is needed - probation periods no longer have status field
        messages.info(request, 
            f'Status syncing is no longer needed - Worker.status is now the single source of truth '
            f'for {probation.worker.get_full_name()}')
        
        return redirect('zone:probation_list')
    
    context = {
        'probation': probation,
        'user_is_manager': user_is_manager,
    }
    return render(request, 'zone/sync_worker_probation.html', context)


@login_required
def bulk_sync_worker_probation_status(request):
    """
    Bulk sync all worker statuses with their probation statuses.
    """
    user_is_manager = is_manager(request.user)
    
    if not user_is_manager:
        messages.error(request, 'Only managers can perform bulk sync operations.')
        return redirect('zone:probation_list')
    
    if request.method == 'POST':
        sync_direction = request.POST.get('sync_direction', 'probation_to_worker')
        
        # Since we now only use Worker.status as single source of truth, 
        # no bulk syncing is needed - probation periods no longer have status field
        messages.info(request, 
            'Bulk status syncing is no longer needed - Worker.status is now the single source of truth. '
            'All probation status is managed through Worker.status only.')
        
        return redirect('zone:probation_list')
    
    # GET request - show confirmation page
    # Since probation periods no longer have status field, no mismatches are possible
    mismatched_count = 0
    mismatched_examples = []
    
    context = {
        'mismatched_count': mismatched_count,
        'mismatched_examples': mismatched_examples,
        'user_is_manager': user_is_manager,
    }
    return render(request, 'zone/bulk_sync_worker_probation.html', context)


@login_required
def probation_extension_history(request, probation_id):
    """
    API endpoint to get extension request history for a probation period.
    """
    from django.http import JsonResponse
    
    probation = get_object_or_404(WorkerProbationPeriod, id=probation_id)
    
    # Check if user has permission to view this probation
    user_is_manager = is_manager(request.user)
    if not user_is_manager and probation.extension_requests.filter(requested_by=request.user).count() == 0:
        # User can only see history if they are a manager or have made a request for this probation
        return JsonResponse({
            'success': False,
            'message': 'Permission denied'
        })
    
    # Get all extension requests for this probation
    from .models import ProbationExtensionRequest
    extension_requests = ProbationExtensionRequest.objects.filter(
        probation_period=probation
    ).order_by('-created_at')
    
    history = []
    for request in extension_requests:
        history.append({
            'extension_duration_days': request.extension_duration_days,
            'reason': request.reason,
            'status': request.status,
            'requested_by': request.requested_by.get_full_name() if request.requested_by else 'Unknown',
            'requested_at': request.requested_at.strftime('%b %d, %Y %H:%M') if request.requested_at else '',
            'reviewed_by': request.reviewed_by.get_full_name() if request.reviewed_by else None,
            'reviewed_at': request.reviewed_at.strftime('%b %d, %Y %H:%M') if request.reviewed_at else None,
            'review_comments': request.review_comments,
        })
    
    return JsonResponse({
        'success': True,
        'history': history
    })


@login_required
def probation_dashboard(request):
    """
    Dashboard view for probation management with role-specific metrics.
    """
    user_is_manager = is_manager(request.user)
    today = timezone.now().date()
    
    # Base statistics
    stats = {
        'total_workers': Worker.objects.count(),
        'on_probation': Worker.objects.filter(status__in=['probation', 'extended']).count(),
        'completed': Worker.objects.filter(status='passed').count(),
    }
    
    if user_is_manager:
        # Manager dashboard
        stats.update({
            'pending_extensions': 0,  # Simplified
            'approved_today': 0,  # Simplified
            'ending_this_week': sum(
                1 for p in WorkerProbationPeriod.objects.filter(worker__status__in=['probation', 'extended'])
                if p.get_end_date() and today <= p.get_end_date() <= today + timedelta(days=7)
            ),
        })
        
        # Recent activities - simplified
        recent_activities = WorkerProbationPeriod.objects.select_related(
            'worker', 'created_by'
        ).order_by('-created_at')[:10]
    else:
        # User dashboard
        user_workers = Worker.objects.filter(created_by=request.user)
        stats.update({
            'my_workers': user_workers.count(),
            'my_pending': 0,  # Simplified
            'my_approved': 0,  # Simplified
        })
        
        # User's recent activities
        recent_activities = WorkerProbationPeriod.objects.filter(
            worker__in=user_workers
        ).select_related(
            'worker', 'created_by'
        ).order_by('-created_at')[:10]
    
    context = {
        'user_is_manager': user_is_manager,
        'stats': stats,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'zone/probation_dashboard.html', context)


@login_required
def probation_extension_requests(request):
    """
    Manager view to approve/reject pending extension requests.
    """
    user_is_manager = is_manager(request.user)
    
    if not user_is_manager:
        messages.error(request, 'Only managers can view extension requests.')
        return redirect('zone:probation_list')
    
    from .models import ProbationExtensionRequest
    
    # Get all pending extension requests
    pending_requests = ProbationExtensionRequest.objects.filter(
        status='pending'
    ).select_related(
        'probation_period', 'probation_period__worker', 'requested_by'
    ).order_by('-created_at')
    
    context = {
        'pending_requests': pending_requests,
        'user_is_manager': user_is_manager,
    }
    
    return render(request, 'zone/extension_requests_list.html', context)


@login_required 
def approve_extension_request(request, request_id):
    """
    Manager action to approve/reject extension requests.
    """
    user_is_manager = is_manager(request.user)
    
    if not user_is_manager:
        messages.error(request, 'Only managers can approve extension requests.')
        return redirect('zone:probation_list')
    
    from .models import ProbationExtensionRequest, WorkerProbationExtension
    
    extension_request = get_object_or_404(ProbationExtensionRequest, id=request_id)
    
    if extension_request.status != 'pending':
        messages.warning(request, f'Extension request has already been {extension_request.status}.')
        return redirect('zone:probation_extension_requests')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        review_notes = request.POST.get('review_notes', '')
        
        if action == 'approve':
            # Approve the extension request
            extension_request.status = 'approved'
            extension_request.reviewed_by = request.user
            extension_request.reviewed_at = timezone.now()
            extension_request.review_comments = review_notes
            extension_request.save()
            
            # Create the actual extension
            WorkerProbationExtension.objects.create(
                probation_period=extension_request.probation_period,
                extension_duration_days=extension_request.extension_duration_days,
                reason=f"Approved extension request: {extension_request.reason}",
                approved_by=request.user,
                created_by=extension_request.requested_by,
                extension_request=extension_request
            )
            
            messages.success(
                request, 
                f'Extension request approved for {extension_request.probation_period.worker.get_full_name()} - '
                f'{extension_request.extension_duration_days} days added'
            )
            
        elif action == 'reject':
            # Reject the extension request
            extension_request.status = 'rejected'
            extension_request.reviewed_by = request.user
            extension_request.reviewed_at = timezone.now()
            extension_request.review_comments = review_notes or "Request rejected by manager"
            extension_request.save()
            
            messages.warning(
                request,
                f'Extension request rejected for {extension_request.probation_period.worker.get_full_name()}'
            )
        
        return redirect('zone:probation_extension_requests')
    
    context = {
        'extension_request': extension_request,
        'user_is_manager': user_is_manager,
    }
    
    return render(request, 'zone/extension_request_review.html', context)


@login_required
def get_buildings_for_zone(request):
    """
    AJAX endpoint to get buildings for a specific zone.
    Used for chained select in filtering.
    """
    from django.http import JsonResponse

    zone_id = request.GET.get('zone_id')

    if not zone_id:
        # Return all buildings if no zone selected
        buildings = Building.objects.filter(is_active=True).order_by('name')
    else:
        buildings = Building.objects.filter(zone_id=zone_id, is_active=True).order_by('name')

    buildings_data = []
    for building in buildings:
        buildings_data.append({
            'id': building.id,
            'name': building.name,
            'code': building.code
        })

    return JsonResponse({'buildings': buildings_data})


@login_required
def get_floors_for_building(request):
    """
    AJAX endpoint to get floors for a specific building.
    Used for chained select in filtering.
    """
    from django.http import JsonResponse

    building_id = request.GET.get('building_id')

    if not building_id:
        return JsonResponse({'floors': []})

    floors = Floor.objects.filter(building_id=building_id, is_active=True).order_by('floor_number')
    floors_data = []
    for floor in floors:
        floors_data.append({
            'id': floor.id,
            'name': floor.name,
            'floor_number': floor.floor_number,
            'display_name': f"F{floor.floor_number}" if floor.floor_number else floor.name
        })

    return JsonResponse({'floors': floors_data})


@login_required
def get_available_workers(request):
    """
    AJAX endpoint to get workers available for probation assignment.
    Returns workers who are not VIP and not currently on probation.
    """
    import json
    from django.http import JsonResponse
    
    # Get workers who are not VIP and not already on probation
    available_workers = Worker.objects.filter(
        is_vip=False,
        status__in=['active', 'inactive', 'terminated']  # Not on probation statuses
    ).exclude(
        status__in=['probation', 'extended']  # Exclude those already on probation
    ).select_related('position', 'zone').order_by('first_name', 'last_name')[:100]  # Limit for performance
    
    workers_data = []
    for worker in available_workers:
        workers_data.append({
            'id': worker.id,
            'name': worker.get_full_name(),
            'worker_id': worker.worker_id,
            'position': worker.position.name if worker.position else 'Unassigned',
            'zone': worker.zone.name if worker.zone else 'Unassigned'
        })
    
    return JsonResponse({
        'workers': workers_data,
        'count': len(workers_data)
    })


@login_required
def probation_bulk_delete(request):
    """
    Bulk delete probation periods - managers only.
    """
    user_is_manager = is_manager(request.user)
    
    if not user_is_manager:
        messages.error(request, 'Only managers can perform bulk deletions.')
        return redirect('zone:probation_list')
    
    if request.method == 'POST':
        probation_ids = request.POST.getlist('probation_ids')
        
        if not probation_ids:
            messages.error(request, 'No probations selected for deletion.')
            return redirect('zone:probation_list')
        
        try:
            # Get probation periods to delete
            probations_to_delete = WorkerProbationPeriod.objects.filter(
                id__in=probation_ids
            ).select_related('worker')
            
            if not probations_to_delete:
                messages.error(request, 'No valid probations found for deletion.')
                return redirect('zone:probation_list')
            
            # Store worker information for status updates
            workers_to_update = []
            deleted_count = 0
            
            for probation in probations_to_delete:
                worker = probation.worker
                worker_name = worker.get_full_name()
                
                # Reset worker status to active if they were on probation
                if worker.status in ['probation', 'extended']:
                    worker.status = 'active'
                    workers_to_update.append(worker)
                
                # Delete the probation period
                probation.delete()
                deleted_count += 1
            
            # Bulk update worker statuses
            if workers_to_update:
                Worker.objects.bulk_update(workers_to_update, ['status'])
            
            messages.success(
                request, 
                f'Successfully deleted {deleted_count} probation period(s). '
                f'Affected workers have been set to active status.'
            )
            
        except Exception as e:
            messages.error(request, f'Error during bulk deletion: {str(e)}')
    
    return redirect('zone:probation_list')


@login_required
def probation_batch_pass(request):
    """
    Batch pass probation periods - managers only.
    """
    user_is_manager = is_manager(request.user)
    
    if not user_is_manager:
        messages.error(request, 'Only managers can perform batch probation passing.')
        return redirect('zone:probation_list')
    
    if request.method == 'POST':
        probation_ids = request.POST.getlist('probation_ids')
        
        if not probation_ids:
            messages.error(request, 'No probations selected for passing.')
            return redirect('zone:probation_list')
        
        try:
            # Get probation periods to pass
            probations_to_pass = WorkerProbationPeriod.objects.filter(
                id__in=probation_ids
            ).select_related('worker')
            
            if not probations_to_pass:
                messages.error(request, 'No valid probations found for passing.')
                return redirect('zone:probation_list')
            
            # Store worker information for status updates
            workers_to_update = []
            passed_count = 0
            worker_names = []
            
            for probation in probations_to_pass:
                worker = probation.worker
                worker_name = worker.get_full_name()
                worker_names.append(worker_name)
                
                # Update worker status to passed if they were on probation
                if worker.status in ['probation', 'extended']:
                    worker.status = 'passed'
                    workers_to_update.append(worker)
                    passed_count += 1
                elif worker.status == 'active':
                    # If worker is already active, still count as passed
                    worker.status = 'passed'
                    workers_to_update.append(worker)
                    passed_count += 1
            
            # Bulk update worker statuses
            if workers_to_update:
                Worker.objects.bulk_update(workers_to_update, ['status'])
            
            # Create success message
            if passed_count == 1:
                success_message = f'Successfully passed probation for {worker_names[0]}.'
            elif passed_count <= 3:
                success_message = f'Successfully passed probation for {", ".join(worker_names)}.'
            else:
                success_message = f'Successfully passed probation for {passed_count} workers.'
                
            messages.success(request, success_message)
            
        except Exception as e:
            messages.error(request, f'Error during batch pass: {str(e)}')
    
    return redirect('zone:probation_list')