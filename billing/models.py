from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
import uuid
import os
from dateutil.relativedelta import relativedelta

# Import related models
# from document_tracking.models import DocumentSubmission
from zone.models import Worker
from core.encrypted_fields import FileEncryptionMixin


class Service(models.Model):
    """Predefined services/items for invoicing"""
    
    CATEGORY_CHOICES = [
        ('id_cards', 'ID Cards'),
        ('documents', 'Document Processing'),
        ('permits', 'Permits & Licenses'),
        ('visas', 'Visa Services'),
        ('other', 'Other Services'),
    ]
    
    # Service details
    service_code = models.CharField(max_length=20, unique=True, blank=True, null=True, help_text="e.g., IDC001, DOC001")
    name = models.CharField(max_length=200, help_text="e.g., Print ID Card for Worker")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    description = models.TextField(blank=True, help_text="Detailed service description")
    default_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Standard price for this service")
    
    # Service settings
    is_active = models.BooleanField(default=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.service_code} - {self.name} - ${self.default_price}"

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['category', 'name']
    
    def save(self, *args, **kwargs):
        # Track changes for history
        is_new = self.pk is None
        old_instance = None
        
        if not is_new:
            try:
                old_instance = Service.objects.get(pk=self.pk)
            except Service.DoesNotExist:
                old_instance = None
        
        # Get the user from kwargs if provided (we'll pass it from views)
        user = kwargs.pop('user', None)
        
        super().save(*args, **kwargs)
        
        # Create history records
        if is_new:
            # Record creation
            ServiceHistory.objects.create(
                service=self,
                action='created',
                field_name='all',
                old_value='',
                new_value=f'Service created: {self.name} - ${self.default_price}',
                changed_by=user,
                notes=f'New service created with code: {self.service_code}'
            )
        else:
            # Track specific field changes
            if old_instance:
                changes = []
                
                if old_instance.default_price != self.default_price:
                    ServiceHistory.objects.create(
                        service=self,
                        action='price_changed',
                        field_name='default_price',
                        old_value=str(old_instance.default_price),
                        new_value=str(self.default_price),
                        changed_by=user,
                        notes=f'Price changed from ${old_instance.default_price} to ${self.default_price}'
                    )
                    changes.append(f'price: ${old_instance.default_price} → ${self.default_price}')
                
                if old_instance.name != self.name:
                    ServiceHistory.objects.create(
                        service=self,
                        action='name_changed',
                        field_name='name',
                        old_value=old_instance.name,
                        new_value=self.name,
                        changed_by=user,
                        notes=f'Name changed from "{old_instance.name}" to "{self.name}"'
                    )
                    changes.append(f'name: "{old_instance.name}" → "{self.name}"')
                
                if old_instance.description != self.description:
                    ServiceHistory.objects.create(
                        service=self,
                        action='description_changed',
                        field_name='description',
                        old_value=old_instance.description,
                        new_value=self.description,
                        changed_by=user,
                        notes='Service description updated'
                    )
                    changes.append('description updated')
                
                if old_instance.category != self.category:
                    old_category = dict(self.CATEGORY_CHOICES).get(old_instance.category, old_instance.category)
                    new_category = dict(self.CATEGORY_CHOICES).get(self.category, self.category)
                    ServiceHistory.objects.create(
                        service=self,
                        action='category_changed',
                        field_name='category',
                        old_value=old_category,
                        new_value=new_category,
                        changed_by=user,
                        notes=f'Category changed from "{old_category}" to "{new_category}"'
                    )
                    changes.append(f'category: "{old_category}" → "{new_category}"')
                
                if old_instance.service_code != self.service_code:
                    ServiceHistory.objects.create(
                        service=self,
                        action='code_changed',
                        field_name='service_code',
                        old_value=old_instance.service_code or '',
                        new_value=self.service_code or '',
                        changed_by=user,
                        notes=f'Service code changed from "{old_instance.service_code}" to "{self.service_code}"'
                    )
                    changes.append(f'code: "{old_instance.service_code}" → "{self.service_code}"')
                
                if old_instance.is_active != self.is_active:
                    status_old = 'Active' if old_instance.is_active else 'Inactive'
                    status_new = 'Active' if self.is_active else 'Inactive'
                    ServiceHistory.objects.create(
                        service=self,
                        action='status_changed',
                        field_name='is_active',
                        old_value=status_old,
                        new_value=status_new,
                        changed_by=user,
                        notes=f'Status changed from "{status_old}" to "{status_new}"'
                    )
                    changes.append(f'status: {status_old} → {status_new}')
    
    @property
    def change_history(self):
        """Get the change history for this service"""
        return self.history.all().order_by('-changed_at')
    
    def is_price_used_in_calculations(self):
        """Check if the service price is being used in any calculations/transactions"""
        usage_info = {
            'is_used': False,
            'usage_details': [],
            'total_references': 0
        }
        
        # Check InvoiceLineItems
        line_items = self.invoicelineitem_set.filter(unit_price=self.default_price)
        if line_items.exists():
            usage_info['is_used'] = True
            usage_info['usage_details'].append({
                'type': 'Invoice Line Items',
                'count': line_items.count(),
                'examples': [f"Invoice #{item.invoice.invoice_number}" for item in line_items[:3]],
                'model': 'invoices'
            })
            usage_info['total_references'] += line_items.count()
        
        # Check VisaServiceRecords
        try:
            visa_services = self.visaservicerecord_set.filter(amount=self.default_price)
            if visa_services.exists():
                usage_info['is_used'] = True
                usage_info['usage_details'].append({
                    'type': 'Visa Service Records',
                    'count': visa_services.count(),
                    'examples': [f"{vs.get_client_name()} - {vs.get_duration_months_display()}" for vs in visa_services[:3]],
                    'model': 'visa_services'
                })
                usage_info['total_references'] += visa_services.count()
        except:
            pass  # VisaServiceRecord might not exist
        
        # Check ExtensionRequests (from eform app)
        try:
            from eform.models import ExtensionRequest
            extension_requests = self.extensionrequest_set.filter(service_fee=self.default_price)
            if extension_requests.exists():
                usage_info['is_used'] = True
                usage_info['usage_details'].append({
                    'type': 'Extension Requests',
                    'count': extension_requests.count(),
                    'examples': [f"#{ext.request_number} - {ext.worker.get_full_name()}" for ext in extension_requests[:3]],
                    'model': 'extension_requests'
                })
                usage_info['total_references'] += extension_requests.count()
        except ImportError:
            pass  # eform app not available
        
        return usage_info
    
    def can_change_price(self, new_price=None):
        """Check if the service price can be changed"""
        if new_price is None or new_price == self.default_price:
            return True, "No price change"
        
        usage_info = self.is_price_used_in_calculations()
        if usage_info['is_used']:
            return False, f"Price cannot be changed because this service is currently used in {usage_info['total_references']} transaction(s)"
        
        return True, "Price can be changed"
    
    def suggest_new_service_code(self):
        """Suggest a new service code for creating a new version of this service"""
        base_code = self.service_code or self.name[:6].upper().replace(' ', '')
        
        # Find existing codes with similar pattern
        existing_codes = Service.objects.filter(
            service_code__startswith=base_code
        ).values_list('service_code', flat=True)
        
        # Try with version numbers
        for version in range(1, 100):
            new_code = f"{base_code}V{version}"
            if new_code not in existing_codes:
                return new_code
        
        # Fallback with timestamp
        import time
        return f"{base_code}{int(time.time()) % 10000}"


