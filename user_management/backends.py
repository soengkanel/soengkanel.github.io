from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Permission
from user_management.models import UserRoleAssignment


class RoleBasedPermissionBackend(BaseBackend):
    """
    Custom authentication backend that integrates our role system
    with Django's permission checking system.
    
    This allows has_perm() to work with role-based permissions.
    """
    
    def authenticate(self, request, **kwargs):
        # This backend only handles permissions, not authentication
        return None
    
    def has_perm(self, user_obj, perm, obj=None):
        """
        Check if user has permission through their assigned role.
        
        Args:
            user_obj: The user to check permissions for
            perm: Permission string in format 'app_label.permission_codename'
            obj: Object instance (not used in our case)
        
        Returns:
            bool: True if user has permission through role, False otherwise
        """
        if not user_obj.is_active:
            return False
        
        # Superusers have all permissions
        if user_obj.is_superuser:
            return True
        
        try:
            # Get user's active role assignment
            role_assignment = UserRoleAssignment.objects.get(
                user=user_obj, 
                is_active=True
            )
            
            if not role_assignment.role:
                return False
            
            # Parse permission string (e.g., 'hr.view_department')
            if '.' not in perm:
                return False
            
            app_label, codename = perm.split('.', 1)
            
            # Check if role has this permission
            return role_assignment.role.permissions.filter(
                content_type__app_label=app_label,
                codename=codename
            ).exists()
            
        except UserRoleAssignment.DoesNotExist:

            
            pass
            # No role assignment, no permissions
            return False
        except Exception:
            # Any other error, deny permission
            return False
    
    def has_module_perms(self, user_obj, app_label):
        """
        Check if user has any permissions for the given app.
        
        Args:
            user_obj: The user to check permissions for
            app_label: App label (e.g., 'hr', 'zone')
        
        Returns:
            bool: True if user has any permission in this app
        """
        if not user_obj.is_active:
            return False
        
        # Superusers have all permissions
        if user_obj.is_superuser:
            return True
        
        try:
            # Get user's active role assignment
            role_assignment = UserRoleAssignment.objects.get(
                user=user_obj, 
                is_active=True
            )
            
            if not role_assignment.role:
                return False
            
            # Check if role has any permissions for this app
            return role_assignment.role.permissions.filter(
                content_type__app_label=app_label
            ).exists()
            
        except UserRoleAssignment.DoesNotExist:

            
            pass
            return False
        except Exception:
            return False
    
    def get_user_permissions(self, user_obj, obj=None):
        """
        Get all permissions for the user through their role.
        
        Args:
            user_obj: The user to get permissions for
            obj: Object instance (not used)
        
        Returns:
            set: Set of permission strings
        """
        if not user_obj.is_active:
            return set()
        
        try:
            # Get user's active role assignment
            role_assignment = UserRoleAssignment.objects.get(
                user=user_obj, 
                is_active=True
            )
            
            if not role_assignment.role:
                return set()
            
            # Get all permissions from role
            permissions = role_assignment.role.permissions.select_related('content_type')
            
            # Convert to permission strings
            perm_set = set()
            for perm in permissions:
                perm_string = f"{perm.content_type.app_label}.{perm.codename}"
                perm_set.add(perm_string)
            
            return perm_set
            
        except UserRoleAssignment.DoesNotExist:

            
            pass
            return set()
        except Exception:
            return set()
    
    def get_group_permissions(self, user_obj, obj=None):
        """
        We don't use Django groups, so return empty set.
        """
        return set()
    
    def get_all_permissions(self, user_obj, obj=None):
        """
        Get all permissions for the user (role + direct permissions).
        """
        if not user_obj.is_active:
            return set()
        
        # Get role permissions
        role_perms = self.get_user_permissions(user_obj, obj)
        
        # Get direct user permissions
        direct_perms = set()
        for perm in user_obj.user_permissions.select_related('content_type'):
            perm_string = f"{perm.content_type.app_label}.{perm.codename}"
            direct_perms.add(perm_string)
        
        return role_perms | direct_perms 