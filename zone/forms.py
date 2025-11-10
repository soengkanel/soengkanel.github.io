from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from .models import Worker, Department, Position, Building, Floor, Zone, Document, WorkerProbationPeriod, WorkerProbationExtension, ProbationExtensionRequest
from django.contrib.auth.models import User
from django.forms import inlineformset_factory
import re
from django.forms.formsets import TOTAL_FORM_COUNT
from django.utils.translation import ngettext
import pandas as pd
import os


class SafePhoneNumberField(forms.CharField):
    """Custom CharField that safely handles encrypted phone number bytes"""
    
    def prepare_value(self, value):
        """Override to safely handle bytes values"""
        if isinstance(value, bytes):
            try:
                # First try UTF-8 decoding
                return value.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    # If UTF-8 fails, try latin-1 (which accepts any byte sequence)
                    return value.decode('latin-1')
                except:
                    # If all else fails, return empty string for form display
                    return ''
        return super().prepare_value(value)


class WorkerForm(forms.ModelForm):
    """Form for creating and updating workers."""
    
    # Add date_joined as a custom read-only field
    date_joined = forms.DateField(
        label='Date Joined',
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'readonly': True}),
        help_text='Date when the worker was added to the system'
    )
    
    class Meta:
        model = Worker
        fields = [
            'worker_id', 'first_name', 'last_name', 'nickname', 'sex', 'dob', 'nationality', 
            'photo', 'position', 'phone_number', 'zone', 'building', 'floor', 'status', 'is_vip'
        ]
        widgets = {
            'worker_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if left empty'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'sex': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': forms.Select(attrs={'class': 'form-select'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter nickname or preferred name'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+85581123456'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'building': forms.Select(attrs={'class': 'form-select'}),
            'floor': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_vip': forms.CheckboxInput(attrs={'class': 'peer'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make key personal information fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['sex'].required = True
        self.fields['dob'].required = True
        self.fields['nationality'].required = True
        self.fields['phone_number'].required = False
        self.fields['phone_number'].label = 'Phone Number'

        # Populate date_joined field for existing workers
        if self.instance and self.instance.pk:
            self.fields['date_joined'].initial = self.instance.date_joined
        
        # Make date_joined disabled (read-only)
        self.fields['date_joined'].disabled = True
        


        # Always set photo as not required in HTML to avoid browser validation conflicts
        # We handle photo requirement validation in JavaScript and server-side clean method
        self.fields['photo'].required = False
        
        # Only clean up existing worker photo settings if needed
        if self.instance and self.instance.pk and self.instance.photo:
            # Remove all validators for existing workers with photos to prevent .enc validation issues
            self.fields['photo'].validators = []
            # Also remove any widget validation
            if hasattr(self.fields['photo'].widget, 'attrs'):
                self.fields['photo'].widget.attrs.pop('accept', None)
        
        # Set default status for new workers (not shown in create form, but ensures it's set)
        if not (self.instance and self.instance.pk):
            self.fields['status'].initial = 'active'
        
        # Set nationality choices
        self.fields['nationality'].choices = [('', 'Select Nationality')] + Worker.NATIONALITY_CHOICES
        
        # Filter floors based on building
        if 'building' in self.data:
            try:
                building_id = int(self.data.get('building'))
                self.fields['floor'].queryset = Floor.objects.filter(building_id=building_id)
            except (ValueError, TypeError):
                self.fields['floor'].queryset = Floor.objects.none()
        elif self.instance.pk and self.instance.building:
            self.fields['floor'].queryset = Floor.objects.filter(building=self.instance.building)
        else:
            self.fields['floor'].queryset = Floor.objects.none()


    def clean_worker_id(self):
        worker_id = self.cleaned_data.get('worker_id')
        if worker_id:
            worker_qs = Worker.objects.filter(worker_id=worker_id)
            if self.instance and self.instance.pk:
                worker_qs = worker_qs.exclude(pk=self.instance.pk)
            if worker_qs.exists():
                raise ValidationError(_('Worker ID already exists.'))
        return worker_id

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Phone number is now optional - no validation required
        # Just return the phone number as-is if provided
        if phone_number:
            import re
            # Just clean up basic formatting but don't validate
            clean_phone = re.sub(r'[\s\-\(\)]', '', phone_number)
            return clean_phone
        return phone_number


    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob:
            from datetime import date
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            if age < 16:
                raise ValidationError(_('Worker must be at least 16 years old.'))
            if age > 80:
                raise ValidationError(_('Please verify the date of birth. Age cannot exceed 80 years.'))
            if dob > today:
                raise ValidationError(_('Date of birth cannot be in the future.'))
        return dob



    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        
        # For existing workers with photos, skip all validation if no new photo is being uploaded
        if self.instance and self.instance.pk and self.instance.photo:
            # If photo field is empty/None, it means user didn't upload a new photo
            if not photo:
                return photo  # Keep existing photo, no validation needed
            
            # Check if this is the same existing photo (not a new upload)
            if hasattr(photo, 'name') and photo.name == self.instance.photo.name:
                return photo  # Same photo, no validation needed
                
            # If photo has strange attributes or looks like an existing file, skip validation
            if hasattr(photo, 'name') and (photo.name.endswith('.enc') or not hasattr(photo, 'content_type')):
                return photo
                
            # If photo is a FieldFile (existing file), not an UploadedFile (new upload), skip validation
            from django.db.models.fields.files import FieldFile
            if isinstance(photo, FieldFile):
                return photo
        
        # Check if photo is required (for new workers or workers without existing photos)
        if not photo:
            # If this is a new worker (no pk) or existing worker without photo, photo is required
            if not (self.instance and self.instance.pk and self.instance.photo):
                raise ValidationError(_('Photo is required. Please upload or capture a photo before submitting.'))
            return photo
        
        # Only validate if a new photo is being uploaded
        if photo and hasattr(photo, 'size') and hasattr(photo, 'name'):
            # Validate file type for new uploads
            import os
            ext = os.path.splitext(photo.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.enc']
            if ext not in valid_extensions:
                raise ValidationError(_('Invalid photo format. Please upload JPG, PNG, GIF, or BMP files only.'))
        
        return photo
    

    def clean(self):
        cleaned_data = super().clean()
        zone = cleaned_data.get('zone')
        building = cleaned_data.get('building')
        floor = cleaned_data.get('floor')
        
        # Chain select validation: Zone > Building > Floor
        if building and zone:
            if building.zone != zone:
                raise ValidationError({
                    'building': _('Selected building does not belong to the selected zone.')
                })
        
        if floor and building:
            if floor.building != building:
                raise ValidationError({
                    'floor': _('Selected floor does not belong to the selected building.')
                })
        
        if floor and zone:
            if floor.building.zone != zone:
                raise ValidationError({
                    'floor': _('Selected floor does not belong to the selected zone.')
                })
        
        return cleaned_data

    def save(self, commit=True):
        """
        Ultra-simplified save method - prioritize working saves over encryption optimization.
        Let Django handle everything normally, encryption will happen automatically.
        """
        # Remove date_joined from cleaned_data since it's a custom display field
        if 'date_joined' in self.cleaned_data:
            del self.cleaned_data['date_joined']
        
        # Just use Django's standard save behavior
        worker = super().save(commit=commit)
        return worker


class WorkerSearchForm(forms.Form):
    """Form for searching and filtering workers."""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, nickname, or worker ID...'
        })
    )
    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        required=False,
        empty_label="All Positions",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    zone = forms.ModelChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        empty_label="All Zones",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    building = forms.ModelChoiceField(
        queryset=Building.objects.all(),
        required=False,
        empty_label="All Buildings",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Worker.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sex = forms.ChoiceField(
        choices=[('', 'All')] + Worker.SEX_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    nationality = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by nationality...'
        })
    )
    worker_type = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('worker', 'Workers'),
            ('vip', 'VIPs')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_joined_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'style': 'font-size: 11px; padding: 4px 8px;',
            'title': 'From date'
        }),
        label='From'
    )
    date_joined_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'style': 'font-size: 11px; padding: 4px 8px;',
            'title': 'To date'
        }),
        label='To'
    )

    def __init__(self, *args, **kwargs):
        # Extract request to check URL parameters
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Disable worker_type field if it's already specified in URL
        if request and request.GET.get('worker_type'):
            self.fields['worker_type'].widget.attrs['disabled'] = 'disabled'
            self.fields['worker_type'].widget.attrs['title'] = 'Worker type is fixed for this view'


