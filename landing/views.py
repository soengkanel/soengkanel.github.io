from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import login_required

# Create your views here.

def zen_landing_page(request):
    """Zen-style minimalist landing page"""
    context = {
        'page_title': 'GuanYu - Find Your Balance',
    }
    return render(request, 'landing/zen_landing.html', context)

def simple_landing_page(request):
    """Simple landing page for internal system"""
    # Get tenant name from request if available
    tenant_name = 'GuanYu'  # Default fallback
    system_title = 'GuanYu System'
    
    if hasattr(request, 'tenant') and request.tenant:
        tenant_name = request.tenant.name
        system_title = f"{tenant_name} System"
    
    context = {
        'tenant_name': tenant_name,
        'system_title': system_title
    }
    return render(request, 'landing/simple_landing.html', context)

def landing_page_view(request):
    from django.utils import timezone
    
    is_dev = getattr(settings, 'DEV_ENV', False)
    show_footer = getattr(settings, 'SHOW_ENV_FOOTER', False)
    
    context = {
        'show_env_footer': show_footer,
        'env_name': 'Development' if is_dev else 'Production',
        'build_time': timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return render(request, 'landing/landing_page.html', context)


def newsletter_subscribe(request):
    """Handle newsletter subscription via HTMX"""
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Simulate processing time
        time.sleep(0.5)
        
        if email and '@' in email:
            # Here you would typically save to database or send to email service
            return HttpResponse("""
                <div class="p-4 bg-green-100 border border-green-300 rounded-lg text-green-700">
                    <div class="flex items-center">
                        <i class="fas fa-check-circle mr-2"></i>
                        <span>Thank you! We'll keep you updated with our latest news.</span>
                    </div>
                </div>
            """)
        else:
            return HttpResponse("""
                <div class="p-4 bg-red-100 border border-red-300 rounded-lg text-red-700">
                    <div class="flex items-center">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        <span>Please enter a valid email address.</span>
                    </div>
                </div>
            """)
    
    return HttpResponse('')


def contact_form(request):
    """Handle contact form via HTMX"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # Simulate processing time
        time.sleep(1)
        
        if name and email and message and '@' in email:
            # Here you would typically save to database or send email
            return HttpResponse("""
                <div class="text-center p-6">
                    <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-500 mb-4">
                        <i class="fas fa-check text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-medium text-gray-900 mb-2">Message Sent!</h3>
                    <p class="text-gray-600">Thanks for reaching out. We'll get back to you within 24 hours.</p>
                </div>
            """)
        else:
            return HttpResponse("""
                <div class="p-4 bg-red-100 border border-red-300 rounded-lg text-red-700 mb-4">
                    <div class="flex items-center">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        <span>Please fill in all fields with valid information.</span>
                    </div>
                </div>
            """)
    
    # Return the contact form
    return HttpResponse("""
        <form hx-post="/contact-form/" hx-target="#contact-form-container" hx-indicator="#contact-loading">
            <div class="space-y-4">
                <div>
                    <label for="name" class="block text-sm font-medium text-gray-700 mb-1">Name</label>
                    <input type="text" id="name" name="name" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
                <div>
                    <label for="email" class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                    <input type="email" id="email" name="email" required
                           class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
                <div>
                    <label for="message" class="block text-sm font-medium text-gray-700 mb-1">Message</label>
                    <textarea id="message" name="message" rows="4" required
                              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"></textarea>
                </div>
                <div>
                    <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors duration-300">
                        Send Message
                    </button>
                </div>
            </div>
        </form>
        <div id="contact-loading" class="htmx-indicator">
            <div class="flex items-center justify-center p-4">
                <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span class="ml-2 text-sm text-gray-600">Sending message...</span>
            </div>
        </div>
    """)


def load_testimonials(request):
    """Load testimonials dynamically via HTMX"""
    # Simulate loading time
    time.sleep(0.8)
    
    testimonials = [
        {
            "name": "Sarah Johnson",
            "company": "TechCorp Inc.",
            "text": "L.Y.P. Group transformed our operations completely. The efficiency gains are remarkable.",
            "rating": 5
        },
        {
            "name": "Michael Chen",
            "company": "StartupXYZ",
            "text": "Outstanding service and support. Their solution saved us countless hours every week.",
            "rating": 5
        },
        {
            "name": "Emily Davis",
            "company": "Global Solutions",
            "text": "The automation features are incredible. We've seen a 40% increase in productivity.",
            "rating": 5
        }
    ]
    
    html = ""
    for testimonial in testimonials:
        stars = "★" * testimonial["rating"]
        html += f"""
            <div class="bg-white p-6 rounded-lg shadow-sm border scroll-fade-in">
                <div class="flex items-center mb-4">
                    <div class="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <span class="text-blue-600 font-medium">{testimonial["name"][0]}</span>
                    </div>
                    <div class="ml-3">
                        <h4 class="text-sm font-medium text-gray-900">{testimonial["name"]}</h4>
                        <p class="text-xs text-gray-500">{testimonial["company"]}</p>
                    </div>
                </div>
                <div class="text-yellow-400 text-sm mb-2">{stars}</div>
                <p class="text-gray-600 text-sm">"{testimonial["text"]}"</p>
            </div>
        """
    
    return HttpResponse(html)


def feature_details(request, feature_id):
    """Load feature details dynamically via HTMX"""
    features = {
        "automation": {
            "title": "Advanced Automation",
            "description": "Streamline your workflow with intelligent automation that learns from your patterns and optimizes processes automatically.",
            "benefits": [
                "Reduce manual tasks by up to 80%",
                "Eliminate human errors",
                "24/7 automated operations",
                "Smart scheduling and prioritization"
            ]
        },
        "analytics": {
            "title": "Powerful Analytics",
            "description": "Get deep insights into your business performance with comprehensive analytics and real-time reporting.",
            "benefits": [
                "Real-time dashboards",
                "Predictive analytics",
                "Custom report generation",
                "Performance tracking"
            ]
        },
        "security": {
            "title": "Enterprise Security",
            "description": "Your data is protected with bank-level security measures and compliance with industry standards.",
            "benefits": [
                "End-to-end encryption",
                "Regular security audits",
                "Compliance with GDPR, SOC2",
                "Role-based access control"
            ]
        }
    }
    
    feature = features.get(feature_id)
    if not feature:
        return HttpResponse("Feature not found")
    
    # Simulate loading time
    time.sleep(0.5)
    
    benefits_html = ""
    for benefit in feature["benefits"]:
        benefits_html += f"""
            <li class="flex items-center">
                <i class="fas fa-check text-green-500 mr-2"></i>
                <span>{benefit}</span>
            </li>
        """
    
    return HttpResponse(f"""
        <div class="bg-white p-6 rounded-lg border">
            <h3 class="text-xl font-semibold text-gray-900 mb-3">{feature["title"]}</h3>
            <p class="text-gray-600 mb-4">{feature["description"]}</p>
            <ul class="space-y-2 text-sm">
                {benefits_html}
            </ul>
        </div>
    """)

