"""
Standalone script to generate Cambodian Labor Law compliant leave types

This script works with multi-tenant systems by:
    pass
1. Setting PUBLIC_SCHEMA_NAME to run in public schema (if no tenants)
2. Or running for all tenants if they exist

Usage:
    python generate_cambodian_leaves.py
    python generate_cambodian_leaves.py --force
    python generate_cambodian_leaves.py --tenant=kk
"""

import os
import sys
import django

# Setup Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from leave.models import LeaveType


def get_leave_types_data():
    """Return the leave types configuration"""
    return [
        {
            'name': 'Annual Leave',
            'code': 'ANNUAL',
            'max_days_per_year': 18,
            'carry_forward_allowed': True,
            'max_carry_forward_days': 6,
            'encashment_allowed': True,
            'include_holiday': False,
            'is_paid': True,
            'apply_in_advance_days': 3,
            'maximum_continuous_days': 18,
            'minimum_continuous_days': 1,
            'medical_certificate_required': False,
            'medical_certificate_min_days': 0,
            'color': '#28a745',
            'is_active': True,
            'description': 'Annual paid leave: 18 working days per year after 1 year of service (Cambodia Labor Law Article 166)'
        },
        {
            'name': 'Sick Leave',
            'code': 'SICK',
            'max_days_per_year': 365,
            'carry_forward_allowed': False,
            'max_carry_forward_days': 0,
            'encashment_allowed': False,
            'include_holiday': True,
            'is_paid': True,
            'apply_in_advance_days': 0,
            'maximum_continuous_days': 365,
            'minimum_continuous_days': 1,
            'medical_certificate_required': True,
            'medical_certificate_min_days': 3,
            'color': '#dc3545',
            'is_active': True,
            'description': 'Sick leave with medical certificate. First 6 months at full pay, next 6 months at 60% (Article 168)'
        },
        {
            'name': 'Maternity Leave',
            'code': 'MATERNITY',
            'max_days_per_year': 90,
            'carry_forward_allowed': False,
            'max_carry_forward_days': 0,
            'encashment_allowed': False,
            'include_holiday': True,
            'is_paid': True,
            'apply_in_advance_days': 7,
            'maximum_continuous_days': 90,
            'minimum_continuous_days': 90,
            'medical_certificate_required': True,
            'medical_certificate_min_days': 1,
            'color': '#e83e8c',
            'is_active': True,
            'description': 'Maternity leave: 90 days paid leave (50% by employer, 50% by NSSF) - Article 182'
        },
        {
            'name': 'Paternity Leave',
            'code': 'PATERNITY',
            'max_days_per_year': 2,
            'carry_forward_allowed': False,
            'max_carry_forward_days': 0,
            'encashment_allowed': False,
            'include_holiday': False,
            'is_paid': True,
            'apply_in_advance_days': 3,
            'maximum_continuous_days': 2,
            'minimum_continuous_days': 1,
            'medical_certificate_required': False,
            'medical_certificate_min_days': 0,
            'color': '#17a2b8',
            'is_active': True,
            'description': 'Paternity leave: 2 days paid leave for birth of child'
        },
        {
            'name': 'Marriage Leave',
            'code': 'MARRIAGE',
            'max_days_per_year': 3,
            'carry_forward_allowed': False,
            'max_carry_forward_days': 0,
            'encashment_allowed': False,
            'include_holiday': False,
            'is_paid': True,
            'apply_in_advance_days': 7,
            'maximum_continuous_days': 3,
            'minimum_continuous_days': 1,
            'medical_certificate_required': False,
            'medical_certificate_min_days': 0,
            'color': '#fd7e14',
            'is_active': True,
            'description': 'Special leave for employee marriage: 3 days paid leave'
        },
        {
            'name': 'Bereavement Leave',
            'code': 'BEREAVE',
            'max_days_per_year': 7,
            'carry_forward_allowed': False,
            'max_carry_forward_days': 0,
            'encashment_allowed': False,
            'include_holiday': False,
            'is_paid': True,
            'apply_in_advance_days': 0,
            'maximum_continuous_days': 7,
            'minimum_continuous_days': 1,
            'medical_certificate_required': False,
            'medical_certificate_min_days': 0,
            'color': '#6c757d',
            'is_active': True,
            'description': 'Bereavement leave for death of immediate family member: up to 7 days'
        },
        {
            'name': 'Special Circumstances Leave',
            'code': 'SPECIAL',
            'max_days_per_year': 7,
            'carry_forward_allowed': False,
            'max_carry_forward_days': 0,
            'encashment_allowed': False,
            'include_holiday': False,
            'is_paid': True,
            'apply_in_advance_days': 1,
            'maximum_continuous_days': 7,
            'minimum_continuous_days': 1,
            'medical_certificate_required': False,
            'medical_certificate_min_days': 0,
            'color': '#6610f2',
            'is_active': True,
            'description': 'Special circumstances leave (religious ceremonies, family events, etc.)'
        },
        {
            'name': 'Unpaid Leave',
            'code': 'UNPAID',
            'max_days_per_year': 365,
            'carry_forward_allowed': False,
            'max_carry_forward_days': 0,
            'encashment_allowed': False,
            'include_holiday': True,
            'is_paid': False,
            'apply_in_advance_days': 7,
            'maximum_continuous_days': 365,
            'minimum_continuous_days': 1,
            'medical_certificate_required': False,
            'medical_certificate_min_days': 0,
            'color': '#adb5bd',
            'is_active': True,
            'description': 'Unpaid leave by mutual agreement between employer and employee'
        },
        {
            'name': 'Compensatory Leave',
            'code': 'COMP',
            'max_days_per_year': 52,
            'carry_forward_allowed': False,
            'max_carry_forward_days': 0,
            'encashment_allowed': False,
            'include_holiday': False,
            'is_paid': True,
            'apply_in_advance_days': 1,
            'maximum_continuous_days': 5,
            'minimum_continuous_days': 0.5,
            'medical_certificate_required': False,
            'medical_certificate_min_days': 0,
            'color': '#20c997',
            'is_active': True,
            'description': 'Compensatory time off for overtime work or work on rest days/holidays'
        },
        {
            'name': 'Study Leave',
            'code': 'STUDY',
            'max_days_per_year': 30,
            'carry_forward_allowed': False,
            'max_carry_forward_days': 0,
            'encashment_allowed': False,
            'include_holiday': False,
            'is_paid': False,
            'apply_in_advance_days': 14,
            'maximum_continuous_days': 30,
            'minimum_continuous_days': 1,
            'medical_certificate_required': False,
            'medical_certificate_min_days': 0,
            'color': '#ffc107',
            'is_active': True,
            'description': 'Leave for educational purposes or professional development'
        },
    ]


