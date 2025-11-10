from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    Suggestion, SuggestionCategory, SuggestionComment,
    SuggestionVote, SuggestionStatusHistory
)
from .forms import (
    SuggestionForm, SuggestionResponseForm,
    SuggestionCommentForm, SuggestionFilterForm,
    SuggestionImplementationForm
)
from hr.models import Employee


# ============================================================================
# EMPLOYEE PORTAL VIEWS (For submitting and viewing suggestions)
# ============================================================================

@login_required
def suggestion_list(request):
    """List all suggestions with filtering (employee portal view)"""
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Check if showing "My Suggestions" or "All Suggestions"
    view_type = request.GET.get('view', 'all')

    # Get filter parameters
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('suggestion_type', '')
    category_filter = request.GET.get('category', '')
    search_query = request.GET.get('search', '')

    # Base queryset
    if view_type == 'my':
        # Show only employee's own suggestions
        suggestions = Suggestion.objects.filter(employee=employee)
    else:
        # Show all suggestions
        suggestions = Suggestion.objects.all()

    suggestions = suggestions.select_related(
        'employee', 'category', 'assigned_to'
    ).prefetch_related('votes', 'comments')

    # Apply filters
    if status_filter:
        suggestions = suggestions.filter(status=status_filter)

    if type_filter:
        suggestions = suggestions.filter(suggestion_type=type_filter)

    if category_filter:
        suggestions = suggestions.filter(category_id=category_filter)

    if search_query:
        suggestions = suggestions.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Order by date
    suggestions = suggestions.order_by('-submitted_date')

    # Pagination
    paginator = Paginator(suggestions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Check which suggestions the employee has voted for
    voted_ids = SuggestionVote.objects.filter(
        employee=employee
    ).values_list('suggestion_id', flat=True)

    # Statistics
    my_suggestions_count = Suggestion.objects.filter(employee=employee).count()
    total_suggestions = Suggestion.objects.count()
    pending_count = Suggestion.objects.filter(status='submitted').count()
    implemented_count = Suggestion.objects.filter(status='implemented').count()

    # Categories for filter
    categories = SuggestionCategory.objects.filter(is_active=True)

    context = {
        'employee': employee,
        'page_obj': page_obj,
        'voted_ids': list(voted_ids),
        'my_suggestions_count': my_suggestions_count,
        'total_suggestions': total_suggestions,
        'pending_count': pending_count,
        'implemented_count': implemented_count,
        'categories': categories,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'category_filter': category_filter,
        'search_query': search_query,
        'view_type': view_type,
        'status_choices': Suggestion.STATUS_CHOICES,
        'type_choices': Suggestion.TYPE_CHOICES,
    }

    return render(request, 'suggestions/suggestion_list.html', context)


@login_required
def suggestion_create(request):
    """Create a new suggestion"""
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    if request.method == 'POST':
        form = SuggestionForm(request.POST, request.FILES)
        if form.is_valid():
            suggestion = form.save(commit=False)
            suggestion.employee = employee
            suggestion.submitted_date = timezone.now()
            suggestion.status = 'submitted'
            suggestion.save()

            messages.success(request, _('Your suggestion has been submitted successfully!'))
            return redirect('suggestions:my_suggestions')
    else:
        form = SuggestionForm()

    context = {
        'employee': employee,
        'form': form,
    }

    return render(request, 'suggestions/suggestion_form.html', context)


@login_required
def suggestion_detail(request, pk):
    """View detailed information about a suggestion"""
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    suggestion = get_object_or_404(
        Suggestion.objects.select_related('employee', 'category', 'assigned_to', 'response_by'),
        pk=pk
    )

    # Increment view count
    suggestion.views += 1
    suggestion.save(update_fields=['views'])

    # Check if employee has voted
    has_voted = SuggestionVote.objects.filter(
        suggestion=suggestion,
        employee=employee
    ).exists()

    # Get comments (exclude internal comments unless user is staff)
    comments = suggestion.comments.select_related('user')
    if not request.user.is_staff:
        comments = comments.filter(is_internal=False)

    # Status history
    status_history = suggestion.status_history.select_related('changed_by').order_by('-created_at')

    # Comment form
    comment_form = SuggestionCommentForm()

    context = {
        'employee': employee,
        'suggestion': suggestion,
        'has_voted': has_voted,
        'comments': comments,
        'status_history': status_history,
        'comment_form': comment_form,
        'can_edit': suggestion.employee == employee and suggestion.status == 'submitted',
    }

    return render(request, 'suggestions/suggestion_detail.html', context)


@login_required
def suggestion_edit(request, pk):
    """Edit an existing suggestion (only if status is 'submitted')"""
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    suggestion = get_object_or_404(Suggestion, pk=pk, employee=employee)

    # Only allow editing if status is submitted
    if suggestion.status != 'submitted':
        messages.error(request, 'You can only edit suggestions that are still in submitted status.')
        return redirect('suggestions:suggestion_detail', pk=pk)

    if request.method == 'POST':
        form = SuggestionForm(request.POST, request.FILES, instance=suggestion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your suggestion has been updated successfully!')
            return redirect('suggestions:suggestion_detail', pk=pk)
    else:
        form = SuggestionForm(instance=suggestion)

    context = {
        'employee': employee,
        'form': form,
        'suggestion': suggestion,
        'is_edit': True,
    }

    return render(request, 'suggestions/suggestion_form.html', context)


@login_required
def my_suggestions(request):
    """View employee's own suggestions"""
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get employee's suggestions
    suggestions = Suggestion.objects.filter(employee=employee).select_related(
        'category', 'assigned_to', 'response_by'
    ).order_by('-submitted_date')

    # Pagination
    paginator = Paginator(suggestions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_count = suggestions.count()
    pending_count = suggestions.filter(status__in=['submitted', 'under_review']).count()
    approved_count = suggestions.filter(status='approved').count()
    implemented_count = suggestions.filter(status='implemented').count()

    context = {
        'employee': employee,
        'page_obj': page_obj,
        'total_count': total_count,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'implemented_count': implemented_count,
    }

    return render(request, 'suggestions/my_suggestions.html', context)


@login_required
@require_POST
def suggestion_vote(request, pk):
    """Vote for a suggestion"""
    try:
        employee = request.user.employee
    except:
        return JsonResponse({'success': False, 'error': 'Employee profile not found'}, status=403)

    suggestion = get_object_or_404(Suggestion, pk=pk)

    # Check if already voted
    vote, created = SuggestionVote.objects.get_or_create(
        suggestion=suggestion,
        employee=employee
    )

    if created:
        # New vote
        suggestion.upvotes += 1
        suggestion.save(update_fields=['upvotes'])
        return JsonResponse({'success': True, 'action': 'voted', 'upvotes': suggestion.upvotes})
    else:
        # Remove vote
        vote.delete()
        suggestion.upvotes = max(0, suggestion.upvotes - 1)
        suggestion.save(update_fields=['upvotes'])
        return JsonResponse({'success': True, 'action': 'unvoted', 'upvotes': suggestion.upvotes})


@login_required
@require_POST
def suggestion_comment_add(request, pk):
    """Add a comment to a suggestion"""
    suggestion = get_object_or_404(Suggestion, pk=pk)

    form = SuggestionCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.suggestion = suggestion
        comment.user = request.user
        comment.save()

        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Failed to add comment. Please try again.')

    return redirect('suggestions:suggestion_detail', pk=pk)


# ============================================================================
# ADMIN/MANAGEMENT VIEWS
# ============================================================================

@login_required
@permission_required('suggestions.can_manage_suggestions', raise_exception=True)
def admin_suggestion_list(request):
    """Admin view for managing all suggestions"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    type_filter = request.GET.get('suggestion_type', '')
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('search', '')

    # Base queryset
    suggestions = Suggestion.objects.select_related(
        'employee', 'category', 'assigned_to'
    )

    # Apply filters
    if status_filter:
        suggestions = suggestions.filter(status=status_filter)

    if type_filter:
        suggestions = suggestions.filter(suggestion_type=type_filter)

    if priority_filter:
        suggestions = suggestions.filter(priority=priority_filter)

    if search_query:
        suggestions = suggestions.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query)
        )

    # Order by priority and date
    suggestions = suggestions.order_by('-priority', '-submitted_date')

    # Pagination
    paginator = Paginator(suggestions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    stats = {
        'total': Suggestion.objects.count(),
        'submitted': Suggestion.objects.filter(status='submitted').count(),
        'under_review': Suggestion.objects.filter(status='under_review').count(),
        'approved': Suggestion.objects.filter(status='approved').count(),
        'implemented': Suggestion.objects.filter(status='implemented').count(),
        'overdue': Suggestion.objects.filter(status='submitted', submitted_date__lt=timezone.now() - timezone.timedelta(days=30)).count(),
    }

    context = {
        'page_obj': page_obj,
        'stats': stats,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'priority_filter': priority_filter,
        'search_query': search_query,
        'status_choices': Suggestion.STATUS_CHOICES,
        'type_choices': Suggestion.TYPE_CHOICES,
        'priority_choices': Suggestion.PRIORITY_CHOICES,
    }

    return render(request, 'suggestions/admin_suggestion_list.html', context)


@login_required
@permission_required('suggestions.can_respond_to_suggestions', raise_exception=True)
def admin_suggestion_respond(request, pk):
    """Admin view for responding to a suggestion"""
    suggestion = get_object_or_404(Suggestion, pk=pk)

    if request.method == 'POST':
        form = SuggestionResponseForm(request.POST, instance=suggestion)
        if form.is_valid():
            old_status = suggestion.status
            suggestion = form.save(commit=False)

            # Set response details if response is provided
            if suggestion.response and not suggestion.response_by:
                suggestion.response_by = request.user
                suggestion.response_date = timezone.now()

            # Update reviewed date if moving from submitted
            if old_status == 'submitted' and suggestion.status != 'submitted':
                suggestion.reviewed_date = timezone.now()

            # Update closed date if closing
            if suggestion.status in ['closed', 'rejected'] and not suggestion.closed_date:
                suggestion.closed_date = timezone.now()

            suggestion.save()

            # Log status change
            if old_status != suggestion.status:
                SuggestionStatusHistory.objects.create(
                    suggestion=suggestion,
                    old_status=old_status,
                    new_status=suggestion.status,
                    changed_by=request.user
                )

            messages.success(request, 'Response saved successfully!')
            return redirect('suggestions:admin_suggestion_list')
    else:
        form = SuggestionResponseForm(instance=suggestion)

    context = {
        'suggestion': suggestion,
        'form': form,
    }

    return render(request, 'suggestions/admin_suggestion_respond.html', context)
