from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.forms import inlineformset_factory
from django.utils import timezone
from datetime import timedelta
from .models import (
    Employee, Department, Position, EmployeeDocument, OvertimeClaim, OvertimePolicy,
    EmployeeOnboarding, OnboardingTaskInstance, OnboardingTemplate,
    PromotionTransfer, ExitInterview, ExitChecklist
)
import re
import os

class SafeFileInput(forms.FileInput):
    """FileInput widget that handles missing files gracefully."""
    
    def format_value(self, value):
        """Return the file value, but handle missing files gracefully."""
        if value is None:
            return None
        
        # Check if the file exists before trying to access it
        try:
            if hasattr(value, 'path') and not os.path.exists(value.path):
                # File is missing, return None to show as empty
                return None
        except (AttributeError, OSError, ValueError):
            # Any error accessing the file, treat as missing
            return None
        
        return super().format_value(value)
    
    def value_from_datadict(self, data, files, name):
        """Get value from form data, handling missing files gracefully."""
        try:
            return super().value_from_datadict(data, files, name)
        except (OSError, ValueError):
            return None

class SafeFileField(forms.FileField):
    """FileField that handles missing files gracefully with proper validation."""
    
    widget = SafeFileInput
    
    def __init__(self, *args, **kwargs):
        # Add default validation messages
        default_error_messages = {
            'invalid': 'Please select a valid image file.',
            'required': 'Please select an image file to upload.',
            'empty': 'The uploaded file is empty.',
            'missing': 'No file was submitted.',
            'invalid_image': 'Please upload a valid image file (JPEG, PNG, GIF, or WebP).',
            'invalid_format': 'Unsupported image format. Please use JPEG, PNG, GIF, or WebP.',
        }
        
        if 'error_messages' in kwargs:
            default_error_messages.update(kwargs['error_messages'])
        kwargs['error_messages'] = default_error_messages
        
        super().__init__(*args, **kwargs)
    
    def to_python(self, data):
        """Convert data to Python object, handling missing files."""
        try:
            file = super().to_python(data)
            if file is None:
                return None
            
            # Only validate newly uploaded files (not existing files)
            # If it's a new upload, it will have TemporaryUploadedFile or InMemoryUploadedFile type
            if hasattr(file, 'content_type') and hasattr(file, 'size'):
                # Check if this is a new upload vs existing file
                from django.core.files.uploadedfile import UploadedFile
                if isinstance(file, UploadedFile):
                    # This is a new upload, validate it
                    self.validate_image_file(file)
            
            return file
        except (OSError, ValueError):
            return None
    
    def validate_image_file(self, file):
        """Validate image file type only."""
        # Check content type
        valid_types = [
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/gif', 'image/webp'
        ]
        
        if file.content_type not in valid_types:
            raise ValidationError(self.error_messages['invalid_format'], code='invalid_format')
        
        # Additional validation: check if file is actually an image
        try:
            from PIL import Image
            import io
            
            # Reset file position
            file.seek(0)
            
            # Try to open as image
            try:
                with Image.open(io.BytesIO(file.read())) as img:
                    # Verify it's a valid image
                    img.verify()
            except Exception:
                raise ValidationError(self.error_messages['invalid_image'], code='invalid_image')
            finally:
                # Reset file position after reading
                file.seek(0)
                
        except ImportError:

                
            pass
            # PIL not available, skip advanced validation
            pass
    
    def bound_data(self, data, initial):
        """Return data bound to this field, handling missing initial files."""
        if initial:
            try:
                # Check if initial file exists
                if hasattr(initial, 'path') and not os.path.exists(initial.path):
                    initial = None
            except (AttributeError, OSError, ValueError):
                initial = None
        return super().bound_data(data, initial)

