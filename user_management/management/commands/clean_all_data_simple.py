from django.core.management.base import BaseCommand
from django.db import connection, transaction

class Command(BaseCommand):
    help = 'Clean all application data while preserving auth users and core tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm you want to delete all data',
        )

    def handle(self, *args, **options):
        confirm = options['confirm']
        
        # Tables to preserve (auth system and core Django functionality)
        preserve_tables = {
            'django_migrations', 'django_content_type', 'django_session', 'django_admin_log',
            'auth_user', 'auth_group', 'auth_permission', 'auth_user_groups', 
            'auth_user_user_permissions', 'auth_group_permissions',
            'user_management_role', 'user_management_role_permissions', 'user_management_userroleassignment',
        }

        cursor = connection.cursor()
        
        # Get all tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
        all_tables = [table[0] for table in cursor.fetchall()]
        tables_to_clean = [table for table in all_tables if table not in preserve_tables]
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"DATABASE CLEANUP SUMMARY")
        self.stdout.write(f"{'='*60}")
        
        # Show preserved tables
        self.stdout.write(f"\nTables to PRESERVE ({len(preserve_tables)}):")
        for table in sorted(preserve_tables):
            if table in all_tables:
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                self.stdout.write(f"  ✅ {table:<35} ({count:,} rows)")
        
        # Show tables to clean
        self.stdout.write(f"\nTables to CLEAN ({len(tables_to_clean)}):")
        total_rows = 0
        table_data = []
        
        for table in sorted(tables_to_clean):
            try:
                cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                count = cursor.fetchone()[0]
                table_data.append((table, count))
                total_rows += count
                if count > 0:
                    self.stdout.write(f"  🗑️  {table:<35} ({count:,} rows)")
                else:
                    self.stdout.write(f"  ⚪ {table:<35} (0 rows)")
            except Exception as e:
                self.stdout.write(f"  ❓ {table:<35} (Error)")
                table_data.append((table, 0))
        
        self.stdout.write(f"\nTOTAL ROWS TO DELETE: {total_rows:,}")
        
        if total_rows == 0:
            self.stdout.write(self.style.SUCCESS("\n✅ No data to delete - all tables are already empty!"))
            return
        
        if not confirm:
            self.stdout.write(self.style.WARNING(f"\n⚠️  This will permanently delete {total_rows:,} rows from {len(tables_to_clean)} tables."))
            self.stdout.write(self.style.WARNING("   Add --confirm flag to proceed with deletion."))
            return
        
        self.stdout.write(f"\n🔄 Starting data cleanup...")
        
        deleted_count = 0
        total_deleted = 0
        errors = []
        
        with transaction.atomic():
            for table, count in table_data:
                if count > 0:
                    try:
                        cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE')
                        deleted_count += 1
                        total_deleted += count
                        self.stdout.write(f"  ✅ Cleaned {table} ({count:,} rows)")
                    except Exception as e:
                        errors.append(f"{table}: {str(e)}")
                        self.stdout.write(f"  ❌ Failed {table}: {str(e)}")
        
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write(f"CLEANUP COMPLETED")
        self.stdout.write(f"{'='*60}")
        self.stdout.write(self.style.SUCCESS(f"✅ Successfully cleaned: {deleted_count} tables"))
        self.stdout.write(self.style.SUCCESS(f"📊 Total rows deleted: {total_deleted:,}"))
        self.stdout.write(f"🛡️  Preserved: {len(preserve_tables)} auth/core tables")
        
        if errors:
            self.stdout.write(self.style.ERROR(f"❌ Errors: {len(errors)}"))
            for error in errors:
                self.stdout.write(f"   - {error}")
        
        self.stdout.write(self.style.SUCCESS(f"\n🎉 Database cleanup complete!")) 