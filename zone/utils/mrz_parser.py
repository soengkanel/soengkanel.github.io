from datetime import datetime

def parse_khid_mrz(mrz_line):
    """
    Parse Cambodian KHID MRZ (3 lines, 30 chars each).
    Example input:
        [
            "IDKHM1234567890<<<<<<<<<<<<<<<<<<<",
            "8001012M3001015KHM<<<<<<<<<<<<<<08",
            "DOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<"
        ]
    """
    mrz_lines = clean_mrz_lines(mrz_line)
    
    if len(mrz_lines) != 3:
        raise ValueError("MRZ must contain exactly 3 lines")

    line1, line2, line3 = mrz_lines

    # --- Line 1 ---
    # For Cambodian ID cards (KHID), always use KHM as issuing authority
    document_code = "IDKH"  # Cambodian ID card
    issuing_country = "KHM"  # Kingdom of Cambodia
    document_number = line1[5:14].replace("<", "").replace("O", "0")  # Fix OCR errors

    # --- Line 2 ---
    birth_date_raw = line2[0:6]
    birth_check_digit = line2[6]
    sex = line2[7]
    expiry_date_raw = line2[8:14]
    expiry_check_digit = line2[14]
    nationality = line2[15:18]
    final_check_digit = line2[29]

    # Convert dates
    def parse_date(yyMMdd):
        year = int(yyMMdd[0:2])
        month = int(yyMMdd[2:4])
        day = int(yyMMdd[4:6])
        # Assume year >= 50 => 1900s, else 2000s
        year += 1900 if year >= 50 else 2000
        return datetime(year, month, day).strftime('%Y-%m-%d')

    birth_date = parse_date(birth_date_raw)
    expiry_date = parse_date(expiry_date_raw)

    # --- Line 3 (names) ---
    name_parts = line3.split("<<", 1)
    surname = name_parts[0].replace("<", "")
    given_names = name_parts[1].replace("<", " ") if len(name_parts) > 1 else ""
    document_type_set = ""
    if document_code == "IDKH":
        document_type_set = "id_card"

    return{
        "document_type": document_type_set,
        "issuing_country": issuing_country,
        "document_number": document_number,
        "expiry_date": str(expiry_date),
    }
    # return {
    #     "document_type": document_code,
    #     "issuing_country": issuing_country,
    #     "document_number": document_number,
    #     "birth_date": str(birth_date),
    #     "sex": sex,
    #     "expiry_date": str(expiry_date),
    #     "nationality": nationality,
    #     "surname": surname.strip(),
    #     "given_names": given_names.strip(),
    #     "final_check_digit": final_check_digit,
    # }

def parse_passport_mrz(mrz_lines):
    """
    Parse TD3 passport MRZ (2 lines, ~44 characters each)
    Returns a dictionary with extracted info
    """

    if len(mrz_lines) != 2:
        raise ValueError("Passport MRZ must be 2 lines")

    line1, line2 = mrz_lines

    # Remove spaces
    line1 = line1.replace(" ", "")
    line2 = line2.replace(" ", "")

    # --- Line 1 ---
    document_type = line1[0]
    issuing_country = line1[2:5]

    # Name (surname << given names)
    name_raw = line1[5:]
    if '<<' in name_raw:
        surname, given_names = name_raw.split("<<", 1)
        given_names = given_names.replace("<", " ").strip()
    else:
        surname = name_raw.replace("<", "").strip()
        given_names = ""

    surname = surname.replace("<", "").strip()

    # --- Line 2 ---
    document_number = line2[0:9].replace("<", "")
    document_number_check = line2[9]
    nationality = line2[10:13]

    dob_raw = line2[13:19]
    dob_check = line2[19]
    sex = line2[20]
    expiry_raw = line2[21:27]
    expiry_check = line2[27]

    personal_number = line2[28:42].replace("<", "")
    final_check_digit = line2[42] if len(line2) > 42 else ""

    # Helper to parse date
    def parse_date(yyMMdd):
        year = int(yyMMdd[:2])
        month = int(yyMMdd[2:4])
        day = int(yyMMdd[4:6])
        year += 1900 if year >= 50 else 2000
        return datetime(year, month, day).strftime('%Y-%m-%d')

    birth_date = parse_date(dob_raw)
    expiry_date = parse_date(expiry_raw)
    document_type_set = ""
    if document_type == "P":
        document_type_set = "passport"

    return {
        "document_type": document_type_set,
        "document_number": document_number,
        "issuing_country": issuing_country,
        "expiry_date": str(expiry_date),
    }
    # return {
    #     "document_type": document_type,
    #     "issuing_country": issuing_country,
    #     "surname": surname,
    #     "given_names": given_names,
    #     "document_number": document_number,
    #     "document_number_check": document_number_check,
    #     "nationality": nationality,
    #     "birth_date": str(birth_date),
    #     "birth_check": str(dob_check),
    #     "sex": sex,
    #     "expiry_date": str(expiry_date),
    #     "expiry_check": str(expiry_check),
    #     "personal_number": personal_number,
    #     "final_check_digit": final_check_digit,
    # }

