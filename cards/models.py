from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal
import uuid

from zone.models import Worker
from hr.models import Employee


# Simplified Worker ID Card Model
class WorkerIDCard(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('printed', 'Printed'),
        ('delivered', 'Delivered'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ]

    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='id_cards')
    card_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='requested')
    
    # Important dates
    request_date = models.DateTimeField(auto_now_add=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Card details
    photo = models.ImageField(upload_to='worker_id_photos/', null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    # Printing tracking fields
    print_count = models.PositiveIntegerField(default=0, help_text='Number of times this card has been printed')
    first_print_date = models.DateTimeField(null=True, blank=True, help_text='Date of first print (free)')
    last_print_date = models.DateTimeField(null=True, blank=True, help_text='Date of most recent print')
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Worker ID: {self.card_number or 'Pending'} - {self.worker}"

    class Meta:
        verbose_name = "Worker ID Card"
        verbose_name_plural = "Worker ID Cards"
        ordering = ['-request_date']

    def save(self, *args, **kwargs):
        # Auto-generate card number when printed/delivered/active
        if not self.card_number and self.status in ['printed', 'delivered', 'active']:
            self.card_number = self.generate_unique_card_number()
        super().save(*args, **kwargs)
    
    def generate_card_number(self):
        """Generate a card number in the format: {ZONE}-{BUILDING_CODE}-{FLOOR_NUMBER}-{SEQUENCE}"""
        import re
        from django.db import transaction

        if not self.worker.zone or not self.worker.building or not self.worker.floor:
            # Fallback to simple format if zone/building/floor not available
            return f"WID{timezone.now().year}{str(uuid.uuid4().hex[:6]).upper()}"

        # Extract zone code from zone name
        zone_raw = self.worker.zone.name if self.worker.zone else 'Z'

        # Extract proper zone name - if zone contains underscore, take only the first part
        # This handles cases where zone name is stored as "3H_B12" instead of just "3H"
        if '_' in zone_raw:
            # If zone name contains underscore (like "3H_B12"), extract just the zone part (3H)
            zone_parts = zone_raw.split('_')
            zone_code = zone_parts[0]
        else:
            zone_code = zone_raw.replace(' ', '')

        # Additional cleanup: if zone name looks like it contains building info, extract zone only
        # Handle patterns like "3HB12" -> "3H"
        zone_match = re.match(r'^([A-Za-z0-9]+)B[0-9]+.*', zone_code)
        if zone_match:
            zone_code = zone_match.group(1)

        # Get building code
        building_code = self.worker.building.code if hasattr(self.worker.building, 'code') else str(self.worker.building)[:10]

        # Get floor number
        floor_number = f"F{self.worker.floor.floor_number}" if hasattr(self.worker.floor, 'floor_number') else str(self.worker.floor)[:10]

        # Find the next sequence number for this zone-building-floor combination
        # Use select_for_update to lock the rows during the transaction
        prefix = f"{zone_code}-{building_code}-{floor_number}-"

        with transaction.atomic():
            existing_cards = WorkerIDCard.objects.select_for_update().filter(
                card_number__startswith=prefix
            ).exclude(pk=self.pk if self.pk else None)

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

        return f"{zone_code}-{building_code}-{floor_number}-{next_sequence:04d}"

    def generate_unique_card_number(self, max_retries=5):
        """Generate a unique card number with retry logic for concurrent scenarios"""
        import time
        from django.db import IntegrityError

        for attempt in range(max_retries):
            try:
                card_number = self.generate_card_number()

                # Check if this card number already exists
                if WorkerIDCard.objects.filter(card_number=card_number).exclude(pk=self.pk).exists():
                    # If it exists, wait a bit and retry
                    time.sleep(0.1 * (attempt + 1))  # Exponential backoff
                    continue

                return card_number
            except Exception as e:
                if attempt == max_retries - 1:
                    # On last attempt, raise the exception
                    raise
                time.sleep(0.1 * (attempt + 1))

        # If all retries failed, raise an exception
        raise ValueError(f"Could not generate unique card number after {max_retries} attempts")

    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False

    @property
    def is_first_print_free(self):
        """Check if this would be the first print (free)"""
        return self.print_count == 0

    @property
    def next_print_charge(self):
        """Calculate the charge for the next print"""
        if self.is_first_print_free:
            return Decimal('0.00')
        
        # Get charge rate from settings (default to $5.00 for reprints)
        from django.conf import settings
        return Decimal(getattr(settings, 'CARD_REPRINT_CHARGE', '5.00'))
    
    @property
    def latest_batch(self):
        """Get the most recent print batch for this card"""
        latest_print = self.printing_history.filter(print_batch__isnull=False).order_by('-print_date').first()
        return latest_print.print_batch if latest_print else None
    
    @property
    def latest_batch_id(self):
        """Get the short batch ID of the most recent print batch"""
        batch = self.latest_batch
        return batch.short_batch_id if batch else None
    
    @property
    def latest_batch_display(self):
        """Get the display name for the most recent print batch (name or ID)"""
        batch = self.latest_batch
        if not batch:
            return None
        return batch.batch_name if batch.batch_name else batch.short_batch_id

    def record_print(self, user, charge_amount=None, notes=None, print_batch=None):
        """Record a printing event and create charge if applicable"""
        now = timezone.now()
        
        # Update card printing fields
        self.print_count += 1
        if self.print_count == 1:
            self.first_print_date = now
        self.last_print_date = now
        self.save()
        
        # Create printing history record
        print_history = CardPrintingHistory.objects.create(
            card=self,
            printed_by=user,
            print_batch=print_batch,
            print_number=self.print_count,
            charge_amount=charge_amount or self.next_print_charge,
            notes=notes
        )
        
        # Create charge record if this is a reprint
        if self.print_count > 1 and charge_amount and charge_amount > 0:
            charge = CardCharge.objects.create(
                worker=self.worker,
                card=self,
                print_history=print_history,
                charge_type='reprint',
                amount=charge_amount,
                reason=f'Card reprint #{self.print_count}',
                status='pending'
            )
            return charge
        
        return None


class CardPrintingHistory(models.Model):
    """Track each time a card is printed"""
    
    card = models.ForeignKey(WorkerIDCard, on_delete=models.CASCADE, related_name='printing_history')
    printed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='printed_cards')
    print_batch = models.ForeignKey('PrintBatch', on_delete=models.SET_NULL, null=True, blank=True, related_name='worker_printing_records', help_text='Batch this print belongs to')
    print_date = models.DateTimeField(auto_now_add=True)
    print_number = models.PositiveIntegerField(help_text='Sequential print number for this card')
    charge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card} - Print #{self.print_number} on {self.print_date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Card Printing History"
        verbose_name_plural = "Card Printing History"
        ordering = ['-print_date']
        unique_together = ['card', 'print_number']

    @property
    def is_free_print(self):
        """Check if this was a free print (first print)"""
        return self.print_number == 1

    @property
    def charge_status(self):
        """Get the charge status for this print"""
        if self.is_free_print:
            return 'free'
        try:
            charge = self.charge_record
            return charge.status
        except CardCharge.DoesNotExist:
            return 'no_charge'


