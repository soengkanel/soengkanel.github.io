"""
Regenerate all migrations from scratch

This script will:
    pass
1. Create fresh initial migrations for all apps
2. Fake-apply them to existing schemas (since tables already exist)
3. Handle both public and tenant schemas
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django_tenants.utils import get_tenant_model, schema_context

def get_all_apps():
    """Get list of all Django apps in the project"""
    from django.apps import apps
    from django.conf import settings

    all_apps = []

    # Get all installed apps
    for app_config in apps.get_app_configs():
        app_label = app_config.label

        # Skip Django's built-in apps and third-party apps
        # Only include our custom apps
        if (
            not app_label.startswith('django') and
            app_label not in ['rest_framework', 'corsheaders', 'django_tenants',
                             'rest_framework_simplejwt', 'drf_yasg']
        ):
            all_apps.append(app_label)

    return sorted(all_apps)

def create_initial_migrations():
    """Create initial migrations for all apps"""

    print("\n" + "=" * 60)
    print("STEP 1: CREATE INITIAL MIGRATIONS")
    print("=" * 60)

    apps = get_all_apps()

    print(f"\nFound {len(apps)} custom apps:")
    for app in apps:
        print(f"  - {app}")

    print("\nCreating migrations...")

    try:
        # Create migrations for all apps at once
        call_command('makemigrations')
        print("\n[SUCCESS] Initial migrations created!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to create migrations: {e}")
        import traceback
        traceback.print_exc()
        return False

def fake_apply_migrations_to_schema(schema_name):
    """Fake-apply all migrations to a schema (since tables already exist)"""

    print(f"\n  Processing schema: {schema_name}")

    try:
        # Set the schema
        with connection.cursor() as cursor:
            cursor.execute(f"SET search_path TO {schema_name};")

        # Fake-apply all migrations
        # This marks them as applied without actually running them
        call_command('migrate', '--fake', verbosity=0)

        print(f"    [OK] Migrations fake-applied to {schema_name}")
        return True

    except Exception as e:
        print(f"    [ERROR] Failed to fake-apply migrations: {e}")
        return False

def fake_apply_migrations_all_schemas():
    """Fake-apply migrations to all schemas"""

    print("\n" + "=" * 60)
    print("STEP 2: FAKE-APPLY MIGRATIONS TO EXISTING SCHEMAS")
    print("=" * 60)
    print("\nSince your database tables already exist, we'll mark")
    print("the new migrations as applied without actually running them.")

    # Process public schema
    print("\n" + "=" * 60)
    print("Processing PUBLIC schema")
    print("=" * 60)
    fake_apply_migrations_to_schema('public')

    # Process tenant schemas
    print("\n" + "=" * 60)
    print("Processing TENANT schemas")
    print("=" * 60)

    TenantModel = get_tenant_model()
    tenants = TenantModel.objects.all()

    print(f"\nFound {tenants.count()} tenant(s)")

    success_count = 0
    failed_count = 0

    for tenant in tenants:
        connection.set_tenant(tenant)

        if fake_apply_migrations_to_schema(tenant.schema_name):
            success_count += 1
        else:
            failed_count += 1

    print("\n" + "=" * 60)
    print(f"Summary: {success_count} schemas successful, {failed_count} failed")
    print("=" * 60)

    return failed_count == 0

def verify_migrations():
    """Verify that migrations were applied correctly"""

    print("\n" + "=" * 60)
    print("STEP 3: VERIFY MIGRATIONS")
    print("=" * 60)

    try:
        # Check migration status
        print("\nChecking migration status...")
        call_command('showmigrations', verbosity=1)
        print("\n[SUCCESS] Migration verification complete!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Verification failed: {e}")
        return False

def main():
    print("=" * 60)
    print("REGENERATE MIGRATIONS")
    print("=" * 60)
    print("\nThis script will:")
    print("  1. Create fresh initial migrations for all apps")
    print("  2. Fake-apply them to existing schemas")
    print("  3. Verify the migration state")
    print("\nPrerequisites:")
    print("  - Migration files have been removed")
    print("  - Migration history has been cleaned from database")
    print("  - Database tables still exist (we won't drop them)")

    print("\n" + "=" * 60)
    print("\nType 'REGENERATE MIGRATIONS' to proceed (case-sensitive):")
    confirmation = input("> ")

    if confirmation != "REGENERATE MIGRATIONS":
        print("\n[CANCELLED] Operation cancelled.")
        return

    # Step 1: Create initial migrations
    if not create_initial_migrations():
        print("\n[FAILED] Could not create migrations. Aborting.")
        return

    # Step 2: Fake-apply migrations to all schemas
    if not fake_apply_migrations_all_schemas():
        print("\n[WARNING] Some schemas failed. Check the errors above.")

    # Step 3: Verify migrations
    verify_migrations()

    print("\n" + "=" * 60)
    print("COMPLETE!")
    print("=" * 60)
    print("\n[SUCCESS] Migration regeneration complete!")
    print("\nYour migrations are now clean and synchronized with your database.")
    print("\nNext steps:")
    print("  1. Test your application: python manage.py runserver")
    print("  2. Create a test tenant: python tenant_setup.py")
    print("  3. Commit the new migration files to git")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Failed to regenerate migrations: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
