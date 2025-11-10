from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q
from django.contrib.auth.models import User
import json

from .models import PermissionSet, Role, UserRoleAssignment
from .forms import UserForm, RoleForm, UserRoleAssignmentForm, UserProfileForm, UserBasicInfoForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required
def dashboard(request):
    """User management dashboard"""
    users_count = User.objects.count()
    roles_count = Role.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    
    recent_users = UserRoleAssignment.objects.select_related('user', 'role').order_by('-assigned_at')[:5]
    
    context = {
        'users_count': users_count,
        'roles_count': roles_count,
        'active_users': active_users,
        'recent_users': recent_users,
    }
    return render(request, 'user_management/dashboard.html', context)

# User Management Views
@login_required
def user_list(request):
    """List all users with their roles - includes search, pagination, and sorting"""
    # Get all users and ensure they have role assignments
    
    all_users = User.objects.all()
    user_assignments = []
    
    for user in all_users:
        # Get or create role assignment for each user
        try:
            default_role = Role.objects.filter(name='User').first() or Role.objects.first()
            if not default_role:
                # If no roles exist, create a basic User role
                default_role = Role.objects.create(
                    name='User',
                    description='Basic user access'
                )
            
            assignment, created = UserRoleAssignment.objects.get_or_create(
                user=user,
                defaults={
                    'assigned_by': request.user,
                    'is_active': user.is_active,
                    'role': default_role
                }
            )
            user_assignments.append(assignment)
        except Exception as e:
            # Log error but continue processing other users
            messages.error(request, f'Error processing user {user.username}: {str(e)}')
            continue
    
    # Convert to QuerySet for further filtering and ordering
    user_assignments_qs = UserRoleAssignment.objects.select_related('user', 'role', 'assigned_by').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        user_assignments_qs = user_assignments_qs.filter(
            Q(user__username__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(role__name__icontains=search_query)
        )
    
    # Role filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        user_assignments_qs = user_assignments_qs.filter(role_id=role_filter)
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        user_assignments_qs = user_assignments_qs.filter(user__is_active=True, is_active=True)
    elif status_filter == 'inactive':
        user_assignments_qs = user_assignments_qs.filter(Q(user__is_active=False) | Q(is_active=False))
    
    # Sorting
    sort_by = request.GET.get('sort', 'user__username')
    order = request.GET.get('order', 'asc')
    
    valid_sort_fields = ['user__username', 'user__first_name', 'user__last_name', 
                        'user__email', 'role__name', 'user__is_active', 
                        'is_active', 'assigned_at', 'user__date_joined']
    
    if sort_by in valid_sort_fields:
        if order == 'desc':
            sort_by = f'-{sort_by}'
        user_assignments_qs = user_assignments_qs.order_by(sort_by)
    else:
        user_assignments_qs = user_assignments_qs.order_by('user__username')
    
    # Pagination
    per_page = request.GET.get('per_page', '20')
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 25, 50, 100, 200]:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20
    
    paginator = Paginator(user_assignments_qs, per_page)
    page = request.GET.get('page')
    
    try:
        users_page = paginator.page(page)
    except PageNotAnInteger:
        users_page = paginator.page(1)
    except EmptyPage:
        users_page = paginator.page(paginator.num_pages)
    
    # Get all roles for filter dropdown
    all_roles = Role.objects.all().order_by('name')
    
    # Ensure there's at least one role available
    if not all_roles.exists():
        # Create a default User role if no roles exist
        default_role = Role.objects.create(
            name='User',
            description='Basic user access'
        )
        all_roles = Role.objects.all().order_by('name')
    
    # Calculate stats
    total_count = paginator.count
    active_count = UserRoleAssignment.objects.filter(user__is_active=True, is_active=True).count()
    roles_count = Role.objects.count()
    
    context = {
        'users': users_page,
        'search_query': search_query,
        'role_filter': role_filter,
        'status_filter': status_filter,
        'current_sort': request.GET.get('sort', 'user__username'),
        'current_order': request.GET.get('order', 'asc'),
        'total_count': total_count,
        'per_page': per_page,
        'active_count': active_count,
        'roles_count': roles_count,
        'all_roles': all_roles,
    }
    
    return render(request, 'user_management/user_list.html', context)

