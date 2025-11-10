from django import forms
from django.utils import timezone
from datetime import date, timedelta
from django.db.models import Q
from decimal import Decimal

from .models import WorkerIDCard, CardReplacement, EmployeeIDCard
from zone.models import Worker, Zone, Building
from zone.models import WorkerProbationPeriod


class WorkerIDCardForm(forms.ModelForm):
    """Form for creating and updating Worker ID cards."""
    
    # Add a custom search field for worker autocomplete
    worker_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for worker by name, ID, email, or phone...',
            'autocomplete': 'off'
        }),
        label='Search Worker',
        help_text='Only workers with "Passed" status are eligible for ID cards'
    )
    
    # Add card_number field for manual assignment/editing
    card_number = forms.CharField(
        required=False,
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Auto-generated (e.g., 3H-B1-F11-0001)'
        }),
        label='Card Number',
        help_text='Format: {ZONE}-{BUILDING}-{FLOOR}-{SEQUENCE} (e.g., 3H-B1-F11-0001). Will be auto-generated based on worker location.'
    )
    
    class Meta:
        model = WorkerIDCard
        fields = [
            'worker', 'card_number', 'status', 'issue_date', 'expiry_date', 'photo'
        ]
        widgets = {
            'worker': forms.HiddenInput(),  # Hidden field to store the selected worker ID
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'id': 'photoInput',
                'style': 'display: none;'
            }),
        }

    def __init__(self, *args, **kwargs):
        # Extract card_type parameter before calling super()
        self.card_type = kwargs.pop('card_type', 'regular')
        self.user = kwargs.pop('user', None)  # Add user parameter for role checking
        super().__init__(*args, **kwargs)
        
        # Filter workers based on the card type being created
        from django.db.models import Q
        
        if self.instance.pk:
            # For existing cards, always include the current worker in queryset
            # This prevents validation errors when updating existing cards
            eligible_workers = Worker.objects.filter(
                id=self.instance.worker_id
            ).select_related('position', 'building', 'zone')
        elif self.card_type == 'vip':
            # For VIP card creation, only show VIP workers
            eligible_workers = Worker.objects.filter(
                is_vip=True
            ).select_related('position', 'building', 'zone').order_by('first_name', 'last_name')
        else:
            # For regular card creation, only show non-VIP workers with passed status
            eligible_workers = Worker.objects.filter(
                is_vip=False,  # Only non-VIP workers
                status='passed'  # Only workers who have passed probation
            ).select_related('position', 'building', 'zone').order_by('first_name', 'last_name')

        self.fields['worker'].queryset = eligible_workers
        
        # Set default dates and card number if creating new card
        if not self.instance.pk:
            self.fields['issue_date'].initial = date.today()
            self.fields['expiry_date'].initial = date.today() + timedelta(days=365)
            # Pre-generate a card number that user can modify
            self.fields['card_number'].initial = self._generate_default_card_number()
        else:
            # If editing, populate the search field with the current worker's name and card number
            if self.instance.worker:
                self.fields['worker_search'].initial = self.instance.worker.get_full_name()
                # IMPORTANT: Set the worker field initial value to the current worker
                self.fields['worker'].initial = self.instance.worker
            # Populate card_number field with current card number
            if self.instance.card_number:
                self.fields['card_number'].initial = self.instance.card_number
        
        # Make worker field not required in form validation since we handle it in clean()
        self.fields['worker'].required = False

        # Ensure status field uses the latest choices from the model
        # This is important to avoid caching issues
        self.fields['status'].choices = self._meta.model.STATUS_CHOICES
    
    def _generate_default_card_number(self, worker=None):
        """Generate a default card number for new cards"""
        import uuid
        from django.utils import timezone
        
        # If worker is provided and has building/floor, use building-floor format
        if worker and worker.building and worker.floor:
            return self._generate_building_floor_card_number(worker)
        
        # Generate a fallback card number format: WID{YEAR}{HEX}
        year = timezone.now().year
        hex_part = str(uuid.uuid4().hex[:6]).upper()
        return f"WID{year}{hex_part}"
    
    def _generate_building_floor_card_number(self, worker):
        """Generate card number based on worker's zone, building and floor"""
        from .models import WorkerIDCard
        
        # Get zone, building, and floor information
        zone_raw = getattr(worker.zone, 'name', 'Z') if worker.zone else 'Z'
        building_raw = getattr(worker.building, 'name', 'B') if worker.building else 'B'
        
        # Extract proper zone name - if zone contains underscore, take only the first part
        # This handles cases where zone name is stored as "3H_B12" instead of just "3H"
        if '_' in zone_raw:
            # If zone name contains underscore (like "3H_B12"), extract just the zone part (3H)
            zone_parts = zone_raw.split('_')
            zone_name = zone_parts[0]
        else:
            zone_name = zone_raw.replace(' ', '')
            
        # Additional cleanup: if zone name looks like it contains building info, extract zone only
        # Handle patterns like "3HB12" -> "3H"
        import re
        # If zone name has pattern like "3H" followed by "B" and numbers, extract just the zone part
        zone_match = re.match(r'^([A-Za-z0-9]+)B[0-9]+.*', zone_name)
        if zone_match:
            zone_name = zone_match.group(1)
        
        # Extract proper building name
        building_name = building_raw.replace('_', '').replace(' ', '')
        
        floor_name = ''
        if worker.floor:
            # Get floor name or number
            if hasattr(worker.floor, 'name') and worker.floor.name:
                floor_name = worker.floor.name
            elif hasattr(worker.floor, 'floor_number'):
                floor_name = f"F{worker.floor.floor_number}"
            else:
                floor_name = str(worker.floor)[:10]
        else:
            floor_name = 'F0'
        
        # Clean floor name - remove any underscores or special characters
        floor_name = floor_name.replace('_', '').replace(' ', '')
        
        # Create the prefix with Zone-Building-Floor format
        prefix = f"{zone_name}-{building_name}-{floor_name}-"

        # Find the next sequence number for this zone-building-floor combination
        existing_cards = WorkerIDCard.objects.filter(
            card_number__startswith=prefix
        )
        
        sequence_numbers = []
        for card in existing_cards:
            try:
                # Extract the sequence number from the end
                seq_part = card.card_number.split('-')[-1]
                if seq_part.isdigit():
                    sequence_numbers.append(int(seq_part))
            except (IndexError, ValueError):
                continue
        
        # Get next sequence number
        next_sequence = max(sequence_numbers, default=0) + 1
        
        return f"{zone_name}-{building_name}-{floor_name}-{next_sequence:04d}"
    
    def clean_worker(self):
        """Custom validation for worker field."""
        worker = self.cleaned_data.get('worker')

        # For existing cards, if no worker is provided, use the current worker
        if not worker and self.instance.pk and self.instance.worker:
            worker = self.instance.worker
            # Update cleaned_data to include the worker
            self.cleaned_data['worker'] = worker

        if not worker:
            raise forms.ValidationError("Please select a worker from the search results.")
        
        # Validate worker eligibility based on card type
        if self.card_type == 'vip':
            # For VIP cards, only VIP workers are allowed
            if not worker.is_vip:
                raise forms.ValidationError(
                    f"Worker {worker.get_full_name()} is not a VIP worker. "
                    f"VIP cards can only be created for workers marked as VIP."
                )
        else:
            # For regular cards, only non-VIP workers with passed status are allowed
            if worker.is_vip:
                raise forms.ValidationError(
                    f"Worker {worker.get_full_name()} is a VIP worker. "
                    f"Please use the VIP card creation process for this worker."
                )
            if worker.status != 'passed':
                raise forms.ValidationError(
                    f"Worker {worker.get_full_name()} has not passed probation (current status: {worker.get_status_display()}). "
                    f"Regular ID cards can only be created for workers with 'Passed' status."
                )
        
        # Check if worker already has an active ID card (when creating new card)
        if not self.instance.pk:  # Only check for new cards
            existing_card = WorkerIDCard.objects.filter(
                worker=worker,
                status__in=['pending', 'approved', 'printed', 'delivered', 'active']
            ).first()
            
            if existing_card:
                raise forms.ValidationError(
                    f"Worker {worker.get_full_name()} already has an active ID card "
                    f"(Status: {existing_card.get_status_display()}). "
                    f"Please complete or cancel the existing card first."
                )
        
        return worker
    
    def clean_card_number(self):
        """Custom validation for card number field."""
        card_number = self.cleaned_data.get('card_number')
        
        # If no card number provided, we'll handle it in clean() method
        if not card_number:
            return card_number
        
        # Validate format: should be either {ZONE}-{BUILDING}-{FLOOR}-{SEQUENCE} or WID{YEAR}{HEX}
        import re
        # Pattern for Zone-Building-Floor-Sequence (e.g., 3H-B1-F11-0001)
        # Allow alphanumeric characters but no underscores in each segment
        zone_building_floor_pattern = r'^[A-Za-z0-9]+\-[A-Za-z0-9]+\-[A-Za-z0-9]+\-[0-9]{4}$'
        # Pattern for fallback format WID{YEAR}{HEX}
        fallback_pattern = r'^WID[0-9]{4}[A-Za-z0-9]{6}$'
        
        if not (re.match(zone_building_floor_pattern, card_number, re.IGNORECASE) or re.match(fallback_pattern, card_number, re.IGNORECASE)):
            raise forms.ValidationError(
                "Card number format must be {ZONE}-{BUILDING}-{FLOOR}-{SEQUENCE} (e.g., 3H-B1-F11-0001) "
                "or WID{YEAR}{HEX} (e.g., WID2025A1B2C3)"
            )
        
        # Check if card number is unique (excluding current instance)
        from .models import WorkerIDCard
        existing_card = WorkerIDCard.objects.filter(card_number=card_number)
        if self.instance.pk:
            existing_card = existing_card.exclude(pk=self.instance.pk)
        
        if existing_card.exists():
            existing_card_obj = existing_card.first()
            raise forms.ValidationError(
                f"Card number '{card_number}' is already in use by "
                f"{existing_card_obj.worker.get_full_name()} ({existing_card_obj.worker.worker_id})"
            )
        
        return card_number
    
    def clean(self):
        """Additional form validation."""
        cleaned_data = super().clean()
        worker = cleaned_data.get('worker')
        card_number = cleaned_data.get('card_number')
        
        # If no card number provided, generate one based on selected worker
        if not card_number:
            if self.instance.pk and self.instance.card_number:
                # If editing an existing card, use current card number
                cleaned_data['card_number'] = self.instance.card_number
            else:
                # If creating new card, use worker info to generate card number
                generated_number = self._generate_default_card_number(worker)
                # Make sure it's unique by checking existing cards
                from .models import WorkerIDCard
                counter = 1
                while WorkerIDCard.objects.filter(card_number=generated_number).exists():
                    # If collision with zone-building-floor format, increment sequence
                    if worker and worker.zone and worker.building and worker.floor and generated_number.count('-') >= 3:
                        # Extract current sequence and increment
                        parts = generated_number.split('-')
                        if len(parts) >= 4 and parts[-1].isdigit():
                            current_seq = int(parts[-1])
                            parts[-1] = f"{current_seq + counter:04d}"
                            generated_number = '-'.join(parts)
                        else:
                            # Regenerate if format is unexpected
                            generated_number = self._generate_default_card_number(worker)
                    else:
                        # For fallback format, generate a new UUID-based number
                        generated_number = self._generate_default_card_number(worker)
                    counter += 1
                    # Safety break to avoid infinite loop
                    if counter > 100:
                        break
                cleaned_data['card_number'] = generated_number
        
        return cleaned_data





