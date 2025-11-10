from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, datetime, timedelta

from .models import (
    JobPosting, Candidate, Interview, Assessment,
    JobOffer, CandidateStatusHistory
)
from hr.models import Department, Position, Employee


# ==================== DASHBOARD ====================

@login_required
def recruitment_dashboard(request):
    """Recruitment dashboard with statistics and pipeline visualization."""

    # Job Posting Stats
    job_stats = {
        'total': JobPosting.objects.count(),
        'open': JobPosting.objects.filter(status='open').count(),
        'draft': JobPosting.objects.filter(status='draft').count(),
        'filled': JobPosting.objects.filter(status='filled').count(),
    }

    # Candidate Stats by Status (SINGLE SOURCE OF TRUTH)
    total_candidates = Candidate.objects.count()
    candidate_stats = {
        'total': total_candidates,
        'applied': Candidate.objects.filter(application_status='applied').count(),
        'screening': Candidate.objects.filter(application_status='screening').count(),
        'interviewing': Candidate.objects.filter(application_status__in=['interview_scheduled', 'interviewing']).count(),
        'assessment': Candidate.objects.filter(application_status='assessment').count(),
        'offer_stage': Candidate.objects.filter(application_status__in=['offer_pending', 'offer_extended', 'offer_accepted']).count(),
        'hired': Candidate.objects.filter(application_status='hired').count(),
        'rejected': Candidate.objects.filter(application_status='rejected').count(),
    }

    # Recent Activities
    recent_candidates = Candidate.objects.select_related('job_posting').order_by('-applied_date')[:5]
    upcoming_interviews = Interview.objects.filter(
        status='scheduled',
        scheduled_date__gte=timezone.now()
    ).select_related('candidate').order_by('scheduled_date')[:5]

    # Pending Actions
    pending_offers = JobOffer.objects.filter(status__in=['draft', 'pending_approval']).count()
    pending_assessments = Assessment.objects.filter(status='assigned').count()

    context = {
        'job_stats': job_stats,
        'candidate_stats': candidate_stats,
        'recent_candidates': recent_candidates,
        'upcoming_interviews': upcoming_interviews,
        'pending_offers': pending_offers,
        'pending_assessments': pending_assessments,
    }

    return render(request, 'recruitment/dashboard.html', context)


# ==================== JOB POSTING VIEWS ====================

@login_required
@permission_required('recruitment.view_jobposting', raise_exception=True)
def job_list(request):
    """List all job postings with filters."""
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')

    jobs = JobPosting.objects.select_related('department', 'position', 'created_by').annotate(
        total_applications=Count('applications')
    )

    if status_filter:
        jobs = jobs.filter(status=status_filter)

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    if department_filter:
        jobs = jobs.filter(department_id=department_filter)

    jobs = jobs.order_by('-posted_date', '-created_at')

    # Pagination
    paginator = Paginator(jobs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    departments = Department.objects.all()

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'search_query': search_query,
        'department_filter': department_filter,
        'departments': departments,
    }
    return render(request, 'recruitment/job_list.html', context)


@login_required
@permission_required('recruitment.view_jobposting', raise_exception=True)
def job_detail(request, pk):
    """View job posting details with candidates."""
    job = get_object_or_404(JobPosting, pk=pk)
    candidates = job.applications.select_related('job_posting').order_by('-applied_date')

    # Group candidates by status
    candidates_by_status = {}
    for candidate in candidates:
        status = candidate.application_status
        if status not in candidates_by_status:
            candidates_by_status[status] = []
        candidates_by_status[status].append(candidate)

    context = {
        'job': job,
        'candidates': candidates,
        'candidates_by_status': candidates_by_status,
    }
    return render(request, 'recruitment/job_detail.html', context)


