from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


class Form(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_public = models.BooleanField(default=False)
    allow_multiple_submissions = models.BooleanField(default=True)
    collect_email = models.BooleanField(default=False)
    require_login = models.BooleanField(default=False)
    submission_deadline = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_submission_count(self):
        return self.submissions.count()


class FormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text Input'),
        ('textarea', 'Textarea'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('time', 'Time'),
        ('datetime', 'Date and Time'),
        ('select', 'Select Dropdown'),
        ('radio', 'Radio Button'),
        ('checkbox', 'Checkbox'),
        ('file', 'File Upload'),
        ('url', 'URL'),
        ('tel', 'Phone'),
        ('range', 'Range Slider'),
        ('color', 'Color Picker'),
    ]
    
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    help_text = models.TextField(blank=True)
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    # For fields with options (select, radio, checkbox)
    options = models.JSONField(default=list, blank=True)
    
    # Field validation
    min_length = models.PositiveIntegerField(null=True, blank=True)
    max_length = models.PositiveIntegerField(null=True, blank=True)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    pattern = models.CharField(max_length=500, blank=True, help_text="Regex pattern for validation")
    
    # Default value
    default_value = models.TextField(blank=True)
    
    # Field styling
    css_class = models.CharField(max_length=200, blank=True)
    placeholder = models.CharField(max_length=200, blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.form.title} - {self.label}"


class FormSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]

    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Email if collected and user is anonymous
    email = models.EmailField(blank=True)

    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_submissions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    admin_notes = models.TextField(blank=True, help_text="Internal notes, not visible to employee")
    response_message = models.TextField(blank=True, help_text="Message visible to employee")

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        user_info = self.submitted_by.username if self.submitted_by else self.email or 'Anonymous'
        return f"{self.form.title} - {user_info} - {self.submitted_at.strftime('%Y-%m-%d %H:%M')}"

    def get_field_value(self, field_label):
        """Get the value for a specific field by label"""
        return self.data.get(field_label, '')


