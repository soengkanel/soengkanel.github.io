"""
Public schema URL configuration for tenant management.
This handles URLs that don't require tenant context (company management, tenant setup).
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('company/', include('company.urls')),  # Company management
    path('accounts/', include('django.contrib.auth.urls')),  # Authentication
    path('api/v1/', include('api.urls')),  # REST API URLs

    # Nationality Management URLs
    path('nationalities/', views.nationality_list, name='nationality_list'),
    path('nationalities/create/', views.nationality_create, name='nationality_create'),
    path('nationalities/<int:pk>/', views.nationality_detail, name='nationality_detail'),
    path('nationalities/<int:pk>/edit/', views.nationality_edit, name='nationality_edit'),
    path('nationalities/<int:pk>/delete/', views.nationality_delete, name='nationality_delete'),

    path('', include('landing.urls')),  # Landing page
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 