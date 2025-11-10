from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Payment(models.Model):
    """Payment tracking for invoices"""
    
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('credit_card', 'Credit Card'),
        ('online', 'Online Payment'),
        ('other', 'Other'),
    ]
    
    # Payment identification
    payment_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Reference to invoice (from billing app)
    invoice = models.ForeignKey('billing.Invoice', on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    invoice_number = models.CharField(max_length=50, help_text="Invoice number from billing system")
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    payment_date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    reference_number = models.CharField(max_length=100, blank=True, help_text="Check number, transaction ID, etc.")
    
    # Payment status
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='completed')
    
    # Additional information
    notes = models.TextField(blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Payment {self.payment_number} - {self.invoice_number} - ${self.amount}"

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-payment_date', '-created_at']

    def save(self, *args, **kwargs):
        # Auto-generate payment number
        if not self.payment_number:
            prefix = "PAY"
            self.payment_number = f"{prefix}{timezone.now().year}{str(uuid.uuid4().hex[:6]).upper()}"
        
        # Sync invoice_number with invoice if invoice is set
        if self.invoice and not self.invoice_number:
            self.invoice_number = self.invoice.invoice_number
        
        super().save(*args, **kwargs)