class CardReplacementForm(forms.ModelForm):
    """Form for creating and updating Card replacement requests."""
    
    # Add worker search field for easier worker selection
    worker_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for worker by name, ID, email, or phone...',
            'autocomplete': 'off'
        }),
        label='Search Worker',
        help_text='Start typing to search for a worker, then select their card below'
    )
    
    # Add VIP search field for easier VIP selection
    vip_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for VIP by name, email, or phone...',
            'autocomplete': 'off'
        }),
        label='Search VIP',
        help_text='Start typing to search for a VIP, then select their card below'
    )
    
    # Add employee search field for easier employee selection
    employee_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for employee by name, ID, email, or phone...',
            'autocomplete': 'off'
        }),
        label='Search Employee',
        help_text='Start typing to search for an employee, then select their card below'
    )
    
    class Meta:
        model = CardReplacement
        fields = ['worker_card', 'employee_card', 'reason', 'notes']
        widgets = {
            'worker_card': forms.HiddenInput(),  # Hidden field to preserve worker card
            'employee_card': forms.HiddenInput(), # Hidden field to preserve employee card
            'reason': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Please describe the reason for replacement...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['reason'].label = 'Reason for Replacement'
        self.fields['notes'].label = 'Additional Notes'
        self.fields['notes'].required = False
        
        # Make card fields optional (since only one will be set)
        self.fields['worker_card'].required = False
        self.fields['employee_card'].required = False

    def clean(self):
        cleaned_data = super().clean()
        worker_card = cleaned_data.get('worker_card')
        employee_card = cleaned_data.get('employee_card')

        # Ensure exactly one card type is selected
        selected_cards = sum([bool(worker_card), bool(employee_card)])
        
        if selected_cards == 0:
            raise forms.ValidationError("Please select a card to replace.")
        
        if selected_cards > 1:
            raise forms.ValidationError("Please select only one card to replace.")

        return cleaned_data

    def get_estimated_charge(self):
        """Calculate estimated replacement charge based on form data"""
        if self.instance and self.instance.pk:
            return self.instance.replacement_charge
        return Decimal('0.00')

# Simplified forms for approval and completion workflows
class CardReplacementApprovalForm(forms.Form):
    """Form for approving or rejecting card replacement requests"""
    action = forms.ChoiceField(
        choices=[('approve', 'Approve'), ('reject', 'Reject')],
        widget=forms.RadioSelect,
        required=True
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label='Approval/Rejection Notes'
    )

class CardReplacementCompletionForm(forms.Form):
    """Form for completing card replacement requests"""
    new_card_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter new card number'}),
        label='New Card Number'
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        required=False,
        label='Completion Notes'
    )


