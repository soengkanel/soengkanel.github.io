"""
Clean migration history from all schemas in the database

WARNING: This will delete all migration records from django_migrations table!
Run this AFTER removing migration files with remove_migrations.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django_tenants.utils import get_tenant_model

def clean_migration_history_for_schema(schema_name, cursor):
    """Clean migration history for a specific schema"""

    print(f"\n  Processing schema: {schema_name}")

    # Set search path
    cursor.execute(f"SET search_path TO {schema_name};")

    # Check if django_migrations table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = %s
            AND table_name = 'django_migrations'
        );
    """, [schema_name])

    if not cursor.fetchone()[0]:
        print(f"    [INFO] No django_migrations table found in {schema_name}")
        return 0

    # Count current migrations
    cursor.execute("SELECT COUNT(*) FROM django_migrations;")
    count_before = cursor.fetchone()[0]
    print(f"    Current migration records: {count_before}")

    if count_before == 0:
        print(f"    [INFO] No migrations to clean")
        return 0

    # Get list of migrations for logging
    cursor.execute("""
        SELECT app, COUNT(*) as count
        FROM django_migrations
        GROUP BY app
        ORDER BY app;
    """)
    app_counts = cursor.fetchall()

    print(f"    Migrations by app:")
    for app, count in app_counts:
        print(f"      - {app}: {count}")

    # Delete all migration records
    cursor.execute("DELETE FROM django_migrations;")
    deleted = cursor.rowcount

    print(f"    [OK] Deleted {deleted} migration records")

    return deleted

def main():
    print("=" * 60)
    print("CLEAN MIGRATION HISTORY")
    print("=" * 60)
    print("\nWARNING: This will delete ALL migration history records!")
    print("         from django_migrations table in all schemas.")
    print("\nThis should ONLY be run:")
    print("  1. After backing up your database")
    print("  2. After removing migration files")
    print("  3. Before regenerating new migrations")

    print("\n" + "=" * 60)
    print("\nType 'CLEAN MIGRATION HISTORY' to proceed (case-sensitive):")
    confirmation = input("> ")

    if confirmation != "CLEAN MIGRATION HISTORY":
        print("\n[CANCELLED] Operation cancelled.")
        return

    total_deleted = 0

    print("\n" + "=" * 60)
    print("CLEANING PUBLIC SCHEMA")
    print("=" * 60)

    # Clean public schema
    with connection.cursor() as cursor:
        deleted = clean_migration_history_for_schema('public', cursor)
        total_deleted += deleted

    print("\n" + "=" * 60)
    print("CLEANING TENANT SCHEMAS")
    print("=" * 60)

    # Clean all tenant schemas
    TenantModel = get_tenant_model()
    tenants = TenantModel.objects.all()

    print(f"\nFound {tenants.count()} tenant(s)")

    for tenant in tenants:
        connection.set_tenant(tenant)
        with connection.cursor() as cursor:
            deleted = clean_migration_history_for_schema(tenant.schema_name, cursor)
            total_deleted += deleted

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total migration records deleted: {total_deleted}")
    print("\n[SUCCESS] Migration history cleaned!")
    print("\nNext step:")
    print("  Run: python regenerate_migrations.py")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Failed to clean migration history: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
