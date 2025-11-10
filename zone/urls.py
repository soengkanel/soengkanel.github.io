from django.urls import path
from . import views
# Import improved probation views to replace the old ones
try:
    from .views_probation_simple import (
        probation_list_improved,
        probation_workflow_action,
        probation_dashboard,
        probation_extension_history,
        sync_worker_probation_status,
        bulk_sync_worker_probation_status,
        probation_extension_requests,
        approve_extension_request,
        get_available_workers,
        get_buildings_for_zone,
        get_floors_for_building,
        probation_bulk_delete,
        probation_batch_pass
    )
    # Replace old probation views with improved ones
    views.probation_list = probation_list_improved  # Replace old view
    views.probation_workflow_action = probation_workflow_action
    views.probation_dashboard = probation_dashboard
    views.probation_extension_history = probation_extension_history
except ImportError:
    pass  # Fallback if the improved views aren't available yet

app_name = 'zone'

urlpatterns = [
    # Main list views
    path('', views.zone_list, name='zone_list'),
    path('workers/', views.worker_list, name='worker_list'),
    path('workers/reports/', views.worker_reports, name='worker_reports'),
    path('buildings/', views.building_list, name='building_list'),
    path('floors/', views.floor_list, name='floor_list'),
    
    # Zone management
    path('create/', views.zone_create, name='zone_create'),
    path('<int:zone_id>/', views.zone_detail, name='zone_detail'),
    path('<int:zone_id>/edit/', views.zone_edit, name='zone_edit'),
    path('<int:zone_id>/delete/', views.zone_delete, name='zone_delete'),
    
    # Building management
    path('buildings/create/', views.building_create, name='building_create'),
    path('buildings/<int:building_id>/', views.building_detail, name='building_detail'),
    path('buildings/<int:building_id>/edit/', views.building_edit, name='building_edit'),
    path('buildings/<int:building_id>/delete/', views.building_delete, name='building_delete'),
    
    # Floor management
    path('floors/create/', views.floor_create, name='floor_create'),
    path('floors/<int:floor_id>/', views.floor_detail, name='floor_detail'),
    path('floors/<int:floor_id>/edit/', views.floor_edit, name='floor_edit'),
    path('floors/<int:floor_id>/delete/', views.floor_delete, name='floor_delete'),
    
    # Worker Department management
    path('worker-departments/', views.worker_department_list, name='worker_department_list'),
    path('worker-departments/create/', views.worker_department_create, name='worker_department_create'),
    path('worker-departments/<int:pk>/', views.worker_department_detail, name='worker_department_detail'),
    path('worker-departments/<int:pk>/edit/', views.worker_department_edit, name='worker_department_edit'),
    path('worker-departments/<int:pk>/delete/', views.worker_department_delete, name='worker_department_delete'),
    
    # Worker Position management
    path('worker-positions/', views.worker_position_list, name='worker_position_list'),
    path('worker-positions/create/', views.worker_position_create, name='worker_position_create'),
    path('worker-positions/<int:pk>/', views.worker_position_detail, name='worker_position_detail'),
    path('worker-positions/<int:pk>/edit/', views.worker_position_edit, name='worker_position_edit'),
    path('worker-positions/<int:pk>/delete/', views.worker_position_delete, name='worker_position_delete'),

    #encrypt image
    path('workers/document/<int:pk>/', views.serve_encrypted_image, name='serve_encrypted_image'),

    # Worker management
    path('workers/create/', views.worker_create, name='worker_create'),
    path('workers/import/', views.worker_import, name='worker_import'),
    
    # Worker Import with Web Interface
    path('workers/import-excel/', views.import_workers_view, name='import_workers'),
    path('workers/import-excel/preview/', views.import_workers_preview, name='import_workers_preview'),
    path('workers/import-excel/results/', views.import_workers_results, name='import_workers_results'),
    path('workers/import-excel/ajax/', views.import_workers_ajax, name='import_workers_ajax'),
    path('workers/import-excel/template/', views.download_template, name='download_template'),
    path('workers/<int:worker_id>/', views.worker_detail, name='worker_detail'),
    path('workers/<int:worker_id>/edit/', views.worker_edit, name='worker_edit'),
    path('workers/<int:worker_id>/delete/', views.worker_delete, name='worker_delete'),
    path('workers/bulk-delete/', views.bulk_delete_workers, name='bulk_delete_workers'),
    
    # Worker photo serving
    path('workers/<int:worker_id>/photo/', views.serve_worker_photo, name='serve_worker_photo'),
    path('workers/<int:worker_id>/professional-photo/', views.serve_worker_professional_photo, name='serve_worker_professional_photo'),
    
    # AJAX endpoints
    path('ajax/get-floors/', views.get_floors_ajax, name='get_floors_ajax'),
    path('ajax/get-floors-by-building/', views.get_floors_by_building, name='get_floors_by_building'),
    path('ajax/get-floors/<int:building_id>/', views.get_floors_by_building_id, name='get_floors_by_building_id'),
    path('ajax/get-buildings-by-zone/', views.get_buildings_by_zone, name='get_buildings_by_zone'),
    path('ajax/worker-photo/<int:worker_id>/', views.worker_photo_ajax, name='worker_photo_ajax'),
    
    # Smart Search
    path('ajax/smart-search/', views.smart_search, name='smart_search'),
    
    # Validation endpoints
    path('workers/check-passport-duplicate/', views.check_passport_duplicate, name='check_passport_duplicate'),
    
    # Document Management
    path('workers/<int:worker_id>/documents/', views.worker_document_list, name='worker_document_list'),
    path('workers/<int:worker_id>/documents/add/', views.worker_document_add, name='worker_document_add'),
    path('documents/<int:document_id>/edit/', views.document_edit, name='document_edit'),
    path('documents/<int:document_id>/delete/', views.document_delete, name='document_delete'),
    path('documents/<int:document_id>/download/', views.document_download, name='document_download'),
    
    # Probation Management (Updated with improved UI and workflow)
    path('probation/', views.probation_list, name='probation_list'),
    path('probation/dashboard/', views.probation_dashboard, name='probation_dashboard'),
    path('probation/bulk-delete/', probation_bulk_delete, name='probation_bulk_delete'),
    path('probation/batch-pass/', probation_batch_pass, name='probation_batch_pass'),
    path('probation/<int:probation_id>/action/<str:action>/', views.probation_workflow_action, name='probation_workflow_action'),
    path('probation/<int:probation_id>/extension-history/', views.probation_extension_history, name='probation_extension_history'),
    path('probation/<int:probation_id>/sync/', sync_worker_probation_status, name='sync_worker_probation_status'),
    path('probation/bulk-sync/', bulk_sync_worker_probation_status, name='bulk_sync_worker_probation_status'),
    
    # Extension request management (Maker-checker workflow)
    path('probation/extension-requests/', probation_extension_requests, name='probation_extension_requests'),
    path('probation/extension-request/<int:request_id>/review/', approve_extension_request, name='approve_extension_request'),
    
    path('probation/<int:probation_id>/', views.probation_detail, name='probation_detail'),
    path('probation/create/', views.probation_create, name='probation_create'),
    path('probation/create/<int:worker_id>/', views.probation_create, name='probation_create_for_worker'),
    path('probation/batch-create/', views.probation_batch_create, name='probation_batch_create'),
    path('probation/<int:probation_id>/edit/', views.probation_edit, name='probation_edit'),
    path('probation/<int:probation_id>/extend/', views.probation_extend, name='probation_extend'),
    path('extension-request/<int:request_id>/review/', views.extension_request_review, name='extension_request_review'),
    path('extension-request/<int:request_id>/cancel/', views.extension_request_cancel, name='extension_request_cancel'),
    path('extension-requests/', views.extension_requests_list, name='extension_requests_list'),
    path('probation/<int:probation_id>/terminate/', views.probation_terminate, name='probation_terminate'),
    path('probation/<int:probation_id>/complete/', views.probation_complete, name='probation_complete'),
    path('probation/<int:probation_id>/pass/', views.probation_pass, name='probation_pass'),
    path('probation/<int:probation_id>/cancel/', views.probation_cancel, name='probation_cancel'),
    path('probation/<int:probation_id>/delete/', views.probation_delete, name='probation_delete'),
    path('workers/<int:worker_id>/probation/', views.worker_probation_status, name='worker_probation_status'),
    path('workers/<int:worker_id>/probation/extensions/', views.worker_probation_extensions, name='worker_probation_extensions'),
    
    # API endpoints
    path('api/workers/available/', get_available_workers, name='get_available_workers'),
    path('api/buildings/by-zone/', get_buildings_for_zone, name='get_buildings_for_zone'),
    path('api/floors/by-building/', get_floors_for_building, name='get_floors_for_building'),
    path('api/worker-search-probation/', views.worker_search_for_probation_api, name='worker_search_for_probation_api'),
    
    # ocr image  
    path('workers/ocr/image/', views.worker_ocr_image, name='worker_ocr_image'),

    # import excel file
    path('upload_excel/', views.upload_excel, name="upload_excel"),
    path('convert/', views.excel_to_json, name='excel_to_json'),

    # worker import excel (simplified)
    path('worker/import/excel', views.simple_excel_import, name="simple_excel_import"),
    
    # Two-step import process
    path('worker/import/step1-extract/', views.step1_extract_excel_to_json, name='step1_extract_excel_to_json'),
    path('worker/import/step2-process-mrz/', views.step2_process_mrz_and_import, name='step2_process_mrz_and_import'),
    
    # Save edited preview data
    path('worker/import/save-edited-data/', views.save_edited_preview_data, name='save_edited_preview_data'),
    
    
] 