from django.urls import path
from . import views

app_name = 'policies'

urlpatterns = [
    # Main policy dashboard
    path('', views.policy_dashboard, name='dashboard'),

    # Leave policies
    path('leave/', views.leave_policy_list, name='leave_policy_list'),
    path('leave/create/', views.leave_policy_create, name='leave_policy_create'),
    path('leave/<int:pk>/edit/', views.leave_policy_edit, name='leave_policy_edit'),

    # Attendance policies
    path('attendance/', views.attendance_policy_list, name='attendance_policy_list'),
    path('attendance/create/', views.attendance_policy_create, name='attendance_policy_create'),
    path('attendance/<int:pk>/edit/', views.attendance_policy_edit, name='attendance_policy_edit'),

    # Overtime policies
    path('overtime/', views.overtime_policy_list, name='overtime_policy_list'),
    path('overtime/create/', views.overtime_policy_create, name='overtime_policy_create'),
    path('overtime/<int:pk>/edit/', views.overtime_policy_edit, name='overtime_policy_edit'),

    # Payroll policies
    path('payroll/', views.payroll_policy_list, name='payroll_policy_list'),
    path('payroll/create/', views.payroll_policy_create, name='payroll_policy_create'),
    path('payroll/<int:pk>/edit/', views.payroll_policy_edit, name='payroll_policy_edit'),

    # Expense policies
    path('expense/', views.expense_policy_list, name='expense_policy_list'),
    path('expense/create/', views.expense_policy_create, name='expense_policy_create'),
    path('expense/<int:pk>/edit/', views.expense_policy_edit, name='expense_policy_edit'),
]
