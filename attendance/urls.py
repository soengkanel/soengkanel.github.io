from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    # Dashboard redirects to attendance list
    path('', views.attendance_list, name='dashboard'),

    # Attendance Records
    path('records/', views.attendance_list, name='attendance_list'),
    path('manual/', views.manual_attendance, name='manual_attendance'),
    path('mark/', views.mark_attendance, name='mark_attendance'),
    path('delete/<int:employee_id>/', views.delete_attendance, name='delete_attendance'),
    path('record/<int:record_id>/delete/', views.delete_attendance_record, name='delete_attendance_record'),
    path('get-employees/', views.get_employees, name='get_employees'),

    # Overtime
    path('overtime/', views.overtime_request_list, name='overtime_list'),
    path('overtime/create/', views.overtime_request_create, name='overtime_create'),
    path('overtime/<int:pk>/update/', views.overtime_request_update, name='overtime_update'),
    path('overtime/<int:pk>/approve/', views.overtime_request_approve, name='overtime_approve'),
    path('overtime/<int:pk>/delete/', views.overtime_request_delete, name='overtime_delete'),

    # Corrections
    path('corrections/', views.correction_request_list, name='correction_list'),
    path('corrections/create/', views.correction_request_create, name='correction_create'),
    path('corrections/<int:pk>/approve/', views.correction_request_approve, name='correction_approve'),

    # Biometric Devices
    path('devices/', views.biometric_device_list, name='device_list'),
    path('devices/create/', views.biometric_device_create, name='device_create'),
    path('devices/<int:pk>/sync/', views.biometric_device_sync, name='device_sync'),

    # Reports
    path('reports/', views.attendance_report, name='report'),
    path('reports/export/', views.attendance_report_export, name='report_export'),
    path('reports/overtime/', views.overtime_report, name='overtime_report'),
    path('reports/overtime/export/', views.overtime_report_export, name='overtime_report_export'),
]