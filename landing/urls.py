from django.urls import path
from . import views
from core.views_landing import landing_page

app_name = 'landing'

urlpatterns = [
    path('', landing_page, name='home'),
    path('simple/', views.simple_landing_page, name='simple_landing'),
    path('old/', views.landing_page_view, name='landing_page'),
] 