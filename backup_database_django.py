"""
Database backup using Django's dumpdata and direct SQL dump
This doesn't require pg_dump to be installed
"""
import os
import sys
import django
from datetime import datetime
import subprocess
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.conf import settings

def backup_with_django_dumpdata():
    """Backup using Django's dumpdata command (JSON format)"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_django_data_{timestamp}.json'

    print("=" * 60)
    print("DJANGO DUMPDATA BACKUP")
    print("=" * 60)
    print(f"\nBackup file: {backup_file}")
    print("\nExporting all data to JSON...")

    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            call_command('dumpdata',
                        indent=2,
                        stdout=f,
                        exclude=['contenttypes', 'auth.permission'])

        # Get file size
        file_size = os.path.getsize(backup_file)
        size_mb = file_size / (1024 * 1024)

        print(f"\n[SUCCESS] Django backup created: {backup_file}")
        print(f"Size: {size_mb:.2f} MB")
        print(f"\nTo restore this backup:")
        print(f"  python manage.py loaddata {backup_file}")
        return True, backup_file
    except Exception as e:
        print(f"\n[ERROR] Django backup failed: {str(e)}")
        return False, None

def backup_schema_and_data_sql():
    """Create SQL backup using Python's subprocess and psql"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backup_full_db_{timestamp}.sql'

    db_settings = settings.DATABASES['default']
    db_name = db_settings['NAME']
    db_user = db_settings['USER']
    db_password = db_settings['PASSWORD']
    db_host = db_settings.get('HOST', 'localhost')
    db_port = db_settings.get('PORT', '5432')

    print("\n" + "=" * 60)
    print("SQL SCHEMA + DATA BACKUP")
    print("=" * 60)
    print(f"\nDatabase: {db_name}")
    print(f"Backup file: {backup_file}")
    print("\nExporting schema and data to SQL...")

    # Try to use pg_dump with full path search
    possible_paths = [
        'pg_dump',  # In PATH
        r'C:\Program Files\PostgreSQL\16\bin\pg_dump.exe',
        r'C:\Program Files\PostgreSQL\15\bin\pg_dump.exe',
        r'C:\Program Files\PostgreSQL\14\bin\pg_dump.exe',
        r'C:\Program Files\PostgreSQL\13\bin\pg_dump.exe',
        r'C:\Program Files (x86)\PostgreSQL\16\bin\pg_dump.exe',
        r'C:\Program Files (x86)\PostgreSQL\15\bin\pg_dump.exe',
    ]

    pg_dump_path = None
    for path in possible_paths:
        try:
            result = subprocess.run([path, '--version'],
                                  capture_output=True,
                                  text=True,
                                  timeout=5)
            if result.returncode == 0:
                pg_dump_path = path
                print(f"Found pg_dump: {path}")
                break
        except:
            continue

    if not pg_dump_path:
        print("\n[WARNING] pg_dump not found in common locations")
        print("Skipping SQL backup. Only Django JSON backup will be available.")
        return False, None

    try:
        # Set environment for password
        env = os.environ.copy()
        env['PGPASSWORD'] = db_password

        # Run pg_dump
        cmd = [
            pg_dump_path,
            '-h', db_host,
            '-p', str(db_port),
            '-U', db_user,
            '-F', 'c',  # Custom format
            '-b',       # Include blobs
            '-v',       # Verbose
            '-f', backup_file,
            db_name
        ]

        result = subprocess.run(cmd,
                              env=env,
                              capture_output=True,
                              text=True,
                              timeout=300)

        if result.returncode == 0:
            file_size = os.path.getsize(backup_file)
            size_mb = file_size / (1024 * 1024)

            print(f"\n[SUCCESS] SQL backup created: {backup_file}")
            print(f"Size: {size_mb:.2f} MB")
            print(f"\nTo restore this backup:")
            print(f"  pg_restore -h {db_host} -p {db_port} -U {db_user} -d {db_name} -c {backup_file}")
            return True, backup_file
        else:
            print(f"\n[ERROR] pg_dump failed: {result.stderr}")
            return False, None

    except Exception as e:
        print(f"\n[ERROR] SQL backup failed: {str(e)}")
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

def create_backup_info():
    """Create a backup information file"""

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    info_file = f'backup_info_{timestamp}.txt'

    db_settings = settings.DATABASES['default']

    with open(info_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("DATABASE BACKUP INFORMATION\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Backup Date: {datetime.now()}\n")
        f.write(f"Database Name: {db_settings['NAME']}\n")
        f.write(f"Database Host: {db_settings.get('HOST', 'localhost')}\n")
        f.write(f"Database Port: {db_settings.get('PORT', '5432')}\n")
        f.write(f"Database User: {db_settings['USER']}\n\n")
        f.write("Backup Files Created:\n")

    return info_file

if __name__ == '__main__':
    print("\nStarting database backup process...\n")

    backup_files = []

    # Create backup info file
    info_file = create_backup_info()

    # 1. Backup migration history
    success1, migration_file = backup_migration_history()
    if success1:
        backup_files.append(migration_file)

    # 2. Backup with Django dumpdata (always works)
    success2, django_file = backup_with_django_dumpdata()
    if success2:
        backup_files.append(django_file)

    # 3. Try to backup with pg_dump (may fail if not installed)
    success3, sql_file = backup_schema_and_data_sql()
    if success3:
        backup_files.append(sql_file)

    # Update info file with created backups
    with open(info_file, 'a', encoding='utf-8') as f:
        for backup_file in backup_files:
            file_size = os.path.getsize(backup_file)
            size_mb = file_size / (1024 * 1024)
            f.write(f"  - {backup_file} ({size_mb:.2f} MB)\n")

    backup_files.append(info_file)

    # Summary
    print("\n" + "=" * 60)
    print("BACKUP SUMMARY")
    print("=" * 60)

    for backup_file in backup_files:
        if os.path.exists(backup_file):
            file_size = os.path.getsize(backup_file)
            size_mb = file_size / (1024 * 1024)
            print(f"OK {backup_file} ({size_mb:.2f} MB)")

    print("\n" + "=" * 60)
    if success1 and success2:
        print("[SUCCESS] Backup completed!")
        print("\nYou have two backup formats:")
        print("1. Django JSON format - Easy to restore with Django")
        print("2. Migration history - For reference")
        if success3:
            print("3. PostgreSQL dump - Full database backup")
    else:
        print("[WARNING] Some backups may have failed.")

    print("=" * 60)
