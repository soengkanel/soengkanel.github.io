from django.urls import path
from . import views

app_name = 'announcements'

urlpatterns = [
    # Employee Views
    path('', views.announcement_list, name='announcement_list'),
    path('<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('<int:pk>/acknowledge/', views.announcement_acknowledge, name='announcement_acknowledge'),
    path('<int:pk>/comment/', views.announcement_comment_add, name='announcement_comment_add'),

    # Staff/Admin Views
    path('manage/', views.announcement_manage_list, name='announcement_manage_list'),
    path('manage/create/', views.announcement_create, name='announcement_create'),
    path('manage/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('manage/<int:pk>/delete/', views.announcement_delete, name='announcement_delete'),
    path('manage/<int:pk>/analytics/', views.announcement_analytics, name='announcement_analytics'),
]
