"""
Custom Swagger UI view that uses CDN resources to avoid static file serving issues
"""
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth.views import redirect_to_login

def test_view(request):
    """Simple test view to check if routing works"""
    return HttpResponse("TEST: This is our custom view working!", content_type='text/plain')

@login_required
def swagger_ui_view(request):
    """
    Custom Swagger UI that loads all resources from CDN
    This bypasses Django's static file serving issues in multi-tenant setup
    """
    from django.db import connection
    current_tenant = connection.tenant

    # Schema URL without tenant parameter - django-tenants handles this automatically
    schema_url = "/api/v1/schema/"

    html_content = f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>NextHR API Documentation - Swagger UI</title>
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css" />
    <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@5.17.14/favicon-32x32.png" sizes="32x32" />
    <link rel="icon" type="image/png" href="https://unpkg.com/swagger-ui-dist@5.17.14/favicon-16x16.png" sizes="16x16" />
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
            margin: 0;
            background: #fafafa;
        }}

        .swagger-ui .topbar {{
            background-color: #007bff;
        }}

        .swagger-ui .topbar .download-url-wrapper .select-label {{
            color: white;
        }}

        .swagger-ui .info .title {{
            color: #007bff;
        }}

        /* Custom header */
        .custom-header {{
            background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
            color: white;
            padding: 20px;
            text-align: center;
            margin-bottom: 0;
        }}

        .custom-header h1 {{
            margin: 0;
            font-size: 28px;
            font-weight: 300;
        }}

        .custom-header p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}

        .tenant-info {{
            position: absolute;
            top: 10px;
            right: 20px;
            background: rgba(255,255,255,0.2);
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
        }}
    </style>
</head>

<body>
    <div class="custom-header">
        <div class="tenant-info">
            Tenant: {current_tenant.name if hasattr(current_tenant, 'name') else 'Current Tenant'} | User: {request.user.username}
        </div>
        <h1>🚀 NextHR API Documentation</h1>
        <p>Interactive API testing and documentation powered by Swagger UI</p>
    </div>

    <div id="swagger-ui"></div>

    <script>
        // Load scripts dynamically to ensure proper loading order
        function loadScript(src) {{
            return new Promise((resolve, reject) => {{
                const script = document.createElement('script');
                script.src = src;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            }});
        }}

        // Load Swagger UI scripts in sequence
        Promise.all([
            loadScript('https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js'),
            loadScript('https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-standalone-preset.js')
        ]).then(() => {{
            console.log('Swagger UI scripts loaded successfully');
            initSwaggerUI();
        }}).catch((error) => {{
            console.error('Failed to load Swagger UI scripts:', error);
            showError();
        }});

        function initSwaggerUI() {{
            console.log('Initializing Swagger UI...');

            // Double-check if SwaggerUIBundle is available
            if (typeof SwaggerUIBundle === 'undefined') {{
                console.error('SwaggerUIBundle still not available after loading');
                showError();
                return;
            }}

            // SwaggerUIBundle is the main object
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

                // Enhanced settings for better experience
                persistAuthorization: true,
                displayOperationId: false,
                displayRequestDuration: true,
                filter: true,
                tryItOutEnabled: true,
                supportedSubmitMethods: ['get', 'post', 'put', 'delete', 'patch', 'head', 'options'],

                // Success callback
                onComplete: function() {{
                    console.log('Swagger UI loaded successfully!');

                    // Add custom styling after load
                    setTimeout(function() {{
                        // Customize the UI after it's fully loaded
                        const topbar = document.querySelector('.swagger-ui .topbar');
                        if (topbar) {{
                            topbar.style.display = 'none'; // Hide default topbar since we have custom header
                        }}
                    }}, 1000);
                }},

                // Error callback
                onFailure: function(error) {{
                    console.error('Failed to load Swagger UI:', error);

                    // Show user-friendly error message
                    const container = document.getElementById('swagger-ui');
                    container.innerHTML = `
                        <div style="padding: 40px; text-align: center; background: white; margin: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                            <h2 style="color: #dc3545; margin-bottom: 20px;">⚠️ Failed to Load API Documentation</h2>
                            <p style="margin-bottom: 20px;">There was an error loading the API schema. This might be due to:</p>
                            <ul style="text-align: left; max-width: 500px; margin: 0 auto 20px auto;">
                                <li>Authentication issues (make sure you're logged in)</li>
                                <li>Network connectivity problems</li>
                                <li>Server configuration issues</li>
                            </ul>
                            <p style="margin-bottom: 20px;"><strong>Schema URL:</strong> <code>{schema_url}</code></p>
                            <div style="margin-top: 30px;">
                                <a href="{schema_url}" target="_blank" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-right: 10px;">View Raw Schema</a>
                                <button onclick="location.reload()" style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Retry</button>
                            </div>
                            <p style="margin-top: 20px; font-size: 14px; color: #666;">
                                Alternative: <a href="/api/v1/endpoints/">Browse API Endpoints</a>
                            </p>
                        </div>
                    `;
                }}
            }});

            // Store UI instance globally for debugging
            window.ui = ui;
        }}

        function showError() {{
            const container = document.getElementById('swagger-ui');
            container.innerHTML = `
                <div style="padding: 40px; text-align: center; background: white; margin: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h2 style="color: #dc3545; margin-bottom: 20px;">⚠️ Failed to Load Swagger UI</h2>
                    <p style="margin-bottom: 20px;">Unable to load the Swagger UI JavaScript libraries from CDN.</p>
                    <p style="margin-bottom: 20px;">This might be due to:</p>
                    <ul style="text-align: left; max-width: 500px; margin: 0 auto 20px auto;">
                        <li>Network connectivity issues</li>
                        <li>CDN being blocked or unavailable</li>
                        <li>Browser security restrictions</li>
                    </ul>
                    <div style="margin-top: 30px;">
                        <a href="{schema_url}" target="_blank" style="background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin-right: 10px;">View Raw Schema</a>
                        <button onclick="location.reload()" style="background: #28a745; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;">Retry</button>
                    </div>
                    <p style="margin-top: 20px; font-size: 14px; color: #666;">
                        Alternative: <a href="/api/v1/endpoints/">Browse API Endpoints</a>
                    </p>
                </div>
            `;
        }}
    </script>
