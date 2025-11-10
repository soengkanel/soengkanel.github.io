from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from company.models import Company, Domain


def tenant_info(request):
    """
    View to display current tenant information for testing/debugging.
    Shows how the tenant parameter system works.
    """
    context = {
        'current_tenant': None,
        'tenant_param': request.GET.get('tenant'),
        'session_tenant': request.session.get('selected_tenant'),
        'available_tenants': [],
        'current_domain': request.get_host(),
    }
    
    # Get current tenant
    if hasattr(request, 'tenant'):
        context['current_tenant'] = {
            'name': request.tenant.name,
            'schema_name': request.tenant.schema_name,
            'id': request.tenant.id,
        }
    
    # Get all available tenants (for switcher)
    try:
        tenants = Company.objects.all().exclude(schema_name='public')
        context['available_tenants'] = [
            {
                'name': t.name,
                'schema_name': t.schema_name,
                'domains': list(t.domains.values_list('domain', flat=True))
            }
            for t in tenants
        ]
    except Exception as e:
        context['error'] = str(e)
    
    # Return JSON response for API calls
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse(context)
    
    # Return HTML response for browser
    return render(request, 'core/tenant_info.html', context)


@login_required
@require_http_methods(['POST'])
def switch_tenant(request):
    """
    AJAX endpoint to switch tenant.
    """
    tenant_code = request.POST.get('tenant')
    
    if not tenant_code:
        return JsonResponse({'error': 'No tenant specified'}, status=400)
    
    try:
        # Try to find the tenant
        tenant = Company.objects.get(schema_name=tenant_code.lower())
        
        # Store in session
        request.session['selected_tenant'] = tenant_code.lower()
        
        return JsonResponse({
            'success': True,
            'tenant': {
                'name': tenant.name,
                'schema_name': tenant.schema_name,
            },
            'redirect_url': f'?tenant={tenant_code.lower()}'
        })
    except Company.DoesNotExist:
        return JsonResponse({'error': f'Tenant {tenant_code} not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def tenant_switcher_data(request):
    """
    API endpoint to get tenant switcher data.
    """
    try:
        tenants = Company.objects.all().exclude(schema_name='public')
        current_tenant = None
        
        if hasattr(request, 'tenant'):
            current_tenant = request.tenant.schema_name
        
        data = {
            'current': current_tenant,
            'tenants': [
                {
                    'name': t.name,
                    'code': t.schema_name,
                    'is_current': t.schema_name == current_tenant
                }
                for t in tenants
            ]
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)