def generate_for_tenant(tenant_schema, force_update=False):
    """Generate leave types for a specific tenant schema"""
    created = 0
    updated = 0
    skipped = 0
    errors = []

    try:
        # Switch to tenant schema
        connection.set_schema(tenant_schema)

        leave_types_data = get_leave_types_data()

        for leave_data in leave_types_data:
            code = leave_data['code']
            name = leave_data['name']
            description = leave_data.pop('description', '')

            try:
                existing = LeaveType.objects.filter(code=code).first()

                if existing:
                    if force_update:
                        for key, value in leave_data.items():
                            setattr(existing, key, value)
                        existing.save()
                        print(f"  [OK] Updated: {name} ({code})")
                        updated += 1
                    else:
                        print(f"  [SKIP] {name} ({code}) - already exists")
                        skipped += 1
                else:
                    LeaveType.objects.create(**leave_data)
                    print(f"  [OK] Created: {name} ({code})")
                    if description:
                        print(f"       {description}")
                    created += 1

            except Exception as e:
                error_msg = f"{name} ({code}): {str(e)}"
                print(f"  [ERROR] {error_msg}")
                errors.append(error_msg)

    except Exception as e:
        print(f"  [ERROR] Failed for schema {tenant_schema}: {str(e)}")
        errors.append(f"Schema {tenant_schema}: {str(e)}")

    return {'created': created, 'updated': updated, 'skipped': skipped, 'errors': errors}


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate Cambodian Labor Law compliant leave types'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force update existing leave types'
    )
    parser.add_argument(
        '--tenant',
        type=str,
        help='Specific tenant schema name (e.g., kk, osm). If not specified, runs for all tenants.'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Cambodian Labor Law - Leave Types Generator")
    print("=" * 70)
    print()

    try:
        from company.models import Company

        if args.tenant:
            # Run for specific tenant
            print(f"Running for tenant: {args.tenant}")
            print("-" * 70)
            result = generate_for_tenant(args.tenant, args.force)

            total_created = result['created']
            total_updated = result['updated']
            total_skipped = result['skipped']
            total_errors = result['errors']
        else:
            # Run for all tenants
            tenants = Company.objects.exclude(schema_name='public').all()

            if not tenants.exists():
                print("[WARNING] No tenants found in the system.")
                print("          Make sure you have created at least one company/tenant.")
                print()
                print("To create leave types, you have two options:")
                print("  1. Create a tenant first, then run this script")
                print("  2. Use Django shell and run: exec(open('generate_cambodian_leaves.py').read()); run()")
                sys.exit(1)

            print(f"Found {tenants.count()} tenant(s)")
            print()

            total_created = 0
            total_updated = 0
            total_skipped = 0
            total_errors = []

            for tenant in tenants:
                print(f"Processing tenant: {tenant.name} (schema: {tenant.schema_name})")
                print("-" * 70)

                result = generate_for_tenant(tenant.schema_name, args.force)

                total_created += result['created']
                total_updated += result['updated']
                total_skipped += result['skipped']
                total_errors.extend(result['errors'])

                print()

        # Print summary
        print()
        print("=" * 70)
        print("Summary")
        print("=" * 70)
        print(f"Created: {total_created}")
        print(f"Updated: {total_updated}")
        print(f"Skipped: {total_skipped}")

        if total_errors:
            print(f"Errors: {len(total_errors)}")
            for error in total_errors:
                print(f"  - {error}")

        print()

        if total_created > 0 or total_updated > 0:
            print("[SUCCESS] Leave types generated successfully!")
            print()
            print("Next steps:")
            print("  1. Review leave types at: http://localhost:8000/leave/types/")
            print("  2. Adjust max days or settings as needed for your organization")
            print("  3. Create leave allocations for employees")
        else:
            print("[INFO] No changes made.")
            if total_skipped > 0:
                print("       All leave types already exist.")
                print("       Run with --force to update existing types:")
                print("       python generate_cambodian_leaves.py --force")

        print()

        # Exit with appropriate code
        sys.exit(0 if not total_errors else 1)

    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
