from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from hr.models import Employee


class PerformanceReview(models.Model):
    """Performance review model for employee evaluations"""
    REVIEW_PERIOD_CHOICES = [
        ('quarterly', _('Quarterly')),
        ('semi_annual', _('Semi-Annual')),
        ('annual', _('Annual')),
    ]

    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
    ]

    RATING_CHOICES = [
        (1, _('Needs Improvement')),
        (2, _('Below Expectations')),
        (3, _('Meets Expectations')),
        (4, _('Exceeds Expectations')),
        (5, _('Outstanding')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name='performance_reviews', verbose_name=_('Employee'))
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                related_name='conducted_reviews', verbose_name=_('Reviewer'))
    review_period = models.CharField(_('Review Period'), max_length=20,
                                    choices=REVIEW_PERIOD_CHOICES, default='annual')
    review_date = models.DateField(_('Review Date'), default=timezone.now)
    period_start = models.DateField(_('Period Start Date'))
    period_end = models.DateField(_('Period End Date'))

    # Review ratings
    overall_rating = models.IntegerField(_('Overall Rating'),
                                        choices=RATING_CHOICES,
                                        validators=[MinValueValidator(1), MaxValueValidator(5)],
                                        null=True, blank=True)

    # Comments and feedback
    strengths = models.TextField(_('Strengths'), blank=True)
    areas_for_improvement = models.TextField(_('Areas for Improvement'), blank=True)
    goals_achieved = models.TextField(_('Goals Achieved'), blank=True)
    comments = models.TextField(_('Additional Comments'), blank=True)

    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.review_period} ({self.review_date})"

    class Meta:
        verbose_name = _('Performance Review')
        verbose_name_plural = _('Performance Reviews')
        ordering = ['-review_date', '-created_at']


class Goal(models.Model):
    """Employee goal/objective model"""
    STATUS_CHOICES = [
        ('not_started', _('Not Started')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                                 related_name='goals', verbose_name=_('Employee'))
    title = models.CharField(_('Goal Title'), max_length=200)
    description = models.TextField(_('Description'))
    priority = models.CharField(_('Priority'), max_length=10,
                               choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(_('Status'), max_length=20,
                             choices=STATUS_CHOICES, default='not_started')

    start_date = models.DateField(_('Start Date'), default=timezone.now)
    target_date = models.DateField(_('Target Date'))
    completion_date = models.DateField(_('Completion Date'), null=True, blank=True)

    progress = models.IntegerField(_('Progress (%)'),
                                  validators=[MinValueValidator(0), MaxValueValidator(100)],
                                  default=0)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                  related_name='created_goals', verbose_name=_('Created By'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.title}"

    class Meta:
        verbose_name = _('Goal')
        verbose_name_plural = _('Goals')
        ordering = ['-created_at']
