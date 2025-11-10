# models for core
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from zone.models import UserProfile
from django.conf import settings

# Add user_type property to User model for compatibility
def get_user_type(self):
    """Get user type from agent profile, default to 'staff' if no profile exists"""
    try:
        profile = UserProfile.objects.get(user=self)
        # Map agent user types
        if profile.user_type in ['admin', 'manager']:
            return 'admin'
        else:
            return 'user'
    except:
        # For superusers or users without profiles
        if self.is_superuser:
            return 'admin'
        return 'user'

def get_display_role(self):
    """Get display role for user"""
    if self.is_superuser:
        return 'Super Admin'
    try:
        profile = UserProfile.objects.get(user=self)
        if profile.user_type == 'admin':
            return 'Administrator'
        elif profile.user_type == 'manager':
            return 'Manager'
        elif profile.user_type == 'staff':
            return 'Staff User'
        else:
            return 'Viewer'
    except:
        return 'Regular User'

def get_role_badge_class(self):
    """Get CSS class for role badge"""
    if self.is_superuser:
        return 'badge-danger'
    try:
        profile = UserProfile.objects.get(user=self)
        if profile.user_type in ['admin', 'manager']:
            return 'badge-warning'
        else:
            return 'badge-info'
    except:
        return 'badge-info'

# Add properties to User model
User.add_to_class('user_type', property(get_user_type))
User.add_to_class('display_role', property(get_display_role))
User.add_to_class('role_badge_class', property(get_role_badge_class))

class Notification(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    TYPE_CHOICES = [
        ('probation_ending', 'Probation Ending'),
        ('probation_overdue', 'Probation Overdue'),
        ('document_expiring', 'Document Expiring'),
        ('document_expired', 'Document Expired'),
        ('general', 'General'),
        ('system', 'System'),
    ]

    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Related objects
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    related_object_type = models.CharField(max_length=50, blank=True, null=True)
    related_object_id = models.PositiveIntegerField(blank=True, null=True)
    
    # Status
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # Action URL
    action_url = models.URLField(blank=True, null=True)
    action_text = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def dismiss(self):
        """Dismiss notification"""
        self.is_dismissed = True
        self.save(update_fields=['is_dismissed'])
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def priority_class(self):
        """Get CSS class for priority"""
        return {
            'low': 'info',
            'medium': 'warning',
            'high': 'warning',
            'critical': 'danger',
        }.get(self.priority, 'info')
    
    @property
    def priority_icon(self):
        """Get icon for priority"""
        return {
            'low': 'bi-info-circle',
            'medium': 'bi-exclamation-circle',
            'high': 'bi-exclamation-triangle',
            'critical': 'bi-exclamation-triangle-fill',
        }.get(self.priority, 'bi-info-circle')

    @classmethod
    def create_probation_notification(cls, worker, probation_period, recipient, days_remaining):
        """Create a probation-related notification"""
        if days_remaining <= 0:
            notification_type = 'probation_overdue'
            priority = 'critical'
            title = f"URGENT: Probation Overdue - {worker.get_full_name()}"
            message = f"Worker {worker.get_full_name()} ({worker.worker_id}) has an overdue probation period that ended {abs(days_remaining)} days ago."
        elif days_remaining == 1:
            notification_type = 'probation_ending'
            priority = 'critical'
            title = f"URGENT: Probation Ending Tomorrow - {worker.get_full_name()}"
            message = f"Worker {worker.get_full_name()} ({worker.worker_id}) probation period ends tomorrow."
        elif days_remaining <= 3:
            notification_type = 'probation_ending'
            priority = 'high'
            title = f"Probation Ending Soon - {worker.get_full_name()}"
            message = f"Worker {worker.get_full_name()} ({worker.worker_id}) probation period ends in {days_remaining} days."
        else:
            notification_type = 'probation_ending'
            priority = 'medium'
            title = f"Probation Period Notice - {worker.get_full_name()}"
            message = f"Worker {worker.get_full_name()} ({worker.worker_id}) probation period ends in {days_remaining} days."
        
        return cls.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            recipient=recipient,
            related_object_type='worker_probation',
            related_object_id=probation_period.id,
                            action_url=f'/zone/probation/{probation_period.id}/',
            action_text='View Details',
            expires_at=timezone.now() + timedelta(days=30)
        )

    @classmethod
    def create_document_expiry_notification(cls, worker, document, recipient, days_remaining):
        """Create a document expiry notification"""
        if days_remaining <= 0:
            notification_type = 'document_expired'
            priority = 'critical'
            title = f"URGENT: Document Expired - {worker.get_full_name()}"
            message = f"Worker {worker.get_full_name()} ({worker.worker_id}) {document.get_document_type_display()} expired {abs(days_remaining)} days ago."
        elif days_remaining == 1:
            notification_type = 'document_expiring'
            priority = 'critical'
            title = f"URGENT: Document Expires Tomorrow - {worker.get_full_name()}"
            message = f"Worker {worker.get_full_name()} ({worker.worker_id}) {document.get_document_type_display()} expires tomorrow."
        elif days_remaining <= 3:
            notification_type = 'document_expiring'
            priority = 'high'
            title = f"Document Expiring Soon - {worker.get_full_name()}"
            message = f"Worker {worker.get_full_name()} ({worker.worker_id}) {document.get_document_type_display()} expires in {days_remaining} days."
        else:
            notification_type = 'document_expiring'
            priority = 'medium'
            title = f"Document Expiry Notice - {worker.get_full_name()}"
            message = f"Worker {worker.get_full_name()} ({worker.worker_id}) {document.get_document_type_display()} expires in {days_remaining} days."
        
        return cls.objects.create(
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            recipient=recipient,
            related_object_type='worker_document',
            related_object_id=document.id,
                            action_url=f'/zone/worker/{worker.id}/documents/',
            action_text='View Documents',
            expires_at=timezone.now() + timedelta(days=30)
        )

class Nationality(models.Model):
    zip_code = models.CharField(max_length=10, unique=True, help_text="Unique zip/postal code")
    country_code = models.CharField(max_length=3, help_text="2-3 letter country code (e.g., KH, US, FR)")
    country_name = models.CharField(max_length=100, help_text="Full country name")
    nationality = models.CharField(max_length=100, help_text="Nationality/demonym (e.g., Cambodian, American)")
    region = models.CharField(max_length=50, help_text="Geographic region (e.g., Southeast Asia, Europe)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_nationalities')

    class Meta:
        verbose_name = "Nationality"
        verbose_name_plural = "Nationalities"
        ordering = ['country_name']

    def __str__(self):
        return f"{self.country_name} ({self.nationality})"