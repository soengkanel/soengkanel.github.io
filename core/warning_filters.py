"""
Warning filters to suppress known non-critical warnings.
"""

import warnings
from django.db.models.fields import DateTimeField


def setup_warning_filters():
    """
    Configure warning filters to suppress known non-critical warnings.
    Call this from settings or apps.py
    """
    
    # Suppress naive datetime warnings for DateTimeFields
    # These can occur when legacy data contains naive datetimes
    # or when dates are compared with datetimes in queries
    warnings.filterwarnings(
        'ignore',
        message=r'DateTimeField .* received a naive datetime',
        category=RuntimeWarning,
        module='django.db.models.fields'
    )
    
    # Alternative: More specific filter for the exact warning
    warnings.filterwarnings(
        'ignore',
        message=r'DateTimeField (CardPrintingHistory\.created_at|Employee\.created_at|Worker\.created_at) received a naive datetime \(2025-08-03 00:00:00\)',
        category=RuntimeWarning
    )