"""
Simplified Excel Import Functions
Based on actual OCR/worker_eform.xlsx structure analysis
"""
import pandas as pd
import openpyxl
from datetime import datetime

# Excel Column Mapping - Based on actual file structure
EXCEL_COLUMNS = {
    # Basic Info
    'NO': 'A',
    'PHOTO': 'B', 
    'NAME': 'C',
    'SEX': 'D',
    'DOB': 'E',
    'NATIONALITY': 'F',
    'BUILDING': 'G',
    'POSITION': 'H',
    'JOINEDDATE': 'I',
    'RESIGNEDDATE': 'J',
    
    # Document Files
    'IDKH/PASSPORT': 'K',
    'WORKINGPERMIT': 'N', 
    'VISA': 'Q',
    
    # Document Numbers
    'IDKHPASSPORT NO': 'L',
    'WORKINGPERMIT NO': 'O',
    'VISA NO': 'R',
    
    # Document Dates
    'IDKH/PASSPORT_DATE': 'M',
    'WORKINGPERMIT_DATE': 'P', 
    'VISA_DATE': 'S',
}

# Reverse mapping for easy lookup
COLUMN_TO_FIELD = {v: k for k, v in EXCEL_COLUMNS.items()}

def read_excel_data(file_path):
    """Read Excel data using pandas - simple and clean."""
    df = pd.read_excel(file_path, engine='openpyxl')
    return df.to_dict('records')

def extract_worker_data(record):
    """Extract worker data from Excel record - simplified."""
    
    # Basic info extraction
    full_name = str(record.get('NAME', '')).strip()
    name_parts = full_name.split(' ', 1) if full_name else ['', '']
    
    # Parse dates
    dob = parse_date(record.get('DOB'))
    joined_date = parse_date(record.get('JOINEDDATE'))
    resigned_date = parse_date(record.get('RESIGNEDDATE'))
    
    # Parse document dates
    passport_dates = parse_date_range(record.get('IDKH/PASSPORT_DATE'))
    visa_dates = parse_date_range(record.get('VISA_DATE'))
    workpermit_dates = parse_date_range(record.get('WORKINGPERMIT_DATE'))
    
    # Format document numbers
    passport_no = format_document_number(record.get('IDKHPASSPORT NO'))
    visa_no = format_document_number(record.get('VISA NO'))
    workpermit_no = format_document_number(record.get('WORKINGPERMIT NO'))
    
    return {
        # Personal Info
        'first_name': name_parts[0],
        'last_name': name_parts[1] if len(name_parts) > 1 else '',
        'sex': str(record.get('SEX', '')).upper(),
        'dob': dob,
        'nationality': map_nationality(record.get('NATIONALITY')),
        'phone_number': str(record.get('PHONE_NUMBER', '')).strip(),
        
        # Work Info
        'building_name': record.get('BUILDING', ''),
        'position_name': record.get('POSITION', 'STAFF'),
        'joined_date': joined_date,
        'resigned_date': resigned_date,
        'status': 'active',
        
        # Document Numbers
        'passport_document_number': passport_no,
        'visa_document_number': visa_no,
        'workpermit_document_number': workpermit_no,
        
        # Document Dates
        'passport_issue_date': passport_dates[0] if passport_dates else None,
        'passport_expiry_date': passport_dates[1] if passport_dates else None,
        'visa_issue_date': visa_dates[0] if visa_dates else None,
        'visa_expiry_date': visa_dates[1] if visa_dates else None,
        'workpermit_issue_date': workpermit_dates[0] if workpermit_dates else None,
        'workpermit_expiry_date': workpermit_dates[1] if workpermit_dates else None,
        
        # File references
        'photo_filename': str(record.get('PHOTO', '')),
        'passport_filename': str(record.get('IDKH/PASSPORT', '')),
        'visa_filename': str(record.get('VISA', '')),
        'workpermit_filename': str(record.get('WORKINGPERMIT', '')),
    }

