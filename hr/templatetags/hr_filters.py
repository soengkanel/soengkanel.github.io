from django import template
from datetime import datetime, date, timedelta

register = template.Library()

@register.filter
def add_days(value, arg):
    """Add a number of days to a date."""
    if isinstance(value, (date, datetime)):
        try:
            days = int(arg)
            return value + timedelta(days=days)
        except (ValueError, TypeError):
            return value
    return value

@register.filter
def subtract_days(value, arg):
    """Subtract a number of days from a date."""
    if isinstance(value, (date, datetime)):
        try:
            days = int(arg)
            return value - timedelta(days=days)
        except (ValueError, TypeError):
            return value
    return value

@register.filter
def days_until(value):
    """Calculate days until a date from today."""
    if isinstance(value, (date, datetime)):
        today = date.today()
        if isinstance(value, datetime):
            value = value.date()
        delta = value - today
        return delta.days
    return None

@register.filter
def is_expiring_soon(value, days=30):
    """Check if a date is expiring within the specified days."""
    if isinstance(value, (date, datetime)):
        today = date.today()
        if isinstance(value, datetime):
            value = value.date()
        delta = value - today
        return 0 <= delta.days <= days
    return False

@register.filter
def is_expired(value):
    """Check if a date has passed."""
    if isinstance(value, (date, datetime)):
        today = date.today()
        if isinstance(value, datetime):
            value = value.date()
        return value < today
    return False

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary in templates."""
    if not dictionary:
        return None
    return dictionary.get(key) 