class Invoice(models.Model):
    """Enhanced Invoice model with maker-checker workflow for financial control"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Invoice identification
    invoice_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Client information - simplified
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True, related_name='invoices')
    client_name = models.CharField(max_length=200, blank=True, help_text="For other clients")
    
    # Invoice details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Calculated from line items")
    tax_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Tax percentage (e.g., 10 for 10%)")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Calculated from subtotal × tax_percentage")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Subtotal + tax")
    
    # Important dates
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    
    # Optional references
    # document_submission = models.ForeignKey(DocumentSubmission, on_delete=models.SET_NULL, null=True, blank=True, help_text="Related document submission")
    
    # Additional information
    notes = models.TextField(blank=True)
    
    # Document attachments
    reference_document = models.FileField(
        upload_to='invoice_documents/%Y/%m/', 
        blank=True, 
        null=True,
        help_text="Upload supporting document (PDF, DOC, DOCX, JPG, PNG)"
    )
    reference_document_2 = models.FileField(
        upload_to='invoice_documents/%Y/%m/', 
        blank=True, 
        null=True,
        help_text="Additional supporting document"
    )
    reference_document_3 = models.FileField(
        upload_to='invoice_documents/%Y/%m/', 
        blank=True, 
        null=True,
        help_text="Additional supporting document"
    )
    
    # Maker-Checker Workflow Fields
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='submitted_invoices', help_text="User who submitted for approval")
    submitted_at = models.DateTimeField(null=True, blank=True, help_text="When submitted for approval")
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_invoices', help_text="User who approved this invoice")
    approved_at = models.DateTimeField(null=True, blank=True, help_text="When approved")
    
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='rejected_invoices', help_text="User who rejected this invoice")
    rejected_at = models.DateTimeField(null=True, blank=True, help_text="When rejected")
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='created_invoices')

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.get_client_name()} - ${self.total_amount}"

    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-issue_date', '-created_at']

    def save(self, *args, **kwargs):
        # Auto-generate invoice number
        if not self.invoice_number:
            prefix = "INV"
            self.invoice_number = f"{prefix}{timezone.now().year}{str(uuid.uuid4().hex[:6]).upper()}"
        
        # Calculate totals if instance exists (has line items)
        if self.pk:
            self.calculate_totals()
        
        super().save(*args, **kwargs)

    def calculate_totals(self):
        """Calculate invoice totals from line items"""
        line_items = self.line_items.all()
        self.subtotal = sum(item.total_amount for item in line_items)
        # Calculate tax amount from percentage
        self.tax_amount = (self.subtotal * self.tax_percentage) / 100
        self.total_amount = self.subtotal + self.tax_amount

    def get_client_name(self):
        """Get the client name"""
        if self.worker:
            return self.worker.get_full_name()
        elif self.client_name:
            return self.client_name
        return "Unknown Client"

    @property
    def is_overdue(self):
        if self.status == 'pending' and self.due_date:
            return timezone.now().date() > self.due_date
        return False

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0

    @property
    def total_paid(self):
        """Calculate total amount paid for this invoice through receipts"""
        # Calculate from related receipts
        official_receipts_total = sum(receipt.total_amount for receipt in self.official_receipts.all())
        cash_receipts_total = sum(receipt.amount_usd for receipt in self.cash_receipts.all())
        return official_receipts_total + cash_receipts_total

    @property
    def balance_due(self):
        """Calculate remaining balance due"""
        return self.total_amount - self.total_paid
    
    @property 
    def has_receipts(self):
        """Check if invoice has any receipts"""
        return self.official_receipts.exists() or self.cash_receipts.exists()
    
    @property
    def has_payment_vouchers(self):
        """Check if invoice has any payment vouchers"""
        return self.payment_vouchers.exists()
    
    @property
    def workflow_status(self):
        """Get the current workflow status for invoice collection"""
        if self.status == 'paid':
            return 'completed'
        elif self.has_receipts:
            return 'receipt_issued'  # Payment received and documented
        elif self.status == 'pending':
            return 'pending_payment'  # Awaiting client payment
        else:
            return 'draft'  # Invoice not yet finalized
    
    # Maker-Checker Workflow Methods
    def can_submit_for_approval(self, user=None):
        """Check if invoice can be submitted for approval"""
        return self.status == 'draft'
    
    def can_approve(self, user=None):
        """Check if invoice can be approved"""
        if self.status != 'pending_approval':
            return False
        
        if not user:
            return False
            
        # Get user's role
        user_role = self._get_user_role(user)
        
        # Manager can approve any invoice (including their own)
        if user_role == 'manager':
            return True
            
        # Regular user cannot approve invoices
        return False
    
    def can_reject(self, user=None):
        """Check if invoice can be rejected"""
        if self.status != 'pending_approval':
            return False
        
        if not user:
            return False
            
        # Get user's role
        user_role = self._get_user_role(user)
        
        # Manager can reject any invoice (including their own)
        if user_role == 'manager':
            return True
            
        # Regular user cannot reject invoices
        return False
    
    def _get_user_role(self, user):
        """Get user's role name from UserRoleAssignment"""
        try:
            from user_management.models import UserRoleAssignment
            role_assignment = UserRoleAssignment.objects.select_related('role').filter(user=user, is_active=True).first()
            if role_assignment and role_assignment.role:
                return role_assignment.role.name.lower()
        except:
            pass
        return 'user'  # Default to regular user if no role found
    
    @property
    def can_edit(self):
        """Check if invoice can be edited"""
        return self.status in ['draft', 'rejected']
    
    @property
    def is_workflow_completed(self):
        """Check if workflow is completed (paid or cancelled)"""
        return self.status in ['paid', 'cancelled']
    
    def submit_for_approval(self, user):
        """Submit invoice for approval"""
        if not self.can_submit_for_approval():
            raise ValueError(f"Cannot submit invoice with status {self.status}")
        
        self.status = 'pending_approval'
        self.submitted_by = user
        self.submitted_at = timezone.now()
        self.save()
    
    def approve_invoice(self, user):
        """Approve the invoice"""
        if not self.can_approve(user):
            raise ValueError(f"Cannot approve invoice with status {self.status}")
        
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        # Clear any rejection data
        self.rejected_by = None
        self.rejected_at = None
        self.rejection_reason = ''
        self.save()
    
    def reject_invoice(self, user, reason=''):
        """Reject the invoice"""
        if not self.can_reject(user):
            raise ValueError(f"Cannot reject invoice with status {self.status}")
        
        self.status = 'rejected'
        self.rejected_by = user
        self.rejected_at = timezone.now()
        self.rejection_reason = reason
        # Clear approval data
        self.approved_by = None
        self.approved_at = None
        self.save()
    
    def send_to_client(self, user):
        """Send approved invoice to client for payment"""
        if self.status != 'approved':
            raise ValueError(f"Cannot send invoice with status {self.status} to client")
        
        self.status = 'pending'
        self.save()
    
    def cancel_invoice(self, user):
        """Cancel the invoice"""
        if self.status == 'paid':
            raise ValueError("Cannot cancel a paid invoice")
        
        self.status = 'cancelled'
        self.save()
    
    @property
    def workflow_history(self):
        """Get workflow history as a list of events"""
        history = []
        
        if self.created_at and self.created_by:
            history.append({
                'action': 'Created',
                'user': self.created_by,
                'timestamp': self.created_at,
                'status': 'draft'
            })
        
        if self.submitted_at and self.submitted_by:
            history.append({
                'action': 'Submitted for Approval',
                'user': self.submitted_by,
                'timestamp': self.submitted_at,
                'status': 'pending_approval'
            })
        
        if self.approved_at and self.approved_by:
            history.append({
                'action': 'Approved',
                'user': self.approved_by,
                'timestamp': self.approved_at,
                'status': 'approved'
            })
        
        if self.rejected_at and self.rejected_by:
            history.append({
                'action': 'Rejected',
                'user': self.rejected_by,
                'timestamp': self.rejected_at,
                'status': 'rejected',
                'reason': self.rejection_reason
            })
        
        # Sort by timestamp
        history.sort(key=lambda x: x['timestamp'])
        return history


