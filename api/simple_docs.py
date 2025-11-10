"""
Simple API documentation view that works without static file dependencies
"""
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.template import Template, Context
import json

SIMPLE_API_DOCS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NextHR API Documentation</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }
        .container { max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden; }
        .header { background: #007bff; color: white; padding: 20px; }
        .content { padding: 20px; }
        .endpoint { background: #f8f9fa; border-left: 4px solid #007bff; padding: 15px; margin: 10px 0; border-radius: 4px; }
        .method { display: inline-block; padding: 4px 8px; border-radius: 4px; color: white; font-weight: bold; margin-right: 10px; }
        .method.get { background: #28a745; }
        .method.post { background: #007bff; }
        .method.put { background: #ffc107; color: #212529; }
        .method.delete { background: #dc3545; }
        .url { font-family: monospace; background: #e9ecef; padding: 2px 6px; border-radius: 3px; }
        .nav { background: #e9ecef; padding: 10px 20px; border-bottom: 1px solid #dee2e6; }
        .nav a { margin-right: 20px; text-decoration: none; color: #007bff; }
        .nav a:hover { text-decoration: underline; }
        .section { margin: 30px 0; }
        .auth-note { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; padding: 15px; border-radius: 4px; margin: 20px 0; }
        .test-button { background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-left: 10px; }
        .test-button:hover { background: #218838; }
        #test-results { background: #f8f9fa; border: 1px solid #dee2e6; padding: 15px; margin-top: 20px; border-radius: 4px; display: none; }
        .code { background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 4px; overflow-x: auto; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>NextHR Project Management API</h1>
            <p>Comprehensive REST API for project management, tasks, teams, and timesheets</p>
        </div>

        <div class="nav">
            <a href="#authentication">Authentication</a>
            <a href="#projects">Projects</a>
            <a href="#tasks">Tasks</a>
            <a href="#teams">Teams</a>
            <a href="#timesheets">Timesheets</a>
            <a href="#testing">Testing</a>
        </div>

        <div class="content">
            <div class="auth-note">
                <strong>🔐 Authentication Required:</strong> All API endpoints require authentication.
                Login to your account before using the API. Current user: <strong>{{ user.username|default:"Not logged in" }}</strong>
            </div>

            <div class="section" id="authentication">
                <h2>Authentication</h2>
                <p>This API uses session authentication. Login through the web interface first.</p>
                <div class="endpoint">
                    <strong>Login URL:</strong> <span class="url">{{ request.scheme }}://{{ request.get_host }}/admin/</span>
                </div>
            </div>

            <div class="section" id="projects">
                <h2>Projects API</h2>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="url">{{ base_url }}/projects/</span>
                    <button class="test-button" onclick="testEndpoint('{{ base_url }}/projects/', 'GET')">Test</button>
                    <p>List all projects with filtering and search capabilities</p>
                </div>

                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="url">{{ base_url }}/projects/</span>
                    <p>Create a new project</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="url">{{ base_url }}/projects/{id}/</span>
                    <p>Get detailed information about a specific project</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="url">{{ base_url }}/projects/stats/</span>
                    <button class="test-button" onclick="testEndpoint('{{ base_url }}/projects/stats/', 'GET')">Test</button>
                    <p>Get project statistics (counts, budgets, completion rates)</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="url">{{ base_url }}/projects/{id}/timeline/</span>
                    <p>Get project timeline with tasks and milestones</p>
                </div>
            </div>

            <div class="section" id="tasks">
                <h2>Tasks API</h2>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="url">{{ base_url }}/project-tasks/</span>
                    <button class="test-button" onclick="testEndpoint('{{ base_url }}/project-tasks/', 'GET')">Test</button>
                    <p>List all project tasks</p>
                </div>

                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="url">{{ base_url }}/project-tasks/{id}/update_progress/</span>
                    <p>Update task progress (0-100%)</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="url">{{ base_url }}/project-milestones/</span>
                    <button class="test-button" onclick="testEndpoint('{{ base_url }}/project-milestones/', 'GET')">Test</button>
                    <p>List project milestones</p>
                </div>
            </div>

            <div class="section" id="teams">
                <h2>Teams API</h2>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="url">{{ base_url }}/teams/</span>
                    <button class="test-button" onclick="testEndpoint('{{ base_url }}/teams/', 'GET')">Test</button>
                    <p>List all teams</p>
                </div>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="url">{{ base_url }}/teams/{id}/members/</span>
                    <p>Get team members</p>
                </div>
            </div>

            <div class="section" id="timesheets">
                <h2>Timesheets API</h2>

                <div class="endpoint">
                    <span class="method get">GET</span>
                    <span class="url">{{ base_url }}/timesheets/</span>
                    <button class="test-button" onclick="testEndpoint('{{ base_url }}/timesheets/', 'GET')">Test</button>
                    <p>List timesheets</p>
                </div>

                <div class="endpoint">
                    <span class="method post">POST</span>
                    <span class="url">{{ base_url }}/timesheets/{id}/submit/</span>
                    <p>Submit timesheet for approval</p>
                </div>
            </div>

            <div class="section" id="testing">
                <h2>API Testing</h2>
                <p>Click the "Test" buttons above to try the API endpoints directly from this page.</p>

                <h3>Example with cURL:</h3>
                <div class="code">
# Get projects list
curl -H "Cookie: sessionid=your-session-id" \\
     "{{ base_url }}/projects/"

# Get project statistics
curl -H "Cookie: sessionid=your-session-id" \\
     "{{ base_url }}/projects/stats/"
                </div>

                <h3>Example with Python:</h3>
                <div class="code">
import requests

# After logging in through web interface
session = requests.Session()
response = session.get("{{ base_url }}/projects/")
print(response.json())
                </div>

                <div id="test-results">
                    <h4>Test Results:</h4>
                    <pre id="result-content"></pre>
                </div>
            </div>

            <div class="section">
                <h2>External Documentation</h2>
                <p>For interactive API testing, try these external tools:</p>
                <ul>
                    <li><strong>ReDoc:</strong> <a href="{{ request.scheme }}://{{ request.get_host }}/api/v1/redoc/?tenant={{ tenant }}" target="_blank">{{ request.scheme }}://{{ request.get_host }}/api/v1/redoc/?tenant={{ tenant }}</a></li>
                    <li><strong>OpenAPI Schema:</strong> <a href="{{ request.scheme }}://{{ request.get_host }}/api/v1/schema/?tenant={{ tenant }}" target="_blank">{{ request.scheme }}://{{ request.get_host }}/api/v1/schema/?tenant={{ tenant }}</a></li>
                    <li><strong>Browsable API:</strong> <a href="{{ base_url }}/" target="_blank">{{ base_url }}/</a></li>
                </ul>
            </div>
        </div>
    </div>

    <script>
        async function testEndpoint(url, method) {
            const resultDiv = document.getElementById('test-results');
            const resultContent = document.getElementById('result-content');

            resultDiv.style.display = 'block';
            resultContent.textContent = 'Loading...';

            try {
                const response = await fetch(url, {
                    method: method,
                    credentials: 'same-origin',
                    headers: {
                        'Accept': 'application/json'
                    }
                });

                const data = await response.json();
                resultContent.textContent = JSON.stringify(data, null, 2);
            } catch (error) {
                resultContent.textContent = 'Error: ' + error.message;
            }
        }
    </script>
</body>
</html>
"""

@login_required
def simple_api_docs(request):
    """Simple API documentation that works without external dependencies"""
    tenant = request.GET.get('tenant', 'kk')
    base_url = f"{request.scheme}://{request.get_host()}/api/v1/endpoints"

    # If tenant parameter is provided, add it to the base URL
    if tenant:
        base_url += f"?tenant={tenant}"

    template = Template(SIMPLE_API_DOCS_TEMPLATE)
    context = Context({
        'request': request,
        'user': request.user,
        'base_url': base_url,
        'tenant': tenant,
    })

    return HttpResponse(template.render(context))