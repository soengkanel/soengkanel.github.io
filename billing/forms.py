from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from datetime import timedelta
from .models import Invoice, InvoiceLineItem, Service, VisaServiceRecord, OfficialReceipt, CashChequeReceipt, PaymentVoucher, PaymentVoucherDocument
from zone.models import Worker

class ServiceForm(forms.ModelForm):
    """Form for creating and editing services"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make service_code required in the form
        self.fields['service_code'].required = True
    
    def clean_service_code(self):
        """Validate service code uniqueness and format"""
        service_code = self.cleaned_data.get('service_code')
        
        if not service_code:
            raise forms.ValidationError('Service code is required.')
        
        # Check uniqueness (excluding current instance if editing)
        existing_service = Service.objects.filter(service_code__iexact=service_code)
        if self.instance.pk:
            existing_service = existing_service.exclude(pk=self.instance.pk)
        
        if existing_service.exists():
            raise forms.ValidationError(f'Service code "{service_code}" already exists. Please use a different code.')
        
        # Format validation - uppercase and alphanumeric
        service_code = service_code.upper().strip()
        if not service_code.replace('_', '').replace('-', '').isalnum():
            raise forms.ValidationError('Service code can only contain letters, numbers, hyphens, and underscores.')
        
        return service_code
    
    class Meta:
        model = Service
        fields = ['service_code', 'name', 'category', 'description', 'default_price', 'is_active']
        widgets = {
            'service_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Service code (e.g., IDC001, DOC001)',
                'maxlength': '20'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Service name (e.g., ID Card Printing)'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Detailed description of the service...'
            }),
            'default_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InvoiceForm(forms.ModelForm):
    """Form for creating and editing invoices"""
    
    # Client selection fields
    client_type = forms.ChoiceField(
        choices=[
            ('', 'Select client type...'),
            ('worker', 'Worker'),
            ('batch_workers', 'Batch Workers'),
            ('vip', 'VIP'),
            ('other', 'Other'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_client_type'
        }),
        label='Client Type',
        required=True
    )
    
    # Hidden fields to store the selected IDs
    worker_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_worker_id'})
    )
    
    vip_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput(attrs={'id': 'id_vip_id'})
    )
    
    # Autocomplete text inputs for searching
    worker_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control autocomplete-input',
            'id': 'id_worker_search',
            'placeholder': 'Type worker name, ID, email, or phone...',
            'autocomplete': 'off'
        }),
        label='Search Worker'
    )
    
    vip_search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control autocomplete-input',
            'id': 'id_vip_search',
            'placeholder': 'Type VIP name, ID, email, or phone...',
            'autocomplete': 'off'
        }),
        label='Search VIP'
    )
    
    # Batch selection field
    batch_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control autocomplete-input',
            'id': 'id_batch_name',
            'placeholder': 'Type batch name to search...',
            'autocomplete': 'off'
        }),
        label='Search Worker Batch'
    )
    
    
    class Meta:
        model = Invoice
        fields = ['status', 'issue_date', 'due_date', 'tax_percentage', 'client_name', 'notes', 
                  'reference_document', 'reference_document_2', 'reference_document_3']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'issue_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'form-control', 
                'type': 'date'
            }),
            'tax_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '0',
                'max': '100',
                'placeholder': '10'
            }),
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter client name...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this invoice...'
            }),
            'reference_document': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'reference_document_2': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
            'reference_document_3': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default due date to 30 days from now
        if not self.instance.pk:
            self.fields['due_date'].initial = timezone.now().date() + timedelta(days=30)
            self.fields['tax_percentage'].initial = 0
        
        # If editing an existing invoice, set the client type and selection
        if self.instance.pk:
            if self.instance.worker:
                self.fields['client_type'].initial = 'worker'
                self.fields['worker_id'].initial = self.instance.worker.id
                self.fields['worker_search'].initial = f"{self.instance.worker.get_full_name()}"
                if self.instance.worker.worker_id:
                    self.fields['worker_search'].initial += f" (ID: {self.instance.worker.worker_id})"
            elif hasattr(self.instance, 'vip') and self.instance.vip:
                self.fields['client_type'].initial = 'vip'
                self.fields['vip_id'].initial = self.instance.vip.id
                self.fields['vip_search'].initial = f"{self.instance.vip.get_full_name()}"
                if hasattr(self.instance.vip, 'member_id') and self.instance.vip.member_id:
                    self.fields['vip_search'].initial += f" (ID: {self.instance.vip.member_id})"
            else:
                self.fields['client_type'].initial = 'other'
    
    def clean(self):
        cleaned_data = super().clean()
        client_type = cleaned_data.get('client_type')
        worker_id = cleaned_data.get('worker_id')
        vip_id = cleaned_data.get('vip_id')
        client_name = cleaned_data.get('client_name')
        batch_name = cleaned_data.get('batch_name')
        
        # Validate client selection based on type
        if client_type == 'worker':
            if not worker_id:
                raise forms.ValidationError('Please select a worker.')
            # Verify worker exists (any status)
            try:
                worker = Worker.objects.get(id=worker_id)
                cleaned_data['selected_worker'] = worker
            except Worker.DoesNotExist:
                raise forms.ValidationError('Selected worker is not valid.')
                
        elif client_type == 'batch_workers':
            if not batch_name:
                raise forms.ValidationError('Please select a worker batch.')
            cleaned_data['selected_batch'] = batch_name
                
        elif client_type == 'vip':
            if not vip_id:
                raise forms.ValidationError('Please select a VIP.')
            # Verify VIP exists and is active
            try:
                from vip.models import Vip
                vip = Vip.objects.get(id=vip_id, status='active')
                cleaned_data['selected_vip'] = vip
            except Vip.DoesNotExist:
                raise forms.ValidationError('Selected VIP is not valid or not active.')
                
        elif client_type == 'other' and not client_name:
            raise forms.ValidationError('Please enter a client name.')
        
        return cleaned_data
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Set the appropriate client based on selection
        client_type = self.cleaned_data.get('client_type')
        if client_type == 'worker':
            instance.worker = self.cleaned_data.get('selected_worker')
            if hasattr(instance, 'vip'):
                instance.vip = None
        elif client_type == 'batch_workers':
            # Store batch name in client_name field for now
            batch_name = self.cleaned_data.get('selected_batch')
            instance.client_name = f"Batch: {batch_name}"
            instance.worker = None
            if hasattr(instance, 'vip'):
                instance.vip = None
            instance.client_name = ''
        elif client_type == 'vip':
            instance.worker = None
            if hasattr(instance, 'vip'):
                instance.vip = self.cleaned_data.get('selected_vip')
            instance.client_name = ''
        else:  # other
            instance.worker = None
            if hasattr(instance, 'vip'):
                instance.vip = None
            # client_name is already set from the form
        
        if commit:
            instance.save()
        return instance


class InvoiceLineItemForm(forms.ModelForm):
    """Form for invoice line items"""
    
    class Meta:
        model = InvoiceLineItem
        fields = ['service', 'description', 'quantity', 'unit_price', 'notes']
        widgets = {
            'service': forms.Select(attrs={
                'class': 'form-select service-select',
                'data-placeholder': 'Select a service...'
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Service description'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '1',
                'min': '1',
                'value': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'notes': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional notes'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active services
        self.fields['service'].queryset = Service.objects.filter(is_active=True)
        # Add empty choice for service selection
        self.fields['service'].empty_label = 'Select a service...'
        # Set default quantity
        if not self.instance.pk:
            self.fields['quantity'].initial = 1


# Create the inline formset for line items
InvoiceLineItemFormSet = inlineformset_factory(
    Invoice, 
    InvoiceLineItem,
    form=InvoiceLineItemForm,
    extra=1,  # Start with 1 empty form
    min_num=1,  # Require at least 1 line item
    validate_min=True,
    can_delete=True
)


class InvoiceSearchForm(forms.Form):
    """Form for searching and filtering invoices"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Search by invoice number, client name...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + Invoice.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    client_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Clients'),
            ('worker', 'Workers'),
            ('other', 'Other Clients'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-sm',
            'type': 'date'
        }),
        label='From Date'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-sm',
            'type': 'date'
        }),
        label='To Date'
    )


