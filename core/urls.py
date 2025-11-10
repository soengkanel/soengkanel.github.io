from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView
from django.views.static import serve
from django.http import HttpResponse, FileResponse
from . import views
from . import views_tenant
import os

# Custom admin logout view that allows GET requests
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages

def admin_logout_view(request):
    """
    Enhanced logout view with improved security measures
    - Clears all session data
    - Invalidates session
    - Redirects to landing page
    """
    # Store user info for logging before logout
    user_info = f"User {request.user.username}" if request.user.is_authenticated else "Anonymous user"
    
    # Clear all session data
    request.session.flush()  # This deletes the session data and regenerates session key
    
    # Perform Django logout (clears authentication)
    logout(request)
    
    # Add success message after logout
    messages.success(request, 'You have been successfully logged out for security.')
    
    # Security audit logging removed
    
    return redirect('/')


def serve_excel_template(request):
    """Serve the worker Excel template file."""
    template_path = os.path.join(settings.BASE_DIR, 'worker_template_minimal.xlsx')
    if os.path.exists(template_path):
        response = FileResponse(
            open(template_path, 'rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="worker_template.xlsx"'
        return response
    else:
        return HttpResponse('Worker template not found', status=404)

# Customize Django Admin Site Titles
admin.site.site_header = "LYP Administration"
admin.site.site_title = "LYP Admin Portal"
admin.site.index_title = "Welcome to LYP Administration Portal"

urlpatterns = [
    # Custom admin logout that accepts GET requests
    path('admin/logout/', admin_logout_view, name='admin_logout'),
    # Override the default accounts logout to use our custom view
    path('accounts/logout/', admin_logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication URLs
    path('zone/', include('zone.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('hr/', include('hr.urls')),
    path('attendance/', include('attendance.urls')),
    path('cards/', include('cards.urls')),
    path('billing/', include('billing.urls')),
    path('payments/', include('payments.urls')),
    path('sinosecu/', include('sinosecu.urls')),
    path('documents/', include('document_tracking.urls')),
    path('eform/', include('eform.urls')),
    path('audit/', include('audit_management.urls')),  # Audit management URLs
    path('user-management/', include('user_management.urls')),  # User management URLs
    path('company/', include('company.urls')),  # Company management URLs
    path('project/', include('project.urls')),  # Project management URLs
    path('api/project/', include('project.api_urls')),  # Project API URLs
    path('payroll/', include('payroll.urls')),  # Payroll management URLs
    path('leave/', include('leave.urls')),  # Leave management URLs
    path('recruitment/', include('recruitment.urls')),  # Recruitment management URLs
    path('performance/', include('performance.urls')),  # Performance management URLs
    path('training/', include('training.urls')),  # Training & Development URLs
    path('policies/', include('policies.urls')),  # Policy management URLs
    path('employee/', include('employee_portal.urls')),  # Employee self-service portal
    path('suggestions/', include('suggestions.urls')),  # Suggestion Box URLs
    path('announcements/', include('announcements.urls')),  # Company Announcements URLs
    path('api/v1/', include('api.urls')),  # REST API URLs
    path('', include('landing.urls')),
    # Worker Excel template download
    path('worker_eform.xlsx', serve_excel_template, name='worker_excel_template'),
    # Notification URLs
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/api/', views.notification_api, name='notification_api'),
    path('notifications/widget/', views.notification_dashboard_widget, name='notification_dashboard_widget'),
    
    # Notification Actions (AJAX)
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/<int:notification_id>/dismiss/', views.dismiss_notification, name='dismiss_notification'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/dismiss-all/', views.dismiss_all_notifications, name='dismiss_all_notifications'),
    
    # Secure Media URLs for encrypted files
    path('document/<int:document_id>/', views.serve_worker_document, name='serve_worker_document'),
    re_path(r'^media/(?P<file_path>.*\.enc)$', views.SecureMediaView.as_view(), name='secure_media'),

    # Nationality Management URLs
    path('nationalities/', views.nationality_list, name='nationality_list'),
    path('nationalities/create/', views.nationality_create, name='nationality_create'),
    path('nationalities/<int:pk>/', views.nationality_detail, name='nationality_detail'),
    path('nationalities/<int:pk>/edit/', views.nationality_edit, name='nationality_edit'),
    path('nationalities/<int:pk>/delete/', views.nationality_delete, name='nationality_delete'),
    
    # Tenant management URLs
    path('tenant/info/', views_tenant.tenant_info, name='tenant_info'),
    path('tenant/switch/', views_tenant.switch_tenant, name='switch_tenant'),
    path('api/tenant/switcher/', views_tenant.tenant_switcher_data, name='tenant_switcher_data'),
]

# Custom error handlers
handler403 = 'core.views.permission_denied_view'

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Only serve non-encrypted media files directly
    # Encrypted files (.enc) are handled by SecureMediaView above
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production media serving (for non-encrypted files)
    urlpatterns += [
        re_path(r'^media/(?!.*\.enc$)(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]