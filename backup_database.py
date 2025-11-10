"""
Backup current database state before resetting migrations

IMPORTANT: Run this BEFORE deleting any migrations!
"""
import os
import sys
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

def backup_database():
    """Create a PostgreSQL dump of the current database"""

    # Get database settings
    from django.conf import settings
    db_settings = settings.DATABASES['default']

    db_name = db_settings['NAME']
    db_user = db_settings['USER']
    db_host = db_settings.get('HOST', 'localhost')
    db_port = db_settings.get('PORT', '5432')

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_{db_name}_{timestamp}.sql'

    print("=" * 60)
    print("DATABASE BACKUP")
    print("=" * 60)
    print(f"\nDatabase: {db_name}")
    print(f"Backup file: {backup_file}")
    print("\nCreating backup...")

    # Build pg_dump command
    # Note: You may need to set PGPASSWORD environment variable or use .pgpass file
    cmd = f'pg_dump -h {db_host} -p {db_port} -U {db_user} -F c -b -v -f {backup_file} {db_name}'

    print(f"\nCommand: {cmd}")
    print("\nNOTE: If you get a password prompt, set PGPASSWORD environment variable:")
    print(f"      set PGPASSWORD=your_password (Windows)")
    print(f"      export PGPASSWORD=your_password (Linux/Mac)")
    print("\nOr use .pgpass file for automatic authentication")

    result = os.system(cmd)

    if result == 0:
        print(f"\n[SUCCESS] Backup created: {backup_file}")
        print(f"\nTo restore this backup later:")
        print(f"  pg_restore -h {db_host} -p {db_port} -U {db_user} -d {db_name} -c {backup_file}")
        return True
    else:
        print(f"\n[ERROR] Backup failed with exit code: {result}")
        return False

def backup_migration_history():
    """Backup migration history from django_migrations table"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'migration_history_{timestamp}.sql'

    print("\n" + "=" * 60)
    print("MIGRATION HISTORY BACKUP")
    print("=" * 60)

    with connection.cursor() as cursor:
        # Get all schemas
        cursor.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            ORDER BY schema_name;
        """)
        schemas = [row[0] for row in cursor.fetchall()]

        print(f"\nFound {len(schemas)} schemas")

        with open(backup_file, 'w') as f:
            f.write("-- Django Migration History Backup\n")
            f.write(f"-- Created: {datetime.now()}\n\n")

            for schema in schemas:
                print(f"  Backing up migrations for schema: {schema}")

                cursor.execute(f"SET search_path TO {schema};")

                # Check if django_migrations table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_schema = %s
                        AND table_name = 'django_migrations'
                    );
                """, [schema])

                if cursor.fetchone()[0]:
                    cursor.execute("SELECT app, name, applied FROM django_migrations ORDER BY id;")
                    migrations = cursor.fetchall()

                    if migrations:
                        f.write(f"\n-- Schema: {schema}\n")
                        f.write(f"-- Migrations count: {len(migrations)}\n")
                        for app, name, applied in migrations:
                            f.write(f"-- {app}.{name} (applied: {applied})\n")

    print(f"\n[SUCCESS] Migration history saved to: {backup_file}")
    return True

if __name__ == '__main__':
    print("\nWARNING: Make sure you have PostgreSQL client tools (pg_dump) installed!")
    print("         On Windows: Install from https://www.postgresql.org/download/windows/")
    print("         The tools are usually in: C:\\Program Files\\PostgreSQL\\{version}\\bin\\")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    input()

    # Backup migration history (always works)
    backup_migration_history()

    print("\n" + "=" * 60)
    print("\nAttempting full database backup...")
    print("(This may fail if pg_dump is not in PATH)")
    backup_database()

    print("\n" + "=" * 60)
    print("BACKUP COMPLETE")
    print("=" * 60)
