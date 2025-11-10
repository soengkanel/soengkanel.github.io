from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect


def user_friendly_permission_required(permission_name, feature_name=None, redirect_url=None):
    """
    Custom permission decorator that shows user-friendly error messages
    instead of raising PermissionDenied.
    
    Args:
        permission_name: The permission required (e.g., 'hr.view_department')
        feature_name: Human-readable name of the feature (e.g., 'HR Departments')
        redirect_url: Optional URL to redirect to instead of showing error page
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            # Check if user has the required permission
            if request.user.has_perm(permission_name):
                return view_func(request, *args, **kwargs)
            
            # User doesn't have permission
            # If redirect_url is provided, redirect with a message
            if redirect_url:
                messages.error(
                    request, 
                    f"You don't have permission to access {feature_name or 'this feature'}. "
                    f"Contact your administrator to request access."
                )
                return HttpResponseRedirect(redirect_url)
            
            # Otherwise, show the user-friendly permission denied page
            # Get user's current role
            current_role = None
            try:
                from user_management.models import UserRoleAssignment
                current_role = UserRoleAssignment.objects.filter(user=request.user, is_active=True).first()
            except Exception:
                pass
            
            # Determine feature name and suggestions
            path = request.path
            suggestions = [
                "Contact your system administrator to request the necessary permissions",
                "Check with your supervisor about getting access to this feature",
                "You may need a different role to access this functionality"
            ]
            
            if not feature_name:
                if "hr" in permission_name:
                    feature_name = "HR Management"
                    suggestions = [
                        "Contact your system administrator to request HR permissions",
                        "You may need the 'HR Manager' or 'HR Staff' role to access this feature",
                        "Check with your supervisor about getting access to HR management tools"
                    ]
                elif "user_management" in permission_name:
                    feature_name = "User Management"
                    suggestions = [
                        "Contact your system administrator to request user management permissions",
                        "You may need the 'Admin' or 'User Manager' role to access this feature",
                        "This feature is typically restricted to system administrators"
                    ]
                elif "audit" in permission_name:
                    feature_name = "Audit Management"
                    suggestions = [
                        "Contact your system administrator to request audit access",
                        "You may need the 'Auditor' or 'Admin' role to access this feature",
                        "Audit logs are typically restricted to authorized personnel only"
                    ]
                else:
                    feature_name = "this feature"
            
            context = {
                'feature_name': feature_name,
                'required_permission': f"have {permission_name} permission",
                'suggestions': suggestions,
                'user': request.user,
                'path': path,
                'current_role': current_role,
            }
            
            return render(request, 'core/permission_denied.html', context, status=403)
            
        return _wrapped_view
    return decorator


def hr_permission_required(permission, feature_name=None):
    """
    Convenience decorator for HR permissions with specific messaging
    """
    if not feature_name:
        feature_name = "HR Management"
    
    return user_friendly_permission_required(
        permission_name=permission,
        feature_name=feature_name
    )


def admin_permission_required(permission, feature_name=None):
    """
    Convenience decorator for admin permissions with specific messaging
    """
    if not feature_name:
        feature_name = "Administrative Features"
    
    return user_friendly_permission_required(
        permission_name=permission,
        feature_name=feature_name
    )


def manager_or_admin_required(feature_name="Settings"):
    """
    Decorator that allows access only to users with Manager or Admin roles.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            from user_management.models import UserRoleAssignment
            from django.core.exceptions import PermissionDenied
            
            # Superusers always have access
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if user has Manager or Admin role
            try:
                role_assignment = UserRoleAssignment.objects.get(
                    user=request.user, 
                    is_active=True
                )
                if role_assignment.role.name in ["Manager", "Admin"]:
                    return view_func(request, *args, **kwargs)
            except UserRoleAssignment.DoesNotExist:
                pass
            
            # User doesn't have permission
            context = {
                'feature_name': feature_name,
                'required_permission': "have Manager or Admin role",
                'suggestions': [
                    "Contact your system administrator to request Manager or Admin role",
                    "This feature is restricted to Managers and Administrators only",
                    "Check with your supervisor about getting access to this feature"
                ],
                'user': request.user,
                'path': request.path,
            }
            
            return render(request, 'core/permission_denied.html', context, status=403)
            
        return _wrapped_view
    return decorator 