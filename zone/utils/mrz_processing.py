"""
Step 2: MRZ Processing from JSON and Images
Process OCR/MRZ extraction from pre-extracted JSON and image files
"""

import json
import os
from datetime import datetime
import pytesseract
import cv2
import numpy as np
import logging

from django.conf import settings
from .mrz_parser import parse_mrz_lines

logger = logging.getLogger(__name__)

def correct_ocr_nationality(raw_nationality):
    """
    Correct common OCR errors in nationality codes.
    """
    if not raw_nationality:
        return raw_nationality
    
    # Common OCR corrections for nationality codes
    corrections = {
        'VWN': 'VNM',  # Vietnam - W often misread as VV/W
        'VN1': 'VNM',  # Vietnam - M often misread as 1
        'VN0': 'VNM',  # Vietnam - M often misread as 0
        '10N': 'IDN',  # Indonesia - I often misread as 1, N as N
        'I0N': 'IDN',  # Indonesia - D often misread as 0
        'IPN': 'IDN',  # Indonesia - D often misread as P
        'THN': 'THA',  # Thailand - A often misread as N
        'TH1': 'THA',  # Thailand - A often misread as 1
        'KH1': 'KHM',  # Cambodia - M often misread as 1
        'KHN': 'KHM',  # Cambodia - M often misread as N
        'KH0': 'KHM',  # Cambodia - M often misread as 0
        'CI': 'IDN',   # Common OCR error - CI misread for IDN (Indonesia)
        'CIN': 'IDN',  # Common OCR error - CIN misread for IDN
        'ID1': 'IDN',  # Indonesia - N often misread as 1
        'ID0': 'IDN',  # Indonesia - N often misread as 0
    }
    
    corrected = corrections.get(raw_nationality, raw_nationality)

    return corrected

def preprocess_image_for_mrz(image_path):
    """Enhanced image preprocessing specifically for MRZ extraction - based on OCR/process_mrz.py"""
    try:
        # Read image directly from path
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise (from OCR/process_mrz.py approach)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations to clean up
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed

    except Exception as e:
        return None

def extract_mrz_text_with_tesseract(image_path):
    """Extract MRZ text using Tesseract - based on OCR/process_mrz.py approach"""
    processed_img = preprocess_image_for_mrz(image_path)
    if processed_img is None:
        return {"error": f"Could not process image: {image_path}"}
    
    try:
        # Configure Tesseract for better MRZ recognition (from OCR/process_mrz.py)
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<'
        
        # Extract text
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        
        # Clean up the text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return {
            "raw_text": text,
            "lines": lines,
            "processed_image_path": image_path
        }
        
    except Exception as e:
        return {"error": f"OCR failed for {image_path}: {str(e)}"}

def parse_mrz_data_structured(mrz_text_data):
    """Parse MRZ data using updated mrz_parser.parse_mrz_lines function"""
    if "error" in mrz_text_data:
        return mrz_text_data
    
    lines = mrz_text_data.get("lines", [])
    
    try:
        # Use the updated parse_mrz_lines function which handles LDKHM correctly
        parsed_data = parse_mrz_lines(lines)
        
        # Add raw_mrz_lines for compatibility with existing code
        parsed_data["raw_mrz_lines"] = lines
        
        # Convert field names to match expected format
        result = {
            "document_type": parsed_data.get("document_type"),
            "country_code": parsed_data.get("issuing_country"),
            "document_number": parsed_data.get("document_number"),
            "surname": parsed_data.get("surname"),
            "given_names": parsed_data.get("given_names"), 
            "nationality": parsed_data.get("nationality"),
            "date_of_birth": parsed_data.get("date_of_birth"),
            "sex": parsed_data.get("sex"),
            "expiry_date": parsed_data.get("expiry_date"),
            "personal_number": parsed_data.get("personal_number"),
            "raw_mrz_lines": lines
        }


        return result

    except Exception as e:
        # Return basic structure with error
        return {
            "document_type": None,
            "country_code": None,
            "document_number": None,
            "surname": None,
            "given_names": None,
            "nationality": None,
            "date_of_birth": None,
            "sex": None,
            "expiry_date": None,
            "personal_number": None,
            "raw_mrz_lines": lines,
            "error": str(e)
        }

