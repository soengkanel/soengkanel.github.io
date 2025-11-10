from django import template
from django.utils.http import urlencode
from urllib.parse import urlparse, parse_qs, urlunparse
from django.conf import settings

register = template.Library()

# Setting to control whether to always append tenant parameter to URLs
# Set to True if you want tenant parameter in every URL
# Set to False to rely on cookies for tenant persistence
ALWAYS_APPEND_TENANT = getattr(settings, 'ALWAYS_APPEND_TENANT_PARAM', False)


@register.simple_tag(takes_context=True)
def add_tenant_param(context, url):
    """
    Add tenant parameter to URL if it exists in the current request.
    Usage: {% add_tenant_param '/some/url/' %}
    """
    request = context.get('request')
    if not request:
        return url
    
    # Skip if not configured to always append
    if not ALWAYS_APPEND_TENANT:
        return url
    
    # Check if there's a tenant parameter in the current request
    tenant_param = request.GET.get('tenant')
    if not tenant_param:
        # Check if there's a tenant in cookies
        tenant_param = request.COOKIES.get('selected_tenant')
    
    if not tenant_param:
        return url
    
    # Parse the URL
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    # Add tenant parameter
    params['tenant'] = [tenant_param]
    
    # Rebuild the URL
    new_query = urlencode(params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    
    return urlunparse(new_parsed)


@register.simple_tag(takes_context=True)
def tenant_url(context, url_name, *args, **kwargs):
    """
    Generate URL with tenant parameter preserved.
    Usage: {% tenant_url 'app:view_name' arg1 arg2 %}
    """
    from django.urls import reverse
    
    request = context.get('request')
    
    # Generate the base URL
    url = reverse(url_name, args=args, kwargs=kwargs)
    
    if not request:
        return url
    
    # Skip if not configured to always append
    if not ALWAYS_APPEND_TENANT:
        return url
    
    # Check if there's a tenant parameter in the current request
    tenant_param = request.GET.get('tenant')
    if not tenant_param:
        # Check if there's a tenant in cookies
        tenant_param = request.COOKIES.get('selected_tenant')
    
    if not tenant_param:
        return url
    
    # Add tenant parameter to the URL
    separator = '&' if '?' in url else '?'
    return f"{url}{separator}tenant={tenant_param}"


@register.filter
def preserve_tenant_params(url, request):
    """
    Filter to preserve tenant parameter in URLs.
    Usage: {{ url|preserve_tenant_params:request }}
    """
    if not request:
        return url
    
    # Skip if not configured to always append
    if not ALWAYS_APPEND_TENANT:
        return url
    
    # Check if there's a tenant parameter in the current request
    tenant_param = request.GET.get('tenant')
    if not tenant_param:
        # Check if there's a tenant in cookies
        tenant_param = request.COOKIES.get('selected_tenant')
    
    if not tenant_param:
        return url
    
    # Parse the URL
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    # Add tenant parameter
    params['tenant'] = [tenant_param]
    
    # Rebuild the URL
    new_query = urlencode(params, doseq=True)
    new_parsed = parsed._replace(query=new_query)
    
    return urlunparse(new_parsed)


@register.simple_tag(takes_context=True)
def get_tenant_param(context):
    """
    Get the current tenant parameter value.
    Usage: {% get_tenant_param as tenant %}
    """
    request = context.get('request')
    if not request:
        return ''
    
    # Check if there's a tenant parameter in the current request
    tenant_param = request.GET.get('tenant')
    if not tenant_param:
        # Check if there's a tenant in cookies
        tenant_param = request.COOKIES.get('selected_tenant')
    
    return tenant_param or ''


@register.simple_tag
def should_append_tenant():
    """
    Check if tenant parameters should be appended to all URLs.
    Usage: {% should_append_tenant as append_tenant %}
    """
    return ALWAYS_APPEND_TENANT