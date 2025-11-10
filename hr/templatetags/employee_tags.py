from django import template
from django.contrib.auth.models import User

register = template.Library()


@register.simple_tag
def get_employee(user):
    """
    Get employee record for a user.

    Usage: {% get_employee user as employee %}
    """
    if user and user.is_authenticated:
        return getattr(user, 'employee', None)
    return None


@register.filter
def has_employee(user):
    """
    Check if user has an employee record.

    Usage: {% if user|has_employee %}
    """
    return hasattr(user, 'employee') and user.employee is not None


@register.filter
def employee_name(user):
    """
    Get employee full name from user.

    Usage: {{ user|employee_name }}
    """
    if user and hasattr(user, 'employee') and user.employee:
        return user.employee.get_full_name()
    return user.get_full_name() if user else ""


@register.filter
def employee_id(user):
    """
    Get employee ID from user.

    Usage: {{ user|employee_id }}
    """
    if user and hasattr(user, 'employee') and user.employee:
        return user.employee.employee_id
    return ""


@register.filter
def employee_photo_url(user):
    """
    Get employee photo URL from user.

    Usage: {{ user|employee_photo_url }}
    """
    if user and hasattr(user, 'employee') and user.employee:
        return user.employee.photo_url
    return '/static/images/default-avatar.svg'


@register.filter
def is_employee_manager(user):
    """
    Check if user's employee is a manager.

    Usage: {% if user|is_employee_manager %}
    """
    if user and hasattr(user, 'employee') and user.employee:
        return user.employee.is_manager()
    return False


@register.filter
def can_approve_attendance(user):
    """
    Check if user can approve attendance requests.

    Usage: {% if user|can_approve_attendance %}
    """
    if user and hasattr(user, 'employee') and user.employee:
        return user.employee.can_approve_attendance_requests()
    return False


@register.inclusion_tag('hr/employee_card.html')
def employee_card(employee, show_details=True):
    """
    Render employee card component.

    Usage: {% employee_card employee %}
           {% employee_card employee show_details=False %}
    """
    return {
        'employee': employee,
        'show_details': show_details,
    }


@register.inclusion_tag('hr/employee_avatar.html')
def employee_avatar(employee, size='md'):
    """
    Render employee avatar component.

    Usage: {% employee_avatar employee %}
           {% employee_avatar employee size='sm' %}
    """
    sizes = {
        'xs': 'width: 24px; height: 24px;',
        'sm': 'width: 32px; height: 32px;',
        'md': 'width: 48px; height: 48px;',
        'lg': 'width: 64px; height: 64px;',
        'xl': 'width: 128px; height: 128px;',
    }

    return {
        'employee': employee,
        'size': size,
        'style': sizes.get(size, sizes['md']),
    }