class DepartmentForm(forms.ModelForm):
    """Form for creating and updating departments."""
    
    class Meta:
        model = Department
        fields = ['name', 'code', 'description', 'parent', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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


class PositionForm(forms.ModelForm):
    """Form for creating and updating positions."""
    
    class Meta:
        model = Position
        fields = ['name', 'code', 'department', 'level', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'level': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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


class BuildingForm(forms.ModelForm):
    """Form for creating and updating buildings."""
    
    class Meta:
        model = Building
        fields = ['name', 'code', 'zone', 'address', 'total_floors', 'no_floor', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unique building code'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'total_floors': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'no_floor': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_code(self):
        code = self.cleaned_data.get('code')
        if not code:
            raise ValidationError(_('Building code is required.'))
        
        # Check for uniqueness, excluding current instance if editing
        building_qs = Building.objects.filter(code=code)
        if self.instance and self.instance.pk:
            building_qs = building_qs.exclude(pk=self.instance.pk)
        if building_qs.exists():
            raise ValidationError(_('Building code already exists.'))
        
        return code

    def clean(self):
        cleaned_data = super().clean()
        no_floor = cleaned_data.get('no_floor')
        total_floors = cleaned_data.get('total_floors')
        
        # Validate floor logic
        if no_floor:
            # When no_floor is True (building has no floors), set total_floors to 0
            cleaned_data['total_floors'] = 0
        elif not no_floor and (total_floors is None or total_floors <= 0):
            # When no_floor is False (building has floors), require floors > 0
            raise ValidationError({
                'total_floors': _('Total floors must be greater than 0 when building has specific floors.')
            })
        
        return cleaned_data


class FloorForm(forms.ModelForm):
    """Form for creating and updating floors."""
    
    class Meta:
        model = Floor
        fields = ['building', 'floor_number', 'name', 'description', 'is_active']
        widgets = {
            'building': forms.Select(attrs={'class': 'form-select'}),
            'floor_number': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DocumentForm(forms.ModelForm):
    """Form for worker documents."""
    
    class Meta:
        model = Document
        fields = [
            'document_type', 'document_number', 'issue_date', 
            'expiry_date', 'issuing_authority', 'document_file', 'notes'
        ]
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select', 'required':True}),
            'document_number': forms.TextInput(attrs={'class': 'form-control', 'required':True}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required':True}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required':True}),
            'issuing_authority': forms.TextInput(attrs={'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        # Store request data BEFORE calling super()
        self._request_data = args[0] if args else None
        self._request_files = args[1] if len(args) > 1 else None
        
        super().__init__(*args, **kwargs)
        
        # Make key fields required ONLY for non-empty forms
        self.fields['document_type'].required = True
        self.fields['document_number'].required = True
        self.fields['issue_date'].required = True
        self.fields['expiry_date'].required = True
        self.fields['issuing_authority'].required = False
        
        # NEVER require document_file at form level - we handle this in clean method
        self.fields['document_file'].required = False
        
        # Remove any default validators that might interfere
        self.fields['document_file'].validators = []
        
        # Remove HTML required attribute to prevent browser validation
        if hasattr(self.fields['document_file'].widget, 'attrs'):
            self.fields['document_file'].widget.attrs.pop('required', None)
            
        # Make sure id field is not required for empty forms
        if 'id' in self.fields:
            self.fields['id'].required = False
    
    def is_empty_form(self):
        """Check if this is an empty document form that should be ignored."""
        if not self.data:
            return True
            
        # Check if any meaningful field has data
        meaningful_fields = ['document_type', 'document_number', 'issue_date', 'expiry_date']
        
        for field_name in meaningful_fields:
            field_key = f"{self.prefix}-{field_name}" if self.prefix else field_name
            field_value = self.data.get(field_key, '').strip()
            if field_value:
                return False
        
        # Check if there's a file uploaded
        if self.files:
            file_key = f"{self.prefix}-document_file" if self.prefix else 'document_file'
            if file_key in self.files:
                return False
        
        return True
    
    def full_clean(self):
        """Override full_clean to skip validation for empty forms."""
        # If this is an empty form and not an existing document, skip validation
        if self.is_empty_form() and not (self.instance and self.instance.pk):
            self._errors = {}
            self.cleaned_data = {}
            return
        
        # Otherwise, proceed with normal validation
        super().full_clean()
    
    def save(self, commit=True):
        """ENHANCED save method - ALWAYS preserve existing files unless explicitly replaced."""
        document = super().save(commit=False)
        
        # For existing documents, ALWAYS preserve the original file unless new one uploaded
        if self.instance and self.instance.pk:
            try:
                original_document = Document.objects.get(pk=self.instance.pk)
                current_file = self.cleaned_data.get('document_file')
                
                # Only replace file if a new one was actually uploaded
                if not current_file or not hasattr(current_file, 'read'):
                    # No new file - preserve the original
                    if original_document.document_file:
                        document.document_file = original_document.document_file
                # else: new file uploaded, use it
                        
            except Document.DoesNotExist:
                pass  # New document, proceed normally
        
        if commit:
            document.save()
        return document
    
    def clean_document_file(self):
        """SIMPLE AND DIRECT: Only require files for truly new documents."""
        document_file = self.cleaned_data.get('document_file')
        
        # RULE 1: If this is an existing document (has PK), SKIP ALL FILE VALIDATION
        if self.instance and self.instance.pk:
            # Existing document - only validate new uploads, never require files
            if document_file and hasattr(document_file, 'size'):
                self._validate_file_properties(document_file)
            return document_file  # Always pass for existing documents
        
        # RULE 2: For truly new documents, check if ANY file evidence exists
        
        # Check if we have a current upload
        has_current_upload = document_file and hasattr(document_file, 'size')
        
        # Check if tracking field indicates file was uploaded
        has_upload_tracking = False
        if self._request_data and self.prefix:
            tracking_field = f"{self.prefix}-file_uploaded"
            has_upload_tracking = self._request_data.get(tracking_field) == 'true'
        
        # If we have ANY evidence of a file, pass validation
        if has_current_upload or has_upload_tracking:
            # Validate file properties if we have a current upload
            if has_current_upload:
                self._validate_file_properties(document_file)
            return document_file
        
        # ONLY require file if this is a truly new document with no evidence
        #raise ValidationError(_('Document file is required for new documents.'))
        return document_file
    
    def _validate_file_properties(self, file):
        """Validate file size and type."""
        # File size check (5MB max)
        if file.size > 5 * 1024 * 1024:
            raise ValidationError(_('Document file too large. Maximum size is 5MB.'))
        
        # File type check
        import os
        ext = os.path.splitext(file.name)[1].lower()
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.pdf', '.enc']
        if ext not in valid_extensions:
            raise ValidationError(_('Invalid document format. Please upload JPG, PNG, GIF, BMP, or PDF files only.'))
    
    def clean(self):
        """Validate document data, but skip validation for empty forms."""

        # Skip validation for empty forms
        if self.is_empty_form() and not (self.instance and self.instance.pk):
            return {}

        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')
        document_type = cleaned_data.get('document_type', 'Unknown')
        
        
        # Only validate dates if both are provided
        if issue_date and expiry_date:
            if expiry_date <= issue_date:
                raise ValidationError(_("Expiry date must be after issue date."))
            
        return cleaned_data


class BaseWorkerDocumentFormSet(forms.BaseInlineFormSet):
    """Custom formset for worker documents with dynamic extra forms."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                
        # Dynamic extra forms based on existing documents
        if self.instance and self.instance.pk:
            # For existing workers, count existing documents
            existing_docs_count = self.instance.documents.count()
            if existing_docs_count == 0:
                # No documents yet, show 1 empty form
                self.extra = 1
            else:
                # Has documents, show no extra empty forms by default
                # User can add more documents via "Add Document" button if needed
                self.extra = 0
        else:
            # For new workers, show 1 empty form
            self.extra = 1
    
    def full_clean(self):
        """Override full_clean to handle file validation properly and skip empty forms."""
        # Use Django's built-in empty form detection
        super().full_clean()
        
        # Filter out errors from forms that should be considered empty
        filtered_errors = []
        for i, (form, errors) in enumerate(zip(self.forms, self._errors)):
            if hasattr(form, 'is_empty_form') and form.is_empty_form() and not (form.instance and form.instance.pk):
                # This is an empty form that shouldn't be validated
                filtered_errors.append({})
            else:
                filtered_errors.append(errors)
        
        self._errors = filtered_errors

    def clean(self):
        """Custom formset clean method with automatic document replacement."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        
        # Track document types that should auto-replace: passport, visa, work_permit
        auto_replace_types = ['passport', 'visa', 'work_permit']
        type_to_forms = {}
        document_numbers = []
        
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                doc_number = form.cleaned_data.get('document_number')
                doc_type = form.cleaned_data.get('document_type')
                
                # Check for duplicate document numbers
                if doc_number:
                    if doc_number in document_numbers:
                        raise ValidationError(_('Document numbers must be unique.'))
                    document_numbers.append(doc_number)
                
                # Handle auto-replacement for specific document types
                if doc_type in auto_replace_types:
                    if doc_type in type_to_forms:
                        # Found another document of the same type
                        existing_form = type_to_forms[doc_type]
                        
                        # Determine which one to keep based on whether it has a new file
                        current_has_new_file = form.cleaned_data.get('document_file') is not None
                        existing_has_new_file = existing_form.cleaned_data.get('document_file') is not None
                        
                        # If current form has a new file and existing doesn't, or if current form is newer
                        if current_has_new_file and not existing_has_new_file:
                            # Mark existing form for deletion and keep current
                            if existing_form.instance.pk:
                                existing_form.cleaned_data['DELETE'] = True
                            type_to_forms[doc_type] = form
                        elif existing_has_new_file and not current_has_new_file:
                            # Mark current form for deletion and keep existing
                            if form.instance.pk:
                                form.cleaned_data['DELETE'] = True
                        elif current_has_new_file and existing_has_new_file:
                            # Both have new files, prefer the current one (user's latest choice)
                            if existing_form.instance.pk:
                                existing_form.cleaned_data['DELETE'] = True
                            type_to_forms[doc_type] = form
                        else:
                            # Neither has new files, keep existing if it has an instance
                            if form.instance.pk and not existing_form.instance.pk:
                                type_to_forms[doc_type] = form
                            elif existing_form.instance.pk and not form.instance.pk:
                                # Keep existing, mark current for deletion (though it may not have an instance)
                                pass
                    else:
                        type_to_forms[doc_type] = form
                        
                        # If this is a new document being added, check if there's an existing one in DB
                        if not form.instance.pk and self.instance and self.instance.pk:
                            existing_docs = self.instance.documents.filter(document_type=doc_type)
                            if existing_docs.exists():
                                # Mark existing documents of this type for deletion
                                for existing_doc in existing_docs:
                                    # Find the form that represents this existing document
                                    for other_form in self.forms:
                                        if (other_form.instance.pk == existing_doc.pk and 
                                            not other_form.cleaned_data.get('DELETE', False)):
                                            other_form.cleaned_data['DELETE'] = True
                                            break
    
    def save(self, commit=True):
        """Override save to handle document replacement with logging."""
        instances = super().save(commit=False)
        
        # Track replaced documents for user feedback
        replaced_docs = []
        
        if commit:
            for form in self.deleted_forms:
                if form.instance.pk:
                    doc_type = form.instance.get_document_type_display()
                    replaced_docs.append(doc_type)
                    form.instance.delete()
            
            for instance in instances:
                instance.save()
                
            # Store replacement info in the request for feedback (if available)
            if replaced_docs and hasattr(self, '_request'):
                from django.contrib import messages
                replaced_types = ', '.join(set(replaced_docs))
                messages.info(self._request, 
                    f'Previous documents were automatically replaced: {replaced_types}')
        
        return instances


def get_worker_document_formset(worker=None, extra=None):
    """
    Create a dynamic formset based on worker's existing documents.
    
    Args:
        worker: Worker instance (None for new workers)
        extra: Override extra forms count (None for automatic)
    
    Returns:
        Configured formset class
    """
    if extra is None:
        if worker and worker.pk:
            existing_docs_count = worker.documents.count()
            extra = 0 if existing_docs_count > 0 else 1
        else:
            extra = 1
    
    return inlineformset_factory(
        Worker, Document, form=DocumentForm, formset=BaseWorkerDocumentFormSet,
        extra=extra, can_delete=True
    )


# Create the formset using our custom class defined above
WorkerDocumentFormSet = inlineformset_factory(
    Worker, Document, form=DocumentForm, formset=BaseWorkerDocumentFormSet,
    extra=0, can_delete=True
)

# OCR form removed


class WorkerWithDocumentsForm(forms.ModelForm):
    """Enhanced worker form that includes document management."""
    
    class Meta:
        model = Worker
        fields = [
            'worker_id', 'first_name', 'last_name', 'nickname', 'sex', 'dob', 'nationality', 
            'photo', 'position', 'phone_number', 'zone', 'building', 'floor', 'status', 'is_vip'
        ]
        widgets = {
            'worker_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Auto-generated if left empty'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter last name'}),
            'sex': forms.Select(attrs={'class': 'form-select'}),
            'dob': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nationality': forms.Select(attrs={'class': 'form-select'}),
            'nickname': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter nickname or preferred name'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'position': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'zone': forms.Select(attrs={'class': 'form-select'}),
            'building': forms.Select(attrs={'class': 'form-select'}),
            'floor': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'is_vip': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make key personal information fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['sex'].required = True
        self.fields['dob'].required = True
        self.fields['nationality'].required = True
        self.fields['phone_number'].required = False
        self.fields['phone_number'].label = 'Phone Number'

        # Handle photo field for existing workers with encrypted photos
        if self.instance and self.instance.pk and self.instance.photo:
            # Remove accept attribute for existing workers to avoid validation issues with .enc files
            self.fields['photo'].widget.attrs.pop('accept', None)
        
        # Always set photo as not required in HTML to avoid browser validation conflicts
        # We handle photo requirement validation in JavaScript and server-side clean method
        self.fields['photo'].required = False
        
        # Only clean up existing worker photo settings if needed
        if self.instance and self.instance.pk and self.instance.photo:
            # Remove all validators for existing workers with photos to prevent .enc validation issues
            self.fields['photo'].validators = []
            # Also remove any widget validation
            if hasattr(self.fields['photo'].widget, 'attrs'):
                self.fields['photo'].widget.attrs.pop('accept', None)
        
        # Set nationality choices
        self.fields['nationality'].choices = [('', 'Select Nationality')] + Worker.NATIONALITY_CHOICES
        
        # Filter floors based on building
        if 'building' in self.data:
            try:
                building_id = int(self.data.get('building'))
                self.fields['floor'].queryset = Floor.objects.filter(building_id=building_id)
            except (ValueError, TypeError):
                self.fields['floor'].queryset = Floor.objects.none()
        elif self.instance.pk and self.instance.building:
            self.fields['floor'].queryset = Floor.objects.filter(building=self.instance.building)
        else:
            self.fields['floor'].queryset = Floor.objects.none()


    def clean_worker_id(self):
        worker_id = self.cleaned_data.get('worker_id')
        if worker_id:
            worker_qs = Worker.objects.filter(worker_id=worker_id)
            if self.instance and self.instance.pk:
                worker_qs = worker_qs.exclude(pk=self.instance.pk)
            if worker_qs.exists():
                raise ValidationError(_('Worker ID already exists.'))
        return worker_id

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        
        
        # For existing workers with photos, skip all validation if no new photo is being uploaded
        if self.instance and self.instance.pk and self.instance.photo:
            # If photo field is empty/None, it means user didn't upload a new photo
            if not photo:
                return photo  # Keep existing photo, no validation needed
            
            # Check if this is the same existing photo (not a new upload)
            if hasattr(photo, 'name') and photo.name == self.instance.photo.name:
                return photo  # Same photo, no validation needed
                
            # If photo has strange attributes or looks like an existing file, skip validation
            if hasattr(photo, 'name') and (photo.name.endswith('.enc') or not hasattr(photo, 'content_type')):
                return photo
                
            # If photo is a FieldFile (existing file), not an UploadedFile (new upload), skip validation
            from django.db.models.fields.files import FieldFile
            if isinstance(photo, FieldFile):
                return photo
        
        # Check if photo is required (for new workers or workers without existing photos)
        if not photo:
            # If this is a new worker (no pk) or existing worker without photo, photo is required
            if not (self.instance and self.instance.pk and self.instance.photo):
                raise ValidationError(_('Photo is required for workers without an existing profile photo.'))
            return photo
        
        # Only validate if a new photo is being uploaded
        if photo and hasattr(photo, 'size') and hasattr(photo, 'name'):
            # Validate file type for new uploads
            import os
            ext = os.path.splitext(photo.name)[1].lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.enc']
            if ext not in valid_extensions:
                raise ValidationError(_('Invalid photo format. Please upload JPG, PNG, GIF, or BMP files only.'))
        
        return photo

    def clean(self):
        cleaned_data = super().clean()
        zone = cleaned_data.get('zone')
        building = cleaned_data.get('building')
        floor = cleaned_data.get('floor')
        
        # Chain select validation: Zone > Building > Floor
        if building and zone:
            if building.zone != zone:
                raise ValidationError({
                    'building': _('Selected building does not belong to the selected zone.')
                })
        
        if floor and building:
            if floor.building != building:
                raise ValidationError({
                    'floor': _('Selected floor does not belong to the selected building.')
                })
        
        if floor and zone:
            if floor.building.zone != zone:
                raise ValidationError({
                    'floor': _('Selected floor does not belong to the selected zone.')
                })
        
        # Age validation
        dob = cleaned_data.get('dob')
        if dob:
            from datetime import date
            age = (date.today() - dob).days / 365.25
            if age < 16:
                raise ValidationError(_('Worker must be at least 16 years old.'))
            if age > 100:
                raise ValidationError(_('Please check the date of birth.'))
                
        return cleaned_data


class ZoneForm(forms.ModelForm):
    """Form for creating and updating zones."""
    
    # Override the phone_number field to use our safe field
    phone_number = SafePhoneNumberField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label='Phone Number'
    )
    
    class Meta:
        model = Zone
        fields = ['name', 'phone_number', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter unique zone name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add help text for the name field
        self.fields['name'].help_text = 'Enter a unique name for this zone (e.g., "North District", "Downtown Area", "Industrial Zone")'



class WorkerProbationPeriodForm(forms.ModelForm):
    """Form for creating and updating worker probation periods."""
    
    # Add worker search field for auto-suggestion
    worker_search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for worker...',
            'autocomplete': 'off'
        }),
        label='Search Worker',
        help_text='Type to search for workers by name or ID'
    )
    
    # Add worker status field
    worker_status = forms.ChoiceField(
        choices=[
            ('probation', 'Probation'),
            ('extended', 'Extended'),
            ('passed', 'Passed'),
            ('failed', 'Failed'),
            ('terminated', 'Terminated'),
            ('active', 'Active'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Worker Status',
        help_text='Update the worker\'s current status'
    )
    
    class Meta:
        model = WorkerProbationPeriod
        fields = ['worker', 'start_date', 'original_end_date', 'actual_end_date', 'evaluation_notes']
        widgets = {
            'worker': forms.HiddenInput(),  # Hidden field to store selected worker ID
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'original_end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'actual_end_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date',
                'required': False
            }),
            'evaluation_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        # Remove worker from kwargs if editing existing probation period
        self.exclude_worker_field = kwargs.pop('exclude_worker_field', False)
        self.worker_id = kwargs.pop('worker_id', None)
        super().__init__(*args, **kwargs)
        
        if self.exclude_worker_field:
            del self.fields['worker']
            del self.fields['worker_search']
            # Keep worker_status field for editing existing probation periods
        else:
            # Filter to show workers eligible for probation creation
            # Primarily focus on 'active' workers, but allow creating probation for any eligible status
            eligible_statuses = ['active', 'probation', 'extended']
            
            # Build the base filter for eligible workers
            from django.db.models import Q
            base_filter = Q(
                status__in=eligible_statuses,
                is_vip=False  # Exclude VIPs - probation only for regular workers
            )
            
            # Note: Remove the restriction that prevents workers with existing probation periods
            # This allows creating new probation periods if the previous one is completed/terminated
            
            # If worker_id is provided, ensure that specific worker is in the queryset
            if self.worker_id:
                try:
                    specific_worker = Worker.objects.get(id=self.worker_id)
                    # Include the specific worker OR eligible workers (using OR logic)
                    worker_queryset = Worker.objects.filter(
                        Q(id=self.worker_id) | base_filter
                    ).select_related('zone', 'position').order_by('first_name', 'last_name')
                    
                    self.fields['worker'].initial = specific_worker
                    
                    # Provide appropriate help text
                    if specific_worker.is_vip:
                        self.fields['worker'].help_text = f"Note: {specific_worker.get_full_name()} is a VIP worker - probation creation may not be standard policy."
                    elif specific_worker.status not in eligible_statuses:
                        self.fields['worker'].help_text = f"Note: {specific_worker.get_full_name()} has status '{specific_worker.get_status_display()}' - verify probation is appropriate."
                    else:
                        self.fields['worker'].help_text = f"Pre-selected: {specific_worker.get_full_name()}"
                        
                except Worker.DoesNotExist:
                    # If specific worker doesn't exist, just use the base filter
                    worker_queryset = Worker.objects.filter(base_filter).select_related('zone', 'position').order_by('first_name', 'last_name')
                    self.fields['worker'].help_text = "Selected worker not found."
            else:
                # Use only the base filter for general probation creation
                worker_queryset = Worker.objects.filter(base_filter).select_related('zone', 'position').order_by('first_name', 'last_name')
                
                # Check if queryset is empty and provide helpful feedback
                worker_count = worker_queryset.count()
                if worker_count == 0:
                    self.fields['worker'].help_text = "No eligible workers found. Workers must be active (or on probation/extended), non-VIP to be eligible for probation."
                else:
                    self.fields['worker'].help_text = f"Found {worker_count} eligible workers. Select a worker to create probation period."
            
            self.fields['worker'].queryset = worker_queryset
        
        # Set default values for new probation periods (only if no instance is provided)
        if not self.instance.pk:
            from django.utils import timezone
            from datetime import timedelta
            
            today = timezone.now().date()
            end_date = today + timedelta(days=15)
            
            self.fields['start_date'].initial = today
            self.fields['original_end_date'].initial = end_date
            # Set default worker status to 'probation' for new probation periods
            self.fields['worker_status'].initial = 'probation'
        else:
            # For editing existing probation periods, set current worker status
            if self.instance.worker:
                self.fields['worker_status'].initial = self.instance.worker.status
        
        # Make actual_end_date explicitly optional (for both new and existing)
        self.fields['actual_end_date'].required = False
    
    def clean_actual_end_date(self):
        """Validate actual end date field - only if user provides a value."""
        actual_end_date = self.cleaned_data.get('actual_end_date')
        
        # If actual_end_date is not provided, skip all validation (probation is ongoing)
        if not actual_end_date:
            return None  # Explicitly return None for ongoing probations
        
        # Only validate if user actually entered a date
        try:
            # Get start_date from form data or existing instance
            start_date = self.cleaned_data.get('start_date')
            if not start_date and self.instance and hasattr(self.instance, 'start_date') and self.instance.start_date:
                start_date = self.instance.start_date
                
            # Only validate if we have a valid start_date to compare against
            if start_date and actual_end_date <= start_date:
                raise ValidationError('Actual end date must be after the start date.')
                
        except (AttributeError, TypeError):
            # If there's any issue with date comparison, skip validation
            pass
        
        return actual_end_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        original_end_date = cleaned_data.get('original_end_date')
        actual_end_date = cleaned_data.get('actual_end_date')
        # Status is now managed at the Worker level
        worker = cleaned_data.get('worker')
        
        if start_date and original_end_date:
            if original_end_date <= start_date:
                raise ValidationError({
                    'original_end_date': 'End date must be after start date.'
                })
                
            # Check probation period length (should be reasonable)
            duration = (original_end_date - start_date).days
            if duration > 365:
                raise ValidationError({
                    'original_end_date': 'Probation period cannot exceed 365 days.'
                })
            if duration < 1:
                raise ValidationError({
                    'original_end_date': 'Probation period must be at least 1 day.'
                })
        
        # Validate that only regular workers (not VIPs) can have probation periods
        # But allow it if worker_id was specifically provided (direct URL access)
        if worker and worker.is_vip and not self.worker_id:
            raise ValidationError("VIP workers are not eligible for probation periods. Probation is only available for regular workers.")
        
        # Check for existing active probation periods for the same worker
        # Allow creating new probation periods but warn about existing ones
        if worker and not self.instance.pk:  # Only for new probation periods
            active_probations = WorkerProbationPeriod.objects.filter(
                worker=worker,
                worker__status__in=['probation', 'extended']
            )
            # Only prevent if there are truly conflicting active probations with no end date
            ongoing_probations = active_probations.filter(actual_end_date__isnull=True)
            if ongoing_probations.exists() and not self.worker_id:
                # Only raise error if worker wasn't specifically selected (direct URL access)
                raise ValidationError(f"This worker has an ongoing probation period. Please complete or terminate the existing probation before creating a new one.")
        
        # Note: actual_end_date validation is handled in clean_actual_end_date method
                
        return cleaned_data
    
    def save(self, commit=True):
        """Save the probation period and update worker status if changed."""
        probation_period = super().save(commit=False)
        
        # Handle worker status update if provided
        worker_status = self.cleaned_data.get('worker_status')
        if worker_status and probation_period.worker:
            probation_period.worker.status = worker_status
            if commit:
                probation_period.worker.save()
        
        if commit:
            probation_period.save()
        
        return probation_period


class WorkerProbationExtensionForm(forms.ModelForm):
    """Form for creating probation extensions."""
    
    class Meta:
        model = WorkerProbationExtension
        fields = ['probation_period', 'extension_duration_days', 'reason', 'approved_by']
        widgets = {
            'probation_period': forms.Select(attrs={'class': 'form-select'}),
            'extension_duration_days': forms.NumberInput(attrs={
                'class': 'form-control', 
                'style':'border-radius:10px !important',
                'min': 1, 
                'max': 15,  # Maximum possible extension is 15 days (30 total - 15 default)
                'title': 'Maximum total probation period is 30 days (15 days default + 15 days maximum extension)'
            }),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,'style':'border-radius:10px !important'}),
            'approved_by': forms.Select(attrs={'class': 'form-select','style':'border-radius:10px !important'}),
        }

    def __init__(self, *args, **kwargs):
        # Remove probation_period from kwargs if extending specific probation
        self.exclude_probation_field = kwargs.pop('exclude_probation_field', False)
        worker = kwargs.pop('worker', None)
        super().__init__(*args, **kwargs)
        
        if self.exclude_probation_field:
            del self.fields['probation_period']
        else:
            # Only set up probation_period field if it exists
            # Filter probation periods to only active ones if worker is specified
            if worker:
                self.fields['probation_period'].queryset = WorkerProbationPeriod.objects.filter(
                    worker=worker,
                    worker__status__in=['probation', 'extended']
                )
            else:
                self.fields['probation_period'].queryset = WorkerProbationPeriod.objects.filter(
                    worker__status__in=['probation', 'extended']
                )
        
        # Filter approved_by to only staff users
        self.fields['approved_by'].queryset = User.objects.filter(is_staff=True)
        
        # Add help text for extension duration
        self.fields['extension_duration_days'].help_text = (
            "Maximum total probation period is 30 days (15 days default + 15 days maximum extension). "
            "Enter number of days to extend the probation period."
        )

    def clean_extension_duration_days(self):
        extension_days = self.cleaned_data.get('extension_duration_days')
        if extension_days and extension_days <= 0:
            raise ValidationError("Extension duration must be positive.")
        if extension_days and extension_days > 15:
            raise ValidationError("Extension duration cannot exceed 15 days (maximum total probation is 30 days).")
        return extension_days

    def clean(self):
        cleaned_data = super().clean()
        probation_period = cleaned_data.get('probation_period')
        extension_duration_days = cleaned_data.get('extension_duration_days')
        
        if probation_period:
            # Check if probation period is eligible for extension
            if probation_period.worker.status not in ['probation', 'extended']:
                raise ValidationError("Only probation or extended workers can have their probation extended.")
                
            # Check if probation period hasn't already ended
            from django.utils import timezone
            today = timezone.now().date()
            end_date = probation_period.actual_end_date or probation_period.original_end_date
            if end_date < today:
                raise ValidationError("Cannot extend a probation period that has already ended.")
                
            # Business Rule: Validate 30-day maximum total probation
            if extension_duration_days:
                current_total_extension_days = sum(ext.extension_duration_days for ext in probation_period.extensions.all())
                new_total_extension_days = current_total_extension_days + extension_duration_days
                
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
                
        return cleaned_data


class ProbationSearchForm(forms.Form):
    """Form for searching and filtering probation periods."""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by worker name or ID...'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + [
            ('probation', 'Probation'),
            ('extended', 'Extended'),
            ('passed', 'Passed'),
            ('failed', 'Failed'),
            ('terminated', 'Terminated'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    zone = forms.ModelChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        empty_label="All Zones",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    position = forms.ModelChoiceField(
        queryset=Position.objects.all(),
        required=False,
        empty_label="All Positions",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    building = forms.ModelChoiceField(
        queryset=Building.objects.all(),
        required=False,
        empty_label="All Buildings",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    days_remaining = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('overdue', 'Overdue'),
            ('ending_soon', 'Ending Soon (≤7 days)'),
            ('ending_month', 'Ending This Month (≤30 days)'),
            ('normal', 'More Than 30 Days'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    batch_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by batch name...'
        }),
        help_text='Filter by batch name (leave empty to show all)'
    )
    


class WorkerProbationTerminationForm(forms.ModelForm):
    """Form for terminating a worker during probation period."""
    
    termination_reason = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please provide a detailed reason for terminating this worker during probation...',
            'required': True
        }),
        help_text='Provide a clear and detailed reason for the termination decision.',
        max_length=1000
    )
    
    terminated_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        }),
        help_text='Date when the termination is effective.'
    )
    
    confirm_termination = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'required': True
        }),
        help_text='I confirm that I want to terminate this worker during probation period.',
        error_messages={
            'required': 'You must confirm the termination to proceed.'
        }
    )
    
    class Meta:
        model = WorkerProbationPeriod
        fields = ['termination_reason', 'terminated_date']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default terminated_date to today
        from django.utils import timezone
        self.fields['terminated_date'].initial = timezone.now().date()
        
        # Add required asterisk to labels
        self.fields['termination_reason'].label = 'Termination Reason *'
        self.fields['terminated_date'].label = 'Termination Date *'
        self.fields['confirm_termination'].label = 'Confirm Termination *'
    
    def clean_terminated_date(self):
        terminated_date = self.cleaned_data.get('terminated_date')
        if terminated_date:
            from django.utils import timezone
            today = timezone.now().date()
            
            # Termination date cannot be in the future
            if terminated_date > today:
                raise forms.ValidationError("Termination date cannot be in the future.")
            
            # If we have the probation instance, check if termination date is within probation period
            if self.instance and self.instance.start_date:
                if terminated_date < self.instance.start_date:
                    raise forms.ValidationError("Termination date cannot be before the probation start date.")
        
        return terminated_date
    
    def clean_termination_reason(self):
        reason = self.cleaned_data.get('termination_reason')
        if reason:
            # Ensure minimum length for meaningful reason
            if len(reason.strip()) < 10:
                raise forms.ValidationError("Please provide a more detailed reason (at least 10 characters).")
        return reason
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Additional validation can be added here if needed
        # For example, checking if the probation is eligible for termination
        if self.instance and self.instance.worker.status not in ['probation', 'extended']:
            raise forms.ValidationError("Only workers with probation or extended status can have their probation terminated.")
        
        return cleaned_data