class CardCharge(models.Model):
    """Track charges for card reprints and lost cards"""
    
    CHARGE_TYPE_CHOICES = [
        ('reprint', 'Card Reprint'),
        ('lost', 'Lost Card Replacement'),
        ('damaged', 'Damaged Card Replacement'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
        ('cancelled', 'Cancelled'),
    ]
    
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='card_charges')
    card = models.ForeignKey(WorkerIDCard, on_delete=models.CASCADE, related_name='charges')
    print_history = models.OneToOneField(CardPrintingHistory, on_delete=models.CASCADE, 
                                        related_name='charge_record', null=True, blank=True)
    
    charge_type = models.CharField(max_length=20, choices=CHARGE_TYPE_CHOICES, default='reprint')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Billing integration
    invoice = models.ForeignKey('billing.Invoice', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='card_charges', help_text='Associated invoice for this charge')
    auto_invoice = models.BooleanField(default=True, help_text='Automatically create invoice for this charge')
    
    # Payment tracking
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Admin fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_charges')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_charges')
    notes = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.worker} - {self.get_charge_type_display()} - ${self.amount}"

    class Meta:
        verbose_name = "Card Charge"
        verbose_name_plural = "Card Charges"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Create invoice automatically if enabled and charge amount > 0
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new and self.auto_invoice and self.amount > 0 and not self.invoice:
            self.create_invoice()

    def create_invoice(self):
        """Create an invoice for this charge"""
        from billing.models import Invoice, InvoiceLineItem, Service
        from datetime import timedelta
        
        # Check if service exists for this charge type, create if not
        service = self.get_or_create_service()
        
        # Create invoice
        invoice = Invoice.objects.create(
            worker=self.worker,
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),  # 30 days from issue
            created_by=self.created_by,
            notes=f'Card charge: {self.reason}'
        )
        
        # Create line item
        InvoiceLineItem.objects.create(
            invoice=invoice,
            service=service,
            description=f'{self.get_charge_type_display()}: {self.reason}',
            quantity=1,
            unit_price=self.amount,
            notes=f'Card: {self.card.card_number or "Pending"}'
        )
        
        # Link the invoice to this charge
        self.invoice = invoice
        self.save(update_fields=['invoice'])
        
        return invoice

    def get_or_create_service(self):
        """Get or create service for this charge type"""
        from billing.models import Service
        
        service_names = {
            'reprint': 'Worker ID Card Reprint',
            'lost': 'Lost Worker ID Card Replacement',
            'damaged': 'Damaged Worker ID Card Replacement',
            'other': 'Worker ID Card Service'
        }
        
        service_name = service_names.get(self.charge_type, 'Worker ID Card Service')
        
        service, created = Service.objects.get_or_create(
            name=service_name,
            category='id_cards',
            defaults={
                'description': f'Service charge for {service_name.lower()}',
                'default_price': self.amount,
                'is_active': True
            }
        )
        
        return service

    def mark_as_paid(self, payment_method=None, payment_reference=None, notes=None):
        """Mark the charge as paid and update invoice if exists"""
        self.status = 'paid'
        self.payment_date = timezone.now()
        if payment_method:
            self.payment_method = payment_method
        if payment_reference:
            self.payment_reference = payment_reference
        if notes:
            self.notes = notes
        
        # Update associated invoice status
        if self.invoice and self.invoice.status == 'pending':
            # Check if invoice is fully paid
            total_paid = self.invoice.total_paid + self.amount
            if total_paid >= self.invoice.total_amount:
                self.invoice.status = 'paid'
                self.invoice.save()
        
        self.save()

    def waive_charge(self, approved_by, reason=None):
        """Waive the charge and cancel associated invoice"""
        self.status = 'waived'
        self.approved_by = approved_by
        if reason:
            self.notes = reason
        
        # Cancel associated invoice if it exists and hasn't been paid
        if self.invoice and self.invoice.status in ['pending', 'overdue']:
            self.invoice.status = 'cancelled'
            self.invoice.notes = f"Cancelled due to charge waiver: {reason or 'Administrative waiver'}"
            self.invoice.save()
        
        self.save()

    @property
    def is_outstanding(self):
        """Check if charge is still pending payment"""
        return self.status == 'pending'

    @property
    def invoice_number(self):
        """Get the invoice number if invoice exists"""
        return self.invoice.invoice_number if self.invoice else None

    @property
    def invoice_status(self):
        """Get the invoice status if invoice exists"""
        return self.invoice.get_status_display() if self.invoice else None



