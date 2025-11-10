from django.urls import path
from . import views

app_name = 'recruitment'

urlpatterns = [
    # Dashboard
    path('', views.recruitment_dashboard, name='dashboard'),

    # Job Postings
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/edit/', views.job_update, name='job_update'),

    # Candidates
    path('candidates/', views.candidate_list, name='candidate_list'),
    path('candidates/<int:pk>/', views.candidate_detail, name='candidate_detail'),
    path('candidates/<int:pk>/update-status/', views.candidate_update_status, name='candidate_update_status'),
    path('candidates/<int:pk>/hire/', views.candidate_hire, name='candidate_hire'),

    # Interviews
    path('candidates/<int:candidate_pk>/interview/schedule/', views.interview_schedule, name='interview_schedule'),
    path('interviews/<int:pk>/complete/', views.interview_complete, name='interview_complete'),

    # Offers
    path('candidates/<int:candidate_pk>/offer/create/', views.offer_create, name='offer_create'),
    path('offers/<int:pk>/update-status/', views.offer_update_status, name='offer_update_status'),
]