def create_worker_documents(worker, worker_data, created_by):
    """Create document records - simplified and clear."""
    from zone.models import Document
    
    documents_created = []
    
    # Document types to process
    doc_types = [
        ('passport', 'passport_document_number', 'passport_issue_date', 'passport_expiry_date', 'Immigration'),
        ('visa', 'visa_document_number', 'visa_issue_date', 'visa_expiry_date', 'Immigration'), 
        ('work_permit', 'workpermit_document_number', 'workpermit_issue_date', 'workpermit_expiry_date', 'Labor Department'),
    ]
    
    for doc_type, number_field, issue_field, expiry_field, authority in doc_types:
        doc_number = worker_data.get(number_field)
        issue_date = worker_data.get(issue_field)
        expiry_date = worker_data.get(expiry_field)
        
        if doc_number:  # Only create if document number exists
            try:
                document = Document.objects.create(
                    worker=worker,
                    document_type=doc_type,
                    document_number=doc_number,
                    issue_date=issue_date,
                    expiry_date=expiry_date,
                    issuing_authority=authority,
                    created_by=created_by
                )
                documents_created.append(document)
            except Exception as e:
                pass
    
    return documents_created

# Helper functions
def parse_date(date_value):
    """Parse date from Excel."""
    if pd.isna(date_value):
        return None
    if isinstance(date_value, datetime):
        return date_value.date()
    if isinstance(date_value, str):
        try:
            return pd.to_datetime(date_value).date()
        except:
            return None
    return None

def parse_date_range(date_range):
    """Parse date range like '14/11/2018-14/11/2028'."""
    if not date_range or pd.isna(date_range):
        return None, None
    
    date_str = str(date_range).strip()
    if '-' not in date_str:
        return None, None
    
    try:
        start_str, end_str = date_str.split('-', 1)
        start_date = datetime.strptime(start_str.strip(), '%d/%m/%Y').date()
        end_date = datetime.strptime(end_str.strip(), '%d/%m/%Y').date()
        return start_date, end_date
    except:
        return None, None

def format_document_number(doc_number):
    """Format document number properly."""
    if pd.isna(doc_number):
        return ''
    
    # Convert to string and handle scientific notation
    doc_str = str(doc_number).strip()
    
    # Handle scientific notation (e.g., 1.23456e+10)
    if 'e+' in doc_str.lower():
        try:
            # Convert to int to remove decimal places, then to string
            doc_str = str(int(float(doc_str)))
        except:
            pass
    
    return doc_str

def map_nationality(nationality_value):
    """Map nationality from Excel to system codes."""
    if pd.isna(nationality_value):
        return ''
    
    nationality_map = {
        'VIETNAMESE': 'VN',
        'CAMBODIAN': 'KH', 
        'INDONESIA': 'ID',
        'THAI': 'TH',
        'MYANMAR': 'MM',
        'PHILIPPINES': 'PH',
        'LAOS': 'LA',
        'CHINESE': 'CN',
    }
    
    nationality_str = str(nationality_value).strip().upper()
    return nationality_map.get(nationality_str, '')

# Main import function
def import_workers_from_excel(file_path, created_by):
    """Main import function - simplified and clean."""
    from zone.models import Worker
    
    # Read data
    records = read_excel_data(file_path)
    
    results = {
        'success_count': 0,
        'error_count': 0,
        'warnings': [],
        'errors': []
    }
    
    for i, record in enumerate(records):
        row_num = i + 2  # Excel row number (1 is header)
        
        try:
            # Extract data
            worker_data = extract_worker_data(record)
            
            # Create worker
            worker = Worker.objects.create(
                first_name=worker_data['first_name'],
                last_name=worker_data['last_name'],
                sex=worker_data['sex'],
                dob=worker_data['dob'],
                nationality=worker_data['nationality'],
                # ... other fields
                created_by=created_by
            )
            
            # Create documents
            create_worker_documents(worker, worker_data, created_by)

            results['success_count'] += 1

        except Exception as e:
            results['error_count'] += 1
            error_msg = f"Row {row_num}: Failed to import - {str(e)}"
            results['errors'].append(error_msg)
    
    return results