class EmployeeForm(forms.ModelForm):
    """Form for creating and updating employees."""

    # Override the photo field to use our safe field that handles missing files
    photo = SafeFileField(required=False, widget=SafeFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}))

    # User account fields
    username = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username for login',
            'minlength': '3',
            'maxlength': '150',
            'pattern': '^[a-zA-Z0-9_.-]+$',
            'data-validation-type': 'username'
        }),
        help_text='3-150 characters. Letters, numbers, and @/./+/-/_ only.'
    )
    new_password = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password (min 8 characters)',
            'minlength': '8',
            'maxlength': '128',
            'data-validation-type': 'password'
        }),
        help_text='Minimum 8 characters.'
    )
    confirm_password = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter password',
            'data-validation-type': 'confirm-password'
        }),
        help_text='Re-enter the same password for confirmation.'
    )
    is_active_user = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name', 'photo', 'gender',
            'date_of_birth', 'nationality', 'phone_number',
            'email', 'address', 'emergency_contact_name', 'emergency_contact_phone',
            'department', 'position', 'branch', 'employment_status', 'work_type', 'hire_date', 'end_date', 'notes'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if left blank (e.g., EMP2024001)'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'employment_status': forms.Select(attrs={'class': 'form-select'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'hire_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.instance_pk = kwargs.get('instance').pk if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)

        # Handle user account fields based on create vs edit mode
        if self.instance.pk:
            # Edit mode
            if self.instance.user:
                # Employee has a user - populate existing data
                self.fields['username'].initial = self.instance.user.username
                self.fields['is_active_user'].initial = self.instance.user.is_active
                self.fields['username'].widget.attrs['readonly'] = True  # Make username readonly when editing
                self.fields['new_password'].widget.attrs['placeholder'] = 'Leave blank to keep current password'
                self.fields['new_password'].help_text = 'Leave blank to keep current password.'
                # Hide confirm_password when user exists (password change is optional)
                self.fields['confirm_password'].widget = forms.HiddenInput()
            else:
                # Employee doesn't have a user - show creation fields (required)
                self.fields['username'].required = True
                self.fields['new_password'].required = True
                self.fields['confirm_password'].required = True
                self.fields['username'].widget.attrs['required'] = 'required'
                self.fields['new_password'].widget.attrs['required'] = 'required'
                self.fields['confirm_password'].widget.attrs['required'] = 'required'
                self.fields['new_password'].widget.attrs['placeholder'] = 'Enter password (min 8 characters)'
                self.fields['new_password'].help_text = 'Minimum 8 characters.'
        else:
            # Create mode - make user fields required
            self.fields['username'].required = True
            self.fields['new_password'].required = True
            self.fields['confirm_password'].required = True
            self.fields['username'].widget.attrs['required'] = 'required'
            self.fields['new_password'].widget.attrs['required'] = 'required'
            self.fields['confirm_password'].widget.attrs['required'] = 'required'

        # Set default values for new employees
        if not self.instance.pk:  # Only for new employees (not editing existing ones)
            self.fields['hire_date'].initial = timezone.now().date()
            self.fields['nationality'].initial = 'KH'  # Set default to Cambodian
            self.fields['photo'].required = True  # Make photo required for new employees
        
        # Calculate date limits for date_of_birth (18 to 90 years old)
        today = timezone.now().date()
        min_date = today - timedelta(days=365 * 90)  # 90 years ago
        max_date = today - timedelta(days=365 * 18)  # 18 years ago
        
        # Update date_of_birth field widget with min and max dates
        self.fields['date_of_birth'].widget.attrs.update({
            'min': min_date.strftime('%Y-%m-%d'),
            'max': max_date.strftime('%Y-%m-%d'),
            'class': 'form-control date-input-hidden',
            'type': 'date',
            'style': 'display: none;'
        })
        
        # Set form field attributes for better validation and UX
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter first name',
            'data-validation-required': 'true',
            'minlength': '2',
            'maxlength': '50'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control', 
            'placeholder': 'Enter last name',
            'data-validation-required': 'true',
            'minlength': '2',
            'maxlength': '50'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter email address (optional)',
            'data-validation-required': 'false',
            'data-validation-type': 'email',
            'maxlength': '254'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+85581123456',
            'data-validation-type': 'phone',
            'maxlength': '20'
        })
        self.fields['emergency_contact_phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+85581123456',
            'data-validation-type': 'phone',
            'maxlength': '20'
        })
        self.fields['employee_id'].widget.attrs.update({
            'placeholder': 'Auto-generated if left blank (e.g., EMP2024001)',
            'maxlength': '20'
        })
        
        # Add blank option for nationality dropdown
        self.fields['nationality'].empty_label = "Select Nationality"

        # Add empty label for branch dropdown
        self.fields['branch'].empty_label = "Select Branch (Optional)"

        # Set default employment status to 'active' for new employees
        if not self.instance_pk:  # New employee (not editing existing)
            self.fields['employment_status'].initial = 'active'
            self.fields['work_type'].initial = 'office'  # Default to Office

        # Add empty label for employment status dropdown
        self.fields['employment_status'].empty_label = "Select Employment Status"
        
        # Date field attributes for enhanced validation
        self.fields['date_of_birth'].widget.attrs.update({
            'data-validation-required': 'true',
            'data-validation-type': 'date',
            'data-field-type': 'dob'
        })
        self.fields['hire_date'].widget.attrs.update({
            'data-validation-required': 'true',
            'data-validation-type': 'date',
            'data-field-type': 'hire_date'
        })
        if 'end_date' in self.fields:
            self.fields['end_date'].widget.attrs.update({
                'data-validation-type': 'date',
                'data-field-type': 'end_date',
                'data-validation-required': 'false',  # Explicitly mark as not required
                'placeholder': 'Select end date (optional)'  # Make it clear it's optional
            })
        
        
        # Make employee_id optional since it can be auto-generated
        self.fields['employee_id'].required = False

        # Make end_date optional
        self.fields['end_date'].required = False

        # Make email optional
        self.fields['email'].required = False

        # Make branch optional
        self.fields['branch'].required = False
        


    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        # Only require photo for new employees
        if not self.instance.pk and not photo:
            raise ValidationError(_('Employee photo is required for new employees.'))
        return photo
    
    def clean_employee_id(self):
        employee_id = self.cleaned_data.get('employee_id')
        if employee_id:
            # Check if employee_id exists for other employees
            emp_qs = Employee.objects.filter(employee_id=employee_id)
            if self.instance and self.instance.pk:
                emp_qs = emp_qs.exclude(pk=self.instance.pk)
            if emp_qs.exists():
                raise ValidationError(_('Employee ID already exists.'))
        # If empty, it will be auto-generated in the model save method
        return employee_id

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email exists for other employees
            emp_qs = Employee.objects.filter(email=email)
            if self.instance and self.instance.pk:
                emp_qs = emp_qs.exclude(pk=self.instance.pk)
            if emp_qs.exists():
                raise ValidationError(_('Email already exists.'))
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Check if phone number exists for other employees
            emp_qs = Employee.objects.filter(phone_number=phone_number)
            if self.instance and self.instance.pk:
                emp_qs = emp_qs.exclude(pk=self.instance.pk)
            if emp_qs.exists():
                raise ValidationError(_('Phone number already exists for another employee.'))
        return phone_number

    def clean_date_of_birth(self):
        date_of_birth = self.cleaned_data.get('date_of_birth')
        if date_of_birth:
            from datetime import date, timedelta
            # Calculate age
            today = date.today()
            age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
            
            # Check if employee is at least 18 years old
            if age < 18:
                raise ValidationError(_('Employee must be at least 18 years old. Current age: {} years.').format(age))
            
            # Check if date is not in the future
            if date_of_birth > today:
                raise ValidationError(_('Date of birth cannot be in the future.'))
            
            # Check for maximum age limit (90 years)
            if age > 90:
                raise ValidationError(_('Employee age must be between 18 and 90 years. Current age: {} years.').format(age))
        
        return date_of_birth

    def clean_hire_date(self):
        hire_date = self.cleaned_data.get('hire_date')
        if hire_date:
            from datetime import date
            today = date.today()
            
            # Check if hire date is not in the future (allow up to 1 year ahead for planning)
            if hire_date > today:
                from datetime import timedelta
                max_future_date = today + timedelta(days=365)
                if hire_date > max_future_date:
                    raise ValidationError(_('Hire date cannot be more than 1 year in the future.'))
            
            # Check if hire date is reasonable (not too far in the past)
            if hire_date.year < 1990:
                raise ValidationError(_('Please enter a reasonable hire date.'))
        
        return hire_date

    def clean_end_date(self):
        end_date = self.cleaned_data.get('end_date')
        # End date is completely optional, no validation needed if empty
        if end_date:
            from datetime import date
            today = date.today()

            # Check if end date is not too far in the future (allow up to 1 year ahead)
            if end_date > today:
                from datetime import timedelta
                max_future_date = today + timedelta(days=365)
                if end_date > max_future_date:
                    raise ValidationError(_('End date cannot be more than 1 year in the future.'))

        return end_date

    def clean_username(self):
        """Validate username for uniqueness and format"""
        from django.contrib.auth.models import User
        import re

        username = self.cleaned_data.get('username')

        if not username:
            return username

        # Validate format (alphanumeric, dots, hyphens, underscores)
        if not re.match(r'^[a-zA-Z0-9_.-]+$', username):
            raise ValidationError(_('Username can only contain letters, numbers, dots, hyphens, and underscores.'))

        # Check minimum length
        if len(username) < 3:
            raise ValidationError(_('Username must be at least 3 characters long.'))

        # Check uniqueness only for new employees or if username is being changed
        if not self.instance.pk or (self.instance.user and self.instance.user.username != username):
            if User.objects.filter(username=username).exists():
                raise ValidationError(_('This username is already taken. Please choose a different username.'))

        return username

    def clean_new_password(self):
        """Validate password strength"""
        password = self.cleaned_data.get('new_password')

        if not password:
            return password

        # Check minimum length
        if len(password) < 8:
            raise ValidationError(_('Password must be at least 8 characters long.'))

        # Optional: Add more password strength validation
        # if not any(char.isdigit() for char in password):
        #     raise ValidationError(_('Password must contain at least one number.'))

        return password

    def clean(self):
        cleaned_data = super().clean()

        # Password confirmation validation (for new employees or existing employees without user accounts)
        if not self.instance.pk or (self.instance.pk and not self.instance.user):
            password = cleaned_data.get('new_password')
            confirm_password = cleaned_data.get('confirm_password')

            if password and confirm_password:
                if password != confirm_password:
                    raise ValidationError({
                        'confirm_password': _('Passwords do not match. Please ensure both passwords are identical.')
                    })

        # Date validation
        hire_date = cleaned_data.get('hire_date')
        end_date = cleaned_data.get('end_date')
        date_of_birth = cleaned_data.get('date_of_birth')

        if hire_date and date_of_birth:
            from datetime import date
            # Calculate age at hire date
            age_at_hire = hire_date.year - date_of_birth.year - ((hire_date.month, hire_date.day) < (date_of_birth.month, date_of_birth.day))
            if age_at_hire < 16:
                raise ValidationError({
                    'hire_date': _('Employee must be at least 16 years old at hire date (Cambodia legal working age). Age at hire would be {} years.').format(age_at_hire)
                })

        if hire_date and end_date and end_date <= hire_date:
            raise ValidationError(_('End date must be after hire date.'))

        return cleaned_data

    def save(self, commit=True):
        """Save the employee instance and handle user account creation/updates"""
        from django.contrib.auth.models import User
        from django.contrib.auth.hashers import make_password

        employee = super().save(commit=False)
        is_new_employee = not employee.pk

        # Ensure employment_status is set to 'active' for new employees
        if is_new_employee and not employee.employment_status:
            employee.employment_status = 'active'

        if commit:
            employee.save()

            # Create user account for new employees OR existing employees without accounts
            if is_new_employee or (not is_new_employee and not employee.user):
                username = self.cleaned_data.get('username')
                password = self.cleaned_data.get('new_password')
                is_active_user = self.cleaned_data.get('is_active_user', True)

                if username and password:
                    # Create new user
                    user = User.objects.create(
                        username=username,
                        email=str(employee.email) if employee.email else '',
                        first_name=employee.first_name,
                        last_name=employee.last_name,
                        is_active=is_active_user,
                        password=make_password(password)
                    )

                    # Link user to employee
                    employee.user = user
                    employee.save()

            # Handle user account updates for existing employees with accounts
            elif employee.user:
                user = employee.user
                new_password = self.cleaned_data.get('new_password')
                is_active_user = self.cleaned_data.get('is_active_user')

                # Update password if provided
                if new_password:
                    user.password = make_password(new_password)

                # Update active status
                if is_active_user is not None:
                    user.is_active = is_active_user

                # Sync first and last name from employee
                user.first_name = employee.first_name
                user.last_name = employee.last_name
                if employee.email:
                    user.email = str(employee.email)

                user.save()

        return employee

