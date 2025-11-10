import threading
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from audit_management.models import AuditTrail
from audit_management.utils import AuditLogger
from audit_management.simple_logger import SimpleAuditLogger
from .models import Employee, EmployeeChangeHistory, EmployeeDocument, ProbationPeriod, IDCardRequest
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

_thread_locals = threading.local()

class CurrentRequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        if hasattr(_thread_locals, 'request'):
            del _thread_locals.request
        return response

def get_current_request():
    return getattr(_thread_locals, 'request', None)

def get_client_info(request):
    if not request:
        return {
            'user': None,
            'user_string': None,
            'ip_address': None,
            'user_agent': None
        }
    
    user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() or request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    return {
        'user': user,  # Return the User object, not username string
        'user_string': user.username if user and hasattr(user, 'username') else 'System',  # Safe username access
        'ip_address': ip_address,
        'user_agent': user_agent
    }

def format_field_value(value):
    if value is None:
        return None
    
    try:
        if hasattr(value, '_meta') and hasattr(value._meta, 'model_name'):
            return f"{value._meta.model_name}: {str(value)}"
        
        if isinstance(value, bool):
            return 'Yes' if value else 'No'
        
        # For file fields, safely get the name without triggering file access
        if hasattr(value, 'name'):
            try:
                return value.name
            except (OSError, ValueError, AttributeError):
                return f"[File field - access error]"
        
        return str(value)[:500]
    except (OSError, ValueError, AttributeError):
        # Handle any unexpected errors safely
        return f"[Field value - access error]"

# Store original decrypted values before save
_employee_original_values = {}

@receiver(pre_save, sender='hr.Employee')
def track_encrypted_field_changes(sender, instance, **kwargs):
    """
    Custom signal handler to track changes in encrypted fields.
    Compares decrypted values instead of encrypted values to avoid false positives.
    """
    if not instance.pk:
        # This is a new instance, no comparison needed
        return
    
    try:
        # Get the original instance from database
        original = sender.objects.get(pk=instance.pk)
        
        # Define encrypted fields to track (none currently for Employee model)
        encrypted_fields = {}
        
        # Compare decrypted values
        changes = {}
        for field_name, display_name in encrypted_fields.items():
            try:
                # Get original decrypted value
                original_value = None
                if hasattr(original, f'get_{field_name}'):
                    original_value = getattr(original, f'get_{field_name}')()
                
                # Get new decrypted value from form data or current instance
                new_value = None
                if hasattr(instance, f'get_{field_name}'):
                    # For existing encrypted values, decrypt them
                    current_encrypted = getattr(instance, field_name)
                    if current_encrypted:
                        from .utils import decrypt_field
                        try:
                            new_value = decrypt_field(current_encrypted)
                        except:
                            # If decryption fails, it might be plain text (from form)
                            new_value = current_encrypted
                    
                # Compare decrypted values
                if original_value != new_value:
                    changes[display_name] = {
                        'old': original_value or '(empty)',
                        'new': new_value or '(empty)'
                    }
                    
            except Exception as e:

                    
                pass
                continue
        
        # Log changes if any were found
        if changes:
            try:
                # Try to get the current user from thread local or request
                user = None
                
                # Create audit log entry
                change_summary = []
                old_values = {}
                new_values = {}
                
                for field, change in changes.items():
                    change_summary.append(f"{field}: {change['old']} → {change['new']}")
                    old_values[field] = change['old']
                    new_values[field] = change['new']
                
                AuditLogger.log_action(
                    user=user,
                    action_type='update',
                    resource_type='employee',
                    resource_id=str(instance.pk),
                    resource_name=f"{instance.first_name} {instance.last_name}",
                    description=f"Updated encrypted fields: {', '.join(changes.keys())}",
                    old_values=old_values,
                    new_values=new_values,
                    severity='warning',  # Encrypted field changes are important
                    risk_score=50,  # Medium-high risk for sensitive data changes
                    tags=['employee_update', 'encrypted_fields', 'sensitive_data']
                )
                
                
            except Exception as e:

                
                
                pass
    
                pass
    except sender.DoesNotExist:
        # Original instance doesn't exist, this shouldn't happen
        pass
    except Exception as e:

        pass


