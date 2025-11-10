from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('', views.dashboard_home, name='index'),  # Alias for 'home'
    path('', views.dashboard_home, name='dashboard'),  # Another alias for 'home'
    path('settings/', views.settings_view, name='settings'),
]