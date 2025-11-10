from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Worker, WorkerChangeHistory, WorkerProbationPeriod, Document

User = get_user_model()

# Import SimpleAuditLogger for audit logging
try:
    from audit_management.simple_logger import SimpleAuditLogger
    SIMPLE_AUDIT_AVAILABLE = True
except ImportError:
    SIMPLE_AUDIT_AVAILABLE = False

# Import auditlog for checking registered models
try:
    from auditlog.registry import auditlog
    AUDITLOG_AVAILABLE = True
except ImportError:
    AUDITLOG_AVAILABLE = False

# Thread-local storage to keep track of who is making changes
import threading
_thread_locals = threading.local()

def get_current_request():
    """Get current request from thread local storage"""
    return getattr(_thread_locals, 'request', None)

def get_current_user():
    """Get current user from thread local storage or auditlog context"""
    # First try our thread local approach
    request = get_current_request()
    if request and hasattr(request, 'user') and request.user.is_authenticated:
        return request.user
    
    # Fallback: Try to get user from auditlog middleware context
    try:
        from auditlog.context import get_actor
        actor = get_actor()
        if actor and actor.is_authenticated:
            return actor
    except ImportError:
        pass
    
    return None

def get_client_ip(request):
    """Get client IP address from request"""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_agent(request):
    """Get user agent from request"""
    if not request:
        return None
    return request.META.get('HTTP_USER_AGENT', '')