# Employee ID Card Model
class EmployeeIDCard(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('printed', 'Printed'),
        ('delivered', 'Delivered'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]

    CARD_TYPE_CHOICES = [
        ('standard', 'Standard'),
        ('manager', 'Manager'),
        ('executive', 'Executive'),
        ('temporary', 'Temporary'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='employee_id_cards')
    card_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='standard')
    
    # Important dates
    request_date = models.DateTimeField(null=True, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # Card details
    photo = models.ImageField(upload_to='employee_id_photos/', null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    
    # Printing tracking fields
    print_count = models.PositiveIntegerField(default=0, help_text='Number of times this card has been printed')
    first_print_date = models.DateTimeField(null=True, blank=True, help_text='Date of first print (free)')
    last_print_date = models.DateTimeField(null=True, blank=True, help_text='Date of most recent print')
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Employee ID: {self.card_number or 'Pending'} - {self.employee.full_name}"

    class Meta:
        verbose_name = "Employee ID Card"
        verbose_name_plural = "Employee ID Cards"
        ordering = ['-request_date']

    @property
    def photo_url(self):
        """Return the URL of the employee ID card photo."""
        if self.photo and self.photo.name:
            return self.photo.url
        return None

    def save(self, *args, **kwargs):
        # Auto-generate card number when printed
        if not self.card_number and self.status in ['printed', 'delivered', 'active']:
            self.card_number = f"EID{timezone.now().year}{str(uuid.uuid4().hex[:6]).upper()}"
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now().date() > self.expiry_date
        return False

    @property
    def is_first_print_free(self):
        """Check if this would be the first print (free)"""
        return self.print_count == 0

    @property
    def next_print_charge(self):
        """Calculate the charge for the next print"""
        if self.is_first_print_free:
            return Decimal('0.00')
        
        # Get charge rate from settings (default to $5.00 for reprints)
        from django.conf import settings
        return Decimal(getattr(settings, 'EMPLOYEE_CARD_REPRINT_CHARGE', '5.00'))
    
    @property
    def latest_batch(self):
        """Get the most recent print batch for this card"""
        latest_print = self.printing_history.filter(print_batch__isnull=False).order_by('-print_date').first()
        return latest_print.print_batch if latest_print else None
    
    @property
    def latest_batch_id(self):
        """Get the short batch ID of the most recent print batch"""
        batch = self.latest_batch
        return batch.short_batch_id if batch else None
    
    @property
    def latest_batch_display(self):
        """Get the display name for the most recent print batch (name or ID)"""
        batch = self.latest_batch
        if not batch:
            return None
        return batch.batch_name if batch.batch_name else batch.short_batch_id

    def record_print(self, user, charge_amount=None, notes=None, print_batch=None):
        """Record a printing event and create charge if applicable"""
        now = timezone.now()
        
        # Update card printing fields
        self.print_count += 1
        if self.print_count == 1:
            self.first_print_date = now
        self.last_print_date = now
        self.save()
        
        # Create printing history record
        print_history = EmployeeCardPrintingHistory.objects.create(
            card=self,
            printed_by=user,
            print_batch=print_batch,
            print_number=self.print_count,
            charge_amount=charge_amount or self.next_print_charge,
            notes=notes
        )
        
        # Create charge record if this is a reprint
        if self.print_count > 1 and charge_amount and charge_amount > 0:
            charge = EmployeeCardCharge.objects.create(
                employee=self.employee,
                card=self,
                print_history=print_history,
                charge_type='reprint',
                amount=charge_amount,
                reason=f'Card reprint #{self.print_count}',
                status='pending'
            )
            return charge
        
        return None


class EmployeeCardPrintingHistory(models.Model):
    """Track each time an employee card is printed"""
    
    card = models.ForeignKey(EmployeeIDCard, on_delete=models.CASCADE, related_name='printing_history')
    printed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='printed_employee_cards')
    print_batch = models.ForeignKey('PrintBatch', on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_printing_records', help_text='Batch this print belongs to')
    print_date = models.DateTimeField(auto_now_add=True)
    print_number = models.PositiveIntegerField(help_text='Sequential print number for this card')
    charge_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.card} - Print #{self.print_number} on {self.print_date.strftime('%Y-%m-%d')}"

    class Meta:
        verbose_name = "Employee Card Printing History"
        verbose_name_plural = "Employee Card Printing History"
        ordering = ['-print_date']
        unique_together = ['card', 'print_number']

    @property
    def is_free_print(self):
        """Check if this was a free print (first print)"""
        return self.print_number == 1

    @property
    def charge_status(self):
        """Get the charge status for this print"""
        if self.is_free_print:
            return 'free'
        try:
            charge = self.charge_record
            return charge.status
        except EmployeeCardCharge.DoesNotExist:
            return 'no_charge'


class EmployeeCardCharge(models.Model):
    """Track charges for employee card reprints and lost cards"""
    
    CHARGE_TYPE_CHOICES = [
        ('reprint', 'Card Reprint'),
        ('lost', 'Lost Card Replacement'),
        ('damaged', 'Damaged Card Replacement'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Payment'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
        ('cancelled', 'Cancelled'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='card_charges')
    card = models.ForeignKey(EmployeeIDCard, on_delete=models.CASCADE, related_name='charges')
    print_history = models.OneToOneField(EmployeeCardPrintingHistory, on_delete=models.CASCADE, 
                                        related_name='charge_record', null=True, blank=True)
    
    charge_type = models.CharField(max_length=20, choices=CHARGE_TYPE_CHOICES, default='reprint')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Billing integration
    invoice = models.ForeignKey('billing.Invoice', on_delete=models.SET_NULL, null=True, blank=True,
                               related_name='employee_card_charges', help_text='Associated invoice for this charge')
    auto_invoice = models.BooleanField(default=True, help_text='Automatically create invoice for this charge')
    
    # Payment tracking
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    payment_reference = models.CharField(max_length=100, blank=True, null=True)
    
    # Admin fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_employee_charges')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_employee_charges')
    notes = models.TextField(blank=True, null=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_charge_type_display()} - {self.employee.get_full_name()} - ${self.amount}"

    class Meta:
        verbose_name = "Employee Card Charge"
        verbose_name_plural = "Employee Card Charges"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # Save the charge first to get a primary key
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Create invoice automatically if enabled and charge amount > 0 and this is a new charge
        if is_new and self.auto_invoice and self.amount > 0 and not self.invoice:
            try:
                self.create_invoice()
            except Exception as e:
                pass

    def create_invoice(self):
        """Create an invoice for this charge"""
        from billing.models import Invoice, InvoiceLineItem
        from datetime import timedelta
        
        # Get or create the service first
        service = self.get_or_create_service()
        
        # Create the invoice with proper fields
        invoice = Invoice.objects.create(
            client_name=self.employee.full_name,  # Use client_name for employees
            issue_date=timezone.now().date(),
            due_date=timezone.now().date() + timedelta(days=30),  # 30 days from issue
            created_by=self.created_by,
            notes=f'Card charge: {self.reason}'
        )
        
        # Create invoice line item
        InvoiceLineItem.objects.create(
            invoice=invoice,
            service=service,
            description=f'{self.get_charge_type_display()}: {self.reason}',
            quantity=1,
            unit_price=self.amount,
            notes=f'Card: {self.card.card_number or "Pending"}'
        )
        
        # Link the invoice to this charge
        self.invoice = invoice
        self.save(update_fields=['invoice'])
        
        return invoice

    def get_or_create_service(self):
        """Get or create service for this charge type"""
        from billing.models import Service
        
        service_names = {
            'reprint': 'Employee ID Card Reprint',
            'lost': 'Lost Employee ID Card Replacement',
            'damaged': 'Damaged Employee ID Card Replacement',
            'other': 'Employee ID Card Service'
        }
        
        service_name = service_names.get(self.charge_type, 'Employee ID Card Service')
        
        service, created = Service.objects.get_or_create(
            name=service_name,
            category='id_cards',
            defaults={
                'description': f'Service charge for {service_name.lower()}',
                'default_price': self.amount,
                'is_active': True
            }
        )
        
        return service

    def mark_as_paid(self, payment_method=None, payment_reference=None, notes=None):
        """Mark the charge as paid and update invoice if exists"""
        self.status = 'paid'
        self.payment_date = timezone.now()
        if payment_method:
            self.payment_method = payment_method
        if payment_reference:
            self.payment_reference = payment_reference
        if notes:
            self.notes = notes
        
        # Update associated invoice status
        if self.invoice and self.invoice.status == 'pending':
            # Check if invoice is fully paid
            total_paid = self.invoice.total_paid + self.amount
            if total_paid >= self.invoice.total_amount:
                self.invoice.status = 'paid'
                self.invoice.save()
        
        self.save()

    def waive_charge(self, approved_by, reason=None):
        """Waive the charge and cancel associated invoice"""
        self.status = 'waived'
        self.approved_by = approved_by
        if reason:
            self.notes = reason
        
        # Cancel associated invoice if it exists and hasn't been paid
        if self.invoice and self.invoice.status in ['pending', 'overdue']:
            self.invoice.status = 'cancelled'
            self.invoice.notes = f"Cancelled due to charge waiver: {reason or 'Administrative waiver'}"
            self.invoice.save()
        
        self.save()

    @property
    def is_outstanding(self):
        """Check if charge is still pending payment"""
        return self.status == 'pending'

    @property
    def invoice_number(self):
        """Get the invoice number if invoice exists"""
        return self.invoice.invoice_number if self.invoice else None

    @property
    def invoice_status(self):
        """Get the invoice status if invoice exists"""
        return self.invoice.get_status_display() if self.invoice else None


# Enhanced Card Replacement Model (Temporary version for existing schema)
class CardReplacement(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    REASON_CHOICES = [
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
        ('expired', 'Expired'),
        ('stolen', 'Stolen'),
        ('other', 'Other'),
    ]

    # Generic reference to any card type
    worker_card = models.ForeignKey(WorkerIDCard, on_delete=models.CASCADE, null=True, blank=True, related_name='replacements')
    employee_card = models.ForeignKey(EmployeeIDCard, on_delete=models.CASCADE, null=True, blank=True, related_name='replacements')
    
    # Basic fields that exist in the original schema
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, default='other')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True, null=True)  # Keep original field name for now
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        card_info = ""
        if self.worker_card:
            card_info = f"Worker: {self.worker_card.worker}"
        elif self.employee_card:
            card_info = f"Employee: {self.employee_card.employee}"
        return f"Replacement for {card_info} - {self.get_reason_display()}"

    class Meta:
        verbose_name = "Card Replacement"
        verbose_name_plural = "Card Replacements"
        ordering = ['-created_at']

    # Computed properties until database is fixed
    @property
    def replacement_charge(self):
        """Calculate the replacement charge based on card type and reason"""
        # Lost cards charge $10 for both worker and employee
        if self.reason in ['lost', 'stolen']:
            return Decimal('10.00')
        
        # Regular replacement charges
        if self.worker_card:
            return Decimal('2.00')  # Worker replacement: $2
        elif self.employee_card:
            return Decimal('2.00')  # Employee replacement: $2
        
        return Decimal('0.00')

    @property
    def request_notes(self):
        """Alias for notes field"""
        return self.notes

    @property
    def request_date(self):
        """Use created_at as request_date"""
        return self.created_at

    @property
    def requested_by(self):
        """Return None until database is updated"""
        return None

    @property
    def approved_by(self):
        """Return None until database is updated"""
        return None

    @property
    def approval_date(self):
        """Return None until database is updated"""
        return None

    @property
    def approval_notes(self):
        """Return None until database is updated"""
        return None

    @property
    def invoice(self):
        """Return None until database is updated"""
        return None

    @property
    def auto_invoice(self):
        """Return True by default"""
        return True

    @property
    def completed_by(self):
        """Return None until database is updated"""
        return None

    @property
    def completion_date(self):
        """Return None until database is updated"""
        return None

    @property
    def new_card_number(self):
        """Return None until database is updated"""
        return None

    def approve_replacement(self, approved_by, notes=None):
        """Approve the replacement request and generate invoice"""
        from django.utils import timezone
        
        # Update status and notes
        self.status = 'approved'
        if notes:
            self.notes = notes
        self.save()
        
        # Mark original card as lost/damaged when appropriate
        if self.reason in ['lost', 'stolen', 'damaged']:
            self.mark_original_card_as_lost_or_damaged()
        
        # Auto-generate invoice if enabled
        if self.auto_invoice:
            try:
                invoice = self.create_invoice()
            except Exception as e:
                pass
        
        return True

    def reject_replacement(self, rejected_by, reason=None):
        """Reject the replacement request (simplified version)"""
        self.status = 'rejected'
        if reason:
            self.notes = reason
        self.save()

    def complete_replacement(self, completed_by, new_card_number=None, notes=None):
        """Complete the replacement request (simplified version)"""
        self.status = 'completed'
        if notes:
            self.notes = notes
        self.save()

    def mark_original_card_as_lost_or_damaged(self):
        """Mark the original card as lost or damaged"""
        if self.worker_card:
            self.worker_card.status = 'lost' if self.reason in ['lost', 'stolen'] else 'damaged'
            self.worker_card.save()
        elif self.employee_card:
            self.employee_card.status = 'lost' if self.reason in ['lost', 'stolen'] else 'damaged'
            self.employee_card.save()

    def create_invoice(self):
        """Create an invoice for the replacement charge (simplified version)"""
        try:
            from billing.models import Invoice, InvoiceLineItem, Service
            from datetime import timedelta
            from django.utils import timezone
            
            # Get or create the service
            service = self.get_or_create_service()
            
            # Determine client information
            client_name = self.card_holder_name
            worker = None
            
            if self.worker_card:
                worker = self.worker_card.worker
            
            # Create the invoice
            invoice = Invoice.objects.create(
                worker=worker,
                client_name=client_name if not worker else '',
                issue_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=30),
                notes=f'Card replacement request: {self.get_reason_display()}'
            )
            
            # Create invoice line item with proper description
            description = self.get_invoice_description()
            
            InvoiceLineItem.objects.create(
                invoice=invoice,
                service=service,
                description=description,
                quantity=1,
                unit_price=self.replacement_charge,
                notes=f'Original card: {self.get_original_card_number()}'
            )
            
            return invoice
            
        except Exception as e:
            # Return None if invoice creation fails
            return None

    def get_or_create_service(self):
        """Get or create service for this replacement type"""
        from billing.models import Service
        
        # Determine service name based on card type and reason
        if self.reason == 'lost':
            if self.worker_card:
                service_name = 'Lost Worker ID Card Replacement'
            else:
                service_name = 'Lost Employee ID Card Replacement'
        elif self.reason == 'stolen':
            if self.worker_card:
                service_name = 'Stolen Worker ID Card Replacement'
            else:
                service_name = 'Stolen Employee ID Card Replacement'
        else:
            if self.worker_card:
                service_name = 'Worker ID Card Replacement'
            else:
                service_name = 'Employee ID Card Replacement'
        
        service, created = Service.objects.get_or_create(
            name=service_name,
            category='id_cards',
            defaults={
                'description': f'Replacement service for {service_name.lower()}',
                'default_price': self.replacement_charge,
                'is_active': True
            }
        )
        
        return service

    def get_invoice_description(self):
        """Get the proper invoice description based on card type and reason"""
        card_type = "Worker" if self.worker_card else "Employee"
        
        if self.reason == 'lost':
            return f"Lost {card_type} ID Card Replacement - {self.card_holder_name}"
        elif self.reason == 'stolen':
            return f"Stolen {card_type} ID Card Replacement - {self.card_holder_name}"
        elif self.reason == 'damaged':
            return f"Damaged {card_type} ID Card Replacement - {self.card_holder_name}"
        elif self.reason == 'expired':
            return f"Expired {card_type} ID Card Replacement - {self.card_holder_name}"
        else:
            return f"{card_type} ID Card Replacement - {self.card_holder_name}"

    @property
    def card_holder_name(self):
        """Get the name of the card holder"""
        if self.worker_card:
            return self.worker_card.worker.get_full_name()
        elif self.employee_card:
            return self.employee_card.employee.full_name
        return "Unknown"

    def get_original_card_number(self):
        """Get the original card number"""
        if self.worker_card:
            return self.worker_card.card_number or 'Pending'
        elif self.employee_card:
            return self.employee_card.card_number or 'Pending'
        return 'Unknown'

    @property
    def card_type(self):
        """Get the card type"""
        if self.worker_card:
            return 'Worker'
        elif self.employee_card:
            return 'Employee'
        return 'Unknown'

    @property
    def is_lost_card(self):
        """Check if this is a lost card replacement"""
        return self.reason in ['lost', 'stolen']

    @property
    def invoice_number(self):
        """Get the invoice number if invoice exists"""
        try:
            from billing.models import Invoice
            from django.db import models as django_models
            # Look for invoices that reference this replacement
            invoice = Invoice.objects.filter(
                notes__icontains=f'Card replacement request: {self.get_reason_display()}'
            ).filter(
                # Try to match by client or worker
                django_models.Q(worker=self.worker_card.worker if self.worker_card else None) |
                django_models.Q(client_name__icontains=self.card_holder_name)
            ).first()
            
            return invoice.invoice_number if invoice else None
        except:
            return None

    @property
    def invoice_status(self):
        """Get the invoice status if invoice exists"""
        try:
            from billing.models import Invoice
            from django.db import models as django_models
            invoice = Invoice.objects.filter(
                notes__icontains=f'Card replacement request: {self.get_reason_display()}'
            ).filter(
                django_models.Q(worker=self.worker_card.worker if self.worker_card else None) |
                django_models.Q(client_name__icontains=self.card_holder_name)
            ).first()
            
            return invoice.status if invoice else None
        except:
            return None

    @property
    def is_paid(self):
        """Check if the replacement has been paid for"""
        try:
            from billing.models import Invoice
            from django.db import models as django_models
            invoice = Invoice.objects.filter(
                notes__icontains=f'Card replacement request: {self.get_reason_display()}'
            ).filter(
                django_models.Q(worker=self.worker_card.worker if self.worker_card else None) |
                django_models.Q(client_name__icontains=self.card_holder_name)
            ).first()
            
            return invoice.status == 'paid' if invoice else False
        except:
            return False


class PrintBatch(models.Model):
    """Track print batches to group multiple cards printed together"""
    
    batch_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, help_text='Unique batch identifier')
    batch_name = models.CharField(max_length=100, blank=True, help_text='Optional name for the batch')
    
    # Batch info
    printed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='print_batches')
    print_date = models.DateTimeField(auto_now_add=True)
    card_count = models.PositiveIntegerField(default=0, help_text='Number of cards in this batch')
    
    # Batch type tracking
    BATCH_TYPE_CHOICES = [
        ('worker', 'Worker ID Cards'),
        ('employee', 'Employee ID Cards'),
        ('mixed', 'Mixed Card Types'),
    ]
    batch_type = models.CharField(max_length=20, choices=BATCH_TYPE_CHOICES, default='worker')
    
    # Additional tracking
    notes = models.TextField(blank=True, help_text='Optional notes about this print batch')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Batch {self.batch_id.hex[:8]} - {self.card_count} cards ({self.print_date.strftime('%Y-%m-%d %H:%M')})"
    
    class Meta:
        verbose_name = "Print Batch"
        verbose_name_plural = "Print Batches"
        ordering = ['-print_date']
    
    @property
    def short_batch_id(self):
        """Return shortened version of batch ID for display"""
        return self.batch_id.hex[:8].upper()
    
    def get_worker_cards(self):
        """Get all worker cards in this batch"""
        return self.worker_printing_records.all()
    
    def get_employee_cards(self):
        """Get all employee cards in this batch"""
        return self.employee_printing_records.all()
    
    def get_all_cards(self):
        """Get all cards in this batch regardless of type"""
        worker_cards = list(self.worker_printing_records.all())
        employee_cards = list(self.employee_printing_records.all())
        return worker_cards + employee_cards 