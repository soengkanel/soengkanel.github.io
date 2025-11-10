from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from hr.models import Employee, Department


class SuggestionCategory(models.Model):
    """Categories for organizing suggestions"""
    name = models.CharField(_('Category Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    icon = models.CharField(_('Icon Class'), max_length=50, blank=True, help_text=_('Bootstrap icon class (e.g., bi-lightbulb)'))
    color = models.CharField(_('Color'), max_length=20, default='primary', help_text=_('Bootstrap color class'))
    is_active = models.BooleanField(_('Active'), default=True)
    order = models.IntegerField(_('Display Order'), default=0)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Suggestion Category')
        verbose_name_plural = _('Suggestion Categories')
        ordering = ['order', 'name']


class Suggestion(models.Model):
    """Employee suggestions and feedback"""
    STATUS_CHOICES = [
        ('submitted', _('Submitted')),
        ('under_review', _('Under Review')),
        ('approved', _('Approved')),
        ('implemented', _('Implemented')),
        ('rejected', _('Rejected')),
        ('closed', _('Closed')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]

    TYPE_CHOICES = [
        ('suggestion', _('Suggestion')),
        ('feedback', _('Feedback')),
        ('complaint', _('Complaint')),
        ('appreciation', _('Appreciation')),
        ('idea', _('Idea/Innovation')),
    ]

    # Basic Information
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='suggestions',
        verbose_name=_('Employee')
    )
    title = models.CharField(_('Title'), max_length=200)
    category = models.ForeignKey(
        SuggestionCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suggestions',
        verbose_name=_('Category')
    )
    suggestion_type = models.CharField(
        _('Type'),
        max_length=20,
        choices=TYPE_CHOICES,
        default='suggestion'
    )

    # Content
    description = models.TextField(_('Description/Details'))
    expected_outcome = models.TextField(
        _('Expected Outcome/Benefit'),
        blank=True,
        help_text=_('What positive changes do you expect from this suggestion?')
    )
    affected_department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='suggestions',
        verbose_name=_('Affected Department')
    )

    # Attachments
    attachment = models.FileField(
        _('Attachment'),
        upload_to='suggestions/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Supporting documents, images, etc.')
    )

    # Status & Priority
    status = models.CharField(
        _('Status'),
        max_length=20,
        choices=STATUS_CHOICES,
        default='submitted'
    )
    priority = models.CharField(
        _('Priority'),
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium'
    )

    # Privacy
    is_anonymous = models.BooleanField(
        _('Submit Anonymously'),
        default=False,
        help_text=_('Your identity will be hidden from other employees')
    )

    # Management Response
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_suggestions',
        verbose_name=_('Assigned To')
    )
    response = models.TextField(_('Management Response'), blank=True)
    response_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responded_suggestions',
        verbose_name=_('Response By')
    )
    response_date = models.DateTimeField(_('Response Date'), null=True, blank=True)

    # Implementation Details
    implementation_notes = models.TextField(_('Implementation Notes'), blank=True)
    implementation_date = models.DateField(_('Implementation Date'), null=True, blank=True)
    estimated_cost = models.DecimalField(
        _('Estimated Cost'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    actual_cost = models.DecimalField(
        _('Actual Cost'),
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Ratings & Metrics
    rating = models.IntegerField(
        _('Rating'),
        null=True,
        blank=True,
        help_text=_('Employee satisfaction with the response (1-5)')
    )
    upvotes = models.IntegerField(_('Upvotes'), default=0)
    views = models.IntegerField(_('Views'), default=0)

    # Timestamps
    submitted_date = models.DateTimeField(_('Submitted Date'), default=timezone.now)
    reviewed_date = models.DateTimeField(_('Reviewed Date'), null=True, blank=True)
    closed_date = models.DateTimeField(_('Closed Date'), null=True, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.employee.get_full_name()}"

    @property
    def days_open(self):
        """Calculate how many days the suggestion has been open"""
        if self.status in ['closed', 'implemented']:
            end_date = self.closed_date or timezone.now()
        else:
            end_date = timezone.now()
        return (end_date - self.submitted_date).days

    @property
    def is_overdue(self):
        """Check if suggestion is overdue (more than 30 days without response)"""
        if self.status == 'submitted' and not self.response:
            return self.days_open > 30
        return False

    class Meta:
        verbose_name = _('Suggestion')
        verbose_name_plural = _('Suggestions')
        ordering = ['-submitted_date']
        permissions = [
            ('can_manage_suggestions', 'Can manage all suggestions'),
            ('can_respond_to_suggestions', 'Can respond to suggestions'),
        ]


class SuggestionComment(models.Model):
    """Comments/discussion on suggestions"""
    suggestion = models.ForeignKey(
        Suggestion,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Suggestion')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='suggestion_comments',
        verbose_name=_('User')
    )
    comment = models.TextField(_('Comment'))
    is_internal = models.BooleanField(
        _('Internal Note'),
        default=False,
        help_text=_('Only visible to management')
    )

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.suggestion.title}"

    class Meta:
        verbose_name = _('Suggestion Comment')
        verbose_name_plural = _('Suggestion Comments')
        ordering = ['created_at']


class SuggestionVote(models.Model):
    """Track employee votes/support for suggestions"""
    suggestion = models.ForeignKey(
        Suggestion,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name=_('Suggestion')
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='suggestion_votes',
        verbose_name=_('Employee')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    def __str__(self):
        return f"{self.employee.get_full_name()} voted for {self.suggestion.title}"

    class Meta:
        verbose_name = _('Suggestion Vote')
        verbose_name_plural = _('Suggestion Votes')
        unique_together = [['suggestion', 'employee']]
        ordering = ['-created_at']


class SuggestionStatusHistory(models.Model):
    """Track status changes for suggestions"""
    suggestion = models.ForeignKey(
        Suggestion,
        on_delete=models.CASCADE,
        related_name='status_history',
        verbose_name=_('Suggestion')
    )
    old_status = models.CharField(_('Old Status'), max_length=20)
    new_status = models.CharField(_('New Status'), max_length=20)
    changed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Changed By')
    )
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    def __str__(self):
        return f"{self.suggestion.title}: {self.old_status} -> {self.new_status}"

    class Meta:
        verbose_name = _('Status History')
        verbose_name_plural = _('Status Histories')
        ordering = ['-created_at']
