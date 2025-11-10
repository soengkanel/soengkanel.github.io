from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import Announcement, AnnouncementRead, AnnouncementComment
from .forms import AnnouncementForm, AnnouncementCommentForm, AnnouncementFilterForm


# Helper decorator for staff-only views
def staff_required(function=None, redirect_url='/employee/'):
    """Decorator to restrict access to staff and superuser only"""
    actual_decorator = user_passes_test(
        lambda u: u.is_staff or u.is_superuser,
        login_url=redirect_url
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


# ============================================================================
# EMPLOYEE VIEWS
# ============================================================================

@login_required
def announcement_list(request):
    """List all announcements for employees"""
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    # Get filter parameters
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('search', '')

    # Get published announcements visible to this employee
    announcements = Announcement.objects.filter(
        is_active=True,
        publish_date__lte=timezone.now()
    ).filter(
        Q(expiry_date__isnull=True) | Q(expiry_date__gt=timezone.now())
    )

    # Filter by target audience
    announcements = announcements.filter(
        Q(target_audience='all') |
        Q(target_audience='department', target_departments=employee.department)
    ).distinct()

    # Apply filters
    if priority_filter:
        announcements = announcements.filter(priority=priority_filter)

    if search_query:
        announcements = announcements.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(summary__icontains=search_query)
        )

    # Get read status for current employee
    read_announcement_ids = AnnouncementRead.objects.filter(
        employee=employee
    ).values_list('announcement_id', flat=True)

    # Mark announcements as read or unread
    for announcement in announcements:
        announcement.is_read = announcement.id in read_announcement_ids

    # Pagination
    paginator = Paginator(announcements, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_announcements = announcements.count()
    unread_count = announcements.exclude(id__in=read_announcement_ids).count()
    urgent_count = announcements.filter(priority='urgent').count()

    context = {
        'employee': employee,
        'page_obj': page_obj,
        'total_announcements': total_announcements,
        'unread_count': unread_count,
        'urgent_count': urgent_count,
        'priority_filter': priority_filter,
        'search_query': search_query,
        'filter_form': AnnouncementFilterForm(initial={
            'priority': priority_filter,
            'search': search_query
        }),
    }

    return render(request, 'announcements/announcement_list.html', context)


@login_required
def announcement_detail(request, pk):
    """View detailed announcement"""
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    announcement = get_object_or_404(Announcement, pk=pk)

    # Check if employee should have access
    if not announcement.is_visible_to_employee(employee):
        messages.error(request, 'You do not have access to this announcement.')
        return redirect('announcements:announcement_list')

    # Mark as read
    read_record, created = AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        employee=employee
    )

    # Increment view count only on first read
    if created:
        announcement.view_count += 1
        announcement.save(update_fields=['view_count'])

    # Get comments
    comments = announcement.comments.select_related('employee').order_by('created_at')

    # Comment form
    comment_form = AnnouncementCommentForm()

    context = {
        'employee': employee,
        'announcement': announcement,
        'read_record': read_record,
        'comments': comments,
        'comment_form': comment_form,
        'total_reads': announcement.reads.count(),
        'total_acknowledged': announcement.reads.filter(acknowledged=True).count(),
    }

    return render(request, 'announcements/announcement_detail.html', context)


@login_required
@require_POST
def announcement_acknowledge(request, pk):
    """Acknowledge reading an announcement"""
    try:
        employee = request.user.employee
    except:
        return JsonResponse({'success': False, 'error': 'Employee profile not found'}, status=403)

    announcement = get_object_or_404(Announcement, pk=pk)

    # Get or create read record
    read_record, created = AnnouncementRead.objects.get_or_create(
        announcement=announcement,
        employee=employee
    )

    # Mark as acknowledged
    if not read_record.acknowledged:
        read_record.acknowledged = True
        read_record.acknowledged_at = timezone.now()
        read_record.save()
        return JsonResponse({'success': True, 'message': 'Announcement acknowledged'})
    else:
        return JsonResponse({'success': True, 'message': 'Already acknowledged'})


@login_required
@require_POST
def announcement_comment_add(request, pk):
    """Add a comment to an announcement"""
    try:
        employee = request.user.employee
    except:
        messages.error(request, 'Employee profile not found.')
        return redirect('employee_portal:dashboard')

    announcement = get_object_or_404(Announcement, pk=pk)

    form = AnnouncementCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.announcement = announcement
        comment.employee = employee
        comment.save()
        messages.success(request, 'Comment added successfully!')
    else:
        messages.error(request, 'Failed to add comment.')

    return redirect('announcements:announcement_detail', pk=pk)


# ============================================================================
# STAFF/ADMIN VIEWS
# ============================================================================

@login_required
@staff_required
def announcement_manage_list(request):
    """List all announcements for management"""
    # Get filter parameters
    priority_filter = request.GET.get('priority', '')
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')

    # Base queryset
    announcements = Announcement.objects.annotate(
        read_count=Count('reads'),
        comment_count=Count('comments')
    ).select_related('created_by')

    # Apply filters
    if priority_filter:
        announcements = announcements.filter(priority=priority_filter)

    if status_filter == 'active':
        announcements = announcements.filter(is_active=True)
    elif status_filter == 'inactive':
        announcements = announcements.filter(is_active=False)
    elif status_filter == 'expired':
        announcements = announcements.filter(expiry_date__lt=timezone.now())

    if search_query:
        announcements = announcements.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(announcements, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Statistics
    total_announcements = Announcement.objects.count()
    active_count = Announcement.objects.filter(is_active=True).count()
    expired_count = Announcement.objects.filter(expiry_date__lt=timezone.now()).count()

    context = {
        'page_obj': page_obj,
        'total_announcements': total_announcements,
        'active_count': active_count,
        'expired_count': expired_count,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'search_query': search_query,
    }

    return render(request, 'announcements/manage_list.html', context)


@login_required
@staff_required
def announcement_create(request):
    """Create a new announcement"""
    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.created_by = request.user
            announcement.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Announcement created successfully!')
            return redirect('announcements:announcement_manage_list')
    else:
        form = AnnouncementForm()

    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'announcements/announcement_form.html', context)


@login_required
@staff_required
def announcement_edit(request, pk):
    """Edit an existing announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)

    if request.method == 'POST':
        form = AnnouncementForm(request.POST, request.FILES, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('announcements:announcement_manage_list')
    else:
        form = AnnouncementForm(instance=announcement)

    context = {
        'form': form,
        'announcement': announcement,
        'action': 'Edit',
    }
    return render(request, 'announcements/announcement_form.html', context)


@login_required
@staff_required
@require_POST
def announcement_delete(request, pk):
    """Delete an announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)
    announcement.delete()
    messages.success(request, 'Announcement deleted successfully!')
    return redirect('announcements:announcement_manage_list')


@login_required
@staff_required
def announcement_analytics(request, pk):
    """View analytics for an announcement"""
    announcement = get_object_or_404(Announcement, pk=pk)

    # Get read statistics
    reads = announcement.reads.select_related('employee').order_by('-read_at')
    total_reads = reads.count()
    acknowledged_count = reads.filter(acknowledged=True).count()
    acknowledgment_rate = (acknowledged_count / total_reads * 100) if total_reads > 0 else 0

    # Get comments
    comments = announcement.comments.select_related('employee').order_by('-created_at')

    context = {
        'announcement': announcement,
        'reads': reads,
        'total_reads': total_reads,
        'acknowledged_count': acknowledged_count,
        'acknowledgment_rate': acknowledgment_rate,
        'comments': comments,
    }

    return render(request, 'announcements/announcement_analytics.html', context)
