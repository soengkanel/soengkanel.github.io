from django.urls import path
from . import views

app_name = 'employee_portal'

urlpatterns = [
    # Dashboard
    path('', views.employee_dashboard, name='dashboard'),

    # Profile
    path('profile/', views.employee_profile, name='profile'),

    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/<int:attendance_id>/', views.attendance_detail, name='attendance_detail'),

    # Payslips
    path('payslips/', views.payslip_list, name='payslip_list'),
    path('payslips/<int:payslip_id>/', views.payslip_detail, name='payslip_detail'),

    # Documents
    path('documents/', views.document_list, name='document_list'),
    path('documents/upload/', views.document_upload, name='document_upload'),

    # Overtime Claims
    path('overtime/', views.overtime_claim_list, name='overtime_claim_list'),
    path('overtime/create/', views.overtime_claim_create, name='overtime_claim_create'),

    # Training
    path('training/', views.training_courses, name='training_courses'),
    path('training/my-courses/', views.training_my_courses, name='training_my_courses'),
    path('training/courses/<int:course_id>/', views.training_course_detail, name='training_course_detail'),
    path('training/courses/<int:course_id>/enroll/', views.training_enroll, name='training_enroll'),

    # Performance & Goals
    path('performance/', views.employee_performance, name='performance'),
    path('performance/reviews/<int:pk>/', views.employee_performance_review_detail, name='performance_review_detail'),
    path('performance/goals/<int:pk>/', views.employee_goal_detail, name='goal_detail'),

    # Request Forms
    path('forms/', views.request_forms, name='request_forms'),
    path('forms/fill/<int:form_id>/', views.fill_request_form, name='fill_request_form'),
    path('forms/my-submissions/', views.my_form_submissions, name='my_form_submissions'),
    path('forms/submission/<int:submission_id>/', views.view_form_submission, name='view_form_submission'),

    # Holiday Calendar
    path('holidays/', views.holiday_calendar, name='holiday_calendar'),

    # Onboarding
    path('onboarding/', views.onboarding_overview, name='onboarding_overview'),
    path('onboarding/task/<int:task_id>/complete/', views.complete_onboarding_task, name='complete_onboarding_task'),
]