class ProbationExtensionRequestForm(forms.ModelForm):
    """Form for creating probation extension requests (maker-checker workflow)."""
    
    class Meta:
        model = ProbationExtensionRequest
        fields = ['extension_duration_days', 'reason']
        widgets = {
            'extension_duration_days': forms.NumberInput(attrs={
                'class': 'form-control', 
                'style': 'border-radius:10px !important',
                'min': 1, 
                'max': 15,  # Maximum possible extension is 15 days
                'title': 'Maximum total probation period is 30 days (15 days default + 15 days maximum extension)'
            }),
            'reason': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4,
                'style': 'border-radius:10px !important',
                'placeholder': 'Please provide a detailed reason for the extension request...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.probation_period = kwargs.pop('probation_period', None)
        super().__init__(*args, **kwargs)
        
        # Set dynamic max value based on remaining extension days
        if self.probation_period:
            max_allowed = self.probation_period.get_max_allowed_extension_days()
            self.fields['extension_duration_days'].widget.attrs['max'] = max_allowed
            self.fields['extension_duration_days'].help_text = f"Maximum extension allowed: {max_allowed} days"

    def clean_extension_duration_days(self):
        extension_days = self.cleaned_data.get('extension_duration_days')
        
        if extension_days and extension_days <= 0:
            raise forms.ValidationError("Extension duration must be positive.")
        
        if self.probation_period:
            max_allowed = self.probation_period.get_max_allowed_extension_days()
            if extension_days > max_allowed:
                raise forms.ValidationError(
                    f"Extension duration exceeds maximum allowed. "
                    f"Maximum additional extension allowed: {max_allowed} days."
                )
        
        return extension_days

    def clean_reason(self):
        reason = self.cleaned_data.get('reason')
        if reason and len(reason.strip()) < 20:
            raise forms.ValidationError("Please provide a detailed reason (at least 20 characters).")
        return reason


class ProbationExtensionRequestReviewForm(forms.ModelForm):
    """Form for managers to approve/reject extension requests."""
    
    class Meta:
        model = ProbationExtensionRequest
        fields = ['status', 'review_comments']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'review_comments': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Optional comments on your decision...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow approval/rejection statuses
        self.fields['status'].choices = [
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ]


class WorkerExcelImportForm(forms.Form):
    """Form for importing workers from Excel file."""
    
    excel_file = forms.FileField(
        label='Excel File',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': '.xlsx,.xls',
            'required': 'required',
        }),
        help_text='Upload the Excel file containing worker data with embedded images.'
    )
    
    update_existing = forms.BooleanField(
        label='Update Existing Workers',
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Update existing workers if matching records are found (based on name).'
    )
    
    skip_duplicates = forms.BooleanField(
        label='Skip Duplicate Workers',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text='Skip workers that already exist in the system.'
    )
    
    def clean_excel_file(self):
        excel_file = self.cleaned_data.get('excel_file')
        
        if not excel_file:
            raise ValidationError('Please select an Excel file to upload.')
            
        # Check file extension
        if not excel_file.name.lower().endswith(('.xlsx', '.xls')):
            raise ValidationError('Please upload an Excel file (.xlsx or .xls)')

        # Check file size (max 100MB)
        if excel_file.size > 100 * 1024 * 1024:
            raise ValidationError('Excel file too large. Maximum size is 100MB.')
        
        # Skip complex validation here - we'll do it in the view
        # This avoids file locking issues during form validation
        return excel_file
    
    def clean_photos_folder(self):
        photos_folder = self.cleaned_data.get('photos_folder')
        
        if photos_folder:
            # Check if folder exists
            if not os.path.exists(photos_folder):
                raise ValidationError('Photos folder does not exist.')
            
            if not os.path.isdir(photos_folder):
                raise ValidationError('Photos folder path is not a directory.')
        
        return photos_folder 
    

