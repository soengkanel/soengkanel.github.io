from django import template
from django.db import models

register = template.Library()

@register.filter
def has_pending_charges(card):
    """Check if a card has pending charges"""
    return card.charges.filter(status='pending').exists()

@register.filter
def pending_charges_count(card):
    """Get count of pending charges for a card"""
    return card.charges.filter(status='pending').count()

@register.filter
def total_outstanding_amount(card):
    """Get total outstanding amount for a card"""
    return card.charges.filter(status='pending').aggregate(
        total=models.Sum('amount')
    )['total'] or 0 