"""
Simple test form for debugging file upload
"""
from django import forms

class SimpleExcelImportForm(forms.Form):
    """Minimal form for testing file upload"""
    
    excel_file = forms.FileField(
        label='Excel File',
        help_text='Select an Excel file to upload'
    )
    
    update_existing = forms.BooleanField(
        label='Update Existing',
        required=False,
        initial=False
    )
    
    skip_duplicates = forms.BooleanField(
        label='Skip Duplicates', 
        required=False,
        initial=True
    )