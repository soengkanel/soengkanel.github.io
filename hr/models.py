# models for employees
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import date, datetime, timedelta
from calendar import monthrange
from decimal import Decimal
from .utils import encrypt_field, decrypt_field
from core.encryption import EncryptedCharField, EncryptedTextField, EncryptedEmailField
from core.encrypted_fields import EncryptedFileField, EncryptedImageField, FileEncryptionMixin
import uuid
import os

def validate_image_file_extension(value):
    """Validate that the uploaded file is an image."""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.enc']  # Include .enc for encrypted files
    if not ext in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Please upload JPG, PNG, GIF, or BMP files only.'))

def validate_image_file_size(value):
    """File size validation removed - no size limits."""
    pass

class Department(models.Model):
    name = models.CharField(_('Department Name'), max_length=100)
    code = models.CharField(_('Department Code'), max_length=20, unique=True)
    description = models.TextField(_('Description'), blank=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                              related_name='children', verbose_name=_('Parent Department'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
        ordering = ['name']

class Position(models.Model):
    name = models.CharField(_('Position Name'), max_length=100)
    code = models.CharField(_('Position Code'), max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, 
                                 related_name='positions', verbose_name=_('Department'))
    description = models.TextField(_('Description'), blank=True)
    level = models.IntegerField(_('Level'), default=1)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.department.name}"

    class Meta:
        verbose_name = _('Position')
        verbose_name_plural = _('Positions')
        ordering = ['department', 'level']

class Employee(FileEncryptionMixin, models.Model):
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
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

    
    EMPLOYMENT_STATUS_CHOICES = [
        ('active', _('Active')),
        ('on_leave', _('On Leave')),
        ('suspended', _('Suspended')),
        ('terminated', _('Terminated')),
    ]

    EMPLOYEE_TYPE_CHOICES = [
        ('onsite', _('Onsite')),
        ('backoffice', _('Back Office')),
    ]

    WORK_TYPE_CHOICES = [
        ('office', _('Office')),
        ('onsite', _('Onsite')),
    ]

    # Employee Information
    employee_id = models.CharField(_('Employee ID'), max_length=20, unique=True, blank=True)
    user = models.OneToOneField('auth.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='employee')
    
    # Basic Information
    first_name = models.CharField(_('First Name'), max_length=100)
    last_name = models.CharField(_('Last Name'), max_length=100)
    photo = EncryptedImageField(_('Photo'), upload_to='employee_photos/', blank=True, null=True,
                             validators=[validate_image_file_extension, validate_image_file_size],
                             help_text=_('Upload employee photo (JPG, PNG, GIF, BMP formats supported) - Automatically encrypted'))
    gender = models.CharField(_('Gender'), max_length=1, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(_('Date of Birth'))
    nationality = models.CharField(_('Nationality'), max_length=50, choices=NATIONALITY_CHOICES)
    
    # Contact Information
    phone_regex = RegexValidator(
        regex=r'^(\+?855|0)\d{8,10}$',
        message=_("Phone number must be in Cambodia format: +855xxxxxxxx or 0xxxxxxxx (8-10 digits after prefix)")
    )
    phone_number = EncryptedCharField(_('Phone Number'), validators=[phone_regex], max_length=17, blank=True)
    email = EncryptedEmailField(_('Email'), blank=True, null=True)
    address = EncryptedTextField(_('Address'))
    emergency_contact_name = EncryptedCharField(_('Emergency Contact Name'), max_length=100)
    emergency_contact_phone = EncryptedCharField(_('Emergency Contact Phone'), validators=[phone_regex], max_length=17)
    
    # Employment Information
    department = models.ForeignKey(Department, on_delete=models.SET_NULL,
                                 null=True, blank=True, related_name='employees',
                                 verbose_name=_('Department'))
    position = models.ForeignKey(Position, on_delete=models.SET_NULL,
                               null=True, blank=True, related_name='employees',
                               verbose_name=_('Position'))
    employment_status = models.CharField(_('Employment Status'), max_length=20,
                                       choices=EMPLOYMENT_STATUS_CHOICES, default='active')
    employee_type = models.CharField(_('Employee Type'), max_length=20,
                                   choices=EMPLOYEE_TYPE_CHOICES, default='backoffice')
    work_type = models.CharField(_('Work Type'), max_length=20,
                                choices=WORK_TYPE_CHOICES, default='office')
    hire_date = models.DateField(_('Hire Date'))
    end_date = models.DateField(_('End Date'), null=True, blank=True)

    # Manager and Compensation
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='subordinates', verbose_name=_('Manager'))
    salary = models.DecimalField(_('Salary'), max_digits=12, decimal_places=2, null=True, blank=True)
    number_of_dependents = models.PositiveIntegerField(
        _('Number of Dependents'),
        default=0,
        help_text=_('Number of spouse/children for tax deduction (150,000 KHR per dependent)')
    )
    work_location = models.CharField(_('Work Location'), max_length=200, blank=True)
    branch = models.ForeignKey('company.Branch', on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='employees', verbose_name=_('Branch'))

    # Notes
    notes = EncryptedTextField(_('Notes'), blank=True)
    
    # System Information
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _('Employee')
        verbose_name_plural = _('Employees')
        ordering = ['employee_id']

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_full_name(self):
        """Return full name of employee (method version for Django compatibility)"""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_active(self):
        return self.employment_status == 'active'
    
    @property
    def photo_url(self):
        """Return the URL of the employee photo or a default placeholder."""
        if self.photo and self.photo.name:
            # Check if the file actually exists before serving
            import os
            try:
                if hasattr(self.photo, 'path') and os.path.exists(self.photo.path):
                    # File exists, use secure URL for encrypted photos
                    from django.urls import reverse
                    import time
                    
                    base_url = reverse('hr:serve_employee_photo', kwargs={'employee_id': self.id})
                    
                    # Add cache-busting parameter based on file modification time
                    try:
                        mtime = int(os.path.getmtime(self.photo.path))
                        return f"{base_url}?v={mtime}"
                    except (OSError, AttributeError):
                        timestamp = int(self.updated_at.timestamp()) if self.updated_at else int(time.time())
                        return f"{base_url}?v={timestamp}"
                else:
                    # File doesn't exist, fall back to default avatar
                    return '/static/images/default-avatar.svg'
            except (OSError, AttributeError, ValueError):
                # Any error accessing the file, use default avatar
                return '/static/images/default-avatar.svg'
        return '/static/images/default-avatar.svg'  # Default avatar
    
    def has_photo(self):
        """Check if the employee has a photo uploaded and the file exists."""
        if not self.photo or not self.photo.name:
            return False
        
        try:
            # Check if the file actually exists
            import os
            if hasattr(self.photo, 'path'):
                return os.path.exists(self.photo.path)
            else:
                # If no path attribute, assume the file exists (for remote storage)
                return True
        except (OSError, AttributeError, ValueError):
            # If there's any error accessing the file, consider it as not having a photo
            return False
    
    def get_nationality_display_custom(self):
        """Get the display name for nationality."""
        return dict(self.NATIONALITY_CHOICES).get(self.nationality, self.nationality)

    def save(self, *args, **kwargs):
        # Auto-generate employee_id if not provided
        if not self.employee_id:
            self.employee_id = self.generate_employee_id()
        
        # Handle photo replacement - delete old photo when new one is uploaded
        if self.pk:  # Only for existing employees (not new ones)
            try:
                old_instance = Employee.objects.get(pk=self.pk)
                # Check if photo has changed
                if old_instance.photo and old_instance.photo != self.photo:
                    # Delete the old photo file
                    import os
                    if os.path.isfile(old_instance.photo.path):
                        os.remove(old_instance.photo.path)
            except Employee.DoesNotExist:
                # This shouldn't happen, but handle gracefully
                pass
            except Exception as e:
                pass
        
        # Note: Encryption is now handled by the form to prevent unnecessary re-encryption
        # This save method is kept simple to avoid audit log issues
        super().save(*args, **kwargs)
    
    def generate_employee_id(self):
        """Generate unique Employee ID in format EMP2024001, EMP2024002, etc."""
        from django.utils import timezone
        year = timezone.now().year
        
        # Get the highest existing employee ID for this year
        last_employee = Employee.objects.filter(
            employee_id__startswith=f'EMP{year}'
        ).order_by('-employee_id').first()
        
        if last_employee:
            # Extract the sequence number and increment
            try:
                last_seq = int(last_employee.employee_id[-3:])
                new_seq = last_seq + 1
            except (ValueError, IndexError):
                new_seq = 1
        else:
            new_seq = 1
        
        return f'EMP{year}{new_seq:03d}'



    @property 
    def current_id_card(self):
        """Get the most recent/current ID card for this employee."""
        return self.employee_id_cards.order_by('-created_at').first()
    
    @property
    def id_card_status(self):
        """Get the status of employee's current ID card."""
        card = self.current_id_card
        if card:
            return card.status
        return None
    
    @property
    def has_delivered_id_card(self):
        """Check if employee has a delivered ID card."""
        return self.employee_id_cards.filter(status='delivered').exists()

    # User relationship helper methods
    def has_user_account(self):
        """Check if employee has an associated user account."""
        return self.user is not None

    def create_user_account(self, username=None, email=None, password=None, commit=True):
        """Create a user account for this employee."""
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import make_password

        if self.user:
            raise ValueError("Employee already has a user account")

        # Generate username if not provided
        if not username:
            username = self.employee_id.lower()
            # Ensure username is unique
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}_{counter}"
                counter += 1

        # Use employee email if available, otherwise generate one
        if not email and self.email:
            email = str(self.email)  # Decrypt if needed
        elif not email:
            email = f"{username}@company.com"

        # Create user
        user = User(
            username=username,
            email=email,
            first_name=self.first_name,
            last_name=self.last_name,
            is_active=self.is_active
        )

        if password:
            user.password = make_password(password)
        else:
            # Generate temporary password
            import secrets
            import string
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            user.password = make_password(temp_password)

        if commit:
            user.save()
            self.user = user
            self.save()

        return user

    def get_user_permissions(self):
        """Get all permissions for the associated user."""
        if not self.user:
            return []
        return self.user.get_all_permissions()

    def has_permission(self, permission):
        """Check if the employee's user has a specific permission."""
        if not self.user:
            return False
        return self.user.has_perm(permission)

    def is_manager(self):
        """Check if employee is a manager (has management permissions)."""
        return self.has_permission('hr.change_employee') or self.has_permission('attendance.can_approve_overtime')

    def can_approve_attendance_requests(self):
        """Check if employee can approve attendance-related requests."""
        return self.has_permission('attendance.can_approve_overtime') or self.has_permission('attendance.can_approve_corrections')
    
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
    
    def delete(self, *args, **kwargs):
        """Custom delete method to remove physical files and cleanup related records when employee is deleted."""
        import os
        from django.db import transaction

        # Set a flag to indicate we're deleting an employee
        # This flag is checked by signal handlers to prevent logging during deletion
        setattr(self, '_being_deleted', True)

        # Store employee info for logging
        employee_id = self.employee_id
        full_name = self.full_name

        with transaction.atomic():
            try:
                # Delete employee photo file if it exists
                if self.photo and hasattr(self.photo, 'path'):
                    try:
                        if os.path.exists(self.photo.path):
                            os.remove(self.photo.path)
                    except Exception as e:
                        pass

                # Delete all document files for this employee
                for document in self.documents.all():
                    # Mark document's employee as being deleted to prevent signal issues
                    setattr(document, '_employee_being_deleted', True)
                    if document.document_file and hasattr(document.document_file, 'path'):
                        try:
                            if os.path.exists(document.document_file.path):
                                os.remove(document.document_file.path)
                        except Exception as e:
                            pass

                # Call the parent delete method to handle database deletion
                # CASCADE will automatically delete related records:
                # - EmployeeDocument, EmployeeChangeHistory, ProbationPeriod, IDCardRequest
                # - Leave allocations, attendance records, salary records, etc.
                # Signal handlers will check _being_deleted flag and skip logging
                super().delete(*args, **kwargs)

            except Exception as e:
                # Log the error but don't prevent deletion
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error during employee deletion: {str(e)}")
                raise

class EmployeeDocument(FileEncryptionMixin, models.Model):
    DOCUMENT_TYPES = [
        ('id_card', _('ID Card')),
        ('certificate', _('Certificate')),
        ('other', _('Other')),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, 
                               related_name='documents', verbose_name=_('Employee'))
    document_type = models.CharField(_('Document Type'), max_length=20, choices=DOCUMENT_TYPES)
    document_number = models.CharField(_('Document Number'), max_length=50)
    issue_date = models.DateField(_('Issue Date'))
    expiry_date = models.DateField(_('Expiry Date'))
    issuing_authority = models.CharField(_('Issuing Authority'), max_length=100)
    document_file = EncryptedFileField(_('Document File'), upload_to='employee_documents/')
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.get_document_type_display()}"
    
    def delete(self, *args, **kwargs):
        """Custom delete method to remove physical document file when document is deleted."""
        import os
        
        # Delete document file if it exists
        if self.document_file and hasattr(self.document_file, 'path'):
            try:
                if os.path.exists(self.document_file.path):
                    os.remove(self.document_file.path)
            except Exception as e:
                # Don't prevent deletion
                pass
        
        # Call the parent delete method to handle database deletion
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = _('Employee Document')
        verbose_name_plural = _('Employee Documents')
        ordering = ['-issue_date']

