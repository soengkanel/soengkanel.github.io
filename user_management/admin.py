from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Role, UserRoleAssignment, PermissionSet

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active', 'user_count', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']
    readonly_fields = ['created_at', 'updated_at']
    
    def user_count(self, obj):
        return obj.assignments.count()
    user_count.short_description = 'Users'

@admin.register(UserRoleAssignment)
class UserRoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'assigned_by', 'assigned_at']
    list_filter = ['is_active', 'role', 'assigned_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['assigned_at']
    # autocomplete_fields disabled for multi-tenant compatibility
    # autocomplete_fields = ['user', 'assigned_by']
    
    fieldsets = (
        ('User Assignment', {
            'fields': ('user', 'role', 'is_active')
        }),
        ('Profile Information', {
            'fields': ('profile_photo', 'notes')
        }),
        ('System Information', {
            'fields': ('assigned_by', 'assigned_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(PermissionSet)
class PermissionSetAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_system_set', 'permission_count', 'created_at']
    list_filter = ['is_system_set', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['permissions']
    readonly_fields = ['created_at', 'updated_at']
    
    def permission_count(self, obj):
        return obj.permissions.count()
    permission_count.short_description = 'Permissions'

# Inline for UserRoleAssignment in User admin
class UserRoleAssignmentInline(admin.StackedInline):
    model = UserRoleAssignment
    fk_name = 'user'  # Specify which ForeignKey to use
    can_delete = True
    max_num = 1
    extra = 0
    fields = ['role', 'is_active', 'notes', 'assigned_by']
    readonly_fields = ['assigned_at']
    
    def get_formset(self, request, obj=None, **kwargs):
        """Override to ensure role is required"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # Set default role for new instances
        def get_default_role():
            from .models import Role
            return Role.objects.filter(name='User').first() or Role.objects.first()
        
        original_init = formset.form.__init__
        
        def __init__(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            if not self.instance.pk and 'role' in self.fields:
                self.fields['role'].initial = get_default_role()
                self.fields['role'].required = True
        
        formset.form.__init__ = __init__
        return formset

# Extend the existing User admin for multi-tenant environment
class UserAdmin(BaseUserAdmin):
    inlines = BaseUserAdmin.inlines + (UserRoleAssignmentInline,)

# Re-register UserAdmin (handling multi-tenant scenarios)
try:
    admin.site.unregister(User)  # First unregister the default User admin
except admin.sites.NotRegistered:
    pass  # User wasn't registered, which is fine

# Now register our custom User admin
admin.site.register(User, UserAdmin)