@login_required
@permission_required('auth.add_user', raise_exception=True)
def user_create(request):
    """Create new user"""
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        assignment_form = UserRoleAssignmentForm(request.POST)
        
        if user_form.is_valid() and assignment_form.is_valid():
            try:
                user = user_form.save()
                role_assignment = assignment_form.save(commit=False)
                role_assignment.user = user
                role_assignment.assigned_by = request.user
                role_assignment.save()
                
                messages.success(request, f'User "{user.username}" created successfully! Full name: {user.get_full_name()}')
                return redirect('user_management:user_list')
            except Exception as e:
                messages.error(request, f'Error creating user: {str(e)}')
        else:
            # Show validation errors
            error_messages = []
            for field, errors in user_form.errors.items():
                for error in errors:
                    error_messages.append(f"{field.replace('_', ' ').title()}: {error}")
            for field, errors in assignment_form.errors.items():
                for error in errors:
                    error_messages.append(f"{field.replace('_', ' ').title()}: {error}")
            
            if error_messages:
                messages.error(request, 'Please fix the following errors: ' + ', '.join(error_messages))
    else:
        user_form = UserForm()
        assignment_form = UserRoleAssignmentForm()
    
    context = {
        'user_form': user_form,
        'assignment_form': assignment_form,
        'title': 'Create User'
    }
    return render(request, 'user_management/user_form.html', context)

@login_required
@permission_required('auth.change_user', raise_exception=True)
def user_edit(request, user_id):
    """Edit existing user"""
    edit_user = get_object_or_404(User, id=user_id)
    default_role = Role.objects.filter(name='User').first() or Role.objects.first()
    if not default_role:
        # If no roles exist, create a basic User role
        default_role = Role.objects.create(
            name='User',
            description='Basic user access'
        )
    
    assignment, created = UserRoleAssignment.objects.get_or_create(
        user=edit_user,
        defaults={
            'assigned_by': request.user, 
            'is_active': edit_user.is_active,
            'role': default_role
        }
    )
    
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=edit_user)
        assignment_form = UserRoleAssignmentForm(request.POST, instance=assignment)
        
        if user_form.is_valid() and assignment_form.is_valid():
            user_form.save()
            assignment_form.save()
            
            messages.success(request, f'User {edit_user.username} updated successfully!')
            return redirect('user_management:user_list')
    else:
        user_form = UserForm(instance=edit_user)
        assignment_form = UserRoleAssignmentForm(instance=assignment)
    
    context = {
        'user_form': user_form,
        'assignment_form': assignment_form,
        'title': 'Edit User',
        'edit_user': edit_user,
        'assignment':assignment
    }
    return render(request, 'user_management/user_form.html', context)

@login_required
@permission_required('auth.delete_user', raise_exception=True)
def user_delete(request, user_id):
    """Delete user"""
    user = get_object_or_404(User, id=user_id)
    default_role = Role.objects.filter(name='User').first() or Role.objects.first()
    if not default_role:
        # If no roles exist, create a basic User role
        default_role = Role.objects.create(
            name='User',
            description='Basic user access'
        )
    
    user_assignment, created = UserRoleAssignment.objects.get_or_create(
        user=user,
        defaults={
            'assigned_by': request.user, 
            'is_active': user.is_active,
            'role': default_role
        }
    )
    
    if request.method == 'POST':
        username = user.username
        user.delete()  # This will also delete the UserRoleAssignment due to CASCADE
        messages.success(request, f'User {username} deleted successfully!')
        return redirect('user_management:user_list')
    
    return render(request, 'user_management/user_delete.html', {'user_assignment': user_assignment})

# Role Management Views
@login_required
def role_list(request):
    """List all roles"""
    user = request.user
    if user.is_superuser:
        roles = Role.objects.prefetch_related('assignments', 'permissions').all()
    else:
        roles = Role.objects.prefetch_related('assignments', 'permissions').filter(name="User")
    
    return render(request, 'user_management/role_list.html', {'roles': roles})

