"""
Views for custom OTP device setup and management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseForbidden
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
import json
import logging
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
from .models import Notification
from datetime import timedelta
import os
import mimetypes
from .file_encryption import FileEncryptionHandler
from zone.models import Document
from django.views import View
from zone.models import WorkerProbationPeriod
from zone.models import UserProfile
from django.template import RequestContext
from user_management.models import UserRoleAssignment


logger = logging.getLogger(__name__)


@login_required
def setup_telegram_otp(request):
    """Setup page for Telegram OTP device."""
    
    # Check if user already has a Telegram device
    existing_device = TelegramDevice.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        telegram_user_id = request.POST.get('telegram_user_id')
        telegram_username = request.POST.get('telegram_username', '')
        test_token = request.POST.get('test_token')
        
        if not telegram_user_id:
            messages.error(request, 'Telegram User ID is required')
            return render(request, 'core/setup_telegram_otp.html')
        
        # Create or update device
        if existing_device:
            device = existing_device
            device.telegram_user_id = telegram_user_id
            device.telegram_username = telegram_username
            device.confirmed = False  # Reset confirmation status
        else:
            device = TelegramDevice.objects.create(
                user=request.user,
                name='Telegram',
                telegram_user_id=telegram_user_id,
                telegram_username=telegram_username,
                confirmed=False
            )
        
        device.save()
        
        # If test token provided, verify it
        if test_token:
            if device.verify_token(test_token):
                device.confirmed = True
                device.save()
                messages.success(request, 'Telegram OTP setup completed successfully!')
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Invalid test code. Please try again.')
        else:
            # Send test code
            try:
                device.generate_challenge()
                messages.info(request, 
                    'Test code sent to your Telegram! Enter it below to complete setup.')
            except ValidationError as e:
                messages.error(request, f'Failed to send test code: {str(e)}')
    
    context = {
        'existing_device': existing_device,
        'bot_username': getattr(settings, 'TELEGRAM_BOT_USERNAME', 'your_bot'),
    }
    
    return render(request, 'core/setup_telegram_otp.html', context)


@login_required
def setup_whatsapp_otp(request):
    """Setup page for WhatsApp OTP device."""
    
    existing_device = WhatsAppDevice.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        test_token = request.POST.get('test_token')
        
        if not phone_number:
            messages.error(request, 'Phone number is required')
            return render(request, 'core/setup_whatsapp_otp.html')
        
        # Create or update device
        if existing_device:
            device = existing_device
            device.phone_number = phone_number
            device.confirmed = False
        else:
            device = WhatsAppDevice.objects.create(
                user=request.user,
                name='WhatsApp',
                phone_number=phone_number,
                confirmed=False
            )
        
        device.save()
        
        # Handle test token verification
        if test_token:
            if device.verify_token(test_token):
                device.confirmed = True
                device.save()
                messages.success(request, 'WhatsApp OTP setup completed successfully!')
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Invalid test code. Please try again.')
        else:
            # Send test code
            try:
                device.generate_challenge()
                messages.info(request, 
                    'Test code sent to your WhatsApp! Enter it below to complete setup.')
            except ValidationError as e:
                messages.error(request, f'Failed to send test code: {str(e)}')
    
    context = {
        'existing_device': existing_device,
    }
    
    return render(request, 'core/setup_whatsapp_otp.html', context)


@login_required
def setup_slack_otp(request):
    """Setup page for Slack OTP device."""
    
    existing_device = SlackDevice.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        slack_user_id = request.POST.get('slack_user_id')
        slack_username = request.POST.get('slack_username', '')
        test_token = request.POST.get('test_token')
        
        if not slack_user_id:
            messages.error(request, 'Slack User ID is required')
            return render(request, 'core/setup_slack_otp.html')
        
        # Create or update device
        if existing_device:
            device = existing_device
            device.slack_user_id = slack_user_id
            device.slack_username = slack_username
            device.confirmed = False
        else:
            device = SlackDevice.objects.create(
                user=request.user,
                name='Slack',
                slack_user_id=slack_user_id,
                slack_username=slack_username,
                confirmed=False
            )
        
        device.save()
        
        # Handle test token verification
        if test_token:
            if device.verify_token(test_token):
                device.confirmed = True
                device.save()
                messages.success(request, 'Slack OTP setup completed successfully!')
                return redirect('dashboard:index')
            else:
                messages.error(request, 'Invalid test code. Please try again.')
        else:
            # Send test code
            try:
                device.generate_challenge()
                messages.info(request, 
                    'Test code sent to your Slack! Enter it below to complete setup.')
            except ValidationError as e:
                messages.error(request, f'Failed to send test code: {str(e)}')
    
    context = {
        'existing_device': existing_device,
    }
    
    return render(request, 'core/setup_slack_otp.html', context)


@login_required
def manage_otp_devices(request):
    """View to manage all OTP devices for the user."""
    
    telegram_devices = TelegramDevice.objects.filter(user=request.user)
    whatsapp_devices = WhatsAppDevice.objects.filter(user=request.user)
    slack_devices = SlackDevice.objects.filter(user=request.user)
    
    context = {
        'telegram_devices': telegram_devices,
        'whatsapp_devices': whatsapp_devices,
        'slack_devices': slack_devices,
    }
    
    return render(request, 'core/manage_otp_devices.html', context)


@require_POST
@login_required
def delete_otp_device(request, device_type, device_id):
    """Delete an OTP device."""
    
    device_classes = {
        'telegram': TelegramDevice,
        'whatsapp': WhatsAppDevice,
        'slack': SlackDevice,
    }
    
    if device_type not in device_classes:
        messages.error(request, 'Invalid device type')
        return redirect('core:manage_otp_devices')
    
    device_class = device_classes[device_type]
    device = get_object_or_404(device_class, id=device_id, user=request.user)
    
    device_name = str(device)
    device.delete()
    
    messages.success(request, f'Deleted {device_name}')
    return redirect('core:manage_otp_devices')


@csrf_exempt
def telegram_webhook(request):
    """
    Webhook endpoint for Telegram bot to handle user registration.
    
    When users send /start to your bot, this webhook can help them
    get their Telegram user ID for OTP setup.
    """
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST allowed'}, status=405)
    
    try:
        data = json.loads(request.body)
        
        # Extract message info
        message = data.get('message', {})
        user = message.get('from', {})
        chat = message.get('chat', {})
        text = message.get('text', '')
        
        user_id = user.get('id')
        username = user.get('username', '')
        first_name = user.get('first_name', '')
        
        if text.startswith('/start'):
            # Send welcome message with user ID
            bot_token = settings.TELEGRAM_BOT_TOKEN
            if bot_token:
                import telegram
                bot = telegram.Bot(token=bot_token)
                
                welcome_message = f"""🤖 Welcome to LYP Core System Security Bot!

