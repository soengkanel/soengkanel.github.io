from django.urls import path
from . import views

app_name = 'leave'

urlpatterns = [
    # Dashboard
    path('', views.leave_dashboard, name='dashboard'),

    # Leave Types
    path('types/', views.leave_type_list, name='type_list'),
    path('types/create/', views.leave_type_create, name='type_create'),
    path('types/<int:pk>/edit/', views.leave_type_edit, name='type_edit'),
    path('types/<int:pk>/delete/', views.leave_type_delete, name='type_delete'),

    # Leave Applications
    path('applications/', views.leave_application_list, name='application_list'),
    path('applications/create/', views.leave_application_create, name='application_create'),
    path('applications/<int:pk>/', views.leave_application_detail, name='application_detail'),
    path('applications/<int:pk>/approve/', views.leave_application_approve, name='application_approve'),
    path('applications/<int:pk>/reject/', views.leave_application_reject, name='application_reject'),
    path('applications/<int:pk>/cancel/', views.leave_application_cancel, name='application_cancel'),

    # Leave Allocations
    path('allocations/', views.leave_allocation_list, name='allocation_list'),
    path('allocations/create/', views.leave_allocation_create, name='allocation_create'),
    path('allocations/<int:pk>/edit/', views.leave_allocation_edit, name='allocation_edit'),

    # Holidays
    path('holidays/', views.holiday_list, name='holiday_list'),
    path('holidays/create/', views.holiday_create, name='holiday_create'),
    path('holidays/<int:pk>/edit/', views.holiday_edit, name='holiday_edit'),
    path('holidays/<int:pk>/delete/', views.holiday_delete, name='holiday_delete'),
]