@login_required
@permission_required('recruitment.add_jobposting', raise_exception=True)
def job_create(request):
    """Create a new job posting."""
    if request.method == 'POST':
        title = request.POST.get('title')
        department_id = request.POST.get('department')
        position_id = request.POST.get('position')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        responsibilities = request.POST.get('responsibilities', '')
        qualifications = request.POST.get('qualifications', '')
        employment_type = request.POST.get('employment_type', 'Full-time')
        vacancies = request.POST.get('vacancies', 1)
        salary_min = request.POST.get('salary_range_min')
        salary_max = request.POST.get('salary_range_max')
        status = request.POST.get('status', 'draft')
        posted_date = request.POST.get('posted_date')
        closing_date = request.POST.get('closing_date')

        try:
            job = JobPosting.objects.create(
                title=title,
                department_id=department_id,
                position_id=position_id,
                description=description,
                requirements=requirements,
                responsibilities=responsibilities,
                qualifications=qualifications,
                employment_type=employment_type,
                vacancies=int(vacancies),
                salary_range_min=salary_min if salary_min else None,
                salary_range_max=salary_max if salary_max else None,
                status=status,
                posted_date=posted_date if posted_date else None,
                closing_date=closing_date if closing_date else None,
                created_by=request.user
            )
            messages.success(request, _('Job posting created successfully!'))
            return redirect('recruitment:job_detail', pk=job.pk)
        except Exception as e:
            messages.error(request, f'Error creating job posting: {str(e)}')

    departments = Department.objects.all()
    positions = Position.objects.all()

    context = {
        'departments': departments,
        'positions': positions,
        'title': 'Create Job Posting',
    }
    return render(request, 'recruitment/job_form.html', context)


@login_required
@permission_required('recruitment.change_jobposting', raise_exception=True)
def job_update(request, pk):
    """Update job posting."""
    job = get_object_or_404(JobPosting, pk=pk)

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.department_id = request.POST.get('department')
        job.position_id = request.POST.get('position')
        job.description = request.POST.get('description')
        job.requirements = request.POST.get('requirements')
        job.responsibilities = request.POST.get('responsibilities', '')
        job.qualifications = request.POST.get('qualifications', '')
        job.employment_type = request.POST.get('employment_type', 'Full-time')
        job.vacancies = int(request.POST.get('vacancies', 1))

        salary_min = request.POST.get('salary_range_min')
        salary_max = request.POST.get('salary_range_max')
        job.salary_range_min = salary_min if salary_min else None
        job.salary_range_max = salary_max if salary_max else None

        job.status = request.POST.get('status', 'draft')

        posted_date = request.POST.get('posted_date')
        closing_date = request.POST.get('closing_date')
        job.posted_date = posted_date if posted_date else None
        job.closing_date = closing_date if closing_date else None

        try:
            job.save()
            messages.success(request, _('Job posting updated successfully!'))
            return redirect('recruitment:job_detail', pk=job.pk)
        except Exception as e:
            messages.error(request, f'Error updating job posting: {str(e)}')

    departments = Department.objects.all()
    positions = Position.objects.all()

    context = {
        'job': job,
        'departments': departments,
        'positions': positions,
        'title': f'Update Job: {job.title}',
    }
    return render(request, 'recruitment/job_form.html', context)


# ==================== CANDIDATE VIEWS ====================

@login_required
@permission_required('recruitment.view_candidate', raise_exception=True)
def candidate_list(request):
    """List all candidates with pipeline view."""
    status_filter = request.GET.get('status', '')
    job_filter = request.GET.get('job', '')
    search_query = request.GET.get('search', '')

    candidates = Candidate.objects.select_related('job_posting').all()

    if status_filter:
        candidates = candidates.filter(application_status=status_filter)

    if job_filter:
        candidates = candidates.filter(job_posting_id=job_filter)

    if search_query:
        candidates = candidates.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    candidates = candidates.order_by('-applied_date')

    # Pagination
    paginator = Paginator(candidates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    jobs = JobPosting.objects.filter(status='open')

    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'job_filter': job_filter,
        'search_query': search_query,
        'jobs': jobs,
        'status_choices': Candidate.APPLICATION_STATUS_CHOICES,
    }
    return render(request, 'recruitment/candidate_list.html', context)