class EmployeeHistory(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, 
                               related_name='history', verbose_name=_('Employee'))
    event_type = models.CharField(_('Event Type'), max_length=50)
    description = models.TextField(_('Description'))
    date = models.DateField(_('Date'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.event_type}"

    class Meta:
        verbose_name = _('Employee History')
        verbose_name_plural = _('Employee History')
        ordering = ['-date']

class EmployeeChangeHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('deleted', 'Deleted'),
        ('status_changed', 'Status Changed'),
        ('photo_updated', 'Photo Updated'),
        ('document_added', 'Document Added'),
        ('document_removed', 'Document Removed'),
        ('probation_started', 'Probation Started'),
        ('probation_extended', 'Probation Extended'),
        ('probation_completed', 'Probation Completed'),
        ('id_card_requested', 'ID Card Requested'),
        ('id_card_issued', 'ID Card Issued'),
        ('employment_ended', 'Employment Ended'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='change_history', null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    field_name = models.CharField(max_length=100, blank=True, null=True)
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    changed_by = models.CharField(max_length=150, blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.CharField(max_length=500, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    additional_info = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.employee} - {self.get_action_display()} ({self.timestamp})"
    
    class Meta:
        verbose_name = _('Employee Change History')
        verbose_name_plural = _('Employee Change History')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['employee', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]

class ProbationPeriod(models.Model):
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('extended', _('Extended')),
        ('failed', _('Failed')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, 
                               related_name='probation_periods', verbose_name=_('Employee'))
    start_date = models.DateField(_('Start Date'))
    original_end_date = models.DateField(_('Original End Date'))
    actual_end_date = models.DateField(_('Actual End Date'), null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='active')
    evaluation_notes = models.TextField(_('Evaluation Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.start_date} to {self.actual_end_date or self.original_end_date}"

    class Meta:
        verbose_name = _('Probation Period')
        verbose_name_plural = _('Probation Periods')
        ordering = ['-start_date']

class ProbationExtension(models.Model):
    probation_period = models.ForeignKey(ProbationPeriod, on_delete=models.CASCADE,
                                       related_name='extensions', verbose_name=_('Probation Period'))
    extension_duration_days = models.IntegerField(_('Extension Duration (Days)'))
    reason = models.TextField(_('Reason for Extension'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.probation_period} - {self.extension_duration_days} days extension"

    class Meta:
        verbose_name = _('Probation Extension')
        verbose_name_plural = _('Probation Extensions')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.probation_period.actual_end_date:
            # Update the actual end date of the probation period
            from datetime import timedelta
            self.probation_period.actual_end_date = (
                self.probation_period.original_end_date + timedelta(days=self.extension_duration_days)
            )
            self.probation_period.status = 'extended'
            self.probation_period.save()
        super().save(*args, **kwargs)

class IDCard(models.Model):
    CARD_TYPE_CHOICES = [
        ('regular', _('Regular')),
        ('temporary', _('Temporary')),
        ('visitor', _('Visitor')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                               related_name='id_cards', verbose_name=_('Employee'))
    card_number = models.CharField(_('Card Number'), max_length=50, unique=True)
    card_type = models.CharField(_('Card Type'), max_length=20, choices=CARD_TYPE_CHOICES, default='regular')
    issue_date = models.DateField(_('Issue Date'))
    expiry_date = models.DateField(_('Expiry Date'))
    qr_code = models.CharField(_('QR Code'), max_length=255, unique=True)
    barcode = models.CharField(_('Barcode'), max_length=255, unique=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    card_request = models.OneToOneField('IDCardRequest', on_delete=models.SET_NULL, null=True,
                                      related_name='issued_card', verbose_name=_('Card Request'))
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.card_number} ({self.get_card_type_display()})"

    class Meta:
        verbose_name = _('ID Card')
        verbose_name_plural = _('ID Cards')
        ordering = ['-issue_date']

    def save(self, *args, **kwargs):
        if not self.card_number:
            # Generate a unique card number
            self.card_number = f"CARD-{uuid.uuid4().hex[:8].upper()}"
        if not self.qr_code:
            # Generate QR code data
            self.qr_code = f"QR-{uuid.uuid4().hex}"
        if not self.barcode:
            # Generate barcode data
            self.barcode = f"BAR-{uuid.uuid4().hex}"
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    @property
    def days_until_expiry(self):
        return (self.expiry_date - timezone.now().date()).days

class IDCardRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('new', _('New ID Card')),
        ('replacement', _('Replacement')),
        ('renewal', _('Renewal')),
    ]

    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('printing', _('Printing')),
        ('ready', _('Ready for Pickup')),
        ('delivered', _('Delivered')),
        ('cancelled', _('Cancelled')),
    ]

    REPLACEMENT_REASON_CHOICES = [
        ('lost', _('Lost')),
        ('damaged', _('Damaged')),
        ('stolen', _('Stolen')),
        ('expired', _('Expired')),
        ('other', _('Other')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE,
                               related_name='id_card_requests', verbose_name=_('Employee'))
    request_type = models.CharField(_('Request Type'), max_length=20, choices=REQUEST_TYPE_CHOICES)
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    replacement_reason = models.CharField(_('Replacement Reason'), max_length=20, 
                                        choices=REPLACEMENT_REASON_CHOICES, null=True, blank=True)
    request_date = models.DateField(_('Request Date'), auto_now_add=True)
    approved_date = models.DateField(_('Approved Date'), null=True, blank=True)
    printed_date = models.DateField(_('Printed Date'), null=True, blank=True)
    delivery_date = models.DateField(_('Delivery Date'), null=True, blank=True)
    validity_period_months = models.IntegerField(_('Validity Period (Months)'), default=12)
    notes = models.TextField(_('Notes'), blank=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    def __str__(self):
        return f"{self.employee} - {self.get_request_type_display()} ({self.get_status_display()})"

    class Meta:
        verbose_name = _('ID Card Request')
        verbose_name_plural = _('ID Card Requests')
        ordering = ['-request_date']

    def save(self, *args, **kwargs):
        # Update status dates based on status changes
        if self.status == 'approved' and not self.approved_date:
            self.approved_date = timezone.now().date()
        elif self.status == 'printing' and not self.printed_date:
            self.printed_date = timezone.now().date()
        elif self.status == 'delivered' and not self.delivery_date:
            self.delivery_date = timezone.now().date()
        super().save(*args, **kwargs)


# ============ EMPLOYEE ONBOARDING MODELS ============

class OnboardingTemplate(models.Model):
    """Template for onboarding process configuration"""
    name = models.CharField(_('Template Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='onboarding_templates', verbose_name=_('Department'))
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True, blank=True,
                               related_name='onboarding_templates', verbose_name=_('Position'))

    # Duration settings
    total_duration_days = models.PositiveIntegerField(_('Total Duration (Days)'), default=30)
    probation_period_days = models.PositiveIntegerField(_('Probation Period (Days)'), default=90)

    # Auto-assign settings
    assign_buddy = models.BooleanField(_('Assign Buddy'), default=True)
    create_user_account = models.BooleanField(_('Create User Account'), default=True)
    send_welcome_email = models.BooleanField(_('Send Welcome Email'), default=True)

    is_active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Onboarding Template')
        verbose_name_plural = _('Onboarding Templates')
        ordering = ['name']

    def __str__(self):
        return self.name


class OnboardingTask(models.Model):
    """Individual tasks in the onboarding process"""
    TASK_TYPE_CHOICES = [
        ('documentation', _('Documentation')),
        ('orientation', _('Orientation')),
        ('training', _('Training')),
        ('setup', _('System Setup')),
        ('meeting', _('Meeting')),
        ('review', _('Review')),
        ('other', _('Other')),
    ]

    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
        ('critical', _('Critical')),
    ]

    template = models.ForeignKey(OnboardingTemplate, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(_('Task Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    task_type = models.CharField(_('Task Type'), max_length=20, choices=TASK_TYPE_CHOICES, default='other')
    priority = models.CharField(_('Priority'), max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Timing
    due_after_days = models.PositiveIntegerField(_('Due After (Days)'), default=1,
                                               help_text=_('Days after onboarding start'))
    estimated_hours = models.FloatField(_('Estimated Hours'), default=1.0)

    # Assignment
    assigned_to_role = models.CharField(_('Assigned To Role'), max_length=50, blank=True,
                                      help_text=_('HR, Manager, IT, etc.'))
    requires_buddy = models.BooleanField(_('Requires Buddy'), default=False)

    # Requirements
    requires_approval = models.BooleanField(_('Requires Approval'), default=False)
    requires_attachment = models.BooleanField(_('Requires Attachment'), default=False)

    # Order and status
    order = models.PositiveIntegerField(_('Order'), default=1)
    is_mandatory = models.BooleanField(_('Mandatory'), default=True)
    is_active = models.BooleanField(_('Active'), default=True)

    class Meta:
        verbose_name = _('Onboarding Task')
        verbose_name_plural = _('Onboarding Tasks')
        ordering = ['template', 'order', 'due_after_days']

    def __str__(self):
        return f"{self.template.name} - {self.title}"


class EmployeeOnboarding(models.Model):
    """Employee onboarding process instance"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('paused', _('Paused')),
        ('cancelled', _('Cancelled')),
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='onboarding')
    template = models.ForeignKey(OnboardingTemplate, on_delete=models.CASCADE)

    # Process details
    start_date = models.DateField(_('Start Date'))
    expected_completion_date = models.DateField(_('Expected Completion Date'))
    actual_completion_date = models.DateField(_('Actual Completion Date'), null=True, blank=True)

    # Status and progress
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')
    progress_percentage = models.FloatField(_('Progress %'), default=0.0)
    total_tasks = models.PositiveIntegerField(_('Total Tasks'), default=0)
    completed_tasks = models.PositiveIntegerField(_('Completed Tasks'), default=0)

    # Assignments
    hr_representative = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='hr_onboardings', verbose_name=_('HR Representative'))
    buddy = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                            related_name='buddy_onboardings', verbose_name=_('Onboarding Buddy'))
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='manager_onboardings', verbose_name=_('Manager'))

    # Notes and feedback
    notes = models.TextField(_('Notes'), blank=True)
    employee_feedback = models.TextField(_('Employee Feedback'), blank=True)
    hr_feedback = models.TextField(_('HR Feedback'), blank=True)

    # System fields
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_onboardings')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Employee Onboarding')
        verbose_name_plural = _('Employee Onboardings')
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.employee.full_name} - Onboarding ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        # Calculate expected completion date
        if self.start_date and self.template:
            self.expected_completion_date = self.start_date + timedelta(days=self.template.total_duration_days)

        # Update progress
        if self.total_tasks > 0:
            self.progress_percentage = (self.completed_tasks / self.total_tasks) * 100

        # Auto-complete if all tasks done
        if self.progress_percentage >= 100 and self.status == 'in_progress':
            self.status = 'completed'
            if not self.actual_completion_date:
                self.actual_completion_date = timezone.now().date()

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status in ['completed', 'cancelled']:
            return False
        return self.expected_completion_date < timezone.now().date()

    @property
    def days_remaining(self):
        if self.status in ['completed', 'cancelled']:
            return 0
        delta = self.expected_completion_date - timezone.now().date()
        return max(0, delta.days)


class OnboardingTaskInstance(models.Model):
    """Instance of an onboarding task for a specific employee"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('skipped', _('Skipped')),
        ('overdue', _('Overdue')),
    ]

    onboarding = models.ForeignKey(EmployeeOnboarding, on_delete=models.CASCADE, related_name='task_instances')
    task = models.ForeignKey(OnboardingTask, on_delete=models.CASCADE)

    # Task details (copied from template for tracking)
    title = models.CharField(_('Title'), max_length=200)
    description = models.TextField(_('Description'), blank=True)
    task_type = models.CharField(_('Task Type'), max_length=20)
    priority = models.CharField(_('Priority'), max_length=10)
    estimated_hours = models.FloatField(_('Estimated Hours'), default=1.0)

    # Scheduling
    due_date = models.DateField(_('Due Date'))
    start_date = models.DateField(_('Start Date'), null=True, blank=True)
    completion_date = models.DateField(_('Completion Date'), null=True, blank=True)

    # Assignment and status
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='assigned_onboarding_tasks')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='pending')

    # Completion details
    actual_hours = models.FloatField(_('Actual Hours'), null=True, blank=True)
    completion_notes = models.TextField(_('Completion Notes'), blank=True)
    attachments = models.FileField(_('Attachments'), upload_to='onboarding_attachments/', null=True, blank=True)

    # Approval
    requires_approval = models.BooleanField(_('Requires Approval'), default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_onboarding_tasks')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Onboarding Task Instance')
        verbose_name_plural = _('Onboarding Task Instances')
        ordering = ['due_date', 'priority']

    def __str__(self):
        return f"{self.onboarding.employee.full_name} - {self.title}"

    def save(self, *args, **kwargs):
        # Update status based on dates
        if self.completion_date and self.status not in ['completed', 'skipped']:
            self.status = 'completed'
        elif self.due_date < timezone.now().date() and self.status == 'pending':
            self.status = 'overdue'

        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status not in ['completed', 'skipped']

    def mark_completed(self, user, notes='', actual_hours=None):
        """Mark task as completed"""
        self.status = 'completed'
        self.completion_date = timezone.now().date()
        self.completion_notes = notes
        if actual_hours:
            self.actual_hours = actual_hours
        if not self.assigned_to:
            self.assigned_to = user
        self.save()

        # Update onboarding progress
        self.onboarding.completed_tasks = self.onboarding.task_instances.filter(status='completed').count()
        self.onboarding.save()


# ============ PROMOTION & TRANSFER MODELS ============

class PromotionTransfer(models.Model):
    """Employee promotion and transfer management"""
    TYPE_CHOICES = [
        ('promotion', _('Promotion')),
        ('transfer', _('Transfer')),
        ('demotion', _('Demotion')),
        ('lateral_move', _('Lateral Move')),
    ]

    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('implemented', _('Implemented')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='promotion_transfers')
    change_type = models.CharField(_('Change Type'), max_length=20, choices=TYPE_CHOICES)

    # Current details
    current_position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='current_promotions',
                                       verbose_name=_('Current Position'))
    current_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='current_promotions',
                                         verbose_name=_('Current Department'))

    # New details
    new_position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='new_promotions',
                                   verbose_name=_('New Position'))
    new_department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='new_promotions',
                                     verbose_name=_('New Department'))

    # Timing
    effective_date = models.DateField(_('Effective Date'))
    announcement_date = models.DateField(_('Announcement Date'), null=True, blank=True)

    # Details
    reason = models.TextField(_('Reason'))
    salary_change = models.DecimalField(_('Salary Change'), max_digits=12, decimal_places=2, default=0)
    salary_change_percentage = models.FloatField(_('Salary Change %'), default=0)

    # Approval workflow
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_promotions')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_promotions')
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)

    # Implementation
    implemented_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='implemented_promotions')
    implemented_at = models.DateTimeField(_('Implemented At'), null=True, blank=True)

    # Notes
    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Promotion/Transfer')
        verbose_name_plural = _('Promotions/Transfers')
        ordering = ['-effective_date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.get_change_type_display()} ({self.effective_date})"

    def save(self, *args, **kwargs):
        # Update status timestamps
        if self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        elif self.status == 'implemented' and not self.implemented_at:
            self.implemented_at = timezone.now()

        super().save(*args, **kwargs)


# ============ EXIT INTERVIEW MODELS ============

class ExitInterview(models.Model):
    """Exit interview management"""
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('in_progress', _('In Progress')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
    ]

    REASON_CHOICES = [
        ('resignation', _('Resignation')),
        ('termination', _('Termination')),
        ('retirement', _('Retirement')),
        ('contract_end', _('Contract End')),
        ('other', _('Other')),
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='exit_interview')
    exit_reason = models.CharField(_('Exit Reason'), max_length=20, choices=REASON_CHOICES)
    last_working_day = models.DateField(_('Last Working Day'))

    # Interview details
    interview_date = models.DateField(_('Interview Date'), null=True, blank=True)
    interviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='conducted_exit_interviews')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='scheduled')

    # Ratings (1-5 scale)
    job_satisfaction = models.PositiveSmallIntegerField(_('Job Satisfaction'), null=True, blank=True)
    work_environment = models.PositiveSmallIntegerField(_('Work Environment'), null=True, blank=True)
    management_quality = models.PositiveSmallIntegerField(_('Management Quality'), null=True, blank=True)
    career_development = models.PositiveSmallIntegerField(_('Career Development'), null=True, blank=True)
    work_life_balance = models.PositiveSmallIntegerField(_('Work-Life Balance'), null=True, blank=True)
    compensation_benefits = models.PositiveSmallIntegerField(_('Compensation & Benefits'), null=True, blank=True)

    # Feedback questions
    liked_most = models.TextField(_('What did you like most about working here?'), blank=True)
    liked_least = models.TextField(_('What did you like least about working here?'), blank=True)
    improvements = models.TextField(_('What improvements would you suggest?'), blank=True)
    recommend_company = models.BooleanField(_('Would you recommend this company?'), null=True, blank=True)

    # Additional feedback
    additional_comments = models.TextField(_('Additional Comments'), blank=True)
    confidential_feedback = models.TextField(_('Confidential Feedback'), blank=True)

    # Follow-up
    follow_up_required = models.BooleanField(_('Follow-up Required'), default=False)
    follow_up_notes = models.TextField(_('Follow-up Notes'), blank=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_exit_interviews')
    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Exit Interview')
        verbose_name_plural = _('Exit Interviews')
        ordering = ['-last_working_day']

    def __str__(self):
        return f"{self.employee.full_name} - Exit Interview ({self.get_status_display()})"

    @property
    def overall_satisfaction(self):
        """Calculate overall satisfaction score"""
        ratings = [
            self.job_satisfaction, self.work_environment, self.management_quality,
            self.career_development, self.work_life_balance, self.compensation_benefits
        ]
        valid_ratings = [r for r in ratings if r is not None]
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        return None


class ExitChecklist(models.Model):
    """Exit checklist for departing employees"""
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('not_applicable', _('Not Applicable')),
    ]

    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='exit_checklist')

    # HR tasks
    final_interview_completed = models.CharField(_('Final Interview'), max_length=20, choices=STATUS_CHOICES, default='pending')
    benefits_explained = models.CharField(_('Benefits Explained'), max_length=20, choices=STATUS_CHOICES, default='pending')
    cobra_forms = models.CharField(_('COBRA Forms'), max_length=20, choices=STATUS_CHOICES, default='pending')
    final_paycheck = models.CharField(_('Final Paycheck'), max_length=20, choices=STATUS_CHOICES, default='pending')

    # IT tasks
    laptop_returned = models.CharField(_('Laptop Returned'), max_length=20, choices=STATUS_CHOICES, default='pending')
    phone_returned = models.CharField(_('Phone Returned'), max_length=20, choices=STATUS_CHOICES, default='pending')
    id_card_returned = models.CharField(_('ID Card Returned'), max_length=20, choices=STATUS_CHOICES, default='pending')
    access_revoked = models.CharField(_('System Access Revoked'), max_length=20, choices=STATUS_CHOICES, default='pending')
    email_deactivated = models.CharField(_('Email Deactivated'), max_length=20, choices=STATUS_CHOICES, default='pending')

    # Finance tasks
    expense_reports = models.CharField(_('Expense Reports Submitted'), max_length=20, choices=STATUS_CHOICES, default='pending')
    company_credit_card = models.CharField(_('Company Credit Card Returned'), max_length=20, choices=STATUS_CHOICES, default='pending')
    outstanding_advances = models.CharField(_('Outstanding Advances Cleared'), max_length=20, choices=STATUS_CHOICES, default='pending')

    # Manager tasks
    knowledge_transfer = models.CharField(_('Knowledge Transfer'), max_length=20, choices=STATUS_CHOICES, default='pending')
    project_handover = models.CharField(_('Project Handover'), max_length=20, choices=STATUS_CHOICES, default='pending')
    keys_returned = models.CharField(_('Keys Returned'), max_length=20, choices=STATUS_CHOICES, default='pending')

    # General
    locker_cleared = models.CharField(_('Locker Cleared'), max_length=20, choices=STATUS_CHOICES, default='pending')
    uniform_returned = models.CharField(_('Uniform Returned'), max_length=20, choices=STATUS_CHOICES, default='pending')

    # Completion
    all_cleared_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    all_cleared_date = models.DateField(_('All Cleared Date'), null=True, blank=True)
    notes = models.TextField(_('Notes'), blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Exit Checklist')
        verbose_name_plural = _('Exit Checklists')

    def __str__(self):
        return f"{self.employee.full_name} - Exit Checklist"

    @property
    def completion_percentage(self):
        """Calculate completion percentage"""
        fields = [
            'final_interview_completed', 'benefits_explained', 'cobra_forms', 'final_paycheck',
            'laptop_returned', 'phone_returned', 'id_card_returned', 'access_revoked', 'email_deactivated',
            'expense_reports', 'company_credit_card', 'outstanding_advances',
            'knowledge_transfer', 'project_handover', 'keys_returned',
            'locker_cleared', 'uniform_returned'
        ]

        total_fields = len(fields)
        completed_fields = sum(1 for field in fields if getattr(self, field) in ['completed', 'not_applicable'])

        return (completed_fields / total_fields) * 100 if total_fields > 0 else 0

# Import Timecard models
from .timecard_models import Timecard, TimecardEntry

# Import Payroll models
from .payroll_models import (
    PayrollPolicy, PayrollPeriod, PayrollComponent, TaxSlab,
    EmployeeSalary, EmployeeSalaryComponent, PayrollRun, PayrollEntry,
    PaySlip, SalaryAdvance, SalaryAdvanceRecovery, YearEndStatement
)

# ============ OVERTIME SYSTEM MODELS ============

class OvertimePolicy(models.Model):
    """
    Define overtime rules and policies for different employee groups
    """
    RATE_TYPE_CHOICES = [
        ('fixed', _('Fixed Rate')),
        ('multiplier', _('Hourly Rate Multiplier')),
        ('tiered', _('Tiered Rate')),
    ]

    APPROVAL_LEVEL_CHOICES = [
        ('manager', _('Manager Approval')),
        ('hr', _('HR Approval')),
        ('department_head', _('Department Head Approval')),
        ('executive', _('Executive Approval')),
    ]

    name = models.CharField(_('Policy Name'), max_length=100)
    description = models.TextField(_('Description'), blank=True)

    # Applicability
    departments = models.ManyToManyField(Department, blank=True, related_name='overtime_policies',
                                       verbose_name=_('Applicable Departments'))
    positions = models.ManyToManyField(Position, blank=True, related_name='overtime_policies',
                                     verbose_name=_('Applicable Positions'))
    employees = models.ManyToManyField(Employee, blank=True, related_name='overtime_policies',
                                     verbose_name=_('Specific Employees'))

    # Thresholds
    daily_threshold_hours = models.DecimalField(_('Daily Threshold (Hours)'), max_digits=4, decimal_places=2,
                                              default=8.00, help_text=_('Hours after which overtime applies'))
    weekly_threshold_hours = models.DecimalField(_('Weekly Threshold (Hours)'), max_digits=4, decimal_places=2,
                                               default=40.00, help_text=_('Weekly hours after which overtime applies'))

    # Rate Configuration
    rate_type = models.CharField(_('Rate Type'), max_length=20, choices=RATE_TYPE_CHOICES, default='multiplier')

    # For multiplier type
    standard_overtime_multiplier = models.DecimalField(_('Standard Overtime Multiplier'), max_digits=4, decimal_places=2,
                                                     default=1.50, help_text=_('e.g., 1.5 for 1.5x regular rate'))
    extended_overtime_multiplier = models.DecimalField(_('Extended Overtime Multiplier'), max_digits=4, decimal_places=2,
                                                     default=2.00, help_text=_('Rate after extended hours'))
    extended_hours_threshold = models.DecimalField(_('Extended Hours Threshold'), max_digits=4, decimal_places=2,
                                                 default=2.00, help_text=_('Hours before extended rate applies'))

    # Weekend and Holiday rates
    weekend_multiplier = models.DecimalField(_('Weekend Multiplier'), max_digits=4, decimal_places=2,
                                           default=1.50, help_text=_('Weekend overtime rate'))
    holiday_multiplier = models.DecimalField(_('Holiday Multiplier'), max_digits=4, decimal_places=2,
                                           default=2.00, help_text=_('Holiday overtime rate'))

    # For fixed rate type
    fixed_hourly_rate = models.DecimalField(_('Fixed Hourly Rate'), max_digits=8, decimal_places=2,
                                          null=True, blank=True, help_text=_('Fixed rate per hour'))

    # Approval requirements
    requires_pre_approval = models.BooleanField(_('Requires Pre-Approval'), default=True)
    approval_level = models.CharField(_('Approval Level'), max_length=20, choices=APPROVAL_LEVEL_CHOICES,
                                    default='manager')
    max_daily_overtime = models.DecimalField(_('Max Daily Overtime (Hours)'), max_digits=4, decimal_places=2,
                                           null=True, blank=True, help_text=_('Maximum overtime hours per day'))
    max_weekly_overtime = models.DecimalField(_('Max Weekly Overtime (Hours)'), max_digits=4, decimal_places=2,
                                            null=True, blank=True, help_text=_('Maximum overtime hours per week'))

    # Auto calculation
    auto_calculate = models.BooleanField(_('Auto Calculate from Timecard'), default=True)

    is_active = models.BooleanField(_('Active'), default=True)
    effective_date = models.DateField(_('Effective Date'), default=date.today)
    end_date = models.DateField(_('End Date'), null=True, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Overtime Policy')
        verbose_name_plural = _('Overtime Policies')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def is_applicable_to_employee(self, employee):
        """Check if this policy applies to a specific employee"""
        # Direct employee assignment
        if self.employees.filter(id=employee.id).exists():
            return True

        # Department check
        if employee.department and self.departments.filter(id=employee.department.id).exists():
            return True

        # Position check
        if employee.position and self.positions.filter(id=employee.position.id).exists():
            return True

        return False

    def calculate_overtime_rate(self, employee, hours, is_weekend=False, is_holiday=False):
        """Calculate overtime rate for given hours"""
        if not employee.salary:
            return 0

        # Calculate hourly rate from salary (assuming monthly salary)
        hourly_rate = employee.salary / Decimal('160')  # Approximate monthly working hours

        if self.rate_type == 'fixed':
            return self.fixed_hourly_rate or 0

        elif self.rate_type == 'multiplier':
            multiplier = self.standard_overtime_multiplier

            # Apply special rates
            if is_holiday:
                multiplier = self.holiday_multiplier
            elif is_weekend:
                multiplier = self.weekend_multiplier
            elif hours > self.extended_hours_threshold:
                multiplier = self.extended_overtime_multiplier

            return hourly_rate * multiplier

        return hourly_rate * self.standard_overtime_multiplier


class OvertimeClaim(models.Model):
    """
    Employee overtime claims/requests
    """
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('paid', _('Paid')),
        ('cancelled', _('Cancelled')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtime_claims',
                               verbose_name=_('Employee'))
    overtime_policy = models.ForeignKey(OvertimePolicy, on_delete=models.CASCADE, related_name='claims',
                                      verbose_name=_('Overtime Policy'))

    # Time period
    claim_date = models.DateField(_('Claim Date'))
    work_date = models.DateField(_('Work Date'))
    start_time = models.TimeField(_('Start Time'))
    end_time = models.TimeField(_('End Time'))

    # Hours breakdown
    regular_hours = models.DecimalField(_('Regular Hours'), max_digits=4, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(_('Overtime Hours'), max_digits=4, decimal_places=2, default=0)
    total_hours = models.DecimalField(_('Total Hours'), max_digits=4, decimal_places=2, default=0)

    # Project/Task reference
    project_name = models.CharField(_('Project/Task'), max_length=200, blank=True)
    timecard_entry = models.ForeignKey(TimecardEntry, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='overtime_claims')

    # Overtime details
    reason = models.TextField(_('Reason/Justification'))
    is_weekend = models.BooleanField(_('Weekend Work'), default=False)
    is_holiday = models.BooleanField(_('Holiday Work'), default=False)
    is_emergency = models.BooleanField(_('Emergency Work'), default=False)

    # Rate and calculation
    hourly_rate = models.DecimalField(_('Hourly Rate'), max_digits=8, decimal_places=2, default=0)
    overtime_rate = models.DecimalField(_('Overtime Rate'), max_digits=8, decimal_places=2, default=0)
    rate_multiplier = models.DecimalField(_('Rate Multiplier'), max_digits=4, decimal_places=2, default=1.50)
    total_amount = models.DecimalField(_('Total Amount'), max_digits=10, decimal_places=2, default=0)

    # Status and workflow
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')

    # Approval chain
    submitted_at = models.DateTimeField(_('Submitted At'), null=True, blank=True)
    approved_at = models.DateTimeField(_('Approved At'), null=True, blank=True)
    approved_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='approved_overtime_claims', verbose_name=_('Approved By'))
    rejection_reason = models.TextField(_('Rejection Reason'), blank=True)

    # Payroll integration
    payroll_period = models.CharField(_('Payroll Period'), max_length=20, blank=True,
                                    help_text=_('e.g., 2024-01 for January 2024'))
    paid_at = models.DateTimeField(_('Paid At'), null=True, blank=True)
    payroll_reference = models.CharField(_('Payroll Reference'), max_length=100, blank=True)

    # Additional info
    notes = models.TextField(_('Notes'), blank=True)
    attachments = models.FileField(_('Attachments'), upload_to='overtime_attachments/', null=True, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)

    class Meta:
        verbose_name = _('Overtime Claim')
        verbose_name_plural = _('Overtime Claims')
        ordering = ['-work_date', '-created_at']
        indexes = [
            models.Index(fields=['employee', 'work_date']),
            models.Index(fields=['status', 'work_date']),
            models.Index(fields=['payroll_period']),
        ]

    def __str__(self):
        return f"{self.employee.full_name} - {self.work_date} ({self.overtime_hours}h)"

    def save(self, *args, **kwargs):
        # Auto-calculate fields
        if self.start_time and self.end_time:
            # Calculate total hours
            start = datetime.combine(self.work_date, self.start_time)
            end = datetime.combine(self.work_date, self.end_time)
            if end < start:  # Next day
                end += timedelta(days=1)

            total_minutes = (end - start).total_seconds() / 60
            self.total_hours = Decimal(str(total_minutes / 60))

            # Calculate regular vs overtime hours based on policy
            threshold = self.overtime_policy.daily_threshold_hours if self.overtime_policy else Decimal('8')
            if self.total_hours > threshold:
                self.regular_hours = threshold
                self.overtime_hours = self.total_hours - threshold
            else:
                self.regular_hours = self.total_hours
                self.overtime_hours = Decimal('0')

        # Auto-detect weekend/holiday
        if self.work_date:
            self.is_weekend = self.work_date.weekday() >= 5  # Saturday=5, Sunday=6

        # Calculate rates and total amount
        if self.overtime_policy and self.employee:
            self.overtime_rate = self.overtime_policy.calculate_overtime_rate(
                self.employee, self.overtime_hours, self.is_weekend, self.is_holiday
            )
            self.total_amount = self.overtime_hours * self.overtime_rate

            # Get hourly rate
            if self.employee.salary:
                self.hourly_rate = self.employee.salary / Decimal('160')  # Monthly salary to hourly

        # Auto-set payroll period
        if self.work_date and not self.payroll_period:
            self.payroll_period = f"{self.work_date.year}-{self.work_date.month:02d}"

        # Update status timestamps
        if self.status == 'submitted' and not self.submitted_at:
            self.submitted_at = timezone.now()
        elif self.status == 'approved' and not self.approved_at:
            self.approved_at = timezone.now()
        elif self.status == 'paid' and not self.paid_at:
            self.paid_at = timezone.now()

        super().save(*args, **kwargs)

    @property
    def is_pending_approval(self):
        return self.status == 'submitted'

    @property
    def can_be_edited(self):
        return self.status in ['draft']

    @property
    def duration_hours(self):
        """Calculate work duration in hours"""
        if self.start_time and self.end_time:
            start = datetime.combine(self.work_date, self.start_time)
            end = datetime.combine(self.work_date, self.end_time)
            if end < start:  # Next day
                end += timedelta(days=1)
            return (end - start).total_seconds() / 3600
        return 0


class OvertimeApproval(models.Model):
    """
    Overtime approval workflow and history
    """
    ACTION_CHOICES = [
        ('submitted', _('Submitted')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('returned', _('Returned for Revision')),
        ('cancelled', _('Cancelled')),
    ]

    overtime_claim = models.ForeignKey(OvertimeClaim, on_delete=models.CASCADE, related_name='approvals',
                                     verbose_name=_('Overtime Claim'))

    # Approval details
    action = models.CharField(_('Action'), max_length=20, choices=ACTION_CHOICES)
    approver = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='overtime_approvals',
                               verbose_name=_('Approver'))
    approver_role = models.CharField(_('Approver Role'), max_length=50, blank=True)

    # Feedback
    comments = models.TextField(_('Comments'), blank=True)
    suggestions = models.TextField(_('Suggestions'), blank=True)

    # Approval conditions
    approved_hours = models.DecimalField(_('Approved Hours'), max_digits=4, decimal_places=2, null=True, blank=True)
    approved_amount = models.DecimalField(_('Approved Amount'), max_digits=10, decimal_places=2, null=True, blank=True)
    conditions = models.TextField(_('Conditions'), blank=True)

    # Workflow
    approval_level = models.IntegerField(_('Approval Level'), default=1)
    is_final_approval = models.BooleanField(_('Final Approval'), default=True)
    next_approver = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='pending_overtime_approvals')

    # System info
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    user_agent = models.CharField(_('User Agent'), max_length=500, blank=True)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Overtime Approval')
        verbose_name_plural = _('Overtime Approvals')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.overtime_claim} - {self.get_action_display()} by {self.approver.full_name}"

    def save(self, *args, **kwargs):
        # Auto-set approver role
        if not self.approver_role and self.approver:
            if self.approver.position:
                self.approver_role = self.approver.position.name

        super().save(*args, **kwargs)

        # Update claim status
        if self.action == 'approved':
            self.overtime_claim.status = 'approved'
            self.overtime_claim.approved_by = self.approver
            self.overtime_claim.approved_at = self.created_at
        elif self.action == 'rejected':
            self.overtime_claim.status = 'rejected'
            self.overtime_claim.rejection_reason = self.comments

        self.overtime_claim.save()


class OvertimeReport(models.Model):
    """
    Overtime reports and analytics
    """
    REPORT_TYPE_CHOICES = [
        ('monthly', _('Monthly Report')),
        ('weekly', _('Weekly Report')),
        ('employee', _('Employee Report')),
        ('department', _('Department Report')),
        ('project', _('Project Report')),
    ]

    report_type = models.CharField(_('Report Type'), max_length=20, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(_('Title'), max_length=200)

    # Filters
    start_date = models.DateField(_('Start Date'))
    end_date = models.DateField(_('End Date'))
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True, blank=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, null=True, blank=True)

    # Summary data (JSON field for flexibility)
    summary_data = models.JSONField(_('Summary Data'), default=dict)

    # Report metadata
    generated_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='generated_overtime_reports')
    total_claims = models.IntegerField(_('Total Claims'), default=0)
    total_hours = models.DecimalField(_('Total Hours'), max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('Total Amount'), max_digits=12, decimal_places=2, default=0)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)

    class Meta:
        verbose_name = _('Overtime Report')
        verbose_name_plural = _('Overtime Reports')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.start_date} to {self.end_date})"