@login_required
@permission_required('user_management.add_role', raise_exception=True)
def role_create(request):
    """Create new role"""
    if request.method == 'POST':
        form = RoleForm(request.POST)
        if form.is_valid():
            role = form.save()
            messages.success(request, f'Role {role.name} created successfully!')
            return redirect('user_management:role_permissions', role_id=role.id)
    else:
        form = RoleForm()
    
    context = {
        'form': form,
        'title': 'Create Role'
    }
    return render(request, 'user_management/role_form.html', context)

@login_required
@permission_required('user_management.change_role', raise_exception=True)
def role_edit(request, role_id):
    """Edit existing role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            messages.success(request, f'Role {role.name} updated successfully!')
            return redirect('user_management:role_list')
    else:
        form = RoleForm(instance=role)
    
    context = {
        'form': form,
        'title': 'Edit Role',
        'role': role
    }
    return render(request, 'user_management/role_form.html', context)

@login_required
@permission_required('user_management.delete_role', raise_exception=True)
def role_delete(request, role_id):
    """Delete role"""
    role = get_object_or_404(Role, id=role_id)
    
    if request.method == 'POST':
        role_name = role.name
        role.delete()
        messages.success(request, f'Role {role_name} deleted successfully!')
        return redirect('user_management:role_list')
    
    return render(request, 'user_management/role_delete.html', {'role': role})

# Permission Management Views
@login_required
def role_permissions(request, role_id):
    """Manage role permissions with matrix table"""
    role = get_object_or_404(Role, id=role_id)
    
    # Get all relevant content types and their permissions
    content_types = ContentType.objects.filter(
        app_label__in=['hr', 'zone', 'vip', 'cards', 'billing', 'payments', 'document_tracking', 'audit_management', 'user_management', 'user_access_control']
    ).order_by('app_label', 'model')

    if request.user.is_superuser:
        modules = PermissionSet.objects.all().order_by('description')
    else:
        modules = PermissionSet.objects.exclude(name = "Settings").order_by('description')
    ## Add custom permissions
    # content_types = ContentType.objects.filter(
    #     app_label__in=['operations', 'people']
    # ).order_by('app_label', 'model')


    permission_matrix = []

    # for ct in content_types:
    #     pass
    for ct in modules: 
        model_name = ct.name
        app_name = ct.description
        
        # Get all CRUD permissions for this content type
        permissions = Permission.objects.filter(permission_sets=ct).order_by('codename')
        
        perm_dict = {
            'content_type': ct,
            'model_name': model_name,
            'app_name': app_name,
            'add': None,
            'view': None,
            'change': None,
            'delete': None,
        }
        
        # Map permissions to CRUD operations
        for perm in permissions:
            if perm.codename.startswith('add_'):
                perm_dict['add'] = perm
            elif perm.codename.startswith('view_'):
                perm_dict['view'] = perm
            elif perm.codename.startswith('change_'):
                perm_dict['change'] = perm
            elif perm.codename.startswith('delete_'):
                perm_dict['delete'] = perm
        
        # Check which permissions are currently assigned to the role
        role_permissions = set(role.permissions.all())
        perm_dict['has_add'] = perm_dict['add'] in role_permissions if perm_dict['add'] else False
        perm_dict['has_view'] = perm_dict['view'] in role_permissions if perm_dict['view'] else False
        perm_dict['has_change'] = perm_dict['change'] in role_permissions if perm_dict['change'] else False
        perm_dict['has_delete'] = perm_dict['delete'] in role_permissions if perm_dict['delete'] else False
        
        permission_matrix.append(perm_dict)
    
    context = {
        'role': role,
        'permission_matrix': permission_matrix,
    }
    return render(request, 'user_management/role_permissions.html', context)

@require_POST
@csrf_exempt
@login_required
def update_permission(request):
    """AJAX endpoint to update role permissions"""
    try:
        data = json.loads(request.body)
        role_id = data.get('role_id')
        permission_id = data.get('permission_id')
        is_checked = data.get('is_checked')
        
        role = get_object_or_404(Role, id=role_id)
        permission = get_object_or_404(Permission, id=permission_id)
        
        if is_checked:
            role.permissions.add(permission)
        else:
            role.permissions.remove(permission)
        
        return JsonResponse({
            'success': True,
            'message': f'Permission {"added to" if is_checked else "removed from"} {role.name}'
        })
        
    except Exception as e:

        
        pass
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

@login_required
def user_permissions(request, user_id):
    """View user's effective permissions"""
    user = get_object_or_404(User, id=user_id)
    default_role = Role.objects.filter(name='User').first() or Role.objects.first()
    if not default_role:
        # If no roles exist, create a basic User role
        default_role = Role.objects.create(
            name='User',
            description='Basic user access'
        )
    
    user_assignment, created = UserRoleAssignment.objects.get_or_create(
        user=user,
        defaults={
            'assigned_by': request.user, 
            'is_active': user.is_active,
            'role': default_role
        }
    )
    
    # Handle permissions based on user type
    permission_matrix = []
    permission_source = "none"
    
    if user.is_superuser:
        # For superusers, show ALL permissions organized by model
        # Get all relevant content types
        content_types = ContentType.objects.filter(
            app_label__in=['hr', 'zone', 'vip', 'cards', 'billing', 'payments', 'document_tracking', 'audit_management', 'user_management']
        ).order_by('app_label', 'model')
        
        modules = PermissionSet.objects.all().order_by('description')

        for ct in modules:
            # model_name = ct.model_class().__name__ if ct.model_class() else ct.model.title()
            # app_name = ct.app_label.replace('_', ' ').title()

            model_name = ct.name
            app_name = ct.description
            
            
            # For superusers, they have ALL permissions
            perm_dict = {
                'model_name': model_name,
                'app_name': app_name,
                'has_add': True,
                'has_view': True,
                'has_change': True,
                'has_delete': True,
            }


            permission_matrix.append(perm_dict)
        
        permission_source = "superuser"
        
    elif user_assignment.role:
        # Regular users get permissions from their role
        permissions = user_assignment.role.permissions.all()
        
        # Organize permissions by model for matrix view
        content_types = ContentType.objects.filter(
            permission__in=permissions
        ).distinct().order_by('app_label', 'model')

        modules = PermissionSet.objects.all().order_by('description')
        
        for ct in modules:
            # model_name = ct.model_class().__name__ if ct.model_class() else ct.model.title()
            # app_name = ct.app_label.replace('_', ' ').title()
            
            model_name = ct.name
            app_name = ct.description
            
            # Get all CRUD permissions for this content type
            permissions = Permission.objects.filter(permission_sets=ct).order_by('codename')
            # Get permissions for this content type
            # ct_permissions = permissions.filter(content_type=ct)
            
            perm_dict = {
                'content_type': ct,
                'model_name': model_name,
                'app_name': app_name,
                'add': None,
                'view': None,
                'change': None,
                'delete': None,
            }
        
            # Map permissions to CRUD operations
            for perm in permissions:
                if perm.codename.startswith('add_'):
                    perm_dict['add'] = perm
                elif perm.codename.startswith('view_'):
                    perm_dict['view'] = perm
                elif perm.codename.startswith('change_'):
                    perm_dict['change'] = perm
                elif perm.codename.startswith('delete_'):
                    perm_dict['delete'] = perm
                
                # Check which permissions are currently assigned to the role
                role_permissions = set(user_assignment.role.permissions.all())
                perm_dict['has_add'] = perm_dict['add'] in role_permissions if perm_dict['add'] else False
                perm_dict['has_view'] = perm_dict['view'] in role_permissions if perm_dict['view'] else False
                perm_dict['has_change'] = perm_dict['change'] in role_permissions if perm_dict['change'] else False
                perm_dict['has_delete'] = perm_dict['delete'] in role_permissions if perm_dict['delete'] else False
                

            permission_matrix.append(perm_dict)
        
        permission_source = "role"
    
    context = {
        'user_assignment': user_assignment,
        'permissions': permission_matrix,
        'total_permissions': len(permission_matrix),
        'permission_source': permission_source,
        'is_superuser': user.is_superuser,
    }
    return render(request, 'user_management/user_permissions.html', context)

