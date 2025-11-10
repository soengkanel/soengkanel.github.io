from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'document_tracking'

urlpatterns = [
    # Redirect root to submissions list (no dashboard needed)
    path('', RedirectView.as_view(pattern_name='document_tracking:submission_list', permanent=True), name='dashboard'),
    
    # Submission management
    path('submissions/', views.submission_list, name='submission_list'),
    path('submissions/create/', views.submission_create, name='submission_create'),
    path('submissions/<int:submission_id>/', views.submission_detail, name='submission_detail'),
    path('submissions/<int:submission_id>/edit/', views.submission_edit, name='submission_edit'),
    path('submissions/<int:submission_id>/delete/', views.submission_delete, name='submission_delete'),
    
    # Reports

    
    # AJAX endpoints
    path('api/submissions/<int:submission_id>/status/', views.update_submission_status, name='update_submission_status'),
    path('api/print-batches/', views.api_get_print_batches, name='api_get_print_batches'),
    path('api/batch/<uuid:batch_id>/workers/', views.api_get_batch_workers, name='api_get_batch_workers'),
    path('api/search-workers/', views.api_search_workers, name='api_search_workers'),
    
    # Extension of Stay Application
    path('extension-stay/', views.extension_stay_form, name='extension_stay_form'),
    
    # Document Submission
    path('document-submission/', views.document_submission, name='document_submission'),
] 