@login_required
@permission_required('recruitment.view_candidate', raise_exception=True)
def candidate_detail(request, pk):
    """View candidate details with full timeline."""
    candidate = get_object_or_404(Candidate, pk=pk)
    interviews = candidate.interviews.order_by('-scheduled_date')
    assessments = candidate.assessments.order_by('-assigned_date')
    offers = candidate.offers.order_by('-created_at')
    status_history = candidate.status_history.select_related('changed_by').order_by('-timestamp')

    context = {
        'candidate': candidate,
        'interviews': interviews,
        'assessments': assessments,
        'offers': offers,
        'status_history': status_history,
    }
    return render(request, 'recruitment/candidate_detail.html', context)


@login_required
@permission_required('recruitment.change_candidate', raise_exception=True)
def candidate_update_status(request, pk):
    """Update candidate application status (SINGLE SOURCE OF TRUTH)."""
    candidate = get_object_or_404(Candidate, pk=pk)

    if request.method == 'POST':
        old_status = candidate.application_status
        new_status = request.POST.get('application_status')
        reason = request.POST.get('reason', '')

        if new_status and new_status != old_status:
            candidate.application_status = new_status

            # Auto-update related fields based on status
            if new_status == 'rejected':
                candidate.rejected_at = timezone.now()
                candidate.rejection_reason = reason

            elif new_status == 'hired':
                candidate.hired_date = date.today()

            # Update review timestamp
            if new_status == 'screening' and not candidate.reviewed_by:
                candidate.reviewed_by = request.user
                candidate.reviewed_at = timezone.now()

            candidate.save()

            # Create status history
            CandidateStatusHistory.objects.create(
                candidate=candidate,
                old_status=old_status,
                new_status=new_status,
                changed_by=request.user,
                reason=reason
            )

            messages.success(request, _('Candidate status updated successfully!'))
            return redirect('recruitment:candidate_detail', pk=candidate.pk)

    context = {
        'candidate': candidate,
        'status_choices': Candidate.APPLICATION_STATUS_CHOICES,
    }
    return render(request, 'recruitment/candidate_update_status.html', context)


# ==================== INTERVIEW VIEWS ====================

@login_required
@permission_required('recruitment.add_interview', raise_exception=True)
def interview_schedule(request, candidate_pk):
    """Schedule an interview for a candidate."""
    candidate = get_object_or_404(Candidate, pk=candidate_pk)

    if request.method == 'POST':
        interview_type = request.POST.get('interview_type')
        scheduled_date = request.POST.get('scheduled_date')
        duration_minutes = request.POST.get('duration_minutes', 60)
        location = request.POST.get('location', '')
        meeting_link = request.POST.get('meeting_link', '')
        interviewer_id = request.POST.get('interviewer')

        try:
            interview = Interview.objects.create(
                candidate=candidate,
                interview_type=interview_type,
                scheduled_date=scheduled_date,
                duration_minutes=int(duration_minutes),
                location=location,
                meeting_link=meeting_link,
                interviewer_id=interviewer_id,
                status='scheduled'
            )

            # AUTO-UPDATE candidate status (single source of truth)
            if candidate.application_status in ['applied', 'screening']:
                candidate.application_status = 'interview_scheduled'
                candidate.save()

            messages.success(request, _('Interview scheduled successfully!'))
            return redirect('recruitment:candidate_detail', pk=candidate.pk)
        except Exception as e:
            messages.error(request, f'Error scheduling interview: {str(e)}')

    from django.contrib.auth.models import User
    interviewers = User.objects.filter(is_staff=True)

    context = {
        'candidate': candidate,
        'interviewers': interviewers,
        'interview_types': Interview.TYPE_CHOICES,
    }
    return render(request, 'recruitment/interview_schedule.html', context)


