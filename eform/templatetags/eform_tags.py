from django import template
import re

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary"""
    if dictionary and key:
        return dictionary.get(key, '')
    return ''

@register.filter
def get_employee_name(value):
    """Get employee full name from ID or return the value if it's already a name"""
    if not value:
        return ''

    # If it's already a string name (not a number), return it as-is
    try:
        # Try to convert to int - if it fails, it's probably already a name
        employee_id = int(value)
    except (ValueError, TypeError):
        # It's already a name string, return it
        return value

    # It's an ID, look up the employee
    try:
        from hr.models import Employee
        employee = Employee.objects.get(id=employee_id)
        return f"{employee.first_name} {employee.last_name}"
    except Employee.DoesNotExist:
        return ''

@register.filter
def extract_duration(service_name):
    """Extract duration from service name (e.g., '1 MONTH', '3 MONTHS', '1 YEAR')"""
    if not service_name:
        return ''

    # Pattern to match numbers followed by duration words
    patterns = [
        r'(\d+)\s*(MONTH|MONTHS)',
        r'(\d+)\s*(YEAR|YEARS)',
        r'(\d+)\s*(WEEK|WEEKS)',
        r'(\d+)\s*(DAY|DAYS)'
    ]

    for pattern in patterns:
        match = re.search(pattern, service_name.upper())
        if match:
            number = match.group(1)
            unit = match.group(2)

            # Normalize to singular/plural
            if unit in ['MONTH', 'MONTHS']:
                unit = 'MONTH' if number == '1' else 'MONTHS'
            elif unit in ['YEAR', 'YEARS']:
                unit = 'YEAR' if number == '1' else 'YEARS'
            elif unit in ['WEEK', 'WEEKS']:
                unit = 'WEEK' if number == '1' else 'WEEKS'
            elif unit in ['DAY', 'DAYS']:
                unit = 'DAY' if number == '1' else 'DAYS'

            return f"{number} {unit}"

    return service_name  # Return original if no pattern matches