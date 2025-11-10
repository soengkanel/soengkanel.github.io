from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings


# TODO: Custom User model will be re-enabled after migrating all FK references across the codebase
# Currently using Django's built-in User model to avoid conflicts


def validate_image_file_extension(value):
    """Validate that the uploaded file is an image."""
    import os
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.enc']  # Include .enc for encrypted files
    if not ext in valid_extensions:
        raise ValidationError(_('Unsupported file extension. Allowed formats: JPG, PNG, GIF, BMP'))

def validate_image_file_size(value):
    """File size validation removed - no size limits."""
    pass

class Role(models.Model):
    """Custom roles for the system"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Many-to-many relationship with permissions
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='custom_roles',
        help_text='Specific permissions for this role.'
    )
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def get_permission_matrix(self):
        """Get permissions organized by content type for matrix display"""
        permissions_by_model = {}
        
        # Get all relevant content types from the system
        content_types = ContentType.objects.filter(
            app_label__in=['hr', 'zone', 'vip', 'cards', 'billing', 'payments', 'document_tracking']
        ).select_related()
        
        for ct in content_types:
            model_name = ct.model_class().__name__ if ct.model_class() else ct.model
            permissions_by_model[model_name] = {
                'content_type': ct,
                'add': False,
                'view': False,
                'change': False,
                'delete': False,
            }
            
            # Check which permissions this role has for each model
            for perm in self.permissions.filter(content_type=ct):
                if perm.codename.startswith('add_'):
                    permissions_by_model[model_name]['add'] = True
                elif perm.codename.startswith('view_'):
                    permissions_by_model[model_name]['view'] = True
                elif perm.codename.startswith('change_'):
                    permissions_by_model[model_name]['change'] = True
                elif perm.codename.startswith('delete_'):
                    permissions_by_model[model_name]['delete'] = True
        
        return permissions_by_model


class UserRoleAssignment(models.Model):
    """Assignment of roles to users - extends the existing UserProfile system"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='role_assignments')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='assignments', null=True, blank=True)
    assigned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_roles')
    
    # Profile photo
    profile_photo = models.ImageField(
        upload_to='user_profile_photos/', 
        blank=True, 
        null=True,
        validators=[validate_image_file_extension, validate_image_file_size],
        verbose_name='Profile Photo',
        help_text='Upload your profile photo (JPG, PNG, GIF, BMP formats supported)'
    )
    
    # Additional management fields
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Notes about this role assignment")
    
    class Meta:
        ordering = ['user__username']
        verbose_name = "User Role Assignment"
        verbose_name_plural = "User Role Assignments"
        
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.role.name if self.role else 'No Role'}"
    
    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username
    
    def get_all_permissions(self):
        """Get all permissions from user's role and direct permissions"""
        all_perms = set()
        
        # Add permissions from role
        if self.role:
            all_perms.update(self.role.permissions.all())
        
        # Add direct user permissions
        all_perms.update(self.user.user_permissions.all())
        
        return list(all_perms)
    
    @property
    def profile_photo_url(self):
        """Return profile photo URL or default avatar"""
        if self.profile_photo and hasattr(self.profile_photo, 'url'):
            try:
                # Check if the file actually exists
                import os
                from django.conf import settings
                file_path = os.path.join(settings.MEDIA_ROOT, str(self.profile_photo))
                if os.path.exists(file_path):
                    return self.profile_photo.url
            except:
                pass
        
        # Return default avatar (corrected to .svg)
        return '/static/images/default-avatar.svg'
    
    @property
    def has_profile_photo(self):
        """Check if user has a profile photo"""
        return bool(self.profile_photo)
    
    def save(self, *args, **kwargs):
        # Set default role if none assigned
        if not self.role:
            try:
                default_role = Role.objects.filter(name='User').first()
                if not default_role:
                    # Create a basic User role if none exist
                    default_role = Role.objects.create(
                        name='User',
                        description='Basic user access'
                    )
                self.role = default_role
            except:
                pass  # If role creation fails, continue without role
        
        super().save(*args, **kwargs)


class PermissionSet(models.Model):
    """Predefined sets of permissions for quick role assignment"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='permission_sets'
    )
    is_system_set = models.BooleanField(default=False, help_text="System-defined permission set")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        
    def __str__(self):
        return self.name