def extract_mrz_from_image(img_data, progress_tracker=None):
    """
    Extract MRZ data from a single image using OCR/process_mrz.py approach.
    Returns: (mrz_text, document_info)
    """
    if not img_data.get("path") or not os.path.exists(img_data["path"]):
        return None, {}

    try:
        pass
        
        # Use proven OCR/process_mrz.py approach
        mrz_text_data = extract_mrz_text_with_tesseract(img_data["path"])
        
        if "error" not in mrz_text_data:
            tesseract_lines = mrz_text_data.get("lines", [])
            
            mrz_lines = []
            
            for line in tesseract_lines:
                clean_line = line.replace(' ', '').upper()
                # Check if this looks like an MRZ line (standard format or IDKHM/LDKHM pattern)
                if ('<' in clean_line and len(clean_line) >= 28) or 'IDKHM' in clean_line or 'LDKHM' in clean_line:
                    mrz_lines.append(line)
            
            # Clean and format MRZ output
            if mrz_lines:
                # Clean each MRZ line to remove invalid characters
                cleaned_lines = []
                for line in mrz_lines:
                    # Keep only valid MRZ characters: A-Z, 0-9, <
                    cleaned_line = ''.join(c for c in line.upper() if c.isalnum() or c == '<')
                    # For IDKHM/LDKHM lines, accept shorter lines; for standard MRZ, require 20+ chars
                    min_length = 10 if ('IDKHM' in cleaned_line or 'LDKHM' in cleaned_line) else 20
                    if len(cleaned_line) > min_length:
                        cleaned_lines.append(cleaned_line)
                
                if cleaned_lines:
                    passport_mrz = '\n'.join(cleaned_lines)

                    # Process document information
                    mrz_text_data = {"lines": cleaned_lines}  # Use cleaned lines for parsing
                    document_info = parse_mrz_data_structured(mrz_text_data)

                    return passport_mrz, document_info
                else:
                    pass

        return None, {}

    except Exception as e:
        return None, {}

def process_mrz_from_json(json_file_path, progress_tracker=None):
    """
    Step 2: Process MRZ from JSON file with image references
    Returns: new_json_path with MRZ data
    """
    if not os.path.exists(json_file_path):
        raise FileNotFoundError(f"JSON file not found: {json_file_path}")
    
    # Load the JSON data
    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    # Handle new JSON structure with metadata
    if isinstance(json_data, dict) and 'records' in json_data:
        # New structure with metadata
        data = json_data['records']
        metadata = json_data.get('metadata', {})
    else:
        # Backward compatibility with old structure
        data = json_data
        metadata = {}
    
    # Create output filename
    media_root = getattr(settings, 'MEDIA_ROOT', '')
    json_dir = os.path.join(media_root, 'worker_import_json')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"worker_eforms_with_mrz_{timestamp}.json"
    output_path = os.path.join(json_dir, output_filename)
    
    transformed_data = []
    
    # Update progress
    if progress_tracker:
        progress_tracker.update(
            stage='processing_mrz',
            stage_message='Processing MRZ from passport/ID images...'
        )
    
    # Process each record
    for i, record in enumerate(data):
        transformed_record = record.copy()
        
        # Update progress
        if progress_tracker:
            progress_tracker.update(
                stage='processing_mrz',
                stage_message=f'Processing MRZ for {record.get("NAME", "Unknown")} ({i+1}/{len(data)})...'
            )
        
        # Process IDKH/PASSPORT images for MRZ
        if record.get("IDKH/PASSPORT"):
            # Handle both single image and multiple images
            idkh_data = record["IDKH/PASSPORT"]
            
            # If it's a single image (has 'path' key)
            if isinstance(idkh_data, dict) and idkh_data.get("path"):
                mrz_text, document_info = extract_mrz_from_image(idkh_data, progress_tracker)
                
                # Update the image data with MRZ info
                updated_image = idkh_data.copy()
                updated_image["mrz"] = mrz_text
                updated_image["document"] = document_info
                updated_image["mrz_processed"] = True
                
                transformed_record['IDKH/PASSPORT'] = updated_image
                
            # If it's multiple images (list)
            elif isinstance(idkh_data, list):
                processed_images = []
                for img_data in idkh_data:
                    if img_data.get("path"):
                        mrz_text, document_info = extract_mrz_from_image(img_data, progress_tracker)
                        
                        # Update the image data with MRZ info
                        updated_image = img_data.copy()
                        updated_image["mrz"] = mrz_text
                        updated_image["document"] = document_info
                        updated_image["mrz_processed"] = True
                        
                        processed_images.append(updated_image)
                    else:
                        processed_images.append(img_data)
                
                transformed_record['IDKH/PASSPORT'] = processed_images
        
        transformed_data.append(transformed_record)
    
    # Save results with preserved metadata structure
    if metadata:
        # Create output with same structure, including metadata
        output_data = {
            'records': transformed_data,
            'metadata': {
                **metadata,  # Preserve original metadata
                'mrz_processed': True,
                'mrz_processing_timestamp': datetime.now().isoformat()
            }
        }
    else:
        # Legacy structure - just the records array
        output_data = transformed_data
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    # Update progress
    if progress_tracker:
        progress_tracker.update(
            stage='completed_mrz',
            stage_message=f'Step 2 complete: MRZ processed for {len(transformed_data)} records'
        )

    return output_path, len(transformed_data)