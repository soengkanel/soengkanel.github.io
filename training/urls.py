from django.urls import path
from . import views

app_name = 'training'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Course URLs
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
    path('courses/<int:pk>/edit/', views.course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.course_delete, name='course_delete'),
    path('courses/<int:pk>/enroll/', views.course_enroll, name='course_enroll'),
    path('courses/<int:pk>/learn/', views.learn_course, name='learn_course'),

    # Module Management URLs
    path('courses/<int:course_pk>/modules/create/', views.module_create, name='module_create'),
    path('modules/<int:pk>/edit/', views.module_edit, name='module_edit'),
    path('modules/<int:pk>/delete/', views.module_delete, name='module_delete'),

    # Lesson Management URLs
    path('modules/<int:module_pk>/lessons/create/', views.lesson_create, name='lesson_create'),
    path('lessons/<int:pk>/edit/', views.lesson_edit, name='lesson_edit'),
    path('lessons/<int:pk>/delete/', views.lesson_delete, name='lesson_delete'),

    # Material Management URLs
    path('lessons/<int:lesson_pk>/materials/upload/', views.material_upload, name='material_upload'),
    path('materials/<int:pk>/delete/', views.material_delete, name='material_delete'),
    path('materials/<int:material_id>/serve/', views.serve_course_material, name='serve_material'),

    # Lesson URLs
    path('courses/<int:course_pk>/lessons/<int:lesson_pk>/', views.lesson_view, name='lesson_view'),
    path('courses/<int:course_pk>/lessons/<int:lesson_pk>/complete/', views.lesson_complete, name='lesson_complete'),

    # Enrollment Management URLs
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/<int:pk>/', views.enrollment_detail, name='enrollment_detail'),
    path('enrollments/create/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/<int:pk>/delete/', views.enrollment_delete, name='enrollment_delete'),

    # Quiz URLs
    path('courses/<int:course_pk>/quiz/<int:quiz_pk>/', views.quiz_take, name='quiz_take'),
    path('courses/<int:course_pk>/quiz/<int:quiz_pk>/submit/<int:attempt_pk>/', views.quiz_submit, name='quiz_submit'),
    path('courses/<int:course_pk>/quiz/<int:quiz_pk>/result/<int:attempt_pk>/', views.quiz_result, name='quiz_result'),

    # Reports URLs
    path('reports/', views.reports_overview, name='reports_overview'),

    # Mock Data Generation (for testing)
    path('generate-mock-data/', views.generate_mock_data, name='generate_mock_data'),
]
