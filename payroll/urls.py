from django.urls import path
from . import views

app_name = 'payroll'

urlpatterns = [
    # Dashboard
    path('', views.payroll_dashboard, name='dashboard'),

    # Payroll Periods
    path('periods/', views.payroll_periods, name='periods'),
    path('periods/create/', views.create_payroll_period, name='create_period'),
    path('periods/<int:period_id>/', views.payroll_period_detail, name='period_detail'),
    path('periods/<int:period_id>/edit/', views.edit_payroll_period, name='edit_period'),
    path('periods/<int:period_id>/generate/', views.generate_payroll, name='generate_payroll'),
    path('periods/<int:period_id>/delete/', views.payroll_period_delete, name='period_delete'),

    # Individual Payroll
    path('payroll/<int:payroll_id>/', views.payroll_detail, name='payroll_detail'),
    path('payroll/<int:payroll_id>/payslip/', views.generate_payslip, name='generate_payslip'),

    # Salary Slip (ERPNext style)
    path('salary-slip/<int:salary_slip_id>/', views.payslip_view, name='salary_slip_view'),

    # Salary Management
    path('salaries/', views.employee_salary_list, name='salary_list'),

    # Salary Structures
    path('salary-structures/', views.salary_structure_list, name='salary_structure_list'),
    path('salary-structures/create/', views.salary_structure_create, name='salary_structure_create'),
    path('salary-structures/<int:structure_id>/', views.salary_structure_detail, name='salary_structure_detail'),
    path('salary-structures/<int:structure_id>/edit/', views.salary_structure_edit, name='salary_structure_edit'),
    path('salary-structures/<int:structure_id>/delete/', views.salary_structure_delete, name='salary_structure_delete'),

    # Salary Structure Assignments
    path('salary-structure-assignments/', views.salary_structure_assignment_list, name='salary_structure_assignment_list'),
    path('salary-structure-assignments/create/', views.salary_structure_assignment_create, name='salary_structure_assignment_create'),
    path('salary-structure-assignments/<int:assignment_id>/edit/', views.salary_structure_assignment_edit, name='salary_structure_assignment_edit'),
    path('salary-structure-assignments/<int:assignment_id>/delete/', views.salary_structure_assignment_delete, name='salary_structure_assignment_delete'),

    # Advances
    path('advances/', views.salary_advances_list, name='advances_list'),
    path('advances/create/', views.salary_advance_create, name='salary_advance_create'),
    path('advances/<int:advance_id>/', views.salary_advance_detail, name='salary_advance_detail'),
    path('advances/<int:advance_id>/edit/', views.salary_advance_edit, name='salary_advance_edit'),
    path('advances/<int:advance_id>/approve/', views.salary_advance_approve, name='salary_advance_approve'),
    path('advances/<int:advance_id>/reject/', views.salary_advance_reject, name='salary_advance_reject'),
    path('advances/<int:advance_id>/delete/', views.salary_advance_delete, name='salary_advance_delete'),

    # Loans
    path('loans/', views.employee_loans_list, name='loans_list'),
    path('loans/create/', views.employee_loan_create, name='employee_loan_create'),
    path('loans/<int:loan_id>/', views.employee_loan_detail, name='employee_loan_detail'),
    path('loans/<int:loan_id>/edit/', views.employee_loan_edit, name='employee_loan_edit'),
    path('loans/<int:loan_id>/approve/', views.employee_loan_approve, name='employee_loan_approve'),
    path('loans/<int:loan_id>/activate/', views.employee_loan_activate, name='employee_loan_activate'),
    path('loans/<int:loan_id>/cancel/', views.employee_loan_cancel, name='employee_loan_cancel'),
    path('loans/<int:loan_id>/delete/', views.employee_loan_delete, name='employee_loan_delete'),

    # Reports
    path('reports/', views.payroll_reports, name='reports'),

    # Salary Components
    path('salary-components/', views.salary_component_list, name='salary_component_list'),
    path('salary-components/create/', views.salary_component_create, name='salary_component_create'),
    path('salary-components/<int:component_id>/', views.salary_component_detail, name='salary_component_detail'),
    path('salary-components/<int:component_id>/edit/', views.salary_component_edit, name='salary_component_edit'),
    path('salary-components/<int:component_id>/delete/', views.salary_component_delete, name='salary_component_delete'),

    # Tax Slabs
    path('tax-slabs/', views.tax_slab_list, name='tax_slab_list'),
    path('tax-slabs/create/', views.tax_slab_create, name='tax_slab_create'),
    path('tax-slabs/<int:slab_id>/edit/', views.tax_slab_edit, name='tax_slab_edit'),
    path('tax-slabs/<int:slab_id>/delete/', views.tax_slab_delete, name='tax_slab_delete'),

    # NSSF Configuration
    path('nssf-config/', views.nssf_config_list, name='nssf_config_list'),
    path('nssf-config/create/', views.nssf_config_create, name='nssf_config_create'),
    path('nssf-config/<int:config_id>/edit/', views.nssf_config_edit, name='nssf_config_edit'),
    path('nssf-config/<int:config_id>/delete/', views.nssf_config_delete, name='nssf_config_delete'),

    # AJAX
    path('ajax/calculate/', views.ajax_calculate_payroll, name='ajax_calculate'),
]