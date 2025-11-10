from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from hr.models import Department, Position, Employee
from datetime import date


class JobPosting(models.Model):
    """Job posting/vacancy model"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('open', _('Open')),
        ('on_hold', _('On Hold')),
        ('filled', _('Filled')),
        ('cancelled', _('Cancelled')),
    ]

    title = models.CharField(_('Job Title'), max_length=200)
    department = models.ForeignKey(Department, on_delete=models.CASCADE,
                                 related_name='job_postings', verbose_name=_('Department'))
    position = models.ForeignKey(Position, on_delete=models.CASCADE,
                               related_name='job_postings', verbose_name=_('Position'))
    description = models.TextField(_('Job Description'))
    requirements = models.TextField(_('Requirements'))
    responsibilities = models.TextField(_('Responsibilities'), blank=True)
    qualifications = models.TextField(_('Qualifications'), blank=True)
    salary_range_min = models.DecimalField(_('Salary Range Min'), max_digits=12, decimal_places=2, null=True, blank=True)
    salary_range_max = models.DecimalField(_('Salary Range Max'), max_digits=12, decimal_places=2, null=True, blank=True)
    employment_type = models.CharField(_('Employment Type'), max_length=50, default='Full-time')
    vacancies = models.PositiveIntegerField(_('Number of Vacancies'), default=1)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    posted_date = models.DateField(_('Posted Date'), null=True, blank=True)
    closing_date = models.DateField(_('Closing Date'), null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  related_name='created_jobs', verbose_name=_('Created By'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.department}"

    @property
    def is_open(self):
        """Check if job is still accepting applications"""
        if self.status != 'open':
            return False
        if self.closing_date and self.closing_date < date.today():
            return False
        return True

    @property
    def applications_count(self):
        return self.applications.count()

    @property
    def hired_count(self):
        return self.applications.filter(application_status='hired').count()

    class Meta:
        verbose_name = _('Job Posting')
        verbose_name_plural = _('Job Postings')
        ordering = ['-posted_date', '-created_at']


class Candidate(models.Model):
    """Candidate/Applicant model with comprehensive status tracking (SINGLE SOURCE OF TRUTH)"""

    # SINGLE SOURCE OF TRUTH - Application Status
    APPLICATION_STATUS_CHOICES = [
        # Initial Stage
        ('applied', _('Applied')),
        ('screening', _('Under Screening')),

        # Interview Stages
        ('interview_scheduled', _('Interview Scheduled')),
        ('interviewing', _('In Interview Process')),
        ('assessment', _('Assessment/Testing')),

        # Decision Stage
        ('offer_pending', _('Offer Pending Approval')),
        ('offer_extended', _('Offer Extended')),
        ('offer_accepted', _('Offer Accepted')),
        ('offer_rejected', _('Offer Rejected by Candidate')),

        # Final Outcomes
        ('hired', _('Hired')),
        ('rejected', _('Rejected')),
        ('withdrawn', _('Withdrawn')),
        ('on_hold', _('On Hold')),
    ]

    # Personal Information
    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    email = models.EmailField(_('Email'), unique=True)
    phone = models.CharField(_('Phone'), max_length=20)
    address = models.TextField(_('Address'), blank=True)

    # Application Details
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE,
                                   related_name='applications', verbose_name=_('Job Posting'))

    # SINGLE SOURCE OF TRUTH
    application_status = models.CharField(
        _('Application Status'),
        max_length=30,
        choices=APPLICATION_STATUS_CHOICES,
        default='applied'
    )

    # Documents
    resume = models.FileField(_('Resume'), upload_to='recruitment/resumes/', null=True, blank=True)
    cover_letter = models.TextField(_('Cover Letter'), blank=True)

    # Additional Info
    expected_salary = models.DecimalField(_('Expected Salary'), max_digits=12, decimal_places=2, null=True, blank=True)
    notice_period = models.CharField(_('Notice Period'), max_length=100, blank=True)
    availability_date = models.DateField(_('Availability Date'), null=True, blank=True)

    # Screening & Review
    notes = models.TextField(_('Internal Notes'), blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='reviewed_candidates', verbose_name=_('Reviewed By'))
    reviewed_at = models.DateTimeField(_('Reviewed At'), null=True, blank=True)

    # References
    reference_check_status = models.CharField(_('Reference Check'), max_length=50, blank=True)
    background_check_status = models.CharField(_('Background Check'), max_length=50, blank=True)

    # Hiring Details (if hired)
    hired_as_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='recruitment_source', verbose_name=_('Employee Record'))
    hired_date = models.DateField(_('Hired Date'), null=True, blank=True)

    # Rejection Details
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)
    rejected_at = models.DateTimeField(_('Rejected At'), null=True, blank=True)

    # Timestamps
    applied_date = models.DateTimeField(_('Applied Date'), default=timezone.now)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.job_posting.title}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self):
        """Check if candidate is still in active recruitment process"""
        return self.application_status not in ['hired', 'rejected', 'withdrawn', 'offer_rejected']

    class Meta:
        verbose_name = _('Candidate')
        verbose_name_plural = _('Candidates')
        ordering = ['-applied_date']
        unique_together = ['email', 'job_posting']


class Interview(models.Model):
    """Interview tracking model - Auto-managed based on Candidate status"""
    TYPE_CHOICES = [
        ('phone_screening', _('Phone Screening')),
        ('technical', _('Technical Interview')),
        ('hr', _('HR Interview')),
        ('manager', _('Manager Interview')),
        ('panel', _('Panel Interview')),
        ('final', _('Final Interview')),
    ]

    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('no_show', _('No Show')),
        ('rescheduled', _('Rescheduled')),
    ]

    RATING_CHOICES = [
        (1, _('Poor')),
        (2, _('Below Average')),
        (3, _('Average')),
        (4, _('Good')),
        (5, _('Excellent')),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,
                                 related_name='interviews', verbose_name=_('Candidate'))
    interview_type = models.CharField(_('Interview Type'), max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Scheduling
    scheduled_date = models.DateTimeField(_('Scheduled Date'))
    duration_minutes = models.PositiveIntegerField(_('Duration (minutes)'), default=60)
    location = models.CharField(_('Location'), max_length=200, blank=True)
    meeting_link = models.URLField(_('Meeting Link'), blank=True)

    # Interviewers
    interviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='conducted_interviews', verbose_name=_('Interviewer'))
    panel_members = models.ManyToManyField(User, blank=True,
                                          related_name='panel_interviews', verbose_name=_('Panel Members'))

    # Feedback
    feedback = models.TextField(_('Feedback'), blank=True)
    rating = models.PositiveSmallIntegerField(_('Rating'), choices=RATING_CHOICES, null=True, blank=True)
    strengths = models.TextField(_('Strengths'), blank=True)
    weaknesses = models.TextField(_('Weaknesses'), blank=True)
    recommendation = models.CharField(_('Recommendation'), max_length=100, blank=True)

    # Timestamps
    completed_at = models.DateTimeField(_('Completed At'), null=True, blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.candidate.full_name} - {self.get_interview_type_display()} ({self.scheduled_date.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = _('Interview')
        verbose_name_plural = _('Interviews')
        ordering = ['-scheduled_date']


class Assessment(models.Model):
    """Assessment/Test tracking model"""
    TYPE_CHOICES = [
        ('technical', _('Technical Test')),
        ('aptitude', _('Aptitude Test')),
        ('personality', _('Personality Assessment')),
        ('skill', _('Skill Assessment')),
        ('case_study', _('Case Study')),
        ('coding', _('Coding Challenge')),
    ]

    STATUS_CHOICES = [
        ('assigned', _('Assigned')),
        ('in_progress', _('In Progress')),
        ('submitted', _('Submitted')),
        ('evaluated', _('Evaluated')),
        ('expired', _('Expired')),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,
                                 related_name='assessments', verbose_name=_('Candidate'))
    assessment_type = models.CharField(_('Assessment Type'), max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='assigned')

    # Assessment Details
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'))
    instructions = models.TextField(_('Instructions'), blank=True)

    # Timing
    assigned_date = models.DateTimeField(_('Assigned Date'), default=timezone.now)
    due_date = models.DateTimeField(_('Due Date'), null=True, blank=True)
    submitted_date = models.DateTimeField(_('Submitted Date'), null=True, blank=True)

    # Results
    file_submission = models.FileField(_('Submission File'), upload_to='recruitment/assessments/', null=True, blank=True)
    score = models.DecimalField(_('Score'), max_digits=5, decimal_places=2, null=True, blank=True)
    max_score = models.DecimalField(_('Maximum Score'), max_digits=5, decimal_places=2, default=100)
    evaluator_notes = models.TextField(_('Evaluator Notes'), blank=True)
    evaluated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='evaluated_assessments', verbose_name=_('Evaluated By'))
    evaluated_at = models.DateTimeField(_('Evaluated At'), null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.candidate.full_name} - {self.title}"

    @property
    def percentage_score(self):
        if self.score and self.max_score:
            return (self.score / self.max_score) * 100
        return None

    class Meta:
        verbose_name = _('Assessment')
        verbose_name_plural = _('Assessments')
        ordering = ['-assigned_date']


class JobOffer(models.Model):
    """Job offer model"""
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending_approval', _('Pending Approval')),
        ('approved', _('Approved')),
        ('sent', _('Sent to Candidate')),
        ('accepted', _('Accepted')),
        ('rejected', _('Rejected')),
        ('withdrawn', _('Withdrawn')),
        ('expired', _('Expired')),
    ]

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,
                                 related_name='offers', verbose_name=_('Candidate'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Offer Details
    position_offered = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True,
                                        verbose_name=_('Position Offered'))
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True,
                                  verbose_name=_('Department'))

    # Compensation
    salary = models.DecimalField(_('Salary'), max_digits=12, decimal_places=2)
    currency = models.CharField(_('Currency'), max_length=10, default='USD')
    bonus = models.DecimalField(_('Bonus'), max_digits=12, decimal_places=2, null=True, blank=True)
    benefits = models.TextField(_('Benefits'), blank=True)

    # Employment Details
    employment_type = models.CharField(_('Employment Type'), max_length=50, default='Full-time')
    start_date = models.DateField(_('Proposed Start Date'))
    probation_period_months = models.PositiveIntegerField(_('Probation Period (Months)'), default=3)

    # Offer Management
    offer_letter = models.FileField(_('Offer Letter'), upload_to='recruitment/offers/', null=True, blank=True)
    offer_sent_date = models.DateTimeField(_('Offer Sent Date'), null=True, blank=True)
    offer_expiry_date = models.DateField(_('Offer Expiry Date'), null=True, blank=True)

    # Response
    candidate_response = models.TextField(_('Candidate Response'), blank=True)
    response_date = models.DateTimeField(_('Response Date'), null=True, blank=True)

    # Approval
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='approved_offers', verbose_name=_('Approved By'))
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)

    # Notes
    notes = models.TextField(_('Internal Notes'), blank=True)

    # Timestamps
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  related_name='created_offers', verbose_name=_('Created By'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"Offer for {self.candidate.full_name} - {self.position_offered}"

    class Meta:
        verbose_name = _('Job Offer')
        verbose_name_plural = _('Job Offers')
        ordering = ['-created_at']


class CandidateStatusHistory(models.Model):
    """Track all status changes for audit trail"""
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,
                                 related_name='status_history', verbose_name=_('Candidate'))
    old_status = models.CharField(_('Old Status'), max_length=30, blank=True)
    new_status = models.CharField(_('New Status'), max_length=30)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  verbose_name=_('Changed By'))
    reason = models.TextField(_('Reason'), blank=True)
    timestamp = models.DateTimeField(_('Timestamp'), auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.full_name}: {self.old_status} → {self.new_status}"

    class Meta:
        verbose_name = _('Status History')
        verbose_name_plural = _('Status Histories')
        ordering = ['-timestamp']


# Legacy model for backward compatibility - will be deprecated
class Application(models.Model):
    """DEPRECATED: Use Candidate model instead. Kept for migration compatibility."""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('reviewing', _('Under Review')),
        ('shortlisted', _('Shortlisted')),
        ('interview', _('Interview Scheduled')),
        ('rejected', _('Rejected')),
        ('accepted', _('Accepted')),
    ]

    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE,
                                   related_name='legacy_applications', verbose_name=_('Job Posting'))
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE,
                                 related_name='legacy_applications', verbose_name=_('Candidate'))
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(_('Applied Date'), default=timezone.now)
    notes = models.TextField(_('Notes'), blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='legacy_reviewed_applications', verbose_name=_('Reviewed By'))
    reviewed_at = models.DateTimeField(_('Reviewed At'), null=True, blank=True)

    def __str__(self):
        return f"{self.candidate} - {self.job_posting.title}"

    class Meta:
        verbose_name = _('Application (Legacy)')
        verbose_name_plural = _('Applications (Legacy)')
        ordering = ['-applied_date']
