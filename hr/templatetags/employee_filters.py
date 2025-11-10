from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def format_audit_value(value, field_name):
    """
    Format audit log values to be more user-friendly
    """
    if not value or value == "(empty)":
        return value
    
    # Convert to string if not already
    value_str = str(value)
    
    # Handle encrypted/hashed fields (none currently for Employee model)
    encrypted_fields = []
    if any(field.lower().replace(' ', '_') in encrypted_fields for field in [field_name.lower()]):
        if len(value_str) > 30:
            return f"••••••••••••••••{value_str[-4:]}" if len(value_str) > 4 else "••••••••"
    
    # Handle file fields (photos, documents)
    if field_name.lower() in ['photo', 'document', 'file'] or 'photo' in field_name.lower():
        if len(value_str) > 30:
            # Extract filename from path if possible
            filename_match = re.search(r'[\w\-_\.]+\.\w+$', value_str)
            if filename_match:
                return filename_match.group(0)
            return "File uploaded"
    
    # Truncate very long values
    if len(value_str) > 50:
        return f"{value_str[:47]}..."
    
    return value

@register.filter
def is_secure_field(field_name):
    """
    Check if a field contains sensitive/encrypted data
    """
    secure_fields = ['photo']
    return any(field.lower().replace(' ', '_') in secure_fields for field in [field_name.lower()])

@register.filter
def get_change_action(old_value, new_value):
    """
    Determine what type of change occurred
    """
    if old_value == "(empty)" or not old_value:
        return "added"
    elif new_value == "(empty)" or not new_value:
        return "removed"
    else:
        return "updated"

@register.filter
def format_field_name(field_name):
    """
    Format field names to be more readable
    """
    # Convert snake_case or camelCase to Title Case
    field_name = re.sub(r'[_\-]', ' ', field_name)
    field_name = re.sub(r'([a-z])([A-Z])', r'\1 \2', field_name)
    return field_name.title() 