class EmployeeSearchForm(forms.Form):
    """Form for searching and filtering employees."""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full border border-neutral-300 rounded-lg py-1 px-2 rounded-lg text-xs placeholder:text-xs',
            'placeholder': 'Search by name, employee ID, or email...'
        })
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        empty_label='All Departments',
        widget=forms.Select(attrs={'class': 'w-full border border-neutral-300 rounded-lg py-1 px-2 rounded-lg text-xs'})
    )
    employment_status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Employee.EMPLOYMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'w-full border border-neutral-300 rounded-lg py-1 px-2 rounded-lg text-xs'})
    )
    gender = forms.ChoiceField(
        choices=[('', 'All Genders')] + Employee.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'w-full border border-neutral-300 rounded-lg py-1 px-2 rounded-lg text-xs'})
    )

class EmployeeDocumentForm(forms.ModelForm):
    """Form for employee documents."""
    
    class Meta:
        model = EmployeeDocument
        fields = [
            'document_type', 'document_number', 'issue_date', 
            'expiry_date', 'issuing_authority', 'document_file', 'notes'
        ]
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'issuing_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')
        
        if issue_date and expiry_date and expiry_date <= issue_date:
            raise ValidationError({
                'expiry_date': _('Expiry date must be after issue date.')
            })
            
        return cleaned_data


