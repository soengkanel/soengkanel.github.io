"""
Quick backup script without interactive prompts
"""
import os
import sys
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from django.conf import settings

def backup_database():
    """Create a PostgreSQL dump of the current database"""

    # Get database settings
    db_settings = settings.DATABASES['default']

    db_name = db_settings['NAME']
    db_user = db_settings['USER']
    db_password = db_settings['PASSWORD']
    db_host = db_settings.get('HOST', 'localhost')
    db_port = db_settings.get('PORT', '5432')

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_{db_name}_{timestamp}.sql'

    print("=" * 60)
    print("DATABASE BACKUP")
    print("=" * 60)
    print(f"\nDatabase: {db_name}")
    print(f"Host: {db_host}:{db_port}")
    print(f"User: {db_user}")
    print(f"Backup file: {backup_file}")
    print("\nCreating backup...")

    # Set password environment variable
    os.environ['PGPASSWORD'] = db_password

    # Build pg_dump command (custom format for better compression and restore options)
    cmd = f'pg_dump -h {db_host} -p {db_port} -U {db_user} -F c -b -v -f "{backup_file}" {db_name}'

    result = os.system(cmd)

    # Clear password from environment
    del os.environ['PGPASSWORD']

    if result == 0:
        # Get file size
        file_size = os.path.getsize(backup_file)
        size_mb = file_size / (1024 * 1024)

        print(f"\n[SUCCESS] Backup created: {backup_file}")
        print(f"Size: {size_mb:.2f} MB")
        print(f"\nTo restore this backup later, use:")
        print(f"  pg_restore -h {db_host} -p {db_port} -U {db_user} -d {db_name} -c \"{backup_file}\"")
        print(f"\nOr to restore to a different database:")
        print(f"  createdb -h {db_host} -p {db_port} -U {db_user} new_db_name")
        print(f"  pg_restore -h {db_host} -p {db_port} -U {db_user} -d new_db_name \"{backup_file}\"")
        return True, backup_file
    else:
        print(f"\n[ERROR] Backup failed with exit code: {result}")
        return False, None

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

        with open(backup_file, 'w', encoding='utf-8') as f:
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
    return True, backup_file

if __name__ == '__main__':
    print("\nStarting database backup process...\n")

    # Backup migration history first
    success1, migration_file = backup_migration_history()

    # Then backup full database
    print("\n" + "=" * 60)
    print("FULL DATABASE BACKUP")
    success2, backup_file = backup_database()

    print("\n" + "=" * 60)
    print("BACKUP SUMMARY")
    print("=" * 60)
    if success1:
        print(f"✓ Migration history: {migration_file}")
    if success2:
        print(f"✓ Database backup: {backup_file}")

    if success1 and success2:
        print("\n[SUCCESS] All backups completed successfully!")
    else:
        print("\n[WARNING] Some backups may have failed. Check the output above.")

    print("=" * 60)