👤 Your Telegram User ID is: `{user_id}`
📝 Your Username: @{username}

To set up two-factor authentication:
    pass
1. Copy your User ID: `{user_id}`
2. Go to your LYP Core account settings
3. Navigate to "Setup Telegram OTP"
4. Paste your User ID and follow the instructions

🔒 This bot will send you security codes for login verification.

Need help? Contact your system administrator."""
                
                bot.send_message(
                    chat_id=user_id,
                    text=welcome_message,
                    parse_mode='Markdown'
                )
        
        return JsonResponse({'status': 'ok'})
        
    except Exception as e:

        
        pass
        return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def notification_list(request):
    """Display all notifications for the current user"""
    notifications = Notification.objects.filter(
        recipient=request.user
    ).exclude(
        expires_at__lt=timezone.now()
    ).order_by('-created_at')
    
    # Filter by type if requested
    notification_type = request.GET.get('type')
    if notification_type:
        notifications = notifications.filter(notification_type=notification_type)
    
    # Filter by priority if requested
    priority = request.GET.get('priority')
    if priority:
        notifications = notifications.filter(priority=priority)
    
    # Filter by read status if requested
    status = request.GET.get('status')
    if status == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status == 'read':
        notifications = notifications.filter(is_read=True)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        notifications = notifications.filter(
            Q(title__icontains=search) | Q(message__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get notification counts for sidebar
    notification_counts = {
        'total': Notification.objects.filter(recipient=request.user).exclude(expires_at__lt=timezone.now()).count(),
        'unread': Notification.objects.filter(recipient=request.user, is_read=False).exclude(expires_at__lt=timezone.now()).count(),
        'critical': Notification.objects.filter(recipient=request.user, priority='critical').exclude(expires_at__lt=timezone.now()).count(),
        'high': Notification.objects.filter(recipient=request.user, priority='high').exclude(expires_at__lt=timezone.now()).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'total_notifications': notification_counts['total'],
        'unread_count': notification_counts['unread'],
        'critical_count': notification_counts['critical'],
        'high_count': notification_counts['high'],
        'per_page': 20,
        'current_type': notification_type,
        'current_priority': priority,
        'current_status': status,
        'search_query': search,
        'title': 'Notifications',
    }
    
    return render(request, 'core/notification_list.html', context)

@login_required
def notification_detail(request, notification_id):
    """View a specific notification and mark it as read"""
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user
    )
    
    # Mark as read
    notification.mark_as_read()
    
    # Get related object details based on notification type
    related_object = None
    worker = None
    document = None
    probation_period = None
    
    if notification.related_object_type and notification.related_object_id:
        try:
            if notification.related_object_type == 'worker_document':
                from zone.models import Document
                document = Document.objects.get(id=notification.related_object_id)
                worker = document.worker
                related_object = document
            elif notification.related_object_type == 'worker_probation':
                from zone.models import WorkerProbationPeriod
                probation_period = WorkerProbationPeriod.objects.get(id=notification.related_object_id)
                worker = probation_period.worker
                related_object = probation_period
        except Exception as e:
    
            pass
    context = {
        'notification': notification,
        'related_object': related_object,
        'worker': worker,
        'document': document,
        'probation_period': probation_period,
        'today': timezone.now().date(),
        'title': f'Notification: {notification.title}',
    }
    
    return render(request, 'core/notification_detail.html', context)

@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a single notification as read via AJAX"""
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user
    )
    
    notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'message': 'Notification marked as read'
    })