class ServiceSearchForm(forms.Form):
    """Form for searching and filtering services"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm',
            'placeholder': 'Search by name or description...'
        })
    )
    
    category = forms.ChoiceField(
        required=False,
        choices=[('', 'All Categories')] + Service.CATEGORY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
    
    is_active = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Services'),
            ('true', 'Active Only'),
            ('false', 'Inactive Only'),
        ],
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )


class VisaServiceRecordForm(forms.ModelForm):
    """Form for creating and editing visa service records"""
    
    class Meta:
        model = VisaServiceRecord
        fields = [
            'worker', 'client_name', 'service', 'duration_months',
            'amount', 'start_date', 'status', 'notes'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter services to only visa services
        self.fields['service'].queryset = Service.objects.filter(
            category='visas', is_active=True
        ).order_by('name')
        
        # Add CSS classes
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'
        
        # Make worker field optional since we can have other clients
        self.fields['worker'].required = False
        self.fields['client_name'].required = False
        
        # Add placeholders
        self.fields['client_name'].widget.attrs['placeholder'] = 'Enter client name if not selecting worker'


class OfficialReceiptForm(forms.ModelForm):
    """Form for creating and editing official receipts"""
    
    class Meta:
        model = OfficialReceipt
        fields = [
            'invoice', 'receipt_type', 'employee_number', 'employee_name', 
            'total_pass', 'total_amount', 'service_fee_5', 'quota_fee_25', 
            'support_document_amount', 'year', 'issue_date', 'notes'
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'total_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'service_fee_5': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'quota_fee_25': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'support_document_amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter invoices to pending only
        self.fields['invoice'].queryset = Invoice.objects.filter(status='pending').order_by('-issue_date')
        self.fields['invoice'].required = False
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'


class CashChequeReceiptForm(forms.ModelForm):
    """Form for creating and editing cash/cheque receipts"""
    
    class Meta:
        model = CashChequeReceipt
        fields = [
            'invoice', 'date', 'received_from', 'payment_method', 
            'amount_usd', 'amount_in_words', 'payment_purpose', 'reference_number'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'payment_purpose': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'amount_usd': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Check #, Transaction ID, etc.'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter invoices to pending only
        self.fields['invoice'].queryset = Invoice.objects.filter(status='pending').order_by('-issue_date')
        self.fields['invoice'].required = False
        
        # Add CSS classes to all fields
        for field_name, field in self.fields.items():
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'


class PaymentVoucherForm(forms.ModelForm):
    """Form for creating and editing payment vouchers"""
    
    class Meta:
        model = PaymentVoucher
        fields = [
            'payee', 'amount_usd', 'date', 'payment_purpose', 'expense_category', 'payment_method',
            'invoice', 'payee_contact', 'budget_code', 'payment_reference', 'notes'
        ]
        widgets = {
            'payee': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company or person name'
            }),
            'amount_usd': forms.NumberInput(attrs={
                'step': '0.01', 
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'value': timezone.now().date().strftime('%Y-%m-%d')
            }),
            'payment_purpose': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'form-control',
                'placeholder': 'What is this payment for? (e.g., Office supplies for Q4, Professional consulting services...)'
            }),
            'expense_category': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
            'invoice': forms.Select(attrs={'class': 'form-select'}),
            'payee_contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone or email'
            }),
            'budget_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Department or project code'
            }),
            'payment_reference': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Check number, transaction ID, etc.'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Any additional notes or special instructions...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filter invoices to pending only
        self.fields['invoice'].queryset = Invoice.objects.filter(status='pending').order_by('-issue_date')
        self.fields['invoice'].required = False
        self.fields['invoice'].empty_label = "-- Select invoice (optional) --"
        
        # Make optional fields not required
        optional_fields = ['invoice', 'payee_contact', 'budget_code', 'payment_reference', 'notes']
        for field in optional_fields:
            if field in self.fields:
                self.fields[field].required = False
        
        # Set default values for new vouchers
        if not self.instance.pk:
            self.fields['expense_category'].initial = 'other'
            self.fields['payment_method'].initial = 'bank_transfer'


class PaymentVoucherDocumentForm(forms.ModelForm):
    """Form for uploading reference documents for payment vouchers"""
    
    class Meta:
        model = PaymentVoucherDocument
        fields = [
            'document_type', 'document_name', 'document_file', 'document_number', 
            'document_date', 'document_amount', 'notes'
        ]
        widgets = {
            'document_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'document_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter document name or description'
            }),
            'document_file': forms.ClearableFileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.xls,.xlsx'
            }),
            'document_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Document/Invoice number (optional)'
            }),
            'document_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'document_amount': forms.NumberInput(attrs={
                'step': '0.01',
                'class': 'form-control',
                'placeholder': '0.00'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Additional notes about this document...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make most fields optional
        optional_fields = ['document_number', 'document_date', 'document_amount', 'notes']
        for field in optional_fields:
            if field in self.fields:
                self.fields[field].required = False
    
    def clean_document_file(self):
        """Validate uploaded file"""
        document_file = self.cleaned_data.get('document_file')
        
        if document_file:
            # Check file size (max 10MB)
            if document_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 10MB.')
            
            # Check file type
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.gif', '.xls', '.xlsx', '.txt']
            import os
            ext = os.path.splitext(document_file.name)[1].lower()
            if ext not in allowed_extensions:
                raise forms.ValidationError(
                    f'File type not allowed. Allowed types: {", ".join(allowed_extensions)}'
                )
        
        return document_file


# Create a formset for managing multiple documents
PaymentVoucherDocumentFormSet = inlineformset_factory(
    PaymentVoucher, PaymentVoucherDocument, 
    form=PaymentVoucherDocumentForm,
    extra=1,  # Show 1 empty form by default
    can_delete=True,
    min_num=0,  # No minimum required documents
    validate_min=True
)