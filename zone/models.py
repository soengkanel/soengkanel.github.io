from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import os
from datetime import timedelta
from core.encryption import EncryptedCharField, EncryptedTextField, EncryptedEmailField
from core.encrypted_fields import EncryptedFileField, EncryptedImageField, FileEncryptionMixin


def validate_image_file_extension(value):
    """Validate that the uploaded file is an image."""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.enc']  # Include .enc for encrypted files
    if not ext in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Please upload JPG, PNG, GIF, or BMP files only.'))


def validate_image_file_size(value):
    """File size validation removed - no size limits."""
    pass


class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('viewer', 'Viewer'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='staff')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    employee_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_regex = RegexValidator(
        regex=r'^(\+?855|0)\d{8,10}$',
        message="Phone number must be in Cambodia format: +855xxxxxxxx or 0xxxxxxxx (8-10 digits after prefix)"
    )
    phone_number = EncryptedCharField(_('Phone Number'), validators=[phone_regex], max_length=17, blank=True)
    department = models.CharField(max_length=100, blank=True)
    position = models.CharField(max_length=100, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class PermissionCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_permission_categories')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Permission Category"
        verbose_name_plural = "Permission Categories"
        ordering = ['name']


class CustomPermission(models.Model):
    name = models.CharField(max_length=100)
    codename = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(PermissionCategory, on_delete=models.CASCADE, related_name='permissions')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_custom_permissions')

    def __str__(self):
        return f"{self.name} ({self.codename})"

    class Meta:
        verbose_name = "Custom Permission"
        verbose_name_plural = "Custom Permissions"
        ordering = ['category', 'name']
        unique_together = ['name', 'category']


class Building(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    address = models.TextField()
    total_floors = models.PositiveIntegerField()
    no_floor = models.BooleanField(default=False)
    zone = models.ForeignKey('Zone', on_delete=models.SET_NULL, null=True, blank=True, related_name='buildings', help_text="Zone that this building belongs to")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_buildings')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Building"
        verbose_name_plural = "Buildings"
        ordering = ['name']


class Floor(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    floor_number = models.PositiveIntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_floors')

    def __str__(self):
        # Use the name field directly (which should be F1, F2, F3, etc.)
        # If name is empty, fallback to the old format
        return self.name if self.name else f"{self.building.name} - Floor {self.floor_number}"

    class Meta:
        verbose_name = "Floor"
        verbose_name_plural = "Floors"
        ordering = ['building', 'floor_number']
        unique_together = ['building', 'floor_number']


class Zone(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text="Unique name for the zone")
    phone_number = EncryptedCharField(_('Phone Number'), max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_zones')
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Zone"
        verbose_name_plural = "Zones"
        ordering = ['name']
    
    # Custom method to safely get phone number for audit logging
    def get_phone_number_for_audit(self):
        """Return a safe representation of phone number for audit logging"""
        if isinstance(self.phone_number, bytes):
            return "[Encrypted Phone Number]"
        return self.phone_number or ""

class Document(FileEncryptionMixin, models.Model):
    DOCUMENT_TYPES = [
        ('id_card', 'ID Card'),
        ('passport', 'Passport'),
        ('visa', 'Visa'),
        ('work_permit', 'Work Permit'),
        ('other', 'Other'),
    ]
    
    # Document belongs to a specific worker
    worker = models.ForeignKey('Worker', on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(max_length=50)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    issuing_authority = models.CharField(max_length=100)
    document_file = EncryptedFileField(upload_to='worker_documents/')
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_documents')

    def __str__(self):
        return f"{self.worker.get_full_name()} - {self.get_document_type_display()} ({self.document_number})"

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        ordering = ['-created_at']

class Worker(FileEncryptionMixin, models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),                    # Normal working status
        ('inactive', 'Inactive'),                # Not currently working
        ('on_leave', 'On Leave'),                # Temporary absence
        ('probation', 'Probation'),
        ('passed', 'Passed'),                    # Successfully completed 
        ('extended', 'Extended'),                # Period was extended
        ('failed', 'Failed'),                    # Failed the probation
        ('terminated', 'Terminated'),            # Terminated during probation
    ]
    
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    NATIONALITY_CHOICES = [
        # ASEAN
        ('KH', 'Cambodian'),
        ('TH', 'Thai'),
        ('VN', 'Vietnamese'),
        ('ID', 'Indonesian'),
        ('MY', 'Malaysian'),
        ('PH', 'Filipino'),
        ('MM', 'Myanmar'),
        ('LA', 'Laotian'),
        ('SG', 'Singaporean'),
        ('BN', 'Bruneian'),

        # East Asia
        ('CH', 'Chinese'),
        ('JP', 'Japanese'),
        ('KR', 'Korean'),
        ('TW', 'Taiwanese'),
        ('MO', 'Macanese'),
        ('MN', 'Mongolian'),

        # South Asia
        ('IN', 'Indian'),
        ('PK', 'Pakistani'),
        ('BD', 'Bangladeshi'),
        ('LK', 'Sri Lankan'),
        ('NP', 'Nepalese'),
        ('BT', 'Bhutanese'),
        ('MV', 'Maldivian'),

        # Middle East
        ('AE', 'Emirati'),
        ('SA', 'Saudi'),
        ('QA', 'Qatari'),
        ('KW', 'Kuwaiti'),
        ('BH', 'Bahraini'),
        ('OM', 'Omani'),
        ('JO', 'Jordanian'),
        ('LB', 'Lebanese'),
        ('SY', 'Syrian'),
        ('IQ', 'Iraqi'),
        ('YE', 'Yemeni'),
        ('IR', 'Iranian'),
        ('TR', 'Turkish'),

        # Europe
        ('GB', 'British'),
        ('FR', 'French'),
        ('DE', 'German'),
        ('IT', 'Italian'),
        ('ES', 'Spanish'),
        ('PT', 'Portuguese'),
        ('NL', 'Dutch'),
        ('BE', 'Belgian'),
        ('CH', 'Swiss'),
        ('SE', 'Swedish'),
        ('NO', 'Norwegian'),
        ('DK', 'Danish'),
        ('FI', 'Finnish'),
        ('RU', 'Russian'),
        ('UA', 'Ukrainian'),
        ('PL', 'Polish'),
        ('GR', 'Greek'),

        # Africa
        ('EG', 'Egyptian'),
        ('ZA', 'South African'),
        ('NG', 'Nigerian'),
        ('KE', 'Kenyan'),
        ('GH', 'Ghanaian'),
        ('ET', 'Ethiopian'),
        ('MA', 'Moroccan'),
        ('DZ', 'Algerian'),
        ('TN', 'Tunisian'),

        # Americas
        ('US', 'American'),
        ('CA', 'Canadian'),
        ('MX', 'Mexican'),
        ('BR', 'Brazilian'),
        ('AR', 'Argentine'),
        ('CL', 'Chilean'),
        ('CO', 'Colombian'),
        ('PE', 'Peruvian'),
        ('CU', 'Cuban'),

        # Oceania
        ('AU', 'Australian'),
        ('NZ', 'New Zealander'),
        ('FJ', 'Fijian'),
        ('PG', 'Papua New Guinean'),

        # Other / Generic
        ('OTHER', 'Other'),
    ]

    
    # Personal Information - Workers are NOT system users
    worker_id = models.CharField(max_length=20, unique=True, help_text="Unique worker identification number", blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    nickname = models.CharField(max_length=50, blank=True, null=True, help_text="Worker's nickname or preferred name")
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True)
    dob = models.DateField(null=True, blank=True, verbose_name="Date of Birth")
    nationality = models.CharField(max_length=50, choices=NATIONALITY_CHOICES, blank=True)
    
    # Photo Information (Encrypted)
    photo = EncryptedImageField(
        upload_to='worker_photos/',
        blank=True, 
        null=True,
        validators=[validate_image_file_extension, validate_image_file_size],
        verbose_name='Photo',
        help_text='Upload worker photo (JPG, PNG, GIF, BMP formats supported) - Automatically encrypted'
    )
    
    # Position Information
    position = models.ForeignKey('Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='workers')
    
    # Contact Information
    phone_number = EncryptedCharField(_('Phone Number'), max_length=20, blank=True, null=True, help_text="Worker's phone number (encrypted)")
    
    # Work Information
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='workers')
    building = models.ForeignKey(Building, on_delete=models.SET_NULL, null=True, related_name='workers')
    floor = models.ForeignKey(Floor, on_delete=models.SET_NULL, null=True, related_name='workers')
    date_joined = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    is_vip = models.BooleanField(default=False, help_text="Mark as VIP worker for special privileges")
    
    # Performance Information
    performance_rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, 
        blank=True,
        help_text="Performance rating from 1 (Poor) to 5 (Excellent)"
    )
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_workers')

    def __str__(self):
        vip_indicator = " [VIP]" if self.is_vip else ""
        position_info = f" - {self.position.name}" if self.position else ""
        return f"{self.first_name} {self.last_name} ({self.worker_id}){vip_indicator}{position_info}"

    class Meta:
        verbose_name = "Worker"
        verbose_name_plural = "Workers"
        ordering = ['-date_joined']

    def get_full_name(self):
        """Return the worker's full name"""
        first = (self.first_name or '').strip()
        last = (self.last_name or '').strip()
        
        if first and last:
            return f"{first} {last}"
        elif first:
            return first
        elif last:
            return last
        else:
            return f"Worker {self.id}"
    
    @property
    def photo_url(self):
        """Return the secure URL of the worker photo or a default placeholder."""
        if self.photo and self.photo.name:
            # Return secure photo URL instead of direct file URL
            from django.urls import reverse
            return reverse('zone:serve_worker_photo', kwargs={'worker_id': self.id})
        return '/static/images/default-worker-avatar.png'
    
    def has_photo(self):
        """Check if the worker has a photo uploaded."""
        return bool(self.photo)
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        if self.dob:
            from django.utils import timezone
            today = timezone.now().date()
            return today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
        return None
    
    @property
    def has_expired_documents(self):
        """Check if any documents are expired"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.documents.filter(expiry_date__lt=today).exists()
    
    @property
    def expiring_soon_documents(self):
        """Get documents expiring within 30 days"""
        from django.utils import timezone
        today = timezone.now().date()
        thirty_days = today + timedelta(days=30)
        return self.documents.filter(expiry_date__lte=thirty_days, expiry_date__gte=today)
    
    @property
    def work_permit_expiry(self):
        """Get work permit expiry date"""
        work_permit = self.documents.filter(document_type='work_permit').first()
        return work_permit.expiry_date if work_permit else None
    
    @property
    def current_probation_period(self):
        """Get the current active probation period (excluding cancelled ones)"""
        # Exclude cancelled probations (those with terminated_date set)
        return self.probation_periods.filter(terminated_date__isnull=True).order_by('-start_date').first()
    
    @property
    def has_passed_probation(self):
        """Check if worker has passed or completed any probation period"""
        # Check worker status instead of probation period status
        return self.status in ['passed', 'completed']
    
    @property
    def is_on_probation(self):
        """Check if worker is currently on probation"""
        current_probation = self.current_probation_period
        if current_probation:
            return current_probation.is_active
        return False
    
    @property
    def probation_end_date(self):
        """Get the end date of current probation period"""
        current_probation = self.current_probation_period
        if current_probation:
            return current_probation.actual_end_date or current_probation.original_end_date
        return None
    
    @property
    def probation_days_remaining(self):
        """Get days remaining in current probation period"""
        current_probation = self.current_probation_period
        if current_probation:
            return current_probation.days_remaining
        return 0

    @property 
    def current_id_card(self):
        """Get the most recent/current ID card for this worker."""
        return self.id_cards.order_by('-created_at').first()
    
    @property
    def id_card_status(self):
        """Get the status of worker's current ID card."""
        card = self.current_id_card
        if card:
            return card.status
        return None
    
    @property
    def has_delivered_id_card(self):
        """Check if worker has a delivered ID card."""
        return self.id_cards.filter(status='delivered').exists()
    
    @property
    def id_card_info(self):
        """Get comprehensive ID card information for display."""
        card = self.current_id_card
        if not card:
            return {
                'status': 'no_card',
                'display': 'No Card',
                'card_number': None,
                'badge_class': 'status-no-card'
            }
        
        status_display_map = {
            'pending': {'display': 'Pending', 'badge_class': 'status-pending'},
            'approved': {'display': 'Approved', 'badge_class': 'status-approved'},
            'printed': {'display': 'Printed', 'badge_class': 'status-printed'},
            'delivered': {'display': 'Delivered', 'badge_class': 'status-delivered'},
            'active': {'display': 'Active', 'badge_class': 'status-active'},
            'expired': {'display': 'Expired', 'badge_class': 'status-expired'},
            'lost': {'display': 'Lost', 'badge_class': 'status-lost'},
            'damaged': {'display': 'Damaged', 'badge_class': 'status-damaged'},
        }
        
        status_info = status_display_map.get(card.status, {
            'display': card.get_status_display(),
            'badge_class': f'status-{card.status}'
        })
        
        return {
            'status': card.status,
            'display': status_info['display'],
            'card_number': card.card_number,
            'badge_class': status_info['badge_class']
        }

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Validate floor belongs to building
        if self.floor and self.building and self.floor.building != self.building:
            raise ValidationError('Selected floor does not belong to the selected building')

    def generate_id_card(self):
        """Generate unique ID card number in format {building}-{floor}-{####}"""
        if not self.building or not self.floor:
            return None
            
        building_code = self.building.code
        floor_number = f"F{self.floor.floor_number}"
        
        # Find the next available number for this building-floor combination
        prefix = f"{building_code}-{floor_number}-"
        # Note: IDCard field doesn't exist in current model
        # This method needs to be updated to work with actual fields
        existing_cards = []
        
        # Extract numbers and find the next available
        existing_numbers = []
        for card in existing_cards:
            try:
                number_part = card.split('-')[-1]
                existing_numbers.append(int(number_part))
            except (ValueError, IndexError):
                continue
        
        # Find next available number
        next_number = 1
        while next_number in existing_numbers:
            next_number += 1
            
        return f"{prefix}{next_number:04d}"

    def get_display_data(self, user):
        """Get display data based on user permissions - handles encrypted fields properly"""
        from core.encryption import mask_sensitive_data
        
        # Check if user has permission to view sensitive data
        can_view_sensitive = (
            user.is_superuser or 
            (hasattr(user, 'profile') and user.profile.user_type in ['admin', 'manager'])
        )
        
        display_data = {
            # Basic info - always visible
            'worker_id': self.worker_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'full_name': self.get_full_name(),
            'nationality': self.get_nationality_display(),
            'position': self.position.name if self.position else None,
            'status': self.get_status_display(),
        }
        
        # Encrypted fields - handle based on permissions
        if can_view_sensitive:
            # Show full data for authorized users
            display_data.update({
                'phone_number': self.phone_number,
            })
        else:
            # Show masked data for unauthorized users
            display_data.update({
                'phone_number': mask_sensitive_data(self.phone_number) if self.phone_number else None,
            })
        
        return display_data

    def save(self, *args, **kwargs):
        # Store if this is a new worker
        is_new_worker = self.pk is None
        
        # Auto-generate worker_id if not provided
        if not self.worker_id:
            # Generate worker ID like: WKR2024001, WKR2024002, etc.
            year = timezone.now().year
            last_worker = Worker.objects.filter(
                worker_id__startswith=f'WKR{year}'
            ).order_by('-worker_id').first()
            
            if last_worker:
                # Extract the sequence number and increment
                try:
                    last_seq = int(last_worker.worker_id[-3:])
                    new_seq = last_seq + 1
                except (ValueError, IndexError):
                    new_seq = 1
            else:
                new_seq = 1
            
            self.worker_id = f'WKR{year}{new_seq:03d}'
        
        # Date of birth field validation
        # Only 'dob' field is now used
        
        super().save(*args, **kwargs)
        
        # Create default documents based on worker data if new worker
        # Note: passport_number field doesn't exist in current model
        # Document creation should be handled separately via forms

class WorkerAssignment(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='assignments')
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='worker_assignments')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_worker_assignments')

    def __str__(self):
        return f"{self.worker.get_full_name()} - {self.zone}"

    class Meta:
        verbose_name = "Worker Assignment"
        verbose_name_plural = "Worker Assignments"
        ordering = ['-start_date']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date cannot be before start date')


class WorkerProbationPeriod(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, 
                               related_name='probation_periods', verbose_name='Worker')
    start_date = models.DateField('Start Date')
    original_end_date = models.DateField('Original End Date')
    actual_end_date = models.DateField('Actual End Date', null=True, blank=True)
    evaluation_notes = models.TextField('Evaluation Notes', blank=True)
    termination_reason = models.TextField('Termination Reason', blank=True, help_text='Reason for termination during probation')
    terminated_date = models.DateField('Termination Date', null=True, blank=True)
    terminated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='terminated_worker_probation_periods', verbose_name='Terminated By')
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                 related_name='created_worker_probation_periods', verbose_name='Created By')

    def __str__(self):
        return f"{self.worker.get_full_name()} - Probation ({self.start_date} to {self.get_end_date()})"

    def get_end_date(self):
        """Get the actual end date considering extensions."""
        if self.actual_end_date:
            return self.actual_end_date
        
        # Calculate end date with extensions
        total_extension_days = sum(ext.extension_duration_days for ext in self.extensions.all())
        return self.original_end_date + timedelta(days=total_extension_days)

    def get_total_duration_days(self):
        """Get total duration including extensions."""
        end_date = self.get_end_date()
        return (end_date - self.start_date).days

    def get_days_completed(self):
        """Get number of days completed so far."""
        from django.utils import timezone
        today = timezone.now().date()
        
        if self.worker.status == 'passed' and self.actual_end_date:
            return (self.actual_end_date - self.start_date).days
        
        if today < self.start_date:
            return 0
        
        end_date = self.get_end_date()
        if today >= end_date:
            return self.get_total_duration_days()
            
        return (today - self.start_date).days

    def get_days_remaining(self):
        """Get number of days remaining in probation."""
        if self.worker.status in ['passed', 'failed', 'terminated']:
            return 0
            
        from django.utils import timezone
        today = timezone.now().date()
        end_date = self.get_end_date()
        
        if today >= end_date:
            return 0
            
        return (end_date - today).days

    def get_progress_percentage(self):
        """Get progress percentage (0-100)."""
        total_days = self.get_total_duration_days()
        if total_days <= 0:
            return 0
            
        completed_days = self.get_days_completed()
        return min(round((completed_days / total_days) * 100), 100)

    def is_ending_soon(self, days_threshold=7):
        """Check if probation is ending within the specified days."""
        if self.worker.status not in ['probation', 'extended']:
            return False
        return self.get_days_remaining() <= days_threshold

    def is_overdue(self):
        """Check if probation period has passed the end date."""
        if self.worker.status in ['passed', 'failed', 'terminated']:
            return False
        return self.get_days_remaining() <= 0

    def get_status_color(self):
        """Get Bootstrap color class for status."""
        status_colors = {
            'probation': 'success',
            'extended': 'warning',
            'passed': 'info',
            'failed': 'danger',
            'terminated': 'secondary'
        }
        return status_colors.get(self.worker.status, 'secondary')

    def get_urgency_level(self):
        """Get urgency level based on days remaining."""
        if self.worker.status not in ['probation', 'extended']:
            return 'none'
            
        days_remaining = self.get_days_remaining()
        if days_remaining <= 0:
            return 'overdue'
        elif days_remaining <= 3:
            return 'critical'
        elif days_remaining <= 7:
            return 'high'
        elif days_remaining <= 14:
            return 'medium'
        else:
            return 'low'

    def get_total_extension_days(self):
        """Get total days from all extensions."""
        return sum(ext.extension_duration_days for ext in self.extensions.all())

    def get_max_allowed_extension_days(self):
        """Get maximum additional extension days allowed based on business rule."""
        DEFAULT_PROBATION_DAYS = 15
        MAX_TOTAL_PROBATION_DAYS = 30
        max_allowed_extension_days = MAX_TOTAL_PROBATION_DAYS - DEFAULT_PROBATION_DAYS  # 15 days max extension
        current_total_extension_days = self.get_total_extension_days()
        return max(0, max_allowed_extension_days - current_total_extension_days)

    def can_be_extended(self):
        """Check if this probation period can be extended further."""
        if self.worker.status not in ['probation', 'extended']:
            return False
        
        # Check if already at maximum extension limit
        if self.get_max_allowed_extension_days() <= 0:
            return False
            
        # Check if probation period hasn't already ended
        from django.utils import timezone
        today = timezone.now().date()
        end_date = self.get_end_date()
        return end_date >= today

    def save(self, *args, **kwargs):
        if not self.created_by and hasattr(self, '_created_by'):
            self.created_by = self._created_by
        
        # Track if this is a new probation period
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Automatically set worker status to "probation" when creating a new probation period
        if is_new and self.worker.status != 'probation':
            self.worker.status = 'probation'
            self.worker.save()

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.actual_end_date and self.actual_end_date <= self.start_date:
            raise ValidationError("Actual end date must be after start date.")
        if self.original_end_date <= self.start_date:
            raise ValidationError("Original end date must be after start date.")

    class Meta:
        verbose_name = 'Worker Probation Period'
        verbose_name_plural = 'Worker Probation Periods'
        ordering = ['-start_date']

    @property
    def is_active(self):
        """Check if probation period is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        end_date = self.get_end_date()
        return self.worker.status == 'probation' and self.start_date <= today <= end_date

    @property
    def days_remaining(self):
        """Legacy property for backward compatibility"""
        return self.get_days_remaining()

    @property
    def total_duration_days(self):
        """Legacy property for backward compatibility"""
        return self.get_total_duration_days()

    @property
    def progress_percentage(self):
        """Legacy property for backward compatibility"""
        return self.get_progress_percentage()
    
    def get_batch_name(self):
        """Extract batch name from evaluation notes."""
        if not self.evaluation_notes:
            return None
        
        # Look for "Batch: [name]" pattern at the beginning of evaluation notes
        lines = self.evaluation_notes.strip().split('\n')
        if lines and lines[0].startswith('Batch: '):
            return lines[0][7:]  # Remove "Batch: " prefix
        return None
    
    @property
    def batch_name(self):
        """Property to get batch name for template usage."""
        return self.get_batch_name()


class WorkerProbationExtension(models.Model):
    probation_period = models.ForeignKey(WorkerProbationPeriod, on_delete=models.CASCADE,
                                       related_name='extensions', verbose_name='Probation Period')
    extension_duration_days = models.IntegerField('Extension Duration (Days)')
    reason = models.TextField('Reason for Extension')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                  related_name='approved_worker_probation_extensions', verbose_name='Approved By')
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                                 related_name='created_worker_probation_extensions', verbose_name='Created By')

    def __str__(self):
        return f"{self.probation_period.worker.get_full_name()} - {self.extension_duration_days} days extension"

    class Meta:
        verbose_name = 'Worker Probation Extension'
        verbose_name_plural = 'Worker Probation Extensions'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Always update the probation period status to 'extended' when extension is created
        from datetime import timedelta
        
        if not self.probation_period.actual_end_date:
            # First extension: set actual_end_date based on original_end_date + extension
            self.probation_period.actual_end_date = (
                self.probation_period.original_end_date + timedelta(days=self.extension_duration_days)
            )
        else:
            # Additional extension: extend the existing actual_end_date
            old_date = self.probation_period.actual_end_date
            self.probation_period.actual_end_date += timedelta(days=self.extension_duration_days)
        
        # Save probation period with updated end date
        self.probation_period.save()
        
        # Always set worker status to 'extended' when any extension is created
        self.probation_period.worker.status = 'extended'
        self.probation_period.worker.save()
        
        super().save(*args, **kwargs)

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.extension_duration_days is not None and self.extension_duration_days <= 0:
            raise ValidationError("Extension duration must be positive.")
            
        # Business Rule: Total probation period cannot exceed 30 days
        # Safely check if probation_period exists (it might not be set yet during form validation)
        try:
            probation_period = self.probation_period
        except WorkerProbationExtension.probation_period.RelatedObjectDoesNotExist:
            # probation_period not set yet, skip validation (will be set later in the view)
            return
            
        if probation_period:
            # Calculate current total extension days (excluding this extension if it's being updated)
            current_extensions = probation_period.extensions.all()
            if self.pk:  # If this is an update, exclude current extension from calculation
                current_extensions = current_extensions.exclude(pk=self.pk)
            
            current_total_extension_days = sum(ext.extension_duration_days for ext in current_extensions)
            new_total_extension_days = current_total_extension_days + self.extension_duration_days
            
            # Default probation is 15 days, total cannot exceed 30 days
            DEFAULT_PROBATION_DAYS = 15
            MAX_TOTAL_PROBATION_DAYS = 30
            max_allowed_extension_days = MAX_TOTAL_PROBATION_DAYS - DEFAULT_PROBATION_DAYS  # 15 days max extension
            
            if new_total_extension_days > max_allowed_extension_days:
                remaining_extension_days = max_allowed_extension_days - current_total_extension_days
                if remaining_extension_days <= 0:
                    raise ValidationError(
                        f"Cannot extend probation. Maximum total probation period is {MAX_TOTAL_PROBATION_DAYS} days. "
                        f"This worker has already reached the maximum extension limit."
                    )
                else:
                    raise ValidationError(
                        f"Extension duration exceeds the maximum limit. "
                        f"Maximum total probation period is {MAX_TOTAL_PROBATION_DAYS} days ({DEFAULT_PROBATION_DAYS} days + {max_allowed_extension_days} days extension). "
                        f"Current extensions total: {current_total_extension_days} days. "
                        f"Maximum additional extension allowed: {remaining_extension_days} days."
                    )


class ProbationExtensionRequest(models.Model):
    """
    Model to track probation extension requests that require manager approval.
    Implements maker-checker workflow where users can request but only managers can approve.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    probation_period = models.ForeignKey(
        WorkerProbationPeriod, 
        on_delete=models.CASCADE,
        related_name='extension_requests', 
        verbose_name='Probation Period'
    )
    extension_duration_days = models.IntegerField('Requested Extension Duration (Days)')
    reason = models.TextField('Reason for Extension Request')
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Request details
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='probation_extension_requests', 
        verbose_name='Requested By'
    )
    requested_at = models.DateTimeField('Requested At', auto_now_add=True)
    
    # Approval/Rejection details
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reviewed_probation_extension_requests', 
        verbose_name='Reviewed By'
    )
    reviewed_at = models.DateTimeField('Reviewed At', null=True, blank=True)
    review_comments = models.TextField('Review Comments', blank=True, help_text='Manager comments on approval/rejection')
    
    # Tracking
    created_at = models.DateTimeField('Created At', auto_now_add=True)
    updated_at = models.DateTimeField('Updated At', auto_now=True)

    def __str__(self):
        return f"{self.probation_period.worker.get_full_name()} - {self.extension_duration_days} days request ({self.get_status_display()})"

    class Meta:
        verbose_name = 'Probation Extension Request'
        verbose_name_plural = 'Probation Extension Requests'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Set reviewed_at when status changes to approved/rejected
        if self.status in ['approved', 'rejected'] and not self.reviewed_at:
            from django.utils import timezone
            self.reviewed_at = timezone.now()
        
        super().save(*args, **kwargs)
        
        # If approved, create the actual extension
        if self.status == 'approved' and not hasattr(self, '_extension_created'):
            self._extension_created = True  # Prevent infinite loop
            self.create_extension()

    def create_extension(self):
        """Create the actual WorkerProbationExtension when request is approved."""
        WorkerProbationExtension.objects.create(
            probation_period=self.probation_period,
            extension_duration_days=self.extension_duration_days,
            reason=f"Approved extension request: {self.reason}",
            approved_by=self.reviewed_by,
            created_by=self.requested_by,
        )

    def can_be_cancelled(self):
        """Check if this request can be cancelled by the requester."""
        return self.status == 'pending'

    def get_status_color(self):
        """Get Bootstrap color class for status."""
        status_colors = {
            'pending': 'warning',
            'approved': 'success', 
            'rejected': 'danger',
            'cancelled': 'secondary'
        }
        return status_colors.get(self.status, 'secondary')

    def clean(self):
        from django.core.exceptions import ValidationError
        
        if self.extension_duration_days is not None and self.extension_duration_days <= 0:
            raise ValidationError("Extension duration must be positive.")
        
        # Check if probation period can be extended
        if self.probation_period and not self.probation_period.can_be_extended():
            raise ValidationError("This probation period cannot be extended further.")
        
        # Business Rule: Total probation period cannot exceed 30 days
        if self.probation_period:
            max_allowed = self.probation_period.get_max_allowed_extension_days()
            if self.extension_duration_days > max_allowed:
                raise ValidationError(
                    f"Requested extension exceeds maximum allowed. "
                    f"Maximum additional extension allowed: {max_allowed} days."
                )


