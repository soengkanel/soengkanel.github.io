from django_tenants.utils import get_tenant
from .models import Company


def get_current_company(request=None):
    """
    Get the current company information for the tenant
    Returns a dictionary with company details for use in templates
    """
    try:
        if request:
            current_company = get_tenant(request)
        else:
            # Fallback to first company if no request context
            current_company = Company.objects.first()
        
        if not isinstance(current_company, Company):
            current_company = Company.objects.first()
        
        if not current_company:
            # Return default company info if no company found
            return {
                'name': 'Your Company Name',
                'tagline': 'Professional Services',
                'address': '123 Business Street, City, State 12345',
                'phone': '(555) 123-4567',
                'email': 'info@company.com',
                'website': 'www.company.com',
                'logo': None,
                'full_address': '123 Business Street, City, State 12345',
            }
        
        # Build tagline from company type or description
        tagline = current_company.get_company_type_display()
        if current_company.description:
            tagline = current_company.description[:50] + ('...' if len(current_company.description) > 50 else '')
        
        return {
            'name': current_company.name,
            'tagline': tagline,
            'address': current_company.full_address,
            'phone': current_company.phone_number or '(555) 123-4567',
            'email': current_company.email or 'info@company.com',
            'website': current_company.website or 'www.company.com',
            'logo': current_company.logo,
            'full_address': current_company.full_address,
            'registration_number': current_company.registration_number,
            'tax_id': current_company.tax_id,
            'established_date': current_company.established_date,
        }
    
    except Exception as e:

    
        pass
        # Return default values if any error occurs
        return {
            'name': 'Your Company Name',
            'tagline': 'Professional Services',
            'address': '123 Business Street, City, State 12345',
            'phone': '(555) 123-4567',
            'email': 'info@company.com',
            'website': 'www.company.com',
            'logo': None,
            'full_address': '123 Business Street, City, State 12345',
        }


def get_company_context(request=None):
    """
    Get company context for templates with proper naming
    """
    company_info = get_current_company(request)
    
    return {
        'company_name': company_info['name'],
        'company_tagline': company_info['tagline'],
        'company_address': company_info['address'],
        'company_phone': company_info['phone'],
        'company_email': company_info['email'],
        'company_website': company_info['website'],
        'company_logo': company_info['logo'],
        'company_full_address': company_info['full_address'],
        'company_registration_number': company_info.get('registration_number'),
        'company_tax_id': company_info.get('tax_id'),
        'company_established_date': company_info.get('established_date'),
    }