def get_current_user():
    """
    Try to get the current user from thread local storage.
    This is a fallback when user context is not available.
    """
    try:
        from threading import current_thread
        thread = current_thread()
        if hasattr(thread, 'user'):
            return thread.user
    except:
        pass
    return None

@receiver(pre_save, sender=Employee)
def employee_pre_save_change_history(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = Employee.objects.get(pk=instance.pk)
        except Employee.DoesNotExist:
            instance._old_instance = None
    else:
        instance._old_instance = None

@receiver(post_save, sender=Employee)
def employee_post_save_change_history(sender, instance, created, **kwargs):
    # Safety check: don't create history if employee is being deleted
    if getattr(instance, '_being_deleted', False):
        return

    request = get_current_request()
    client_info = get_client_info(request)
    
    if created:
        try:
            EmployeeChangeHistory.objects.create(
                employee=instance,
                action='created',
                new_value=f"Employee created: {instance.employee_id} - {instance.full_name}",
                changed_by=client_info['user_string'],
                ip_address=client_info['ip_address'],
                user_agent=client_info['user_agent'],
                additional_info={'employee_id': instance.employee_id}
            )
        except Exception as e:
        
            pass
        # Simple audit log
        try:
            SimpleAuditLogger.log_create(
                user=client_info['user'],
                model_name='Employee',
                obj=instance,
                request=request
            )
        except Exception as e:
            pass
    else:
        old_instance = getattr(instance, '_old_instance', None)
        if old_instance:
            tracked_fields = [
                'first_name', 'last_name', 'gender', 'date_of_birth', 'nationality',
                'phone_number', 'email', 'address', 'emergency_contact_name', 
                'emergency_contact_phone', 'employment_status', 'hire_date', 
                'end_date', 'notes'
            ]
            
            for field_name in tracked_fields:
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)
                
                if field_name in ['phone_number', 'email', 'address', 'emergency_contact_name', 'emergency_contact_phone', 'notes']:
                    if old_value != new_value:
                        try:
                            EmployeeChangeHistory.objects.create(
                                employee=instance,
                                action='updated',
                                field_name=field_name,
                                old_value="[Encrypted]" if old_value else None,
                                new_value="[Encrypted]" if new_value else None,
                                changed_by=client_info['user_string'],
                                ip_address=client_info['ip_address'],
                                user_agent=client_info['user_agent']
                            )
                        except Exception as e:
                            pass
                else:
                    if old_value != new_value:
                        try:
                            EmployeeChangeHistory.objects.create(
                                employee=instance,
                                action='updated',
                                field_name=field_name,
                                old_value=format_field_value(old_value),
                                new_value=format_field_value(new_value),
                                changed_by=client_info['user_string'],
                                ip_address=client_info['ip_address'],
                                user_agent=client_info['user_agent']
                            )
                        except Exception as e:
            
                            pass
            if old_instance.employment_status != instance.employment_status:
                try:
                    EmployeeChangeHistory.objects.create(
                        employee=instance,
                        action='status_changed',
                        field_name='employment_status',
                        old_value=old_instance.get_employment_status_display(),
                        new_value=instance.get_employment_status_display(),
                        changed_by=client_info['user_string'],
                        ip_address=client_info['ip_address'],
                        user_agent=client_info['user_agent']
                    )
                except Exception as e:
            
                    pass
            # Safely compare photo fields without triggering file access
            try:
                old_photo_name = old_instance.photo.name if old_instance.photo else None
                new_photo_name = instance.photo.name if instance.photo else None
                
                if old_photo_name != new_photo_name:
                    try:
                        EmployeeChangeHistory.objects.create(
                            employee=instance,
                            action='photo_updated',
                            old_value="Previous photo" if old_photo_name else None,
                            new_value="New photo uploaded" if new_photo_name else "Photo removed",
                            changed_by=client_info['user_string'],
                            ip_address=client_info['ip_address'],
                            user_agent=client_info['user_agent']
                        )
                    except Exception as e:
                        pass
            except (OSError, ValueError, AttributeError):
                # Handle cases where photo files are missing or corrupted
                try:
                    EmployeeChangeHistory.objects.create(
                        employee=instance,
                        action='photo_updated',
                        old_value="Photo field changed (file access error)",
                        new_value="Photo field updated",
                        changed_by=client_info['user_string'],
                        ip_address=client_info['ip_address'],
                        user_agent=client_info['user_agent']
                    )
                except Exception as e:
            
                    pass
            # Simple audit log for update
            changes = {}
            for field_name in tracked_fields:
                old_value = getattr(old_instance, field_name, None)
                new_value = getattr(instance, field_name, None)
                if old_value != new_value:
                    if field_name in ['phone_number', 'email', 'address', 'emergency_contact_name', 'emergency_contact_phone', 'notes']:
                        changes[field_name] = {'old': '[Encrypted]', 'new': '[Encrypted]'}
                    else:
                        changes[field_name] = {'old': str(old_value), 'new': str(new_value)}
            
            if changes:
                try:
                    SimpleAuditLogger.log_update(
                        user=client_info['user'],
                        model_name='Employee',
                        obj=instance,
                        changes=changes,
                        request=request
                    )
                except Exception as e:

                    pass
