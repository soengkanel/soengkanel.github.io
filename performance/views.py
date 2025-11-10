from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q, Count, Avg
from .models import PerformanceReview, Goal
from .forms import PerformanceReviewForm, GoalForm
from hr.models import Employee


@login_required
def review_list(request):
    """List all performance reviews with filters and pagination"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    period_filter = request.GET.get('period', '')

    # Base queryset
    reviews = PerformanceReview.objects.select_related('employee', 'reviewer')

    # Apply filters
    if status_filter:
        reviews = reviews.filter(status=status_filter)

    if search_query:
        reviews = reviews.filter(
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(reviewer__username__icontains=search_query)
        )

    if period_filter:
        reviews = reviews.filter(review_period=period_filter)

    # Get status counts
    all_reviews = PerformanceReview.objects.all()
    status_counts = {
        'all': all_reviews.count(),
        'draft': all_reviews.filter(status='draft').count(),
        'in_progress': all_reviews.filter(status='in_progress').count(),
        'completed': all_reviews.filter(status='completed').count(),
    }

    # Order by review date
    reviews = reviews.order_by('-review_date', '-created_at')

    # Pagination
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'period_filter': period_filter,
        'status_counts': status_counts,
    }
    return render(request, 'performance/review_list.html', context)


@login_required
def review_detail(request, pk):
    """View performance review details"""
    review = get_object_or_404(PerformanceReview, pk=pk)
    context = {
        'review': review,
    }
    return render(request, 'performance/review_detail.html', context)


@login_required
def review_create(request):
    """Create a new performance review"""
    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.reviewer = request.user
            review.save()
            messages.success(request, _('Performance review created successfully!'))
            return redirect('performance:review_list')
    else:
        form = PerformanceReviewForm()

    # Get active employees for autocomplete
    employees = Employee.objects.filter(employment_status='active').order_by('first_name', 'last_name')

    context = {
        'form': form,
        'action': 'Create',
        'employees': employees,
    }
    return render(request, 'performance/review_form.html', context)


@login_required
def review_edit(request, pk):
    """Edit an existing performance review"""
    review = get_object_or_404(PerformanceReview, pk=pk)

    if request.method == 'POST':
        form = PerformanceReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, _('Performance review updated successfully!'))
            return redirect('performance:review_list')
    else:
        form = PerformanceReviewForm(instance=review)

    # Get active employees for autocomplete
    employees = Employee.objects.filter(employment_status='active').order_by('first_name', 'last_name')

    context = {
        'form': form,
        'review': review,
        'action': 'Edit',
        'employees': employees,
        'selected_employee': review.employee,
    }
    return render(request, 'performance/review_form.html', context)


@login_required
def review_delete(request, pk):
    """Delete a performance review"""
    review = get_object_or_404(PerformanceReview, pk=pk)

    if request.method == 'POST':
        review.delete()
        messages.success(request, _('Performance review deleted successfully!'))
        return redirect('performance:review_list')

    context = {
        'review': review,
    }
    return render(request, 'performance/review_confirm_delete.html', context)


# Goal views
@login_required
def goal_list(request):
    """List all goals with filters and pagination"""
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    priority_filter = request.GET.get('priority', '')

    # Base queryset
    goals = Goal.objects.select_related('employee', 'created_by')

    # Apply filters
    if status_filter:
        goals = goals.filter(status=status_filter)

    if search_query:
        goals = goals.filter(
            Q(title__icontains=search_query) |
            Q(employee__first_name__icontains=search_query) |
            Q(employee__last_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if priority_filter:
        goals = goals.filter(priority=priority_filter)

    # Get status counts
    all_goals = Goal.objects.all()
    status_counts = {
        'all': all_goals.count(),
        'not_started': all_goals.filter(status='not_started').count(),
        'in_progress': all_goals.filter(status='in_progress').count(),
        'completed': all_goals.filter(status='completed').count(),
        'cancelled': all_goals.filter(status='cancelled').count(),
    }

    # Order by created date
    goals = goals.order_by('-created_at')

    # Pagination
    paginator = Paginator(goals, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'priority_filter': priority_filter,
        'status_counts': status_counts,
    }
    return render(request, 'performance/goal_list.html', context)


@login_required
def goal_detail(request, pk):
    """View goal details"""
    goal = get_object_or_404(Goal, pk=pk)
    context = {
        'goal': goal,
    }
    return render(request, 'performance/goal_detail.html', context)


@login_required
def goal_create(request):
    """Create a new goal"""
    if request.method == 'POST':
        form = GoalForm(request.POST)
        if form.is_valid():
            goal = form.save(commit=False)
            goal.created_by = request.user
            goal.save()
            messages.success(request, _('Goal created successfully!'))
            return redirect('performance:goal_list')
    else:
        form = GoalForm()

    # Get active employees for autocomplete
    employees = Employee.objects.filter(employment_status='active').order_by('first_name', 'last_name')

    context = {
        'form': form,
        'action': 'Create',
        'employees': employees,
    }
    return render(request, 'performance/goal_form.html', context)


@login_required
def goal_edit(request, pk):
    """Edit an existing goal"""
    goal = get_object_or_404(Goal, pk=pk)

    if request.method == 'POST':
        form = GoalForm(request.POST, instance=goal)
        if form.is_valid():
            form.save()
            messages.success(request, _('Goal updated successfully!'))
            return redirect('performance:goal_list')
    else:
        form = GoalForm(instance=goal)

    # Get active employees for autocomplete
    employees = Employee.objects.filter(employment_status='active').order_by('first_name', 'last_name')

    context = {
        'form': form,
        'goal': goal,
        'action': 'Edit',
        'employees': employees,
        'selected_employee': goal.employee,
    }
    return render(request, 'performance/goal_form.html', context)


@login_required
def goal_delete(request, pk):
    """Delete a goal"""
    goal = get_object_or_404(Goal, pk=pk)

    if request.method == 'POST':
        goal.delete()
        messages.success(request, _('Goal deleted successfully!'))
        return redirect('performance:goal_list')

    context = {
        'goal': goal,
    }
    return render(request, 'performance/goal_confirm_delete.html', context)
