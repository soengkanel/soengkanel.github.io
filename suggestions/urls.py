from django.urls import path
from . import views

app_name = 'suggestions'

urlpatterns = [
    # Employee Portal Views
    path('', views.suggestion_list, name='suggestion_list'),
    path('create/', views.suggestion_create, name='suggestion_create'),
    path('my-suggestions/', views.my_suggestions, name='my_suggestions'),
    path('<int:pk>/', views.suggestion_detail, name='suggestion_detail'),
    path('<int:pk>/edit/', views.suggestion_edit, name='suggestion_edit'),
    path('<int:pk>/vote/', views.suggestion_vote, name='suggestion_vote'),
    path('<int:pk>/comment/', views.suggestion_comment_add, name='suggestion_comment_add'),

    # Admin/Management Views
    path('admin/', views.admin_suggestion_list, name='admin_suggestion_list'),
    path('admin/<int:pk>/respond/', views.admin_suggestion_respond, name='admin_suggestion_respond'),
]
