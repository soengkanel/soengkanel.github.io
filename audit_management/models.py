from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from auditlog.models import LogEntry
import json

# Simple audit log model for easy what/when/who tracking
class SimpleAuditLog(models.Model):
    """Simple audit log focusing on what/when/who"""
    
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'), 
        ('delete', 'Deleted'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    # Core information - What/When/Who
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Who")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="What Action")
    model_name = models.CharField(max_length=100, verbose_name="What Model")
    object_id = models.CharField(max_length=100, blank=True, null=True)
    object_name = models.CharField(max_length=200, blank=True, help_text="Human readable name of the object")
    
    # Simple description of what changed
    description = models.TextField(verbose_name="What Changed")
    
    # When
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="When", db_index=True)
    
    # Optional: Simple before/after for updates
    old_values = models.TextField(blank=True, null=True, help_text="Old values (for updates)")
    new_values = models.TextField(blank=True, null=True, help_text="New values (for updates)")
    
    # Basic context
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Simple Audit Log"
        verbose_name_plural = "Simple Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['model_name', '-timestamp']),
        ]
    
    def __str__(self):
        user_name = self.user.get_full_name() or self.user.username if self.user else "System"
        return f"{user_name} {self.get_action_display().lower()} {self.model_name} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def user_display(self):
        """Get a display name for the user"""
        if not self.user:
            return "Unknown User"  # Changed from "System" to make it clear there's a data issue
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    @property
    def changes_summary(self):
        """Get a simple summary of changes"""
        if not self.old_values or not self.new_values:
            return self.description
        
        return f"{self.description} (Details: {self.old_values} → {self.new_values})"


class AuditSession(models.Model):
    """
    Track user sessions for audit correlation
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Audit Session"
        verbose_name_plural = "Audit Sessions"
        ordering = ['-started_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} ({self.started_at})"


class AuditTrail(models.Model):
    """
    Enhanced audit trail with business context
    """
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('create', 'Record Created'),
        ('update', 'Record Updated'),
        ('delete', 'Record Deleted'),
        ('view', 'Record Viewed'),
        ('export', 'Data Exported'),
        ('import', 'Data Imported'),
        ('permission_change', 'Permission Changed'),
        ('configuration_change', 'System Configuration Changed'),
        ('security_event', 'Security Event'),
    ]
    
    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    
    # Core audit information
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session = models.ForeignKey(AuditSession, on_delete=models.SET_NULL, null=True, blank=True)
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info')
    
    # Resource information
    resource_type = models.CharField(max_length=100)  # Model name or resource type
    resource_id = models.CharField(max_length=100, blank=True)
    resource_name = models.TextField(blank=True)  # Human readable name
    
    # Action details
    description = models.TextField()
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    
    # Context
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    request_path = models.CharField(max_length=500, blank=True)
    request_method = models.CharField(max_length=10, blank=True)
    
    # Business context
    department = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    business_unit = models.CharField(max_length=100, blank=True)
    
    # Metadata
    correlation_id = models.CharField(max_length=255, blank=True, db_index=True)
    tags = models.JSONField(default=list, blank=True)  # For categorization
    risk_score = models.IntegerField(default=0)  # 0-100 risk assessment
    
    # Timestamps
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Related auditlog entry
    log_entry = models.OneToOneField(
        LogEntry, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='enhanced_audit'
    )
    
    class Meta:
        verbose_name = "Audit Trail"
        verbose_name_plural = "Audit Trails"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
            models.Index(fields=['resource_type', 'timestamp']),
            models.Index(fields=['severity', 'timestamp']),
            models.Index(fields=['correlation_id']),
            models.Index(fields=['risk_score']),
        ]
        
    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.resource_type} ({self.timestamp})"
    
    @property
    def changes_summary(self):
        """Get a summary of changes made"""
        if not self.old_values or not self.new_values:
            return ""
        
        changes = []
        for field, new_value in self.new_values.items():
            old_value = self.old_values.get(field, '')
            if old_value != new_value:
                changes.append(f"{field}: {old_value} → {new_value}")
        
        return "; ".join(changes)
    
    def get_risk_level(self):
        """Get human readable risk level"""
        if self.risk_score >= 80:
            return "Critical"
        elif self.risk_score >= 60:
            return "High"
        elif self.risk_score >= 40:
            return "Medium"
        elif self.risk_score >= 20:
            return "Low"
        else:
            return "Minimal"


class AuditException(models.Model):
    """
    Track audit logging exceptions and failures
    """
    EXCEPTION_TYPES = [
        ('logging_failure', 'Audit Logging Failed'),
        ('permission_denied', 'Permission Denied'),
        ('data_corruption', 'Data Corruption Detected'),
        ('suspicious_activity', 'Suspicious Activity'),
        ('system_error', 'System Error'),
    ]
    
    exception_type = models.CharField(max_length=50, choices=EXCEPTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    error_message = models.TextField(blank=True)
    stack_trace = models.TextField(blank=True)
    
    # Context when exception occurred
    request_path = models.CharField(max_length=500, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Resolution
    resolved = models.BooleanField(default=False)
    resolved_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='resolved_audit_exceptions'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Audit Exception"
        verbose_name_plural = "Audit Exceptions"
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"{self.exception_type} - {self.timestamp}"


class AuditReport(models.Model):
    """
    Scheduled and generated audit reports
    """
    REPORT_TYPES = [
        ('user_activity', 'User Activity Report'),
        ('data_changes', 'Data Changes Report'),
        ('security_events', 'Security Events Report'),
        ('compliance', 'Compliance Report'),
        ('risk_assessment', 'Risk Assessment Report'),
    ]
    
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('on_demand', 'On Demand'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    
    # Report parameters
    date_from = models.DateTimeField()
    date_to = models.DateTimeField()
    users = models.ManyToManyField(User, blank=True, related_name='audit_reports')
    resource_types = models.JSONField(default=list, blank=True)
    action_types = models.JSONField(default=list, blank=True)
    
    # Scheduling
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='on_demand')
    is_active = models.BooleanField(default=True)
    last_generated = models.DateTimeField(null=True, blank=True)
    next_generation = models.DateTimeField(null=True, blank=True)
    
    # Results
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='generated_audit_reports')
    file_path = models.FileField(upload_to='audit_reports/', blank=True)
    record_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Audit Report"
        verbose_name_plural = "Audit Reports"
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.report_type})"
