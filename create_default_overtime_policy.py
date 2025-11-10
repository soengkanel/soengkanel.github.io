"""
Script to create a default overtime policy for the system
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import schema_context
from hr.models import OvertimePolicy

def create_default_overtime_policy():
    """Create a default overtime policy if none exists"""

    # Get the tenant schema name (e.g., kk_company)
    print("Available schemas:")
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('public', 'information_schema', 'pg_catalog', 'pg_toast')
            AND schema_name NOT LIKE 'pg_%'
        """)
        schemas = cursor.fetchall()
        for schema in schemas:
            print(f"  - {schema[0]}")

    # Use the first tenant schema (usually kk_company)
    tenant_schema = 'kk_company'

    print(f"\nCreating default overtime policy in schema: {tenant_schema}")

    with schema_context(tenant_schema):
        # Check if policy already exists
        existing_policies = OvertimePolicy.objects.all().count()
        if existing_policies > 0:
            print(f"Found {existing_policies} existing overtime policies. No need to create default.")
            return

        # Create default policy
        policy = OvertimePolicy.objects.create(
            name='Default Overtime Policy',
            description='Standard overtime policy for all employees',
            daily_threshold_hours=8.00,
            weekly_threshold_hours=40.00,
            rate_type='multiplier',
            standard_overtime_multiplier=1.50,
            extended_overtime_multiplier=2.00,
            extended_hours_threshold=10.00,
            weekend_multiplier=2.00,
            holiday_multiplier=3.00,
            fixed_hourly_rate=0.00,
            requires_pre_approval=True,
            approval_level='manager',
            max_daily_overtime=4.00,
            max_weekly_overtime=12.00,
            auto_calculate=True
        )

        print(f"[OK] Created default overtime policy: {policy.name}")
        print(f"  - Daily threshold: {policy.daily_threshold_hours} hours")
        print(f"  - Weekly threshold: {policy.weekly_threshold_hours} hours")
        print(f"  - Standard rate: {policy.standard_overtime_multiplier}x")
        print(f"  - Weekend rate: {policy.weekend_multiplier}x")
        print(f"  - Holiday rate: {policy.holiday_multiplier}x")

if __name__ == '__main__':
    create_default_overtime_policy()