@login_required
def user_profile(request):
    """User profile page - Redirect to comprehensive employee portal profile"""
    return redirect('employee_portal:profile')

@login_required
def user_profile_edit(request):
    """Edit user profile"""
    user = request.user
    
    # Get or create role assignment
    default_role = Role.objects.filter(name='User').first() or Role.objects.first()
    if not default_role:
        # If no roles exist, create a basic User role
        default_role = Role.objects.create(
            name='User',
            description='Basic user access'
        )
    
    role_assignment, created = UserRoleAssignment.objects.get_or_create(
        user=user,
        defaults={
            'assigned_by': user, 
            'is_active': user.is_active,
            'role': default_role
        }
    )
    
    if request.method == 'POST':
        user_form = UserBasicInfoForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=role_assignment)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('user_management:user_profile')
    else:
        user_form = UserBasicInfoForm(instance=user)
        profile_form = UserProfileForm(instance=role_assignment)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
        'role_assignment': role_assignment,
    }
    return render(request, 'user_management/user_profile_edit.html', context)


## custome user access control
##user list
@login_required
def user_access_list(request):
    content_types = ContentType.objects.filter(model='user_access_control').all()
    return render(request, 'user_access_control/users/user_lists.html', {'content_types':content_types})

##role
@login_required
def user_access_role_list(request):
    
    return render(request, 'user_access_control/roles/role_lists.html')