@receiver(post_delete, sender=Employee)
def employee_post_delete_change_history(sender, instance, **kwargs):
    # Skip ALL logging if employee is being deleted via custom delete method
    if getattr(instance, '_being_deleted', False):
        return

    # Skip creating EmployeeChangeHistory for employee deletion to avoid constraint issues
    # The deletion is already logged by our custom delete method
    request = get_current_request()
    client_info = get_client_info(request)

    try:
        # Only create audit log, not EmployeeChangeHistory
        SimpleAuditLogger.log_delete(
            user=client_info['user'],
            model_name='Employee',
            obj=instance,
            request=request
        )
    except Exception as e:
        pass

@receiver(post_save, sender=EmployeeDocument)
def employee_document_post_save_change_history(sender, instance, created, **kwargs):
    # Safety check: don't create history if employee is being deleted or doesn't exist
    if not instance.employee or getattr(instance.employee, '_being_deleted', False):
        return
    
    try:
        # Verify employee still exists in database
        if not Employee.objects.filter(pk=instance.employee.pk).exists():
            return
    except Exception:
        return
    
    request = get_current_request()
    client_info = get_client_info(request)
    
    if created:
        try:
            EmployeeChangeHistory.objects.create(
                employee=instance.employee,
                action='document_added',
                new_value=f"Document added: {instance.get_document_type_display()} - {instance.document_number}",
                changed_by=client_info['user_string'],
                ip_address=client_info['ip_address'],
                user_agent=client_info['user_agent'],
                additional_info={'document_type': instance.document_type, 'document_number': instance.document_number}
            )
        except Exception as e:

            pass
@receiver(post_delete, sender=EmployeeDocument)
def employee_document_post_delete_change_history(sender, instance, **kwargs):
    # Skip if employee is being deleted (cascade delete)
    if hasattr(instance, '_employee_being_deleted') and instance._employee_being_deleted:
        return

    # Skip if employee has _being_deleted flag
    if instance.employee and getattr(instance.employee, '_being_deleted', False):
        return

    request = get_current_request()
    client_info = get_client_info(request)

    # Only create change history if the employee still exists
    try:
        if instance.employee and Employee.objects.filter(pk=instance.employee.pk).exists():
            EmployeeChangeHistory.objects.create(
                employee=instance.employee,
                action='document_removed',
                old_value=f"Document removed: {instance.get_document_type_display()} - {instance.document_number}",
                changed_by=client_info['user_string'],
                ip_address=client_info['ip_address'],
                user_agent=client_info['user_agent'],
                additional_info={'document_type': instance.document_type, 'document_number': instance.document_number}
            )
    except Exception as e:
        # Skip logging if employee is being deleted (cascade)
        pass

