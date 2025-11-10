from django.urls import path
from . import views

app_name = 'hr'

urlpatterns = [
    # HR Dashboard
    path('dashboard/', views.hr_dashboard, name='hr_dashboard'),
    
    # Employee CRUD - now under employee/ prefix
    path('employee/', views.employee_list, name='employee_list'),
    path('employee/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employee/create/', views.employee_create, name='employee_create'),
    path('employee/<int:pk>/update/', views.employee_update, name='employee_update'),
    path('employee/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # AJAX endpoints - keep under employee/ prefix
    path('employee/ajax/positions/', views.get_positions_by_department, name='get_positions_by_department'),
    
    # Secure file serving
    path('employee/<int:employee_id>/photo/', views.serve_employee_photo, name='serve_employee_photo'),
    path('document/<int:document_id>/file/', views.serve_employee_document, name='serve_employee_document'),
    
    
    # Document management - under employee/ prefix
    path('employee/<int:employee_pk>/documents/create/', views.employee_document_create, name='employee_document_create'),
    path('employee/<int:employee_pk>/documents/<int:document_pk>/delete/', views.employee_document_delete, name='employee_document_delete'),

    # Department CRUD - keep at hr/ root level
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    # Position CRUD - keep at hr/ root level
    path('positions/', views.position_list, name='position_list'),
    path('positions/<int:pk>/', views.position_detail, name='position_detail'),
    path('positions/create/', views.position_create, name='position_create'),
    path('positions/<int:pk>/edit/', views.position_edit, name='position_edit'),
    path('positions/<int:pk>/delete/', views.position_delete, name='position_delete'),

    # Worker Reports
    path('worker-reports/', views.worker_reports_dashboard, name='worker_reports_dashboard'),
    path('worker-reports/foreign-khmer/', views.foreign_khmer_report, name='foreign_khmer_report'),
    path('api/buildings-by-zone/', views.get_buildings_by_zone, name='get_buildings_by_zone'),
    path('api/floors-by-building/', views.get_floors_by_building, name='get_floors_by_building'),
    path('worker-reports/staff/', views.staff_report, name='staff_report'),

    # Probation Management
    path('probation/', views.probation_list, name='probation_list'),
    path('probation/<int:pk>/', views.probation_detail, name='probation_detail'),
    path('probation/create/', views.probation_create, name='probation_create'),
    path('probation/<int:pk>/update/', views.probation_update, name='probation_update'),
    path('probation/<int:pk>/extend/', views.probation_extend, name='probation_extend'),
    path('probation/<int:pk>/delete/', views.probation_delete, name='probation_delete'),

    # Employee Lifecycle Dashboard
    path('lifecycle/', views.lifecycle_dashboard, name='lifecycle_dashboard'),

    # Onboarding Management
    path('onboarding/', views.onboarding_list, name='onboarding_list'),
    path('onboarding/<int:pk>/', views.onboarding_detail, name='onboarding_detail'),
    path('onboarding/create/', views.onboarding_create, name='onboarding_create'),
    path('onboarding/<int:pk>/delete/', views.onboarding_delete, name='onboarding_delete'),
    path('onboarding/task/<int:task_pk>/status/', views.onboarding_task_update_status, name='onboarding_task_update_status'),
    path('onboarding/task/<int:task_pk>/complete/', views.onboarding_task_complete, name='onboarding_task_complete'),

    # Promotion/Transfer Management
    path('promotion-transfer/', views.promotion_transfer_list, name='promotion_transfer_list'),
    path('promotion-transfer/<int:pk>/', views.promotion_transfer_detail, name='promotion_transfer_detail'),
    path('promotion-transfer/create/', views.promotion_transfer_create, name='promotion_transfer_create'),
    path('promotion-transfer/<int:pk>/approve/', views.promotion_transfer_approve, name='promotion_transfer_approve'),
    path('promotion-transfer/<int:pk>/implement/', views.promotion_transfer_implement, name='promotion_transfer_implement'),

    # Exit Management
    path('exit-interview/', views.exit_interview_list, name='exit_interview_list'),
    path('exit-interview/<int:pk>/', views.exit_interview_detail, name='exit_interview_detail'),
    path('exit-interview/create/', views.exit_interview_create, name='exit_interview_create'),
    path('exit-interview/<int:pk>/update/', views.exit_interview_update, name='exit_interview_update'),
    path('exit-checklist/<int:employee_pk>/', views.exit_checklist_detail, name='exit_checklist_detail'),
    path('exit-checklist/<int:employee_pk>/update/', views.exit_checklist_update, name='exit_checklist_update'),

]