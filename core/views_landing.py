from django.shortcuts import render, redirect
from django.views.generic import TemplateView

class LandingPageView(TemplateView):
    """Landing page view for the HRMS system."""
    template_name = 'landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'NGHR - Modern HR Management System'
        return context

def landing_page(request):
    """Function-based view for the landing page.

    Redirects authenticated users to their appropriate dashboard:
    - Staff/Admin users -> Admin dashboard (/dashboard/)
    - Regular employees -> Employee portal (/employee/)
    """
    # If user is authenticated, redirect to appropriate dashboard
    if request.user.is_authenticated:
        # Staff and admins go to admin dashboard
        if request.user.is_staff or request.user.is_superuser:
            return redirect('dashboard:home')
        # Regular employees go to employee portal
        else:
            return redirect('employee_portal:dashboard')

    # Non-authenticated users see the landing page
    return render(request, 'landing.html', {
        'title': 'NGHR - Modern HR Management System'
    })