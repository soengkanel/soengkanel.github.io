from django.urls import path
from . import views

app_name = 'sinosecu'

urlpatterns = [
    # Main interface views
    path('', views.scanner_dashboard, name='dashboard'),
   
    
    # API endpoints for WebSocket communication
    path('api/start-scan/', views.api_start_scan, name='api_start_scan'),
    path('api/save-result/', views.api_save_scan_result, name='api_save_scan_result'),
    path('api/device-status/', views.api_update_device_status, name='api_update_device_status'),
    path('api/device-status/get/', views.api_get_device_status, name='api_get_device_status'),
    path('api/websocket-session/', views.api_websocket_session, name='api_websocket_session'),
    
    # Export functionality
    path('export/<str:scan_id>/', views.export_scan_data, name='export_scan_data'),
] 