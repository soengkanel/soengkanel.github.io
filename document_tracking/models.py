from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid

from zone.models import Worker


class SubmissionWorker(models.Model):
    """Intermediate model for DocumentSubmission-Worker relationship with additional fields"""
    MARK_CHOICES = [
        ('New', 'New'),
        ('Renew', 'Renew'),
    ]

    submission = models.ForeignKey('DocumentSubmission', on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    mark = models.CharField(max_length=10, choices=MARK_CHOICES, default='New')
    visa_service_charge = models.ForeignKey('billing.Service', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='submission_workers', help_text="Individual visa service charge for this worker")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('submission', 'worker')
        verbose_name = "Submission Worker"
        verbose_name_plural = "Submission Workers"
    
    def __str__(self):
        return f"{self.submission.submission_id} - {self.worker.get_full_name()} ({self.mark})"


class DocumentSubmission(models.Model):
    """Main model for tracking government document submissions"""
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('checked', 'Checked'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
    ]
    
    DOCUMENT_TYPE_CHOICES = [
        ('visa', 'Visa'),
        ('visa_regular', 'Visa Process (2 Weeks - Building)'),
        ('work_permit_regular', 'Work Permit (25 Days - Building)'),
        ('visa_express', 'Express Visa (3 Days - People)'),
        ('work_permit_express', 'Express Work Permit (15 Days - People)'),
        ('passport_renewal', 'Passport Renewal'),
        ('residence_permit', 'Residence Permit'),
        ('business_license', 'Business License'),
        ('id_cards', 'ID Cards'),
        ('other', 'Other Document'),
    ]
    
    PROCESSING_ENTITY_CHOICES = [
        ('building', 'Government Building Office'),
        ('people', 'People\'s Office'),
        ('embassy', 'Embassy'),
        ('consulate', 'Consulate'),
        ('ministry', 'Ministry'),
        ('agent', 'Agent'),
        ('other', 'Other'),
    ]
    
    # Core tracking information
    submission_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    # Applicant information (many-to-many relations to Workers)
    workers = models.ManyToManyField(Worker, through='SubmissionWorker', blank=True, related_name='document_submissions', help_text="Select multiple workers for this submission")
    
    # Government office information
    processing_entity = models.CharField(max_length=20, choices=PROCESSING_ENTITY_CHOICES, default='building')
    government_office = models.CharField(max_length=200, help_text="Name of specific government office")
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Government reference/tracking number")
    
    # Important dates
    submission_date = models.DateField(null=True, blank=True)
    expected_completion_date = models.DateField(null=True, blank=True)
    actual_completion_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, help_text="Document expiry date")
    
    # Document details
    document_title = models.CharField(max_length=200, blank=True, help_text="Specific document title/name")
    purpose = models.TextField(blank=True, help_text="Purpose of document application")
    notes = models.TextField(blank=True, help_text="Additional notes and comments")
    
    # Service charge reference removed - now handled per worker in SubmissionWorker model
    
    # File attachments
    submitted_documents = models.FileField(upload_to='document_submissions/', null=True, blank=True, help_text="Scanned copies of submitted documents")
    received_documents = models.FileField(upload_to='received_documents/', null=True, blank=True, help_text="Final received documents")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Check if instance is saved (has a primary key)
        if not self.pk:
            return f"{self.get_document_type_display()} - New Submission"
            
        # Get all applicants for display
        worker_names = [worker.get_full_name() for worker in self.workers.all()]
        all_names = worker_names
        
        if all_names:
            applicants = ", ".join(all_names[:3])  # Show first 3 names
            if len(all_names) > 3:
                applicants += f" (+{len(all_names) - 3} more)"
        else:
            applicants = "No applicants"
            
        return f"{self.get_document_type_display()} - {applicants} ({self.submission_id or 'Pending'})"

    class Meta:
        verbose_name = "Document Submission"
        verbose_name_plural = "Document Submissions"
        ordering = ['-submission_date', '-created_at']

    def save(self, *args, **kwargs):
        # Auto-generate submission ID
        if not self.submission_id and self.status != 'pending':
            prefix = self.get_document_prefix()
            self.submission_id = f"{prefix}{timezone.now().year}{str(uuid.uuid4().hex[:6]).upper()}"
        
        # Auto-calculate expected completion date based on document type
        if self.submission_date and not self.expected_completion_date:
            processing_days = self.get_processing_days()
            if processing_days:
                self.expected_completion_date = self.submission_date + timedelta(days=processing_days)
        
        super().save(*args, **kwargs)

    def get_document_prefix(self):
        """Get prefix for submission ID based on document type"""
        prefixes = {
            'visa_regular': 'VR',
            'work_permit_regular': 'WPR',
            'visa_express': 'VE',
            'work_permit_express': 'WPE',
            'passport_renewal': 'PR',
            'residence_permit': 'RP',
            'business_license': 'BL',
            'id_cards': 'IDC',
            'other': 'DOC'
        }
        return prefixes.get(self.document_type, 'DOC')

    def get_processing_days(self):
        """Get expected processing days based on document type"""
        processing_times = {
            'visa_regular': 14,  # 2 weeks
            'work_permit_regular': 25,  # 25 days
            'visa_express': 3,  # 3 days
            'work_permit_express': 15,  # 15 days
            'passport_renewal': 21,  # 3 weeks
            'residence_permit': 30,  # 1 month
            'business_license': 14,  # 2 weeks
            'id_cards': 7,  # 1 week
        }
        return processing_times.get(self.document_type)

    @property
    def applicant_names(self):
        """Get all applicant names (workers only)"""
        if not self.pk:
            return []
        worker_names = [worker.get_full_name() for worker in self.workers.all()]
        return worker_names

    @property
    def total_applicants(self):
        """Get total number of applicants"""
        if not self.pk:
            return 0
        return self.workers.count()

    @property
    def applicant_name(self):
        """Get the name of applicants (for backwards compatibility)"""
        if not self.pk:
            return "New Submission"
        names = self.applicant_names
        if not names:
            return "No applicants"
        elif len(names) == 1:
            return names[0]
        else:
            return f"{names[0]} (+{len(names) - 1} more)"

    @property
    def days_remaining(self):
        """Calculate days remaining until expected completion"""
        if self.expected_completion_date:
            delta = self.expected_completion_date - timezone.now().date()
            return delta.days
        return None

    @property
    def is_overdue(self):
        """Check if document processing is overdue"""
        if self.expected_completion_date and self.status not in ['approved', 'completed']:
            return timezone.now().date() > self.expected_completion_date
        return False

    @property
    def days_overdue(self):
        """Get number of days overdue (positive number)"""
        if self.is_overdue and self.days_remaining is not None:
            return abs(self.days_remaining)
        return 0

    @property
    def is_expiring_soon(self):
        """Check if document will expire within 30 days"""
        if self.expiry_date and self.status == 'completed':
            return (self.expiry_date - timezone.now().date()).days <= 30
        return False