@login_required
@require_POST
def mark_all_notifications_read(request):
    """Mark all notifications as read via AJAX"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    ).exclude(
        expires_at__lt=timezone.now()
    ).update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return JsonResponse({
        'success': True,
        'count': count,
        'message': f'Marked {count} notifications as read'
    })

@login_required
@require_POST
def dismiss_notification(request, notification_id):
    """Dismiss a notification via AJAX"""
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        recipient=request.user
    )
    
    notification.dismiss()
    
    return JsonResponse({
        'success': True,
        'message': 'Notification dismissed'
    })

@login_required
@require_POST
def dismiss_all_notifications(request):
    """Dismiss all notifications via AJAX"""
    count = Notification.objects.filter(
        recipient=request.user,
        is_dismissed=False
    ).exclude(
        expires_at__lt=timezone.now()
    ).update(
        is_dismissed=True
    )
    
    return JsonResponse({
        'success': True,
        'count': count,
        'message': f'Dismissed {count} notifications'
    })

@login_required
def notification_api(request):
    """API endpoint for getting notifications data"""
    notifications = Notification.objects.filter(
        recipient=request.user,
        is_dismissed=False
    ).exclude(
        expires_at__lt=timezone.now()
    ).order_by('-created_at')[:10]
    
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'title': notification.title,
            'message': notification.message,
            'type': notification.notification_type,
            'priority': notification.priority,
            'priority_class': notification.priority_class,
            'priority_icon': notification.priority_icon,
            'is_read': notification.is_read,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
            'action_text': notification.action_text,
        })
    
    return JsonResponse({
        'notifications': data,
        'unread_count': notifications.filter(is_read=False).count(),
        'total_count': notifications.count(),
    })

@login_required
def notification_dashboard_widget(request):
    """Dashboard widget showing notification summary"""
    # Get recent critical notifications
    critical_notifications = Notification.objects.filter(
        recipient=request.user,
        priority__in=['critical', 'high'],
        is_dismissed=False,
        created_at__gte=timezone.now() - timedelta(days=7)
    ).exclude(
        expires_at__lt=timezone.now()
    ).order_by('-created_at')[:5]
    
    # Get notification counts by type
    type_counts = {}
    for notification_type, display_name in Notification.TYPE_CHOICES:
        count = Notification.objects.filter(
            recipient=request.user,
            notification_type=notification_type,
            is_read=False,
            is_dismissed=False
        ).exclude(
            expires_at__lt=timezone.now()
        ).count()
        
        if count > 0:
            type_counts[notification_type] = {
                'count': count,
                'display_name': display_name
            }
    
    # Get recent notifications for the widget
    recent_notifications = Notification.objects.filter(
        recipient=request.user,
        is_dismissed=False
    ).exclude(
        expires_at__lt=timezone.now()
    ).order_by('-created_at')[:5]
    
    # Get counts
    unread_count = Notification.objects.filter(
        recipient=request.user,
        is_read=False,
        is_dismissed=False
    ).exclude(
        expires_at__lt=timezone.now()
    ).count()
    
    critical_count = Notification.objects.filter(
        recipient=request.user,
        priority='critical',
        is_dismissed=False
    ).exclude(
        expires_at__lt=timezone.now()
    ).count()
    
    high_count = Notification.objects.filter(
        recipient=request.user,
        priority='high',
        is_dismissed=False
    ).exclude(
        expires_at__lt=timezone.now()
    ).count()
    
    total_count = Notification.objects.filter(
        recipient=request.user,
        is_dismissed=False
    ).exclude(
        expires_at__lt=timezone.now()
    ).count()
    
    context = {
        'recent_notifications': recent_notifications,
        'critical_notifications': critical_notifications,
        'type_counts': type_counts,
        'unread_count': unread_count,
        'critical_count': critical_count,
        'high_count': high_count,
        'total_count': total_count,
    }
    
    return render(request, 'core/notification_dashboard_widget.html', context)

def get_user_statistics():
    """
    Calculate comprehensive user statistics for dashboards.
    Returns a dictionary with user counts by role and status.
    """
    total_users = User.objects.filter(is_superuser=False).count()
    
    # Count users by type using the zone profile
    from zone.models import UserProfile
    admin_users = UserProfile.objects.filter(user_type='admin').count()
    manager_users = UserProfile.objects.filter(user_type='manager').count()
    staff_users = UserProfile.objects.filter(user_type='staff').count()
    viewer_users = UserProfile.objects.filter(user_type='viewer').count()
    active_users = User.objects.filter(is_active=True, is_superuser=False).count()
    inactive_users = total_users - active_users
    
    # Role capacity calculations
    max_admin_users = 10  # Configurable limit
    max_regular_users = 1000  # Configurable limit
    admin_slots_remaining = max_admin_users - admin_users
    user_slots_remaining = max_regular_users - (staff_users + viewer_users)
    
    return {
        'total_users': total_users,
        'admin_users': admin_users,
        'manager_users': manager_users,
        'staff_users': staff_users,
        'viewer_users': viewer_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'max_admin_users': max_admin_users,
        'max_regular_users': max_regular_users,
        'admin_slots_remaining': admin_slots_remaining,
        'user_slots_remaining': user_slots_remaining,
        'can_create_admin': admin_slots_remaining > 0,
        'can_create_user': user_slots_remaining > 0,
        'regular_users': staff_users + viewer_users,  # For backward compatibility
    }

@method_decorator(login_required, name='dispatch')
class SecureMediaView(View):
    """
    Secure view for serving encrypted media files.
    Only serves files to authenticated users who have access to them.
    """
    
    def get(self, request, file_path):
        """Serve encrypted files with proper decryption."""
        try:
            # Security check: only serve .enc files through this view
            if not file_path.endswith('.enc'):
                raise Http404("File not found")
            
            # Build full file path
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)
            
            # Check if file exists
            if not os.path.exists(full_path):
                raise Http404("File not found")
            
            # Find the document that owns this file
            document = None
            try:
                # Try to find document by file path
                documents = Document.objects.filter(document_file__icontains=file_path.split('/')[-1])
                for doc in documents:
                    if doc.document_file.name == file_path:
                        document = doc
                        break
                
                if not document:
                    raise Http404("Document not found")
                
            except Exception as e:

                
                pass
                raise Http404("Document not found")
            
            # Security check: verify user has access to this document
            # For now, any authenticated user can access (you may want to add more restrictions)
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")
            
            # Read and decrypt the file
            try:
                with open(full_path, 'rb') as f:
                    encrypted_content = f.read().decode('utf-8')
                
                decrypted_content = FileEncryptionHandler.decrypt_file_content(encrypted_content)
                
                # Determine content type
                original_filename = file_path.replace('.enc', '')
                content_type, _ = mimetypes.guess_type(original_filename)
                if not content_type:
                    content_type = 'application/octet-stream'
                
                # Create response
                response = HttpResponse(decrypted_content, content_type=content_type)
                
                # Set headers for proper file handling
                if content_type.startswith('image/'):
                    response['Content-Disposition'] = f'inline; filename="{os.path.basename(original_filename)}"'
                else:
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(original_filename)}"'
                
                response['Content-Length'] = len(decrypted_content)
                
                return response
                
            except Exception as e:

                
                pass
                raise Http404("File could not be processed")
                
        except Http404:

                
            pass
            raise
        except Exception as e:
            raise Http404("File not found")


@login_required
@require_http_methods(["GET"])
def serve_worker_document(request, document_id):
    """
    Serve a specific worker document by ID.
    More secure alternative to direct file access.
    """
    try:
        document = get_object_or_404(Document, id=document_id)
        
        # Security check: verify user has access to this document
        # Add your access control logic here
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required")
        
        # Check if document has a file
        if not document.document_file or not document.document_file.name:
            raise Http404("Document file not found")
        
        # Get the file path
        file_path = document.document_file.path
        
        if not os.path.exists(file_path):
            raise Http404("Document file not found on disk")
        
        # Read and decrypt if needed
        try:
            if document.document_file.name.endswith('.enc'):
                # Encrypted file - decrypt it
                with open(file_path, 'rb') as f:
                    encrypted_content = f.read().decode('utf-8')
                
                decrypted_content = FileEncryptionHandler.decrypt_file_content(encrypted_content)
                file_content = decrypted_content
                original_filename = document.document_file.name.replace('.enc', '')
            else:
                # Non-encrypted file - serve directly
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                original_filename = document.document_file.name
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(original_filename)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Create response
            response = HttpResponse(file_content, content_type=content_type)
            
            # Set headers
            filename = f"{document.get_document_type_display()}_{document.document_number}.{original_filename.split('.')[-1]}"
            if content_type.startswith('image/'):
                response['Content-Disposition'] = f'inline; filename="{filename}"'
            else:
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            response['Content-Length'] = len(file_content)
            
            return response
            
        except Exception as e:

            
            pass
            raise Http404("Document could not be processed")
            
    except Document.DoesNotExist:

            
        pass
        raise Http404("Document not found")
    except Exception as e:
        raise Http404("Document not found")

def permission_denied_view(request, exception=None):
    """
    Custom 403 permission denied view with user-friendly message
    """
    # Get some context about what the user was trying to access
    path = request.path
    user = request.user
    
    # Get user's current role assignment
    current_role = None
    try:
        current_role = UserRoleAssignment.objects.filter(user=user, is_active=True).first()
    except Exception:
        pass
    
    # Determine what feature they were trying to access
    feature_name = "this feature"
    required_permission = "access"
    suggestions = []
    
    if "/hr/positions/" in path:
        feature_name = "HR Positions Management"
        required_permission = "view HR positions"
        suggestions = [
            "Contact your system administrator to request HR permissions",
            "You may need the 'HR Manager' or 'HR Staff' role to access this feature",
            "Check with your supervisor about getting access to HR management tools"
        ]
    elif "/hr/departments/" in path:
        feature_name = "HR Departments Management"
        required_permission = "view HR departments"
        suggestions = [
            "Contact your system administrator to request HR permissions",
            "You may need the 'HR Manager' or 'HR Staff' role to access this feature",
            "Check with your supervisor about getting access to HR management tools"
        ]
    elif "/hr/" in path:
        feature_name = "HR Management"
        required_permission = "access HR features"
        suggestions = [
            "Contact your system administrator to request HR permissions",
            "You may need an HR-related role to access these features",
            "Check with your supervisor about getting access to HR management tools"
        ]
    elif "/user-management/" in path:
        feature_name = "User Management"
        required_permission = "manage users and roles"
        suggestions = [
            "Contact your system administrator to request user management permissions",
            "You may need the 'Admin' or 'User Manager' role to access this feature",
            "This feature is typically restricted to system administrators"
        ]
    elif "/audit/" in path:
        feature_name = "Audit Management"
        required_permission = "view audit logs"
        suggestions = [
            "Contact your system administrator to request audit access",
            "You may need the 'Auditor' or 'Admin' role to access this feature",
            "Audit logs are typically restricted to authorized personnel only"
        ]
    
    context = {
        'feature_name': feature_name,
        'required_permission': required_permission,
        'suggestions': suggestions,
        'user': user,
        'path': path,
        'current_role': current_role,
    }
    
    return render(request, 'core/permission_denied.html', context, status=403)


# Nationality Management Views
from .models import Nationality
from django.urls import reverse

@login_required
def nationality_list(request):
    """List all nationalities with search and pagination"""
    search_query = request.GET.get('search', '')
    region_filter = request.GET.get('region', '')

    nationalities = Nationality.objects.all()

    if search_query:
        nationalities = nationalities.filter(
            Q(zip_code__icontains=search_query) |
            Q(country_code__icontains=search_query) |
            Q(country_name__icontains=search_query) |
            Q(nationality__icontains=search_query)
        )

    if region_filter:
        nationalities = nationalities.filter(region__icontains=region_filter)

    nationalities = nationalities.order_by('country_name')

    # Get unique regions for filter dropdown
    regions = Nationality.objects.values_list('region', flat=True).distinct().order_by('region')

    # Pagination
    paginator = Paginator(nationalities, 25)  # Show 25 nationalities per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'region_filter': region_filter,
        'regions': regions,
        'title': 'Nationality Management',
    }

    return render(request, 'core/nationality_list.html', context)

@login_required
def nationality_detail(request, pk):
    """View details of a specific nationality"""
    nationality = get_object_or_404(Nationality, pk=pk)

    context = {
        'nationality': nationality,
        'title': f'Nationality: {nationality.country_name}',
    }

    return render(request, 'core/nationality_detail.html', context)

@login_required
def nationality_create(request):
    """Create a new nationality"""
    if request.method == 'POST':
        try:
            nationality = Nationality(
                zip_code=request.POST.get('zip_code'),
                country_code=request.POST.get('country_code'),
                country_name=request.POST.get('country_name'),
                nationality=request.POST.get('nationality'),
                region=request.POST.get('region'),
                created_by=request.user
            )
            nationality.full_clean()
            nationality.save()

            messages.success(request, f'Nationality "{nationality.country_name}" created successfully!')
            return redirect('core:nationality_detail', pk=nationality.pk)

        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        except Exception as e:
            messages.error(request, f'Error creating nationality: {str(e)}')

    context = {
        'title': 'Create New Nationality',
    }

    return render(request, 'core/nationality_form.html', context)

@login_required
def nationality_edit(request, pk):
    """Edit an existing nationality"""
    nationality = get_object_or_404(Nationality, pk=pk)

    if request.method == 'POST':
        try:
            nationality.zip_code = request.POST.get('zip_code')
            nationality.country_code = request.POST.get('country_code')
            nationality.country_name = request.POST.get('country_name')
            nationality.nationality = request.POST.get('nationality')
            nationality.region = request.POST.get('region')

            nationality.full_clean()
            nationality.save()

            messages.success(request, f'Nationality "{nationality.country_name}" updated successfully!')
            return redirect('core:nationality_detail', pk=nationality.pk)

        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
        except Exception as e:
            messages.error(request, f'Error updating nationality: {str(e)}')

    context = {
        'nationality': nationality,
        'title': f'Edit Nationality: {nationality.country_name}',
    }

    return render(request, 'core/nationality_form.html', context)

@login_required
@require_POST
def nationality_delete(request, pk):
    """Delete a nationality"""
    nationality = get_object_or_404(Nationality, pk=pk)

    try:
        country_name = nationality.country_name
        nationality.delete()
        messages.success(request, f'Nationality "{country_name}" deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting nationality: {str(e)}')

    return redirect('core:nationality_list')