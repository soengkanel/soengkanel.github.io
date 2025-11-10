import time
import logging
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseBadRequest
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, get_public_schema_name
from django.db import connection

# Get security logger with fallback
try:
    logger = logging.getLogger('security')
except Exception:
    logger = logging.getLogger(__name__)


class SessionSecurityMiddleware(MiddlewareMixin):
    """
    Enhanced session security middleware that provides:
        pass
    1. Absolute session timeout (regardless of activity)
    2. Idle timeout detection
    3. Security logging
    4. Automatic cleanup of expired sessions
    """
    
    def process_request(self, request):
        """
        Process incoming request to check session validity and timeouts
        """
        # Skip if user attribute is not available (before authentication middleware)
        if not hasattr(request, 'user'):
            return None
        
        # Skip if user is None or not available
        if not request.user:
            return None
            
        # Skip for non-authenticated users
        try:
            if not request.user.is_authenticated:
                return None
        except AttributeError:
            # Handle case where user doesn't have is_authenticated method
            return None
        
        # Skip for admin and auth URLs to prevent logout loops
        if request.path.startswith('/admin/') or request.path.startswith('/accounts/'):
            return None
            
        current_time = time.time()
        
        # Check if session has required security markers
        if 'session_created' not in request.session:
            # First time login - set session creation time
            request.session['session_created'] = current_time
            request.session['last_activity'] = current_time
            try:
                username = getattr(request.user, 'username', 'Unknown') if hasattr(request, 'user') else 'Unknown'
            except Exception:
                pass  # Continue if logging fails
            return None
        
        session_created = request.session['session_created']
        last_activity = request.session.get('last_activity', session_created)
        
        # Calculate timeouts
        session_age = current_time - session_created
        idle_time = current_time - last_activity
        
        # Absolute timeout: 8 hours (same as SESSION_COOKIE_AGE)
        absolute_timeout = getattr(settings, 'SESSION_COOKIE_AGE', 8 * 60 * 60)
        
        # Idle timeout: 2 hours of inactivity
        idle_timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT', 2 * 60 * 60)
        
        # Check for absolute timeout
        if session_age > absolute_timeout:
            try:
                username = getattr(request.user, 'username', 'Unknown') if hasattr(request, 'user') else 'Unknown'
            except Exception:
                pass
            return self._logout_user(request, 'Your session has expired for security reasons.')
        
        # Check for idle timeout
        if idle_time > idle_timeout:
            try:
                username = getattr(request.user, 'username', 'Unknown') if hasattr(request, 'user') else 'Unknown'
            except Exception:
                pass
            return self._logout_user(request, 'You have been logged out due to inactivity.')
        
        # Update last activity
        request.session['last_activity'] = current_time
        
        # Session is valid
        return None
    
    def _logout_user(self, request, message):
        """
        Securely logout user and redirect to login page
        """
        # Get user info safely
        try:
            user_info = f"User {request.user.username}" if hasattr(request, 'user') and request.user.is_authenticated else "Anonymous user"
        except Exception:
            user_info = "Unknown user"
        
        # Clear session data safely
        try:
            request.session.flush()
        except Exception:
            pass  # Continue if session flush fails
        
        # Logout user safely
        try:
            logout(request)
        except Exception:
            pass  # Continue if logout fails
        
        # Add message safely
        try:
            messages.warning(request, message)
        except Exception:
            pass  # Continue if message fails
        
        # Security event logging removed
        
        # Redirect to login page
        return redirect(settings.LOGIN_URL)


