from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment list and management
    path('list/', views.payment_list, name='payment_list'),
    path('create/', views.payment_create, name='payment_create'),
    path('<int:payment_id>/', views.payment_detail, name='payment_detail'),
    path('<int:payment_id>/edit/', views.payment_edit, name='payment_edit'),
    path('<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),
    path('<int:payment_id>/receipt/', views.payment_receipt, name='payment_receipt'),
    
    # Invoice payment
    path('invoice/<int:invoice_id>/pay/', views.invoice_payment, name='invoice_payment'),
    
    # Reports
    path('reports/', views.payment_reports, name='reports'),
    path('reports/daily/', views.daily_collection_report, name='daily_collection_report'),
    path('reports/monthly/', views.monthly_payment_report, name='monthly_payment_report'),
    
    # AJAX endpoints
    path('api/invoice/<int:invoice_id>/balance/', views.get_invoice_balance, name='get_invoice_balance'),
    path('api/payment/<int:payment_id>/status/', views.update_payment_status, name='update_payment_status'),
] 