"""
SinoSecu API Service Module
Provides OCR and document processing capabilities via SinoSecu API
"""

import base64
import json
import logging
import requests
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from typing import Dict, Any, Optional, List
from .models import PassportScan, ScanImage, ScanResult

logger = logging.getLogger(__name__)


class SinoSecuAPIService:
    """Service class for SinoSecu API integration"""
    
    def __init__(self):
        # Default SinoSecu WebSocket endpoint (can be configured in settings)
        self.websocket_host = getattr(settings, 'SINOSECU_WEBSOCKET_HOST', 'ws://127.0.0.1:90/echo')
        self.api_timeout = getattr(settings, 'SINOSECU_API_TIMEOUT', 30)
        self.max_retries = getattr(settings, 'SINOSECU_API_RETRIES', 3)
    
    def process_document_image(self, image_path: str, document_type: str = 'id_card') -> Dict[str, Any]:
        """
        Process document image using SinoSecu OCR
        
        Args:
            image_path: Path to the image file
            document_type: Type of document (id_card, passport, work_permit, visa)
            
        Returns:
            Dict containing extracted data and images
        """
        try:
            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Simulate SinoSecu OCR processing
            # In production, this would make actual API calls to SinoSecu hardware/service
            extracted_data = self._simulate_ocr_extraction(image_base64, document_type)
            
            return {
                'success': True,
                'extracted_data': extracted_data,
                'images': {
                    'document_front': image_base64
                },
                'confidence_score': extracted_data.get('confidence', 0.95)
            }
            
        except Exception as e:

            
            pass
            return {
                'success': False,
                'error': str(e),
                'extracted_data': {},
                'images': {}
            }
    
    def _simulate_ocr_extraction(self, image_base64: str, document_type: str) -> Dict[str, Any]:
        """
        Simulate OCR extraction based on document type
        In production, this would call actual SinoSecu API endpoints
        """
        
        # Get current timestamp for realistic data
        current_date = datetime.now()
        
        if document_type == 'id_card':
            return {
                'document_type': 'National ID Card',
                'document_number': f'ID{current_date.strftime("%Y%m%d")}{current_date.microsecond}',
                'full_name': 'EXTRACTED_NAME',
                'english_first_name': 'EXTRACTED_FIRST',
                'english_surname': 'EXTRACTED_LAST',
                'sex': 'M',
                'nationality': 'KH',
                'date_of_birth': (current_date - timedelta(days=8000)).strftime('%Y-%m-%d'),
                'issuing_authority': 'Ministry of Interior',
                'issue_date': (current_date - timedelta(days=1800)).strftime('%Y-%m-%d'),
                'expiry_date': (current_date + timedelta(days=1800)).strftime('%Y-%m-%d'),
                'address': 'EXTRACTED_ADDRESS',
                'confidence': 0.95,
                'extracted_at': current_date.isoformat()
            }
            
        elif document_type == 'passport':
            return {
                'document_type': 'Passport',
                'passport_type': 'P',
                'document_number': f'P{current_date.strftime("%Y%m%d")}{current_date.microsecond}',
                'full_name': 'EXTRACTED_NAME',
                'english_first_name': 'EXTRACTED_FIRST',
                'english_surname': 'EXTRACTED_LAST',
                'sex': 'M',
                'nationality': 'KHM',
                'date_of_birth': (current_date - timedelta(days=8000)).strftime('%Y-%m-%d'),
                'place_of_birth': 'Cambodia',
                'issuing_country': 'Cambodia',
                'issuing_authority': 'Ministry of Foreign Affairs',
                'issue_date': (current_date - timedelta(days=1800)).strftime('%Y-%m-%d'),
                'expiry_date': (current_date + timedelta(days=1800)).strftime('%Y-%m-%d'),
                'mrz_line1': 'P<KHMEXTRACTED<<FIRST<<<<<<<<<<<<<<<<<<<<<<<',
                'mrz_line2': f'P{current_date.strftime("%Y%m%d")}{current_date.microsecond}<KHM{(current_date - timedelta(days=8000)).strftime("%y%m%d")}M{(current_date + timedelta(days=1800)).strftime("%y%m%d")}',
                'confidence': 0.95,
                'extracted_at': current_date.isoformat()
            }
            
        elif document_type == 'work_permit':
            return {
                'document_type': 'Work Permit',
                'document_number': f'WP{current_date.strftime("%Y%m%d")}{current_date.microsecond}',
                'full_name': 'EXTRACTED_NAME',
                'english_first_name': 'EXTRACTED_FIRST',
                'english_surname': 'EXTRACTED_LAST',
                'sex': 'M',
                'nationality': 'KH',
                'date_of_birth': (current_date - timedelta(days=8000)).strftime('%Y-%m-%d'),
                'issuing_authority': 'Ministry of Labour',
                'issue_date': (current_date - timedelta(days=365)).strftime('%Y-%m-%d'),
                'expiry_date': (current_date + timedelta(days=365)).strftime('%Y-%m-%d'),
                'employer': 'EXTRACTED_EMPLOYER',
                'position': 'EXTRACTED_POSITION',
                'confidence': 0.92,
                'extracted_at': current_date.isoformat()
            }
            
        elif document_type == 'visa':
            return {
                'document_type': 'Visa',
                'document_number': f'V{current_date.strftime("%Y%m%d")}{current_date.microsecond}',
                'full_name': 'EXTRACTED_NAME',
                'english_first_name': 'EXTRACTED_FIRST',
                'english_surname': 'EXTRACTED_LAST',
                'sex': 'M',
                'nationality': 'KH',
                'date_of_birth': (current_date - timedelta(days=8000)).strftime('%Y-%m-%d'),
                'visa_type': 'EB',
                'visa_category': 'Business',
                'issuing_country': 'Cambodia',
                'issuing_authority': 'Ministry of Foreign Affairs',
                'issue_date': (current_date - timedelta(days=180)).strftime('%Y-%m-%d'),
                'expiry_date': (current_date + timedelta(days=180)).strftime('%Y-%m-%d'),
                'entries': 'Multiple',
                'confidence': 0.90,
                'extracted_at': current_date.isoformat()
            }
        
        # Default fallback
        return {
            'document_type': 'Unknown',
            'document_number': f'DOC{current_date.strftime("%Y%m%d")}{current_date.microsecond}',
            'confidence': 0.75,
            'extracted_at': current_date.isoformat(),
            'note': 'Fallback extraction - manual verification required'
        }
    
    def create_scan_with_ocr(self, user, image_path: str, document_type: str, 
                           worker_id: Optional[int] = None) -> PassportScan:
                               pass
        """
        Create a scan record and process OCR in one operation
        
        Args:
            user: Django User instance
            image_path: Path to document image
            document_type: Type of document
            worker_id: Optional worker ID for tracking
            
        Returns:
            PassportScan instance with results
        """
        
        # Generate unique scan ID
        scan_id = f"IMPORT_{worker_id or 'BULK'}_{document_type}_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create scan record
        scan = PassportScan.objects.create(
            user=user,
            scan_id=scan_id,
            document_type=self._map_document_type(document_type),
            status='processing'
        )
        
        try:
            # Process image with OCR
            ocr_result = self.process_document_image(image_path, document_type)
            
            if ocr_result['success']:
                # Store extracted data
                scan.extracted_data = ocr_result['extracted_data']
                
                # Store images
                for image_type, image_data in ocr_result['images'].items():
                    ScanImage.objects.create(
                        scan=scan,
                        image_type=image_type,
                        image_data=image_data,
                    )
                
                # Create detailed scan result
                self._create_scan_result(scan, ocr_result['extracted_data'])
                
                # Mark as completed
                scan.status = 'completed'
                scan.completed_at = timezone.now()
                
            else:
                # Mark as failed with error
                scan.status = 'failed'
                scan.error_message = ocr_result.get('error', 'OCR processing failed')
                scan.completed_at = timezone.now()
                
        except Exception as e:

                
            pass
            scan.status = 'failed'
            scan.error_message = f"Processing error: {str(e)}"
            scan.completed_at = timezone.now()
        
        scan.save()
        return scan
    
    def _create_scan_result(self, scan: PassportScan, extracted_data: Dict[str, Any]) -> ScanResult:
        """Create ScanResult from extracted OCR data"""
        
        # Parse date fields safely
        def parse_date(date_str):
            if not date_str:
                return None
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                return None
        
        result_data = {
            'scan': scan,
            'full_name': extracted_data.get('full_name', ''),
            'given_names': extracted_data.get('english_first_name', ''),
            'surname': extracted_data.get('english_surname', ''),
            'gender': extracted_data.get('sex', ''),
            'nationality': extracted_data.get('nationality', ''),
            'date_of_birth': parse_date(extracted_data.get('date_of_birth')),
            'document_number': extracted_data.get('document_number', ''),
            'document_type': extracted_data.get('document_type', ''),
            'issuing_authority': extracted_data.get('issuing_authority', ''),
            'issue_date': parse_date(extracted_data.get('issue_date')),
            'expiry_date': parse_date(extracted_data.get('expiry_date')),
            'address': extracted_data.get('address', ''),
            'mrz_line1': extracted_data.get('mrz_line1', ''),
            'mrz_line2': extracted_data.get('mrz_line2', ''),
            'mrz_line3': extracted_data.get('mrz_line3', ''),
            'ocr_confidence': extracted_data.get('confidence', 0.0),
            'additional_fields': extracted_data
        }
        
        return ScanResult.objects.create(**result_data)
    
    def _map_document_type(self, field_type: str) -> str:
        """Map field type to SinoSecu document type"""
        mapping = {
            'id_document': 'id_card',
            'work_permit': 'work_permit',
            'visa': 'visa',
            'passport': 'passport',
        }
        return mapping.get(field_type, 'other')
    
    def batch_process_documents(self, document_list: List[Dict[str, Any]], user) -> Dict[str, Any]:
        """
        Process multiple documents in batch for improved performance
        
        Args:
            document_list: List of dicts with {image_path, document_type, worker_id}
            user: Django User instance
            
        Returns:
            Dict with processing results
        """
        results = {
            'processed': 0,
            'failed': 0,
            'scan_ids': [],
            'errors': []
        }
        
        for doc_info in document_list:
            try:
                scan = self.create_scan_with_ocr(
                    user=user,
                    image_path=doc_info['image_path'],
                    document_type=doc_info['document_type'],
                    worker_id=doc_info.get('worker_id')
                )
                
                if scan.status == 'completed':
                    results['processed'] += 1
                    results['scan_ids'].append(scan.scan_id)
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Scan {scan.scan_id}: {scan.error_message}")
                    
            except Exception as e:

                    
                pass
                results['failed'] += 1
                results['errors'].append(f"Document {doc_info.get('image_path', 'unknown')}: {str(e)}")
        
        return results


# Global service instance
sinosecu_service = SinoSecuAPIService()