@login_required
@permission_required('recruitment.change_interview', raise_exception=True)
def interview_complete(request, pk):
    """Mark interview as completed and add feedback."""
    interview = get_object_or_404(Interview, pk=pk)

    if request.method == 'POST':
        interview.status = 'completed'
        interview.completed_at = timezone.now()
        interview.feedback = request.POST.get('feedback', '')
        interview.rating = request.POST.get('rating')
        interview.strengths = request.POST.get('strengths', '')
        interview.weaknesses = request.POST.get('weaknesses', '')
        interview.recommendation = request.POST.get('recommendation', '')

        interview.save()

        # AUTO-UPDATE candidate status
        candidate = interview.candidate
        pending_interviews = candidate.interviews.filter(status='scheduled').exists()

        if not pending_interviews:
            # All interviews completed
            candidate.application_status = 'interviewing'
            candidate.save()

        messages.success(request, _('Interview feedback saved successfully!'))
        return redirect('recruitment:candidate_detail', pk=interview.candidate.pk)

    context = {
        'interview': interview,
        'rating_choices': Interview.RATING_CHOICES,
    }
    return render(request, 'recruitment/interview_complete.html', context)


# ==================== OFFER VIEWS ====================

@login_required
@permission_required('recruitment.add_joboffer', raise_exception=True)
def offer_create(request, candidate_pk):
    """Create job offer for a candidate."""
    candidate = get_object_or_404(Candidate, pk=candidate_pk)

    if request.method == 'POST':
        position_id = request.POST.get('position_offered')
        department_id = request.POST.get('department')
        salary = request.POST.get('salary')
        currency = request.POST.get('currency', 'USD')
        bonus = request.POST.get('bonus')
        benefits = request.POST.get('benefits', '')
        employment_type = request.POST.get('employment_type', 'Full-time')
        start_date = request.POST.get('start_date')
        probation_period = request.POST.get('probation_period_months', 3)
        offer_expiry = request.POST.get('offer_expiry_date')
        notes = request.POST.get('notes', '')

        try:
            offer = JobOffer.objects.create(
                candidate=candidate,
                position_offered_id=position_id,
                department_id=department_id,
                salary=salary,
                currency=currency,
                bonus=bonus if bonus else None,
                benefits=benefits,
                employment_type=employment_type,
                start_date=start_date,
                probation_period_months=int(probation_period),
                offer_expiry_date=offer_expiry if offer_expiry else None,
                notes=notes,
                status='draft',
                created_by=request.user
            )

            # AUTO-UPDATE candidate status
            candidate.application_status = 'offer_pending'
            candidate.save()

            messages.success(request, _('Job offer created successfully!'))
            return redirect('recruitment:candidate_detail', pk=candidate.pk)
        except Exception as e:
            messages.error(request, f'Error creating offer: {str(e)}')

    positions = Position.objects.all()
    departments = Department.objects.all()

    context = {
        'candidate': candidate,
        'positions': positions,
        'departments': departments,
    }
    return render(request, 'recruitment/offer_form.html', context)


@login_required
@permission_required('recruitment.change_joboffer', raise_exception=True)
def offer_update_status(request, pk):
    """Update offer status and auto-update candidate status."""
    offer = get_object_or_404(JobOffer, pk=pk)

    if request.method == 'POST':
        old_status = offer.status
        new_status = request.POST.get('status')

        offer.status = new_status

        if new_status == 'sent':
            offer.offer_sent_date = timezone.now()
        elif new_status == 'accepted':
            offer.response_date = timezone.now()
            offer.candidate_response = request.POST.get('candidate_response', '')
        elif new_status == 'rejected':
            offer.response_date = timezone.now()
            offer.candidate_response = request.POST.get('candidate_response', '')

        offer.save()

        # AUTO-UPDATE candidate status (single source of truth)
        candidate = offer.candidate
        if new_status == 'sent':
            candidate.application_status = 'offer_extended'
        elif new_status == 'accepted':
            candidate.application_status = 'offer_accepted'
        elif new_status == 'rejected':
            candidate.application_status = 'offer_rejected'

        candidate.save()

        messages.success(request, _('Offer status updated successfully!'))
        return redirect('recruitment:candidate_detail', pk=candidate.pk)

    context = {
        'offer': offer,
        'status_choices': JobOffer.STATUS_CHOICES,
    }
    return render(request, 'recruitment/offer_update_status.html', context)


