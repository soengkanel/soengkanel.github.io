from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


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
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
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
            return "System"
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username
    
    @property
    def changes_summary(self):
        """Get a simple summary of changes"""
        if not self.old_values or not self.new_values:
            return self.description
        
        return f"{self.description} (Details: {self.old_values} → {self.new_values})"