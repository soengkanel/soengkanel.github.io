from django.urls import path
from . import views

app_name = 'user_management'

urlpatterns = [
    # Dashboard
    # path('', views.dashboard, name='dashboard'),
    
    # User Management
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/permissions/', views.user_permissions, name='user_permissions'),
    
    # Role Management
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/<int:role_id>/edit/', views.role_edit, name='role_edit'),
    path('roles/<int:role_id>/delete/', views.role_delete, name='role_delete'),
    path('roles/<int:role_id>/permissions/', views.role_permissions, name='role_permissions'),
    
    # Permission Management (AJAX)
    path('api/update-permission/', views.update_permission, name='update_permission'),
    
    # User Profile
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.user_profile_edit, name='user_profile_edit'),
    path('profile/password/', views.password_change, name='password_change'),

    #custome user access control
    #user list
    path('user_access/lists', views.user_access_list,name='user_access_list'),
    #roles route
    path('user_access/roles', views.user_access_role_list,name='user_access_role_list'),
    #modules route
    path('user_access/modules', views.user_access_module_list,name='user_access_module_list'),
] 