class FormTemplate(models.Model):
    """Pre-built form templates for common use cases"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=100)
    template_data = models.JSONField(default=dict)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name


class ExtensionRequest(models.Model):
    """Model to store Extension of Stay application requests"""
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    ]
    
    VISA_TYPE_CHOICES = [
        ('tourist', 'Tourist Visa'),
        ('business', 'Business Visa'),
        ('work', 'Work Visa'),
        ('student', 'Student Visa'),
        ('other', 'Other'),
    ]
    
    EXTENSION_TYPE_CHOICES = [
        ('tourist', 'Tourist Extension'),
        ('business', 'Business Extension'),
        ('work', 'Work Permit Extension'),
        ('emergency', 'Emergency Extension'),
    ]
    
    REASON_CHOICES = [
        ('employment', 'Employment purposes'),
        ('medical', 'Medical treatment'),
        ('family', 'Family matters'),
        ('business', 'Business activities'),
        ('tourism', 'Tourism'),
        ('other', 'Other'),
    ]

    # Request tracking
    request_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='extension_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Service reference for billing
    service = models.ForeignKey('billing.Service', on_delete=models.CASCADE, null=True, blank=True, help_text="Associated billing service")

    # Worker information
    worker = models.ForeignKey('zone.Worker', on_delete=models.CASCADE, related_name='extension_requests')

    # Current visa details
    passport_number = models.CharField(max_length=50)
    passport_expiry_date = models.DateField(null=True, blank=True)
    passport_issued_date = models.DateField(null=True, blank=True)
    current_visa_type = models.CharField(max_length=20, choices=VISA_TYPE_CHOICES)
    current_visa_number = models.CharField(max_length=50, blank=True)
    current_visa_expiry = models.DateField()
    entry_date = models.DateField()
    
    # Work permit details
    work_permit_number = models.CharField(max_length=50, blank=True)
    work_permit_expiry = models.DateField(null=True, blank=True)
    
    # Address information
    address_name = models.CharField(max_length=200, blank=True, help_text="Address name in Cambodia")
    house_no = models.CharField(max_length=50, blank=True, help_text="House Number")
    street_no = models.CharField(max_length=50, blank=True, help_text="Street Number")
    commune = models.CharField(max_length=100, blank=True, help_text="Commune/Sangkat")
    district = models.CharField(max_length=100, blank=True, help_text="District/Khan")

    # Organization information
    organization_name = models.CharField(max_length=200, blank=True, default='KOH KONG RESORT', help_text="Institution/Organization Name")
    position = models.CharField(max_length=100, blank=True, help_text="Position/Job Title")

    # Extension request details
    extension_type = models.CharField(max_length=20, choices=EXTENSION_TYPE_CHOICES)
    extension_duration = models.PositiveIntegerField(help_text="Duration in days")
    extension_reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    extension_start_date = models.DateField()
    additional_details = models.TextField(blank=True)
    
    # Supporting documents (optional - files can be stored separately)
    passport_copy = models.FileField(upload_to='extension_requests/passports/', blank=True, null=True)
    visa_copy = models.FileField(upload_to='extension_requests/visas/', blank=True, null=True)
    employment_letter = models.FileField(upload_to='extension_requests/employment/', blank=True, null=True)
    other_documents = models.FileField(upload_to='extension_requests/other/', blank=True, null=True)
    
    # Processing information
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_extensions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_number']),
            models.Index(fields=['status']),
            models.Index(fields=['worker']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Extension Request #{self.request_number} - {self.worker.get_full_name()}"
    
    def save(self, *args, **kwargs):
        if not self.request_number:
            # Generate unique request number
            from datetime import datetime
            year = datetime.now().year
            count = ExtensionRequest.objects.filter(created_at__year=year).count() + 1
            self.request_number = f"EXT{year}{count:04d}"
        super().save(*args, **kwargs)
    
    @property
    def extension_end_date(self):
        """Calculate the end date of the extension"""
        if self.extension_start_date and self.extension_duration:
            import datetime
            return self.extension_start_date + datetime.timedelta(days=self.extension_duration)
        return None
    
    @property
    def is_expired(self):
        """Check if the extension request has expired"""
        if self.extension_end_date:
            return timezone.now().date() > self.extension_end_date
        return False
    
    @property
    def days_until_expiry(self):
        """Calculate days until extension expires"""
        if self.extension_end_date:
            delta = self.extension_end_date - timezone.now().date()
            return delta.days
        return None


class CertificateRequest(models.Model):
    """Model to store Employee Certificate requests - supports both single and batch requests"""
    STATUS_CHOICES = [
        ('requested', 'Requested'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
    ]
    
    CERTIFICATE_TYPE_CHOICES = [
        ('employment', 'Employment Certificate'),
        ('salary', 'Salary Certificate'),
        ('experience', 'Experience Certificate'),
        ('conduct', 'Good Conduct Certificate'),
        ('service', 'Service Certificate'),
        ('reference', 'Reference Letter'),
        ('other', 'Other'),
    ]
    
    PURPOSE_CHOICES = [
        ('bank_loan', 'Bank Loan Application'),
        ('visa_application', 'Application for visa extension'),
        ('new_employment', 'New Employment'),
        ('housing_rental', 'Housing Rental'),
        ('government_requirement', 'Government Requirement'),
        ('personal_use', 'Personal Use'),
        ('other', 'Other'),
    ]
    
    URGENCY_CHOICES = [
        ('normal', 'Normal (5-7 days)'),
        ('urgent', 'Urgent (2-3 days)'),
        ('emergency', 'Emergency (Same day)'),
    ]
    
    # Request tracking
    request_number = models.CharField(max_length=20, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificate_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Worker information - supports both single and batch requests
    workers = models.ManyToManyField('zone.Worker', related_name='certificate_requests')
    is_batch_request = models.BooleanField(default=False, help_text="True if this is a batch request for multiple workers")
    
    # Certificate request details
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPE_CHOICES)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    urgency = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='normal')
    specific_details = models.TextField(blank=True, help_text="Additional details or specific requirements")
    
    # Additional information for certificate content
    include_salary = models.BooleanField(default=False, help_text="Include salary information in certificate")
    include_start_date = models.BooleanField(default=True, help_text="Include employment start date")
    include_position = models.BooleanField(default=True, help_text="Include current position")
    include_department = models.BooleanField(default=True, help_text="Include department information")
    custom_text = models.TextField(blank=True, help_text="Custom text to include in certificate")
    
    # Delivery information
    delivery_method = models.CharField(max_length=20, choices=[
        ('pickup', 'Pickup from Office'),
        ('mail', 'Mail to Address'),
        ('email', 'Email Copy'),
        ('courier', 'Courier Service'),
    ], default='pickup')
    delivery_address = models.TextField(blank=True, help_text="Required if delivery method is mail or courier")
    delivery_contact = models.CharField(max_length=100, blank=True, help_text="Contact person for delivery")
    
    # Processing information
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_certificates')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_notes = models.TextField(blank=True)
    
    # Certificate generation information
    certificate_generated_at = models.DateTimeField(null=True, blank=True)
    certificate_file = models.FileField(upload_to='certificate_requests/certificates/', blank=True, null=True)
    
    # Expected completion date
    expected_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)
    request_ref = models.CharField(max_length=255, blank=True, null=True)
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['certificate_type']),
            models.Index(fields=['is_batch_request']),
        ]
    
    def __str__(self):
        if self.is_batch_request:
            worker_count = self.workers.count()
            return f"Certificate Request #{self.request_number} - Batch ({worker_count} workers)"
        else:
            worker = self.workers.first()
            return f"Certificate Request #{self.request_number} - {worker.get_full_name() if worker else 'No worker'}"
    
    @property
    def worker_names(self):
        """Get comma-separated list of worker names"""
        return ", ".join([worker.get_full_name() for worker in self.workers.all()])
    
    @property
    def worker_count(self):
        """Get count of workers in this request"""
        return self.workers.count()
    
    def save(self, *args, **kwargs):
        if not self.request_number:
            # Generate unique request number
            from datetime import datetime
            year = datetime.now().year
            count = CertificateRequest.objects.filter(created_at__year=year).count() + 1
            self.request_number = f"CERT{year}{count:04d}"
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if the certificate request is overdue"""
        if self.expected_completion and self.status not in ['completed']:
            return timezone.now().date() > self.expected_completion
        return False
    
    @property
    def days_until_deadline(self):
        """Calculate days until expected completion"""
        if self.expected_completion:
            delta = self.expected_completion - timezone.now().date()
            return delta.days
        return None
    
    @property
    def processing_duration(self):
        """Calculate how long the request has been in processing"""
        if self.actual_completion:
            return (self.actual_completion - self.created_at.date()).days
        return (timezone.now().date() - self.created_at.date()).days


class CertificateRequestWorkerService(models.Model):
    """Model to store visa service charges for each worker in a certificate request"""

    certificate_request = models.ForeignKey(CertificateRequest, on_delete=models.CASCADE, related_name='worker_services')
    worker = models.ForeignKey('zone.Worker', on_delete=models.CASCADE)
    visa_service_charge = models.ForeignKey('billing.Service', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='certificate_worker_services', help_text="Visa service charge for this worker")
    notes = models.TextField(blank=True, help_text="Additional notes about the service")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['certificate_request', 'worker']
        ordering = ['worker__first_name', 'worker__last_name']

    def __str__(self):
        service_name = self.visa_service_charge.name if self.visa_service_charge else "No service selected"
        return f"{self.worker.get_full_name()} - {service_name}"

    @property
    def service_price(self):
        """Get the price for the selected service"""
        return self.visa_service_charge.default_price if self.visa_service_charge else 0