class InvoiceLineItem(models.Model):
    """Invoice line items for itemized billing"""
    
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='line_items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True, help_text="Select the service/item")
    description = models.CharField(max_length=300, help_text="Service description")
    
    # Line item details
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1, validators=[MinValueValidator(0)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], help_text="Price per unit")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    
    # Optional customization
    notes = models.CharField(max_length=300, blank=True, help_text="Additional notes for this line item")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        service_name = self.service.name if self.service else self.description
        return f"{self.invoice.invoice_number} - {service_name}"

    class Meta:
        verbose_name = "Invoice Line Item"
        verbose_name_plural = "Invoice Line Items"
        ordering = ['invoice', 'id']

    def save(self, *args, **kwargs):
        # Auto-populate description and unit_price from service if service is selected
        if self.service:
            if not self.description:
                self.description = self.service.name
            if not self.unit_price:
                self.unit_price = self.service.default_price
        
        # Auto-calculate total amount
        self.total_amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # Update invoice totals
        if self.invoice_id:
            self.invoice.calculate_totals()
            self.invoice.save()


class OfficialReceipt(models.Model):
    """Official Receipt model matching Cambodian government format"""
    
    RECEIPT_TYPE_CHOICES = [
        ('tax_payment', 'Tax Payment to Department of Labour and Vocational Training'),
        ('service_fee', 'Service Fee Receipt'),
        ('quota_payment', 'Quota Payment Receipt'),
        ('general', 'General Official Receipt'),
    ]
    
    # Receipt identification
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    receipt_type = models.CharField(max_length=20, choices=RECEIPT_TYPE_CHOICES, default='general')
    
    # Billing flow connections
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='official_receipts', help_text="Related invoice for this receipt")
    
    # Client information
    employee_number = models.CharField(max_length=50, blank=True, help_text="Employee No. (e.g., NO.065)")
    employee_name = models.CharField(max_length=200, help_text="Employee name (e.g., KHEANG)")
    total_pass = models.IntegerField(default=0, help_text="Number of passes/permits")
    
    # Payment details
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Total amount")
    service_fee_5 = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Income Service from Service (5$/p)")
    quota_fee_25 = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Income Service from Quota (25$/p)")
    support_document_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Available for used to support document out side")
    
    # Government tax information
    year = models.IntegerField(default=timezone.now().year, help_text="Tax payment year")
    
    # Dates
    issue_date = models.DateField(default=timezone.now)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.employee_name} - ${self.total_amount}"

    class Meta:
        verbose_name = "Official Receipt"
        verbose_name_plural = "Official Receipts"
        ordering = ['-issue_date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate unique receipt number with format OR-YYYYNNN
            year = timezone.now().year
            # Get the latest receipt number for this year
            latest_receipt = OfficialReceipt.objects.filter(
                receipt_number__startswith=f'OR-{year}'
            ).order_by('-receipt_number').first()
            
            if latest_receipt:
                # Extract the sequence number and increment
                try:
                    last_seq = int(latest_receipt.receipt_number.split('-')[-1])
                    next_seq = last_seq + 1
                except (ValueError, IndexError):
                    next_seq = 1
            else:
                next_seq = 1
            
            self.receipt_number = f"OR-{year}-{next_seq:03d}"
        super().save(*args, **kwargs)

    @property
    def total_paid_amount(self):
        """Calculate total paid amount"""
        return abs(self.service_fee_5 + self.quota_fee_25 - abs(self.support_document_amount))


class CashChequeReceipt(models.Model):
    """Cash/Cheque Receipt model matching Cambodian format"""
    
    # Receipt identification
    receipt_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Billing flow connections
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='cash_receipts', help_text="Related invoice for this receipt")
    
    # Receipt details
    date = models.DateField(default=timezone.now)
    received_from = models.CharField(max_length=200, help_text="Name of person or organization making payment")
    payment_method = models.CharField(max_length=50, choices=[
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('other', 'Other')
    ], default='cash', help_text="Method of payment")
    
    # Amount details
    amount_in_words = models.CharField(max_length=300, blank=True, help_text="Amount written in words")
    amount_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Amount in USD")
    
    # Purpose and reference
    payment_purpose = models.TextField(help_text="Purpose or description of payment")
    reference_number = models.CharField(max_length=100, blank=True, help_text="Check number, transaction ID, or other reference")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Cash Receipt {self.receipt_number} - {self.received_from} - ${self.amount_usd}"

    class Meta:
        verbose_name = "Cash/Cheque Receipt"
        verbose_name_plural = "Cash/Cheque Receipts"
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate unique receipt number with format CR-YYYYNNN
            year = timezone.now().year
            # Get the latest receipt number for this year
            latest_receipt = CashChequeReceipt.objects.filter(
                receipt_number__startswith=f'CR-{year}'
            ).order_by('-receipt_number').first()
            
            if latest_receipt:
                # Extract the sequence number and increment
                try:
                    last_seq = int(latest_receipt.receipt_number.split('-')[-1])
                    next_seq = last_seq + 1
                except (ValueError, IndexError):
                    next_seq = 1
            else:
                next_seq = 1
            
            self.receipt_number = f"CR-{year}-{next_seq:03d}"
        super().save(*args, **kwargs)