# ============================================================================
# SEARCH FORMS
# ============================================================================

class WorkerIDCardSearchForm(forms.Form):
    """Search form for Worker ID cards list."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by worker name, ID, or card number...',
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + WorkerIDCard.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    building = forms.ModelChoiceField(
        required=False,
        queryset=Building.objects.all(),
        empty_label="All Buildings",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    zone = forms.ModelChoiceField(
        required=False,
        queryset=Zone.objects.select_related('created_by'),
        empty_label="All Zones",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    batch = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by batch name...',
        })
    )
    
    date_range = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Time'),
            ('today', 'Today'),
            ('week', 'Last 7 Days'),
            ('month', 'Last 30 Days'),
            ('year', 'Last Year'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )





class CardReplacementSearchForm(forms.Form):
    """Search form for Card replacements list."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, card number...',
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + CardReplacement.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    reason = forms.ChoiceField(
        required=False,
        choices=[('', 'All Reasons')] + CardReplacement.REASON_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_range = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Time'),
            ('today', 'Today'),
            ('week', 'Last 7 Days'),
            ('month', 'Last 30 Days'),
            ('year', 'Last Year'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


# ============================================================================
# BATCH CREATION FORMS  
# ============================================================================

class BatchWorkerIDCardForm(forms.Form):
    """Form for batch creating Worker ID cards."""
    
    workers = forms.ModelMultipleChoiceField(
        queryset=Worker.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Select Regular Workers',
        help_text='Choose regular workers to create ID cards for (only non-VIP workers who have completed probation are shown)'
    )
    
    status = forms.ChoiceField(
        choices=WorkerIDCard.STATUS_CHOICES,
        initial='pending',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Initial Status'
    )
    
    issue_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Issue Date',
        help_text='Leave blank for cards in pending status'
    )
    
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Expiry Date',
        initial=lambda: date.today() + timedelta(days=365)
    )
    
    copy_worker_photo = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Copy Worker Photos',
        help_text='Automatically copy worker photos to ID cards (recommended)'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes for all cards...'
        }),
        label='Notes'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Only show regular workers with 'passed' status (exclude VIP workers)
        from django.db.models import Q
        
        eligible_workers = Worker.objects.filter(
            status='passed',  # Only workers who have passed probation
            is_vip=False  # Exclude VIP workers - only regular workers
        ).exclude(
            id_cards__status__in=['pending', 'approved', 'printed', 'delivered', 'active']
        ).select_related('position', 'building', 'zone').order_by('first_name', 'last_name')
        
        self.fields['workers'].queryset = eligible_workers
        
        # Update help text with current count
        eligible_count = eligible_workers.count()
        
        # Count regular workers who have passed probation (excluding VIPs)
        total_passed = Worker.objects.filter(
            status='passed',
            is_vip=False
        ).count()
        workers_with_cards = total_passed - eligible_count
        
        self.fields['workers'].help_text = (
            f'Choose regular workers to create ID cards for (VIP workers excluded). '
            f'Showing {eligible_count} eligible workers out of {total_passed} who passed probation '
            f'({workers_with_cards} already have active ID cards)'
        )

    def clean(self):
        """Custom validation for batch creation."""
        cleaned_data = super().clean()
        workers = cleaned_data.get('workers')
        status = cleaned_data.get('status')
        issue_date = cleaned_data.get('issue_date')
        
        if not workers:
            raise forms.ValidationError("Please select at least one worker.")
        
        # Validate that all selected workers have passed probation and are not VIP
        for worker in workers:
            if worker.is_vip:
                raise forms.ValidationError(
                    f"Worker {worker.get_full_name()} is a VIP worker and cannot be processed through batch creation. Please create their ID card individually."
                )
            if worker.status != 'passed':
                raise forms.ValidationError(
                    f"Worker {worker.get_full_name()} has not passed probation (status: {worker.get_status_display()}) and cannot receive an ID card."
                )
        
        # If status requires issue_date, make sure it's provided
        if status in ['approved', 'printed', 'delivered', 'active'] and not issue_date:
            raise forms.ValidationError("Issue date is required for the selected status.")
        
        return cleaned_data


