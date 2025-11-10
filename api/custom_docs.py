"""
Custom API documentation views that work around static file serving issues
"""
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.views import redirect_to_login
import json

def get_tenant_param(request):
    """Extract tenant parameter from request"""
    return request.GET.get('tenant', 'kk')

def custom_swagger_ui(request):
    """Custom Swagger UI that uses CDN resources"""
    tenant = get_tenant_param(request)

    # Check authentication
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    # Get the schema URL with tenant parameter
    schema_url = f"/api/v1/schema/?tenant={tenant}"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NextHR API Documentation - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css" />
    <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@5.17.14/favicon-32x32.png" sizes="32x32" />
    <style>
        html {{
            box-sizing: border-box;
            overflow: -moz-scrollbars-vertical;
            overflow-y: scroll;
        }}
        *, *:before, *:after {{
            box-sizing: inherit;
        }}
        body {{
            margin:0;
            background: #fafafa;
        }}
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {{
            const ui = SwaggerUIBundle({{
                url: '{schema_url}',
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                persistAuthorization: true,
                displayOperationId: false,
                filter: true,
                tryItOutEnabled: true,
                supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch'],
                onComplete: function() {{
                    console.log('Swagger UI loaded successfully');
                }},
                onFailure: function(error) {{
                    console.error('Swagger UI failed to load:', error);
                }}
            }});
        }}
    </script>
</body>
</html>
"""
    return HttpResponse(html_content, content_type='text/html')

def custom_redoc(request):
    """Custom ReDoc that uses CDN resources"""
    tenant = get_tenant_param(request)

    # Check authentication
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    # Get the schema URL with tenant parameter
    schema_url = f"/api/v1/schema/?tenant={tenant}"

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>NextHR API Documentation - ReDoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
    <style>
        body {{
            margin: 0;
            padding: 0;
        }}
    </style>
</head>
<body>
    <redoc spec-url='{schema_url}'></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.5/bundles/redoc.standalone.js"></script>
</body>
</html>
"""
    return HttpResponse(html_content, content_type='text/html')

def api_home(request):
    """API documentation home page"""
    tenant = get_tenant_param(request)

    # Check authentication
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    base_url = f"{request.scheme}://{request.get_host()}"

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NextHR API Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        .container {{
            background: white;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #007bff;
        }}
        .header h1 {{
            color: #007bff;
            margin-bottom: 10px;
        }}
        .docs-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .doc-card {{
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 20px;
            background: #f8f9fa;
            transition: transform 0.2s;
        }}
        .doc-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .doc-card h3 {{
            color: #007bff;
            margin-top: 0;
        }}
        .btn {{
            display: inline-block;
            background: #007bff;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
            transition: background 0.2s;
        }}
        .btn:hover {{
            background: #0056b3;
        }}
        .btn-secondary {{
            background: #6c757d;
        }}
        .btn-secondary:hover {{
            background: #545b62;
        }}
        .alert {{
            background: #d1ecf1;
            border: 1px solid #bee5eb;
            color: #0c5460;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .endpoints {{
            background: #f8f9fa;
            border-radius: 5px;
            padding: 20px;
            margin: 20px 0;
        }}
        .endpoint {{
            background: white;
            border-left: 4px solid #007bff;
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 0 5px 5px 0;
        }}
        .method {{
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            color: white;
            font-weight: bold;
            margin-right: 10px;
            font-size: 12px;
        }}
        .method.get {{ background: #28a745; }}
        .method.post {{ background: #007bff; }}
        .method.put {{ background: #ffc107; color: #212529; }}
        .method.delete {{ background: #dc3545; }}
        code {{
            background: #e9ecef;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 NextHR API Documentation</h1>
            <p>Comprehensive REST API for Project Management</p>
            <p><strong>Current Tenant:</strong> {tenant} | <strong>User:</strong> {request.user.username}</p>
        </div>

        <div class="alert">
            <strong>🔐 Authentication:</strong> You are logged in and can access all API endpoints.
            All requests include authentication automatically through your browser session.
        </div>

        <div class="docs-grid">
            <div class="doc-card">
                <h3>📚 Interactive Documentation</h3>
                <p><strong>Swagger UI</strong> - Test endpoints directly from your browser with an interactive interface.</p>
                <a href="{base_url}/api/v1/swagger/?tenant={tenant}" class="btn" target="_blank">Open Swagger UI</a>
            </div>

            <div class="doc-card">
                <h3>📖 Clean Documentation</h3>
                <p><strong>ReDoc</strong> - Beautiful, responsive documentation that's easy to read and navigate.</p>
                <a href="{base_url}/api/v1/docs-redoc/?tenant={tenant}" class="btn" target="_blank">Open ReDoc</a>
            </div>

            <div class="doc-card">
                <h3>🔧 API Schema</h3>
                <p><strong>OpenAPI Schema</strong> - Raw schema for importing into Postman, Insomnia, or code generation.</p>
                <a href="{base_url}/api/v1/schema/?tenant={tenant}" class="btn btn-secondary" target="_blank">Download Schema</a>
            </div>
        </div>

        <div class="endpoints">
            <h3>🎯 Quick API Endpoints</h3>

            <div class="endpoint">
                <span class="method get">GET</span>
                <code>{base_url}/api/v1/endpoints/projects/?tenant={tenant}</code>
                <p>List all projects with filtering and pagination</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <code>{base_url}/api/v1/endpoints/projects/stats/?tenant={tenant}</code>
                <p>Get project statistics and dashboard data</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <code>{base_url}/api/v1/endpoints/project-tasks/?tenant={tenant}</code>
                <p>List project tasks with filtering options</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <code>{base_url}/api/v1/endpoints/teams/?tenant={tenant}</code>
                <p>List teams and team management</p>
            </div>

            <div class="endpoint">
                <span class="method get">GET</span>
                <code>{base_url}/api/v1/endpoints/timesheets/?tenant={tenant}</code>
                <p>List timesheets with approval workflows</p>
            </div>
        </div>

        <div style="text-align: center; margin-top: 30px;">
            <p><em>Click the links above to explore the full API documentation and start testing endpoints!</em></p>
        </div>
    </div>
</body>
</html>
"""
    return HttpResponse(html_content, content_type='text/html')