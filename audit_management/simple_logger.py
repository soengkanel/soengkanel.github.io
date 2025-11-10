from django.utils import timezone
from .models import SimpleAuditLog


class SimpleAuditLogger:
    """Simple audit logger focusing on what/when/who"""
    
    @staticmethod
    def log_action(user, action, model_name, object_id=None, object_name="",
                   description="", old_values=None, new_values=None, request=None):
        """
        Log a simple audit action
        
        Args:
            user: User who performed the action
            action: Action performed ('create', 'update', 'delete', 'login', 'logout')
            model_name: Name of the model/resource affected
            object_id: ID of the specific object
            object_name: Human readable name of the object
            description: Simple description of what happened
            old_values: Old values (for updates, as simple string)
            new_values: New values (for updates, as simple string)
            request: Django request object for IP address
        """
        # Try to get user from request if not provided
        if not user and request and hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
        
        ip_address = None
        if request:
            # Get IP address from request
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(',')[0].strip()
            else:
                ip_address = request.META.get('REMOTE_ADDR')
        
        return SimpleAuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=str(object_id) if object_id else None,
            object_name=object_name,
            description=description,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
        )
    
    @staticmethod
    def log_create(user, model_name, obj, request=None):
        """Log object creation"""
        return SimpleAuditLogger.log_action(
            user=user,
            action='create',
            model_name=model_name,
            object_id=obj.pk,
            object_name=str(obj),
            description=f"Created new {model_name}",
            request=request
        )
    
    @staticmethod
    def log_update(user, model_name, obj, changes=None, request=None):
        """Log object update"""
        if changes:
            old_vals = ", ".join([f"{k}: {v['old']}" for k, v in changes.items()])
            new_vals = ", ".join([f"{k}: {v['new']}" for k, v in changes.items()])
            description = f"Updated {model_name} - Changed: {', '.join(changes.keys())}"
        else:
            old_vals = None
            new_vals = None
            description = f"Updated {model_name}"
        
        return SimpleAuditLogger.log_action(
            user=user,
            action='update',
            model_name=model_name,
            object_id=obj.pk,
            object_name=str(obj),
            description=description,
            old_values=old_vals,
            new_values=new_vals,
            request=request
        )
    
    @staticmethod
    def log_delete(user, model_name, obj, request=None):
        """Log object deletion"""
        return SimpleAuditLogger.log_action(
            user=user,
            action='delete',
            model_name=model_name,
            object_id=obj.pk,
            object_name=str(obj),
            description=f"Deleted {model_name}",
            request=request
        )
    
    @staticmethod
    def log_login(user, request=None):
        """Log user login"""
        return SimpleAuditLogger.log_action(
            user=user,
            action='login',
            model_name='User Session',
            description=f"User logged in",
            request=request
        )
    
    @staticmethod
    def log_logout(user, request=None):
        """Log user logout"""
        return SimpleAuditLogger.log_action(
            user=user,
            action='logout',
            model_name='User Session',
            description=f"User logged out",
            request=request
        )