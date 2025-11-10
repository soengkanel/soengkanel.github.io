"""
Script to allocate leave to employees in a tenant
Usage: python allocate_employee_leave.py
"""
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from hr.models import Employee
from leave.models import LeaveType, LeaveAllocation
from company.models import Company

# Set the tenant schema
TENANT_SCHEMA = 'kk_company'  # Change this to your tenant schema name

print(f"Setting schema to: {TENANT_SCHEMA}")
connection.set_schema(TENANT_SCHEMA)

# Current year
year = timezone.now().year
print(f"Allocating leave for year: {year}")

# Get all active employees
employees = Employee.objects.filter(employment_status='active')
print(f"Found {employees.count()} active employees")

# Get all active leave types
leave_types = LeaveType.objects.filter(is_active=True)
print(f"Found {leave_types.count()} leave types")

if not leave_types.exists():
    print("ERROR: No leave types found. Please create leave types first.")
    exit(1)

# Default allocations
default_allocations = {
    'AL': 20,  # Annual Leave
    'SL': 15,  # Sick Leave
    'PL': 5,   # Personal Leave
    'ML': 90,  # Maternity Leave
    'PaL': 7,  # Paternity Leave
}

allocated_count = 0
from_date = timezone.datetime(year, 1, 1).date()
to_date = timezone.datetime(year, 12, 31).date()

for employee in employees:
    print(f'\nProcessing {employee.full_name}...')

    for leave_type in leave_types:
        # Check if allocation already exists
        existing = LeaveAllocation.objects.filter(
            employee=employee,
            leave_type=leave_type,
            year=year
        ).first()

        if existing:
            print(f'  - {leave_type.code}: Already allocated ({existing.allocated_days} days)')
            continue

        # Get default allocation for this leave type
        allocated_days = default_allocations.get(
            leave_type.code,
            leave_type.max_days_per_year
        )

        # Create allocation
        allocation = LeaveAllocation.objects.create(
            employee=employee,
            leave_type=leave_type,
            year=year,
            allocated_days=allocated_days,
            used_days=0,
            carried_forward=0,
            from_date=from_date,
            to_date=to_date,
        )

        print(f'  + {leave_type.code}: Allocated {allocated_days} days')
        allocated_count += 1

print(f'\n+ Successfully created {allocated_count} leave allocations for {employees.count()} employee(s)')
