"""
Utility functions for the core application
"""
from django.contrib.auth.models import User


def get_employee_from_user(user):
    """
    Get the employee record for a user.

    Args:
        user: Django User instance

    Returns:
        Employee instance if exists, None otherwise
    """
    if user and user.is_authenticated:
        try:
            return user.employee
        except AttributeError:
            return None
    return None


def get_current_employee(request):
    """
    Get the current employee from request.

    Args:
        request: Django HttpRequest instance

    Returns:
        Employee instance if user has one, None otherwise
    """
    return get_employee_from_user(request.user)


# Monkey patch User model to add employee helper methods
def user_has_employee(self):
    """Check if user has an associated employee record."""
    return hasattr(self, 'employee') and self.employee is not None

def user_get_employee(self):
    """Get the employee record for this user."""
    return getattr(self, 'employee', None)

def user_is_employee_manager(self):
    """Check if user's employee is a manager."""
    employee = self.user_get_employee()
    return employee and employee.is_manager() if employee else False

# Add methods to User class
User.add_to_class('has_employee', user_has_employee)
User.add_to_class('get_employee', user_get_employee)
User.add_to_class('is_employee_manager', user_is_employee_manager)