class PaymentVoucher(models.Model):
    """Payment Voucher model - Enhanced for business expense management with maker-checker workflow"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_approval', 'Pending Approval'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    EXPENSE_CATEGORY_CHOICES = [
        ('office_supplies', 'Office Supplies'),
        ('utilities', 'Utilities & Services'),
        ('permits_licenses', 'Permits & Licenses'),
        ('professional_services', 'Professional Services'),
        ('travel_transport', 'Travel & Transportation'),
        ('maintenance_repairs', 'Maintenance & Repairs'),
        ('marketing', 'Marketing & Advertising'),
        ('employee_benefits', 'Employee Benefits'),
        ('training_development', 'Training & Development'),
        ('insurance', 'Insurance'),
        ('rent_lease', 'Rent & Lease'),
        ('equipment', 'Equipment & Technology'),
        ('workpermit', 'Work Permit & Visa Services'),
        ('government_fees', 'Government Fees & Taxes'),
        ('other', 'Other Expenses'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('credit_card', 'Credit Card'),
        ('petty_cash', 'Petty Cash'),
        ('other', 'Other'),
    ]
    
    # Voucher identification
    voucher_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Workflow status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', 
                             help_text="Current workflow status")
    
    # Billing flow connections
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='payment_vouchers', help_text="Related invoice for this payment")
    
    # Voucher details
    date = models.DateField(default=timezone.now, help_text="Payment date")
    payee = models.CharField(max_length=200, help_text="Name of person/organization to be paid")
    payee_contact = models.CharField(max_length=100, blank=True, help_text="Phone or email contact")
    
    # Enhanced categorization
    expense_category = models.CharField(max_length=30, choices=EXPENSE_CATEGORY_CHOICES, default='other',
                                      help_text="Category of expense for accounting purposes")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='bank_transfer',
                                    help_text="Method of payment")
    
    # Amount details
    amount_in_words = models.CharField(max_length=300, blank=True, help_text="Amount written in words")
    amount_usd = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Payment amount")
    currency = models.CharField(max_length=3, default='USD', help_text="Currency code (USD, KHR, etc.)")
    
    # Purpose and documentation
    payment_purpose = models.TextField(help_text="Detailed description of what this payment is for")
    supporting_documents = models.TextField(blank=True, help_text="List of supporting documents")
    budget_code = models.CharField(max_length=50, blank=True, help_text="Budget or cost center reference")
    
    # Payment tracking
    payment_reference = models.CharField(max_length=100, blank=True, help_text="Bank reference, check number, etc.")
    
    # Authorization fields (simplified but professional)
    prepared_by = models.CharField(max_length=200, blank=True, help_text="Person who prepared this voucher")
    authorised_by = models.CharField(max_length=200, blank=True, help_text="Person who authorized this payment")
    received_by = models.CharField(max_length=200, blank=True, help_text="Person who received the payment")
    received_date = models.DateField(blank=True, null=True, help_text="Date payment was received")
    
    # Additional notes
    notes = models.TextField(blank=True, help_text="Additional notes or special instructions")
    
    # Maker-Checker Workflow Fields
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                    related_name='submitted_vouchers', help_text="User who submitted for approval")
    submitted_at = models.DateTimeField(null=True, blank=True, help_text="When submitted for approval")
    
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_vouchers', help_text="User who approved this voucher")
    approved_at = models.DateTimeField(null=True, blank=True, help_text="When approved")
    
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='rejected_vouchers', help_text="User who rejected this voucher")
    rejected_at = models.DateTimeField(null=True, blank=True, help_text="When rejected")
    rejection_reason = models.TextField(blank=True, help_text="Reason for rejection")
    
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='paid_vouchers', help_text="User who marked as paid")
    paid_at = models.DateTimeField(null=True, blank=True, help_text="When marked as paid")
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='created_vouchers')

    def __str__(self):
        return f"Payment Voucher {self.voucher_number} - {self.payee} - ${self.amount_usd}"

    class Meta:
        verbose_name = "Payment Voucher"
        verbose_name_plural = "Payment Vouchers"
        ordering = ['-date', '-created_at']

    def save(self, *args, **kwargs):
        # Auto-generate voucher number
        if not self.voucher_number:
            year = timezone.now().year
            try:
                latest_voucher = PaymentVoucher.objects.filter(
                    voucher_number__startswith=f'PV-{year}'
                ).order_by('-voucher_number').first()
                
                if latest_voucher:
                    try:
                        last_seq = int(latest_voucher.voucher_number.split('-')[-1])
                        next_seq = last_seq + 1
                    except (ValueError, IndexError):
                        next_seq = 1
                else:
                    next_seq = 1
            except:
                # If table doesn't exist yet, start with 1
                next_seq = 1
            
            self.voucher_number = f"PV-{year}-{next_seq:03d}"
        
        super().save(*args, **kwargs)

    @property
    def expense_category_display(self):
        """Get a user-friendly category display"""
        return dict(self.EXPENSE_CATEGORY_CHOICES).get(self.expense_category, self.expense_category)
    
    @property
    def payment_method_display(self):
        """Get a user-friendly payment method display"""
        return dict(self.PAYMENT_METHOD_CHOICES).get(self.payment_method, self.payment_method)
    
    def can_submit_for_approval(self, user=None):
        """Check if voucher can be submitted for approval"""
        return self.status == 'draft'
    
    def can_approve(self, user=None):
        """Check if voucher can be approved"""
        if self.status != 'pending_approval':
            return False
        
        if not user:
            return False
            
        # Get user's role
        user_role = self._get_user_role(user)
        
        # Manager can approve any voucher (except their own)
        if user_role == 'manager':
            return self.created_by != user
            
        # Regular user cannot approve vouchers
        return False
    
    def can_reject(self, user=None):
        """Check if voucher can be rejected"""
        if self.status != 'pending_approval':
            return False
        
        if not user:
            return False
            
        # Get user's role
        user_role = self._get_user_role(user)
        
        # Manager can reject any voucher (except their own)
        if user_role == 'manager':
            return self.created_by != user
            
        # Regular user cannot reject vouchers
        return False
    
    def _get_user_role(self, user):
        """Get user's role name from UserRoleAssignment"""
        try:
            from user_management.models import UserRoleAssignment
            role_assignment = UserRoleAssignment.objects.select_related('role').filter(user=user, is_active=True).first()
            if role_assignment and role_assignment.role:
                return role_assignment.role.name.lower()
        except:
            pass
        return 'user'  # Default to regular user if no role found
    
    @property
    def can_mark_paid(self):
        """Check if voucher can be marked as paid"""
        return self.status == 'approved'
    
    @property
    def can_edit(self):
        """Check if voucher can be edited"""
        return self.status in ['draft', 'rejected']
    
    @property
    def is_workflow_completed(self):
        """Check if workflow is completed (paid or cancelled)"""
        return self.status in ['paid', 'cancelled']
    
    def submit_for_approval(self, user):
        """Submit voucher for approval"""
        if not self.can_submit_for_approval:
            raise ValueError(f"Cannot submit voucher with status {self.status}")
        
        self.status = 'pending_approval'
        self.submitted_by = user
        self.submitted_at = timezone.now()
        self.save()
    
    def approve_voucher(self, user):
        """Approve the voucher"""
        if not self.can_approve:
            raise ValueError(f"Cannot approve voucher with status {self.status}")
        
        self.status = 'approved'
        self.approved_by = user
        self.approved_at = timezone.now()
        # Clear any rejection data
        self.rejected_by = None
        self.rejected_at = None
        self.rejection_reason = ''
        self.save()
    
    def reject_voucher(self, user, reason=''):
        """Reject the voucher"""
        if not self.can_reject:
            raise ValueError(f"Cannot reject voucher with status {self.status}")
        
        self.status = 'rejected'
        self.rejected_by = user
        self.rejected_at = timezone.now()
        self.rejection_reason = reason
        # Clear approval data
        self.approved_by = None
        self.approved_at = None
        self.save()
    
    def mark_paid(self, user):
        """Mark voucher as paid"""
        if not self.can_mark_paid:
            raise ValueError(f"Cannot mark voucher with status {self.status} as paid")
        
        self.status = 'paid'
        self.paid_by = user
        self.paid_at = timezone.now()
        self.save()
    
    def cancel_voucher(self, user):
        """Cancel the voucher"""
        if self.status == 'paid':
            raise ValueError("Cannot cancel a paid voucher")
        
        self.status = 'cancelled'
        self.save()
    
    @property
    def workflow_history(self):
        """Get workflow history as a list of events"""
        history = []
        
        if self.created_at and self.created_by:
            history.append({
                'action': 'Created',
                'user': self.created_by,
                'timestamp': self.created_at,
                'status': 'draft'
            })
        
        if self.submitted_at and self.submitted_by:
            history.append({
                'action': 'Submitted for Approval',
                'user': self.submitted_by,
                'timestamp': self.submitted_at,
                'status': 'pending_approval'
            })
        
        if self.approved_at and self.approved_by:
            history.append({
                'action': 'Approved',
                'user': self.approved_by,
                'timestamp': self.approved_at,
                'status': 'approved'
            })
        
        if self.rejected_at and self.rejected_by:
            history.append({
                'action': 'Rejected',
                'user': self.rejected_by,
                'timestamp': self.rejected_at,
                'status': 'rejected',
                'reason': self.rejection_reason
            })
        
        if self.paid_at and self.paid_by:
            history.append({
                'action': 'Marked as Paid',
                'user': self.paid_by,
                'timestamp': self.paid_at,
                'status': 'paid'
            })
        
        # Sort by timestamp
        history.sort(key=lambda x: x['timestamp'])
        return history


