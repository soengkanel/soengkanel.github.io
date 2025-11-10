from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from django.db.models import Q
import json
import uuid
import logging

from .models import DeviceStatus, PassportScan, ScanImage, ScanResult, WebSocketSession

logger = logging.getLogger(__name__)


@login_required
def scanner_dashboard(request):
    """Main passport scanner interface"""
    # Get or create device status for current user/session
    device_status, created = DeviceStatus.objects.get_or_create(
        defaults={
            'device_name': 'Passport Scanner',
            'device_type': 'PassportReader',
            'status': 'disconnected'
        }
    )
    
    # Get recent scans for the user
    recent_scans = PassportScan.objects.filter(user=request.user)[:10]
    
    # Get active websocket session if any
    active_session = WebSocketSession.objects.filter(
        user=request.user,
        is_active=True
    ).first()
    
    context = {
        'device_status': device_status,
        'recent_scans': recent_scans,
        'active_session': active_session,
        'page_title': 'Passport Scanner System',
    }
    
    return render(request, 'sinosecu/scanner_dashboard.html', context)



# API Endpoints for WebSocket communication

@csrf_exempt
@require_http_methods(["POST"])
def api_start_scan(request):
    """Start a new passport scan session"""
    try:
        data = json.loads(request.body)
        
        # Generate unique scan ID
        scan_id = f"SCAN_{uuid.uuid4().hex[:8].upper()}"
        
        # Create new scan record
        scan = PassportScan.objects.create(
            user=request.user,
            scan_id=scan_id,
            document_type=data.get('document_type', 'passport'),
            read_rfid=data.get('read_rfid', True),
            read_viz=data.get('read_viz', True),
            enable_rejection=data.get('enable_rejection', False),
            enable_callback=data.get('enable_callback', False),
            detect_card_removal=data.get('detect_card_removal', False),
            status='processing'
        )
        
        return JsonResponse({
            'success': True,
            'scan_id': scan_id,
            'message': 'Scan session started successfully'
        })
        
    except Exception as e:

        
        pass
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def api_save_scan_result(request):
    """Save scan results from WebSocket"""
    try:
        data = json.loads(request.body)
        scan_id = data.get('scan_id')
        
        if not scan_id:
            return JsonResponse({'success': False, 'error': 'scan_id required'}, status=400)
        
        scan = get_object_or_404(PassportScan, scan_id=scan_id)
        
        # Save extracted text data
        extracted_data = data.get('extracted_data', {})
        scan.extracted_data = extracted_data
        
        # Save images if provided
        images_data = data.get('images', {})
        for image_type, image_base64 in images_data.items():
            if image_base64:
                ScanImage.objects.update_or_create(
                    scan=scan,
                    image_type=image_type,
                    defaults={
                        'image_data': image_base64,
                        'width': data.get(f'{image_type}_width'),
                        'height': data.get(f'{image_type}_height'),
                    }
                )
        
        # Create or update scan result
        if extracted_data:
            result_data = {
                'full_name': extracted_data.get('姓名') or extracted_data.get('Name', ''),
                'gender': extracted_data.get('性别') or extracted_data.get('Sex', ''),
                'nationality': extracted_data.get('民族') or extracted_data.get('Nationality', ''),
                'document_number': extracted_data.get('公民身份证号码') or extracted_data.get('Document Number', ''),
                'address': extracted_data.get('住址') or extracted_data.get('Address', ''),
                'issuing_authority': extracted_data.get('签发机关') or extracted_data.get('Issuing Authority', ''),
                'additional_fields': extracted_data,
            }
            
            # Parse dates
            birth_date_str = extracted_data.get('出生') or extracted_data.get('出生日期') or extracted_data.get('Date of Birth')
            if birth_date_str:
                try:
                    from datetime import datetime
                    # Try different date formats
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d']:
                        try:
                            result_data['date_of_birth'] = datetime.strptime(birth_date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass
            
            ScanResult.objects.update_or_create(
                scan=scan,
                defaults=result_data
            )
        
        # Mark scan as completed
        scan.complete_scan(extracted_data=extracted_data)
        
        return JsonResponse({
            'success': True,
            'message': 'Scan results saved successfully'
        })
        
    except Exception as e:

        
        pass
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_update_device_status(request):
    """Update device connection status"""
    try:
        data = json.loads(request.body)
        
        device_status, created = DeviceStatus.objects.get_or_create(
            defaults={
                'device_name': 'Passport Scanner',
                'device_type': 'PassportReader',
                'status': 'disconnected'
            }
        )
        
        # Update device information
        device_status.device_name = data.get('device_name', device_status.device_name)
        device_status.device_serial = data.get('device_serial', device_status.device_serial)
        device_status.device_type = data.get('device_type', device_status.device_type)
        device_status.status = data.get('status', device_status.status)
        device_status.version_info = data.get('version_info', device_status.version_info)
        
        if data.get('status') == 'connected':
            device_status.last_connected = timezone.now()
        
        device_status.save()
        
        return JsonResponse({
            'success': True,
            'device_status': {
                'device_name': device_status.device_name,
                'device_serial': device_status.device_serial,
                'device_type': device_status.device_type,
                'status': device_status.status,
                'version_info': device_status.version_info,
            }
        })
        
    except Exception as e:

        
        pass
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_websocket_session(request):
    """Manage WebSocket session"""
    try:
        data = json.loads(request.body)
        action = data.get('action')  # 'start', 'ping', 'end'
        session_id = data.get('session_id')
        
        if action == 'start':
            # Create new WebSocket session
            device_status = DeviceStatus.objects.first()
            if not device_status:
                device_status = DeviceStatus.objects.create(
                    device_name='Passport Scanner',
                    device_type='PassportReader',
                    status='disconnected'
                )
            
            session = WebSocketSession.objects.create(
                session_id=session_id or f"WS_{uuid.uuid4().hex[:8]}",
                user=request.user,
                device_status=device_status,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'session_id': session.session_id
            })
            
        elif action == 'ping' and session_id:
            # Update session ping
            WebSocketSession.objects.filter(
                session_id=session_id,
                user=request.user
            ).update(last_ping=timezone.now())
            
            return JsonResponse({'success': True})
            
        elif action == 'end' and session_id:
            # End WebSocket session
            WebSocketSession.objects.filter(
                session_id=session_id,
                user=request.user
            ).update(is_active=False)
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)
        
    except Exception as e:

        
        pass
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
def api_get_device_status(request):
    """Get current device status"""
    device_status = DeviceStatus.objects.first()
    
    if not device_status:
        return JsonResponse({
            'success': False,
            'error': 'No device status found'
        }, status=404)
    
    return JsonResponse({
        'success': True,
        'device_status': {
            'device_name': device_status.device_name,
            'device_serial': device_status.device_serial,
            'device_type': device_status.device_type,
            'status': device_status.status,
            'version_info': device_status.version_info,
            'websocket_host': device_status.websocket_host,
            'auto_reconnect': device_status.auto_reconnect,
            'last_connected': device_status.last_connected.isoformat() if device_status.last_connected else None,
        }
    })