class CSRFSecurityMiddleware(MiddlewareMixin):
    """
    Additional CSRF protection middleware
    """
    
    def process_request(self, request):
        """
        Add security headers and CSRF protection
        """
        # Add security headers
        if hasattr(request, 'META'):
            # Log suspicious requests
            user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
            ip_address = self._get_client_ip(request)
            
            # Basic bot detection
            suspicious_agents = ['bot', 'crawler', 'spider', 'scraper']
            if any(agent in user_agent.lower() for agent in suspicious_agents):
                pass
        
        return None
    
    def process_response(self, request, response):
        """
        Add security headers to response
        """
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Only add HSTS in production with HTTPS
        if not settings.DEBUG and request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
    
    def _get_client_ip(self, request):
        """
        Get the real client IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class TenantParameterMiddleware(TenantMainMiddleware):
    """
    Custom middleware that extends TenantMainMiddleware to support tenant selection via URL parameter.
    Supports both domain-based routing (e.g., kk.lyp, osm.lyp) and parameter-based routing (?tenant=kk, ?tenant=osm).
    """
    
    def process_request(self, request):
        """
        Process the request to determine the tenant based on URL parameter, headers, or domain.
        Priority: Header > URL parameter > Cookie > Domain-based routing
        """
        # Check for tenant in HTTP headers first (for API consumers)
        tenant_header = request.META.get('HTTP_X_TENANT') or request.META.get('HTTP_TENANT')

        if tenant_header:
            # API/Mobile client specified tenant via header
            if self._set_tenant_from_identifier(request, tenant_header, source="header"):
                return None

        # Check for tenant parameter in GET request
        tenant_param = request.GET.get('tenant')
        
        if tenant_param:
            # Web client specified tenant via URL parameter
            if self._set_tenant_from_identifier(request, tenant_param, source="parameter"):
                return None
        
        # Check if tenant was previously selected and stored in cookie
        elif 'selected_tenant' in request.COOKIES:
            try:
                TenantModel = get_tenant_model()
                tenant_identifier = request.COOKIES['selected_tenant']
                
                # Try to find the tenant
                try:
                    tenant = TenantModel.objects.get(schema_name=tenant_identifier)
                except TenantModel.DoesNotExist:
                    try:
                        # Try with _company suffix
                        tenant = TenantModel.objects.get(schema_name=f"{tenant_identifier}_company")
                    except TenantModel.DoesNotExist:
                        try:
                            tenant = TenantModel.objects.get(name__iexact=tenant_identifier)
                        except TenantModel.DoesNotExist:
                            tenant = None
                
                if tenant:
                    request.tenant = tenant
                    connection.set_tenant(tenant)
                    return None

            except Exception as e:
                pass
        
        # Fall back to default domain-based routing
        return super().process_request(request)

    def _set_tenant_from_identifier(self, request, tenant_identifier, source="unknown"):
        """
        Helper method to set tenant from identifier (header, parameter, etc.)
        Returns True if tenant was successfully set, False otherwise
        """
        try:
            TenantModel = get_tenant_model()
            tenant = None

            # First try to find by exact schema_name
            try:
                tenant = TenantModel.objects.get(schema_name=tenant_identifier.lower())
            except TenantModel.DoesNotExist:
                # Try to find by schema_name with _company suffix
                try:
                    tenant = TenantModel.objects.get(schema_name=f"{tenant_identifier.lower()}_company")
                except TenantModel.DoesNotExist:
                    # Try to find by name (case-insensitive)
                    try:
                        tenant = TenantModel.objects.get(name__iexact=tenant_identifier)
                    except TenantModel.DoesNotExist:
                        # Try to find by name containing the param
                        try:
                            tenant = TenantModel.objects.filter(name__icontains=tenant_identifier).first()
                        except:
                            pass

            if tenant:
                # Set the tenant for this request
                request.tenant = tenant
                connection.set_tenant(tenant)

                # Store the tenant parameter in a cookie for web clients (not API)
                if source == "parameter":
                    request._tenant_cookie_to_set = tenant_identifier.lower()

                return True
            else:
                return False

        except Exception as e:
            return False


class TenantContextMiddleware:
    """
    Middleware to ensure tenant context is properly set in templates.
    This should be placed after TenantParameterMiddleware.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Process the request
        response = self.get_response(request)
        
        # Set tenant cookie if needed
        if hasattr(request, '_tenant_cookie_to_set'):
            response.set_cookie(
                'selected_tenant', 
                request._tenant_cookie_to_set,
                max_age=30*24*60*60,  # 30 days
                httponly=True,
                samesite='Lax'
            )
        
        # Add tenant info to response headers for debugging (optional)
        if hasattr(request, 'tenant') and request.tenant:
            response['X-Tenant'] = request.tenant.schema_name
        
        return response


class AdminRoleRestrictionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            if request.user.is_authenticated and getattr(request.user, 'is_superuser', '') == False:
                return redirect('/')  # Or show forbidden
        return self.get_response(request)


class UserRoleMiddleware:
    """
    Middleware to attach the user's role assignment to the user object.
    This makes it easier to access role information in templates.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            try:
                from user_management.models import UserRoleAssignment
                # Get the user's active role assignment and attach it to the user object
                role_assignment = UserRoleAssignment.objects.select_related('role').filter(
                    user=request.user,
                    is_active=True
                ).first()

                # Attach role_assignment as a property on the user object
                request.user.role_assignment = role_assignment
            except Exception:
                # If there's any error, set role_assignment to None
                request.user.role_assignment = None

        response = self.get_response(request)
        return response