class PaymentVoucherDocument(FileEncryptionMixin, models.Model):
    """Reference documents for Payment Vouchers"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('invoice', 'Invoice/Bill'),
        ('receipt', 'Receipt'),
        ('quotation', 'Quotation'),
        ('contract', 'Contract'),
        ('approval_memo', 'Approval Memo'),
        ('purchase_order', 'Purchase Order'),
        ('delivery_note', 'Delivery Note'),
        ('bank_statement', 'Bank Statement'),
        ('tax_document', 'Tax Document'),
        ('other', 'Other Supporting Document'),
    ]
    
    # Reference to the payment voucher
    payment_voucher = models.ForeignKey(PaymentVoucher, on_delete=models.CASCADE, related_name='reference_documents')
    
    # Document details
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='other',
                                   help_text="Type of reference document")
    document_name = models.CharField(max_length=200, help_text="Name or description of the document")
    document_file = models.FileField(upload_to='payment_voucher_docs/%Y/%m/', 
                                   help_text="Upload the reference document file")
    
    # Optional document metadata
    document_number = models.CharField(max_length=100, blank=True, 
                                     help_text="Document number (invoice number, receipt number, etc.)")
    document_date = models.DateField(blank=True, null=True, 
                                   help_text="Date of the document")
    document_amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True,
                                        help_text="Amount mentioned in the document")
    
    # Notes
    notes = models.TextField(blank=True, help_text="Additional notes about this document")
    
    # System fields
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.payment_voucher.voucher_number} - {self.document_name}"
    
    class Meta:
        verbose_name = "Payment Voucher Reference Document"
        verbose_name_plural = "Payment Voucher Reference Documents"
        ordering = ['-uploaded_at']
    
    @property
    def document_type_display(self):
        """Get user-friendly document type display"""
        return dict(self.DOCUMENT_TYPE_CHOICES).get(self.document_type, self.document_type)
    
    def get_file_size(self):
        """Get file size in human readable format"""
        if self.document_file and hasattr(self.document_file, 'size'):
            size = self.document_file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
            return f"{size:.1f} TB"
        return "Unknown"
    
    def get_file_extension(self):
        """Get file extension"""
        if self.document_file and self.document_file.name:
            return os.path.splitext(self.document_file.name)[1].lower()
        return ""


class ServiceHistory(models.Model):
    """Track changes to service prices and details"""
    
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('price_changed', 'Price Changed'),
        ('name_changed', 'Name Changed'),
        ('description_changed', 'Description Changed'),
        ('category_changed', 'Category Changed'),
        ('status_changed', 'Status Changed'),
        ('code_changed', 'Service Code Changed'),
    ]
    
    # Reference to the service
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='history')
    
    # What changed
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    field_name = models.CharField(max_length=50, blank=True, help_text="Name of the field that changed")
    old_value = models.TextField(blank=True, help_text="Previous value")
    new_value = models.TextField(blank=True, help_text="New value")
    
    # When and who
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)
    
    # Additional context
    notes = models.TextField(blank=True, help_text="Additional notes about the change")

    def __str__(self):
        return f"{self.service.name} - {self.get_action_display()} by {self.changed_by} at {self.changed_at}"

    class Meta:
        verbose_name = "Service History"
        verbose_name_plural = "Service Histories"
        ordering = ['-changed_at']


class ServiceCategory(models.Model):
    """Service categories for enhanced organization"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ['name']


