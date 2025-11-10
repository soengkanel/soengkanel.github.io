from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Dashboard
    path('', views.billing_dashboard, name='dashboard'),
    
    # Invoices
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/edit/', views.invoice_edit, name='invoice_edit'),
    path('invoices/<int:invoice_id>/delete/', views.invoice_delete, name='invoice_delete'),
    path('invoices/<int:invoice_id>/void/', views.invoice_void, name='invoice_void'),
    path('invoices/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:invoice_id>/mark-paid/', views.invoice_mark_paid, name='invoice_mark_paid'),
    
    # Invoice Workflow
    path('invoices/<int:invoice_id>/submit/', views.invoice_submit, name='invoice_submit'),
    path('invoices/<int:invoice_id>/approve/', views.invoice_approve, name='invoice_approve'),
    path('invoices/<int:invoice_id>/reject/', views.invoice_reject, name='invoice_reject'),
    path('invoices/<int:invoice_id>/send-to-client/', views.invoice_send_to_client, name='invoice_send_to_client'),
    path('invoices/<int:invoice_id>/cancel/', views.invoice_cancel, name='invoice_cancel'),
    
    # Official Receipts (Cambodian Government Format)
    path('official-receipts/', views.official_receipt_list, name='official_receipt_list'),
    path('official-receipts/create/', views.official_receipt_create, name='official_receipt_create'),
    path('official-receipts/<int:receipt_id>/', views.official_receipt_detail, name='official_receipt_detail'),
    path('official-receipts/<int:receipt_id>/edit/', views.official_receipt_edit, name='official_receipt_edit'),
    path('official-receipts/<int:receipt_id>/delete/', views.official_receipt_delete, name='official_receipt_delete'),
    path('official-receipts/<int:receipt_id>/print/', views.official_receipt_print, name='official_receipt_print'),
    
    # Cash/Cheque Receipts
    path('cash-receipts/', views.cash_receipt_list, name='cash_receipt_list'),
    path('cash-receipts/create/', views.cash_receipt_create, name='cash_receipt_create'),
    path('cash-receipts/<int:receipt_id>/', views.cash_receipt_detail, name='cash_receipt_detail'),
    path('cash-receipts/<int:receipt_id>/edit/', views.cash_receipt_edit, name='cash_receipt_edit'),
    path('cash-receipts/<int:receipt_id>/delete/', views.cash_receipt_delete, name='cash_receipt_delete'),
    path('cash-receipts/<int:receipt_id>/print/', views.cash_receipt_print, name='cash_receipt_print'),
    
    # Payment Vouchers
    path('payment-vouchers/', views.payment_voucher_list, name='payment_voucher_list'),
    path('payment-vouchers/create/', views.payment_voucher_create, name='payment_voucher_create'),
    path('payment-vouchers/<int:voucher_id>/', views.payment_voucher_detail, name='payment_voucher_detail'),
    path('payment-vouchers/<int:voucher_id>/edit/', views.payment_voucher_edit, name='payment_voucher_edit'),
    path('payment-vouchers/<int:voucher_id>/delete/', views.payment_voucher_delete, name='payment_voucher_delete'),
    path('payment-vouchers/<int:voucher_id>/print/', views.payment_voucher_print, name='payment_voucher_print'),
    
    # Payment Voucher Workflow
    path('payment-vouchers/<int:voucher_id>/submit/', views.payment_voucher_submit, name='payment_voucher_submit'),
    path('payment-vouchers/<int:voucher_id>/approve/', views.payment_voucher_approve, name='payment_voucher_approve'),
    path('payment-vouchers/<int:voucher_id>/reject/', views.payment_voucher_reject, name='payment_voucher_reject'),
    path('payment-vouchers/<int:voucher_id>/mark-paid/', views.payment_voucher_mark_paid, name='payment_voucher_mark_paid'),
    path('payment-vouchers/<int:voucher_id>/cancel/', views.payment_voucher_cancel, name='payment_voucher_cancel'),
    
    # Services
    path('services/', views.service_list, name='service_list'),
    path('services/create/', views.service_create, name='service_create'),
    path('services/<int:service_id>/edit/', views.service_edit, name='service_edit'),
    path('services/<int:service_id>/delete/', views.service_delete, name='service_delete'),
    path('services/<int:service_id>/history/', views.service_history, name='service_history'),
    
    # Reports
    path('reports/revenue/', views.revenue_report, name='revenue_report'),
    path('reports/overdue/', views.overdue_report, name='overdue_report'),
    path('reports/receipts/', views.receipt_summary_report, name='receipt_summary_report'),
    
    # Modern Print Templates
    path('invoices/<int:invoice_id>/print-preview/', views.invoice_print_preview, name='invoice_print_preview'),
    path('payment-vouchers/<int:voucher_id>/print-preview/', views.payment_voucher_print_preview, name='payment_voucher_print_preview'),
    path('receipts/<int:receipt_id>/print-preview/', views.receipt_print_preview, name='receipt_print_preview'),
    
    # AJAX endpoints
    path('api/services/<int:service_id>/', views.get_service_details, name='get_service_details'),
    path('api/services/search/', views.search_services, name='search_services'),
    path('api/invoices/<int:invoice_id>/line-items/', views.manage_line_items, name='manage_line_items'),
    
    # Autocomplete endpoints
    path('ajax/search-workers/', views.ajax_search_workers, name='ajax_search_workers'),
    path('ajax/search-vips/', views.ajax_search_vips, name='ajax_search_vips'),
    path('ajax/search-batches/', views.ajax_search_batches, name='ajax_search_batches'),
    
    # Batch workers
    path('batch-workers/<str:batch_name>/', views.batch_workers_list, name='batch_workers_list'),
    
    # Visa Services
    path('visa-services/', views.visa_services_dashboard, name='visa_services_dashboard'),
    path('visa-services/create/', views.visa_service_create, name='visa_service_create'),
    path('visa-services/list/', views.visa_service_list, name='visa_service_list'),
    path('visa-services/<int:service_id>/', views.visa_service_detail, name='visa_service_detail'),
    path('visa-services/report/', views.visa_services_report, name='visa_services_report'),
] 