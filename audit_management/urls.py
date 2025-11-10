from django.urls import path
from . import views
from . import simple_views

app_name = 'audit_management'

urlpatterns = [
    # Simple Audit Logs (default route)
    path('', simple_views.simple_audit_logs, name='simple_logs'),
    path('simple/', simple_views.simple_audit_logs, name='simple_logs_alt'),
    path('export/', simple_views.export_simple_logs, name='export_simple_logs'),
    path('clear/', simple_views.clear_simple_logs, name='clear_simple_logs'),
    path('models/', simple_views.audit_models_settings, name='audit_models_settings'),
    
    # Original complex dashboard (moved to /dashboard)
    path('dashboard/', views.audit_dashboard, name='dashboard'),
    
    # Audit Logs
    path('logs/', views.audit_logs, name='logs'),
    path('logs/<int:log_id>/', views.log_detail, name='log_detail'),
    path('logs/export/', views.export_logs, name='export_logs'),
    path('logs/search/', views.search_logs, name='search_logs'),
    
    # Sessions
    path('sessions/', views.audit_sessions, name='sessions'),
    
    # User Activity
    path('users/<int:user_id>/activity/', views.user_activity, name='user_activity'),
    
    # Exceptions
    path('exceptions/', views.audit_exceptions, name='exceptions'),
    path('exceptions/<int:exception_id>/resolve/', views.resolve_exception, name='resolve_exception'),
    
    # API endpoints
    path('api/logs-data/', views.api_logs_data, name='api_logs_data'),
    
    # Maintenance
    path('clear-logs/', views.clear_logs, name='clear_logs'),
] 