def is_khid_mrz(mrz_lines):
    """
    Check if MRZ belongs to Cambodian KHID (TD1 format).
    """
    if len(mrz_lines) != 3:
        return False

    # Each line must be 30 characters
    if not all(len(line) == 30 for line in mrz_lines):
        return False

    line1, line2, line3 = mrz_lines

    # Document code must be ID, issuing country must be KHM
    if not (line1.startswith("IDKHM")):
        return False

    # Line 2 basic date pattern (YYMMDD + digit)
    dob = line2[0:7]   # e.g., "8001012"
    exp = line2[7:15]  # e.g., "M3001015"

    if not (dob[:6].isdigit() and dob[6].isdigit()):
        return False
    if not (exp[1:7].isdigit() and exp[7].isdigit()):
        return False

    # Nationality must be KHM
    nationality = line2[15:18]
    if nationality != "KHM":
        return False

    return True

def detect_mrz_type(mrz_line):
    """
    Detect MRZ type: KHID, PASSPORT, or UNKNOWN
    """

    mrz_lines = clean_mrz_lines(mrz_line)

    print("mrz_lines :", mrz_lines)
    print("mrz_line_not_clean :", mrz_line)
    print("len mrz_lines =:",len(mrz_lines))
    # --- KHID (Cambodian ID, TD1) ---
    if len(mrz_lines) == 3 and all(28 <= len(line) <= 35 for line in mrz_lines):
        line1 = mrz_lines[0].upper()
        line2 = mrz_lines[1].upper()
        print("line1==:", line1)
        print("line2==:", line2)
        
        # Check for various Cambodian ID card indicators:
        # 1. IDKHM/LDKHM at start of line 1
        # 2. KHM anywhere in the MRZ (issuing country or nationality)
        # 3. Line structure typical of Cambodian ID cards
        line3 = mrz_lines[2].upper() if len(mrz_lines) > 2 else ""
        
        khm_indicators = (
            line1.startswith("IDKHM") or 
            line1.startswith("LDKHM") or
            "KHM" in line1 or 
            "KHM" in line2 or 
            "KHM" in line3 or
            # Additional patterns for Cambodian IDs
            (len(mrz_lines) == 3 and any("KH" in line.upper() for line in mrz_lines))
        )
        
        if khm_indicators:
            print("KHID (Cambodian ID Card detected)")
            print(f"  Detection criteria met for lines: {mrz_lines}")
            return "KHID"

    # --- Passport (TD3) ---
    if len(mrz_lines) == 2 and all(len(line) == 44 or 43 for line in mrz_lines):
       
        line1 = mrz_lines[0].upper()
        if line1.startswith("P"):
            print("PASSPORT TYPE")
            return "PASSPORT"

    return "UNKNOWN"


