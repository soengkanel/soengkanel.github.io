from rest_framework import permissions


class CanUpdateOwnCompany(permissions.BasePermission):
    """
    Permission that allows authenticated users to update their own tenant's company information.
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow all authenticated users to read/update their own company
        return True

    def has_object_permission(self, request, view, obj):
        # Allow if user is authenticated (object-level permission for company updates)
        return request.user and request.user.is_authenticated


class CanManageGroups(permissions.BasePermission):
    """
    Permission for group management operations.

    - Read operations: Any authenticated user
    - Create/Update operations: Staff users
    - Delete operations: Superusers only (due to cascade deletion impact)
    """

    def has_permission(self, request, view):
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Allow read operations for all authenticated users
        if request.method in permissions.READONLY_METHODS:
            return True

        # Delete operations require superuser
        if view.action == 'destroy':
            return request.user.is_superuser

        # Create and update operations require staff status
        if view.action in ['create', 'update', 'partial_update']:
            return request.user.is_staff

        # Allow cascade_info action for all authenticated users
        if hasattr(view, 'action') and view.action == 'cascade_info':
            return True

        return request.user.is_staff

    def has_object_permission(self, request, view, obj):
        """Object-level permissions for group operations"""
        # Must be authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Read operations allowed for authenticated users
        if request.method in permissions.READONLY_METHODS:
            return True

        # Delete operations require superuser
        if view.action == 'destroy':
            return request.user.is_superuser

        # Other operations require staff status
        return request.user.is_staff