class EmployeeDocumentFormSet(forms.BaseInlineFormSet):
    """Custom formset for Employee documents with dynamic extra forms."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Always start with no extra forms - users can add documents via button if needed
        self.extra = 0
    
    def is_valid(self):
        """Override is_valid to allow empty formsets."""
        # Check if any forms have actual data
        has_data = False
        for form in self.forms:
            if form.has_changed():
                has_data = True
                break
        
        # If no forms have data, consider formset valid (no documents to validate)
        if not has_data:
            return True
        
        # Otherwise, use normal validation
        return super().is_valid()
    
    def save(self, commit=True):
        """Override save to handle empty formsets."""
        # Check if any forms have data
        has_data = False
        for form in self.forms:
            if form.has_changed():
                has_data = True
                break
        
        # If no forms have data, return empty list (no documents to save)
        if not has_data:
            return []
        
        # Otherwise, use normal save
        return super().save(commit=commit)


def get_employee_document_formset(extra=None):
    """Factory function to create Employee document formset with configurable extra forms."""
    
    return inlineformset_factory(
        Employee, EmployeeDocument,
        form=EmployeeDocumentForm,
        formset=EmployeeDocumentFormSet,
        extra=0,  # Always start with 0 extra forms
        can_delete=True,
        can_delete_extra=True,
        validate_min=False,  # Don't require any documents
        min_num=0,  # Minimum 0 documents required
        validate_max=False   # No max limit on documents
    )



# Department Form
class DepartmentForm(forms.ModelForm):
    """Form for creating and updating departments."""
    
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude self from parent choices to prevent circular references
        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = Department.objects.exclude(pk=self.instance.pk)

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Check if code exists for other departments
            dept_qs = Department.objects.filter(code=code)
            if self.instance and self.instance.pk:
                dept_qs = dept_qs.exclude(pk=self.instance.pk)
            if dept_qs.exists():
                raise ValidationError(_('Department code already exists.'))
        return code

# Position Form
class PositionForm(forms.ModelForm):
    """Form for creating and updating positions."""
    
    class Meta:
        model = Position
        fields = ['name', 'code', 'department', 'description', 'level']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'level': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if code:
            # Check if code exists for other positions
            pos_qs = Position.objects.filter(code=code)
            if self.instance and self.instance.pk:
                pos_qs = pos_qs.exclude(pk=self.instance.pk)
            if pos_qs.exists():
                raise ValidationError(_('Position code already exists.'))
        return code


class OvertimeClaimForm(forms.ModelForm):
    """Form for employee overtime claim submission"""

    class Meta:
        model = OvertimeClaim
        fields = [
            'work_date', 'start_time', 'end_time',
            'project_name', 'reason',
            'is_weekend', 'is_holiday', 'is_emergency'
        ]
        widgets = {
            'work_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project or task name'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Reason for overtime...'}),
            'is_weekend': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_holiday': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_emergency': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'work_date': _('Work Date'),
            'start_time': _('Start Time'),
            'end_time': _('End Time'),
            'project_name': _('Project/Task'),
            'reason': _('Reason for Overtime'),
            'is_weekend': _('Weekend Work'),
            'is_holiday': _('Holiday Work'),
            'is_emergency': _('Emergency Work'),
        }


# ============================================================================
# EMPLOYEE LIFECYCLE FORMS
# ============================================================================

class OnboardingCreateForm(forms.Form):
    """Form for creating onboarding for a new employee"""
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(employment_status='active'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Employee')
    )
    template = forms.ModelChoiceField(
        queryset=OnboardingTemplate.objects.filter(is_active=True),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Onboarding Template'),
        required=False,
        empty_label='Select template (optional)'
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label=_('Start Date'),
        initial=timezone.now().date
    )
    hr_representative = forms.ModelChoiceField(
        queryset=Employee.objects.filter(employment_status='active'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('HR Representative'),
        required=False
    )
    buddy = forms.ModelChoiceField(
        queryset=Employee.objects.filter(employment_status='active'),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Onboarding Buddy'),
        required=False
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label=_('Notes'),
        required=False
    )


class OnboardingTaskCompleteForm(forms.ModelForm):
    """Form for completing an onboarding task"""
    class Meta:
        model = OnboardingTaskInstance
        fields = ['completion_notes', 'actual_hours', 'attachments']
        widgets = {
            'completion_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add completion notes...'}),
            'actual_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5', 'min': '0'}),
            'attachments': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PromotionTransferForm(forms.ModelForm):
    """Form for creating promotion/transfer requests"""
    class Meta:
        model = PromotionTransfer
        fields = [
            'employee', 'change_type', 'new_position', 'new_department',
            'effective_date', 'announcement_date', 'reason',
            'salary_change', 'salary_change_percentage', 'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'change_type': forms.Select(attrs={'class': 'form-select'}),
            'new_position': forms.Select(attrs={'class': 'form-select'}),
            'new_department': forms.Select(attrs={'class': 'form-select'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'announcement_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'salary_change': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salary_change_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].queryset = Employee.objects.filter(employment_status='active')

        # Make salary fields optional
        self.fields['salary_change'].required = False
        self.fields['salary_change_percentage'].required = False

        # If editing existing instance, set current values
        if self.instance and self.instance.pk:
            self.fields['new_position'].initial = self.instance.new_position
            self.fields['new_department'].initial = self.instance.new_department

    def clean(self):
        cleaned_data = super().clean()
        effective_date = cleaned_data.get('effective_date')
        announcement_date = cleaned_data.get('announcement_date')

        if effective_date and announcement_date:
            if effective_date < announcement_date:
                raise ValidationError(_('Effective date must be on or after announcement date.'))

        return cleaned_data


class PromotionTransferApprovalForm(forms.Form):
    """Form for approving/rejecting promotion/transfer"""
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label=_('Action')
    )
    rejection_reason = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Required if rejecting...'}),
        label=_('Rejection Reason'),
        required=False
    )

    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        rejection_reason = cleaned_data.get('rejection_reason')

        if action == 'reject' and not rejection_reason:
            raise ValidationError({'rejection_reason': _('Rejection reason is required when rejecting.')})

        return cleaned_data


class ExitInterviewForm(forms.ModelForm):
    """Form for conducting exit interviews"""
    class Meta:
        model = ExitInterview
        fields = [
            'employee', 'exit_reason', 'last_working_day', 'interview_date',
            'interviewer', 'job_satisfaction', 'work_environment',
            'management_quality', 'career_development',
            'work_life_balance', 'compensation_benefits',
            'liked_most', 'liked_least', 'improvements',
            'recommend_company', 'additional_comments',
            'confidential_feedback', 'follow_up_required', 'follow_up_notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            'exit_reason': forms.Select(attrs={'class': 'form-select'}),
            'last_working_day': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'interview_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'interviewer': forms.Select(attrs={'class': 'form-select'}),
            'job_satisfaction': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'work_environment': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'management_quality': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'career_development': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'work_life_balance': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'compensation_benefits': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'liked_most': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'liked_least': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'improvements': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'recommend_company': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'additional_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'confidential_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'follow_up_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'follow_up_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default interview date to today
        if not self.instance.pk:
            self.fields['interview_date'].initial = timezone.now().date()

        # Make rating fields optional
        for field in ['job_satisfaction', 'work_environment', 'management_quality',
                      'career_development', 'work_life_balance', 'compensation_benefits']:
            self.fields[field].required = False


class ExitChecklistForm(forms.ModelForm):
    """Form for managing exit checklist"""
    class Meta:
        model = ExitChecklist
        fields = [
            'employee',
            # HR Tasks
            'final_interview_completed', 'benefits_explained', 'cobra_forms',
            'final_paycheck',
            # IT Tasks
            'laptop_returned', 'phone_returned', 'id_card_returned',
            'access_revoked', 'email_deactivated',
            # Finance Tasks
            'expense_reports', 'company_credit_card',
            'outstanding_advances',
            # Manager Tasks
            'knowledge_transfer', 'project_handover',
            'keys_returned',
            # General
            'locker_cleared', 'uniform_returned',
            'notes'
        ]
        widgets = {
            'employee': forms.Select(attrs={'class': 'form-select'}),
            # HR Tasks
            'final_interview_completed': forms.Select(attrs={'class': 'form-select'}),
            'benefits_explained': forms.Select(attrs={'class': 'form-select'}),
            'cobra_forms': forms.Select(attrs={'class': 'form-select'}),
            'final_paycheck': forms.Select(attrs={'class': 'form-select'}),
            # IT Tasks
            'laptop_returned': forms.Select(attrs={'class': 'form-select'}),
            'phone_returned': forms.Select(attrs={'class': 'form-select'}),
            'id_card_returned': forms.Select(attrs={'class': 'form-select'}),
            'access_revoked': forms.Select(attrs={'class': 'form-select'}),
            'email_deactivated': forms.Select(attrs={'class': 'form-select'}),
            # Finance Tasks
            'expense_reports': forms.Select(attrs={'class': 'form-select'}),
            'company_credit_card': forms.Select(attrs={'class': 'form-select'}),
            'outstanding_advances': forms.Select(attrs={'class': 'form-select'}),
            # Manager Tasks
            'knowledge_transfer': forms.Select(attrs={'class': 'form-select'}),
            'project_handover': forms.Select(attrs={'class': 'form-select'}),
            'keys_returned': forms.Select(attrs={'class': 'form-select'}),
            # General
            'locker_cleared': forms.Select(attrs={'class': 'form-select'}),
            'uniform_returned': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