</body>
</html>
'''

    return HttpResponse(html_content, content_type='text/html')


@login_required
def swagger_ui_template(request):
    """
    Swagger UI using Django template
    """
    # Get tenant from the current connection context
    from django.db import connection
    current_tenant = connection.tenant

    # Schema URL without tenant parameter - django-tenants handles this automatically
    schema_url = "/api/v1/schema/"

    context = {
        'tenant': current_tenant.name if hasattr(current_tenant, 'name') else 'Current Tenant',
        'schema_url': schema_url,
        'user': request.user,
    }

    return render(request, 'swagger_ui.html', context)


def swagger_ui_simple(request):
    """
    Simpler Swagger UI without authentication check for testing
    """
    schema_url = "/api/v1/schema/"

    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>NextHR API - Swagger UI</title>
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui.css" />
</head>
<body>
    <div id="swagger-ui"></div>
    <script>
        function loadScript(src) {{
            return new Promise((resolve, reject) => {{
                const script = document.createElement('script');
                script.src = src;
                script.onload = resolve;
                script.onerror = reject;
                document.head.appendChild(script);
            }});
        }}

        loadScript('https://unpkg.com/swagger-ui-dist@5.17.14/swagger-ui-bundle.js')
            .then(() => {{
                SwaggerUIBundle({{
                    url: '{schema_url}',
                    dom_id: '#swagger-ui',
                    presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.presets.standalone]
                }});
            }})
            .catch((error) => {{
                console.error('Failed to load Swagger UI:', error);
                document.getElementById('swagger-ui').innerHTML = '<p>Failed to load Swagger UI</p>';
            }});
    </script>
</body>
</html>
'''

    return HttpResponse(html_content, content_type='text/html')