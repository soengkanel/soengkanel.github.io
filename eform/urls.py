from django.urls import path
from . import views

app_name = 'eform'

urlpatterns = [
    path('', views.form_list, name='form_list'),
    path('create/', views.create_form, name='create_form'),
    path('builder/<int:form_id>/', views.form_builder, name='form_builder'),
    path('view/<int:form_id>/', views.view_form, name='view_form'),
    path('fill/<int:form_id>/', views.fill_form, name='fill_form'),
    path('submissions/<int:form_id>/', views.form_submissions, name='form_submissions'),
    path('submission/<int:submission_id>/', views.view_submission, name='view_submission'),
    path('submission/<int:submission_id>/edit/', views.edit_submission, name='edit_submission'),
    path('delete/<int:form_id>/', views.delete_form, name='delete_form'),
    
    # Operations Dashboard
    path('operations/', views.operations_dashboard, name='operations_dashboard'),
    path('unified/', views.unified_dashboard, name='unified_dashboard'),
    path('ajax/workers/', views.ajax_load_workers, name='ajax_load_workers'),
    path('operations/extension-form/', views.extension_form, name='extension_form'),
    path('operations/extension-form/edit/<int:worker_id>/', views.extension_edit_form, name='extension_edit_form'),
    path('operations/extension-form/edit/request/<int:request_id>/', views.extension_edit_form, name='extension_edit_form_request'),
    path('operations/extension-requests/', views.extension_requests_list, name='extension_requests_list'),
    path('operations/extension-requests/<int:request_id>/', views.extension_request_detail, name='extension_request_detail'),
    path('operations/extension-requests/<int:request_id>/delete/', views.extension_request_delete, name='extension_request_delete'),
    path('operations/certificate-form/', views.certificate_form, name='certificate_form'),
    path('operations/certificate-form/workers/', views.certificate_form_workers, name='certificate_form_workers'),
    path('operations/certificate-request-form/', views.certificate_request_form, name='certificate_request_form'),
    path('operations/certificate-form/edit/<int:worker_id>/', views.certificate_edit_form, name='certificate_edit_form'),
    path('operations/certificate-requests/', views.certificate_requests_list, name='certificate_requests_list'),
    path('operations/certificate-requests/<int:request_id>/', views.certificate_request_detail, name='certificate_request_detail'),
    path('operations/certificate-requests/<int:request_id>/delete/', views.certificate_request_delete, name='certificate_request_delete'),
    path('operations/certificate-form/edit/request/<int:request_id>/', views.certificate_edit_form, name='certificate_edit_form_request'),

    path('operations/extension-form/print/<int:worker_id>/', views.print_extension_form, name='print_extension_form'),
    path('operations/certificate-form/print/', views.print_certificate_form, name='print_certificate_form'),

    
    
    # Worker Reports
    path('worker-reports/', views.worker_reports, name='worker_reports'),
    path('worker-reports/generate/', views.worker_reports, name='generate_worker_report'),
    path('worker-reports/print/', views.print_worker_report, name='print_worker_report'),
    
    # Recent Requests
    path('recent-requests/', views.recent_requests, name='recent_requests'),

    # Employee Form Submissions Management
    path('employee-submissions/', views.employee_submissions_list, name='employee_submissions_list'),
    path('employee-submissions/<int:submission_id>/', views.employee_submission_detail, name='employee_submission_detail'),
    path('employee-submissions/<int:submission_id>/update-status/', views.update_submission_status, name='update_submission_status'),
    path('form-builder/', views.form_builder_new, name='form_builder'),

    # Quick Forms (Ready-to-use forms)
    path('form/<slug:form_slug>/', views.quick_form, name='quick_form'),
    path('form/<slug:form_slug>/list/', views.quick_form_list, name='quick_form_list'),
] 