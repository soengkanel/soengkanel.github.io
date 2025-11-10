from django import template

register = template.Library()

@register.filter
def has_role(user, role_name):
    """Check if user has a specific role"""
    if not user or not user.is_authenticated:
        return False
    
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.select_related('role').filter(
            user=user, 
            is_active=True
        ).first()
        
        if role_assignment and role_assignment.role:
            user_role = role_assignment.role.name.lower()
            return user_role == role_name.lower() or user_role == 'admin'
    except:
        pass
    
    return False

@register.filter
def is_manager_or_admin(user):
    """Check if user is manager or admin"""
    if not user or not user.is_authenticated:
        return False
    
    try:
        from user_management.models import UserRoleAssignment
        role_assignment = UserRoleAssignment.objects.select_related('role').filter(
            user=user, 
            is_active=True
        ).first()
        
        if role_assignment and role_assignment.role:
            user_role = role_assignment.role.name.lower()
            return user_role in ['manager', 'admin']
    except:
        pass
    
    return False