class WorkerSelectionForm(forms.Form):
    """Form for selecting workers for batch operations."""
    
    building = forms.ModelChoiceField(
        required=False,
        queryset=Building.objects.all(),
        empty_label="All Buildings",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Filter by Building'
    )
    
    zone = forms.ModelChoiceField(
        required=False,
        queryset=Zone.objects.select_related('created_by'),
        empty_label="All Zones",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Filter by Zone'
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Workers')] + Worker.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Worker Status'
    )
    
    has_photo = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Workers'),
            ('yes', 'With Photo Only'),
            ('no', 'Without Photo Only')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Photo Status'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        from zone.models import Building, Zone
        
        # Set querysets
        self.fields['building'].queryset = Building.objects.all()
        self.fields['zone'].queryset = Zone.objects.select_related('created_by')
        
        # Set status choices
        self.fields['status'].choices = [('', 'All Workers')] + Worker.STATUS_CHOICES


class PrintingPreviewForm(forms.Form):
    """Form for printing preview options."""
    
    cards = forms.ModelMultipleChoiceField(
        queryset=WorkerIDCard.objects.none(),
        widget=forms.MultipleHiddenInput(),
        label='Selected Cards'
    )
    
    print_layout = forms.ChoiceField(
        choices=[
            ('single', 'Single Card per Page'),
            ('grid_2x2', '2x2 Grid (4 cards per page)'),
            ('grid_3x3', '3x3 Grid (9 cards per page)'),
            ('grid_4x4', '4x4 Grid (16 cards per page)'),
        ],
        initial='grid_2x2',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Print Layout'
    )
    
    card_size = forms.ChoiceField(
        choices=[
            ('standard', 'Standard ID Card (85.6 × 53.98 mm)'),
            ('large', 'Large ID Card (100 × 65 mm)'),
            ('badge', 'Badge Size (90 × 60 mm)'),
        ],
        initial='standard',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Card Size'
    )
    
    include_qr_code = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Include QR Code'
    )
    
    include_barcode = forms.BooleanField(
        initial=False,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Include Barcode'
    )
    
    include_logo = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Include Company Logo'
    )

    def __init__(self, *args, **kwargs):
        cards_queryset = kwargs.pop('cards_queryset', None)
        super().__init__(*args, **kwargs)
        
        if cards_queryset is not None:
            self.fields['cards'].queryset = cards_queryset 