# ==================== HIRE CANDIDATE ====================

@login_required
@permission_required('recruitment.change_candidate', raise_exception=True)
def candidate_hire(request, pk):
    """Convert candidate to employee."""
    candidate = get_object_or_404(Candidate, pk=pk)

    if request.method == 'POST':
        # Get offer details
        offer = candidate.offers.filter(status='accepted').first()

        if not offer:
            messages.error(request, _('No accepted offer found for this candidate.'))
            return redirect('recruitment:candidate_detail', pk=candidate.pk)

        try:
            # Create Employee record
            employee = Employee.objects.create(
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                email=candidate.email.replace('ENCRYPTED:', ''),  # Remove encryption prefix if exists
                phone_number=candidate.phone,
                address=candidate.address,
                department=offer.department,
                position=offer.position_offered,
                hire_date=offer.start_date,
                employment_status='active',
                salary=offer.salary,
                # Additional fields can be added via employee update later
            )

            # Link candidate to employee
            candidate.hired_as_employee = employee
            candidate.hired_date = date.today()
            candidate.application_status = 'hired'
            candidate.save()

            # Update job posting if all vacancies filled
            job = candidate.job_posting
            hired_count = job.applications.filter(application_status='hired').count()
            if hired_count >= job.vacancies:
                job.status = 'filled'
                job.save()

            # Auto-create onboarding process if template exists
            from hr.models import OnboardingTemplate, EmployeeOnboarding, OnboardingTaskInstance
            from datetime import timedelta

            try:
                # Try to find an onboarding template for this position/department
                template = OnboardingTemplate.objects.filter(
                    is_active=True
                ).filter(
                    Q(position=employee.position) | Q(department=employee.department) | Q(position__isnull=True, department__isnull=True)
                ).first()

                if template:
                    # Create onboarding process
                    onboarding = EmployeeOnboarding.objects.create(
                        employee=employee,
                        template=template,
                        start_date=employee.hire_date,
                        status='pending',
                        created_by=request.user
                    )

                    # Create task instances from template
                    for task in template.tasks.filter(is_active=True).order_by('order'):
                        due_date = employee.hire_date + timedelta(days=task.due_after_days)
                        OnboardingTaskInstance.objects.create(
                            onboarding=onboarding,
                            task=task,
                            title=task.title,
                            description=task.description,
                            task_type=task.task_type,
                            priority=task.priority,
                            estimated_hours=task.estimated_hours,
                            due_date=due_date,
                            status='pending'
                        )

                    messages.success(request, _(f'Candidate hired successfully as Employee ID: {employee.employee_id}. Onboarding process created automatically.'))
                else:
                    messages.success(request, _(f'Candidate hired successfully as Employee ID: {employee.employee_id}'))
            except Exception as e:
                # If onboarding creation fails, just log it but don't fail the hire
                logger.warning(f'Failed to create onboarding for employee {employee.employee_id}: {str(e)}')
                messages.success(request, _(f'Candidate hired successfully as Employee ID: {employee.employee_id}'))

            return redirect('hr:employee_detail', pk=employee.pk)
        except Exception as e:
            messages.error(request, f'Error hiring candidate: {str(e)}')
            return redirect('recruitment:candidate_detail', pk=candidate.pk)

    # Get accepted offer
    offer = candidate.offers.filter(status='accepted').first()

    context = {
        'candidate': candidate,
        'offer': offer,
    }
    return render(request, 'recruitment/candidate_hire.html', context)