def clean_mrz_text(raw_text):
    """
    Remove all spaces and normalize MRZ text into lines.
    MRZ may come as a single string with newlines or spaces.
    """
    # Remove all spaces
    text_no_spaces = raw_text.replace(" ", "")
    # Split into lines by newline characters
    lines = [line.strip() for line in text_no_spaces.splitlines() if line.strip()]
    return lines

def clean_mrz_lines(mrz_lines):
    """
    Remove all spaces from each MRZ line.
    Input: list of strings (MRZ lines)
    Output: list of strings with spaces removed
    """
    return [line.replace(" ", "") for line in mrz_lines]


def detect_document_type(mrz_lines):
    if len(mrz_lines) == 2 and all(len(line) >= 40 for line in mrz_lines):
        return 'passport'
    elif len(mrz_lines) == 3 and all(len(line) >= 30 for line in mrz_lines):
        return 'khid'
    else:
        return 'unknown'

def parse_mrz_lines(mrz_lines):
    print("generate_passport_td_mrz_lines==:", mrz_lines)
    parsed_data = {}
    doc_type = detect_mrz_type(mrz_lines)
    
    print("doc_type==: ", doc_type)
    
    if doc_type == 'PASSPORT':

        line1, line2 = mrz_lines

        dob =  parse_mrz_date(line2[12:18])

        # names = line1[5:].replace('<', ' ').strip()
        # surname, *given_names = names.split()
        # parsed_data['surname'] = surname
        # parsed_data['given_names'] = ' '.join(given_names)
        # parsed_data['nationality'] = line2[10:12]
        # parsed_data['date_of_birth'] = dob
        # parsed_data['sex'] = line2[20]
        # parsed_data['personal_number'] = line2[28:42].replace('<', '')
            # Helper to parse date
        def parse_date(yyMMdd):
            year = int(yyMMdd[:2])
            month = int(yyMMdd[2:4])
            day = int(yyMMdd[4:6])
            if month < 1 or month > 12:
                month=12
            if day < 1 or day > 31:
                day=30

            year += 1900 if year >= 50 else 2000
            return datetime(year, month, day).strftime('%Y-%m-%d')
        
        expiry_raw = line2[21:27]
        print("expiry_raw=:", expiry_raw)
        expiry_date = parse_date(expiry_raw)

        # Extract nationality from line2 (positions 10-13 for 3-character codes)
        raw_nationality = line2[10:13]
        
        # Apply OCR corrections for common nationality misreadings
        nationality_corrections = {
            '10N': 'IDN',  # Indonesia - I often misread as 1
            'I0N': 'IDN',  # Indonesia - D often misread as 0
            'IPN': 'IDN',  # Indonesia - D often misread as P
            'CID': 'IDN',  # Indonesia - sometimes issuing country gets mixed with nationality
            'VWN': 'VNM',  # Vietnam
            'VN1': 'VNM',  # Vietnam
            'THN': 'THA',  # Thailand
            'KHN': 'KHM',  # Cambodia
        }
        
        nationality = nationality_corrections.get(raw_nationality, raw_nationality)
        if nationality != raw_nationality:
            print(f"OCR nationality correction: '{raw_nationality}' -> '{nationality}'")
        
        parsed_data['document_type'] = "passport"
        parsed_data['issuing_country'] = line1[2:5]
        parsed_data['document_number'] = line2[0:9].replace('<', '')
        parsed_data['nationality'] = nationality
        parsed_data['expiry_date'] = expiry_date

    
    elif doc_type == 'KHID':
       
        # mrz_data = parse_khid_mrz(mrz_lines)
        # parsed_data['document_type'] = mrz_data["document_type"]
        # parsed_data['issuing_country'] = mrz_data["issuing_country"]
        # parsed_data['document_number'] =  mrz_data["document_number"]
        # parsed_data['expiry_date'] =  mrz_data["expiry_date"]
        
        # Handle Khmer National ID custom MRZ parsing (example logic)
        
        mrz_line = clean_mrz_lines(mrz_lines)
    
        if len(mrz_line) != 3:
            raise ValueError("MRZ must contain exactly 3 lines")

        line1, line2, line3 = mrz_line
        
        # Handle both IDKHM and LDKHM (OCR misreading)
        # For Cambodian ID cards, always set:
        # - issuing_country/authority: KHM (Kingdom of Cambodia)
        # - nationality: KH (Cambodian)
        
        if line1.startswith("LDKHM") or line1.startswith("IDKHM"):
            # This is a Cambodian ID card
            issuing_country = "KHM"  # Always KHM for Cambodian ID cards
            nationality = "KH"  # Always Cambodian nationality for KHID
            document_number = line1[5:14].replace("<", "").replace("O", "0")  # O often misread for 0
        else:
            # Fallback for other formats
            issuing_country = "KHM"  # Default to KHM for ID cards
            nationality = "KH"  # Default to Cambodian
            document_number = line1[5:14].replace("<", "")
        
        # Parse dates from line 2
        birth_date_raw = line2[0:6]
        sex = line2[7] if len(line2) > 7 else ""
        expiry_date_raw = line2[8:14]
        # Note: We ignore the nationality field in line2[15:18] since it's always KH for KHID
        
        # Parse dates
        birth_date = parse_mrz_date(birth_date_raw) if birth_date_raw else None
        expiry_date = parse_mrz_date(expiry_date_raw, is_expiry=True) if expiry_date_raw else None
        
        # Parse names from line 3
        if "<<" in line3:
            name_parts = line3.split("<<", 1)
            surname = name_parts[0].replace("<", " ").strip()
            given_names = name_parts[1].replace("<", " ").strip() if len(name_parts) > 1 else ""
        else:
            surname = line3.replace("<", " ").strip()
            given_names = ""
        
        parsed_data['document_type'] = "id_card"
        parsed_data['issuing_country'] = issuing_country  # KHM for Cambodian ID cards
        parsed_data['document_number'] = document_number
        parsed_data['expiry_date'] = expiry_date
        parsed_data['date_of_birth'] = birth_date
        parsed_data['nationality'] = nationality  # Always KH for Cambodian ID cards
        parsed_data['sex'] = sex
        parsed_data['surname'] = surname
        parsed_data['given_names'] = given_names


        # You can customize this further if you know the format

    else:
        parsed_data['Error'] = "Unrecognized MRZ format"

    return parsed_data