class DocumentUpdate(models.Model):
    """Track updates and status changes for document submissions"""
    
    submission = models.ForeignKey(DocumentSubmission, on_delete=models.CASCADE, related_name='updates')
    update_type = models.CharField(max_length=50, choices=[
        ('status_change', 'Status Change'),
        ('date_update', 'Date Update'),
        ('reference_added', 'Reference Number Added'),
        ('note_added', 'Note Added'),
        ('document_received', 'Document Received'),
        ('other', 'Other Update'),
    ])
    
    old_value = models.TextField(blank=True, help_text="Previous value")
    new_value = models.TextField(help_text="New value")
    notes = models.TextField(blank=True, help_text="Additional update notes")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.CharField(max_length=100, blank=True, help_text="Who made the update")

    def __str__(self):
        return f"{self.submission.submission_id} - {self.get_update_type_display()} ({self.created_at.strftime('%Y-%m-%d')})"

    class Meta:
        verbose_name = "Document Update"
        verbose_name_plural = "Document Updates"
        ordering = ['-created_at']


class DocumentType(models.Model):
    """Configuration model for document types and their processing times"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    processing_days = models.IntegerField(help_text="Expected processing time in days")
    processing_entity = models.CharField(max_length=20, choices=DocumentSubmission.PROCESSING_ENTITY_CHOICES)
    is_express = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Requirements
    required_documents = models.TextField(blank=True, help_text="List of required documents")
    fees = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Processing fees")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.processing_days} days - {self.get_processing_entity_display()})"

    class Meta:
        verbose_name = "Document Type"
        verbose_name_plural = "Document Types"
        ordering = ['name']
