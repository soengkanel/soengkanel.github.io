from django.core.management.base import BaseCommand
from django.db import connection
from django_tenants.utils import schema_context
from company.models import Company


class Command(BaseCommand):
    help = 'Add missing columns to zone_worker table in all tenant schemas'

    def handle(self, *args, **options):
        self.stdout.write('Fixing missing columns in tenant schemas...')
        
        # Define missing columns to add
        missing_columns = [
            ('nickname', 'VARCHAR(50)'),
            ('is_vip', 'BOOLEAN DEFAULT FALSE'),
        ]
        
        # Get all tenant companies (exclude public schema)
        companies = Company.objects.exclude(schema_name='public')
        
        for company in companies:
            self.stdout.write(f'Processing {company.name} (schema: {company.schema_name})')
            
            with schema_context(company.schema_name):
                with connection.cursor() as cursor:
                    for column_name, column_def in missing_columns:
                        try:
                            # Check if column exists in current schema
                            cursor.execute("""
                                SELECT column_name 
                                FROM information_schema.columns 
                                WHERE table_name='zone_worker' AND column_name=%s
                                AND table_schema=current_schema()
                            """, [column_name])
                            
                            if cursor.fetchone():
                                self.stdout.write(f'  - {column_name} column already exists in {company.schema_name}')
                            else:
                                # Add the column
                                self.stdout.write(f'  - Adding {column_name} column to {company.schema_name}')
                                cursor.execute(f'ALTER TABLE zone_worker ADD COLUMN {column_name} {column_def}')
                                self.stdout.write(
                                    self.style.SUCCESS(f'  SUCCESS: Added {column_name} column to {company.schema_name}')
                                )
                        except Exception as e:
                            self.stdout.write(
                                self.style.ERROR(f'  ERROR adding {column_name} in {company.schema_name}: {e}')
                            )
        
        self.stdout.write(self.style.SUCCESS('Missing columns fix completed!'))