class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='zone_created_departments')

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']


class Position(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    level = models.PositiveIntegerField(help_text="Position level in the organization hierarchy")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='zone_created_positions')

    def __str__(self):
        return f"{self.name} - {self.department.name}"

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"
        ordering = ['department', 'level', 'name']
        unique_together = ['name', 'department']


class WorkerChangeHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('status_changed', 'Status Changed'),
        ('assigned', 'Zone/Building Assigned'),
        ('probation_started', 'Probation Started'),
        ('probation_passed', 'Probation Passed'),
        ('probation_extended', 'Probation Extended'),
        ('probation_failed', 'Probation Failed'),
        ('document_added', 'Document Added'),
        ('document_updated', 'Document Updated'),
        ('document_deleted', 'Document Deleted'),
    ]
    
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='change_history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    field_name = models.CharField(max_length=100, blank=True, null=True, help_text="Name of the changed field")
    old_value = models.TextField(blank=True, null=True, help_text="Previous value")
    new_value = models.TextField(blank=True, null=True, help_text="New value")
    description = models.TextField(blank=True, null=True, help_text="Human readable description of the change")
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.worker.get_full_name()} - {self.get_action_display()} ({self.changed_at.strftime('%Y-%m-%d %H:%M')})"
    
    class Meta:
        verbose_name = "Worker Change History"
        verbose_name_plural = "Worker Change History"
        ordering = ['-changed_at']
        
    def get_change_summary(self):
        """Get a human-readable summary of the change"""
        if self.description:
            return self.description
            
        if self.field_name and self.old_value and self.new_value:
            field_display = self.field_name.replace('_', ' ').title()
            return f"{field_display} changed from '{self.old_value}' to '{self.new_value}'"
        elif self.field_name and self.new_value:
            field_display = self.field_name.replace('_', ' ').title()
            return f"{field_display} set to '{self.new_value}'"
        
        return self.get_action_display()
    
    def get_icon_class(self):
        """Get Font Awesome icon class for the action"""
        icon_map = {
            'created': 'fa-plus-circle text-success',
            'updated': 'fa-edit text-primary',
            'deleted': 'fa-trash text-danger',
            'status_changed': 'fa-exchange-alt text-warning',
            'assigned': 'fa-map-marker-alt text-info',
            'probation_started': 'fa-hourglass-start text-warning',
            'probation_passed': 'fa-check-circle text-success',
            'probation_extended': 'fa-clock text-orange',
            'probation_failed': 'fa-times-circle text-danger',
            'document_added': 'fa-file-plus text-success',
            'document_updated': 'fa-file-edit text-primary',
            'document_deleted': 'fa-file-minus text-danger',
        }
        return icon_map.get(self.action, 'fa-info-circle text-secondary')
