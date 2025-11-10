import uuid
import json
import logging
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from auditlog.models import LogEntry
from .models import AuditSession, AuditTrail, AuditException

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Centralized audit logging utility
    """
    
    @staticmethod
    def get_or_create_session(request):
        """Get or create audit session for tracking"""
        if not request.user.is_authenticated:
            return None
            
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            
        ip_address = AuditLogger.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        audit_session, created = AuditSession.objects.get_or_create(
            session_key=session_key,
            defaults={
                'user': request.user,
                'ip_address': ip_address,
                'user_agent': user_agent,
            }
        )
        
        if not created:
            # Update last activity
            audit_session.last_activity = timezone.now()
            audit_session.save(update_fields=['last_activity'])
            
        return audit_session
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def log_action(
        user, 
        action_type, 
        resource_type, 
        description,
        resource_id=None,
        resource_name=None,
        old_values=None,
        new_values=None,
        severity='info',
        request=None,
        risk_score=0,
        tags=None,
        correlation_id=None,
        business_context=None
    ):
        """
        Log an audit action with enhanced context
        """
        try:
            # Generate correlation ID if not provided
            if not correlation_id:
                correlation_id = str(uuid.uuid4())
            
            # Get session if request is provided
            session = None
            ip_address = '127.0.0.1'
            user_agent = ''
            request_path = ''
            request_method = ''
            
            if request:
                session = AuditLogger.get_or_create_session(request)
                ip_address = AuditLogger.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                request_path = request.get_full_path()
                request_method = request.method
            
            # Set business context
            department = ''
            location = ''
            business_unit = ''
            
            if business_context:
                department = business_context.get('department', '')
                location = business_context.get('location', '')
                business_unit = business_context.get('business_unit', '')
            elif user and hasattr(user, 'employeerecord'):
                # Try to get context from user's employee record
                emp_record = user.employeerecord
                department = getattr(emp_record, 'department', '')
                location = getattr(emp_record, 'location', '')
                business_unit = getattr(emp_record, 'business_unit', '')
            
            # Create audit trail entry
            audit_trail = AuditTrail.objects.create(
                user=user,
                session=session,
                action_type=action_type,
                severity=severity,
                resource_type=resource_type,
                resource_id=str(resource_id) if resource_id else '',
                resource_name=resource_name or '',
                description=description,
                old_values=old_values,
                new_values=new_values,
                ip_address=ip_address,
                user_agent=user_agent,
                request_path=request_path,
                request_method=request_method,
                department=department,
                location=location,
                business_unit=business_unit,
                correlation_id=correlation_id,
                tags=tags or [],
                risk_score=risk_score,
            )
            
            return audit_trail
            
        except Exception as e:

            
            pass
            # Log the audit logging failure
            AuditLogger.log_exception(
                'logging_failure',
                f"Failed to create audit log: {str(e)}",
                user=user,
                error_message=str(e),
                request=request
            )
            return None
    
    @staticmethod
    def log_login(user, request, success=True, failure_reason=None):
        """Log user login attempt"""
        action_type = 'login'
        severity = 'info' if success else 'warning'
        description = f"User {user.username if user else 'Unknown'} login attempt"
        
        if not success:
            description += f" failed: {failure_reason}"
            
        risk_score = 0 if success else 30
        
        return AuditLogger.log_action(
            user=user,
            action_type=action_type,
            resource_type='authentication',
            description=description,
            severity=severity,
            request=request,
            risk_score=risk_score,
            tags=['authentication']
        )
    
    @staticmethod
    def log_logout(user, request):
        """Log user logout"""
        return AuditLogger.log_action(
            user=user,
            action_type='logout',
            resource_type='authentication',
            description=f"User {user.username} logged out",
            request=request,
            tags=['authentication']
        )
    
    @staticmethod
    def log_model_change(instance, action, user=None, request=None, old_values=None):
        """Log model instance changes"""
        content_type = ContentType.objects.get_for_model(instance)
        resource_type = f"{content_type.app_label}.{content_type.model}"
        
        # Calculate risk score based on model type and action
        risk_score = AuditLogger.calculate_risk_score(resource_type, action, old_values)
        
        # Prepare new values
        new_values = {}
        if hasattr(instance, '__dict__'):
            for field, value in instance.__dict__.items():
                if not field.startswith('_'):
                    if isinstance(value, (str, int, float, bool, type(None))):
                        new_values[field] = value
                    else:
                        new_values[field] = str(value)
        
        return AuditLogger.log_action(
            user=user,
            action_type=action,
            resource_type=resource_type,
            resource_id=instance.pk,
            resource_name=str(instance),
            description=f"{action.capitalize()} {resource_type} '{instance}'",
            old_values=old_values,
            new_values=new_values,
            request=request,
            risk_score=risk_score,
            tags=[content_type.app_label, content_type.model]
        )
    
    @staticmethod
    def log_permission_check(user, resource, permission, granted, request=None):
        """Log permission check"""
        severity = 'info' if granted else 'warning'
        risk_score = 0 if granted else 40
        
        return AuditLogger.log_action(
            user=user,
            action_type='permission_check',
            resource_type='permission',
            resource_name=resource,
            description=f"Permission '{permission}' {'granted' if granted else 'denied'} for {resource}",
            severity=severity,
            request=request,
            risk_score=risk_score,
            tags=['permission', 'access_control']
        )
    
    @staticmethod
    def log_data_export(user, resource_type, count, request=None):
        """Log data export"""
        risk_score = min(count // 10, 60)  # Higher risk for larger exports
        
        return AuditLogger.log_action(
            user=user,
            action_type='export',
            resource_type=resource_type,
            description=f"Exported {count} {resource_type} records",
            severity='info',
            request=request,
            risk_score=risk_score,
            tags=['export', 'data_access']
        )
    
    @staticmethod
    def log_security_event(user, event_type, description, severity='warning', request=None):
        """Log security-related events"""
        return AuditLogger.log_action(
            user=user,
            action_type='security_event',
            resource_type='security',
            description=description,
            severity=severity,
            request=request,
            risk_score=70,
            tags=['security', event_type]
        )
    
    @staticmethod
    def log_exception(exception_type, description, user=None, error_message=None,
                     stack_trace=None, request=None):
        """Log audit exceptions"""
        try:
            ip_address = None
            user_agent = ''
            request_path = ''
            
            if request:
                ip_address = AuditLogger.get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
                request_path = request.get_full_path()
            
            AuditException.objects.create(
                exception_type=exception_type,
                user=user,
                description=description,
                error_message=error_message or '',
                stack_trace=stack_trace or '',
                request_path=request_path,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
    
            pass
    @staticmethod
    def calculate_risk_score(resource_type, action, old_values=None):
        """Calculate risk score based on action and resource"""
        base_scores = {
            'delete': 60,
            'update': 30,
            'create': 20,
            'view': 5,
            'login': 5,
            'logout': 0,
        }
        
        # High-risk resources
        high_risk_resources = [
            'auth.user',
            'billing.',
            'payments.'
        ]
        
        score = base_scores.get(action, 10)
        
        # Increase score for high-risk resources
        for risk_resource in high_risk_resources:
            if risk_resource in resource_type.lower():
                score += 20
                break
        
        # Additional score for sensitive field changes
        if old_values and action == 'update':
            sensitive_fields = ['password', 'email', 'permissions', 'is_staff', 'is_superuser']
            for field in sensitive_fields:
                if field in str(old_values).lower():
                    score += 10
        
        return min(score, 100)  # Cap at 100
    
    @staticmethod
    def cleanup_old_sessions(days=30):
        """Clean up old audit sessions"""
        cutoff_date = timezone.now() - timedelta(days=days)
        old_sessions = AuditSession.objects.filter(
            last_activity__lt=cutoff_date,
            is_active=False
        )
        count = old_sessions.count()
        old_sessions.delete()
        return count
    
    @staticmethod
    def get_user_activity_summary(user, days=30):
        """Get user activity summary"""
        start_date = timezone.now() - timedelta(days=days)
        
        activities = AuditTrail.objects.filter(
            user=user,
            timestamp__gte=start_date
        )
        
        return {
            'total_actions': activities.count(),
            'login_count': activities.filter(action_type='login').count(),
            'create_count': activities.filter(action_type='create').count(),
            'update_count': activities.filter(action_type='update').count(),
            'delete_count': activities.filter(action_type='delete').count(),
            'view_count': activities.filter(action_type='view').count(),
            'high_risk_actions': activities.filter(risk_score__gte=50).count(),
            'last_activity': activities.first().timestamp if activities.exists() else None,
        }


class AuditContext:
    """Context manager for audit logging"""
    
    def __init__(self, user, action_type, resource_type, description, request=None):
        self.user = user
        self.action_type = action_type
        self.resource_type = resource_type
        self.description = description
        self.request = request
        self.correlation_id = str(uuid.uuid4())
        self.start_time = None
        self.audit_trail = None
    
    def __enter__(self):
        self.start_time = timezone.now()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Log the action with duration
        duration = (timezone.now() - self.start_time).total_seconds()
        description = f"{self.description} (duration: {duration:.2f}s)"
        
        if exc_type:
            # Log as error if exception occurred
            description += f" - Failed: {str(exc_val)}"
            severity = 'error'
            risk_score = 50
        else:
            severity = 'info'
            risk_score = 0
        
        self.audit_trail = AuditLogger.log_action(
            user=self.user,
            action_type=self.action_type,
            resource_type=self.resource_type,
            description=description,
            severity=severity,
            request=self.request,
            risk_score=risk_score,
            correlation_id=self.correlation_id
        )
        
        return False  # Don't suppress exceptions 