class VisaServiceRecord(models.Model):
    """Model to track visa service charges and payment records"""
    
    DURATION_CHOICES = [
        (1, '1 Month'),
        (3, '3 Months'), 
        (6, '6 Months'),
        (12, '1 Year'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Client information
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True, related_name='visa_services')
    client_name = models.CharField(max_length=200, blank=True, help_text="For other clients")
    
    # Service details
    service = models.ForeignKey(Service, on_delete=models.CASCADE, limit_choices_to={'category': 'visas'})
    duration_months = models.IntegerField(choices=DURATION_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Service period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Payment tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='visa_services')
    payment_date = models.DateField(null=True, blank=True)
    
    # Additional information
    notes = models.TextField(blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        client = self.get_client_name()
        return f"Visa Service - {client} - {self.get_duration_months_display()} - ${self.amount}"

    class Meta:
        verbose_name = "Visa Service Record"
        verbose_name_plural = "Visa Service Records"
        ordering = ['-created_at']

    def get_client_name(self):
        """Get the client name"""
        if self.worker:
            return self.worker.get_full_name()
        elif self.client_name:
            return self.client_name
        return "Unknown Client"

    @property
    def is_expired(self):
        """Check if visa service has expired"""
        return timezone.now().date() > self.end_date

    @property
    def is_expiring_soon(self, days=30):
        """Check if visa service is expiring within specified days"""
        return (self.end_date - timezone.now().date()).days <= days

    @property
    def days_remaining(self):
        """Calculate days remaining until expiry"""
        if self.is_expired:
            return 0
        return (self.end_date - timezone.now().date()).days

    def save(self, *args, **kwargs):
        # Auto-calculate end date if not provided
        if not self.end_date and self.start_date:
            self.end_date = self.start_date + relativedelta(months=self.duration_months)
        
        # Auto-set amount from service if not provided
        if not self.amount and self.service:
            self.amount = self.service.default_price
            
        super().save(*args, **kwargs)