def parse_mrz_date(raw_date, is_expiry=False):
    """
    Parses MRZ date (YYMMDD) into YYYY-MM-DD format.
    Handles invalid days/months gracefully.
    """
    try:
        yy = int(raw_date[0:2])
        mm = int(raw_date[2:4])
        dd = int(raw_date[4:6])

        if mm < 1 or mm > 12:
            mm=12
        if dd < 1 or dd > 31:
           dd=30

        now_year = datetime.now().year % 100

        if is_expiry:
            year = 2000 + yy
        else:
            year = 1900 + yy if yy > now_year else 2000 + yy

        # Try building the date
        date_obj = datetime(year, mm, dd)
        return date_obj.strftime("%Y-%m-%d")

    except Exception as e:
        return f"Invalid ({e})"
    


# def parse_mrz_date(raw_date, is_expiry=False):

#     try:
#         yy = int(raw_date[0:2])
#         mm = int(raw_date[2:4])
#         dd = int(raw_date[4:6])
#         now_year = datetime.now().year % 100  # last 2 digits of current year

#         if is_expiry:
#             # Force expiry years to be 2000–2099
#             full_year = 2000 + yy
#         else:
#             # DOB: if YY > current YY, it's likely 1900s, else 2000s
#             full_year = 1900 + yy if yy > now_year else 2000 + yy

#         return datetime(full_year, mm, dd).strftime("%Y-%m-%d")
#     except Exception:
#         return "Invalid"

