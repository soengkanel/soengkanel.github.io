import uuid
import traceback
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from auditlog.signals import post_log


class EnhancedAuditMiddleware(MiddlewareMixin):
    """Enhanced audit middleware that integrates with django-auditlog"""
    
    def process_request(self, request):
        # Generate correlation ID
        correlation_id = request.META.get('HTTP_X_CORRELATION_ID', str(uuid.uuid4()))
        request.correlation_id = correlation_id
        
        # Update audit session for authenticated users
        if request.user.is_authenticated:
            try:
                from .utils import AuditLogger
                audit_session = AuditLogger.get_or_create_session(request)
                request.audit_session = audit_session
            except Exception:
                pass
    
    def process_response(self, request, response):
        # Log error responses
        if hasattr(request, 'user') and request.user.is_authenticated and response.status_code >= 400:
            try:
                from .utils import AuditLogger
                severity = 'error' if response.status_code >= 500 else 'warning'
                risk_score = 40 if response.status_code >= 500 else 20
                
                AuditLogger.log_action(
                    user=request.user,
                    action_type='view',
                    resource_type='http_response',
                    description=f"HTTP {response.status_code} response for {request.get_full_path()}",
                    severity=severity,
                    request=request,
                    risk_score=risk_score,
                    correlation_id=getattr(request, 'correlation_id', None)
                )
            except Exception:
                pass
        
        return response


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login"""
    try:
        from .utils import AuditLogger
        from .simple_logger import SimpleAuditLogger
        AuditLogger.log_login(user, request, success=True)
        
        # Also log with simple audit logger
        SimpleAuditLogger.log_login(user, request)
    except Exception:
        pass


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout"""
    if user:
        try:
            from .utils import AuditLogger
            from .simple_logger import SimpleAuditLogger
            AuditLogger.log_logout(user, request)
            
            # Also log with simple audit logger
            SimpleAuditLogger.log_logout(user, request)
        except Exception:
            pass