class UploadExcelForm(forms.Form):
    file = forms.FileField()


class BatchProbationForm(forms.Form):
    """Form for creating probation periods for multiple workers at once."""
    
    # Batch identification
    batch_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., "January 2025 New Hires", "Zone 3H Staff Probation"'
        }),
        label='Batch Name',
        help_text='Enter a unique name to identify this probation batch. This helps with tracking and reporting.',
        required=True
    )
    
    # Filter fields for worker selection
    filter_zone = forms.ModelChoiceField(
        queryset=Zone.objects.all(),
        required=False,
        empty_label="All Zones",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    filter_building = forms.ModelChoiceField(
        queryset=Building.objects.all(),
        required=False,
        empty_label="All Buildings",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    filter_floor = forms.ModelChoiceField(
        queryset=Floor.objects.all(),
        required=False,
        empty_label="All Floors", 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    filter_date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Joined From',
        help_text='Filter workers joined from this date'
    )
    
    filter_date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Joined To',
        help_text='Filter workers joined up to this date'
    )
    
    # Workers selection - will be populated dynamically
    workers = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.none(),  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Select Workers',
        help_text='Choose workers to create probation periods for. Only active workers eligible for probation are shown.',
        required=True
    )
    
    # Common probation period details
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='Start Date',
        help_text='Start date for all selected probation periods'
    )
    
    original_end_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label='End Date',
        help_text='End date for all selected probation periods'
    )
    
    evaluation_notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        label='Evaluation Notes',
        help_text='Common notes for all probation periods (optional)',
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default date range (1 month period)
        from datetime import date, timedelta
        today = date.today()
        one_month_ago = today - timedelta(days=30)
        
        self.fields['filter_date_from'].initial = one_month_ago
        self.fields['filter_date_to'].initial = today
        
        # Filter to show workers eligible for probation creation
        # Focus on 'active' workers who don't have active probation periods
        from django.db.models import Q
        
        # Get workers who are eligible for probation
        # Start with basic filtering to show active non-VIP workers
        
        try:
            # First check if Worker table exists and has data
            total_workers = Worker.objects.count()
            
            if total_workers == 0:
                # No workers in database at all
                eligible_workers = Worker.objects.none()
                self.fields['workers'].help_text = "No workers found in the system. Please add workers first before creating probation periods."
            else:
                # Filter for eligible workers - active, non-VIP, without active probation periods
                from django.db.models import Exists, OuterRef
                
                # Subquery to find workers with active probation periods
                active_probations = WorkerProbationPeriod.objects.filter(
                    worker=OuterRef('pk'),
                    actual_end_date__isnull=True  # No end date means probation is still active
                )
                
                eligible_workers = Worker.objects.filter(
                    status='active',  # Only active workers
                    is_vip=False  # Exclude VIPs
                ).annotate(
                    has_active_probation=Exists(active_probations)
                ).filter(
                    has_active_probation=False  # Only workers without active probation
                ).select_related('zone', 'position', 'building', 'floor').order_by('first_name', 'last_name')
                
                # Apply additional filters based on form data
                if self.data:  # Only apply filters if form has data (during filtering)
                    # Zone filter
                    zone_filter = self.data.get('filter_zone')
                    if zone_filter:
                        eligible_workers = eligible_workers.filter(zone_id=zone_filter)
                    
                    # Building filter
                    building_filter = self.data.get('filter_building') 
                    if building_filter:
                        eligible_workers = eligible_workers.filter(building_id=building_filter)
                    
                    # Floor filter
                    floor_filter = self.data.get('filter_floor')
                    if floor_filter:
                        try:
                            eligible_workers = eligible_workers.filter(floor_id=floor_filter)
                        except Exception:
                            # Ignore floor filter if there's a database issue
                            pass
                    
                    # Date range filter
                    date_from = self.data.get('filter_date_from')
                    date_to = self.data.get('filter_date_to')

                    if date_from and date_to:
                        try:
                            from_date = date.fromisoformat(date_from)
                            to_date = date.fromisoformat(date_to)

                            # Validate date range
                            if from_date > to_date:
                                # Don't filter if dates are invalid
                                pass
                            else:
                                eligible_workers = eligible_workers.filter(
                                    date_joined__gte=from_date,
                                    date_joined__lte=to_date
                                )
                        except ValueError:
                            pass  # Invalid date format, ignore filter
                    elif date_from:
                        try:
                            from_date = date.fromisoformat(date_from)
                            eligible_workers = eligible_workers.filter(date_joined__gte=from_date)
                        except ValueError:
                            pass  # Invalid date format, ignore filter
                    elif date_to:
                        try:
                            to_date = date.fromisoformat(date_to)
                            eligible_workers = eligible_workers.filter(date_joined__lte=to_date)
                        except ValueError:
                            pass  # Invalid date format, ignore filter
                else:
                    # Apply default 1-month filter for initial load
                    eligible_workers = eligible_workers.filter(
                        date_joined__gte=one_month_ago,
                        date_joined__lte=today
                    )
                
                # Get counts for better feedback
                worker_count = eligible_workers.count()
                active_workers_count = Worker.objects.filter(status='active').count()
                vip_workers_count = Worker.objects.filter(is_vip=True).count()
                
                # Count active non-VIP workers (before probation filtering)
                active_nonvip_count = Worker.objects.filter(status='active', is_vip=False).count()
                
                # Count workers with active probation periods
                workers_with_probation = Worker.objects.filter(
                    probation_periods__actual_end_date__isnull=True
                ).distinct().count()
                
                if worker_count == 0:
                    # Provide detailed feedback about why no workers are available
                    debug_info = []
                    if active_workers_count == 0:
                        debug_info.append("No workers with 'active' status")
                    else:
                        debug_info.append(f"{active_workers_count} active workers")
                    
                    if vip_workers_count > 0:
                        debug_info.append(f"{vip_workers_count} VIP workers excluded")
                    
                    if active_nonvip_count > 0:
                        debug_info.append(f"{active_nonvip_count} active non-VIP workers")
                        if workers_with_probation > 0:
                            debug_info.append(f"{workers_with_probation} already have active probation periods")
                    
                    self.fields['workers'].help_text = (
                        f"No eligible workers found. Debug: {' | '.join(debug_info)}. "
                        f"Total: {total_workers} workers. "
                        "Requirements: Active status, non-VIP, no current probation period."
                    )
                else:
                    self.fields['workers'].help_text = (
                        f"Choose from {worker_count} eligible workers. "
                        f"({total_workers} total, {active_workers_count} active, "
                        f"{vip_workers_count} VIPs, {workers_with_probation} with active probation excluded)"
                    )
        except Exception as e:
            # Handle database connection or other issues gracefully
            eligible_workers = Worker.objects.none()
            self.fields['workers'].help_text = f"Error loading workers: {str(e)}. Please contact system administrator."
        
        self.fields['workers'].queryset = eligible_workers
        
        # Set default start date to today
        self.fields['start_date'].initial = date.today()
        
        # Worker count info and help text are already set above based on the filtering results
    
    def clean_batch_name(self):
        batch_name = self.cleaned_data.get('batch_name')
        if batch_name:
            # Check if batch name already exists by looking in evaluation_notes
            # We'll store batch names in the evaluation_notes field for tracking
            existing_batch = WorkerProbationPeriod.objects.filter(
                evaluation_notes__icontains=f'Batch: {batch_name}'
            ).exists()
            
            if existing_batch:
                raise forms.ValidationError(f'A batch with the name "{batch_name}" already exists. Please choose a different name.')
        
        return batch_name
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        original_end_date = cleaned_data.get('original_end_date')
        workers = cleaned_data.get('workers')
        batch_name = cleaned_data.get('batch_name')
        
        # Validate date range
        if start_date and original_end_date:
            if original_end_date <= start_date:
                raise forms.ValidationError('End date must be after start date.')
        
        # Validate at least one worker is selected
        if not workers:
            raise forms.ValidationError('You must select at least one worker.')
        
        # Validate batch name is provided
        if not batch_name:
            raise forms.ValidationError('Batch name is required.')
            
        return cleaned_data