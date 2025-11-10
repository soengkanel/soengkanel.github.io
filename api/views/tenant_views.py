"""
Tenant management API views for NextHR.

This module contains all views related to tenant management,
including tenant information, available tenants, and API overview.
"""
from django.shortcuts import render
from django.contrib.auth.views import redirect_to_login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def tenant_info_api(request):
    """
    API endpoint to get current tenant information.
    This helps clients understand which tenant context they're operating in.
    """
    current_tenant = connection.tenant

    tenant_data = {
        'tenant_name': current_tenant.name if hasattr(current_tenant, 'name') else str(current_tenant),
        'tenant_schema': current_tenant.schema_name if hasattr(current_tenant, 'schema_name') else 'unknown',
        'user': request.user.username,
        'is_authenticated': request.user.is_authenticated,
        'message': 'All API operations will be scoped to this tenant automatically',
        'api_behavior': {
            'GET_requests': 'Return only data belonging to this tenant',
            'POST_requests': 'Create new records automatically assigned to this tenant',
            'PUT_PATCH_requests': 'Update only records belonging to this tenant',
            'DELETE_requests': 'Delete only records belonging to this tenant'
        },
        'mobile_api_usage': {
            'method_1_header': 'Send X-Tenant: kk in HTTP headers',
            'method_2_parameter': 'Add ?tenant=kk to all API URLs',
            'method_3_subdomain': 'Use kk.yourdomain.com as base URL'
        }
    }

    return JsonResponse(tenant_data)


@api_view(['GET'])
def available_tenants_api(request):
    """
    API endpoint for mobile/API clients to discover available tenants.
    No authentication required for discovery.
    """
    from django_tenants.utils import get_tenant_model

    TenantModel = get_tenant_model()

    try:
        # Get all active tenants (excluding public schema)
        tenants = TenantModel.objects.exclude(schema_name='public').filter(
            schema_name__isnull=False
        ).values('schema_name', 'name')

        tenant_list = []
        for tenant in tenants:
            # Clean schema name for API consumers
            clean_name = tenant['schema_name'].replace('_company', '')
            tenant_list.append({
                'tenant_id': clean_name,
                'tenant_name': tenant['name'],
                'schema_name': tenant['schema_name'],
                'api_usage': {
                    'header': f'X-Tenant: {clean_name}',
                    'parameter': f'?tenant={clean_name}',
                    'example_url': f'/api/v1/projects/?tenant={clean_name}'
                }
            })

        return JsonResponse({
            'available_tenants': tenant_list,
            'total_tenants': len(tenant_list),
            'usage_instructions': {
                'method_1': 'Add X-Tenant header to all requests',
                'method_2': 'Add ?tenant=<tenant_id> parameter to URLs',
                'authentication': 'Include Authorization: Bearer <token> header',
                'example_request': {
                    'url': '/api/v1/projects/',
                    'headers': {
                        'X-Tenant': 'kk',
                        'Authorization': 'Bearer your-api-token',
                        'Content-Type': 'application/json'
                    }
                }
            }
        })

    except Exception as e:
        return JsonResponse({
            'error': 'Unable to fetch tenant information',
            'message': str(e)
        }, status=500)


@csrf_exempt
def api_overview(request):
    """Display API documentation overview page or return API info"""
    # If requesting JSON, return API information
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'message': 'Welcome to NextHR API',
            'version': '1.0.0',
            'documentation': {
                'swagger': request.build_absolute_uri('/api/v1/docs/'),
                'redoc': request.build_absolute_uri('/api/v1/redoc/'),
                'schema': request.build_absolute_uri('/api/v1/schema/')
            },
            'endpoints': {
                'projects': request.build_absolute_uri('/api/v1/endpoints/projects/'),
                'tasks': request.build_absolute_uri('/api/v1/endpoints/project-tasks/'),
                'milestones': request.build_absolute_uri('/api/v1/endpoints/project-milestones/'),
                'teams': request.build_absolute_uri('/api/v1/endpoints/teams/'),
                'timesheets': request.build_absolute_uri('/api/v1/endpoints/timesheets/'),
            }
        })

    # For HTML requests, check if user is authenticated
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    # Render the HTML overview page
    try:
        return render(request, 'api/api_overview.html')
    except Exception as e:
        # Fallback to JSON response if template is not found
        return JsonResponse({
            'error': 'Template not found',
            'message': 'Please access the API documentation at /api/v1/docs/ or /api/v1/redoc/',
            'documentation_urls': {
                'swagger': request.build_absolute_uri('/api/v1/docs/'),
                'redoc': request.build_absolute_uri('/api/v1/redoc/'),
                'schema': request.build_absolute_uri('/api/v1/schema/')
            }
        }, status=500)