@login_required
def export_scan_data(request, scan_id):
    """Export scan data as JSON"""
    scan = get_object_or_404(PassportScan, scan_id=scan_id, user=request.user)
    
    # Prepare export data
    export_data = {
        'scan_id': scan.scan_id,
        'document_type': scan.document_type,
        'status': scan.status,
        'started_at': scan.started_at.isoformat(),
        'completed_at': scan.completed_at.isoformat() if scan.completed_at else None,
        'extracted_data': scan.extracted_data,
        'error_message': scan.error_message,
    }
    
    # Add scan result if exists
    if hasattr(scan, 'result'):
        result = scan.result
        export_data['scan_result'] = {
            'full_name': result.full_name,
            'gender': result.gender,
            'nationality': result.nationality,
            'date_of_birth': result.date_of_birth.isoformat() if result.date_of_birth else None,
            'document_number': result.document_number,
            'address': result.address,
            'issuing_authority': result.issuing_authority,
            'issue_date': result.issue_date.isoformat() if result.issue_date else None,
            'expiry_date': result.expiry_date.isoformat() if result.expiry_date else None,
            'mrz_line1': result.mrz_line1,
            'mrz_line2': result.mrz_line2,
            'mrz_line3': result.mrz_line3,
            'additional_fields': result.additional_fields,
        }
    
    # Add images metadata
    export_data['images'] = []
    for image in scan.images.all():
        export_data['images'].append({
            'image_type': image.image_type,
            'width': image.width,
            'height': image.height,
            'created_at': image.created_at.isoformat(),
            # Note: Not including base64 data for size reasons
        })
    
    response = HttpResponse(
        json.dumps(export_data, indent=2),
        content_type='application/json'
    )
    response['Content-Disposition'] = f'attachment; filename="scan_{scan_id}_export.json"'
    
    return response