@receiver(pre_save, sender=ProbationPeriod)
def probation_period_pre_save_change_history(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = ProbationPeriod.objects.get(pk=instance.pk)
        except ProbationPeriod.DoesNotExist:
            instance._old_instance = None

@receiver(post_save, sender=ProbationPeriod)
def probation_period_post_save_change_history(sender, instance, created, **kwargs):
    # Safety check: don't create history if employee is being deleted or doesn't exist
    if not instance.employee or getattr(instance.employee, '_being_deleted', False):
        return
    
    try:
        # Verify employee still exists in database
        if not Employee.objects.filter(pk=instance.employee.pk).exists():
            return
    except Exception:
        return
    
    request = get_current_request()
    client_info = get_client_info(request)
    
    try:
        if created:
            EmployeeChangeHistory.objects.create(
                employee=instance.employee,
                action='probation_started',
                new_value=f"Probation period started: {instance.start_date} to {instance.original_end_date}",
                changed_by=client_info['user_string'],
                ip_address=client_info['ip_address'],
                user_agent=client_info['user_agent'],
                additional_info={'start_date': str(instance.start_date), 'end_date': str(instance.original_end_date)}
            )
        else:
            old_instance = getattr(instance, '_old_instance', None)
            if old_instance and old_instance.status != instance.status:
                if instance.status == 'extended':
                    EmployeeChangeHistory.objects.create(
                        employee=instance.employee,
                        action='probation_extended',
                        new_value=f"Probation extended to {instance.actual_end_date}",
                        changed_by=client_info['user_string'],
                        ip_address=client_info['ip_address'],
                        user_agent=client_info['user_agent']
                    )
                elif instance.status == 'completed':
                    EmployeeChangeHistory.objects.create(
                        employee=instance.employee,
                        action='probation_completed',
                        new_value=f"Probation completed on {instance.actual_end_date or instance.original_end_date}",
                        changed_by=client_info['user_string'],
                        ip_address=client_info['ip_address'],
                        user_agent=client_info['user_agent']
                    )
    except Exception as e:

        pass
@receiver(pre_save, sender=IDCardRequest)
def id_card_request_pre_save_change_history(sender, instance, **kwargs):
    if instance.pk:
        try:
            instance._old_instance = IDCardRequest.objects.get(pk=instance.pk)
        except IDCardRequest.DoesNotExist:
            instance._old_instance = None

@receiver(post_save, sender=IDCardRequest)
def id_card_request_post_save_change_history(sender, instance, created, **kwargs):
    # Safety check: don't create history if employee is being deleted or doesn't exist
    if not instance.employee or getattr(instance.employee, '_being_deleted', False):
        return
    
    try:
        # Verify employee still exists in database
        if not Employee.objects.filter(pk=instance.employee.pk).exists():
            return
    except Exception:
        return
    
    request = get_current_request()
    client_info = get_client_info(request)
    
    try:
        if created:
            EmployeeChangeHistory.objects.create(
                employee=instance.employee,
                action='id_card_requested',
                new_value=f"ID Card requested: {instance.get_request_type_display()}",
                changed_by=client_info['user_string'],
                ip_address=client_info['ip_address'],
                user_agent=client_info['user_agent'],
                additional_info={'request_type': instance.request_type}
            )
        else:
            old_instance = getattr(instance, '_old_instance', None)
            if old_instance and old_instance.status != instance.status and instance.status == 'delivered':
                EmployeeChangeHistory.objects.create(
                    employee=instance.employee,
                    action='id_card_issued',
                    new_value=f"ID Card delivered: {instance.get_request_type_display()}",
                    changed_by=client_info['user_string'],
                    ip_address=client_info['ip_address'],
                    user_agent=client_info['user_agent']
                )
    except Exception as e:        pass