# ============================================================================
# EMPLOYEE ID CARD FORMS
# ============================================================================

class EmployeeIDCardForm(forms.ModelForm):
    """Form for creating and updating Employee ID cards."""
    
    # Add a custom search field for employee autocomplete
    employee_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search for employee by name, ID, email...',
            'autocomplete': 'off'
        }),
        label='Search Employee'
    )
    
    # Add card_number field for manual assignment/editing
    card_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Will be auto-generated when status is Printed/Delivered/Active'
        }),
        label='Card Number',
        help_text='Auto-generated when status is Printed, Delivered, or Active. Can be manually assigned if needed.'
    )
    
    class Meta:
        model = EmployeeIDCard
        fields = [
            'employee', 'card_number', 'status', 'issue_date', 'expiry_date', 'notes'
        ]
        widgets = {
            'employee': forms.HiddenInput(),  # Hidden field to store the selected employee ID
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'expiry_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about the ID card...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        from hr.models import Employee
        # Remove the queryset limit since we're using autocomplete
        self.fields['employee'].queryset = Employee.objects.all()
        
        # Set default dates if creating new card
        if not self.instance.pk:
            self.fields['issue_date'].initial = date.today()
            self.fields['expiry_date'].initial = date.today() + timedelta(days=365)
        else:
            # If editing, populate the search field with the current employee's name
            # and set the employee field value
            if self.instance.employee:
                self.fields['employee_search'].initial = self.instance.employee.full_name
                self.fields['employee'].initial = self.instance.employee
        
        # Make employee field not required in form validation since we handle it in clean()
        self.fields['employee'].required = False
    
    def clean_employee(self):
        """Custom validation for employee field."""
        employee = self.cleaned_data.get('employee')
        
        # If editing an existing card and no employee is provided, use the current employee
        if not employee and self.instance.pk and self.instance.employee:
            employee = self.instance.employee
        
        if not employee:
            raise forms.ValidationError("Please select an employee from the search results.")
        
        # Check if employee already has an active ID card (when creating new card)
        if not self.instance.pk:  # Only check for new cards
            from .models import EmployeeIDCard
            existing_card = EmployeeIDCard.objects.filter(
                employee=employee,
                status__in=['pending', 'approved', 'printed', 'delivered', 'active']
            ).first()
            
            if existing_card:
                raise forms.ValidationError(
                    f"Employee {employee.full_name} already has an active ID card "
                    f"(Status: {existing_card.get_status_display()}). "
                    f"Please complete or cancel the existing card first."
                )
        
        return employee
    
    def clean_card_number(self):
        """Custom validation for card number field."""
        card_number = self.cleaned_data.get('card_number')
        
        if card_number:
            # Check if card number is unique (excluding current instance)
            from .models import EmployeeIDCard
            existing_card = EmployeeIDCard.objects.filter(card_number=card_number)
            if self.instance.pk:
                existing_card = existing_card.exclude(pk=self.instance.pk)
            
            if existing_card.exists():
                raise forms.ValidationError(f"Card number '{card_number}' is already in use.")
        
        return card_number


class EmployeeIDCardSearchForm(forms.Form):
    """Search form for Employee ID cards list."""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by employee name, ID, or card number...',
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    

    
    department = forms.ModelChoiceField(
        required=False,
        queryset=None,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    date_range = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Time'),
            ('today', 'Today'),
            ('week', 'Last 7 Days'),
            ('month', 'Last 30 Days'),
            ('year', 'Last Year'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Import here to avoid circular imports
        from .models import EmployeeIDCard
        from hr.models import Department
        
        # Set choices for status
        self.fields['status'].choices = [('', 'All Statuses')] + EmployeeIDCard.STATUS_CHOICES
        
        # Set queryset for department
        self.fields['department'].queryset = Department.objects.all()


class BatchEmployeeIDCardForm(forms.Form):
    """Form for batch creating Employee ID cards."""
    
    employees = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        label='Select Employees',
        help_text='Choose employees to create ID cards for'
    )
    

    
    status = forms.ChoiceField(
        choices=[],
        initial='pending',
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Initial Status'
    )
    
    issue_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Issue Date',
        help_text='Leave blank for cards in pending status'
    )
    
    expiry_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Expiry Date',
        initial=lambda: date.today() + timedelta(days=365)
    )
    
    copy_employee_photo = forms.BooleanField(
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Copy Employee Photos',
        help_text='Automatically copy employee photos to ID cards (recommended)'
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Notes for all cards...'
        }),
        label='Notes (applied to all cards)'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        from hr.models import Employee
        from .models import EmployeeIDCard
        from django.db.models import Q
        
        # Set choices for status
        self.fields['status'].choices = EmployeeIDCard.STATUS_CHOICES
        
        # Only show employees who don't have active ID cards
        self.fields['employees'].queryset = Employee.objects.select_related(
            'department', 'position'
        ).filter(
            Q(employee_id_cards__isnull=True) | 
            ~Q(employee_id_cards__status__in=['pending', 'approved', 'printed', 'delivered', 'active'])
        ).distinct().order_by('first_name', 'last_name')
        
        # Set default expiry date to one year from today
        self.fields['expiry_date'].initial = date.today() + timedelta(days=365)

    def clean(self):
        cleaned_data = super().clean()
        employees = cleaned_data.get('employees')
        
        if not employees:
            raise forms.ValidationError('Please select at least one employee.')
        
        # Check if any selected employees already have active cards
        from .models import EmployeeIDCard
        existing_cards = EmployeeIDCard.objects.filter(
            employee__in=employees,
            status__in=['pending', 'approved', 'printed', 'delivered', 'active']
        ).select_related('employee')
        
        if existing_cards.exists():
            existing_names = [card.employee.full_name for card in existing_cards]
            raise forms.ValidationError(
                f'The following employees already have active ID cards: {", ".join(existing_names)}'
            )
        
        return cleaned_data


class EmployeeSelectionForm(forms.Form):
    """Form for selecting employees for batch operations."""
    
    department = forms.ModelChoiceField(
        required=False,
        queryset=None,
        empty_label="All Departments",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Filter by Department'
    )
    
    position = forms.ModelChoiceField(
        required=False,
        queryset=None,
        empty_label="All Positions",
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Filter by Position'
    )
    
    employment_status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Employees')],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Employment Status'
    )
    
    has_photo = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Employees'),
            ('yes', 'With Photo Only'),
            ('no', 'Without Photo Only')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Photo Status'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        from hr.models import Department, Position, Employee
        
        # Set querysets
        self.fields['department'].queryset = Department.objects.all()
        self.fields['position'].queryset = Position.objects.select_related('department')
        
        # Set employment status choices
        self.fields['employment_status'].choices = [('', 'All Employees')] + Employee.EMPLOYMENT_STATUS_CHOICES 