##modul
@login_required
def user_access_module_list(request):
    modules = []
    modules.append({
        'name':'Entry',
        'slug':'entry',
        'desc':'View system overview and stats',
        'permissions':[
            {
            'name':'view',
            'allow':True
            },
             {
            'name':'create',
            'allow':True
            },
             {
            'name':'edit',
            'allow':True
            },
             {
            'name':'delete',
            'allow':True
            }
            ]
    })

    modules.extend([
        {
        'name':'Probation',
        'slug':'probation',
        'desc':'View system overview and stats',
        'permissions':[
            {
            'name':'view',
            'allow':True
            },
             {
            'name':'create',
            'allow':True
            },
             {
            'name':'edit',
            'allow':True
            },
             {
            'name':'delete',
            'allow':True
            }
            ]
    },
    {
        'name':'IDCards',
        'slug':'idcards',
        'desc':'View system overview and stats',
        'permissions':[
            {
            'name':'view',
            'allow':True
            },
             {
            'name':'create',
            'allow':True
            },
             {
            'name':'edit',
            'allow':True
            },
             {
            'name':'delete',
            'allow':True
            }
            ]
    },
    {
        'name':'Documents',
        'slug':'documents',
        'desc':'View system overview and stats',
        'permissions':[
            {
            'name':'view',
            'allow':True
            },
             {
            'name':'create',
            'allow':True
            },
             {
            'name':'edit',
            'allow':True
            },
             {
            'name':'delete',
            'allow':True
            }
            ]
    },
    {
        'name':'Billing',
        'slug':'billing',
        'desc':'View system overview and stats',
        'permissions':[
            {
            'name':'view',
            'allow':True
            },
             {
            'name':'create',
            'allow':True
            },
             {
            'name':'edit',
            'allow':True
            },
             {
            'name':'delete',
            'allow':True
            }
            ]
    },
     {
        'name':'E-Form',
        'slug':'e-form',
        'desc':'View system overview and stats',
        'permissions':[
            {
            'name':'view',
            'allow':True
            },
             {
            'name':'create',
            'allow':True
            },
             {
            'name':'edit',
            'allow':True
            },
             {
            'name':'delete',
            'allow':True
            }
            ]
    }
    ])
    context = {
        'modules':modules
    }
    return render(request, 'user_access_control/modules/module_lists.html', context)


@login_required
def password_change(request):
    """Custom password change view with simple, compact form"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important! Keep user logged in
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('user_management:user_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)
    
    context = {
        'form': form,
        'title': 'Change Password'
    }
    return render(request, 'user_management/password_change.html', context)
