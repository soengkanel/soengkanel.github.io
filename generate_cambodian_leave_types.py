"""
Script to generate Cambodian Labor Law leave types in tenant
Usage: python generate_cambodian_leave_types.py
"""
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from leave.models import LeaveType

# Set the tenant schema
TENANT_SCHEMA = 'kk_company'  # Change this to your tenant schema name

print("=" * 70)
print("Cambodian Labor Law - Leave Types Generator")
print("=" * 70)
print(f"\nSetting schema to: {TENANT_SCHEMA}")
connection.set_schema(TENANT_SCHEMA)

# Define leave types based on Cambodian Labor Law
leave_types_data = [
    {
        'name': 'Annual Leave',
        'code': 'ANNUAL',
        'max_days_per_year': 18,
        'carry_forward_allowed': True,
        'max_carry_forward_days': 6,
        'encashment_allowed': False,
        'is_paid': True,
        'include_holiday': False,
        'color': '#3b82f6',
        'apply_in_advance_days': 3,
        'maximum_continuous_days': 365,
    },
    {
        'name': 'Sick Leave',
        'code': 'SICK',
        'max_days_per_year': 365,
        'carry_forward_allowed': False,
        'is_paid': True,
        'include_holiday': False,
        'color': '#ef4444',
        'medical_certificate_required': True,
        'medical_certificate_min_days': 3,
    },
    {
        'name': 'Maternity Leave',
        'code': 'MATERNITY',
        'max_days_per_year': 90,
        'carry_forward_allowed': False,
        'is_paid': True,
        'include_holiday': True,
        'color': '#ec4899',
        'apply_in_advance_days': 30,
    },
    {
        'name': 'Paternity Leave',
        'code': 'PATERNITY',
        'max_days_per_year': 2,
        'carry_forward_allowed': False,
        'is_paid': True,
        'include_holiday': False,
        'color': '#10b981',
        'apply_in_advance_days': 7,
    },
    {
        'name': 'Marriage Leave',
        'code': 'MARRIAGE',
        'max_days_per_year': 3,
        'carry_forward_allowed': False,
        'is_paid': True,
        'include_holiday': False,
        'color': '#f59e0b',
        'apply_in_advance_days': 7,
    },
    {
        'name': 'Bereavement Leave',
        'code': 'BEREAVE',
        'max_days_per_year': 7,
        'carry_forward_allowed': False,
        'is_paid': True,
        'include_holiday': False,
        'color': '#6b7280',
    },
    {
        'name': 'Special Circumstances Leave',
        'code': 'SPECIAL',
        'max_days_per_year': 7,
        'carry_forward_allowed': False,
        'is_paid': True,
        'include_holiday': False,
        'color': '#8b5cf6',
        'apply_in_advance_days': 1,
    },
    {
        'name': 'Unpaid Leave',
        'code': 'UNPAID',
        'max_days_per_year': 365,
        'carry_forward_allowed': False,
        'is_paid': False,
        'include_holiday': False,
        'color': '#94a3b8',
        'apply_in_advance_days': 7,
    },
    {
        'name': 'Compensatory Leave',
        'code': 'COMP',
        'max_days_per_year': 52,
        'carry_forward_allowed': True,
        'max_carry_forward_days': 10,
        'is_paid': True,
        'include_holiday': False,
        'color': '#06b6d4',
    },
    {
        'name': 'Study Leave',
        'code': 'STUDY',
        'max_days_per_year': 30,
        'carry_forward_allowed': False,
        'is_paid': False,
        'include_holiday': False,
        'color': '#f97316',
        'apply_in_advance_days': 14,
    },
]

created = 0
updated = 0

for data in leave_types_data:
    code = data.pop('code')
    name = data.pop('name')

    try:
        leave_type, created_flag = LeaveType.objects.update_or_create(
            code=code,
            defaults={'name': name, **data}
        )

        if created_flag:
            print(f"[CREATED] {name} ({code})")
            created += 1
        else:
            print(f"[UPDATED] {name} ({code})")
            updated += 1
    except Exception as e:
        print(f"[ERROR] {name} ({code}): {e}")

print("\n" + "=" * 70)
print(f"Summary: {created} created, {updated} updated")
print("=" * 70)
