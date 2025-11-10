import base64
import io
import json
from django import template
from django.utils.safestring import mark_safe
from django.utils import timezone
import qrcode
from barcode import Code128
from barcode.writer import ImageWriter

register = template.Library()


@register.simple_tag
def worker_qr_code(card, size=100):
    """Generate a QR code for a worker ID card containing comprehensive JSON data including documents."""
    try:
        # Get worker documents
        documents = {}
        document_summary = {}
        
        # Process worker documents
        for doc in card.worker.documents.all():
            doc_type = doc.document_type
            documents[doc_type] = {
                'document_number': doc.document_number,
                'issue_date': doc.issue_date.isoformat() if doc.issue_date else None,
                'expiry_date': doc.expiry_date.isoformat() if doc.expiry_date else None,
                'issuing_authority': doc.issuing_authority,
                'is_expired': doc.expiry_date <= timezone.now().date() if doc.expiry_date else False,
            }
            
            # Create document summary for quick reference
            if doc.expiry_date:
                document_summary[f'{doc_type}_expiry'] = doc.expiry_date.isoformat()
                document_summary[f'{doc_type}_expired'] = doc.expiry_date <= timezone.now().date() if doc.expiry_date else False
        
        # Prepare comprehensive data for QR code
        qr_data = {
            'type': 'worker_id_card',
            'version': '2.0',  # Version to indicate enhanced data structure
            'timestamp': card.updated_at.isoformat() if card.updated_at else None,
            
            # Core worker information
            'card_id': card.id,
            'worker_id': card.worker.worker_id,
            'worker_name': card.worker.get_full_name(),
            'first_name': card.worker.first_name,
            'last_name': card.worker.last_name,
            'nickname': card.worker.nickname,
            'card_number': card.card_number or f'TEMP-{card.id}',
            
            # Personal information
            'gender': card.worker.get_sex_display() if card.worker.sex else None,
            'date_of_birth': card.worker.dob.isoformat() if card.worker.dob else None,
            'age': card.worker.age,
            'nationality': card.worker.get_nationality_display() if card.worker.nationality else None,
            'phone_number': str(card.worker.phone_number) if card.worker.phone_number else None,
            
            # Work information
            'position': card.worker.position.name if card.worker.position else None,
            'zone': card.worker.zone.name if card.worker.zone else None,
            'building': card.worker.building.name if card.worker.building else None,
            'floor': card.worker.floor.name if card.worker.floor else None,
            'floor_number': card.worker.floor.floor_number if card.worker.floor else None,
            'worker_status': card.worker.status,
            'is_vip': card.worker.is_vip,
            'date_joined': card.worker.date_joined.isoformat() if card.worker.date_joined else None,
            'performance_rating': card.worker.performance_rating,
            
            # Card information
            'card_status': card.status,
            'request_date': card.request_date.isoformat() if card.request_date else None,
            'issue_date': card.issue_date.isoformat() if card.issue_date else None,
            'expiry_date': card.expiry_date.isoformat() if card.expiry_date else None,
            'card_expired': card.is_expired,
            
            # Document information (detailed)
            'documents': documents,
            
            # Document summary (quick access)
            'document_summary': document_summary,
            
            # Additional metadata
            'has_photo': card.worker.has_photo(),
            'total_documents': card.worker.documents.count(),
            'valid_documents': card.worker.documents.filter(expiry_date__gt=timezone.now().date()).count() if card.worker.documents.exists() else 0,
            'expired_documents': card.worker.documents.filter(expiry_date__lte=timezone.now().date()).count() if card.worker.documents.exists() else 0,
        }
        
        # Create QR code with higher error correction and version for more data
        qr = qrcode.QRCode(
            version=2,  # Reduced version to avoid data overflow
            error_correction=qrcode.constants.ERROR_CORRECT_L,  # Low error correction for more data capacity
            box_size=3,
            border=1,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = buffer.getvalue()
        buffer.close()
        
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        return mark_safe(f'<img src="data:image/png;base64,{img_base64}" width="{size}" height="{size}" alt="QR Code" style="display: block;">')
        
    except Exception as e:

        
        pass
        # Return placeholder if QR generation fails
        return mark_safe(f'<div style="width: {size}px; height: {size}px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #666;">QR</div>')


@register.simple_tag
def worker_barcode(card, width=150, height=30):
    """Generate a barcode for a worker ID card."""
    try:
        # Use card number or worker ID for barcode
        code_data = card.card_number or card.worker.worker_id or f'TEMP{card.id}'
        
        # Generate barcode
        barcode = Code128(code_data, writer=ImageWriter())
        
        # Create image in memory
        buffer = io.BytesIO()
        barcode.write(buffer, options={
            'module_width': 0.3,
            'module_height': 8,
            'font_size': 8,
            'text_distance': 2,
            'quiet_zone': 2
        })
        buffer.seek(0)
        
        # Convert to base64
        img_data = buffer.getvalue()
        buffer.close()
        
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        return mark_safe(f'<img src="data:image/png;base64,{img_base64}" width="{width}" height="{height}" alt="Barcode" style="display: block;">')
        
    except Exception as e:

        
        pass
        # Return placeholder if barcode generation fails
        return mark_safe(f'<div style="width: {width}px; height: {height}px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 10px; color: #666; font-family: monospace;">|||||||||||</div>')


@register.simple_tag
def simple_qr_code(data, size=100):
    """Generate a simple QR code from any text data."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=1,
        )
        qr.add_data(str(data))
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = buffer.getvalue()
        buffer.close()
        
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        return mark_safe(f'<img src="data:image/png;base64,{img_base64}" width="{size}" height="{size}" alt="QR Code">')
        
    except Exception:

        
        pass
        return mark_safe(f'<div style="width: {size}px; height: {size}px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #666;">QR</div>')


@register.simple_tag
def worker_qr_code_data(card):
    """Get the QR code data as JSON string for debugging purposes."""
    try:
        # Get worker documents
        documents = {}
        document_summary = {}
        
        # Process worker documents
        for doc in card.worker.documents.all():
            doc_type = doc.document_type
            documents[doc_type] = {
                'document_number': doc.document_number,
                'issue_date': doc.issue_date.isoformat() if doc.issue_date else None,
                'expiry_date': doc.expiry_date.isoformat() if doc.expiry_date else None,
                'issuing_authority': doc.issuing_authority,
                'is_expired': doc.expiry_date <= timezone.now().date() if doc.expiry_date else False,
            }
            
            # Create document summary for quick reference
            if doc.expiry_date:
                document_summary[f'{doc_type}_expiry'] = doc.expiry_date.isoformat()
                document_summary[f'{doc_type}_expired'] = doc.expiry_date <= timezone.now().date() if doc.expiry_date else False
        
        # Prepare comprehensive data for QR code
        qr_data = {
            'type': 'worker_id_card',
            'version': '2.0',
            'timestamp': card.updated_at.isoformat() if card.updated_at else None,
            
            # Core worker information
            'card_id': card.id,
            'worker_id': card.worker.worker_id,
            'worker_name': card.worker.get_full_name(),
            'first_name': card.worker.first_name,
            'last_name': card.worker.last_name,
            'nickname': card.worker.nickname,
            'card_number': card.card_number or f'TEMP-{card.id}',
            
            # Personal information
            'gender': card.worker.get_sex_display() if card.worker.sex else None,
            'date_of_birth': card.worker.dob.isoformat() if card.worker.dob else None,
            'age': card.worker.age,
            'nationality': card.worker.get_nationality_display() if card.worker.nationality else None,
            'phone_number': str(card.worker.phone_number) if card.worker.phone_number else None,
            
            # Work information
            'position': card.worker.position.name if card.worker.position else None,
            'zone': card.worker.zone.name if card.worker.zone else None,
            'building': card.worker.building.name if card.worker.building else None,
            'floor': card.worker.floor.name if card.worker.floor else None,
            'floor_number': card.worker.floor.floor_number if card.worker.floor else None,
            'worker_status': card.worker.status,
            'is_vip': card.worker.is_vip,
            'date_joined': card.worker.date_joined.isoformat() if card.worker.date_joined else None,
            'performance_rating': card.worker.performance_rating,
            
            # Card information
            'card_status': card.status,
            'request_date': card.request_date.isoformat() if card.request_date else None,
            'issue_date': card.issue_date.isoformat() if card.issue_date else None,
            'expiry_date': card.expiry_date.isoformat() if card.expiry_date else None,
            'card_expired': card.is_expired,
            
            # Document information (detailed)
            'documents': documents,
            
            # Document summary (quick access)
            'document_summary': document_summary,
            
            # Additional metadata
            'has_photo': card.worker.has_photo(),
            'total_documents': card.worker.documents.count(),
            'valid_documents': card.worker.documents.filter(expiry_date__gt=timezone.now().date()).count() if card.worker.documents.exists() else 0,
            'expired_documents': card.worker.documents.filter(expiry_date__lte=timezone.now().date()).count() if card.worker.documents.exists() else 0,
        }
        
        return json.dumps(qr_data, indent=2)
        
    except Exception as e:

        
        pass
        return f"Error generating QR data: {str(e)}"


@register.simple_tag
def worker_card_url(card):
    """Generate a URL for worker card verification."""
    from django.urls import reverse
    from django.conf import settings
    
    try:
        # This would be a public verification URL
        path = reverse('cards:worker_id_card_detail', kwargs={'pk': card.id})
        domain = getattr(settings, 'SITE_DOMAIN', 'localhost:8000')
        protocol = 'https' if getattr(settings, 'SECURE_SSL_REDIRECT', False) else 'http'
        return f"{protocol}://{domain}{path}"
    except Exception:
        return f"Card-{card.id}"


@register.simple_tag
def debug_qr_generation(card):
    """Debug QR code generation - shows if template tag is being called."""
    try:
        return mark_safe(f'<div style="background: yellow; padding: 5px; font-size: 10px;">QR Debug: Worker ID {card.worker.worker_id}, Card ID {card.id}, Documents: {card.worker.documents.count()}</div>')
    except Exception as e:
        return mark_safe(f'<div style="background: red; color: white; padding: 5px; font-size: 10px;">QR Debug Error: {str(e)}</div>')


@register.simple_tag
def worker_qr_code_lite(card, size=100):
    """Generate a lightweight QR code for a worker ID card with essential data only."""
    try:
        # Prepare essential data only for QR code
        qr_data = {
            'type': 'worker_id_card_lite',
            'version': '1.0',
            'worker_id': card.worker.worker_id,
            'worker_name': card.worker.get_full_name(),
            'card_number': card.card_number or f'TEMP-{card.id}',
            'position': card.worker.position.name if card.worker.position else None,
            'building': card.worker.building.name if card.worker.building else None,
            'status': card.status,
            'nationality': card.worker.get_nationality_display() if card.worker.nationality else None,
            'card_id': card.id,
        }
        
        # Add document summary (only critical info)
        if card.worker.documents.exists():
            from django.utils import timezone
            current_date = timezone.now().date()
            
            for doc in card.worker.documents.all():
                if doc.expiry_date:
                    qr_data[f'{doc.document_type}_expiry'] = doc.expiry_date.isoformat()
                    # Calculate expired status manually
                    qr_data[f'{doc.document_type}_expired'] = doc.expiry_date <= current_date
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=1,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = buffer.getvalue()
        buffer.close()
        
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        return mark_safe(f'<img src="data:image/png;base64,{img_base64}" width="{size}" height="{size}" alt="Worker QR Code Lite" style="display: block;">')
        
    except Exception as e:

        
        pass
        # Return placeholder if QR generation fails
        return mark_safe(f'<div style="width: {size}px; height: {size}px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #666;">QR Lite Error: {str(e)}</div>')


@register.simple_tag
def worker_qr_code_simple_format(card, size=100):
    """Generate a QR code with format: {FULLNAME}>>>{ID_CARD}>>>{DOB}>>>{DOC_NO}"""
    try:
        # Get worker full name
        fullname = card.worker.get_full_name()

        # Get worker ID (assuming this is the ID_CARD field)
        id_card = card.worker.worker_id or f"TEMP-{card.id}"

        # Get date of birth
        dob = card.worker.dob.strftime('%Y-%m-%d') if card.worker.dob else ""

        # Get primary document number (prioritize ID card, then passport, then first available)
        doc_no = ""
        if card.worker.documents.exists():
            # Try to get ID card document first
            id_card_doc = card.worker.documents.filter(document_type='id_card').first()
            if id_card_doc:
                doc_no = id_card_doc.document_number
            else:
                # Fall back to passport
                passport_doc = card.worker.documents.filter(document_type='passport').first()
                if passport_doc:
                    doc_no = passport_doc.document_number
                else:
                    # Fall back to first available document
                    first_doc = card.worker.documents.first()
                    if first_doc:
                        doc_no = first_doc.document_number

        # Format: {FULLNAME}>>>{ID_CARD}>>>{DOB}>>>{DOC_NO}
        qr_data = f"{fullname}>>>{id_card}>>>{dob}>>>{doc_no}"

        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=1,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)

        # Create image
        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = buffer.getvalue()
        buffer.close()

        img_base64 = base64.b64encode(img_data).decode('utf-8')

        return mark_safe(f'<img src="data:image/png;base64,{img_base64}" width="{size}" height="{size}" alt="Worker QR Code Simple" style="display: block;">')

    except Exception as e:
        # Return placeholder if QR generation fails
        return mark_safe(f'<div style="width: {size}px; height: {size}px; background: #f0f0f0; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #666;">QR Simple Error: {str(e)}</div>')


@register.simple_tag
def test_simple_qr(text="TEST", size=100):
    """Generate a very basic test QR code."""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=2,
        )
        qr.add_data(str(text))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_data = buffer.getvalue()
        buffer.close()

        img_base64 = base64.b64encode(img_data).decode('utf-8')

        return mark_safe(f'<img src="data:image/png;base64,{img_base64}" width="{size}" height="{size}" alt="Test QR Code" style="border: 2px solid green;">')

    except Exception as e:
        return mark_safe(f'<div style="width: {size}px; height: {size}px; background: red; color: white; display: flex; align-items: center; justify-content: center; font-size: 10px;">ERROR: {str(e)}</div>') 