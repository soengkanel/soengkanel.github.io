from django.urls import path
from . import views

app_name = 'cards'

urlpatterns = [
    # ID Cards Dashboard (main landing page)
    path('', views.id_cards_dashboard, name='id_cards_dashboard'),
    
    # Worker ID Cards - Order matters! More specific patterns first
    path('worker-id-cards/create/<str:filter>/', views.worker_id_card_create, name='worker_id_card_create'),
    path('worker-id-cards/batch-create/', views.worker_id_card_batch_create, name='worker_id_card_batch_create'),
    path('worker-id-cards/print-preview/', views.worker_id_card_print_preview, name='worker_id_card_print_preview'),
    path('worker-id-cards/print-confirm/', views.worker_id_card_print_confirm, name='worker_id_card_print_confirm'),
    path('worker-id-cards/<int:pk>/', views.worker_id_card_detail, name='worker_id_card_detail'),
    path('worker-id-cards/<int:pk>/update/', views.worker_id_card_update, name='worker_id_card_update'),
    path('worker-id-cards/<int:pk>/delete/', views.worker_id_card_delete, name='worker_id_card_delete'),
    path('worker-id-cards/<str:option>/', views.worker_id_card_list, name='worker_id_card_list'),
    

    
    # Employee ID Cards
    path('employee-id-cards/', views.employee_id_card_list, name='employee_id_card_list'),
    path('employee-id-cards/<int:pk>/', views.employee_id_card_detail, name='employee_id_card_detail'),
    path('employee-id-cards/create/', views.employee_id_card_create, name='employee_id_card_create'),
    path('employee-id-cards/batch-create/', views.employee_id_card_batch_create, name='employee_id_card_batch_create'),
    path('employee-id-cards/<int:pk>/update/', views.employee_id_card_update, name='employee_id_card_update'),
    path('employee-id-cards/<int:pk>/delete/', views.employee_id_card_delete, name='employee_id_card_delete'),
    path('employee-id-cards/select-print/', views.employee_id_card_select_for_print, name='employee_id_card_select_print'),
    path('employee-id-cards/print-preview/', views.employee_id_card_print_preview, name='employee_id_card_print_preview'),
    path('employee-id-cards/print-confirm/', views.employee_id_card_print_confirm, name='employee_id_card_print_confirm'),
    
    # Card Replacements
    path('replacements/', views.card_replacement_list, name='card_replacement_list'),
    path('replacements/<int:pk>/', views.card_replacement_detail, name='card_replacement_detail'),
    path('replacements/<int:pk>/invoice', views.card_replacement_invoice, name='card_replacement_invoice'),
    path('replacements/create/', views.card_replacement_create, name='card_replacement_create'),
    path('replacements/create-invoice/', views.card_replacement_invoice_create, name='card_replacement_invoice_create'),
    path('replacements/<int:pk>/update/', views.card_replacement_update, name='card_replacement_update'),
    path('replacements/<int:pk>/approve/', views.card_replacement_approve, name='card_replacement_approve'),
    path('replacements/<int:pk>/complete/', views.card_replacement_complete, name='card_replacement_complete'),
    path('replacements/<int:pk>/delete/', views.card_replacement_delete, name='card_replacement_delete'),
    
    # Printing History & Charges
    path('printing-history/', views.card_printing_history, name='card_printing_history'),
    path('charges/', views.card_charges_list, name='card_charges_list'),
    path('charges/<int:pk>/update/', views.card_charge_update, name='card_charge_update'),
    
    # API Endpoints
    path('api/worker-search/', views.worker_search_api, name='worker_search_api'),
    path('api/worker-search-new-card/', views.worker_search_for_new_card_api, name='worker_search_for_new_card_api'),
    path('api/next-card-sequence/', views.next_card_sequence_api, name='next_card_sequence_api'),
    path('api/worker-card-search/', views.worker_card_search_api, name='worker_card_search_api'),
    path('api/worker-card/<int:pk>/verify/', views.worker_card_verify_api, name='worker_card_verify_api'),

    path('api/employee-card-search/', views.employee_card_search_api, name='employee_card_search_api'),
    path('api/employee-search/', views.employee_search_api, name='employee_search_api'),
    path('api/employee-card/<int:pk>/verify/', views.employee_card_verify_api, name='employee_card_verify_api'),

]
