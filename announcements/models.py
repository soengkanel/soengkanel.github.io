from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from hr.models import Employee, Department


class Announcement(models.Model):
    """Company announcements for employees"""

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('normal', _('Normal')),
        ('high', _('High')),
        ('urgent', _('Urgent')),
    ]

    TARGET_AUDIENCE_CHOICES = [
        ('all', _('All Employees')),
        ('department', _('Specific Department')),
        ('role', _('Specific Role')),
    ]

    # Basic Information
    title = models.CharField(_('Title'), max_length=200)
    content = models.TextField(_('Content'))
    summary = models.CharField(
        _('Summary'),
        max_length=300,
        blank=True,
        help_text=_('Brief summary shown in lists (auto-generated if empty)')
    )

    # Priority and Visibility
    priority = models.CharField(
        _('Priority'),
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='normal'
    )
    is_active = models.BooleanField(_('Active'), default=True)
    is_pinned = models.BooleanField(
        _('Pinned'),
        default=False,
        help_text=_('Pinned announcements appear at the top')
    )

    # Targeting
    target_audience = models.CharField(
        _('Target Audience'),
        max_length=20,
        choices=TARGET_AUDIENCE_CHOICES,
        default='all'
    )
    target_departments = models.ManyToManyField(
        Department,
        blank=True,
        related_name='announcements',
        verbose_name=_('Target Departments')
    )

    # Scheduling
    publish_date = models.DateTimeField(
        _('Publish Date'),
        default=timezone.now,
        help_text=_('Announcement will be visible from this date')
    )
    expiry_date = models.DateTimeField(
        _('Expiry Date'),
        null=True,
        blank=True,
        help_text=_('Announcement will be hidden after this date')
    )

    # Attachments
    attachment = models.FileField(
        _('Attachment'),
        upload_to='announcements/%Y/%m/',
        blank=True,
        null=True,
        help_text=_('Optional file attachment (PDF, images, etc.)')
    )

    # Tracking
    require_acknowledgment = models.BooleanField(
        _('Require Acknowledgment'),
        default=False,
        help_text=_('Employees must acknowledge they have read this')
    )
    view_count = models.IntegerField(_('View Count'), default=0)

    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_announcements',
        verbose_name=_('Created By')
    )
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-is_pinned', '-publish_date']
        permissions = [
            ('can_manage_announcements', 'Can manage announcements'),
        ]

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        """Check if announcement is currently published"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.publish_date > now:
            return False
        if self.expiry_date and self.expiry_date < now:
            return False
        return True

    @property
    def is_expired(self):
        """Check if announcement has expired"""
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False

    @property
    def days_remaining(self):
        """Calculate days until expiry"""
        if self.expiry_date:
            delta = self.expiry_date - timezone.now()
            return max(0, delta.days)
        return None

    def get_summary(self):
        """Get summary or generate from content"""
        if self.summary:
            return self.summary
        # Auto-generate summary from first 150 characters
        return self.content[:150] + '...' if len(self.content) > 150 else self.content

    def is_visible_to_employee(self, employee):
        """Check if this announcement should be visible to a specific employee"""
        if not self.is_published:
            return False

        if self.target_audience == 'all':
            return True
        elif self.target_audience == 'department':
            return employee.department in self.target_departments.all()

        return True


class AnnouncementRead(models.Model):
    """Track which employees have read which announcements"""

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='reads',
        verbose_name=_('Announcement')
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='announcement_reads',
        verbose_name=_('Employee')
    )
    read_at = models.DateTimeField(_('Read At'), auto_now_add=True)
    acknowledged = models.BooleanField(_('Acknowledged'), default=False)
    acknowledged_at = models.DateTimeField(_('Acknowledged At'), null=True, blank=True)

    class Meta:
        verbose_name = _('Announcement Read')
        verbose_name_plural = _('Announcement Reads')
        unique_together = [['announcement', 'employee']]
        ordering = ['-read_at']

    def __str__(self):
        return f"{self.employee.get_full_name()} read {self.announcement.title}"


class AnnouncementComment(models.Model):
    """Comments on announcements"""

    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Announcement')
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='announcement_comments',
        verbose_name=_('Employee')
    )
    comment = models.TextField(_('Comment'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Announcement Comment')
        verbose_name_plural = _('Announcement Comments')
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.employee.get_full_name()} on {self.announcement.title}"