class CurrentRequestMiddleware:
    """Middleware to store current request in thread local storage"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response

def get_trackable_fields(model_instance):
    """Get all trackable fields from a model instance automatically"""
    fields = []
    
    # Skip sensitive and system fields
    skip_fields = [
        'id', 'pk', 'password', 'created_at', 'updated_at', 'created_by', 'updated_by',
        'phone_number', 'email', 'address', 'emergency_phone', 'emergency_contact_phone',
        'passport_number', 'id_card_number', 'notes', 'photo'  # Sensitive/encrypted fields
    ]
    
    # Skip foreign key reverse relations and other complex fields
    skip_field_types = ['ManyToManyField', 'GenericForeignKey']
    
    for field in model_instance._meta.fields:
        if field.name in skip_fields:
            continue
            
        # Skip certain field types
        if field.__class__.__name__ in skip_field_types:
            continue
            
        # Use verbose_name if available, otherwise make field name human-readable
        display_name = field.verbose_name if hasattr(field, 'verbose_name') and field.verbose_name else field.name.replace('_', ' ').title()
        fields.append((field.name, display_name))
    
    return fields

def is_model_registered_for_audit(model_class):
    """Check if a model is registered with auditlog"""
    if not AUDITLOG_AVAILABLE:
        return False
    try:
        return auditlog.contains(model_class)
    except:
        return False

def log_model_changes(instance, old_instance, action='update'):
    """Generic function to log changes for any registered model"""
    if not SIMPLE_AUDIT_AVAILABLE:
        return
        
    model_class = instance.__class__
    
    # Only log if model is registered with auditlog
    if not is_model_registered_for_audit(model_class):
        return
    
    try:
        model_name = model_class.__name__
        
        if action == 'create':
            # Log creation
            SimpleAuditLogger.log_create(
                user=get_current_user(),
                model_name=model_name,
                obj=instance,
                request=get_current_request()
            )
        elif action == 'update' and old_instance:
            # Get all trackable fields and check for changes
            fields_to_track = get_trackable_fields(instance)
            changes = {}
            
            for field_name, display_name in fields_to_track:
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)
                
                # Convert to strings for comparison
                old_str = str(old_value) if old_value is not None else None
                new_str = str(new_value) if new_value is not None else None
                
                if old_str != new_str:
                    changes[field_name] = {'old': old_str, 'new': new_str}
            
            if changes:
                SimpleAuditLogger.log_update(
                    user=get_current_user(),
                    model_name=model_name,
                    obj=instance,
                    changes=changes,
                    request=get_current_request()
                )
        elif action == 'delete':
            # Log deletion
            SimpleAuditLogger.log_delete(
                user=get_current_user(),
                model_name=model_name,
                obj=instance,
                request=get_current_request()
            )

    except Exception as e:
        pass

def log_worker_change(worker, action, field_name=None, old_value=None, new_value=None, description=None):
    """Helper function to log worker changes"""
    # Check if we're in the middle of deleting a worker
    import threading
    if hasattr(threading.current_thread(), 'deleting_worker'):
        # Skip logging during worker deletion to avoid constraint violations
        return
        
    # Check if worker still exists in database before attempting to create history
    try:
        if worker and worker.pk:
            # Verify worker exists in database
            Worker.objects.get(pk=worker.pk)
            
            request = get_current_request()
            
            WorkerChangeHistory.objects.create(
                worker=worker,
                action=action,
                field_name=field_name,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value) if new_value is not None else None,
                description=description,
                changed_by=get_current_user(),
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request)
            )
    except Worker.DoesNotExist:
        # Worker was deleted - this is expected during cascade delete
        pass
    except Exception as e:
        # Log the error but don't fail the operation
        pass

@receiver(pre_save, sender=Worker)
def worker_pre_save(sender, instance, **kwargs):
    """Track changes before saving worker"""
    if instance.pk:  # This is an update, not creation
        try:
            old_instance = Worker.objects.get(pk=instance.pk)
            
            # Store old instance for comparison in post_save
            instance._old_instance = old_instance
            
        except Worker.DoesNotExist:
            pass

@receiver(post_save, sender=Worker)
def worker_post_save(sender, instance, created, **kwargs):
    """Log worker changes after save"""
    if created:
        # New worker created
        log_worker_change(
            worker=instance,
            action='created',
            description=f"Worker {instance.get_full_name()} ({instance.worker_id}) was created"
        )
        
        # Log to SimpleAuditLog using generic function
        log_model_changes(instance, None, action='create')
        
        # Auto-create probation period if worker has probation-related status
        if instance.status in ['probation', 'extended']:
            from datetime import timedelta
            
            # Check if worker already has a probation period
            existing_probation = WorkerProbationPeriod.objects.filter(worker=instance).exists()
            
            if not existing_probation:
                # Create automatic probation period
                start_date = instance.date_joined or instance.created_at.date()
                end_date = start_date + timedelta(days=90)  # Standard 90-day probation
                
                # Create probation period (no signal disconnection needed since the function is disabled)
                try:
                    WorkerProbationPeriod.objects.create(
                        worker=instance,
                        start_date=start_date,
                        original_end_date=end_date,
                        evaluation_notes="Automatically created probation period based on worker status",
                        created_by=get_current_user()
                    )
                    
                    log_worker_change(
                        worker=instance,
                        action='probation_started',
                        description=f"Probation period automatically created ({start_date} to {end_date})"
                    )
                except Exception as e:
                    pass
    else:
        # Worker updated - check what changed
        if hasattr(instance, '_old_instance'):
            old_instance = instance._old_instance
            
            # Get all trackable fields automatically
            fields_to_track = get_trackable_fields(instance)
            
            for field_name, display_name in fields_to_track:
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)
                
                # Handle foreign key fields
                if hasattr(old_value, '__str__'):
                    old_value = str(old_value)
                if hasattr(new_value, '__str__'):
                    new_value = str(new_value)
                
                if old_value != new_value:
                    # Special handling for status changes
                    if field_name == 'status':
                        log_worker_change(
                            worker=instance,
                            action='status_changed',
                            field_name=field_name,
                            old_value=old_value,
                            new_value=new_value,
                            description=f"Status changed from {old_value} to {new_value}"
                        )
                    # Special handling for zone/building assignment
                    elif field_name in ['zone', 'building']:
                        log_worker_change(
                            worker=instance,
                            action='assigned',
                            field_name=field_name,
                            old_value=old_value,
                            new_value=new_value,
                            description=f"{display_name} changed from {old_value or 'None'} to {new_value or 'None'}"
                        )
                    else:
                        log_worker_change(
                            worker=instance,
                            action='updated',
                            field_name=field_name,
                            old_value=old_value,
                            new_value=new_value
                        )
            
            # Log to SimpleAuditLog using generic function
            log_model_changes(instance, old_instance, action='update')
            
            # Clean up
            delattr(instance, '_old_instance')

@receiver(post_save, sender=WorkerProbationPeriod)
def probation_post_save(sender, instance, created, **kwargs):
    """Log probation period changes"""
    # Check if we're in the middle of deleting a worker
    import threading
    if hasattr(threading.current_thread(), 'deleting_worker'):
        # Skip logging during worker deletion to avoid constraint violations
        return
        
    if created:
        log_worker_change(
            worker=instance.worker,
            action='probation_started',
            description=f"Probation period started from {instance.start_date} to {instance.original_end_date}"
        )
    # Note: WorkerProbationPeriod no longer has status field
    # Status tracking is now handled only through Worker.status
    # Probation status changes are logged via worker_post_save signal

# Disabled - WorkerProbationPeriod no longer has status field
# Status is now tracked only on Worker model
# @receiver(pre_save, sender=WorkerProbationPeriod)
# def probation_pre_save(sender, instance, **kwargs):
#     """Track probation status before save for comparison"""
#     # WorkerProbationPeriod no longer has status field
#     pass

# Disabled - WorkerProbationPeriod no longer has status field  
# Status is now tracked only on Worker model
# @receiver(post_save, sender=WorkerProbationPeriod)
# def auto_sync_worker_status_on_probation_change(sender, instance, created, **kwargs):
#     """Disabled - WorkerProbationPeriod no longer has status field"""
#     pass

@receiver(post_save, sender=Worker) 
def auto_sync_probation_status_on_worker_change(sender, instance, created, **kwargs):
    """
    Automatically synchronize probation status when worker status changes.
    This ensures worker and probation statuses are always in sync.
    """
    # Only handle status changes for existing workers
    if not created and hasattr(instance, '_old_instance'):
        old_instance = instance._old_instance
        
        # Check if status changed
        if old_instance.status != instance.status:
            # Find active probation periods for this worker  
            active_probations = WorkerProbationPeriod.objects.filter(
                worker=instance
            )
            
            # Status is now tracked only on Worker model, no need to sync
            # WorkerProbationPeriod no longer has a status field

@receiver(post_save, sender=Document)
def document_post_save(sender, instance, created, **kwargs):
    """Log document changes"""
    # Check if we're in the middle of deleting a worker
    import threading
    if hasattr(threading.current_thread(), 'deleting_worker'):
        # Skip logging during worker deletion to avoid constraint violations
        return
        
    if instance.worker:
        if created:
            log_worker_change(
                worker=instance.worker,
                action='document_added',
                description=f"Document added: {instance.get_document_type_display()} - {instance.document_number}"
            )
        else:
            log_worker_change(
                worker=instance.worker,
                action='document_updated',
                description=f"Document updated: {instance.get_document_type_display()} - {instance.document_number}"
            )

@receiver(post_delete, sender=Document)
def document_post_delete(sender, instance, **kwargs):
    """Log document deletion"""
    # Check if we're in the middle of deleting a worker
    import threading
    if hasattr(threading.current_thread(), 'deleting_worker'):
        # Skip logging during worker deletion to avoid constraint violations
        return
    
    # Check if the worker still exists before trying to log
    # (worker might be deleted via cascade, causing this document to be deleted)
    if instance.worker and instance.worker.pk:
        try:
            # Verify the worker still exists in the database
            Worker.objects.get(pk=instance.worker.pk)
            log_worker_change(
                worker=instance.worker,
                action='document_deleted',
                description=f"Document deleted: {instance.get_document_type_display()} - {instance.document_number}"
            )
        except Worker.DoesNotExist:
            # Worker was deleted via cascade, so we can't log to WorkerChangeHistory
            # This is expected behavior during cascade delete
            pass
        except Exception as e:
            # Any other exception - log it but don't fail
            pass

@receiver(post_delete, sender=Worker)
def worker_post_delete(sender, instance, **kwargs):
    """Clean up files when worker is deleted"""
    import os

    files_deleted = 0

    try:
        # Clean up worker photo
        if instance.photo and instance.photo.name:
            try:
                if os.path.exists(instance.photo.path):
                    os.remove(instance.photo.path)
                    files_deleted += 1
            except Exception as e:
                pass

        # Note: Document files are cleaned up by their own post_delete signal
        # since documents are cascade deleted when worker is deleted

    except Exception as e:
        pass


@receiver(post_delete, sender=Document)
def document_file_cleanup(sender, instance, **kwargs):
    """Clean up document files when document is deleted"""
    import os

    try:
        # Clean up document file
        if instance.document_file and instance.document_file.name:
            try:
                if os.path.exists(instance.document_file.path):
                    os.remove(instance.document_file.path)
            except Exception as e:
                pass

    except Exception as e:
        pass


# Removed worker_post_delete signal logging because it causes foreign key constraint violations
# The worker deletion logging is now handled in the view before deletion occurs

# ============================================================================
# GENERIC AUDIT SIGNALS FOR ALL REGISTERED MODELS
# ============================================================================

@receiver(pre_save)
def generic_audit_pre_save(sender, instance, **kwargs):
    """Generic pre_save signal to track changes for any registered model"""
    # Only process if model is registered with auditlog
    if not is_model_registered_for_audit(sender):
        return
        
    if instance.pk:  # This is an update, not creation
        try:
            old_instance = sender.objects.get(pk=instance.pk)
            # Store old instance for comparison in post_save
            instance._old_instance = old_instance
        except sender.DoesNotExist:
            pass

@receiver(post_save)
def generic_audit_post_save(sender, instance, created, **kwargs):
    """Generic post_save signal to log changes for any registered model"""
    # Skip Worker model as it has its own specific handling above
    if sender.__name__ == 'Worker':
        return
        
    # Only process if model is registered with auditlog
    if not is_model_registered_for_audit(sender):
        return
    
    try:
        if created:
            # Log creation
            log_model_changes(instance, None, action='create')
        else:
            # Log updates if we have old instance data
            if hasattr(instance, '_old_instance'):
                old_instance = instance._old_instance
                log_model_changes(instance, old_instance, action='update')
                # Clean up
                delattr(instance, '_old_instance')

    except Exception as e:
        pass

@receiver(post_delete)
def generic_audit_post_delete(sender, instance, **kwargs):
    """Generic post_delete signal to log deletions for any registered model"""
    # Skip Worker model as deletion is handled in views
    if sender.__name__ == 'Worker':
        return
        
    # Only process if model is registered with auditlog
    if not is_model_registered_for_audit(sender):
        return
    
    try:
        log_model_changes(instance, None, action='delete')
    except Exception as e:
        pass